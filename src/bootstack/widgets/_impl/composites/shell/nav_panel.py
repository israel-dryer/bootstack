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

Section headers may be **1-level collapsible groups** (a header + the run of
items after it, up to the next header/separator). Compaction to icon-only is a
native `-compound` toggle on each item (`'left'` <-> `'image'`).
"""

from __future__ import annotations

from typing import Callable

from bootstack.signals import Signal
from bootstack.widgets._impl.primitives.frame import Frame
from bootstack.widgets._impl.primitives.radiotoggle import RadioToggle
from bootstack.widgets._impl.composites.sidenav.header import SideNavHeader
from bootstack.widgets._impl.composites.sidenav.separator import SideNavSeparator


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

        # Footer pinned to the bottom; main area fills the rest above it.
        self._footer = Frame(self, surface=surface)
        self._footer.pack(side="bottom", fill="x")
        self._main = Frame(self, surface=surface)
        self._main.pack(side="top", fill="both", expand=True)

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
            variant=self._variant,
        )
        item.pack(fill="x")
        # Click reports the key to the shell (which drives NavModel). The radio
        # also updates the shared signal on click; the shell reconciles via select().
        item.bind("<Button-1>", lambda _e, k=key: self._on_select(k), add="+")
        self._items[key] = item
        (self._footer_items if footer else self._main_children).append(item)
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

    def update_item(self, key: str, *, text: str | None = None, icon=None) -> None:
        """Update an existing item's label and/or icon in place."""
        item = self._items.get(key)
        if item is None:
            return
        if text is not None:
            item.configure(text=text)
        if icon is not None:
            item.configure(icon=icon)

    def add_header(self, text: str, *, collapsible: bool = False) -> SideNavHeader:
        """Add a section header to the main area.

        With `collapsible=True` the header gains a chevron and toggles the run of
        items that follows it (up to the next header or separator) — a 1-level
        accordion group. `collapsible=False` is a plain static section label (a
        group "pinned open").

        Uses a tighter top margin than the stock `SideNavHeader` default — the
        header alone carries enough separation, so a roomy top gap reads as
        excess (especially when it follows an item).
        """
        # (left, top, right, bottom) — aligned to the item icon column.
        header = SideNavHeader(
            self._main, text=text, padding=(12, 10, 12, 4), collapsible=collapsible
        )
        if collapsible:
            header._on_toggle = lambda h=header: self._toggle_group(h)
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

    def _toggle_group(self, header: SideNavHeader) -> None:
        """Collapse/expand a collapsible header's item run."""
        header.set_collapsed(not header.collapsed)
        self._relayout_main()

    def expand_all(self) -> None:
        """Expand every collapsible group."""
        self._set_all_groups_collapsed(False)

    def collapse_all(self) -> None:
        """Collapse every collapsible group."""
        self._set_all_groups_collapsed(True)

    def _set_all_groups_collapsed(self, collapsed: bool) -> None:
        changed = False
        for child in self._main_children:
            if isinstance(child, SideNavHeader) and child.collapsible:
                if child.collapsed != collapsed:
                    child.set_collapsed(collapsed)
                    changed = True
        if changed:
            self._relayout_main()

    def _relayout_main(self) -> None:
        """Re-pack the main area in insertion order, honoring compact + groups.

        - Compact: items render icon-only (`-compound='image'`); headers and
          separators hide; collapsed groups are *flattened* (their items still
          show as icons) — collapse state is preserved and restored on expand.
        - Expanded: headers/separators show; an item is hidden when it belongs to
          a collapsed group (the run of items after a collapsed collapsible
          header, up to the next header or separator).
        """
        for child in self._main_children:
            child.pack_forget()
        group_collapsed = False  # whether the current item run is collapsed
        for child in self._main_children:
            if isinstance(child, SideNavHeader):
                group_collapsed = child.collapsible and child.collapsed
                if not self._compact:
                    child.pack(fill="x")
            elif isinstance(child, SideNavSeparator):
                group_collapsed = False
                if not self._compact:
                    child.pack(fill="x")
            else:  # RadioToggle nav item
                child.configure(compound="image" if self._compact else "left")
                if self._compact or not group_collapsed:
                    child.pack(fill="x")

    def set_compact(self, compact: bool) -> None:
        """Render items icon-only (compact) or with labels (expanded).

        Compaction is a native `-compound` toggle on each item, not a style state.
        """
        if self._compact == compact:
            return
        self._compact = compact
        self._relayout_main()
        for item in self._footer_items:
            item.configure(compound="image" if compact else "left")

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
