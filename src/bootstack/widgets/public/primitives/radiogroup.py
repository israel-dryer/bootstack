from __future__ import annotations

import tkinter
from typing import Any, Callable

from bootstack.widgets.composites.radiogroup import RadioGroup as _InternalRadioGroup
from bootstack.widgets.public.base import PublicWidgetBase
from bootstack.widgets.public.events import register_widget_events
from bootstack.widgets.public.subscription import Subscription

_RADIOGROUP_EVENTS: dict[str, str] = {
    "change": "<<Change>>",
}


class RadioGroup(PublicWidgetBase):
    """A group of mutually exclusive radio buttons.

    Options are passed at construction via `options=`. Each option is either
    a plain string (label and value are the same) or a `(label, value)` tuple.

    Args:
        options: Choices for the group, e.g. `["A", "B"]` or
            `[("Label A", "a"), ("Label B", "b")]`.
        signal: Reactive `Signal` that holds the selected value.
        value: Initially selected value.
        orient: `'horizontal'` (default) or `'vertical'`.
        label: Group label displayed above (or beside) the buttons.
        accent: Accent token applied to all buttons, e.g. `'primary'`.
        disabled: If True, all buttons are non-interactive.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        options: list[str | tuple[str, Any]] | None = None,
        *,
        signal: Any = None,
        value: Any = None,
        orient: str = "horizontal",
        label: str | None = None,
        accent: str | None = None,
        disabled: bool = False,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {"orient": orient}
        if signal is not None:
            internal_kwargs["signal"] = signal
        if value is not None:
            internal_kwargs["value"] = value
        if label is not None:
            internal_kwargs["text"] = label
        if accent is not None:
            internal_kwargs["accent"] = accent
        if disabled:
            internal_kwargs["state"] = "disabled"
        internal_kwargs.update(kwargs)

        self._internal = _InternalRadioGroup(tk_master, **internal_kwargs)

        # Populate options passed at construction.
        if options:
            for opt in options:
                if isinstance(opt, str):
                    self._internal.add(text=opt, value=opt)
                else:
                    lbl, val = opt
                    self._internal.add(text=lbl, value=val)

        # Trace the signal so <<Change>> fires on the internal Frame whenever
        # the value changes — this lets on_change() use standard Subscription binding.
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
        return self._internal.value

    @value.setter
    def value(self, v: Any) -> None:
        self._internal.value = v

    @property
    def disabled(self) -> bool:
        return self._internal._state == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    # ----- Methods -----

    def add(self, label: str, value: Any | None = None, **kwargs: Any) -> None:
        """Add a radio button to the group at runtime.

        Args:
            label: Display text for the button.
            value: Value assigned when this button is selected. Defaults to `label`.
        """
        self._internal.add(text=label, value=value if value is not None else label, **kwargs)

    def remove(self, value: Any) -> None:
        """Remove the button identified by `value`."""
        self._internal.remove(str(value))

    # ----- Event shorthands -----

    def on_change(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired whenever the selection changes.

        The current value is available via `group.value` inside the handler.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("change", handler)


register_widget_events(RadioGroup, _RADIOGROUP_EVENTS)
