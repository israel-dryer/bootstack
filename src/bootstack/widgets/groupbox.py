from __future__ import annotations

import tkinter
from typing import Any

from bootstack.widgets._impl.primitives.labelframe import LabelFrame as _LabelFrame
from bootstack.widgets._impl.primitives.flexframe import FlexFrame
from bootstack.widgets._impl.primitives.gridframe import GridFrame
from bootstack.widgets._core.container import (
    PublicContainer, GRID_KEYS, place_flex_child, grid_sticky,
    _reject_legacy_child_kwargs,
)
from bootstack.widgets.types import (
    AccentToken, Padding, LayoutKind, AutoFlow, LocalizeMode,
)


class GroupBox(PublicContainer):
    """A labeled container that groups related content inside a bordered frame.

    The title is embedded in the top border line, giving the classic fieldset
    look. Children are laid out according to `layout`.

    Args:
        title: Text label embedded in the top border line. Defaults to an
            empty string (border only, no label).
        layout: Internal layout manager. Defaults to `'column'`.
        padding: Space in pixels between the border and the content. A single
            value applies to all sides; `(x, y)` sets the horizontal and
            vertical amounts. Defaults to `16`.
        accent: Color intent token applied to the border and title label.
            When omitted, the border uses the theme's default foreground color.
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
            grows equally to share the main axis. Defaults to `False`.
        columns: Column definitions for `'grid'` layout. An integer sets
            the number of equal-weight columns; a list sets per-column
            weights or sizes — integers are relative weights, `'auto'`
            sizes to content, `'Npx'` sets a fixed pixel width (e.g.
            `[1, 2, 'auto', '120px']`).
        rows: Row definitions for `'grid'` layout, same format as `columns`.
        auto_flow: Grid auto-placement direction. Defaults to `'row'`.
        localize: Whether the title is translated through the catalog — `True`,
            `False`, or `'auto'`. Defaults to the app's `localize_mode`.
        parent: Override the context-stack parent widget.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        title: str = "",
        *,
        layout: LayoutKind = "column",
        padding: Padding | None = 16,
        accent: AccentToken | str | None = None,
        gap: int = 0,
        horizontal_items: str | None = None,
        vertical_items: str | None = None,
        grow_items: bool = False,
        columns: int | list[int | str] | None = None,
        rows: int | list[int | str] | None = None,
        auto_flow: AutoFlow = "row",
        localize: LocalizeMode | None = None,
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

        lf_kwargs: dict[str, Any] = {"text": title, "padding": padding}
        if accent is not None:
            lf_kwargs["accent"] = accent
        if localize is not None:
            lf_kwargs["localize"] = localize

        self._internal = _LabelFrame(tk_master, **lf_kwargs)

        if layout in ("column", "row"):
            self._layout_frame = FlexFrame(
                self._internal,
                direction="vertical" if layout == "column" else "horizontal",
                gap=gap,
                horizontal_items=horizontal_items,
                vertical_items=vertical_items,
                grow_items=grow_items,
            )
        elif layout == "grid":
            self._layout_frame = GridFrame(
                self._internal,
                columns=columns,
                rows=rows,
                gap=gap,
                auto_flow=auto_flow,
            )
        else:
            raise ValueError(
                f"GroupBox layout must be 'column', 'row', or 'grid', got {layout!r}"
            )

        self._horizontal_items = horizontal_items
        self._vertical_items = vertical_items
        self._layout_frame.pack(fill="both", expand=True)
        self._attach_to_parent(layout_kw)

    def _child_master(self) -> tkinter.Misc:
        return self._layout_frame

    def _default_layout_method(self) -> str:
        return "grid" if self._layout == "grid" else "flex"

    def guide_layout(self, child: Any, **layout_kw: Any) -> None:
        if self._layout == "grid":
            return super().guide_layout(child, **layout_kw)
        place_flex_child(self._layout_frame, child, layout_kw, "GroupBox")

    def _merge_layout_options(self, child: Any, layout_kw: dict) -> tuple[str, dict]:
        # Only reached for grid layout (column/row use the flex path above).
        _reject_legacy_child_kwargs(layout_kw, "GroupBox")
        options = {k: v for k, v in layout_kw.items() if k in GRID_KEYS}
        h = layout_kw.get("horizontal") or self._horizontal_items
        v = layout_kw.get("vertical") or self._vertical_items
        options["sticky"] = grid_sticky(h, v)
        return ("grid", options)

    # ----- Properties -----

    @property
    def title(self) -> str:
        """The text embedded in the border."""
        return self._internal.cget("text")

    @title.setter
    def title(self, value: str) -> None:
        self._internal.configure(text=value)