from __future__ import annotations

from typing import Any

from bootstack.widgets._impl.primitives.separator import Separator as _InternalSeparator
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events


class Separator(PublicWidgetBase):
    """A horizontal or vertical dividing line.

    Args:
        orient: `'horizontal'` (default) or `'vertical'`.
        accent: Accent token for the line colour.
        thickness: Line thickness in pixels.
        length: Fixed length in pixels. If not set, stretches to fill.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        orient: str = "horizontal",
        *,
        accent: str | None = None,
        thickness: int | None = None,
        length: int | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {"orient": orient}
        if accent is not None:
            internal_kwargs["accent"] = accent
        if thickness is not None:
            internal_kwargs["thickness"] = thickness
        if length is not None:
            internal_kwargs["length"] = length
        internal_kwargs.update(kwargs)

        self._internal = _InternalSeparator(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)


register_widget_events(Separator, {})
