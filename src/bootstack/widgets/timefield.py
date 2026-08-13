from __future__ import annotations

import datetime
import tkinter
from typing import overload, Any, Callable, TYPE_CHECKING

from bootstack.widgets._impl.composites.timeentry import TimeEntry as _InternalTimeEntry
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._core.field_mixin import FieldAddonMixin, ValueSignalMixin
from bootstack.events import ChangeEvent, Subscription, ValidationEvent
from bootstack.streams import Stream
from bootstack.widgets.textfield import _INNER_ENTRY_SEQUENCES
from bootstack.widgets.types import AccentToken, Event, WidgetDensity

if TYPE_CHECKING:
    from bootstack.signals import Signal

_TIME_FIELD_EVENTS: dict[str, str] = {
    "change":   "<<Change>>",
    "validate": "<<Validate>>",
    "valid":    "<<Valid>>",
    "invalid":  "<<Invalid>>",
    "submit":   "<Return>",
    "focus":    "<FocusIn>",
    "blur":     "<FocusOut>",
}


class TimeField(ValueSignalMixin, FieldAddonMixin, PublicWidgetBase):
    """A time-input field with a searchable dropdown of time intervals.

    Displays a formatted time value and shows a dropdown list of times at
    the specified `interval`. The user can type a custom time or pick from
    the list.

    Args:
        value: Initial time value — a `datetime.time` object or a time
            string (e.g. `'14:30'` or `'2:30 PM'`). Empty by default; pass a
            value to seed a starting time.
        value_format: Format applied to the displayed time — a named preset
            (e.g. `'shortTime'`, `'longTime'`) or a custom pattern (e.g.
            `'HH:mm'`, `'h:mm a'`). Default `'shortTime'`. See
            :ref:`format specs <value-formats>`.
        interval: Minute interval for dropdown entries. Default `30`.
        min_time: Earliest time shown in the dropdown.
        max_time: Latest time shown in the dropdown.
        label: Label displayed above the field.
        message: Hint text displayed below the field.
        signal: Reactive `Signal` two-way bound to the field's `time` value (not
            its text). When given, it seeds the initial value. This is the usual
            way to bind a time field.
        required: If `True`, field cannot be left empty.
        disabled: If `True`, field is non-interactive.
        read_only: If `True`, the time is visible but cannot be changed —
            typing is blocked, and neither the clock button nor a click in the
            field opens the time list. Unlike `disabled`, the field keeps its
            normal appearance and stays in the tab order. Defaults to `False`.
        width: Width in character cells.
        accent: Accent color applied to the focus ring. Default `'primary'`.
        density: Widget density.
        parent: Override the context-stack parent.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    _VALIDATION_KIND = "time"

    def __init__(
        self,
        value: datetime.time | str | None = None,
        *,
        signal: "Signal | None" = None,
        value_format: str = "shortTime",
        interval: int = 30,
        min_time: datetime.time | str | None = None,
        max_time: datetime.time | str | None = None,
        label: str | None = None,
        message: str | None = None,
        required: bool = False,
        disabled: bool = False,
        read_only: bool = False,
        width: int | None = None,
        accent: AccentToken | str | None = None,
        density: WidgetDensity | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        if "textsignal" in kwargs:
            raise TypeError(
                "TimeField does not accept 'textsignal=' — a time field binds its "
                "time value. Use signal= with a time-typed Signal "
                "(e.g. Signal(time(9, 0)))."
            )
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
        # Read-only rides its own option, not `state="readonly"` — the internal
        # here is a select, where the ttk `readonly` state is an OUTPUT of the
        # interaction state ("no free typing") and is re-derived at the end of
        # construction, so a state write is overwritten before anyone sees it
        # (#453). Same shape as the setter below and as `Select`.
        internal_kwargs["readonly"] = read_only
        if disabled:
            internal_kwargs["state"] = "disabled"
        if width is not None:
            internal_kwargs["width"] = width
        if accent is not None:
            internal_kwargs["accent"] = accent
        if density is not None:
            internal_kwargs["density"] = density

        self._internal = _InternalTimeEntry(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

        if signal is not None:
            self._bind_value_signal(signal)

    # ----- Event routing -----

    def _entry_widget(self) -> tkinter.Misc:
        return self._internal._entry

    def _event_target(self, sequence: str) -> tkinter.Misc:
        """Route the entry-editing events to the inner entry, not the frame."""
        if sequence in _INNER_ENTRY_SEQUENCES:
            return self._entry_widget()
        return self._internal

    # ----- Properties -----

    @property
    def value(self) -> "datetime.time | None":
        """Current time value, or `None` if the field is empty."""
        return self._internal.value

    @value.setter
    def value(self, v: "datetime.time | str | None") -> None:
        self._internal.value = v
        self._sync_value_set(self._internal.value)

    @property
    def disabled(self) -> bool:
        """Whether the field is disabled (non-interactive and greyed out)."""
        return self._internal._entry.instate(("disabled",))

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    @property
    def read_only(self) -> bool:
        """Whether the field is read-only — the time shows but cannot be changed."""
        # Report the setting, not the state derived from it. The two agree at
        # rest, but the derivation is cleared and restored around a programmatic
        # value write, so reading it answers `False` for a locked field from
        # inside that window (#453). Same reason `Select.read_only` reads the
        # setting; `cget`, never `configure(name)`, which answers a query with a
        # truthy 5-tuple.
        return bool(self._internal.cget("readonly"))

    @read_only.setter
    def read_only(self, v: bool) -> None:
        # Route through the `readonly` option, not `state="readonly"`. The
        # internal here is a select, where the ttk `readonly` state is an
        # OUTPUT of the interaction state ("no free typing") and is re-derived
        # on every change — so a state write is overwritten immediately (#453).
        self._internal.configure(readonly=bool(v))

    # ----- Methods -----

    def validate(self) -> bool:
        """Run validation rules against the current value.

        Returns:
            `True` if all rules pass, `False` otherwise.
        """
        entry = self._internal._entry
        return entry.validate(entry._get_validation_value(), trigger="manual")

    def focus(self) -> None:
        """Give keyboard focus to this field."""
        self._entry_widget().focus_set()

    def clear(self) -> None:
        """Clear the field, setting the value to `None`."""
        self._internal.value = None

    # ----- Event shorthands -----

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[ChangeEvent], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[ChangeEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the time value changes.

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


register_widget_events(TimeField, _TIME_FIELD_EVENTS)