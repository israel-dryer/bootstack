from __future__ import annotations

import tkinter
from typing import Any

from bootstack.widgets._impl.primitives.flexframe import FlexFrame
from bootstack.widgets._impl.primitives.gridframe import GridFrame
from bootstack.widgets._core.container import (
    PublicContainer, GRID_KEYS, place_flex_child, grid_sticky,
    _reject_legacy_child_kwargs,
)
from bootstack.widgets.types import (
    AccentToken, Padding, LayoutKind, AutoFlow,
)


class Card(PublicContainer):
    """A card-surface container that groups content with an elevated background and border.

    Renders with the `card` surface token, so nested cards step up through the
    surface hierarchy automatically (`background` → `card` → `overlay`).
    Children are arranged by the internal layout selected with `layout`.

    Args:
        layout: Internal layout manager. Defaults to `'column'`.
        padding: Space in pixels between the card border and its content.
            A single value applies to all sides; `(x, y)` sets the horizontal
            and vertical amounts. Defaults to `16`.
        gap: Space in pixels between child widgets. Defaults to `0`.
        horizontal_items: How children sit on the horizontal axis — edge values
            `'left'`/`'center'`/`'right'`/`'stretch'`, plus the `'space-*'` modes
            when horizontal is the stacking axis (`'row'`). Override per child
            with `horizontal`. Defaults to `'stretch'` for `'grid'`, else
            `'left'`.
        vertical_items: How children sit on the vertical axis — edge values
            `'top'`/`'center'`/`'bottom'`/`'stretch'`, plus the `'space-*'` modes
            when vertical is the stacking axis (`'column'`). Override per child
            with `vertical`. Defaults to `'stretch'` for `'grid'`, else `'top'`.
        grow_items: For `'column'`/`'row'` layout, when `True` every child
            grows equally to share the stacking axis. Defaults to `False`.
        columns: Column definitions for `'grid'` layout. An integer sets
            the number of equal-weight columns; a list sets per-column weights
            or sizes — integers are relative weights, `'auto'` sizes to
            content, `'Npx'` sets a fixed pixel width (e.g.
            `[1, 2, 'auto', '120px']`).
        rows: Row definitions for `'grid'` layout, same format as `columns`.
        auto_flow: Grid auto-placement direction. Defaults to `'row'`.
        accent: Color intent token applied to the card border. When set, the
            card interior uses a subtle tint of that accent. When omitted, the
            card uses the next surface step with no border color.
        parent: Override the context-stack parent widget.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        *,
        layout: LayoutKind = "column",
        padding: Padding | None = 16,
        gap: int = 0,
        horizontal_items: str | None = None,
        vertical_items: str | None = None,
        grow_items: bool = False,
        columns: int | list[int | str] | None = None,
        rows: int | list[int | str] | None = None,
        auto_flow: AutoFlow = "row",
        accent: AccentToken | str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        self._layout = layout
        layout_kw = self._split_layout_kwargs(kwargs)

        # One horizontal_items/vertical_items pair serves both modes; the sensible
        # default differs — grid cells fill (stretch), stacked children sit at the
        # leading edge (left/top).
        if horizontal_items is None:
            horizontal_items = "stretch" if layout == "grid" else "left"
        if vertical_items is None:
            vertical_items = "stretch" if layout == "grid" else "top"

        tk_master = self._parent._child_master() if self._parent else None

        # Determine the surface children will sit on:
        # - With accent: always accent[subtle], fixed — accent is the identity, not an elevation marker
        # - Without accent: alternate between card and card_raised at each nesting level
        _SURFACE_STEPS = {
            "background":  "card",
            "content":     "card",
            "card":        "card_raised",
            "card_raised": "card",
        }
        parent_surface = getattr(tk_master, '_surface', 'background') or 'background'
        effective_surface = f'{accent}[subtle]' if accent is not None else _SURFACE_STEPS.get(parent_surface, 'card')

        if layout in ("column", "row"):
            self._internal = FlexFrame(
                tk_master,
                direction="vertical" if layout == "column" else "horizontal",
                variant="card",
                show_border=True,
                surface=effective_surface,
                **({"accent": accent} if accent is not None else {}),
                padding=padding,
                gap=gap,
                horizontal_items=horizontal_items,
                vertical_items=vertical_items,
                grow_items=grow_items,
            )
        elif layout == "grid":
            self._internal = GridFrame(
                tk_master,
                variant="card",
                show_border=True,
                surface=effective_surface,
                **({"accent": accent} if accent is not None else {}),
                padding=padding,
                columns=columns,
                rows=rows,
                gap=gap,
                auto_flow=auto_flow,
            )
        else:
            raise ValueError(
                f"Card layout must be 'column', 'row', or 'grid', got {layout!r}"
            )

        self._horizontal_items = horizontal_items
        self._vertical_items = vertical_items
        self._attach_to_parent(layout_kw)

    def _child_master(self) -> tkinter.Misc:
        return self._internal

    def _default_layout_method(self) -> str:
        return "grid" if self._layout == "grid" else "flex"

    def guide_layout(self, child: Any, **layout_kw: Any) -> None:
        if self._layout == "grid":
            return super().guide_layout(child, **layout_kw)
        place_flex_child(self._internal, child, layout_kw, "Card")

    def _merge_layout_options(self, child: Any, layout_kw: dict) -> tuple[str, dict]:
        # Only reached for grid layout (column/row use the flex path above).
        _reject_legacy_child_kwargs(layout_kw, "Card")
        options = {k: v for k, v in layout_kw.items() if k in GRID_KEYS}
        h = layout_kw.get("horizontal") or self._horizontal_items
        v = layout_kw.get("vertical") or self._vertical_items
        options["sticky"] = grid_sticky(h, v)
        return ("grid", options)