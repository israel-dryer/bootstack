from __future__ import annotations

from typing import Any, Literal, TYPE_CHECKING

from bootstack.widgets._impl.primitives.progressbar import Progressbar as _InternalProgressbar
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets.types import AccentToken, Orient

if TYPE_CHECKING:
    from bootstack.signals import Signal


class ProgressBar(PublicWidgetBase):
    """A progress indicator bar.

    Displays determinate progress (a fixed percentage fill) or indeterminate
    progress (a looping animation) for operations whose duration is unknown.

    Args:
        value: Initial progress value. Defaults to `0`.
        max_value: Value that represents 100% progress. Defaults to `100`.
        mode: `'determinate'` shows a fixed fill proportional to
            `value / max_value`; `'indeterminate'` runs a looping animation.
            Default `'determinate'`.
        orient: Track orientation. Default `'horizontal'`.
        signal: Reactive `Signal` two-way bound to `value`.
        accent: Color intent token for the bar. Defaults to the theme's default
            color.
        variant: Style variant. `'thin'` reduces the bar height.
        parent: Override the context-stack parent.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        value: float = 0,
        *,
        max_value: float = 100,
        mode: Literal["determinate", "indeterminate"] = "determinate",
        orient: Orient = "horizontal",
        signal: Signal | None = None,
        accent: AccentToken | str | None = None,
        variant: Literal["thin"] | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "value": value,
            "maximum": max_value,
            "mode": mode,
            "orient": orient,
        }
        if signal is not None:
            internal_kwargs["signal"] = signal
        if accent is not None:
            internal_kwargs["accent"] = accent
        if variant is not None:
            internal_kwargs["variant"] = variant

        self._internal = _InternalProgressbar(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Properties -----

    @property
    def value(self) -> float:
        """The current progress value."""
        return self._internal.get()

    @value.setter
    def value(self, v: float) -> None:
        self._internal.set(v)

    @property
    def max_value(self) -> float:
        """The value that represents 100% progress."""
        return float(self._internal.cget("maximum"))

    @max_value.setter
    def max_value(self, v: float) -> None:
        self._internal.configure(maximum=float(v))

    # ----- Methods -----

    def start(self, interval: int = 50) -> None:
        """Start indeterminate animation. `interval` is the step delay in ms."""
        self._internal.start(interval)

    def stop(self) -> None:
        """Stop indeterminate animation."""
        self._internal.stop()

    def step(self, amount: float = 1.0) -> None:
        """Advance the value by `amount`."""
        self._internal.step(amount)


register_widget_events(ProgressBar, {})
