from __future__ import annotations

from typing import overload, Any, Callable, TYPE_CHECKING

from bootstack.widgets._impl.composites.slider.slider import Slider as _InternalSlider
from bootstack.widgets._impl.composites.slider.rangeslider import RangeSlider as _InternalRangeSlider
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.events import RangeSliderCommitEvent, RangeSliderEvent, SliderCommitEvent, SliderEvent, Subscription
from bootstack.streams import Stream
from bootstack.widgets.types import AccentToken, Event, Orient

if TYPE_CHECKING:
    from bootstack.signals import Signal

_SLIDER_EVENTS: dict[str, str] = {
    "change": "<<Change>>",
    "commit": "<<Commit>>",
}


class Slider(PublicWidgetBase):
    """A single-handle slider for selecting a numeric value within a range.

    The initial value is the first positional argument. All options are
    keyword-only.

    Args:
        value: Initial value. Defaults to ``0``.
        min_value: Minimum of the range. Defaults to ``0``.
        max_value: Maximum of the range. Defaults to ``100``.
        signal: Reactive ``Signal[float]`` linked to the slider value. The
            slider and signal stay in sync automatically.
        orient: Track orientation. ``'horizontal'`` (default) or
            ``'vertical'``.
        show_value: If ``True``, shows a floating badge with the current
            value above the handle. Defaults to ``False``.
        show_minmax: If ``True``, shows min/max labels at the track ends.
            Defaults to ``False``.
        tick_step: Spacing between major tick marks. ``None`` disables
            ticks entirely.
        minor_ticks: Number of minor tick marks between each major tick.
            Defaults to ``0``.
        tick_labels: If ``True``, shows numeric labels at major tick
            positions. Defaults to ``True``.
        tick_format: Format string applied to tick and badge labels.
            Defaults to ``'{:.0f}'``.
        accent: Accent token controlling the fill, handle, and focus ring
            color. One of ``'primary'`` (default), ``'secondary'``,
            ``'success'``, ``'warning'``, ``'danger'``.
        disabled: If ``True``, slider is non-interactive. Defaults to
            ``False``.
        parent: Explicit parent widget. If omitted, the current
            context-stack container is used.
    """

    def __init__(
        self,
        value: float = 0,
        *,
        min_value: float = 0,
        max_value: float = 100,
        signal: "Signal[float] | None" = None,
        orient: Orient = "horizontal",
        show_value: bool = False,
        show_minmax: bool = False,
        tick_step: float | None = None,
        minor_ticks: int = 0,
        tick_labels: bool = True,
        tick_format: str = "{:.0f}",
        accent: AccentToken | str | None = None,
        disabled: bool = False,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "value":        value,
            "minvalue":     min_value,
            "maxvalue":     max_value,
            "orient":       orient,
            "show_value":   show_value,
            "show_minmax":  show_minmax,
            "tick_interval": tick_step,
            "minor_ticks":  minor_ticks,
            "tick_labels":  tick_labels,
            "tick_format":  tick_format,
        }
        if signal is not None:
            internal_kwargs["signal"] = signal
        if accent is not None:
            internal_kwargs["accent"] = accent
        if disabled:
            internal_kwargs["state"] = "disabled"

        self._internal = _InternalSlider(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Properties -----

    @property
    def value(self) -> float:
        """The current slider value."""
        return self._internal.value

    @value.setter
    def value(self, v: float) -> None:
        self._internal._signal.set(float(v))

    @property
    def signal(self) -> "Signal[float]":
        """The reactive ``Signal[float]`` linked to this slider."""
        return self._internal.signal

    @property
    def min_value(self) -> float:
        """The minimum value of the slider range."""
        return self._internal._minvalue

    @min_value.setter
    def min_value(self, v: float) -> None:
        self._internal.configure(minvalue=float(v))

    @property
    def max_value(self) -> float:
        """The maximum value of the slider range."""
        return self._internal._maxvalue

    @max_value.setter
    def max_value(self, v: float) -> None:
        self._internal.configure(maxvalue=float(v))

    @property
    def disabled(self) -> bool:
        """Whether the slider is non-interactive."""
        return self._internal._state == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    # ----- Event shorthands -----

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[SliderEvent], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[SliderEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired continuously as the handle moves.

        The current value is available via ``slider.value`` inside the handler.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("change", handler)

    @overload
    def on_commit(self) -> Stream: ...
    @overload
    def on_commit(self, handler: Callable[[SliderCommitEvent], Any]) -> Subscription: ...
    def on_commit(self, handler: Callable[[SliderCommitEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the handle is released.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("commit", handler)


register_widget_events(Slider, _SLIDER_EVENTS)


class RangeSlider(PublicWidgetBase):
    """A two-handle slider for selecting a low/high value range.

    The initial handle positions are the first two positional arguments.
    All options are keyword-only.

    Args:
        low_value: Initial low-handle value. Defaults to ``0``.
        high_value: Initial high-handle value. Defaults to ``100``.
        min_value: Minimum of the range. Defaults to ``0``.
        max_value: Maximum of the range. Defaults to ``100``.
        low_signal: Reactive ``Signal[float]`` linked to the low handle.
        high_signal: Reactive ``Signal[float]`` linked to the high handle.
        orient: Track orientation. ``'horizontal'`` (default) or
            ``'vertical'``.
        show_value: If ``True``, shows floating badges on both handles.
            Defaults to ``False``.
        tick_step: Spacing between major tick marks. ``None`` disables
            ticks entirely.
        minor_ticks: Number of minor tick marks between each major tick.
            Defaults to ``0``.
        tick_labels: If ``True``, shows numeric labels at major tick
            positions. Defaults to ``True``.
        tick_format: Format string applied to tick and badge labels.
            Defaults to ``'{:.0f}'``.
        accent: Accent token controlling the fill, handles, and focus ring
            color. One of ``'primary'`` (default), ``'secondary'``,
            ``'success'``, ``'warning'``, ``'danger'``.
        disabled: If ``True``, slider is non-interactive. Defaults to
            ``False``.
        parent: Explicit parent widget. If omitted, the current
            context-stack container is used.
    """

    def __init__(
        self,
        low_value: float = 0,
        high_value: float = 100,
        *,
        min_value: float = 0,
        max_value: float = 100,
        low_signal: "Signal[float] | None" = None,
        high_signal: "Signal[float] | None" = None,
        orient: Orient = "horizontal",
        show_value: bool = False,
        tick_step: float | None = None,
        minor_ticks: int = 0,
        tick_labels: bool = True,
        tick_format: str = "{:.0f}",
        accent: AccentToken | str | None = None,
        disabled: bool = False,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "lovalue":       low_value,
            "hivalue":       high_value,
            "minvalue":      min_value,
            "maxvalue":      max_value,
            "orient":        orient,
            "show_value":    show_value,
            "tick_interval": tick_step,
            "minor_ticks":   minor_ticks,
            "tick_labels":   tick_labels,
            "tick_format":   tick_format,
        }
        if low_signal is not None:
            internal_kwargs["lo_signal"] = low_signal
        if high_signal is not None:
            internal_kwargs["hi_signal"] = high_signal
        if accent is not None:
            internal_kwargs["accent"] = accent
        if disabled:
            internal_kwargs["state"] = "disabled"

        self._internal = _InternalRangeSlider(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Properties -----

    @property
    def low_value(self) -> float:
        """The current low-handle value."""
        return self._internal.lovalue

    @low_value.setter
    def low_value(self, v: float) -> None:
        self._internal._lo_signal.set(float(v))

    @property
    def high_value(self) -> float:
        """The current high-handle value."""
        return self._internal.hivalue

    @high_value.setter
    def high_value(self, v: float) -> None:
        self._internal._hi_signal.set(float(v))

    @property
    def value(self) -> tuple[float, float]:
        """Current ``(low, high)`` values as a tuple."""
        return (self._internal.lovalue, self._internal.hivalue)

    @property
    def low_signal(self) -> "Signal[float]":
        """The reactive ``Signal[float]`` linked to the low handle."""
        return self._internal._lo_signal

    @property
    def high_signal(self) -> "Signal[float]":
        """The reactive ``Signal[float]`` linked to the high handle."""
        return self._internal._hi_signal

    @property
    def min_value(self) -> float:
        """The minimum value of the slider range."""
        return self._internal._minvalue

    @min_value.setter
    def min_value(self, v: float) -> None:
        self._internal.configure(minvalue=float(v))

    @property
    def max_value(self) -> float:
        """The maximum value of the slider range."""
        return self._internal._maxvalue

    @max_value.setter
    def max_value(self, v: float) -> None:
        self._internal.configure(maxvalue=float(v))

    @property
    def disabled(self) -> bool:
        """Whether the slider is non-interactive."""
        return self._internal._state == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    # ----- Event shorthands -----

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[RangeSliderEvent], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[RangeSliderEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired continuously as either handle moves.

        The current values are available via ``slider.low_value`` and
        ``slider.high_value`` inside the handler.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("change", handler)

    @overload
    def on_commit(self) -> Stream: ...
    @overload
    def on_commit(self, handler: Callable[[RangeSliderCommitEvent], Any]) -> Subscription: ...
    def on_commit(self, handler: Callable[[RangeSliderCommitEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when a handle is released.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("commit", handler)


register_widget_events(RangeSlider, _SLIDER_EVENTS)
