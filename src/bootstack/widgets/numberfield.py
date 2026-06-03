from __future__ import annotations

import tkinter
from typing import overload, Any, Callable, TYPE_CHECKING

from bootstack.widgets._impl.composites.numericentry import NumericEntry as _InternalNumericEntry
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import resolve_event, register_widget_events
from bootstack.widgets._core.field_mixin import FieldAddonMixin
from bootstack.widgets._core.subscription import Subscription
from bootstack.widgets._core.stream import Stream
from bootstack.widgets.textfield import _INNER_ENTRY_SEQUENCES
from bootstack.widgets.types import AccentToken, Event, Justify, WidgetDensity

if TYPE_CHECKING:
    from bootstack.signals import Signal

_NUMBER_FIELD_EVENTS: dict[str, str] = {
    "input":    "<<Input>>",
    "change":   "<<Change>>",
    "valid":    "<<Valid>>",
    "invalid":  "<<Invalid>>",
    "validate": "<<Validate>>",
    "submit":   "<Return>",
    "focus":    "<FocusIn>",
    "blur":     "<FocusOut>",
}


class NumberField(FieldAddonMixin, PublicWidgetBase):
    """A numeric input field with optional stepper buttons.

    Accepts integer or float values. Up/Down arrow keys and the mouse wheel
    step the value by ``step``. The field validates that the typed value is
    numeric and within ``min_value``/``max_value`` bounds.

    The initial value is the first positional argument. All options are
    keyword-only.

    Args:
        value: Initial numeric value. Defaults to ``0``.
        textsignal: Reactive ``Signal[str]`` bound to the field text. The
            field and signal stay in sync automatically. Note: the signal
            must be typed as ``str`` — initialize with ``Signal("0")``,
            not ``Signal(0)``.
        label: Label displayed above the field.
        message: Hint or helper text displayed below the field.
        min_value: Minimum allowed value (inclusive). No lower bound if omitted.
        max_value: Maximum allowed value (inclusive). No upper bound if omitted.
        step: Amount added or subtracted per increment/decrement. Defaults to
            ``1``.
        show_steppers: If ``False``, hides the +/− stepper buttons. Defaults
            to ``True``.
        required: If ``True``, marks the field as required and prevents empty
            submission.
        read_only: If ``True``, value is visible and selectable but not
            editable.
        disabled: If ``True``, field is fully non-interactive and dimmed.
        width: Width in character units.
        justify: Text alignment inside the entry. One of ``'left'`` (default),
            ``'center'``, ``'right'``.
        font: Semantic font token (e.g. ``'body'``, ``'code'``).
        value_format: ICU format pattern applied when displaying the value.
            Common patterns: ``'#,##0'`` (thousands separator),
            ``'#,##0.00'`` (two decimal places), ``'percent'``,
            ``'currency'``. Requires localization to be enabled.
        accent: Accent token applied to the focus ring. One of ``'primary'``,
            ``'secondary'``, ``'success'``, ``'warning'``, ``'danger'``.
        density: Padding density. ``'default'`` or ``'compact'``.
        parent: Explicit parent widget. If omitted, the current context-stack
            container is used.
    """

    def __init__(
        self,
        value: int | float = 0,
        *,
        textsignal: "Signal | None" = None,
        value_format: str | None = None,
        label: str | None = None,
        message: str | None = None,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        step: int | float = 1,
        show_steppers: bool = True,
        required: bool = False,
        read_only: bool = False,
        disabled: bool = False,
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
            "show_spin_buttons": show_steppers,
        }
        if textsignal is not None:
            internal_kwargs["textsignal"] = textsignal
        if value_format is not None:
            internal_kwargs["value_format"] = value_format
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
        if justify is not None:
            internal_kwargs["justify"] = justify
        if font is not None:
            internal_kwargs["font"] = font
        if accent is not None:
            internal_kwargs["accent"] = accent
        if density is not None:
            internal_kwargs["density"] = density

        self._internal = _InternalNumericEntry(tk_master, **internal_kwargs)
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
    def value(self) -> int | float | None:
        """The current numeric value, or ``None`` if the field is empty."""
        return self._internal.value

    @value.setter
    def value(self, v: int | float) -> None:
        self._internal.value = v

    @property
    def signal(self) -> "Signal | None":
        """The reactive ``Signal`` bound to this field, or ``None``."""
        return getattr(self._internal, 'signal', None)

    @property
    def read_only(self) -> bool:
        """Whether the field is visible but not editable."""
        return str(self._entry_widget().cget("state")) == "readonly"

    @read_only.setter
    def read_only(self, v: bool) -> None:
        self._internal.configure(state="readonly" if v else "normal")

    @property
    def disabled(self) -> bool:
        """Whether the field is fully non-interactive."""
        return str(self._entry_widget().cget("state")) == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    # ----- Methods -----

    def increment(self, steps: int = 1) -> None:
        """Increment the value by ``steps`` × step size.

        Args:
            steps: Number of steps to increment. Defaults to ``1``.
        """
        self._internal.step(steps)

    def decrement(self, steps: int = 1) -> None:
        """Decrement the value by ``steps`` × step size.

        Args:
            steps: Number of steps to decrement. Defaults to ``1``.
        """
        self._internal.step(-steps)

    def validate(self, trigger: str = "manual") -> bool:
        """Run validation rules against the current value.

        Args:
            trigger: Validation trigger label. One of ``'manual'``,
                ``'blur'``, ``'key'``. Defaults to ``'manual'``.

        Returns:
            ``True`` if all rules pass, ``False`` otherwise.
        """
        return self._internal._entry.validate(
            self._internal._entry.value(), trigger=trigger
        )

    def focus(self) -> None:
        """Give keyboard focus to this field."""
        self._entry_widget().focus_set()

    def clear(self) -> None:
        """Clear the field value."""
        self._internal.value = 0

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
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("input", handler)

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the value is committed.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("change", handler)

    @overload
    def on_submit(self) -> Stream: ...
    @overload
    def on_submit(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_submit(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the user presses Enter.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("submit", handler)

    @overload
    def on_focus(self) -> Stream: ...
    @overload
    def on_focus(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_focus(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the field gains focus.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("focus", handler)

    @overload
    def on_blur(self) -> Stream: ...
    @overload
    def on_blur(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_blur(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the field loses focus.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("blur", handler)

    @overload
    def on_valid(self) -> Stream: ...
    @overload
    def on_valid(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_valid(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when validation passes.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("valid", handler)

    @overload
    def on_invalid(self) -> Stream: ...
    @overload
    def on_invalid(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_invalid(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when validation fails.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("invalid", handler)

    @overload
    def on_validate(self) -> Stream: ...
    @overload
    def on_validate(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_validate(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired after any validation run.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("validate", handler)


register_widget_events(NumberField, _NUMBER_FIELD_EVENTS)
