from __future__ import annotations

from typing import Literal, overload, Any, Callable

from bootstack.widgets._impl.composites.meter import Meter as _InternalMeter
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.events import SliderEvent, Subscription
from bootstack.streams import Stream
from bootstack.widgets.types import AccentToken, Event


class Gauge(PublicWidgetBase):
    """A circular gauge for displaying a value within a range.

    Renders a circular arc gauge with an optional center text display. Supports
    full-circle and semicircle layouts, solid and segmented arcs, and an
    interactive drag mode for value input.

    Args:
        value: Initial value. Defaults to ``0``.
        min_value: Minimum of the range. Defaults to ``0``.
        max_value: Maximum of the range. Defaults to ``100``.
        subtitle: Secondary label displayed below the value text.
        value_prefix: Text prepended to the displayed value (e.g. ``'$'``).
        value_suffix: Text appended to the displayed value (e.g. ``'%'``).
        value_format: Python format string applied to the value.
            Defaults to ``'{:.0f}'`` (integer display).
        size: Diameter of the gauge in pixels. Defaults to ``200``.
        thickness: Width of the arc stroke in pixels. Defaults to ``10``.
        variant: Shape variant. ``'full'`` (default) draws a complete 360° ring;
            ``'semi'`` draws a half-circle arc along the bottom.
        segment_width: Width of each dash segment for a dashed arc style.
            ``0`` (default) draws a solid arc.
        interactive: If ``True``, the user can click or drag the arc to change
            the value. Defaults to ``False``.
        step: Value increment per drag step in interactive mode. Defaults to ``1``.
        show_text: If ``False``, hides the center value text. Defaults to ``True``.
        accent: Color intent token for the arc. One of ``'primary'``,
            ``'secondary'``, ``'info'``, ``'success'``, ``'warning'``,
            ``'danger'``. Defaults to the theme's default color.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        value: int | float = 0,
        *,
        min_value: int | float = 0,
        max_value: int | float = 100,
        subtitle: str | None = None,
        value_prefix: str | None = None,
        value_suffix: str | None = None,
        value_format: str = "{:.0f}",
        size: int = 200,
        thickness: int = 10,
        variant: Literal["full", "semi"] = "full",
        segment_width: int = 0,
        interactive: bool = False,
        step: int | float = 1,
        show_text: bool = True,
        accent: AccentToken | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "value": value,
            "minvalue": min_value,
            "maxvalue": max_value,
            "value_format": value_format,
            "size": size,
            "thickness": thickness,
            "meter_type": variant,
            "segment_width": segment_width,
            "interactive": interactive,
            "step_size": step,
            "show_text": show_text,
        }
        if subtitle is not None:
            internal_kwargs["subtitle"] = subtitle
        if value_prefix is not None:
            internal_kwargs["value_prefix"] = value_prefix
        if value_suffix is not None:
            internal_kwargs["value_suffix"] = value_suffix
        if accent is not None:
            internal_kwargs["accent"] = accent
        internal_kwargs.update(kwargs)

        self._internal = _InternalMeter(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Properties -----

    @property
    def value(self) -> int | float:
        return self._internal.value

    @value.setter
    def value(self, v: int | float) -> None:
        self._internal.value = v

    @property
    def subtitle(self) -> str:
        return self._internal.subtitle

    @subtitle.setter
    def subtitle(self, v: str) -> None:
        self._internal.subtitle = v

    # ----- Event shorthands -----

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[SliderEvent], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[SliderEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the gauge value changes.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("change", handler)


_GAUGE_EVENTS: dict[str, str] = {
    "change": "<<Change>>",
}

register_widget_events(Gauge, _GAUGE_EVENTS)
