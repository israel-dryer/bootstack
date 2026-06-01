from __future__ import annotations

from typing import overload, Any, Callable, Literal

from bootstack.widgets._impl.composites.sidenav.view import SideNav as _InternalSideNav, DisplayMode
from bootstack.widgets._impl.composites.sidenav.item import SideNavItem
from bootstack.widgets._impl.composites.sidenav.group import SideNavGroup
from bootstack.widgets._impl.composites.sidenav.header import SideNavHeader
from bootstack.widgets._impl.composites.sidenav.separator import SideNavSeparator
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events, resolve_event
from bootstack.widgets._core.subscription import Subscription
from bootstack.widgets._core.stream import Stream
from bootstack.widgets.types import Event
from bootstack.signals import Signal


_SIDENAV_EVENTS: dict[str, str] = {
    "selection_changed":    "<<SelectionChanged>>",
    "back_requested":       "<<BackRequested>>",
    "pane_toggled":         "<<PaneToggled>>",
    "display_mode_changed": "<<DisplayModeChanged>>",
}


class SideNav(PublicWidgetBase):
    """A sidebar navigation container with header, scrollable items, and footer.

    Accepts layout kwargs inline (`fill=`, `expand=`, `margin=`, etc.).

    Args:
        title: Title displayed in the pane header.
        show_header: Show the internal header toolbar. Set to `False` when using
            an external toolbar (e.g. `AppShell`).
        show_back_button: Show a back button in the header.
        collapsible: Allow the pane to collapse. Shows a hamburger menu button.
        display_mode: Initial display mode — `'expanded'`, `'compact'`, or
            `'minimal'`.
        is_pane_open: Whether the pane starts open.
        pane_width: Override the default pane width in pixels.
        signal: Reactive `Signal[str]` for the selected item key.
        accent: Accent token for selection indicators.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        *,
        title: str = "",
        show_header: bool = True,
        show_back_button: bool = False,
        collapsible: bool = True,
        display_mode: DisplayMode = "expanded",
        is_pane_open: bool = True,
        pane_width: int | None = None,
        signal: "Signal[str] | None" = None,
        accent: str = "primary",
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        internal_kw: dict[str, Any] = {
            "title": title,
            "show_header": show_header,
            "show_back_button": show_back_button,
            "collapsible": collapsible,
            "display_mode": display_mode,
            "is_pane_open": is_pane_open,
            "accent": accent,
        }
        if pane_width is not None:
            internal_kw["pane_width"] = pane_width
        if signal is not None:
            internal_kw["signal"] = signal

        self._internal = _InternalSideNav(tk_master, **internal_kw)
        self._attach_to_parent(layout_kw)

    # ----- Event routing -----

    @overload
    def on(self, event: str) -> Stream: ...
    @overload
    def on(self, event: str, handler: Callable[[Event], Any]) -> Subscription: ...
    def on(self, event: str, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Bind `handler` to `event` and return a `Subscription`."""
        sequence = resolve_event(self, str(event))
        if handler is None:
            def _source(h):
                bid = self._internal.bind(sequence, h, add="+")
                return Subscription(self._internal, sequence, bid)
            return Stream(self._internal, _source=_source)
        bid = self._internal.bind(sequence, handler, add="+")
        return Subscription(self._internal, sequence, bid)

    # ----- Item management -----

    def add_item(
        self,
        key: str,
        text: str = "",
        *,
        icon: str | dict | None = None,
        group: str | None = None,
    ) -> SideNavItem:
        """Add a navigation item.

        Args:
            key: Unique identifier for the item.
            text: Display text.
            icon: Icon name or configuration dict.
            group: Key of a group to nest this item under.

        Returns:
            The created `SideNavItem`.
        """
        return self._internal.add_item(key, text, icon=icon, group=group)

    def add_group(
        self,
        key: str,
        text: str = "",
        *,
        icon: str | dict | None = None,
        is_expanded: bool = False,
    ) -> SideNavGroup:
        """Add a collapsible navigation group.

        Args:
            key: Unique identifier for the group.
            text: Display text.
            icon: Icon name or configuration dict.
            is_expanded: Start expanded. Default `False`.

        Returns:
            The created `SideNavGroup`.
        """
        return self._internal.add_group(key, text, icon=icon, is_expanded=is_expanded)

    def add_header(self, text: str) -> SideNavHeader:
        """Add a non-selectable section header label.

        Args:
            text: Header text.

        Returns:
            The created `SideNavHeader`.
        """
        return self._internal.add_header(text)

    def add_separator(self) -> SideNavSeparator:
        """Add a visual separator between items.

        Returns:
            The created `SideNavSeparator`.
        """
        return self._internal.add_separator()

    def add_footer_item(
        self,
        key: str,
        text: str = "",
        *,
        icon: str | dict | None = None,
    ) -> SideNavItem:
        """Add a navigation item pinned to the footer.

        Args:
            key: Unique identifier for the item.
            text: Display text.
            icon: Icon name or configuration dict.

        Returns:
            The created `SideNavItem`.
        """
        return self._internal.add_footer_item(key, text, icon=icon)

    # ----- Item access -----

    def node(self, key: str) -> SideNavItem:
        """Return the item with the given key.

        Args:
            key: Item key assigned in `add_item()` or `add_footer_item()`.

        Raises:
            KeyError: If no item with the given key exists.
        """
        return self._internal.node(key)

    def nodes(self) -> tuple[SideNavItem, ...]:
        """Return all main-area items in insertion order."""
        return self._internal.nodes()

    def node_keys(self) -> tuple[str, ...]:
        """Return all main-area item keys in insertion order."""
        return self._internal.node_keys()

    def footer_nodes(self) -> tuple[SideNavItem, ...]:
        """Return all footer items in insertion order."""
        return self._internal.footer_nodes()

    def footer_node_keys(self) -> tuple[str, ...]:
        """Return all footer item keys in insertion order."""
        return self._internal.footer_node_keys()

    def group(self, key: str) -> SideNavGroup:
        """Return the group with the given key.

        Args:
            key: Group key assigned in `add_group()`.

        Raises:
            KeyError: If no group with the given key exists.
        """
        return self._internal.group(key)

    def groups(self) -> tuple[SideNavGroup, ...]:
        """Return all groups in insertion order."""
        return self._internal.groups()

    def configure_node(self, key: str, option: str | None = None, **kwargs: Any) -> Any:
        """Get or set options on a specific item.

        Args:
            key: Item key.
            option: If provided, return this option's value.
            **kwargs: Options to apply to the item.
        """
        return self._internal.configure_node(key, option, **kwargs)

    # ----- Mutation -----

    def select(self, key: str) -> None:
        """Select an item by key.

        Args:
            key: Item key to select.
        """
        self._internal.select(key)

    def remove_item(self, key: str) -> None:
        """Remove an item by key, including any group membership.

        Args:
            key: Item key to remove.
        """
        self._internal.remove_item(key)

    def remove_group(self, key: str) -> None:
        """Remove a group and all its items.

        Args:
            key: Group key to remove.
        """
        self._internal.remove_group(key)

    # ----- Pane control -----

    def toggle_pane(self) -> None:
        """Toggle the pane between expanded and compact, or show/hide in minimal mode."""
        self._internal.toggle_pane()

    def open_pane(self) -> None:
        """Open the pane."""
        self._internal.open_pane()

    def close_pane(self) -> None:
        """Close the pane."""
        self._internal.close_pane()

    def set_display_mode(self, mode: DisplayMode) -> None:
        """Switch display mode.

        Args:
            mode: `'expanded'`, `'compact'`, or `'minimal'`.
        """
        self._internal.set_display_mode(mode)

    # ----- Properties -----

    @property
    def selected_key(self) -> str | None:
        """The currently selected item key, or `None`."""
        return self._internal.selected_key

    @property
    def is_pane_open(self) -> bool:
        """Whether the pane is currently visible."""
        return self._internal.is_pane_open

    @property
    def display_mode(self) -> DisplayMode:
        """Current display mode: `'expanded'`, `'compact'`, or `'minimal'`."""
        return self._internal.display_mode

    @property
    def signal(self) -> "Signal[str] | None":
        """The reactive signal tracking the selected item key."""
        return self._internal.signal

    # ----- Event shorthands -----

    @overload
    def on_selection_changed(self) -> Stream: ...
    @overload
    def on_selection_changed(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_selection_changed(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the selected item changes.

        Args:
            handler: Receives `event.data = {'key': str}` — newly selected key.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("selection_changed", handler)

    @overload
    def on_back_requested(self) -> Stream: ...
    @overload
    def on_back_requested(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_back_requested(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the back button is clicked.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("back_requested", handler)

    @overload
    def on_pane_toggled(self) -> Stream: ...
    @overload
    def on_pane_toggled(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_pane_toggled(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the pane is opened or closed.

        Args:
            handler: Receives `event.data = {'is_open': bool}`.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("pane_toggled", handler)

    @overload
    def on_display_mode_changed(self) -> Stream: ...
    @overload
    def on_display_mode_changed(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_display_mode_changed(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the display mode changes.

        Args:
            handler: Receives `event.data = {'mode': str}`.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("display_mode_changed", handler)


register_widget_events(SideNav, _SIDENAV_EVENTS)

__all__ = [
    "SideNav",
    "SideNavItem",
    "SideNavGroup",
    "SideNavHeader",
    "SideNavSeparator",
    "DisplayMode",
]
