from __future__ import annotations

import tkinter
from typing import overload, Any, Callable, Literal

from bootstack.widgets._impl.composites.tabs.tabview import TabView as _InternalTabView
from bootstack.widgets._impl.composites.tabs.events import TabChangeEventData, TabRef
from bootstack.widgets._impl.primitives.packframe import PackFrame
from bootstack.widgets._impl.primitives.gridframe import GridFrame
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.container import PACK_KEYS, GRID_KEYS, normalize_fill
from bootstack.widgets._core.context import push_container, pop_container
from bootstack.widgets._core.events import register_widget_events, resolve_event
from bootstack.widgets._core.subscription import Subscription
from bootstack.widgets._core.stream import Stream
from bootstack.widgets.types import Event, AccentToken

_TABS_EVENTS: dict[str, str] = {
    "change":    "<<TabChanged>>",
    "tab_close": "<<TabClose>>",
    "tab_add":   "<<TabAdd>>",
}


class TabPage:
    """Context-manager container returned by `Tabs.add()`.

    Place child widgets inside the ``with`` block to add them to the tab's page.

    Args:
        layout: Internal layout mode — ``'vstack'`` (default), ``'hstack'``,
            or ``'grid'``.
        padding: Space inside the page frame.
        gap: Space between children in pixels.
        fill_items: Default fill direction applied to each child.
        expand_items: Whether children expand to fill available space.
        anchor_items: Default anchor applied to each child.
        columns: Column definitions for ``'grid'`` layout.
        rows: Row definitions for ``'grid'`` layout.
        sticky_items: Default sticky value for grid children.
        auto_flow: Grid auto-flow direction — ``'row'`` (default) or
            ``'column'``.
    """

    def __init__(
        self,
        page_widget: tkinter.Widget,
        *,
        layout: str = "vstack",
        padding: Any = None,
        gap: int = 0,
        fill_items: str | None = None,
        expand_items: bool | None = None,
        anchor_items: str | None = None,
        columns: int | list | None = None,
        rows: int | list | None = None,
        sticky_items: str | None = None,
        auto_flow: str = "row",
    ) -> None:
        self._page = page_widget
        self._layout = layout

        if layout in ("vstack", "hstack"):
            self._layout_frame = PackFrame(
                page_widget,
                direction="vertical" if layout == "vstack" else "horizontal",
                padding=padding,
                gap=gap,
                fill_items=normalize_fill(fill_items),
                expand_items=expand_items,
                anchor_items=anchor_items,
            )
        elif layout == "grid":
            self._layout_frame = GridFrame(
                page_widget,
                columns=columns,
                rows=rows,
                padding=padding,
                gap=gap,
                sticky_items=sticky_items,
                auto_flow=auto_flow,
            )
        else:
            raise ValueError(
                f"TabPage layout must be 'vstack', 'hstack', or 'grid', got {layout!r}"
            )

        self._fill_items = normalize_fill(fill_items)
        self._expand_items = expand_items
        self._anchor_items = anchor_items
        self._sticky_items = sticky_items
        self._layout_frame.pack(fill="both", expand=True)

    def _child_master(self) -> tkinter.Widget:
        return self._layout_frame

    def guide_layout(self, child: PublicWidgetBase, **layout_kw: Any) -> None:
        if self._layout == "grid":
            options = {k: v for k, v in layout_kw.items() if k in GRID_KEYS}
            if "sticky" not in options and self._sticky_items:
                options["sticky"] = self._sticky_items
            child._internal.grid(in_=self._child_master(), **options)
            return
        options = {k: v for k, v in layout_kw.items() if k in PACK_KEYS}
        if "fill" not in options and self._fill_items:
            options["fill"] = self._fill_items
        if "expand" not in options and self._expand_items is not None:
            options["expand"] = self._expand_items
        if "anchor" not in options and self._anchor_items:
            options["anchor"] = self._anchor_items
        child._internal.pack(in_=self._child_master(), **options)

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
            `'hover'` = on hover. Default `False`.
        allow_add: Show an add-tab button that fires the `tab_add` event.
        accent: Accent token for the tab bar.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        *,
        orient: Literal["horizontal", "vertical"] = "horizontal",
        show_divider: bool | None = None,
        tab_width: int | Literal["stretch"] | None = None,
        allow_close: bool | Literal["hover"] = False,
        allow_add: bool = False,
        accent: AccentToken | None = None,
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
        internal_kwargs.update(kwargs)

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

        def _target():
            if sequence in ("<<TabAdd>>", "<<TabClose>>"):
                return self._internal._tabs
            return self._internal

        if handler is None:
            def _source(h):
                t = _target()
                _bid = t.bind(sequence, h, add="+")
                return Subscription(t, sequence, _bid)
            return Stream(self._internal, _source=_source)

        t = _target()
        bind_id = t.bind(sequence, handler, add="+")
        return Subscription(t, sequence, bind_id)

    # ----- Tab management -----

    def add(
        self,
        key: str,
        *,
        label: str = "",
        icon: str | None = None,
        closable: bool | Literal["hover"] | None = None,
        close_command: Callable | None = None,
        layout: str = "vstack",
        padding: Any = None,
        gap: int = 0,
        fill_items: str | None = None,
        expand_items: bool | None = None,
        anchor_items: str | None = None,
        columns: int | list | None = None,
        rows: int | list | None = None,
        sticky_items: str | None = None,
        auto_flow: str = "row",
    ) -> TabPage:
        """Add a tab and return a context manager for placing its children.

        Args:
            key: Unique identifier for the tab/page.
            label: Label displayed on the tab.
            icon: Icon name displayed on the tab.
            closable: Close-button visibility for this tab. Overrides `allow_close`.
            close_command: Called when the close button is clicked.
            layout: Internal layout — `'vstack'` (default), `'hstack'`, or `'grid'`.
            gap: Space between children in pixels.
            fill_items: Default fill direction applied to each child.
            expand_items: Whether children expand to fill available space.
            anchor_items: Default anchor applied to each child.
            columns: Column definitions for `'grid'` layout.
            rows: Row definitions for `'grid'` layout.
            sticky_items: Default sticky value for grid children.
            auto_flow: Grid auto-flow direction.

        Returns:
            `TabPage` — use as a context manager to place children.
        """
        add_kwargs: dict[str, Any] = {}
        if icon is not None:
            add_kwargs["icon"] = icon
        if closable is not None:
            add_kwargs["closable"] = closable
        if close_command is not None:
            add_kwargs["close_command"] = close_command

        page_widget = self._internal.add(key, text=label, **add_kwargs)
        return TabPage(
            page_widget,
            layout=layout, padding=padding, gap=gap, fill_items=fill_items,
            expand_items=expand_items, anchor_items=anchor_items,
            columns=columns, rows=rows, sticky_items=sticky_items,
            auto_flow=auto_flow,
        )

    def select(self, key: str) -> None:
        """Select the tab identified by `key`."""
        self._internal.select(key)

    def hide_tab(self, key: str) -> None:
        """Hide a tab without removing it. Restore with `show_tab()`."""
        self._internal.hide_tab(key)

    def show_tab(self, key: str) -> None:
        """Restore a previously hidden tab."""
        self._internal.show_tab(key)

    def forget_tab(self, key: str) -> None:
        """Remove a tab and its page entirely."""
        self._internal.forget_tab(key)

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

    def item(self, key: str) -> Any:
        """Return the tab header item for `key` (for runtime configuration).

        Args:
            key: Tab key assigned in `add()`.
        """
        return self._internal.item(key)

    def items(self) -> tuple:
        """Return all tab header items in insertion order."""
        return self._internal.items()

    # ----- Event shorthands -----

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the selected tab changes.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("change", handler)

    @overload
    def on_tab_close(self) -> Stream: ...
    @overload
    def on_tab_close(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_tab_close(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when a tab's close button is clicked.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("tab_close", handler)

    @overload
    def on_tab_add(self) -> Stream: ...
    @overload
    def on_tab_add(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_tab_add(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the add-tab button is clicked.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("tab_add", handler)


register_widget_events(Tabs, _TABS_EVENTS)

__all__ = ["Tabs", "TabPage", "TabChangeEventData", "TabRef"]