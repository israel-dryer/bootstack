from __future__ import annotations

import tkinter
from typing import Any

from bootstack.widgets._impl.primitives.labelframe import LabelFrame as _LabelFrame
from bootstack.widgets._impl.primitives.packframe import PackFrame
from bootstack.widgets._impl.primitives.gridframe import GridFrame
from bootstack.widgets._core.container import (
    PublicContainer, PACK_KEYS, GRID_KEYS, normalize_fill,
)
from bootstack.widgets.types import (
    AccentToken, Padding, Fill, Anchor, Sticky, LayoutKind, AutoFlow,
)


class GroupBox(PublicContainer):
    """A labeled container that groups related content inside a bordered frame.

    The title is embedded in the top border line, giving the classic fieldset
    look. Children are laid out according to `layout`.

    Args:
        title: Text label embedded in the top border line. Defaults to an
            empty string (border only, no label).
        layout: Internal layout manager. Defaults to `'vstack'`.
        padding: Space in pixels between the border and the content. A single
            value applies to all sides; `(x, y)` sets the horizontal and
            vertical amounts. Defaults to `16`.
        accent: Color intent token applied to the border and title label.
            When omitted, the border uses the theme's default foreground color.
        gap: Space in pixels between child widgets. Defaults to `0`.
        fill_items: Default `fill` direction applied to every child.
            Individual children can override this with their own `fill=`.
        expand_items: When `True`, each child expands to consume extra
            space along the pack direction. Defaults to `None`.
        anchor_items: Default alignment anchor for children that do not fill
            their slot.
        columns: Column definitions for `'grid'` layout. An integer sets
            the number of equal-weight columns; a list sets per-column
            weights or sizes — integers are relative weights, `'auto'`
            sizes to content, `'Npx'` sets a fixed pixel width (e.g.
            `[1, 2, 'auto', '120px']`).
        rows: Row definitions for `'grid'` layout, same format as `columns`.
        sticky_items: Default cell alignment for every grid child
            (e.g. `'ew'`, `'nsew'`). Children can override this.
        auto_flow: Grid auto-placement direction. Defaults to `'row'`.
        parent: Override the context-stack parent widget.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        title: str = "",
        *,
        layout: LayoutKind = "vstack",
        padding: Padding | None = 16,
        accent: AccentToken | str | None = None,
        gap: int = 0,
        fill_items: Fill | str | None = None,
        expand_items: bool | None = None,
        anchor_items: Anchor | str | None = None,
        columns: int | list[int | str] | None = None,
        rows: int | list[int | str] | None = None,
        sticky_items: Sticky | str | None = None,
        auto_flow: AutoFlow = "row",
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        self._layout = layout
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        lf_kwargs: dict[str, Any] = {"text": title, "padding": padding}
        if accent is not None:
            lf_kwargs["accent"] = accent

        self._internal = _LabelFrame(tk_master, **lf_kwargs)

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
            raise ValueError(
                f"GroupBox layout must be 'vstack', 'hstack', or 'grid', got {layout!r}"
            )

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

    # ----- Properties -----

    @property
    def title(self) -> str:
        """The text embedded in the border."""
        return self._internal.cget("text")

    @title.setter
    def title(self, value: str) -> None:
        self._internal.configure(text=value)