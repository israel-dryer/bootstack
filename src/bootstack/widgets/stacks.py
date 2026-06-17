from __future__ import annotations

from typing import Any

from bootstack.widgets._impl.primitives.frame import Frame
from bootstack.widgets._impl.primitives.flexframe import FlexFrame
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.container import FlexContainer
from bootstack.widgets.types import (
    AccentToken, SurfaceToken, HAlign, VAlign, HArrange, VArrange, Padding,
)


class _FlexBase(FlexContainer):
    _direction: str  # set by subclass

    def __init__(
        self,
        *,
        parent: Any = None,
        horizontal_items: str = "left",
        vertical_items: str = "top",
        grow_items: bool = False,
        weights: list[int] | None = None,
        gap: int = 0,
        padding: Padding | None = None,
        surface: SurfaceToken | AccentToken | str | None = None,
        show_border: bool = False,
        width: int | None = None,
        height: int | None = None,
        **kwargs: Any,
    ) -> None:
        # Shared implementation for Row/Column. Each subclass declares its own
        # __init__ so Sphinx renders the (axis-specific) params and value types
        # per class.
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        frame_kwargs: dict[str, Any] = {
            "direction": self._direction,
            "horizontal_items": horizontal_items,
            "vertical_items": vertical_items,
            "grow_items": grow_items,
            "weights": weights,
            "gap": gap,
        }
        if padding is not None:
            frame_kwargs["padding"] = padding
        if surface is not None:
            frame_kwargs["surface"] = surface
        if show_border:
            frame_kwargs["show_border"] = show_border
        if width is not None:
            frame_kwargs["width"] = width
        if height is not None:
            frame_kwargs["height"] = height
        if width is not None or height is not None:
            frame_kwargs["propagate"] = False

        tk_master = self._parent._child_master() if self._parent else None
        self._internal = FlexFrame(tk_master, **frame_kwargs)
        self._attach_to_parent(layout_kw)


class Row(_FlexBase):
    """Lays out children left to right along the horizontal axis.

    Children flow in order. Position them on each screen axis: `horizontal_items`
    *arranges the group* along the row (`'left'`/`'center'`/`'right'` or a
    `'space-*'` mode), `vertical_items` *aligns* them up and down
    (`'top'`/`'center'`/`'bottom'`/`'stretch'`), and `grow` / `weights` let
    children share the available width. Drop a `Spacer` between children to push a
    group aside without nesting.

    Example::

        with bs.Row(gap=8, vertical_items="center"):
            bs.Label("Name:")
            bs.TextField(grow=1)

    Args:
        horizontal_items: How the whole group of children is arranged along the
            row — `'left'`, `'center'`, `'right'`, or the `'space-*'` modes. Has
            no effect once any child grows. Defaults to `'left'`.
        vertical_items: Vertical alignment of children — `'top'`, `'center'`,
            `'bottom'`, or `'stretch'` (fill the row's height). Override per child
            with `vertical`. Defaults to `'center'`.
        grow_items: When `True`, every child grows equally to fill the row.
            Defaults to `False`.
        weights: Explicit per-child width weights (e.g. `[1, 2, 1]`) — shorthand
            for setting `grow` on each child positionally. Overrides `grow_items`
            and per-child `grow`. Defaults to `None`.
        gap: Spacing in pixels between adjacent children. Defaults to `0`.
        padding: Space in pixels between the row border and its content. Defaults
            to `None` (no padding).
        surface: Background token. Accepts a surface token, an accent token, or
            any token with modifiers (e.g. `'primary[subtle]'`). Defaults to
            `None` (inherits from parent surface).
        show_border: When `True`, draws a 1 px border around the row frame.
            Defaults to `False`.
        width: Fixed width in pixels. Disables frame propagation so children
            cannot resize the container. Defaults to `None` (size from children).
        height: Fixed height in pixels. Disables frame propagation so children
            cannot resize the container. Defaults to `None` (size from children).
        parent: Override the context-stack parent widget.
        **kwargs: Per-child placement options — `grow` (`bool | int`: `grow=True`
            fills the leftover width with weight 1, `grow=N` takes N shares),
            `vertical` (this child's vertical alignment: `'top'`/`'center'`/
            `'bottom'`/`'stretch'`), `margin`, `index`. See :doc:`/tasks/layout`.
    """
    _direction = "horizontal"

    def __init__(
        self,
        *,
        parent: Any = None,
        horizontal_items: HArrange = "left",
        vertical_items: VAlign = "center",
        grow_items: bool = False,
        weights: list[int] | None = None,
        gap: int = 0,
        padding: Padding | None = None,
        surface: SurfaceToken | AccentToken | str | None = None,
        show_border: bool = False,
        width: int | None = None,
        height: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            parent=parent, horizontal_items=horizontal_items,
            vertical_items=vertical_items, grow_items=grow_items, weights=weights,
            gap=gap, padding=padding, surface=surface, show_border=show_border,
            width=width, height=height, **kwargs,
        )


class Column(_FlexBase):
    """Lays out children top to bottom along the vertical axis.

    Children flow in order. Position them on each screen axis: `vertical_items`
    *arranges the group* down the column (`'top'`/`'center'`/`'bottom'` or a
    `'space-*'` mode), `horizontal_items` *aligns* them left and right
    (`'left'`/`'center'`/`'right'`/`'stretch'`), and `grow` / `weights` let
    children share the available height. Use `horizontal_items='stretch'` for a
    full-width form column.

    Example::

        with bs.Column(gap=12, horizontal_items="stretch", padding=16):
            bs.Label("Title", font="heading-md")
            bs.TextField()
            bs.Button("Submit", accent="primary")

    Args:
        horizontal_items: Horizontal alignment of children — `'left'`,
            `'center'`, `'right'`, or `'stretch'` (fill the column's width).
            Override per child with `horizontal`. Defaults to `'center'`.
        vertical_items: How the whole group of children is arranged down the
            column — `'top'`, `'center'`, `'bottom'`, or the `'space-*'` modes.
            Has no effect once any child grows. Defaults to `'top'`.
        grow_items: When `True`, every child grows equally to fill the column.
            Defaults to `False`.
        weights: Explicit per-child height weights (e.g. `[1, 2, 1]`) — shorthand
            for setting `grow` on each child positionally. Overrides `grow_items`
            and per-child `grow`. Defaults to `None`.
        gap: Spacing in pixels between adjacent children. Defaults to `0`.
        padding: Space in pixels between the column border and its content.
            Defaults to `None` (no padding).
        surface: Background token. Accepts a surface token, an accent token, or
            any token with modifiers (e.g. `'primary[subtle]'`). Defaults to
            `None` (inherits from parent surface).
        show_border: When `True`, draws a 1 px border around the column frame.
            Defaults to `False`.
        width: Fixed width in pixels. Disables frame propagation so children
            cannot resize the container. Defaults to `None` (size from children).
        height: Fixed height in pixels. Disables frame propagation so children
            cannot resize the container. Defaults to `None` (size from children).
        parent: Override the context-stack parent widget.
        **kwargs: Per-child placement options — `grow` (`bool | int`: `grow=True`
            fills the leftover height with weight 1, `grow=N` takes N shares),
            `horizontal` (this child's horizontal alignment: `'left'`/`'center'`/
            `'right'`/`'stretch'`), `margin`, `index`. See :doc:`/tasks/layout`.
    """
    _direction = "vertical"

    def __init__(
        self,
        *,
        parent: Any = None,
        horizontal_items: HAlign = "center",
        vertical_items: VArrange = "top",
        grow_items: bool = False,
        weights: list[int] | None = None,
        gap: int = 0,
        padding: Padding | None = None,
        surface: SurfaceToken | AccentToken | str | None = None,
        show_border: bool = False,
        width: int | None = None,
        height: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            parent=parent, horizontal_items=horizontal_items,
            vertical_items=vertical_items, grow_items=grow_items, weights=weights,
            gap=gap, padding=padding, surface=surface, show_border=show_border,
            width=width, height=height, **kwargs,
        )


class Spacer(PublicWidgetBase):
    """A composable break that pushes neighbors apart in a Row or Column.

    Flexible by default — it absorbs the available stacking-axis space, so items
    before it cluster at the start and items after it at the end. `Spacer(size=N)`
    is instead a fixed N-pixel gap, and `Spacer(weight=N)` shares slack with
    other spacers in proportion to their weights.

    Unlike `horizontal_items`/`vertical_items` (which arrange the *whole* group),
    a `Spacer` is a local break at one point — use it for clustered toolbars and
    footers without nesting::

        with bs.Row(gap=4):
            bs.Button("New"); bs.Button("Open")
            bs.Spacer()
            bs.Button("Settings")

    Args:
        size: Fixed size in pixels. When set, the spacer is a rigid gap rather
            than flexible slack. Defaults to `None` (flexible).
        weight: Relative share of the leftover space when flexible. Ignored when
            `size` is set. Defaults to `1`.
        parent: Override the context-stack parent widget.
    """

    _is_spacer = True

    def __init__(
        self,
        *,
        size: int | None = None,
        weight: int = 1,
        parent: Any = None,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        self._spacer_size = size
        self._spacer_weight = 0 if size is not None else weight
        tk_master = self._parent._child_master() if self._parent else None
        self._internal = Frame(tk_master, width=1, height=1)
        self._attach_to_parent({})
