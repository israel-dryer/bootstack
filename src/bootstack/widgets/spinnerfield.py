from __future__ import annotations

import tkinter
from typing import Any, Callable

from bootstack.widgets._impl.composites.spinnerentry import SpinnerEntry as _InternalSpinnerEntry
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._core.field_mixin import FieldAddonMixin
from bootstack.widgets._core.subscription import Subscription
from bootstack.widgets.textfield import _INNER_ENTRY_SEQUENCES

_SPINNER_FIELD_EVENTS: dict[str, str] = {
    "change": "<<Change>>",
    "submit": "<Return>",
}


class SpinnerField(FieldAddonMixin, PublicWidgetBase):
    """A text-entry field with spin buttons for stepping through values.

    Supports two modes: a fixed list of text values (`options=`) or a numeric
    range (`min_value=` / `max_value=`). Exactly one mode should be used.

    Args:
        value: Initial value — a string (text mode) or number (numeric mode).
        options: Fixed list of string values to step through (text mode).
        min_value: Minimum value for numeric range mode.
        max_value: Maximum value for numeric range mode.
        step: Increment step size for numeric mode. Default `1`.
        wrap: If True, values wrap around at the boundaries.
        label: Label displayed above the field.
        message: Hint text displayed below the field.
        required: If True, field cannot be left empty.
        disabled: If True, field is non-interactive.
        width: Width in character cells.
        accent: Accent token for the focus ring.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        value: int | float | str = "",
        *,
        options: list[str] | None = None,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        step: int | float = 1,
        wrap: bool = False,
        label: str | None = None,
        message: str | None = None,
        required: bool = False,
        disabled: bool = False,
        width: int | None = None,
        accent: str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "value": value,
            "increment": step,
            "wrap": wrap,
        }
        if options is not None:
            internal_kwargs["values"] = options
        if min_value is not None:
            internal_kwargs["minvalue"] = min_value
        if max_value is not None:
            internal_kwargs["maxvalue"] = max_value
        if label is not None:
            internal_kwargs["label"] = label
        if message is not None:
            internal_kwargs["message"] = message
        if required:
            internal_kwargs["required"] = True
        if disabled:
            internal_kwargs["state"] = "disabled"
        if width is not None:
            internal_kwargs["width"] = width
        if accent is not None:
            internal_kwargs["accent"] = accent
        internal_kwargs.update(kwargs)

        self._internal = _InternalSpinnerEntry(tk_master, **internal_kwargs)
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
    def value(self) -> str:
        """Current value as a string."""
        return self._internal.value

    @value.setter
    def value(self, v: Any) -> None:
        self._internal.value = v

    @property
    def options(self) -> list[str] | None:
        """The fixed list of text values, or `None` in numeric mode."""
        return self._internal._values

    @options.setter
    def options(self, v: list[str]) -> None:
        self._internal.configure(values=v)

    @property
    def disabled(self) -> bool:
        return str(self._internal._entry.cget("state")) == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    # ----- Event shorthands -----

    def on_change(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired when the value changes.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("change", handler)

    def on_submit(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired when Enter is pressed.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("submit", handler)


register_widget_events(SpinnerField, _SPINNER_FIELD_EVENTS)