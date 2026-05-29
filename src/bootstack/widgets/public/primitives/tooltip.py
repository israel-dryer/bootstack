from __future__ import annotations

from typing import Any, Literal

from bootstack.widgets.composites.tooltip import ToolTip as _InternalToolTip
from bootstack.widgets.public.base import PublicWidgetBase


class Tooltip:
    """A hover tooltip attached to a target widget.

    The tooltip appears after `delay` milliseconds when the mouse enters the target
    and disappears on mouse leave or click. Positioning follows the mouse by default;
    pass `anchor_point` and `window_point` to anchor it to the widget instead.

    Args:
        target: The widget to attach the tooltip to.
        text: Tooltip text content.
        delay: Milliseconds before the tooltip appears. Default `250`.
        accent: Accent token for tooltip styling.
        wrap_width: Maximum line width in pixels before text wraps. Default `None` (no wrap).
        justify: Text alignment — `'left'` (default), `'center'`, or `'right'`.
        anchor_point: Widget anchor for tooltip positioning (e.g. `'n'`, `'se'`).
        window_point: Tooltip anchor matched to `anchor_point`.
        auto_flip: Flip the tooltip to stay on screen. Default `True`.
    """

    def __init__(
        self,
        target: PublicWidgetBase | Any,
        text: str = "",
        *,
        delay: int = 250,
        accent: str | None = None,
        wrap_width: int | None = None,
        justify: Literal["left", "center", "right"] = "left",
        anchor_point: str | None = None,
        window_point: str | None = None,
        auto_flip: bool | Literal["vertical", "horizontal"] = True,
    ) -> None:
        tk_widget = target.tk if isinstance(target, PublicWidgetBase) else target

        internal_kwargs: dict[str, Any] = {
            "text": text,
            "delay": delay,
            "justify": justify,
            "auto_flip": auto_flip,
        }
        if accent is not None:
            internal_kwargs["accent"] = accent
        if wrap_width is not None:
            internal_kwargs["wraplength"] = wrap_width
        if anchor_point is not None:
            internal_kwargs["anchor_point"] = anchor_point
        if window_point is not None:
            internal_kwargs["window_point"] = window_point

        self._internal = _InternalToolTip(tk_widget, **internal_kwargs)

    def destroy(self) -> None:
        """Remove the tooltip and unbind all event handlers."""
        self._internal.destroy()