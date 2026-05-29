from __future__ import annotations

from typing import Any

from bootstack.widgets.primitives.sizegrip import SizeGrip as _InternalSizeGrip
from bootstack.widgets.public.base import PublicWidgetBase


class SizeGrip(PublicWidgetBase):
    """A resize handle placed in the corner of a window or panel.

    Typically anchored to the bottom-right corner so users can drag to resize
    the parent window.

    Args:
        accent: Accent token for styling.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        *,
        accent: str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {}
        if accent is not None:
            internal_kwargs["accent"] = accent
        internal_kwargs.update(kwargs)

        self._internal = _InternalSizeGrip(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)