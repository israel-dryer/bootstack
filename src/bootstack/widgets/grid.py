from __future__ import annotations

from typing import Any, Literal

from bootstack.widgets._impl.primitives.gridframe import GridFrame
from bootstack.widgets._core.container import PublicContainer, GRID_KEYS
from bootstack.widgets.types import AccentToken, SurfaceToken, Sticky


class Grid(PublicContainer):
    """A container that arranges children in rows and columns.

    Children are auto-placed left-to-right, top-to-bottom by default.
    Column and row sizes are defined with ``columns=`` and ``rows=``;
    omitting them lets the grid size itself to fit its children.

    Args:
        columns: Column definitions. An integer creates that many
            equal-weight columns. A list sets per-column weights or
            sizes — integers are relative weights, ``'auto'`` sizes to
            content, ``'Npx'`` sets a fixed pixel width (e.g.
            ``'120px'``). Defaults to ``None`` (single column, sized to
            content).
        rows: Row definitions, same format as ``columns``. Defaults to
            ``None`` (rows added automatically as children are placed).
        gap: Space in pixels between cells. An integer applies to both
            axes; a 2-tuple ``(col_gap, row_gap)`` sets them
            independently. Defaults to ``0``.
        sticky_items: Default cell alignment applied to every child
            (e.g. ``'ew'``, ``'nsew'``). Children can override this
            with their own ``sticky=``. Defaults to ``None`` (children
            sit at their natural size in the cell).
        auto_flow: Auto-placement direction. One of ``'row'`` (default),
            ``'column'``, ``'row-dense'``, or ``'column-dense'``.
        padding: Space in pixels between the grid border and its
            content. Accepts an integer (all sides) or a 2-tuple
            ``(x, y)``. Defaults to ``None`` (no padding).
        surface: Background token. Accepts a surface token
            (``'content'``, ``'card'``, ``'chrome'``, ``'overlay'``),
            an accent token (``'primary'``, ``'success'``, etc.), or
            any token with modifiers (e.g. ``'primary[subtle]'``).
            Defaults to ``None`` (inherits from parent surface).
        show_border: When ``True``, draws a 1 px border around the
            grid. Use at least ``padding=1`` to give the border visual
            clearance. Defaults to ``False``.
        width: Fixed width in pixels. Disables frame propagation —
            see the note in :class:`HStack` for sizing behavior.
            Defaults to ``None``.
        height: Fixed height in pixels. Disables frame propagation —
            see the note in :class:`VStack` for sizing behavior.
            Defaults to ``None``.
        parent: Override the context-stack parent widget.
        **kwargs: Self-placement kwargs (``fill=``, ``expand=``,
            ``row=``, ``column=``, etc.) forwarded to the parent
            geometry manager.
    """

    def __init__(
        self,
        *,
        parent: Any = None,
        columns: int | list[int | str] | None = None,
        rows: int | list[int | str] | None = None,
        gap: int | tuple[int, int] = 0,
        sticky_items: Sticky | str | None = None,
        auto_flow: Literal["row", "column", "row-dense", "column-dense", "none"] = "row",
        padding: Any = None,
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
            "sticky_items": sticky_items,
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

        self._sticky_items = sticky_items

        tk_master = self._parent._child_master() if self._parent else None
        self._internal = GridFrame(tk_master, **frame_kwargs)
        self._attach_to_parent(layout_kw)

    def _default_layout_method(self) -> str:
        return "grid"

    def _merge_layout_options(self, child: Any, layout_kw: dict) -> tuple[str, dict]:
        options = {k: v for k, v in layout_kw.items() if k in GRID_KEYS}
        if "sticky" not in options and self._sticky_items:
            options["sticky"] = self._sticky_items
        return ("grid", options)