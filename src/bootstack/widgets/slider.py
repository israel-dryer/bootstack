from __future__ import annotations

import tkinter
from typing import overload, Any, Callable

from bootstack.widgets._impl.composites.slider.slider import Slider as _InternalSlider
from bootstack.widgets._impl.composites.slider.rangeslider import RangeSlider as _InternalRangeSlider
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._core.subscription import Subscription
from bootstack.widgets._core.stream import Stream

_SLIDER_EVENTS: dict[str, str] = {
    "change": "<<Change>>",
    "commit": "<<Commit>>",
}


class Slider(PublicWidgetBase):
    """A single-handle slider for selecting a value within a range.

    Args:
        value: Initial value.
        min_value: Minimum of the range. Default `0`.
        max_value: Maximum of the range. Default `100`.
        signal: Reactive `Signal[float]` linked to the value.
        orient: `'horizontal'` (default) or `'vertical'`.
        show_value: Show a floating badge displaying the current value.
        show_minmax: Show min/max labels at the track ends.
        tick_step: Spacing between major tick marks. `None` disables ticks.
        minor_ticks: Number of minor ticks between each major tick.
        tick_labels: Show numeric labels at major tick positions.
        tick_format: Format string for tick and badge labels, e.g. `'{:.1f}°C'`.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        value: float = 0,
        *,
        min_value: float = 0,
        max_value: float = 100,
        signal: Any = None,
        orient: str = "horizontal",
        show_value: bool = False,
        show_minmax: bool = False,
        tick_step: float | None = None,
        minor_ticks: int = 0,
        tick_labels: bool = True,
        tick_format: str = "{:.0f}",
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
            "orient": orient,
            "show_value": show_value,
            "show_minmax": show_minmax,
            "tick_interval": tick_step,
            "minor_ticks": minor_ticks,
            "tick_labels": tick_labels,
            "tick_format": tick_format,
        }
        if signal is not None:
            internal_kwargs["signal"] = signal
        internal_kwargs.update(kwargs)

        self._internal = _InternalSlider(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Properties -----

    @property
    def value(self) -> float:
        return self._internal.value

    @value.setter
    def value(self, v: float) -> None:
        self._internal._signal.set(float(v))

    @property
    def min_value(self) -> float:
        return self._internal._minvalue

    @min_value.setter
    def min_value(self, v: float) -> None:
        self._internal.configure(minvalue=float(v))

    @property
    def max_value(self) -> float:
        return self._internal._maxvalue

    @max_value.setter
    def max_value(self, v: float) -> None:
        self._internal.configure(maxvalue=float(v))

    @property
    def disabled(self) -> bool:
        return self._internal._state == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    # ----- Event shorthands -----

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[tkinter.Event], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[tkinter.Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired continuously as the handle moves.

        The current value is available via `slider.value` inside the handler.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("change", handler)

    @overload
    def on_commit(self) -> Stream: ...
    @overload
    def on_commit(self, handler: Callable[[tkinter.Event], Any]) -> Subscription: ...
    def on_commit(self, handler: Callable[[tkinter.Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the handle is released.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("commit", handler)


register_widget_events(Slider, _SLIDER_EVENTS)


class RangeSlider(PublicWidgetBase):
    """A two-handle slider for selecting a low/high value range.

    Args:
        low_value: Initial low-handle value. Default `0`.
        high_value: Initial high-handle value. Default `100`.
        min_value: Minimum of the range. Default `0`.
        max_value: Maximum of the range. Default `100`.
        low_signal: Reactive `Signal[float]` linked to the low handle.
        high_signal: Reactive `Signal[float]` linked to the high handle.
        orient: `'horizontal'` (default) or `'vertical'`.
        show_value: Show floating badges on both handles.
        tick_step: Spacing between major tick marks.
        minor_ticks: Number of minor ticks between each major tick.
        tick_labels: Show numeric labels at major tick positions.
        tick_format: Format string for tick and badge labels.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        low_value: float = 0,
        high_value: float = 100,
        *,
        min_value: float = 0,
        max_value: float = 100,
        low_signal: Any = None,
        high_signal: Any = None,
        orient: str = "horizontal",
        show_value: bool = False,
        tick_step: float | None = None,
        minor_ticks: int = 0,
        tick_labels: bool = True,
        tick_format: str = "{:.0f}",
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "lovalue": low_value,
            "hivalue": high_value,
            "minvalue": min_value,
            "maxvalue": max_value,
            "orient": orient,
            "show_value": show_value,
            "tick_interval": tick_step,
            "minor_ticks": minor_ticks,
            "tick_labels": tick_labels,
            "tick_format": tick_format,
        }
        if low_signal is not None:
            internal_kwargs["lo_signal"] = low_signal
        if high_signal is not None:
            internal_kwargs["hi_signal"] = high_signal
        internal_kwargs.update(kwargs)

        self._internal = _InternalRangeSlider(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Properties -----

    @property
    def low_value(self) -> float:
        return self._internal.lovalue

    @low_value.setter
    def low_value(self, v: float) -> None:
        self._internal._lo_signal.set(float(v))

    @property
    def high_value(self) -> float:
        return self._internal.hivalue

    @high_value.setter
    def high_value(self, v: float) -> None:
        self._internal._hi_signal.set(float(v))

    @property
    def value(self) -> tuple[float, float]:
        """Current `(low, high)` values as a tuple."""
        return (self._internal.lovalue, self._internal.hivalue)

    # ----- Event shorthands -----

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[tkinter.Event], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[tkinter.Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired continuously as either handle moves.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("change", handler)

    @overload
    def on_commit(self) -> Stream: ...
    @overload
    def on_commit(self, handler: Callable[[tkinter.Event], Any]) -> Subscription: ...
    def on_commit(self, handler: Callable[[tkinter.Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when a handle is released.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("commit", handler)


register_widget_events(RangeSlider, _SLIDER_EVENTS)
