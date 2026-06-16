from __future__ import annotations

from typing import Any

from bootstack.widgets._impl.primitives.gridframe import GridFrame
from bootstack.widgets._core.container import (
    PublicContainer, GRID_KEYS, grid_sticky, _reject_legacy_child_kwargs,
)
from bootstack.widgets.types import (
    AccentToken, SurfaceToken, HAlign, VAlign, Padding, AutoFlow,
)


class Grid(PublicContainer):
    """A container that arranges children in rows and columns.

    Children are auto-placed left-to-right, top-to-bottom by default. Column and
    row sizes are set with weighted `columns=` / `rows=`; in-cell alignment is
    controlled with `horizontal_items` and `vertical_items`, overridable per
    child with `horizontal` / `vertical`.

    Args:
        columns: Column definitions. An integer creates that many
            equal-weight columns. A list sets per-column weights or
            sizes — integers are relative weights, `'auto'` sizes to
            content, `'Npx'` sets a fixed pixel width (e.g. `'120px'`).
            Defaults to `None` (single column, sized to content).
        rows: Row definitions, same format as `columns`. Defaults to
            `None` (rows added automatically as children are placed).
        gap: Space in pixels between cells. An integer applies to both
            axes; a 2-tuple `(col_gap, row_gap)` sets them
            independently. Defaults to `0`.
        horizontal_items: Horizontal in-cell alignment of every child —
            `'stretch'` (fill the cell width), `'left'`, `'center'`, or
            `'right'`. Override per child with `horizontal`. Defaults to
            `'stretch'`.
        vertical_items: Vertical in-cell alignment of every child —
            `'stretch'` (fill the cell height), `'top'`, `'center'`, or
            `'bottom'`. Override per child with `vertical`. Defaults to
            `'stretch'`.
        auto_flow: Auto-placement direction. Defaults to `'row'`.
        padding: Space in pixels between the grid border and its
            content. Defaults to `None` (no padding).
        surface: Background token. Accepts a surface token, an accent
            token, or any token with modifiers (e.g. `'primary[subtle]'`).
            Defaults to `None` (inherits from parent surface).
        show_border: When `True`, draws a 1 px border around the
            grid. Use at least `padding=1` to give the border visual
            clearance. Defaults to `False`.
        width: Fixed width in pixels. Disables frame propagation —
            see the note in :class:`Row` for sizing behavior.
            Defaults to `None`.
        height: Fixed height in pixels. Disables frame propagation —
            see the note in :class:`Column` for sizing behavior.
            Defaults to `None`.
        parent: Override the context-stack parent widget.
        **kwargs: Per-child placement options — `row`, `column`,
            `rowspan`, `columnspan`, `horizontal`, `vertical`,
            `margin`. See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        *,
        parent: Any = None,
        columns: int | list[int | str] | None = None,
        rows: int | list[int | str] | None = None,
        gap: int | tuple[int, int] = 0,
        horizontal_items: HAlign = "stretch",
        vertical_items: VAlign = "stretch",
        auto_flow: AutoFlow = "row",
        padding: Padding | None = None,
        surface: SurfaceToken | AccentToken | str | None = None,
        show_border: bool = False,
        width: int | None = None,
        height: int | None = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        frame_kwargs: dict[str, Any] = {
            "rows": rows,
            "columns": columns,
            "gap": gap,
            "auto_flow": auto_flow,
        }
        for k, v in {
            "padding": padding,
            "surface": surface,
        }.items():
            if v is not None:
                frame_kwargs[k] = v
        if show_border:
            frame_kwargs["show_border"] = True
        if width is not None:
            frame_kwargs["width"] = width
        if height is not None:
            frame_kwargs["height"] = height

        self._horizontal_items = horizontal_items
        self._vertical_items = vertical_items

        tk_master = self._parent._child_master() if self._parent else None
        self._internal = GridFrame(tk_master, **frame_kwargs)
        self._attach_to_parent(layout_kw)

    def _default_layout_method(self) -> str:
        return "grid"

    def _merge_layout_options(self, child: Any, layout_kw: dict) -> tuple[str, dict]:
        _reject_legacy_child_kwargs(layout_kw, "Grid")
        options = {k: v for k, v in layout_kw.items() if k in GRID_KEYS}
        # Derive the cell sticky from per-child horizontal/vertical, each falling
        # back to the container default for its axis.
        h = layout_kw.get("horizontal") or self._horizontal_items
        v = layout_kw.get("vertical") or self._vertical_items
        options["sticky"] = grid_sticky(h, v)
        return ("grid", options)
