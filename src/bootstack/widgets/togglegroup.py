from __future__ import annotations

import tkinter
from typing import Any, Callable

from bootstack.widgets._impl.composites.togglegroup import ToggleGroup as _InternalToggleGroup
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._core.subscription import Subscription

_TOGGLEGROUP_EVENTS: dict[str, str] = {
    "change": "<<Change>>",
}


class ToggleGroup(PublicWidgetBase):
    """A group of toggle buttons — single-select or multi-select.

    Options are passed at construction via `options=`. Each option is either
    a plain string (label and value are the same) or a `(label, value)` tuple.

    Args:
        options: Choices, e.g. `["Grid", "List"]` or `[("Label", "val"), ...]`.
        mode: `'single'` (default, radio behaviour) or `'multi'` (checkbox behaviour).
        signal: Reactive `Signal` holding the selected value(s).
        value: Initially selected value (string for `'single'`, set for `'multi'`).
        orient: `'horizontal'` (default) or `'vertical'`.
        accent: Accent token applied to all buttons.
        variant: Style variant, e.g. `'outline'`, `'ghost'`.
        disabled: If True, all buttons are non-interactive.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        options: list[str | tuple[str, Any]] | None = None,
        *,
        mode: str = "single",
        signal: Any = None,
        value: Any = None,
        orient: str = "horizontal",
        accent: str | None = None,
        variant: str | None = None,
        disabled: bool = False,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "mode": mode,
            "orient": orient,
        }
        if signal is not None:
            internal_kwargs["signal"] = signal
        if value is not None:
            internal_kwargs["value"] = value
        if accent is not None:
            internal_kwargs["accent"] = accent
        if variant is not None:
            internal_kwargs["variant"] = variant
        if disabled:
            internal_kwargs["state"] = "disabled"
        internal_kwargs.update(kwargs)

        self._internal = _InternalToggleGroup(tk_master, **internal_kwargs)

        # Populate options passed at construction.
        if options:
            for opt in options:
                if isinstance(opt, str):
                    self._internal.add(text=opt, value=opt)
                else:
                    lbl, val = opt
                    self._internal.add(text=lbl, value=val)

        # Trace signal → <<Change>> for consistent Subscription-based on_change().
        def _on_value_change(_new_value: Any) -> None:
            try:
                self._internal.event_generate("<<Change>>")
            except tkinter.TclError:
                pass

        self._trace_id = self._internal.signal.subscribe(_on_value_change)
        self._attach_to_parent(layout_kw)

    # ----- Properties -----

    @property
    def value(self) -> Any:
        return self._internal.get()

    @value.setter
    def value(self, v: Any) -> None:
        self._internal.set(v)

    @property
    def disabled(self) -> bool:
        return self._internal._state == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    # ----- Methods -----

    def add(self, label: str, value: Any | None = None, **kwargs: Any) -> None:
        """Add a toggle button at runtime.

        Args:
            label: Display text.
            value: Value this button represents. Defaults to `label`.
        """
        self._internal.add(text=label, value=value if value is not None else label, **kwargs)

    # ----- Event shorthands -----

    def on_change(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired whenever the selection changes.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("change", handler)


register_widget_events(ToggleGroup, _TOGGLEGROUP_EVENTS)
