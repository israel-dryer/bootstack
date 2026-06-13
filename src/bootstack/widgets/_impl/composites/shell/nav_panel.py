"""The static navigation panel — single-select nav items in the sidebar.

`NavPanel` is the seed of the static (`add_page`) provider: it renders a flat,
single-select list of `SideNavItem`s into a sidebar region. Selection is driven
externally (by the shell, from `NavModel`) — clicking an item reports the key via
the `on_select` callback; the shell decides what becomes active and calls
`select()` back to update the visual state. The panel never owns selection truth.

Collapsible groups are deliberately absent (see `docs/_dev/appshell-navigation-spec.md`,
decision #11): the primary nav is a flat list of items plus static headers.
"""

from __future__ import annotations

from typing import Callable

from bootstack.widgets._impl.primitives.frame import Frame
from bootstack.widgets._impl.composites.sidenav.item import SideNavItem


class NavPanel(Frame):
    """A flat, single-select list of navigation items.

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

    def add_item(self, key: str, *, text: str = "", icon=None) -> SideNavItem:
        """Add a navigation item and wire its click to `on_select`.

        Args:
            key: Unique item key (also the page key).
            text: Display label.
            icon: Icon name or icon-spec dict.

        Returns:
            The created `SideNavItem`.
        """
        item = SideNavItem(self, key=key, text=text, icon=icon, accent=self._accent)
        item.pack(fill="x")
        item.on_invoked(lambda _event, k=key: self._on_select(k))
        self._items[key] = item
        return item

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
        """All item keys in insertion order."""
        return tuple(self._items)
