from __future__ import annotations

import tkinter
from typing import Any, Callable

from bootstack.widgets._impl.composites.numericentry import NumericEntry as _InternalNumericEntry
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._core.field_mixin import FieldAddonMixin
from bootstack.widgets._core.subscription import Subscription
from bootstack.widgets.textfield import _INNER_ENTRY_SEQUENCES

_NUMBER_FIELD_EVENTS: dict[str, str] = {
    "change":  "<<Change>>",
    "submit":  "<Return>",
    "valid":   "<<Valid>>",
    "invalid": "<<Invalid>>",
}


class NumberField(FieldAddonMixin, PublicWidgetBase):
    """A numeric input field with optional stepper buttons.

    Args:
        value: Initial numeric value.
        label: Label displayed above the field.
        message: Hint text displayed below the field.
        min_value: Minimum allowed value (inclusive).
        max_value: Maximum allowed value (inclusive).
        step: Increment/decrement step size.
        show_steppers: If False, hides the +/− stepper buttons.
        required: If True, field cannot be left empty.
        disabled: If True, field is non-interactive.
        read_only: If True, value is visible but not editable.
        width: Width in character cells.
        accent: Accent token for the focus ring.
        density: Widget density — `'default'` or `'compact'`.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        value: int | float = 0,
        *,
        label: str | None = None,
        message: str | None = None,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        step: int | float = 1,
        show_steppers: bool = True,
        required: bool = False,
        disabled: bool = False,
        read_only: bool = False,
        width: int | None = None,
        accent: str | None = None,
        density: str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "value": value,
            "increment": step,
            "show_spin_buttons": show_steppers,
        }
        if label is not None:
            internal_kwargs["label"] = label
        if message is not None:
            internal_kwargs["message"] = message
        if min_value is not None:
            internal_kwargs["minvalue"] = min_value
        if max_value is not None:
            internal_kwargs["maxvalue"] = max_value
        if required:
            internal_kwargs["required"] = True
        if disabled:
            internal_kwargs["state"] = "disabled"
        elif read_only:
            internal_kwargs["state"] = "readonly"
        if width is not None:
            internal_kwargs["width"] = width
        if accent is not None:
            internal_kwargs["accent"] = accent
        if density is not None:
            internal_kwargs["density"] = density
        internal_kwargs.update(kwargs)

        self._internal = _InternalNumericEntry(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Event routing -----

    def _entry_widget(self) -> tkinter.Misc:
        return self._internal._entry

    def on(self, event: str, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        from bootstack.widgets._core.events import resolve_event
        sequence = resolve_event(self, str(event))
        widget = self._entry_widget() if sequence in _INNER_ENTRY_SEQUENCES else self._internal
        bind_id = widget.bind(sequence, handler, add="+")
        return Subscription(widget, sequence, bind_id)

    # ----- Properties -----

    @property
    def value(self) -> int | float | None:
        return self._internal.value

    @value.setter
    def value(self, v: int | float) -> None:
        self._internal.value = v

    @property
    def disabled(self) -> bool:
        return str(self._internal._entry.cget("state")) == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    @property
    def read_only(self) -> bool:
        return str(self._internal._entry.cget("state")) == "readonly"

    @read_only.setter
    def read_only(self, v: bool) -> None:
        self._internal.configure(state="readonly" if v else "normal")

    # ----- Methods -----

    def increment(self, steps: int = 1) -> None:
        """Increment the value by `steps` × step size."""
        self._internal.step(steps)

    def decrement(self, steps: int = 1) -> None:
        """Decrement the value by `steps` × step size."""
        self._internal.step(-steps)

    # ----- Event shorthands -----

    def on_change(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired when the value is committed.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("change", handler)

    def on_submit(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired on Enter key.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("submit", handler)

    def on_valid(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired when validation passes.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("valid", handler)

    def on_invalid(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired when validation fails.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("invalid", handler)


register_widget_events(NumberField, _NUMBER_FIELD_EVENTS)
