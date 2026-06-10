from __future__ import annotations

import tkinter
from typing import overload, Any, Callable

from bootstack.widgets._impl.composites.pagestack import PageStack as _InternalPageStack
from bootstack.widgets._impl.primitives.packframe import PackFrame
from bootstack.widgets._impl.primitives.gridframe import GridFrame
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.container import PACK_KEYS, GRID_KEYS, normalize_fill
from bootstack.widgets._core.context import push_container, pop_container
from bootstack.widgets._core.events import register_widget_events
from bootstack.events import PageChangeEvent, Subscription
from bootstack.streams import Stream
from bootstack.widgets.types import (
    Event, Padding, Fill, Anchor, Sticky, LayoutKind, AutoFlow,
)

_PAGESTACK_EVENTS: dict[str, str] = {
    "page_change": "<<PageChange>>",
    "page_mount":  "<<PageMount>>",
}


class StackPage:
    """A handle for one page — both a layout context and a navigation target.

    Returned by `PageStack.add()` and by `PageStack.item()` / `items()`. Use it
    as a `with` block to place child widgets, and read `key` or call `navigate()`
    to show the page afterward.

    As a context manager it accepts the same layout kwargs as the standalone
    layout containers — `layout=`, `gap=`, `fill_items=`, `expand_items=`,
    `anchor_items=`, `columns=`, `rows=`, `sticky_items=`, `auto_flow=`.
    """

    def __init__(
        self,
        page_widget: tkinter.Widget,
        *,
        key: str,
        owner: "PageStack",
        layout: LayoutKind = "vstack",
        padding: Padding | None = None,
        gap: int = 0,
        fill_items: Fill | str | None = None,
        expand_items: bool | None = None,
        anchor_items: Anchor | str | None = None,
        columns: int | list[int | str] | None = None,
        rows: int | list[int | str] | None = None,
        sticky_items: Sticky | str | None = None,
        auto_flow: AutoFlow = "row",
    ) -> None:
        self._page = page_widget
        self._key = key
        self._owner = owner
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
                f"StackPage layout must be 'vstack', 'hstack', or 'grid', got {layout!r}"
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

    # ----- Page identity and navigation -----

    @property
    def key(self) -> str:
        """The page's unique key, used with `PageStack.item()` / `navigate()`."""
        return self._key

    def navigate(self, data: dict | None = None) -> None:
        """Navigate to this page.

        Args:
            data: Optional data dict passed to the page's mount event.
        """
        self._owner.navigate(self._key, data=data)

    def __enter__(self) -> "StackPage":
        push_container(self)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pop_container(self)


class PageStack(PublicWidgetBase):
    """A browser-style navigation container showing one page at a time.

    Add pages with `.add()` and place children inside each page using the
    returned context manager. Navigate between pages with `navigate()`,
    `back()`, and `forward()`.

    Usage::

        ps = bs.PageStack(fill="both", expand=True)
        with ps.add("home"):
            bs.Label("Home page")
        with ps.add("settings"):
            bs.Label("Settings page")
        ps.navigate("home")

    Args:
        padding: Space around the page area.
        width: Requested width in pixels.
        height: Requested height in pixels.
        parent: Override the context-stack parent.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        *,
        padding: Padding | None = None,
        width: int | None = None,
        height: int | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        ps_kwargs: dict[str, Any] = {}
        if padding is not None:
            ps_kwargs["padding"] = padding
        if width is not None:
            ps_kwargs["width"] = width
        if height is not None:
            ps_kwargs["height"] = height

        self._pages: dict[str, StackPage] = {}
        tk_master = self._parent._child_master() if self._parent else None
        self._internal = _InternalPageStack(tk_master, **ps_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Page management -----

    def add(
        self,
        key: str,
        *,
        layout: LayoutKind = "vstack",
        padding: Padding | None = None,
        gap: int = 0,
        fill_items: Fill | str | None = None,
        expand_items: bool | None = None,
        anchor_items: Anchor | str | None = None,
        columns: int | list[int | str] | None = None,
        rows: int | list[int | str] | None = None,
        sticky_items: Sticky | str | None = None,
        auto_flow: AutoFlow = "row",
    ) -> StackPage:
        """Add a page and return a handle for placing its children and navigating to it.

        Args:
            key: Unique identifier for this page.
            layout: Internal layout. Defaults to `'vstack'`.
            padding: Space inside the page frame. Defaults to `None`.
            gap: Space between children in pixels. Defaults to `0`.
            fill_items: Default fill direction applied to each child.
            expand_items: Whether children expand to fill available space.
            anchor_items: Default anchor applied to each child.
            columns: Column definitions for `'grid'` layout. An integer sets
                the number of equal-weight columns; a list sets per-column
                weights or sizes (e.g. `[1, 2, 'auto', '120px']`).
            rows: Row definitions for `'grid'` layout, same format as `columns`.
            sticky_items: Default sticky value for grid children.
            auto_flow: Grid auto-flow direction. Defaults to `'row'`.

        Returns:
            `StackPage` — use as a context manager to place children, and as a
            handle to `navigate()` to the page.
        """
        page_widget = self._internal.add(key)
        page = StackPage(
            page_widget,
            key=key, owner=self,
            layout=layout, padding=padding, gap=gap, fill_items=fill_items,
            expand_items=expand_items, anchor_items=anchor_items,
            columns=columns, rows=rows, sticky_items=sticky_items,
            auto_flow=auto_flow,
        )
        self._pages[key] = page
        return page

    def remove(self, key: str) -> None:
        """Remove a page and destroy its widget."""
        self._internal.remove(key)
        self._pages.pop(key, None)

    # ----- Navigation -----

    def navigate(self, key: str, data: dict | None = None) -> None:
        """Navigate to the page identified by `key`.

        Args:
            key: Page identifier to navigate to.
            data: Optional data dict passed to the page's mount event.
        """
        self._internal.navigate(key, data=data)

    def back(self) -> None:
        """Navigate to the previous page in history."""
        self._internal.back()

    def forward(self) -> None:
        """Navigate to the next page in history."""
        self._internal.forward()

    # ----- Properties / introspection -----

    @property
    def can_back(self) -> bool:
        """True if backward navigation is possible."""
        return self._internal.can_back()

    @property
    def can_forward(self) -> bool:
        """True if forward navigation is possible."""
        return self._internal.can_forward()

    @property
    def current(self) -> str | None:
        """Key of the currently displayed page, or `None`."""
        result = self._internal.current()
        return result[0] if result else None

    def page_keys(self) -> tuple[str, ...]:
        """All registered page keys in insertion order."""
        return self._internal.keys()

    def item(self, key: str) -> StackPage:
        """Return the page handle for `key`.

        Args:
            key: Page key assigned in `add()`.

        Returns:
            The `StackPage` for that key — read its `key` or `navigate()` to it.
        """
        return self._pages[key]

    def items(self) -> tuple[StackPage, ...]:
        """Return all page handles in insertion order."""
        return tuple(self._pages[k] for k in self._internal.keys())

    # ----- Event shorthands -----

    @overload
    def on_page_change(self) -> Stream: ...
    @overload
    def on_page_change(self, handler: Callable[[PageChangeEvent], Any]) -> Subscription: ...
    def on_page_change(self, handler: Callable[[PageChangeEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired after every navigation.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("page_change", handler)

    @overload
    def on_page_mount(self) -> Stream: ...
    @overload
    def on_page_mount(self, handler: Callable[[PageChangeEvent], Any]) -> Subscription: ...
    def on_page_mount(self, handler: Callable[[PageChangeEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when a page is mounted.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("page_mount", handler)


register_widget_events(PageStack, _PAGESTACK_EVENTS)