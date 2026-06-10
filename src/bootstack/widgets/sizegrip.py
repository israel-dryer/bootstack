from __future__ import annotations

from typing import Any

from bootstack.widgets._impl.primitives.sizegrip import SizeGrip as _InternalSizeGrip
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets.types import AccentToken


class SizeGrip(PublicWidgetBase):
    """A resize handle placed in the corner of a window or panel.

    Typically anchored to the bottom-right corner so users can drag to resize
    the parent window.

    Args:
        accent: Accent token for styling.
        parent: Override the context-stack parent.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        *,
        accent: AccentToken | str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {}
        if accent is not None:
            internal_kwargs["accent"] = accent
        # **kwargs is layout-only (split out above) — not forwarded to the internal.

        self._internal = _InternalSizeGrip(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)