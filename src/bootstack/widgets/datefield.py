from __future__ import annotations

import tkinter
from datetime import date
from typing import overload, Any, Callable, Iterable, Literal, TYPE_CHECKING

from bootstack.widgets._impl.composites.dateentry import DateEntry as _InternalDateEntry
from bootstack.widgets._core.base import PublicWidgetBase, adapt_handler
from bootstack.widgets._core.events import resolve_event, register_widget_events
from bootstack.widgets._core.field_mixin import FieldAddonMixin, ValueSignalMixin
from bootstack.events import ChangeEvent, Subscription, ValidationEvent
from bootstack.streams import Stream
from bootstack.validation import RuleType
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


class DateField(ValueSignalMixin, FieldAddonMixin, PublicWidgetBase):
    """A date input field with an optional calendar picker button.

    In `'single'` mode `value` returns a `date`; in `'range'` mode it returns
    a `(start, end)` tuple of dates.

    Args:
        value: Initial date value — a `date` object or an ISO string
            (`'YYYY-MM-DD'`). `None` for an empty field.
        value_format: Format applied to the displayed date — a named preset
            (e.g. `'shortDate'`, `'longDate'`) or a custom pattern (e.g.
            `'dd.MM.yy'`). Default `'longDate'`. See
            :ref:`format specs <value-formats>`.
        label: Label displayed above the field.
        message: Hint text displayed below the field.
        signal: Reactive `Signal` two-way bound to the field's `date` value (not
            its text). When given, it seeds the initial value. This is the usual
            way to bind a date field.
        textsignal: Reactive `Signal[str]` bound to the field's raw text rather
            than its date value. Niche; prefer `signal`.
        show_picker_button: Show the calendar icon button. Default `True`.
        picker_title: Title of the picker dialog.
        picker_first_weekday: First day of week in the picker (0=Mon … 6=Sun).
            Default `6` (Sunday).
        selection_mode: Single date or a start/end range. In range mode the
            entry is read-only and dates must be selected via the picker.
            Default `'single'`.
        range_start: Pre-selected range start date (range mode only).
        range_end: Pre-selected range end date (range mode only).
        min_date: Earliest selectable date.
        max_date: Latest selectable date.
        disabled_dates: Dates that cannot be selected.
        required: Mark field as required; blocks empty submission.
        disabled: If `True`, field is non-interactive.
        read_only: If `True`, value is visible but not editable.
        accent: Accent color applied to the focus ring. Default `'primary'`.
        density: Widget density.
        parent: Override the context-stack parent.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        value: str | date | None = None,
        *,
        signal: "Signal | None" = None,
        value_format: str = "longDate",
        label: str | None = None,
        message: str | None = None,
        textsignal: "Signal[str] | None" = None,
        show_picker_button: bool = True,
        picker_title: str | None = None,
        picker_first_weekday: int = 6,
        selection_mode: Literal["single", "range"] = "single",
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

        self._internal = _InternalDateEntry(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

        if signal is not None:
            self._bind_value_signal(signal)

    # ----- Event routing -----

    def _entry_widget(self) -> tkinter.Misc:
        return self._internal._entry

    @overload
    def on(self, event: str) -> Stream: ...
    @overload
    def on(self, event: str, handler: Callable[[Event], Any]) -> Subscription: ...
    def on(self, event: str, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback for an event by name.

        A generic, string-keyed escape hatch — prefer the typed `on_*`
        shorthands (e.g. `on_change`), which carry the precise payload type.
        Called with no handler, returns a composable `Stream`; with a handler,
        binds it and returns a `Subscription`.

        Args:
            event: Event name (for example `'change'` or `'focus'`).
            handler: Called with the event payload. Omit to get a composable
                :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        sequence = resolve_event(self, str(event))
        widget = self._entry_widget() if sequence in _INNER_ENTRY_SEQUENCES else self._internal
        if handler is None:
            from bootstack.streams import Stream as _Stream
            def _source(h):
                _w = self._entry_widget() if sequence in _INNER_ENTRY_SEQUENCES else self._internal
                _bid = _w.bind(sequence, adapt_handler(h), add="+")
                return Subscription(_w, sequence, _bid)
            return _Stream(self._internal, _source=_source)
        bind_id = widget.bind(sequence, adapt_handler(handler), add="+")
        return Subscription(widget, sequence, bind_id)

    # ----- Properties -----

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
        """Whether the field is disabled (non-interactive and greyed out)."""
        return str(self._entry_widget().cget("state")) == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    @property
    def read_only(self) -> bool:
        """Whether the field is read-only (selectable but not editable)."""
        return str(self._entry_widget().cget("state")) == "readonly"

    @read_only.setter
    def read_only(self, v: bool) -> None:
        self._internal.configure(state="readonly" if v else "normal")

    # ----- Date constraints -----

    @property
    def min_date(self) -> date | None:
        """Earliest selectable date. Assigning takes effect the next time the picker opens."""
        return self._internal._coerce_date(self._internal._min_date)

    @min_date.setter
    def min_date(self, value: date | str | None) -> None:
        self._internal.set_min_date(value)

    @property
    def max_date(self) -> date | None:
        """Latest selectable date. Assigning takes effect the next time the picker opens."""
        return self._internal._coerce_date(self._internal._max_date)

    @max_date.setter
    def max_date(self, value: date | str | None) -> None:
        self._internal.set_max_date(value)

    @property
    def disabled_dates(self) -> tuple[date, ...]:
        """Dates disabled in the picker. Assigning a new iterable takes effect the next time it opens."""
        raw = self._internal._disabled_dates or []
        coerce = self._internal._coerce_date
        return tuple(sorted(d for d in (coerce(x) for x in raw) if d is not None))

    @disabled_dates.setter
    def disabled_dates(self, value: Iterable[date | str] | None) -> None:
        self._internal.set_disabled_dates(value)

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

    def add_validation_rule(self, rule_type: RuleType, **kwargs: Any) -> None:
        """Add a validation rule to this field.

        Args:
            rule_type: The kind of validation rule to apply.
        """
        self._internal.add_validation_rule(rule_type, **kwargs)

    # ----- Event shorthands -----

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[ChangeEvent], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[ChangeEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the selected date changes.

        Args:
            handler: Called with a :class:`~bootstack.events.ChangeEvent`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("change", handler)

    @overload
    def on_submit(self) -> Stream: ...
    @overload
    def on_submit(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_submit(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the user presses Return to confirm input.

        Args:
            handler: Called with an :class:`~bootstack.events.Event`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("submit", handler)

    @overload
    def on_valid(self) -> Stream: ...
    @overload
    def on_valid(self, handler: Callable[[ValidationEvent], Any]) -> Subscription: ...
    def on_valid(self, handler: Callable[[ValidationEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when validation passes.

        Args:
            handler: Called with a :class:`~bootstack.events.ValidationEvent`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("valid", handler)

    @overload
    def on_invalid(self) -> Stream: ...
    @overload
    def on_invalid(self, handler: Callable[[ValidationEvent], Any]) -> Subscription: ...
    def on_invalid(self, handler: Callable[[ValidationEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when validation fails.

        Args:
            handler: Called with a :class:`~bootstack.events.ValidationEvent`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("invalid", handler)

    @overload
    def on_validate(self) -> Stream: ...
    @overload
    def on_validate(self, handler: Callable[[ValidationEvent], Any]) -> Subscription: ...
    def on_validate(self, handler: Callable[[ValidationEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when a validation check runs.

        Args:
            handler: Called with a :class:`~bootstack.events.ValidationEvent`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("validate", handler)

    @overload
    def on_focus(self) -> Stream: ...
    @overload
    def on_focus(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_focus(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the field gains keyboard focus.

        Args:
            handler: Called with an :class:`~bootstack.events.Event`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("focus", handler)

    @overload
    def on_blur(self) -> Stream: ...
    @overload
    def on_blur(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_blur(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the field loses keyboard focus.

        Args:
            handler: Called with an :class:`~bootstack.events.Event`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("blur", handler)


register_widget_events(DateField, _DATEFIELD_EVENTS)