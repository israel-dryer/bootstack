from __future__ import annotations

import tkinter
from typing import Any, Callable

from bootstack.widgets._impl.composites.textarea.textarea import TextArea as _InternalTextArea
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._core.subscription import Subscription

_TEXTAREA_EVENTS: dict[str, str] = {
    "change":   "<<Change>>",
    "input":    "<KeyRelease>",
    "blur":     "<FocusOut>",
    "valid":    "<<Valid>>",
    "invalid":  "<<Invalid>>",
    "modified": "<<TextModified>>",
    "undo":     "<<TextUndo>>",
    "redo":     "<<TextRedo>>",
}


class TextArea(PublicWidgetBase):
    """A multi-line text input with optional label, placeholder, and scrollbars.

    Args:
        value: Initial text content.
        text_signal: Reactive `Signal[str]` linked to the text content.
        label: Label displayed above the field.
        message: Hint text displayed below the field.
        required: If True, field cannot be left empty.
        placeholder: Placeholder text shown when the field is empty.
        max_length: Maximum number of characters allowed.
        read_only: If True, text is visible but not editable.
        wrap: If True (default), long lines wrap at the widget boundary.
        height: Visible row count. Default `4`.
        scrollbars: Scrollbar visibility — `'auto'` (default), `'vertical'`,
            `'both'`, or `'none'`.
        font: Font token. Default `'body'`.
        accent: Accent token for the focus border.
        show_border: If True (default), wraps the text area in a themed
            border with a focus ring.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        value: str = "",
        *,
        text_signal: Any = None,
        label: str | None = None,
        message: str | None = None,
        required: bool = False,
        placeholder: str | None = None,
        max_length: int | None = None,
        read_only: bool = False,
        wrap: bool = True,
        height: int = 4,
        scrollbars: str = "auto",
        font: Any = "body",
        accent: str = "primary",
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
            "show_border": show_border,
            "font": font,
            "accent": accent,
        }
        if text_signal is not None:
            internal_kwargs["textsignal"] = text_signal
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
        """The underlying Tk Text widget where input events fire."""
        return self._internal._core.text

    def on(self, event: str, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        from bootstack.widgets._core.events import resolve_event
        sequence = resolve_event(self, str(event))
        # Change and keystroke events fire on the inner text widget
        inner_sequences = {"<<Change>>", "<KeyRelease>", "<FocusIn>", "<FocusOut>"}
        widget = self._text_widget() if sequence in inner_sequences else self._internal
        bind_id = widget.bind(sequence, handler, add="+")
        return Subscription(widget, sequence, bind_id)

    # ----- Properties -----

    @property
    def value(self) -> str:
        return self._internal.value

    @value.setter
    def value(self, v: str) -> None:
        self._internal.value = v

    @property
    def is_dirty(self) -> bool:
        """True if the content has changed since the last `mark_saved()` call."""
        return self._internal.is_dirty

    # ----- Methods -----

    def clear(self) -> None:
        """Clear all text content."""
        self._internal.value = ""

    def insert(self, index: str, text: str) -> None:
        """Insert `text` at `index` (Tk text index, e.g. `'end'` or `'1.0'`)."""
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

    def on_change(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired when the value is committed (blur).

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("change", handler)

    def on_input(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired on every keystroke.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("input", handler)

    def on_blur(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired when the text area loses focus.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("blur", handler)

    def on_valid(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired when validation passes.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("valid", handler)

    def on_invalid(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired when validation fails.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("invalid", handler)

    def on_modified(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired when the dirty state changes.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("modified", handler)

    def on_undo(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired after an undo operation.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("undo", handler)

    def on_redo(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired after a redo operation.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("redo", handler)


register_widget_events(TextArea, _TEXTAREA_EVENTS)
