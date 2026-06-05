from __future__ import annotations

import tkinter
from typing import overload, Any, Callable, TYPE_CHECKING

from bootstack.widgets._impl.composites.textarea.textarea import TextArea as _InternalTextArea
from bootstack.widgets._core.base import PublicWidgetBase, adapt_handler
from bootstack.widgets._core.events import register_widget_events, resolve_event
from bootstack.events import ChangeEvent, InputEvent, Subscription, TextModifiedEvent, ValidationEvent
from bootstack.streams import Stream
from bootstack.widgets.types import AccentToken, Event

if TYPE_CHECKING:
    from bootstack.signals import Signal

# Events that fire on the inner tk.Text widget, not the outer frame.
_INNER_TEXT_SEQUENCES = frozenset({
    "<FocusIn>",
    "<FocusOut>",
    "<<TextModified>>",
    "<<TextUndo>>",
    "<<TextRedo>>",
})

_TEXTAREA_EVENTS: dict[str, str] = {
    "input":    "<<Input>>",
    "change":   "<<Changed>>",
    "valid":    "<<Valid>>",
    "invalid":  "<<Invalid>>",
    "validate": "<<Validate>>",
    "focus":    "<FocusIn>",
    "blur":     "<FocusOut>",
    "modified": "<<TextModified>>",
    "undo":     "<<TextUndo>>",
    "redo":     "<<TextRedo>>",
}


class TextArea(PublicWidgetBase):
    """A multi-line text input with optional label, placeholder, and scrollbars.

    Args:
        value: Initial text content.
        textsignal: Reactive `Signal[str]` linked to the text content.
        label: Label displayed above the field.
        message: Hint text displayed below the field.
        required: If True, field cannot be left empty.
        placeholder: Placeholder text shown when the field is empty.
        max_length: Maximum number of characters allowed.
        read_only: If True, text is visible but not editable.
        wrap: If True (default), long lines wrap at the widget boundary.
        height: Visible row count. Default `4`.
        width: Width in character units. Omit to let the widget fill its
            container via layout.
        scrollbars: Scrollbar visibility — `'auto'` (default), `'vertical'`,
            `'both'`, or `'none'`.
        font: Font token. Default `'body'`.
        accent: Accent token for the focus border. One of `'primary'`,
            `'secondary'`, `'success'`, `'warning'`, `'danger'`.
        show_border: If True (default), wraps the text area in a themed
            border with a focus ring.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        value: str = "",
        *,
        textsignal: "Signal[str] | None" = None,
        label: str | None = None,
        message: str | None = None,
        required: bool = False,
        placeholder: str | None = None,
        max_length: int | None = None,
        read_only: bool = False,
        wrap: bool = True,
        height: int = 4,
        width: int | None = None,
        scrollbars: str = "auto",
        font: str = "body",
        accent: AccentToken | str = "primary",
        show_border: bool = True,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "value": value,
            "read_only": read_only,
            "wrap": wrap,
            "height": height,
            "scrollbars": scrollbars,
            **({"width": width} if width is not None else {}),
            "show_border": show_border,
            "font": font,
            "accent": accent,
        }
        if textsignal is not None:
            internal_kwargs["textsignal"] = textsignal
        if label is not None:
            internal_kwargs["label"] = label
        if message is not None:
            internal_kwargs["message"] = message
        if required:
            internal_kwargs["required"] = True
        if placeholder is not None:
            internal_kwargs["placeholder"] = placeholder
        if max_length is not None:
            internal_kwargs["max_length"] = max_length
        internal_kwargs.update(kwargs)

        self._internal = _InternalTextArea(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Event routing -----

    def _text_widget(self) -> tkinter.Misc:
        return self._internal._core.text

    @overload
    def on(self, event: str) -> Stream: ...
    @overload
    def on(self, event: str, handler: Callable[[Event], Any]) -> Subscription: ...
    def on(self, event: str, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        sequence = resolve_event(self, str(event))
        target = self._text_widget() if sequence in _INNER_TEXT_SEQUENCES else self._internal
        if handler is None:
            def _source(h):
                t = self._text_widget() if sequence in _INNER_TEXT_SEQUENCES else self._internal
                bid = t.bind(sequence, adapt_handler(h), add="+")
                return Subscription(t, sequence, bid)
            return Stream(self._internal, _source=_source)
        bid = target.bind(sequence, adapt_handler(handler), add="+")
        return Subscription(target, sequence, bid)

    # ----- Properties -----

    @property
    def value(self) -> str:
        """The current text content."""
        return self._internal.value

    @value.setter
    def value(self, v: str) -> None:
        self._internal.value = v

    @property
    def signal(self) -> "Signal[str] | None":
        """The reactive `Signal` bound to this field, or `None`."""
        return getattr(self._internal, "signal", None)

    @property
    def read_only(self) -> bool:
        """Whether the text area is visible but not editable."""
        return self._internal._core.text.cget("state") == "disabled"

    @read_only.setter
    def read_only(self, v: bool) -> None:
        self._internal._core.text.configure(state="disabled" if v else "normal")

    @property
    def is_dirty(self) -> bool:
        """True if the content has changed since the last `mark_saved()` call."""
        return self._internal.is_dirty

    # ----- Methods -----

    def focus(self) -> None:
        """Give keyboard focus to the text area."""
        self._text_widget().focus_set()

    def clear(self) -> None:
        """Clear all text content."""
        self._internal.value = ""

    def validate(self) -> bool:
        """Run validation rules against the current value.

        Returns:
            `True` if all rules pass, `False` otherwise.
        """
        return self._internal.validate()

    def add_validation_rule(self, rule_type: str, **kwargs: Any) -> None:
        """Attach a validation rule to this field.

        Args:
            rule_type: Rule identifier (e.g. `'stringLength'`, `'custom'`).
            **kwargs: Rule options such as `message=`, `min=`, `max=`,
                `trigger=`.
        """
        self._internal.add_validation_rule(rule_type, **kwargs)

    def insert(self, index: str, text: str) -> None:
        """Insert `text` at `index`.

        `index` is a text position: `'end'` for the end of the content, or a
        `'line.column'` string such as `'1.0'` (line 1, column 0).

        Args:
            index: Target text position, e.g. `'end'` or `'1.0'`.
            text: Text to insert.
        """
        self._internal._core.text.insert(index, text)

    def select_all(self) -> None:
        """Select all text content."""
        tw = self._internal._core.text
        tw.focus_set()
        tw.tag_add("sel", "1.0", "end-1c")
        tw.mark_set("insert", "end-1c")

    def mark_saved(self) -> None:
        """Reset the dirty flag — call after saving content."""
        self._internal.mark_saved()

    def undo(self) -> None:
        """Undo the last edit."""
        self._internal.undo()

    def redo(self) -> None:
        """Redo the last undone edit."""
        self._internal.redo()

    # ----- Event shorthands -----

    @overload
    def on_input(self) -> Stream: ...
    @overload
    def on_input(self, handler: Callable[[InputEvent], Any]) -> Subscription: ...
    def on_input(self, handler: Callable[[InputEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired on every edit.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("input", handler)

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[ChangeEvent], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[ChangeEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the value is committed (on blur).

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("change", handler)

    @overload
    def on_focus(self) -> Stream: ...
    @overload
    def on_focus(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_focus(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the text area gains focus.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("focus", handler)

    @overload
    def on_blur(self) -> Stream: ...
    @overload
    def on_blur(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_blur(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the text area loses focus.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("blur", handler)

    @overload
    def on_valid(self) -> Stream: ...
    @overload
    def on_valid(self, handler: Callable[[ValidationEvent], Any]) -> Subscription: ...
    def on_valid(self, handler: Callable[[ValidationEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when validation passes.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("valid", handler)

    @overload
    def on_invalid(self) -> Stream: ...
    @overload
    def on_invalid(self, handler: Callable[[ValidationEvent], Any]) -> Subscription: ...
    def on_invalid(self, handler: Callable[[ValidationEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when validation fails.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("invalid", handler)

    @overload
    def on_validate(self) -> Stream: ...
    @overload
    def on_validate(self, handler: Callable[[ValidationEvent], Any]) -> Subscription: ...
    def on_validate(self, handler: Callable[[ValidationEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired after any validation run.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("validate", handler)

    @overload
    def on_modified(self) -> Stream: ...
    @overload
    def on_modified(self, handler: Callable[[TextModifiedEvent], Any]) -> Subscription: ...
    def on_modified(self, handler: Callable[[TextModifiedEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the dirty state changes.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("modified", handler)

    @overload
    def on_undo(self) -> Stream: ...
    @overload
    def on_undo(self, handler: Callable[[InputEvent], Any]) -> Subscription: ...
    def on_undo(self, handler: Callable[[InputEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired after an undo operation.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("undo", handler)

    @overload
    def on_redo(self) -> Stream: ...
    @overload
    def on_redo(self, handler: Callable[[InputEvent], Any]) -> Subscription: ...
    def on_redo(self, handler: Callable[[InputEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired after a redo operation.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("redo", handler)


register_widget_events(TextArea, _TEXTAREA_EVENTS)
