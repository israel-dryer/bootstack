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

        # Footer pinned to the bottom; main area fills the rest above it.
        self._footer = Frame(self)
        self._footer.pack(side="bottom", fill="x")
        self._main = Frame(self)
        self._main.pack(side="top", fill="both", expand=True)

    def add_item(self, key: str, *, text: str = "", icon=None) -> SideNavItem:
        """Add a selectable item to the main area; wire its click to `on_select`."""
        return self._add_item(self._main, key, text=text, icon=icon)

    def add_footer_item(self, key: str, *, text: str = "", icon=None) -> SideNavItem:
        """Add a selectable item pinned to the footer."""
        return self._add_item(self._footer, key, text=text, icon=icon)

    def _add_item(self, parent: Frame, key: str, *, text: str, icon) -> SideNavItem:
        if key in self._items:
            raise ValueError(f"duplicate nav item key: {key!r}")
        item = SideNavItem(parent, key=key, text=text, icon=icon, accent=self._accent)
        item.pack(fill="x")
        item.on_invoked(lambda _event, k=key: self._on_select(k))
        self._items[key] = item
        return item

    def remove_item(self, key: str) -> None:
        """Remove and destroy an item by key (no error if absent)."""
        item = self._items.pop(key, None)
        if item is not None:
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
        # (left, top, right, bottom) — aligned to the item icon column.
        header = SideNavHeader(self._main, text=text, padding=(12, 10, 12, 4))
        header.pack(fill="x")
        return header

    def add_separator(self) -> SideNavSeparator:
        """Add a separator to the main area."""
        sep = SideNavSeparator(self._main)
        sep.pack(fill="x")
        return sep

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
