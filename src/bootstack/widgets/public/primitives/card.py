from __future__ import annotations

from typing import Any

from bootstack.widgets.primitives.card import Card as _InternalCard
from bootstack.widgets.public.container import PublicContainer, PACK_KEYS, normalize_fill


class Card(PublicContainer):
    """A styled container with a border and padding — the standard surface for grouping content.

    Children placed inside the context block are packed vertically by default.

    Args:
        padding: Space inside the card between its border and content. Default `16`.
        show_border: Draw a border around the card. Default `True`.
        accent: Accent token. Default `'card'`.
        surface: Surface token for the background.
        width: Requested width in pixels.
        height: Requested height in pixels.
        fill: Self-placement — fill direction in parent (`'x'`, `'y'`, `'both'`).
        expand: Self-placement — expand to fill available space in parent.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        *,
        padding: Any = 16,
        show_border: bool = True,
        accent: str | None = None,
        surface: str | None = None,
        width: int | None = None,
        height: int | None = None,
        # Self-placement
        fill: str | None = None,
        expand: bool | None = None,
        anchor: str | None = None,
        parent: Any = None,
        **extra_kw: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)

        layout_kw: dict[str, Any] = {}
        if fill is not None:
            layout_kw["fill"] = normalize_fill(fill)
        if expand is not None:
            layout_kw["expand"] = expand
        if anchor is not None:
            layout_kw["anchor"] = anchor
        layout_kw.update(self._split_layout_kwargs(extra_kw))

        card_kwargs: dict[str, Any] = {
            "padding": padding,
            "show_border": show_border,
        }
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
        self._attach_to_parent(layout_kw)

    def _default_layout_method(self) -> str:
        return "pack"

    def _merge_layout_options(self, child: Any, layout_kw: dict) -> tuple[str, dict]:
        options = {k: v for k, v in layout_kw.items() if k in PACK_KEYS}
        return ("pack", options)