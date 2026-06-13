"""The static navigation panel — single-select items, headers, separators, footer.

`NavPanel` renders a flat, single-select list into a sidebar region: items in a
scrolling main area plus a pinned footer area. Selection is driven externally
(by the shell, from `NavModel`) — clicking an item reports the key via the
`on_select` callback; the shell decides what becomes active and calls `select()`
back to update the visual state. The panel never owns selection truth.

Collapsible groups are deliberately absent (see `docs/_dev/appshell-navigation-spec.md`,
decision #11): the primary nav is a flat list of items plus *static* headers.
"""

from __future__ import annotations

from typing import Callable

from bootstack.widgets._impl.primitives.frame import Frame
from bootstack.widgets._impl.composites.sidenav.item import SideNavItem
from bootstack.widgets._impl.composites.sidenav.header import SideNavHeader
from bootstack.widgets._impl.composites.sidenav.separator import SideNavSeparator


class NavPanel(Frame):
    """A flat, single-select list of navigation items with a pinned footer.

    Args:
        master: Parent widget (a sidebar region).
        on_select: Called with an item key when that item is clicked.
        accent: Accent token for the active-item indicator.
    """

    def __init__(
        self,
        master,
        *,
        on_select: Callable[[str], None],
        accent: str = "primary",
    ) -> None:
        super().__init__(master)
        self._on_select = on_select
        self._accent = accent
        self._items: dict[str, SideNavItem] = {}
        self._selected: str | None = None
        self._compact = False
        # Insertion-ordered main-area children (items, headers, separators) so
        # compaction can re-pack them in order; footer items tracked separately.
        self._main_children: list[Frame] = []
        self._footer_items: list[SideNavItem] = []

        # Footer pinned to the bottom; main area fills the rest above it.
        self._footer = Frame(self)
        self._footer.pack(side="bottom", fill="x")
        self._main = Frame(self)
        self._main.pack(side="top", fill="both", expand=True)

    def add_item(self, key: str, *, text: str = "", icon=None) -> SideNavItem:
        """Add a selectable item to the main area; wire its click to `on_select`."""
        return self._add_item(self._main, key, text=text, icon=icon, footer=False)

    def add_footer_item(self, key: str, *, text: str = "", icon=None) -> SideNavItem:
        """Add a selectable item pinned to the footer."""
        return self._add_item(self._footer, key, text=text, icon=icon, footer=True)

    def _add_item(self, parent: Frame, key: str, *, text: str, icon, footer: bool) -> SideNavItem:
        if key in self._items:
            raise ValueError(f"duplicate nav item key: {key!r}")
        item = SideNavItem(parent, key=key, text=text, icon=icon, accent=self._accent)
        if self._compact:
            item.set_compact(True)
        item.pack(fill="x")
        item.on_invoked(lambda _event, k=key: self._on_select(k))
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
            if self._selected == key:
                self._selected = None

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
        """Add a static (non-collapsible) section header to the main area.

        Uses a tighter top margin than the stock `SideNavHeader` default — the
        header alone carries enough separation, so a roomy top gap reads as
        excess (especially when it follows an item).
        """
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

        - Compact: items render icon-only; headers and separators hide; collapsed
          groups are *flattened* (their items still show as icons) — collapse
          state is preserved and restored on expand.
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
            else:  # SideNavItem
                child.set_compact(self._compact)
                if self._compact or not group_collapsed:
                    child.pack(fill="x")

    def set_compact(self, compact: bool) -> None:
        """Render items icon-only (compact) or with labels (expanded)."""
        if self._compact == compact:
            return
        self._compact = compact
        self._relayout_main()
        for item in self._footer_items:
            item.set_compact(compact)

    @property
    def compact(self) -> bool:
        """Whether the panel is rendering items icon-only."""
        return self._compact

    def select(self, key: str | None) -> None:
        """Set the visual selection to `key` (or clear it with `None`)."""
        for k, item in self._items.items():
            item.set_selected(k == key)
        self._selected = key

    @property
    def selected(self) -> str | None:
        """The currently selected item key, or `None`."""
        return self._selected

    def item_keys(self) -> tuple[str, ...]:
        """All item keys (main + footer) in insertion order."""
        return tuple(self._items)
