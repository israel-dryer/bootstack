from __future__ import annotations

import tkinter
from typing import overload, Any, Callable, TYPE_CHECKING

from bootstack.widgets._impl.composites.spinnerentry import SpinnerEntry as _InternalSpinnerEntry
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import resolve_event, register_widget_events
from bootstack.widgets._core.field_mixin import FieldAddonMixin
from bootstack.widgets._core.subscription import Subscription
from bootstack.widgets._core.stream import Stream
from bootstack.widgets.textfield import _INNER_ENTRY_SEQUENCES
from bootstack.widgets.types import AccentToken, Event, Justify, WidgetDensity

if TYPE_CHECKING:
    from bootstack.signals import Signal

_SPINNER_FIELD_EVENTS: dict[str, str] = {
    "input":    "<<Input>>",
    "change":   "<<Change>>",
    "valid":    "<<Valid>>",
    "invalid":  "<<Invalid>>",
    "validate": "<<Validate>>",
    "submit":   "<Return>",
    "focus":    "<FocusIn>",
    "blur":     "<FocusOut>",
}


class SpinnerField(FieldAddonMixin, PublicWidgetBase):
    """A text-entry field with spin buttons for stepping through values.

    Supports two modes: a fixed list of text values (`options=`) or a numeric
    range (`min_value=` / `max_value=`). Exactly one mode should be used at
    a time.

    Args:
        value: Initial value — a string (text mode) or number (numeric mode).
        options: Fixed list of string values to step through (text mode).
        min_value: Minimum value for numeric range mode.
        max_value: Maximum value for numeric range mode.
        step: Increment step size for numeric mode. Default `1`.
        wrap: If True, values wrap around at the boundaries.
        label: Label displayed above the field.
        message: Hint text displayed below the field.
        placeholder: Ghost text shown when the field is empty and unfocused.
        textsignal: Reactive `Signal[str]` bound to the field text. The
            field value and signal stay in sync automatically.
        required: If True, field cannot be left empty.
        disabled: If True, field is non-interactive.
        read_only: If True, value is visible but not editable.
        width: Width in character cells.
        justify: Text alignment. One of `'left'` (default), `'center'`,
            `'right'`.
        font: Semantic font token (e.g. `'body'`, `'code'`).
        accent: Accent token for the focus ring. One of `'primary'`,
            `'secondary'`, `'success'`, `'warning'`, `'danger'`.
        density: Widget density — `'default'` or `'compact'`.
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
        placeholder: str | None = None,
        textsignal: "Signal[str] | None" = None,
        required: bool = False,
        disabled: bool = False,
        read_only: bool = False,
        width: int | None = None,
        justify: Justify | None = None,
        font: str | None = None,
        accent: AccentToken | str | None = None,
        density: WidgetDensity | None = None,
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
        if placeholder is not None:
            internal_kwargs["placeholder"] = placeholder
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
        if justify is not None:
            internal_kwargs["justify"] = justify
        if font is not None:
            internal_kwargs["font"] = font
        if accent is not None:
            internal_kwargs["accent"] = accent
        if density is not None:
            internal_kwargs["density"] = density
        internal_kwargs.update(kwargs)

        self._internal = _InternalSpinnerEntry(tk_master, **internal_kwargs)
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
        target = self._entry_widget() if sequence in _INNER_ENTRY_SEQUENCES else self._internal
        if handler is None:
            def _source(h):
                t = self._entry_widget() if sequence in _INNER_ENTRY_SEQUENCES else self._internal
                bid = t.bind(sequence, h, add="+")
                return Subscription(t, sequence, bid)
            return Stream(self._internal, _source=_source)
        bid = target.bind(sequence, handler, add="+")
        return Subscription(target, sequence, bid)

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
    def signal(self) -> "Signal[str] | None":
        """The reactive `Signal` bound to this field, or `None`."""
        return getattr(self._internal, "signal", None)

    @property
    def disabled(self) -> bool:
        """Whether the field is fully non-interactive."""
        return str(self._internal._entry.cget("state")) == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    @property
    def read_only(self) -> bool:
        """Whether the field is visible but not editable."""
        return str(self._entry_widget().cget("state")) == "readonly"

    @read_only.setter
    def read_only(self, v: bool) -> None:
        self._internal.configure(state="readonly" if v else "normal")

    # ----- Methods -----

    def focus(self) -> None:
        """Give keyboard focus to this field."""
        self._entry_widget().focus_set()

    def clear(self) -> None:
        """Clear the field value."""
        self._internal.value = ""

    def validate(self, trigger: str = "manual") -> bool:
        """Run validation rules against the current value.

        Args:
            trigger: Validation trigger label. One of `'manual'`,
                `'blur'`, `'key'`. Defaults to `'manual'`.

        Returns:
            `True` if all rules pass, `False` otherwise.
        """
        return self._internal._entry.validate(
            self._internal._entry.value(), trigger=trigger
        )

    def select_all(self) -> None:
        """Select all text in the field."""
        self._entry_widget().selection_range(0, "end")

    def select_range(self, start: int, end: int) -> None:
        """Select text between ``start`` and ``end`` character positions.

        Args:
            start: Start index (0-based, inclusive).
            end: End index (exclusive).
        """
        self._entry_widget().selection_range(start, end)

    # ----- Event shorthands -----

    @overload
    def on_input(self) -> Stream: ...
    @overload
    def on_input(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_input(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired on every keystroke.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("input", handler)

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the value changes.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("change", handler)

    @overload
    def on_submit(self) -> Stream: ...
    @overload
    def on_submit(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_submit(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the user presses Enter.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("submit", handler)

    @overload
    def on_focus(self) -> Stream: ...
    @overload
    def on_focus(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_focus(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the field gains focus.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("focus", handler)

    @overload
    def on_blur(self) -> Stream: ...
    @overload
    def on_blur(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_blur(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the field loses focus.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("blur", handler)

    @overload
    def on_valid(self) -> Stream: ...
    @overload
    def on_valid(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_valid(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when validation passes.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("valid", handler)

    @overload
    def on_invalid(self) -> Stream: ...
    @overload
    def on_invalid(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_invalid(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when validation fails.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("invalid", handler)

    @overload
    def on_validate(self) -> Stream: ...
    @overload
    def on_validate(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_validate(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired after any validation run.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("validate", handler)


register_widget_events(SpinnerField, _SPINNER_FIELD_EVENTS)