from __future__ import annotations

from typing import Any

from bootstack.widgets._impl.primitives.labelframe import LabelFrame as _InternalLabelFrame
from bootstack.widgets._core.container import PublicContainer, PACK_KEYS, normalize_fill


class GroupBox(PublicContainer):
    """A labelled container that groups related content inside a bordered frame.

    Args:
        title: Text displayed in the border label.
        title_anchor: Where the label sits on the border edge —
            `'nw'` (default), `'n'`, `'ne'`, `'w'`, `'e'`, `'sw'`, `'s'`, `'se'`.
        padding: Space between the border and the content area.
        accent: Accent token for border styling.
        relief: Border style (e.g. `'groove'`, `'ridge'`, `'flat'`).
        border_width: Border thickness in pixels.
        width: Requested width in pixels.
        height: Requested height in pixels.
        fill: Self-placement fill direction in parent (`'x'`, `'y'`, `'both'`).
        expand: Self-placement expand flag.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        title: str = "",
        *,
        title_anchor: str | None = None,
        padding: Any = None,
        accent: str | None = None,
        relief: str | None = None,
        border_width: int | None = None,
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

        frame_kwargs: dict[str, Any] = {"text": title}
        if title_anchor is not None:
            frame_kwargs["labelanchor"] = title_anchor
        if padding is not None:
            frame_kwargs["padding"] = padding
        if accent is not None:
            frame_kwargs["accent"] = accent
        if relief is not None:
            frame_kwargs["relief"] = relief
        if border_width is not None:
            frame_kwargs["borderwidth"] = border_width
        if width is not None:
            frame_kwargs["width"] = width
        if height is not None:
            frame_kwargs["height"] = height
        frame_kwargs.update(extra_kw)

        tk_master = self._parent._child_master() if self._parent else None
        self._internal = _InternalLabelFrame(tk_master, **frame_kwargs)
        self._attach_to_parent(layout_kw)

    def _default_layout_method(self) -> str:
        return "pack"

    def _merge_layout_options(self, child: Any, layout_kw: dict) -> tuple[str, dict]:
        options = {k: v for k, v in layout_kw.items() if k in PACK_KEYS}
        return ("pack", options)

    # ----- Properties -----

    @property
    def title(self) -> str:
        """The border label text."""
        return self._internal.cget("text")

    @title.setter
    def title(self, value: str) -> None:
        self._internal.configure(text=value)