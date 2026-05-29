from __future__ import annotations

import tkinter
from datetime import date
from typing import Any, Callable, Iterable

from bootstack.widgets.composites.dateentry import DateEntry as _InternalDateEntry
from bootstack.widgets.public.base import PublicWidgetBase
from bootstack.widgets.public.events import resolve_event, register_widget_events
from bootstack.widgets.public.subscription import Subscription
from bootstack.widgets.public.primitives.textfield import _INNER_ENTRY_SEQUENCES

_DATEFIELD_EVENTS: dict[str, str] = {
    "change":   "<<Change>>",
    "validate": "<<Validate>>",
    "valid":    "<<Valid>>",
    "invalid":  "<<Invalid>>",
    "submit":   "<Return>",
}


class DateField(PublicWidgetBase):
    """A date input field with an optional calendar picker button.

    In `'single'` mode `value` returns a `date`; in `'range'` mode it returns
    a `(start, end)` tuple of dates.

    Args:
        value: Initial date value — a `date` object or an ISO string
            (`'YYYY-MM-DD'`). `None` for an empty field.
        value_format: Display format token. Default `'longDate'`.
        label: Label displayed above the field.
        message: Hint text displayed below the field.
        show_picker_button: Show the calendar icon button. Default `True`.
        picker_title: Title of the picker dialog.
        picker_first_weekday: First day of week in the picker (0=Mon … 6=Sun).
            Default `6` (Sunday).
        selection_mode: `'single'` (default) or `'range'`.
        range_start: Pre-selected range start date (range mode only).
        range_end: Pre-selected range end date (range mode only).
        min_date: Earliest selectable date.
        max_date: Latest selectable date.
        disabled_dates: Dates that cannot be selected.
        required: Mark field as required; blocks empty submission.
        disabled: If True, field is non-interactive.
        read_only: If True, value is visible but not editable.
        accent: Accent token for the focus ring.
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
        accent: str | None = None,
        density: str | None = None,
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
        internal_kwargs.update(kwargs)

        self._internal = _InternalDateEntry(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Event routing -----

    def _entry_widget(self) -> tkinter.Misc:
        return self._internal._entry

    def on(self, event: str, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        sequence = resolve_event(self, str(event))
        widget = self._entry_widget() if sequence in _INNER_ENTRY_SEQUENCES else self._internal
        bind_id = widget.bind(sequence, handler, add="+")
        return Subscription(widget, sequence, bind_id)

    # ----- Properties -----

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

    # ----- Event shorthands -----

    def on_change(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired when the selected date changes.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("change", handler)


register_widget_events(DateField, _DATEFIELD_EVENTS)