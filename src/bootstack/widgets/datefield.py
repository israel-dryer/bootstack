from __future__ import annotations

import tkinter
from datetime import date
from typing import overload, Any, Callable, Iterable, TYPE_CHECKING

from bootstack.widgets._impl.composites.dateentry import DateEntry as _InternalDateEntry
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import resolve_event, register_widget_events
from bootstack.widgets._core.field_mixin import FieldAddonMixin
from bootstack.widgets._core.subscription import Subscription
from bootstack.widgets._core.stream import Stream
from bootstack.widgets.textfield import _INNER_ENTRY_SEQUENCES
from bootstack.widgets.types import AccentToken, Event, WidgetDensity

if TYPE_CHECKING:
    from bootstack.signals import Signal

_DATEFIELD_EVENTS: dict[str, str] = {
    "change":   "<<Change>>",
    "validate": "<<Validate>>",
    "valid":    "<<Valid>>",
    "invalid":  "<<Invalid>>",
    "submit":   "<Return>",
    "focus":    "<FocusIn>",
    "blur":     "<FocusOut>",
}


class DateField(FieldAddonMixin, PublicWidgetBase):
    """A date input field with an optional calendar picker button.

    In `'single'` mode `value` returns a `date`; in `'range'` mode it returns
    a `(start, end)` tuple of dates.

    Args:
        value: Initial date value — a `date` object or an ISO string
            (`'YYYY-MM-DD'`). `None` for an empty field.
        value_format: Display format token. Default `'longDate'`.
        label: Label displayed above the field.
        message: Hint text displayed below the field.
        textsignal: Reactive `Signal[str]` bound to the field text. The
            field value and signal stay in sync automatically.
        show_picker_button: Show the calendar icon button. Default `True`.
        picker_title: Title of the picker dialog.
        picker_first_weekday: First day of week in the picker (0=Mon … 6=Sun).
            Default `6` (Sunday).
        selection_mode: `'single'` (default) or `'range'`. In range mode the
            entry is read-only and dates must be selected via the picker.
        range_start: Pre-selected range start date (range mode only).
        range_end: Pre-selected range end date (range mode only).
        min_date: Earliest selectable date.
        max_date: Latest selectable date.
        disabled_dates: Dates that cannot be selected.
        required: Mark field as required; blocks empty submission.
        disabled: If `True`, field is non-interactive.
        read_only: If `True`, value is visible but not editable.
        accent: Accent color for the focus ring — `'primary'`, `'secondary'`,
            `'info'`, `'success'`, `'warning'`, `'danger'`, or `'default'`.
            Default `'primary'`.
        density: Widget density — `'default'` or `'compact'`.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        value: str | date | None = None,
        *,
        value_format: str = "longDate",
        label: str | None = None,
        message: str | None = None,
        textsignal: "Signal[str] | None" = None,
        show_picker_button: bool = True,
        picker_title: str | None = None,
        picker_first_weekday: int = 6,
        selection_mode: str = "single",
        range_start: date | str | None = None,
        range_end: date | str | None = None,
        min_date: date | str | None = None,
        max_date: date | str | None = None,
        disabled_dates: Iterable[date | str] | None = None,
        required: bool = False,
        disabled: bool = False,
        read_only: bool = False,
        accent: AccentToken | str | None = None,
        density: WidgetDensity | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "value_format": value_format,
            "show_picker_button": show_picker_button,
            "picker_first_weekday": picker_first_weekday,
            "selection_mode": selection_mode,
        }
        if value is not None:
            internal_kwargs["value"] = value
        if label is not None:
            internal_kwargs["label"] = label
        if message is not None:
            internal_kwargs["message"] = message
        if textsignal is not None:
            internal_kwargs["textsignal"] = textsignal
        if picker_title is not None:
            internal_kwargs["picker_title"] = picker_title
        if range_start is not None:
            internal_kwargs["start_date"] = range_start
        if range_end is not None:
            internal_kwargs["end_date"] = range_end
        if min_date is not None:
            internal_kwargs["min_date"] = min_date
        if max_date is not None:
            internal_kwargs["max_date"] = max_date
        if disabled_dates is not None:
            internal_kwargs["disabled_dates"] = disabled_dates
        if required:
            internal_kwargs["required"] = True
        if disabled:
            internal_kwargs["state"] = "disabled"
        elif read_only:
            internal_kwargs["state"] = "readonly"
        if accent is not None:
            internal_kwargs["accent"] = accent
        if density is not None:
            internal_kwargs["density"] = density
        internal_kwargs.update({k: v for k, v in kwargs.items()
                                 if k not in internal_kwargs})

        self._internal = _InternalDateEntry(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Event routing -----

    def _entry_widget(self) -> tkinter.Misc:
        return self._internal._entry

    @overload
    def on(self, event: str) -> Stream: ...
    @overload
    def on(self, event: str, handler: Callable[[Event], Any]) -> Subscription: ...
    def on(self, event: str, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        sequence = resolve_event(self, str(event))
        widget = self._entry_widget() if sequence in _INNER_ENTRY_SEQUENCES else self._internal
        if handler is None:
            from bootstack.widgets._core.stream import Stream as _Stream
            def _source(h):
                _w = self._entry_widget() if sequence in _INNER_ENTRY_SEQUENCES else self._internal
                _bid = _w.bind(sequence, h, add="+")
                return Subscription(_w, sequence, _bid)
            return _Stream(self._internal, _source=_source)
        bind_id = widget.bind(sequence, handler, add="+")
        return Subscription(widget, sequence, bind_id)

    # ----- Properties -----

    @property
    def signal(self) -> "Signal[str] | None":
        """The reactive signal bound to this field's text, if any."""
        return getattr(self._internal, 'signal', None)

    @property
    def picker_button(self):
        """The calendar picker button widget, or `None` if hidden."""
        return self._internal.addons.get('date-picker')

    @property
    def value(self) -> "date | tuple[date, date] | None":
        """Selected date, or `(start, end)` tuple in range mode."""
        return self._internal.value

    @value.setter
    def value(self, v: "date | str | None") -> None:
        self._internal.value = v

    @property
    def disabled(self) -> bool:
        return str(self._entry_widget().cget("state")) == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    @property
    def read_only(self) -> bool:
        return str(self._entry_widget().cget("state")) == "readonly"

    @read_only.setter
    def read_only(self, v: bool) -> None:
        self._internal.configure(state="readonly" if v else "normal")

    # ----- Methods -----

    def validate(self) -> bool:
        """Run validation rules against the current value.

        Returns:
            `True` if all rules pass, `False` otherwise.
        """
        return self._internal._entry.validate(
            self._internal._entry.get(), trigger="manual"
        )

    def focus(self) -> None:
        """Give keyboard focus to this field."""
        self._entry_widget().focus_set()

    def clear(self) -> None:
        """Clear the field, setting the value to `None`."""
        self._internal.value = None

    def add_validation_rule(self, rule_type: str, **kwargs: Any) -> None:
        """Add a validation rule to this field.

        Args:
            rule_type: Rule identifier string (e.g. `'required'`, `'min_date'`).
        """
        self._internal.add_validation_rule(rule_type, **kwargs)

    # ----- Event shorthands -----

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the selected date changes.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("change", handler)

    @overload
    def on_submit(self) -> Stream: ...
    @overload
    def on_submit(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_submit(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the user presses Return to confirm input.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("submit", handler)

    @overload
    def on_valid(self) -> Stream: ...
    @overload
    def on_valid(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_valid(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when validation passes.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("valid", handler)

    @overload
    def on_invalid(self) -> Stream: ...
    @overload
    def on_invalid(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_invalid(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when validation fails.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("invalid", handler)

    @overload
    def on_validate(self) -> Stream: ...
    @overload
    def on_validate(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_validate(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when a validation check runs.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("validate", handler)

    @overload
    def on_focus(self) -> Stream: ...
    @overload
    def on_focus(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_focus(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the field gains keyboard focus.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("focus", handler)

    @overload
    def on_blur(self) -> Stream: ...
    @overload
    def on_blur(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_blur(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the field loses keyboard focus.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("blur", handler)


register_widget_events(DateField, _DATEFIELD_EVENTS)