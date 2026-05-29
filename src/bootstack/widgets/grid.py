from __future__ import annotations

from typing import Any

from bootstack.widgets._impl.primitives.gridframe import GridFrame
from bootstack.widgets._core.container import PublicContainer, GRID_KEYS


class Grid(PublicContainer):
    """Grid container — lays out children in rows and columns."""

    def __init__(
        self,
        *,
        parent: Any = None,
        rows: int | list | None = None,
        columns: int | list | None = None,
        gap: int | tuple[int, int] = 0,
        sticky_items: str | None = None,
        auto_flow: str = "row",
        padding: Any = None,
        accent: str | None = None,
        variant: str | None = None,
        surface: str | None = None,
        show_border: bool = False,
        width: int | None = None,
        height: int | None = None,
        # Self-placement
        fill: str | None = None,
        expand: bool | None = None,
        anchor: str | None = None,
        **extra_kw: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)

        layout_kw: dict[str, Any] = {}
        if fill is not None:
            layout_kw["fill"] = fill
        if expand is not None:
            layout_kw["expand"] = expand
        if anchor is not None:
            layout_kw["anchor"] = anchor
        layout_kw.update(self._split_layout_kwargs(extra_kw))

        frame_kwargs: dict[str, Any] = {
            "rows": rows,
            "columns": columns,
            "gap": gap,
            "sticky_items": sticky_items,
            "auto_flow": auto_flow,
        }
        for k, v in {
            "padding": padding,
            "accent": accent,
            "variant": variant,
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
        frame_kwargs.update(extra_kw)

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
