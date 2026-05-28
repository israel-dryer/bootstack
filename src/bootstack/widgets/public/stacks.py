from __future__ import annotations

from typing import Any

from bootstack.widgets.primitives.packframe import PackFrame
from bootstack.widgets.public.container import PublicContainer, PACK_KEYS


class _StackBase(PublicContainer):
    _direction: str  # set by subclass

    def __init__(
        self,
        *,
        parent: Any = None,
        # Self-placement (consumed by parent.guide_layout)
        fill: str | None = None,
        expand: bool | None = None,
        anchor: str | None = None,
        # Child-guidance defaults for children
        gap: int = 0,
        padding: Any = None,
        fill_items: str | None = None,
        expand_items: bool | None = None,
        anchor_items: str | None = None,
        # Frame styling
        accent: str | None = None,
        variant: str | None = None,
        surface: str | None = None,
        show_border: bool = False,
        width: int | None = None,
        height: int | None = None,
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
        # Grab any grid/pack/place kwargs the caller also passed
        layout_kw.update(self._split_layout_kwargs(extra_kw))

        frame_kwargs: dict[str, Any] = {
            "direction": self._direction,
            "gap": gap,
            "fill_items": fill_items,
            "expand_items": expand_items,
            "anchor_items": anchor_items,
        }
        if padding is not None:
            frame_kwargs["padding"] = padding
        if accent is not None:
            frame_kwargs["accent"] = accent
        if variant is not None:
            frame_kwargs["variant"] = variant
        if surface is not None:
            frame_kwargs["surface"] = surface
        if show_border:
            frame_kwargs["show_border"] = show_border
        if width is not None:
            frame_kwargs["width"] = width
        if height is not None:
            frame_kwargs["height"] = height
        frame_kwargs.update(extra_kw)

        tk_master = self._parent._child_master() if self._parent else None
        self._internal = PackFrame(tk_master, **frame_kwargs)
        self._attach_to_parent(layout_kw)

    def _default_layout_method(self) -> str:
        return "pack"

    def _merge_layout_options(self, child: Any, layout_kw: dict) -> tuple[str, dict]:
        options = {k: v for k, v in layout_kw.items() if k in PACK_KEYS}
        return ("pack", options)


class HStack(_StackBase):
    """Horizontal stack — lays out children left-to-right."""
    _direction = "horizontal"


class VStack(_StackBase):
    """Vertical stack — lays out children top-to-bottom."""
    _direction = "vertical"
