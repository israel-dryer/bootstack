from __future__ import annotations

from typing import Any

from bootstack.widgets._impl.primitives.separator import Separator as _InternalSeparator
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets.types import AccentToken, Orient


class Divider(PublicWidgetBase):
    """A horizontal or vertical dividing line.

    Renders a thin themed line that can be used to visually divide sections
    of a layout. The line color inherits from the active surface by default
    and can be overridden with an accent token. (For invisible flexible space
    between items, use :class:`Spacer <bootstack.Spacer>` instead.)

    Args:
        orient: Direction of the line. Defaults to `'horizontal'`.
        accent: Color intent token applied to the line. When omitted, the
            line color is derived from the active surface.
        thickness: Line thickness in pixels. Defaults to the theme value
            (typically 1 px).
        length: Fixed length in pixels. When omitted the line stretches to
            fill the available space along its axis.
        parent: Override the context-stack parent widget.
        **kwargs: Layout placement options applied by the parent container —
            `grow`, `horizontal`, `vertical`, `margin`, `row`, `column`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        orient: Orient | str = "horizontal",
        *,
        accent: AccentToken | str | None = None,
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

        self._internal = _InternalSeparator(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)


register_widget_events(Divider, {})
