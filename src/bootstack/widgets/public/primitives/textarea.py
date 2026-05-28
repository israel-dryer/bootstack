from __future__ import annotations

import tkinter
from typing import Any, Callable

from bootstack.widgets.composites.textarea.textarea import TextArea as _InternalTextArea
from bootstack.widgets.public.base import PublicWidgetBase
from bootstack.widgets.public.events import register_widget_events
from bootstack.widgets.public.subscription import Subscription

_TEXTAREA_EVENTS: dict[str, str] = {
    "change": "<<Change>>",
    "input":  "<KeyRelease>",
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
        from bootstack.widgets.public.events import resolve_event
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

    # ----- Methods -----

    def clear(self) -> None:
        """Clear all text content."""
        self._internal.value = ""

    def insert(self, index: str, text: str) -> None:
        """Insert `text` at `index` (Tk text index, e.g. `'end'` or `'1.0'`)."""
        self._internal._core.text.insert(index, text)

    def select_all(self) -> None:
        """Select all text content."""
        self._internal._core.text.tag_add("sel", "1.0", "end")

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


register_widget_events(TextArea, _TEXTAREA_EVENTS)
