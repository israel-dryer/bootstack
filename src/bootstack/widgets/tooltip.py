from __future__ import annotations

from typing import Any, Literal

from bootstack.widgets._impl.composites.tooltip import ToolTip as _InternalToolTip
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets.types import AccentToken, Anchor, Justify


class Tooltip:
    """A hover tooltip attached to a target widget.

    The tooltip appears after `delay` milliseconds when the mouse enters the
    target and disappears when the mouse leaves or clicks. Positioning follows
    the mouse cursor by default; pass `anchor_point` and `window_point` to
    pin the tooltip to a specific edge of the widget instead.

    Args:
        target: Widget to attach the tooltip to. Accepts any bootstack widget.
            When the target is a container, the tooltip shows while hovering
            anywhere inside it, including over its children present at attach
            time. For children added later, call `refresh_bindings()`.
        text: Tooltip text content. Defaults to `''`.
        delay: Milliseconds before the tooltip appears on mouse enter. Defaults
            to `250`.
        accent: Semantic color accent. Defaults to the theme's elevated
            background color.
        wrap_width: Maximum text width in pixels before wrapping. Defaults to
            `None` (auto-scaled to approximately 300 px).
        justify: Text alignment inside the tooltip. Defaults to `'left'`.
        anchor_point: Anchor on the *target widget* the tooltip attaches to.
            Defaults to `None` (tooltip follows the mouse).
        window_point: Anchor on the *tooltip window* aligned to `anchor_point`.
            Defaults to the opposite of `anchor_point` when it is set.
        auto_flip: Keep the tooltip fully on screen. `True` flips both axes,
            `False` disables flipping, `'vertical'` or `'horizontal'` restricts
            flipping to one axis. Defaults to `True`.
    """

    def __init__(
        self,
        target: PublicWidgetBase | Any,
        text: str = "",
        *,
        delay: int = 250,
        accent: AccentToken | str | None = None,
        wrap_width: int | None = None,
        justify: Justify = "left",
        anchor_point: Anchor | None = None,
        window_point: Anchor | None = None,
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

    def refresh_bindings(self) -> None:
        """Re-cover a container target's subtree after adding children to it.

        A tooltip on a container covers the children present when it was
        created. Add more children later and call this so hovering them shows
        the tip too. Safe to call repeatedly — already-covered children are
        left untouched.
        """
        self._internal.refresh_bindings()

    @property
    def text(self) -> str:
        """The tooltip text. Assign to change it — a visible tooltip updates
        immediately, and the next hover shows the new text."""
        return self._internal._text

    @text.setter
    def text(self, value: str) -> None:
        self._internal.text = value

    def destroy(self) -> None:
        """Remove the tooltip and unbind all event handlers."""
        self._internal.destroy()