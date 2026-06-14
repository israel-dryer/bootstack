"""The static navigation panel — single-select items, headers, separators, footer.

`NavPanel` renders a flat, single-select list into a sidebar region: items in a
scrolling main area plus a pinned footer area. Each item is a `RadioToggle`
sharing one `Signal`, so single-select is the radio machinery itself — no
hand-rolled selection state. The items are styled via a native Toolbutton
**variant** (`nav-quiet` under a rail; `nav-pill` standalone is added later), so
the look is driven by the style engine, not custom composite state.

Selection truth still lives in the shell's `NavModel`: clicking an item reports
the key via the `on_select` callback; the shell decides what becomes active and
calls `select()` back (setting the shared signal) to reflect it.

Section headers are plain, non-interactive labels (they chunk a flat list and
hide on compaction). There is no built-in collapsible section — hiding/revealing
a sub-list is a content concern (compose `bs.Accordion` in a custom panel).
Compaction to icon-only is a native `-compound` toggle on each item
(`'left'` <-> `'image'`); headers and separators hide while compact.
"""

from __future__ import annotations

from typing import Callable

from bootstack.signals import Signal
from bootstack.style.style import get_style
from bootstack.widgets._impl.primitives.frame import Frame
from bootstack.widgets._impl.primitives.radiotoggle import RadioToggle
from bootstack.widgets._impl.composites.scrollview import ScrollView
from bootstack.widgets._impl.composites.sidenav.header import SideNavHeader
from bootstack.widgets._impl.composites.sidenav.separator import SideNavSeparator


# Container-controlled spacing (the button's own size is the style's job).
_ITEM_GAP = 3       # vertical gap between nav buttons
_COMPACT_INSET = 6  # horizontal inset of the compact (rail-width) sidebar


class NavPanel(Frame):
    """A flat, single-select list of navigation items with a pinned footer.

    Args:
        master: Parent widget (a sidebar region).
        on_select: Called with an item key when that item is clicked.
        accent: Accent token for the active item.
        variant: Toolbutton style variant for the items (the tier treatment) —
            `'nav-quiet'` under a rail, `'nav-pill'` standalone.
        surface: Surface token the items sit on (the sidebar region surface).
    """

    def __init__(
        self,
        master,
        *,
        on_select: Callable[[str], None],
        accent: str = "primary",
        variant: str = "nav-quiet",
        surface: str = "card",
    ) -> None:
        super().__init__(master, surface=surface)
        self._on_select = on_select
        self._accent = accent
        self._variant = variant
        self._surface = surface
        self._items: dict[str, RadioToggle] = {}
        self._compact = False
        # Shared selection signal: value is the selected item key (radio
        # single-select). "" is the sentinel for "nothing selected" (a Signal is
        # typed by its initial value, so it can't hold None here).
        self._signal: Signal = Signal("")
        # Insertion-ordered main-area children (items, headers, separators) so
        # compaction can re-pack them in order; footer items tracked separately.
        self._main_children: list = []
        self._footer_items: list = []

        # Pill items are inset from the sidebar edges (the rounded pill needs
        # breathing room from the container); quiet rows run full-width.
        self._inset = 8 if variant == "nav-pill" else 0

        # Footer pinned to the bottom; the item area scrolls in the space above it
        # (a wheel-scrollable canvas with an auto-hiding bar — the footer itself
        # never scrolls). The canvas background is painted to the sidebar surface
        # so the area below short content doesn't flash the default canvas color.
        self._footer = Frame(self, surface=surface)
        self._footer.pack(side="bottom", fill="x")
        # A divider above the footer, shown ONLY when the item area scrolls — so a
        # pinned footer reads as its own band instead of abutting a clipped row.
        # When everything fits it stays hidden (no needless chrome).
        self._footer_divider = SideNavSeparator(self, surface=surface, padding=(0, 0, 0, 0))
        # Start with no gutter/bar; overflow detection switches it on only when the
        # content is actually tall enough to scroll (see _update_overflow_state).
        self._scroll = ScrollView(
            self,
            scroll_direction="vertical",
            scrollbar_visibility="never",
            surface=surface,
        )
        self._scroll.pack(side="top", fill="both", expand=True)
        self._main = self._scroll.add(surface=surface)
        self._updating_overflow = False
        self._paint_canvas_surface()
        self.bind("<<BsThemeChanged>>", lambda _e: self._paint_canvas_surface(), add="+")
        # Re-evaluate the gutter/bar + footer divider whenever the content height
        # or viewport changes (items added/removed, sidebar resized, compaction).
        self._scroll.canvas.bind("<Configure>", lambda _e: self._update_overflow_state(), add="+")
        self._main.bind("<Configure>", lambda _e: self._update_overflow_state(), add="+")
        self._apply_inset(self._inset)

    def add_item(self, key: str, *, text: str = "", icon=None) -> RadioToggle:
        """Add a selectable item to the main area; wire its click to `on_select`."""
        return self._add_item(self._main, key, text=text, icon=icon, footer=False)

    def add_footer_item(self, key: str, *, text: str = "", icon=None) -> RadioToggle:
        """Add a selectable item pinned to the footer."""
        return self._add_item(self._footer, key, text=text, icon=icon, footer=True)

    def _add_item(self, parent: Frame, key: str, *, text: str, icon, footer: bool) -> RadioToggle:
        if key in self._items:
            raise ValueError(f"duplicate nav item key: {key!r}")
        item = RadioToggle(
            parent,
            value=key,
            signal=self._signal,
            text=text,
            icon=icon,
            compound="image" if self._compact else "left",
            accent=self._accent,
            surface=self._surface,
            variant=self._item_variant(),
        )
        item.pack(fill="x", pady=(0, _ITEM_GAP))
        # Click reports the key to the shell (which drives NavModel). The radio
        # also updates the shared signal on click; the shell reconciles via select().
        item.bind("<Button-1>", lambda _e, k=key: self._on_select(k), add="+")
        self._items[key] = item
        (self._footer_items if footer else self._main_children).append(item)
        if footer:
            # A footer item may appear after the content is laid out; the divider
            # gate depends on footer presence, so re-evaluate now.
            self._update_overflow_state()
        return item

    def remove_item(self, key: str) -> None:
        """Remove and destroy an item by key (no error if absent)."""
        item = self._items.pop(key, None)
        if item is not None:
            for tracker in (self._main_children, self._footer_items):
                if item in tracker:
                    tracker.remove(item)
            item.destroy()
            if self._signal() == key:
                self._signal.set("")
            self._update_overflow_state()

    def update_item(self, key: str, *, text: str | None = None, icon=None) -> None:
        """Update an existing item's label and/or icon in place."""
        item = self._items.get(key)
        if item is None:
            return
        if text is not None:
            item.configure(text=text)
        if icon is not None:
            item.configure(icon=icon)

    def add_header(self, text: str) -> SideNavHeader:
        """Add a plain section-label header to the main area.

        A header is a quiet, non-interactive label that chunks the flat list; it
        hides while the panel is compacted. (There is no collapsible-header
        primitive — a collapsible sub-list is a content concern.)

        Uses a tighter top margin than the stock `SideNavHeader` default — the
        header alone carries enough separation, so a roomy top gap reads as
        excess (especially when it follows an item).
        """
        # (left, top, right, bottom) — aligned to the item icon column. A roomier
        # top gap separates the new group from the one above; the small bottom gap
        # keeps the header bound to its own items.
        header = SideNavHeader(self._main, text=text, padding=(12, 16, 12, 4))
        if not self._compact:
            header.pack(fill="x")
        self._main_children.append(header)
        return header

    def add_separator(self) -> SideNavSeparator:
        """Add a separator to the main area."""
        sep = SideNavSeparator(self._main)
        if not self._compact:
            sep.pack(fill="x")
        self._main_children.append(sep)
        return sep

    def _relayout_main(self) -> None:
        """Re-pack the main area in insertion order, honoring compact.

        Compact renders items icon-only (`-compound='image'`) and hides headers
        and separators (a label-less icon strip); expanded shows everything.
        """
        for child in self._main_children:
            child.pack_forget()
        for child in self._main_children:
            if isinstance(child, (SideNavHeader, SideNavSeparator)):
                if not self._compact:
                    child.pack(fill="x")
            else:  # RadioToggle nav item
                child.pack(fill="x", pady=(0, _ITEM_GAP))

    def _item_variant(self) -> str:
        """The Toolbutton style variant for items in the current mode."""
        return f"{self._variant}-compact" if self._compact else self._variant

    def _apply_inset(self, inset: int) -> None:
        """Inset the scrolled item area + footer from the sidebar edges.

        Pills need breathing room; quiet rows run flush (inset 0). The item area
        is a canvas window (not pack-managed), so its inset is its own padding.
        """
        self._main.configure(padding=(inset, inset, inset, 0))
        self._footer.pack_configure(padx=inset, pady=(0, inset))

    def _paint_canvas_surface(self) -> None:
        """Match the scroll canvas background to the sidebar surface token."""
        try:
            color = get_style().style_builder.color(self._surface)
            self._scroll.canvas.configure(background=color)
        except Exception:
            pass

    def _content_overflows(self) -> bool:
        """Whether the item content is taller than the scroll viewport.

        Uses a small epsilon so a 1–4px overhang doesn't toggle the gutter — and,
        with the gutter's own width, gives stable hysteresis (no flicker).
        """
        try:
            bbox = self._scroll.canvas.bbox("all")
            if not bbox:
                return False
            viewport_h = self._scroll.canvas.winfo_height()
            return viewport_h > 1 and (bbox[3] - bbox[1]) > viewport_h + 4
        except Exception:
            return False

    def _update_overflow_state(self) -> None:
        """Reserve the scrollbar gutter + show the footer divider only on overflow.

        When the content fits, the bar/gutter is off (`'never'`) so items run
        full-width and there's no footer divider; when it overflows, the gutter +
        auto-hiding bar turn on (`'scroll'`) and a divider separates the pinned
        footer from the scrolling rows.
        """
        if self._updating_overflow:
            return
        self._updating_overflow = True
        try:
            overflow = self._content_overflows()
            desired = "scroll" if overflow else "never"
            if self._scroll.cget("scrollbar_visibility") != desired:
                self._scroll.configure(scrollbar_visibility=desired)
            show_divider = overflow and bool(self._footer_items)
            mapped = self._footer_divider.winfo_manager() != ""
            if show_divider and not mapped:
                self._footer_divider.pack(side="bottom", fill="x")
            elif not show_divider and mapped:
                self._footer_divider.pack_forget()
        finally:
            self._updating_overflow = False

    def set_compact(self, compact: bool) -> None:
        """Render items icon-only (compact) or with labels (expanded).

        Compaction swaps each item to the matching `-compact` style variant (a
        centered icon-only layout) and flips `-compound` to hide the label — both
        native, no custom composite state.
        """
        if self._compact == compact:
            return
        self._compact = compact
        # Compact shrinks the sidebar to the rail width; use a small inset so the
        # pills don't touch the edges (the card pill is narrow enough to fit).
        self._apply_inset(_COMPACT_INSET if compact else self._inset)
        variant = self._item_variant()
        compound = "image" if compact else "left"
        for item in self._items.values():
            item.configure(variant=variant, compound=compound)
        self._relayout_main()

    @property
    def compact(self) -> bool:
        """Whether the panel is rendering items icon-only."""
        return self._compact

    def select(self, key: str | None) -> None:
        """Set the visual selection to `key` (or clear it with `None`)."""
        self._signal.set(key if key is not None else "")

    @property
    def selected(self) -> str | None:
        """The currently selected item key, or `None`."""
        return self._signal() or None

    def item_keys(self) -> tuple[str, ...]:
        """All item keys (main + footer) in insertion order."""
        return tuple(self._items)
