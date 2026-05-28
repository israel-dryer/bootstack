from __future__ import annotations

from typing import Any

from bootstack.widgets.primitives.progressbar import Progressbar as _InternalProgressbar
from bootstack.widgets.public.base import PublicWidgetBase
from bootstack.widgets.public.events import register_widget_events


class ProgressBar(PublicWidgetBase):
    """A progress indicator bar.

    Args:
        value: Initial progress value.
        maximum: Value that represents 100% progress. Default `100`.
        mode: `'determinate'` (default) shows a fixed percentage;
            `'indeterminate'` animates continuously.
        orient: `'horizontal'` (default) or `'vertical'`.
        signal: Reactive `Signal` linked to the value.
        accent: Accent token, e.g. `'primary'`, `'success'`.
        variant: Style variant, e.g. `'thin'`.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        value: float = 0,
        *,
        maximum: float = 100,
        mode: str = "determinate",
        orient: str = "horizontal",
        signal: Any = None,
        accent: str | None = None,
        variant: str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "value": value,
            "maximum": maximum,
            "mode": mode,
            "orient": orient,
        }
        if signal is not None:
            internal_kwargs["signal"] = signal
        if accent is not None:
            internal_kwargs["accent"] = accent
        if variant is not None:
            internal_kwargs["variant"] = variant
        internal_kwargs.update(kwargs)

        self._internal = _InternalProgressbar(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Properties -----

    @property
    def value(self) -> float:
        return self._internal.get()

    @value.setter
    def value(self, v: float) -> None:
        self._internal.set(v)

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
