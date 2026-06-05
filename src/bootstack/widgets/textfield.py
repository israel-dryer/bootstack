from __future__ import annotations

import tkinter
from typing import overload, Any, Callable, Literal, TYPE_CHECKING

from bootstack.widgets._impl.composites.textentry import TextEntry as _InternalTextEntry
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import resolve_event, register_widget_events
from bootstack.widgets._core.field_mixin import FieldAddonMixin
from bootstack.events import Subscription
from bootstack.streams import Stream
from bootstack.widgets.types import AccentToken, Event, Justify, WidgetDensity

if TYPE_CHECKING:
    from bootstack.signals import Signal

# Events that fire on the inner entry part, not the outer Frame.
_INNER_ENTRY_SEQUENCES = frozenset({
    "<<Input>>",
    "<<Change>>",
    "<<Valid>>",
    "<<Invalid>>",
    "<<Validate>>",
    "<Return>",
    "<KeyRelease>",
    "<FocusIn>",
    "<FocusOut>",
})

_TEXTFIELD_EVENTS: dict[str, str] = {
    "input":    "<<Input>>",
    "change":   "<<Change>>",
    "valid":    "<<Valid>>",
    "invalid":  "<<Invalid>>",
    "validate": "<<Validate>>",
    "submit":   "<Return>",
    "focus":    "<FocusIn>",
    "blur":     "<FocusOut>",
}


class TextField(FieldAddonMixin, PublicWidgetBase):
    """Single-line text input with optional label, message, and validation.

    The initial value is the first positional argument. All options are
    keyword-only.

    Args:
        value: Initial text value.
        placeholder: Ghost text shown when the field is empty and unfocused.
        textsignal: Reactive ``Signal[str]`` bound to the field text. The
            field value and signal stay in sync automatically.
        value_format: ICU format pattern applied when displaying and parsing
            the value. Examples: ``'#,##0.00'`` (decimal with thousands),
            ``'currency'``, ``'percent'``, ``'yyyy-MM-dd'`` (date).
            Requires localization to be enabled.
        label: Label displayed above the input.
        message: Hint or helper text displayed below the input.
        required: If ``True``, marks the field as required and prevents empty
            submission.
        mask: Character used to mask each typed character (e.g. ``'*'``
            for password inputs).
        read_only: If ``True``, text is visible and selectable but not
            editable.
        disabled: If ``True``, field is fully non-interactive and dimmed.
        width: Width in character units.
        justify: Text alignment. One of ``'left'`` (default), ``'center'``,
            ``'right'``.
        font: Semantic font token (e.g. ``'body'``, ``'code'``).
        accent: Accent token applied to the focus ring. One of ``'primary'``,
            ``'secondary'``, ``'success'``, ``'warning'``, ``'danger'``.
        density: Padding density. ``'default'`` or ``'compact'``.
        parent: Explicit parent widget. If omitted, the current context-stack
            container is used.
    """

    def __init__(
        self,
        value: str = "",
        *,
        placeholder: str | None = None,
        textsignal: "Signal[str] | None" = None,
        value_format: str | None = None,
        label: str | None = None,
        message: str | None = None,
        required: bool = False,
        mask: str | None = None,
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

        internal_kwargs: dict[str, Any] = {}
        if value:
            internal_kwargs["value"] = value
        if placeholder is not None:
            internal_kwargs["placeholder"] = placeholder
        if textsignal is not None:
            internal_kwargs["textsignal"] = textsignal
        if value_format is not None:
            internal_kwargs["value_format"] = value_format
        if label is not None:
            internal_kwargs["label"] = label
        if message is not None:
            internal_kwargs["message"] = message
        if required:
            internal_kwargs["required"] = True
        if mask is not None:
            internal_kwargs["show"] = mask
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

        self._internal = _InternalTextEntry(tk_master, **internal_kwargs)
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
        """The current text value of the field."""
        return self._internal.value

    @value.setter
    def value(self, v: str) -> None:
        self._internal.value = v

    @property
    def signal(self) -> "Signal[str] | None":
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

    def validate(self) -> bool:
        """Run validation rules against the current value.

        Returns:
            `True` if all rules pass, `False` otherwise.
        """
        return self._internal._entry.validate(
            self._internal._entry.value(), trigger="manual"
        )

    def focus(self) -> None:
        """Give keyboard focus to this field."""
        self._entry_widget().focus_set()

    def clear(self) -> None:
        """Clear the field text."""
        self._internal.value = ""

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

    def insert(self, index: int, text: str) -> None:
        """Insert ``text`` at ``index``.

        Args:
            index: Character position to insert at.
            text: Text to insert.
        """
        self._entry_widget().insert(index, text)

    def delete(self, start: int, end: int | None = None) -> None:
        """Delete characters from ``start`` to ``end``.

        Args:
            start: Start index (inclusive).
            end: End index (exclusive). If ``None``, deletes to end of field.
        """
        self._entry_widget().delete(start, "end" if end is None else end)

    # ----- Event shorthands -----

    @overload
    def on_input(self) -> Stream: ...
    @overload
    def on_input(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_input(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired on every keystroke.

        Unlike ``on_change()`` which fires on commit (blur or Enter),
        ``on_input()`` fires after each character typed. Use it for
        real-time feedback, character counting, or live filtering.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("input", handler)

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the field value changes.

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


register_widget_events(TextField, _TEXTFIELD_EVENTS)
