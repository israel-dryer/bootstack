from __future__ import annotations

import tkinter
from typing import Any, Literal

from bootstack.widgets._impl.primitives.panedwindow import PanedWindow as _InternalPanedWindow
from bootstack.widgets._impl.primitives.frame import Frame as _InternalFrame
from bootstack.widgets._impl.primitives.packframe import PackFrame
from bootstack.widgets._impl.primitives.gridframe import GridFrame
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.container import PACK_KEYS, GRID_KEYS, normalize_fill
from bootstack.widgets._core.context import push_container, pop_container
from bootstack.widgets.types import AccentToken, SurfaceToken, Fill, Anchor, Sticky


class SplitPane:
    """Context-manager container returned by `SplitView.add()`.

    Use as a ``with`` block to place child widgets inside the pane.
    Supports the same layout kwargs as standalone layout containers:
    ``layout=``, ``gap=``, ``fill_items=``, ``expand_items=``,
    ``anchor_items=``, ``columns=``, ``rows=``, ``sticky_items=``,
    ``auto_flow=``.
    """

    def __init__(
        self,
        frame: tkinter.Widget,
        *,
        layout: Literal["vstack", "hstack", "grid"] = "vstack",
        padding: Any = None,
        gap: int = 0,
        fill_items: Fill | str | None = None,
        expand_items: bool | None = None,
        anchor_items: Anchor | str | None = None,
        columns: int | list | None = None,
        rows: int | list | None = None,
        sticky_items: Sticky | str | None = None,
        auto_flow: Literal["row", "column", "row-dense", "column-dense"] = "row",
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
    """A resizable split container with panes separated by draggable sashes.

    Add panes with `.add()` and place children inside each pane using the
    returned context manager. Sashes between panes can be dragged at runtime
    to resize them.

    Args:
        orient: Pane arrangement — ``'horizontal'`` (side-by-side, default)
            or ``'vertical'`` (stacked top-to-bottom).
        padding: Space in pixels between the outer border and the pane area.
            Accepts an integer (all sides) or a 2-tuple ``(x, y)``.
        accent: Color intent token applied to the sash. One of
            ``'primary'``, ``'secondary'``, ``'info'``, ``'success'``,
            ``'warning'``, ``'danger'``, ``'default'``.
        surface: Surface token for the pane background. One of
            ``'content'``, ``'card'``, ``'chrome'``, ``'overlay'``.
        sash_thickness: Width (horizontal split) or height (vertical split)
            of the draggable sash in pixels. Defaults to the theme's
            standard sash size (typically 6 px).
        width: Requested width in pixels.
        height: Requested height in pixels.
        parent: Override the context-stack parent.
        **kwargs: Layout placement kwargs (``fill=``, ``expand=``,
            ``row=``, ``column=``, ``sticky=``, etc.) forwarded to the
            parent geometry manager.
    """

    def __init__(
        self,
        orient: Literal["horizontal", "vertical"] = "horizontal",
        *,
        padding: Any = None,
        accent: AccentToken | str | None = None,
        surface: SurfaceToken | str | None = None,
        sash_thickness: int | None = None,
        width: int | None = None,
        height: int | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        pw_kwargs: dict[str, Any] = {"orient": orient}
        if padding is not None:
            pw_kwargs["padding"] = padding
        if accent is not None:
            pw_kwargs["accent"] = accent
        if surface is not None:
            pw_kwargs["surface"] = surface
        if width is not None:
            pw_kwargs["width"] = width
        if height is not None:
            pw_kwargs["height"] = height
        if sash_thickness is not None:
            pw_kwargs["style_options"] = {"sash_thickness": sash_thickness}

        tk_master = self._parent._child_master() if self._parent else None
        self._internal = _InternalPanedWindow(tk_master, **pw_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Pane management -----

    def add(
        self,
        *,
        weight: int = 1,
        min_size: int | None = None,
        layout: Literal["vstack", "hstack", "grid"] = "vstack",
        padding: Any = None,
        gap: int = 0,
        fill_items: Fill | str | None = None,
        expand_items: bool | None = None,
        anchor_items: Anchor | str | None = None,
        columns: int | list | None = None,
        rows: int | list | None = None,
        sticky_items: Sticky | str | None = None,
        auto_flow: Literal["row", "column", "row-dense", "column-dense"] = "row",
    ) -> SplitPane:
        """Add a pane and return a context manager for placing its children.

        Args:
            weight: Relative size weight when the container is resized.
                Panes with higher weight take proportionally more space.
                Defaults to ``1``.
            min_size: Minimum pane size in pixels. The sash cannot be
                dragged past this boundary. Defaults to ``None`` (no minimum).
            layout: Internal pane layout — ``'vstack'`` (children stacked
                top-to-bottom, default), ``'hstack'`` (left-to-right), or
                ``'grid'``.
            padding: Space in pixels inside the pane border. Accepts an
                integer or a 2-tuple ``(x, y)``. Defaults to ``None``.
            gap: Space in pixels between children. Defaults to ``0``.
            fill_items: Default fill direction applied to every child.
                One of ``'x'``, ``'y'``, ``'both'``, or ``'none'``.
            expand_items: Whether children expand to consume extra space.
            anchor_items: Default anchor applied to every child.
            columns: Column definitions for ``'grid'`` layout.
            rows: Row definitions for ``'grid'`` layout.
            sticky_items: Default sticky value for grid children.
            auto_flow: Grid auto-flow direction — ``'row'`` (default),
                ``'column'``, ``'row-dense'``, or ``'column-dense'``.

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
            position: New position in pixels. If ``None``, returns the
                current position.

        Returns:
            Current sash position in pixels when ``position`` is ``None``.
        """
        if position is None:
            return self._internal.sashpos(index)
        self._internal.sashpos(index, position)
        return None
