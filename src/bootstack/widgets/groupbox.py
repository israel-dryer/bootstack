from __future__ import annotations

import tkinter
from typing import Any

from bootstack.widgets._impl.primitives.frame import Frame as _Frame
from bootstack.widgets._impl.primitives.label import Label as _Label
from bootstack.widgets._impl.primitives.packframe import PackFrame
from bootstack.widgets._impl.primitives.gridframe import GridFrame
from bootstack.widgets._core.container import (
    PublicContainer, PACK_KEYS, GRID_KEYS, normalize_fill,
)


class GroupBox(PublicContainer):
    """A labelled container that groups related content inside a bordered frame.

    Renders as a small title label above a bordered content area — no
    background bleed around the border. The content area has its own surface
    token, independent of the surrounding page surface.

    Children are laid out according to `layout`. The default (`'vstack'`) stacks
    children top-to-bottom and fills them horizontally — the most common pattern
    for a group of form fields or stacked widgets.

    Args:
        title: Text displayed above the bordered content area.
        layout: Internal layout manager — `'vstack'` (default), `'hstack'`, or
            `'grid'`.
        padding: Space between the border and the content area. Default `16`.
        surface: Surface token for the content area background.
        accent: Accent token for the title label and border.
        gap: Space between children in pixels.
        fill_items: Default fill direction applied to each child.
        expand_items: Whether children expand to fill available space.
        anchor_items: Default anchor applied to each child.
        columns: Column definitions for `'grid'` layout.
        rows: Row definitions for `'grid'` layout.
        sticky_items: Default sticky value for grid children.
        auto_flow: Grid auto-flow direction.
        fill: Self-placement fill direction in parent.
        expand: Self-placement expand flag.
        anchor: Self-placement anchor.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        title: str = "",
        *,
        layout: str = "vstack",
        padding: Any = 16,
        surface: str | None = None,
        accent: str | None = None,
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

        tk_master = self._parent._child_master() if self._parent else None

        # Outer PackFrame — transparent, just stacks title + content vertically
        self._internal = PackFrame(tk_master, direction="vertical", gap=4)

        # Title label — small, muted, no background of its own
        if title:
            self._title_label = _Label(
                self._internal,
                text=title,
                font="label",
                accent=accent or "secondary",
            )
            self._title_label.pack(anchor="w", padx=2)
        else:
            self._title_label = None

        # Content frame styled as a card. Surface must be set explicitly so
        # _surface is propagated to all child widgets via _refresh_descendant_surfaces.
        effective_surface = surface if surface is not None else (accent or "card")
        content_kwargs: dict[str, Any] = {
            "variant": "card",
            "surface": effective_surface,
            "padding": padding,
        }
        if accent is not None:
            content_kwargs["accent"] = accent
        self._content_frame = _Frame(self._internal, **content_kwargs)
        self._content_frame.pack(fill="both", expand=True)

        # Layout engine inside the content frame
        if layout in ("vstack", "hstack"):
            self._layout_frame = PackFrame(
                self._content_frame,
                direction="vertical" if layout == "vstack" else "horizontal",
                gap=gap,
                fill_items=normalize_fill(fill_items),
                expand_items=expand_items,
                anchor_items=anchor_items,
            )
        elif layout == "grid":
            self._layout_frame = GridFrame(
                self._content_frame,
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
        """The title label text."""
        return self._title_label.cget("text") if self._title_label else ""

    @title.setter
    def title(self, value: str) -> None:
        if self._title_label:
            self._title_label.configure(text=value)