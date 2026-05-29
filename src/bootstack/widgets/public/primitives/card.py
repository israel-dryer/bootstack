from __future__ import annotations

import tkinter
from typing import Any

from bootstack.widgets.primitives.card import Card as _InternalCard
from bootstack.widgets.primitives.gridframe import GridFrame
from bootstack.widgets.primitives.packframe import PackFrame
from bootstack.widgets.public.container import (
    PublicContainer, PACK_KEYS, GRID_KEYS, normalize_fill,
)


class Card(PublicContainer):
    """A styled container with a border and padding — the standard surface for
    grouping content.

    Children are laid out according to `layout`. The default (`'vstack'`) stacks
    children top-to-bottom, matching the most common card pattern.

    Args:
        layout: Internal layout manager — `'vstack'` (default), `'hstack'`, or
            `'grid'`.
        padding: Space inside the card between its border and content. Default `16`.
        show_border: Draw a border around the card. Default `True`.
        accent: Accent token. Default `'card'`.
        surface: Surface token for the background.
        width: Requested width in pixels.
        height: Requested height in pixels.
        gap: Space between children (pixels). Passed to the layout frame.
        fill_items: Default fill direction applied to each child — `'horizontal'`,
            `'vertical'`, or `'both'`. Only applies to `'vstack'` and `'hstack'`
            layouts.
        expand_items: Whether children expand to fill available space. Only applies
            to `'vstack'` and `'hstack'` layouts.
        anchor_items: Default anchor applied to each child. Only applies to
            `'vstack'` and `'hstack'` layouts.
        columns: Column definitions passed to the `'grid'` layout frame.
        rows: Row definitions passed to the `'grid'` layout frame.
        sticky_items: Default sticky value for grid children. Only applies to
            `'grid'` layout.
        auto_flow: Grid auto-flow direction. Only applies to `'grid'` layout.
        fill: Self-placement — fill direction in parent.
        expand: Self-placement — expand to fill available space in parent.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        *,
        layout: str = "vstack",
        padding: Any = 16,
        show_border: bool = True,
        accent: str | None = None,
        surface: str | None = None,
        width: int | None = None,
        height: int | None = None,
        # Child guidance — pack layouts
        gap: int = 0,
        fill_items: str | None = None,
        expand_items: bool | None = None,
        anchor_items: str | None = None,
        # Child guidance — grid layout
        columns: int | list | None = None,
        rows: int | list | None = None,
        sticky_items: str | None = None,
        auto_flow: str = "row",
        # Self-placement
        fill: str | None = None,
        expand: bool | None = None,
        anchor: str | None = None,
        parent: Any = None,
        **extra_kw: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        self._layout = layout

        layout_kw: dict[str, Any] = {}
        if fill is not None:
            layout_kw["fill"] = normalize_fill(fill)
        if expand is not None:
            layout_kw["expand"] = expand
        if anchor is not None:
            layout_kw["anchor"] = anchor
        layout_kw.update(self._split_layout_kwargs(extra_kw))

        card_kwargs: dict[str, Any] = {"padding": padding, "show_border": show_border}
        if accent is not None:
            card_kwargs["accent"] = accent
        if surface is not None:
            card_kwargs["surface"] = surface
        if width is not None:
            card_kwargs["width"] = width
        if height is not None:
            card_kwargs["height"] = height
        card_kwargs.update(extra_kw)

        tk_master = self._parent._child_master() if self._parent else None
        self._internal = _InternalCard(tk_master, **card_kwargs)

        if layout in ("vstack", "hstack"):
            self._layout_frame = PackFrame(
                self._internal,
                direction="vertical" if layout == "vstack" else "horizontal",
                gap=gap,
                fill_items=normalize_fill(fill_items),
                expand_items=expand_items,
                anchor_items=anchor_items,
            )
        elif layout == "grid":
            self._layout_frame = GridFrame(
                self._internal,
                columns=columns,
                rows=rows,
                gap=gap,
                sticky_items=sticky_items,
                auto_flow=auto_flow,
            )
        else:
            raise ValueError(f"Card layout must be 'vstack', 'hstack', or 'grid', got {layout!r}")

        self._fill_items = normalize_fill(fill_items)
        self._expand_items = expand_items
        self._anchor_items = anchor_items
        self._sticky_items = sticky_items
        self._layout_frame.pack(fill="both", expand=True)
        self._attach_to_parent(layout_kw)

    def _child_master(self) -> tkinter.Misc:
        return self._layout_frame

    def _default_layout_method(self) -> str:
        return "grid" if self._layout == "grid" else "pack"

    def _merge_layout_options(self, child: Any, layout_kw: dict) -> tuple[str, dict]:
        if self._layout == "grid":
            options = {k: v for k, v in layout_kw.items() if k in GRID_KEYS}
            if "sticky" not in options and self._sticky_items:
                options["sticky"] = self._sticky_items
            return ("grid", options)
        options = {k: v for k, v in layout_kw.items() if k in PACK_KEYS}
        if "fill" not in options and self._fill_items:
            options["fill"] = self._fill_items
        if "expand" not in options and self._expand_items is not None:
            options["expand"] = self._expand_items
        if "anchor" not in options and self._anchor_items:
            options["anchor"] = self._anchor_items
        return ("pack", options)