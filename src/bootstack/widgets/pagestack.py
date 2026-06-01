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
from bootstack.widgets._core.subscription import Subscription
from bootstack.widgets._core.stream import Stream
from bootstack.widgets.types import Event

_PAGESTACK_EVENTS: dict[str, str] = {
    "page_change": "<<PageChange>>",
    "page_mount":  "<<PageMount>>",
}


class StackPage:
    """Context-manager container returned by `PageStack.add()`.

    Accepts the same layout kwargs as `Expander` — `layout=`, `gap=`,
    `fill_items=`, `expand_items=`, `anchor_items=`, `columns=`, `rows=`,
    `sticky_items=`, `auto_flow=`.
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
        fill: Self-placement fill direction in parent.
        expand: Self-placement expand flag.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        *,
        padding: Any = None,
        width: int | None = None,
        height: int | None = None,
        # Self-placement
        fill: str | None = None,
        expand: bool | None = None,
        anchor: str | None = None,
        parent: Any = None,
        **extra_kw: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)

        layout_kw: dict[str, Any] = {}
        if fill is not None:
            layout_kw["fill"] = normalize_fill(fill)
        if expand is not None:
            layout_kw["expand"] = expand
        if anchor is not None:
            layout_kw["anchor"] = anchor
        layout_kw.update(self._split_layout_kwargs(extra_kw))

        ps_kwargs: dict[str, Any] = {}
        if padding is not None:
            ps_kwargs["padding"] = padding
        if width is not None:
            ps_kwargs["width"] = width
        if height is not None:
            ps_kwargs["height"] = height
        ps_kwargs.update(extra_kw)

        tk_master = self._parent._child_master() if self._parent else None
        self._internal = _InternalPageStack(tk_master, **ps_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Page management -----

    def add(
        self,
        key: str,
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
    ) -> StackPage:
        """Add a page and return a context manager for placing its children.

        Args:
            key: Unique identifier for this page.
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
            `StackPage` — use as a context manager to place children.
        """
        page_widget = self._internal.add(key)
        return StackPage(
            page_widget,
            layout=layout, padding=padding, gap=gap, fill_items=fill_items,
            expand_items=expand_items, anchor_items=anchor_items,
            columns=columns, rows=rows, sticky_items=sticky_items,
            auto_flow=auto_flow,
        )

    def remove(self, key: str) -> None:
        """Remove a page and destroy its widget."""
        self._internal.remove(key)

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

    def item(self, key: str) -> Any:
        """Return the page widget for `key`.

        Args:
            key: Page key assigned in `add()`.
        """
        return self._internal.item(key)

    def items(self) -> tuple:
        """Return all page widgets in insertion order."""
        return self._internal.items()

    # ----- Event shorthands -----

    @overload
    def on_page_change(self) -> Stream: ...
    @overload
    def on_page_change(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_page_change(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired after every navigation.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("page_change", handler)

    @overload
    def on_page_mount(self) -> Stream: ...
    @overload
    def on_page_mount(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_page_mount(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when a page is mounted.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("page_mount", handler)


register_widget_events(PageStack, _PAGESTACK_EVENTS)