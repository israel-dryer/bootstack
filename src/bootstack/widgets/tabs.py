from __future__ import annotations

import tkinter
from typing import overload, Any, Callable, Literal

from bootstack.widgets._impl.composites.tabs.tabview import TabView as _InternalTabView
from bootstack.events import TabChangeEvent, TabCloseEvent, TabRef
from bootstack.widgets._impl.primitives.flexframe import FlexFrame
from bootstack.widgets._impl.primitives.gridframe import GridFrame
from bootstack.widgets._core.base import PublicWidgetBase, adapt_handler
from bootstack.widgets._core.container import (
    GRID_KEYS, grid_sticky, place_flex_child, _reject_legacy_child_kwargs,
    _expand_margin,
)
from bootstack.widgets._core.context import push_container, pop_container
from bootstack.widgets._core.events import register_widget_events, resolve_event
from bootstack.events import Subscription
from bootstack._core import NavigationError
from bootstack.streams import Stream
from bootstack.widgets.types import (
    Event, AccentToken, Padding, LayoutKind, AutoFlow, Orient,
)

_TABS_EVENTS: dict[str, str] = {
    "change":    "<<TabChanged>>",
    "tab_close": "<<TabClose>>",
    "tab_add":   "<<TabAdd>>",
}


class TabPage:
    """A handle for one tab — both a layout context and a live controller.

    Returned by `Tabs.add()` and by `Tabs.item()` / `items()`. Use it as a `with`
    block to place child widgets, and read `key` / read or set `label`, or call
    `select()` / `hide()` / `show()` / `remove()` to drive the tab afterward.

    As a context manager it accepts the same layout kwargs as the standalone
    layout containers — `layout=`, `gap=`, `horizontal_items=`, `vertical_items=`,
    `grow_items=`, `columns=`, `rows=`, `auto_flow=`.
    """

    def __init__(
        self,
        page_widget: tkinter.Widget,
        *,
        key: str,
        owner: "Tabs",
        layout: LayoutKind = "column",
        padding: Padding | None = None,
        gap: int = 0,
        horizontal_items: str | None = None,
        vertical_items: str | None = None,
        grow_items: bool = False,
        columns: int | list[int | str] | None = None,
        rows: int | list[int | str] | None = None,
        auto_flow: AutoFlow = "row",
    ) -> None:
        self._page = page_widget
        self._key = key
        self._owner = owner
        self._layout = layout

        if horizontal_items is None:
            horizontal_items = (
                "stretch" if layout == "grid"
                else "center" if layout == "column" else "left"
            )
        if vertical_items is None:
            vertical_items = (
                "stretch" if layout == "grid"
                else "center" if layout == "row" else "top"
            )

        if layout in ("column", "row"):
            self._layout_frame = FlexFrame(
                page_widget,
                direction="vertical" if layout == "column" else "horizontal",
                padding=padding,
                gap=gap,
                horizontal_items=horizontal_items,
                vertical_items=vertical_items,
                grow_items=grow_items,
            )
        elif layout == "grid":
            self._layout_frame = GridFrame(
                page_widget,
                columns=columns,
                rows=rows,
                padding=padding,
                gap=gap,
                auto_flow=auto_flow,
            )
        else:
            raise ValueError(
                f"TabPage layout must be 'column', 'row', or 'grid', got {layout!r}"
            )

        self._horizontal_items = horizontal_items
        self._vertical_items = vertical_items
        self._layout_frame.pack(fill="both", expand=True)

    def _child_master(self) -> tkinter.Widget:
        return self._layout_frame

    def guide_layout(self, child: PublicWidgetBase, **layout_kw: Any) -> None:
        if self._layout == "grid":
            _reject_legacy_child_kwargs(layout_kw, "TabPage")
            _expand_margin(layout_kw)
            options = {k: v for k, v in layout_kw.items() if k in GRID_KEYS}
            h = layout_kw.get("horizontal") or self._horizontal_items
            v = layout_kw.get("vertical") or self._vertical_items
            options["sticky"] = grid_sticky(h, v)
            child._internal.grid(in_=self._child_master(), **options)
            return
        place_flex_child(self._layout_frame, child, layout_kw, "TabPage")

    # ----- Tab identity, label, and control -----

    @property
    def key(self) -> str:
        """The tab's unique key, used with `Tabs.item()` / `select()`."""
        return self._key

    @property
    def label(self) -> str:
        """The text shown on the tab. Assigning a new value relabels the tab."""
        return self._owner._internal.configure_tab(self._key, "text")

    @label.setter
    def label(self, value: str) -> None:
        self._owner._internal.configure_tab(self._key, text=value)

    def select(self) -> None:
        """Select (focus) this tab."""
        self._owner.select(self._key)

    def hide(self) -> None:
        """Hide this tab without removing it. Restore with `show()`."""
        self._owner.hide_tab(self._key)

    def show(self) -> None:
        """Restore this tab after it was hidden."""
        self._owner.show_tab(self._key)

    def remove(self) -> None:
        """Remove this tab and its page entirely."""
        self._owner.forget_tab(self._key)

    def __enter__(self) -> "TabPage":
        push_container(self)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pop_container(self)


class Tabs(PublicWidgetBase):
    """A tabbed container. Add pages with `.add()` and place children inside them.

    Usage::

        tabs = bs.Tabs()
        with tabs.add("home", label="Home"):
            bs.Label("Welcome")
        with tabs.add("settings", label="Settings"):
            bs.Label("Settings here")

    Args:
        orient: `'horizontal'` (default, tabs above content) or `'vertical'` (tabs left).
        show_divider: Show a divider line between the tab bar and the page area.
        tab_width: Fixed tab width in pixels, `'stretch'` to fill available space, or
            `None` (default, size to content).
        allow_close: Show close buttons on tabs. `True` = always, `False` = never,
            `'hover'` = on hover. Defaults to `False`.
        allow_add: Show an add-tab button that fires the `tab_add` event.
        accent: Accent token for the tab bar. Defaults to the theme accent.
        parent: Override the context-stack parent.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        *,
        orient: Orient = "horizontal",
        show_divider: bool | None = None,
        tab_width: int | Literal["stretch"] | None = None,
        allow_close: bool | Literal["hover"] = False,
        allow_add: bool = False,
        accent: AccentToken | str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "orient": orient,
            "enable_closing": allow_close,
            "enable_adding": allow_add,
        }
        if show_divider is not None:
            internal_kwargs["show_divider"] = show_divider
        if tab_width is not None:
            internal_kwargs["tab_width"] = tab_width
        if accent is not None:
            internal_kwargs["accent"] = accent

        self._pages: dict[str, TabPage] = {}
        self._internal = _InternalTabView(tk_master, **internal_kwargs)
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
                bid = self._internal.bind(sequence, adapt_handler(h), add="+")
                return Subscription(self._internal, sequence, bid)
            return Stream(self._internal, _source=_source)

        bind_id = self._internal.bind(sequence, adapt_handler(handler), add="+")
        return Subscription(self._internal, sequence, bind_id)

    # ----- Tab management -----

    def add(
        self,
        key: str,
        *,
        label: str = "",
        icon: str | None = None,
        closable: bool | Literal["hover"] | None = None,
        close_command: Callable[[], Any] | None = None,
        layout: LayoutKind = "column",
        padding: Padding | None = None,
        gap: int = 0,
        horizontal_items: str | None = None,
        vertical_items: str | None = None,
        grow_items: bool = False,
        columns: int | list[int | str] | None = None,
        rows: int | list[int | str] | None = None,
        auto_flow: AutoFlow = "row",
    ) -> TabPage:
        """Add a tab and return a handle for placing its children and controlling it.

        Args:
            key: Unique identifier for the tab/page.
            label: Label displayed on the tab.
            icon: Icon name displayed on the tab.
            closable: Close-button visibility for this tab. Overrides `allow_close`.
            close_command: Called when the close button is clicked.
            layout: Internal layout. Defaults to `'column'`.
            padding: Space inside the page frame. Defaults to `None`.
            gap: Space between children in pixels. Defaults to `0`.
            horizontal_items: How children sit on the horizontal axis — edge
                values `'left'`/`'center'`/`'right'`/`'stretch'`, plus `'space-*'`
                when horizontal is the stacking axis. Defaults to `'stretch'` in grid mode,
                `'center'` in a column and `'left'` in a row.
            vertical_items: How children sit on the vertical axis — edge values
                `'top'`/`'center'`/`'bottom'`/`'stretch'`, plus `'space-*'` when
                vertical is the stacking axis. Defaults to `'stretch'` in grid mode,
                `'center'` in a row and `'top'` in a column.
            grow_items: For `'column'`/`'row'`, when `True` every child grows
                equally to share the main axis. Defaults to `False`.
            columns: Column definitions for `'grid'` layout. An integer sets
                the number of equal-weight columns; a list sets per-column
                weights or sizes (e.g. `[1, 2, 'auto', '120px']`).
            rows: Row definitions for `'grid'` layout, same format as `columns`.
            auto_flow: Grid auto-flow direction. Defaults to `'row'`.

        Returns:
            `TabPage` — use as a context manager to place children, and as a
            handle to `select()`/`hide()`/`show()`/`remove()` the tab.
        """
        add_kwargs: dict[str, Any] = {}
        if icon is not None:
            add_kwargs["icon"] = icon
        if closable is not None:
            add_kwargs["closable"] = closable
        if close_command is not None:
            add_kwargs["close_command"] = close_command

        page_widget = self._internal.add(key, text=label, **add_kwargs)
        page = TabPage(
            page_widget,
            key=key, owner=self,
            layout=layout, padding=padding, gap=gap,
            horizontal_items=horizontal_items, vertical_items=vertical_items,
            grow_items=grow_items,
            columns=columns, rows=rows, auto_flow=auto_flow,
        )
        self._pages[key] = page
        return page

    def select(self, key: str) -> None:
        """Select the tab identified by `key`.

        Raises:
            NavigationError: If no tab with the given key exists.
        """
        self._internal.select(key)

    def hide_tab(self, key: str) -> None:
        """Hide a tab without removing it. Restore with `show_tab()`.

        Raises:
            NavigationError: If no tab with the given key exists.
        """
        self._internal.hide_tab(key)

    def show_tab(self, key: str) -> None:
        """Restore a previously hidden tab.

        Raises:
            NavigationError: If no tab with the given key exists.
        """
        self._internal.show_tab(key)

    def forget_tab(self, key: str) -> None:
        """Remove a tab and its page entirely.

        Raises:
            NavigationError: If no tab with the given key exists.
        """
        self._internal.forget_tab(key)
        self._pages.pop(key, None)

    # ----- Properties / introspection -----

    @property
    def current(self) -> str | None:
        """Key of the currently selected tab, or `None` if no tab is selected."""
        return self._internal.current

    def tab_keys(self) -> tuple[str, ...]:
        """All tab keys in insertion order."""
        return self._internal.tab_keys()

    def page_keys(self) -> tuple[str, ...]:
        """All page keys in insertion order."""
        return self._internal.page_keys()

    def item(self, key: str) -> TabPage:
        """Return the tab handle for `key`.

        Args:
            key: Tab key assigned in `add()`.

        Returns:
            The `TabPage` for that key — read/set its `label` or call
            `select()`/`hide()`/`show()`/`remove()`.

        Raises:
            NavigationError: If no tab with the given key exists.
        """
        if key not in self._pages:
            raise NavigationError(f"No tab with key '{key}'")
        return self._pages[key]

    def items(self) -> tuple[TabPage, ...]:
        """Return all tab handles in insertion order."""
        return tuple(self._pages[k] for k in self._internal.tab_keys())

    # ----- Event shorthands -----

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[TabChangeEvent], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[TabChangeEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the selected tab changes.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("change", handler)

    @overload
    def on_tab_close(self) -> Stream: ...
    @overload
    def on_tab_close(self, handler: Callable[[TabCloseEvent], Any]) -> Subscription: ...
    def on_tab_close(self, handler: Callable[[TabCloseEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when a tab's close button is clicked.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("tab_close", handler)

    @overload
    def on_tab_add(self) -> Stream: ...
    @overload
    def on_tab_add(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_tab_add(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the add-tab button is clicked.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("tab_add", handler)


register_widget_events(Tabs, _TABS_EVENTS)

__all__ = ["Tabs", "TabPage", "TabChangeEvent", "TabRef"]