from __future__ import annotations

import tkinter
from typing import Any

from bootstack.widgets._impl.primitives.packframe import PackFrame
from bootstack.widgets._impl.primitives.gridframe import GridFrame
from bootstack.widgets._core.container import (
    PublicContainer, PACK_KEYS, GRID_KEYS, normalize_fill,
)
from bootstack.widgets.types import AccentToken


class Card(PublicContainer):
    """A card-surface container that groups content with an elevated background and border.

    Renders with the ``card`` surface token, so nested cards step up through the
    surface hierarchy automatically (``background`` → ``card`` → ``overlay``).
    Children are arranged by the internal layout selected with ``layout``.

    Args:
        layout: Internal layout manager. One of ``'vstack'`` (default),
            ``'hstack'``, or ``'grid'``.
        padding: Space in pixels between the card border and its content.
            Accepts an integer (all sides) or a 2-tuple ``(x, y)``.
            Defaults to ``16``.
        gap: Space in pixels between child widgets. Defaults to ``0``.
        fill_items: Default ``fill`` direction applied to every child.
            One of ``'x'``, ``'y'``, ``'both'``, or ``'none'``.
            Individual children can override this with their own ``fill=``.
        expand_items: When ``True``, each child expands to take any extra
            space along the pack direction. Defaults to ``None`` (no expand).
        anchor_items: Default alignment anchor applied to each child when it
            does not fill its slot. One of ``'n'``, ``'s'``, ``'e'``,
            ``'w'``, ``'center'``, etc.
        columns: Column definitions for ``'grid'`` layout. An integer sets
            the number of equal-weight columns; a list sets per-column weights
            or sizes (e.g. ``[1, 2, 'auto']``).
        rows: Row definitions for ``'grid'`` layout, same format as
            ``columns``.
        sticky_items: Default cell alignment applied to every grid child
            (e.g. ``'ew'``, ``'nsew'``). Children can override this.
        auto_flow: Grid auto-placement direction. One of ``'row'`` (default),
            ``'column'``, ``'row-dense'``, ``'column-dense'``, or ``'none'``.
        accent: Color intent token applied to the card border. One of
            ``'primary'``, ``'secondary'``, ``'info'``, ``'success'``,
            ``'warning'``, ``'danger'``, ``'muted'``, ``'default'``. When
            set, the card interior uses a subtle tint of that accent. When
            omitted, the card uses the next surface step with no border color.
        parent: Override the context-stack parent widget.
        **kwargs: Self-placement kwargs (``fill=``, ``expand=``,
            ``row=``, ``column=``, etc.) forwarded to the parent
            geometry manager.
    """

    def __init__(
        self,
        *,
        layout: str = "vstack",
        padding: Any = 16,
        gap: int = 0,
        fill_items: str | None = None,
        expand_items: bool | None = None,
        anchor_items: str | None = None,
        columns: int | list | None = None,
        rows: int | list | None = None,
        sticky_items: str | None = None,
        auto_flow: str = "row",
        accent: AccentToken | str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        self._layout = layout
        layout_kw = self._split_layout_kwargs(kwargs)

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

        if layout in ("vstack", "hstack"):
            self._internal = PackFrame(
                tk_master,
                direction="vertical" if layout == "vstack" else "horizontal",
                variant="card",
                show_border=True,
                surface=effective_surface,
                **({"accent": accent} if accent is not None else {}),
                padding=padding,
                gap=gap,
                fill_items=normalize_fill(fill_items),
                expand_items=expand_items,
                anchor_items=anchor_items,
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
                sticky_items=sticky_items,
                auto_flow=auto_flow,
            )
        else:
            raise ValueError(
                f"Card layout must be 'vstack', 'hstack', or 'grid', got {layout!r}"
            )

        self._fill_items = normalize_fill(fill_items)
        self._expand_items = expand_items
        self._anchor_items = anchor_items
        self._sticky_items = sticky_items
        self._attach_to_parent(layout_kw)

    def _child_master(self) -> tkinter.Misc:
        return self._internal

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