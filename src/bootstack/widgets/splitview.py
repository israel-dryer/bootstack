from __future__ import annotations

import tkinter
from typing import Any

from bootstack.widgets._impl.primitives.panedwindow import PanedWindow as _InternalPanedWindow
from bootstack.widgets._impl.primitives.frame import Frame as _InternalFrame
from bootstack.widgets._impl.primitives.packframe import PackFrame
from bootstack.widgets._impl.primitives.gridframe import GridFrame
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.container import PACK_KEYS, GRID_KEYS, normalize_fill
from bootstack.widgets._core.context import push_container, pop_container


class SplitPane:
    """Context-manager container returned by `SplitView.add()`.

    Accepts the same layout kwargs as `Expander` — `layout=`, `gap=`,
    `fill_items=`, `expand_items=`, `anchor_items=`, `columns=`, `rows=`,
    `sticky_items=`, `auto_flow=`.
    """

    def __init__(
        self,
        frame: tkinter.Widget,
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
        self._frame = frame
        self._layout = layout

        if layout in ("vstack", "hstack"):
            self._layout_frame = PackFrame(
                frame,
                direction="vertical" if layout == "vstack" else "horizontal",
                padding=padding,
                gap=gap,
                fill_items=normalize_fill(fill_items),
                expand_items=expand_items,
                anchor_items=anchor_items,
            )
        elif layout == "grid":
            self._layout_frame = GridFrame(
                frame,
                columns=columns,
                rows=rows,
                padding=padding,
                gap=gap,
                sticky_items=sticky_items,
                auto_flow=auto_flow,
            )
        else:
            raise ValueError(
                f"SplitPane layout must be 'vstack', 'hstack', or 'grid', got {layout!r}"
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

    def __enter__(self) -> "SplitPane":
        push_container(self)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pop_container(self)


class SplitView(PublicWidgetBase):
    """A resizable split container with one or more panes separated by draggable sashes.

    Add panes with `.add()` and place children inside each pane using the
    returned context manager.

    Usage::

        sv = bs.SplitView(fill="both", expand=True)
        with sv.add(weight=1):
            bs.Label("Left pane")
        with sv.add(weight=2):
            bs.Label("Right pane")

    Args:
        orient: `'horizontal'` (default, panes side-by-side) or `'vertical'` (stacked).
        padding: Space around the pane area.
        accent: Accent token for styling.
        width: Requested width in pixels.
        height: Requested height in pixels.
        fill: Self-placement fill direction in parent.
        expand: Self-placement expand flag.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        orient: str = "horizontal",
        *,
        padding: Any = None,
        accent: str | None = None,
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

        pw_kwargs: dict[str, Any] = {"orient": orient}
        if padding is not None:
            pw_kwargs["padding"] = padding
        if accent is not None:
            pw_kwargs["accent"] = accent
        if width is not None:
            pw_kwargs["width"] = width
        if height is not None:
            pw_kwargs["height"] = height
        pw_kwargs.update(extra_kw)

        tk_master = self._parent._child_master() if self._parent else None
        self._internal = _InternalPanedWindow(tk_master, **pw_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Pane management -----

    def add(
        self,
        *,
        weight: int = 1,
        min_size: int | None = None,
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
    ) -> SplitPane:
        """Add a pane and return a context manager for placing its children.

        Args:
            weight: Relative size weight when the container is resized.
            min_size: Minimum pane size in pixels.
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
            `SplitPane` — use as a context manager to place children.
        """
        frame = _InternalFrame(self._internal)
        add_kw: dict[str, Any] = {"weight": weight}
        if min_size is not None:
            add_kw["minsize"] = min_size
        self._internal.add(frame, **add_kw)
        return SplitPane(
            frame,
            layout=layout, padding=padding, gap=gap, fill_items=fill_items,
            expand_items=expand_items, anchor_items=anchor_items,
            columns=columns, rows=rows, sticky_items=sticky_items,
            auto_flow=auto_flow,
        )

    # ----- Sash control -----

    @property
    def sash_positions(self) -> list[int]:
        """Current position of every sash in pixels, in order."""
        n = len(self._internal.panes())
        return [self._internal.sashpos(i) for i in range(max(0, n - 1))]

    def sash_position(self, index: int, position: int | None = None) -> int | None:
        """Get or set the position of a sash.

        Args:
            index: Zero-based sash index.
            position: New position in pixels. If `None`, returns the current position.

        Returns:
            Current sash position in pixels when `position` is `None`.
        """
        if position is None:
            return self._internal.sashpos(index)
        self._internal.sashpos(index, position)
        return None