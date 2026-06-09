from __future__ import annotations

import datetime
import tkinter
from typing import overload, Any, Callable, TYPE_CHECKING

from bootstack.widgets._impl.composites.timeentry import TimeEntry as _InternalTimeEntry
from bootstack.widgets._core.base import PublicWidgetBase, adapt_handler
from bootstack.widgets._core.events import resolve_event, register_widget_events
from bootstack.widgets._core.field_mixin import FieldAddonMixin
from bootstack.events import ChangeEvent, Subscription, ValidationEvent
from bootstack.streams import Stream
from bootstack.validation import RuleType
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


class TimeField(FieldAddonMixin, PublicWidgetBase):
    """A time-input field with a searchable dropdown of time intervals.

    Displays a formatted time value and shows a dropdown list of times at
    the specified `interval`. The user can type a custom time or pick from
    the list.

    Args:
        value: Initial time value — a `datetime.time` object or a time
            string (e.g. `'14:30'` or `'2:30 PM'`). Defaults to the current
            time.
        value_format: Format applied to the displayed time — a named preset
            (e.g. `'shortTime'`, `'longTime'`) or a custom pattern (e.g.
            `'HH:mm'`, `'h:mm a'`). Default `'shortTime'`. See
            :ref:`format specs <value-formats>`.
        interval: Minute interval for dropdown entries. Default `30`.
        min_time: Earliest time shown in the dropdown.
        max_time: Latest time shown in the dropdown.
        label: Label displayed above the field.
        message: Hint text displayed below the field.
        textsignal: Reactive `Signal[str]` bound to the field text. The
            field value and signal stay in sync automatically.
        required: If `True`, field cannot be left empty.
        disabled: If `True`, field is non-interactive.
        read_only: If `True`, free-text entry is blocked; user must pick
            from the dropdown.
        width: Width in character cells.
        accent: Accent color applied to the focus ring. Default `'primary'`.
        density: Widget density.
        parent: Override the context-stack parent.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
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
        textsignal: "Signal[str] | None" = None,
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
        if textsignal is not None:
            internal_kwargs["textsignal"] = textsignal
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

        self._internal = _InternalTimeEntry(tk_master, **internal_kwargs)
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
    def signal(self) -> "Signal[str] | None":
        """The reactive signal bound to this field's text, if any."""
        return getattr(self._internal, 'signal', None)

    @property
    def value(self) -> "datetime.time | None":
        """Current time value, or `None` if the field is empty."""
        return self._internal.value

    @value.setter
    def value(self, v: "datetime.time | str | None") -> None:
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