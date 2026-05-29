from __future__ import annotations

import datetime
import tkinter
from typing import Any, Callable

from bootstack.widgets.composites.timeentry import TimeEntry as _InternalTimeEntry
from bootstack.widgets.public.base import PublicWidgetBase
from bootstack.widgets.public.events import register_widget_events
from bootstack.widgets.public.subscription import Subscription
from bootstack.widgets.public.primitives.textfield import _INNER_ENTRY_SEQUENCES

_TIME_FIELD_EVENTS: dict[str, str] = {
    "change": "<<Change>>",
    "submit": "<Return>",
}


class TimeField(PublicWidgetBase):
    """A time-input field with a searchable dropdown of time intervals.

    Displays a formatted time value and shows a dropdown list of times at
    the specified `interval`. The user can type a custom time or pick from
    the list.

    Args:
        value: Initial time value (`datetime.time` or `'HH:MM'` string).
            Defaults to the current time.
        value_format: ICU time format preset or pattern. Common values:
            `'shortTime'` (default, e.g. `'3:30 PM'`), `'mediumTime'`,
            `'HH:mm'`, `'h:mm a'`.
        interval: Minute interval for dropdown entries. Default `30`.
        min_time: Earliest time shown in the dropdown.
        max_time: Latest time shown in the dropdown.
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
        value: datetime.time | str | None = None,
        *,
        value_format: str = "shortTime",
        interval: int = 30,
        min_time: datetime.time | str | None = None,
        max_time: datetime.time | str | None = None,
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
            "value_format": value_format,
            "interval": interval,
        }
        if value is not None:
            internal_kwargs["value"] = value
        if min_time is not None:
            internal_kwargs["min_time"] = min_time
        if max_time is not None:
            internal_kwargs["max_time"] = max_time
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

        self._internal = _InternalTimeEntry(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Event routing -----

    def _entry_widget(self) -> tkinter.Misc:
        return self._internal._entry

    def on(self, event: str, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        from bootstack.widgets.public.events import resolve_event
        sequence = resolve_event(self, str(event))
        widget = self._entry_widget() if sequence in _INNER_ENTRY_SEQUENCES else self._internal
        bind_id = widget.bind(sequence, handler, add="+")
        return Subscription(widget, sequence, bind_id)

    # ----- Properties -----

    @property
    def value(self) -> str:
        """Current time value as a formatted string."""
        return self._internal.value

    @value.setter
    def value(self, v: datetime.time | str) -> None:
        self._internal.value = v

    @property
    def disabled(self) -> bool:
        return str(self._internal._entry.cget("state")) == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    # ----- Event shorthands -----

    def on_change(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired when the time value changes.

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


register_widget_events(TimeField, _TIME_FIELD_EVENTS)