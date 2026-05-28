from __future__ import annotations

import tkinter
from typing import Any, Callable

from bootstack.widgets.composites.textentry import TextEntry as _InternalTextEntry
from bootstack.widgets.public.base import PublicWidgetBase
from bootstack.widgets.public.events import resolve_event, register_widget_events
from bootstack.widgets.public.subscription import Subscription

# Events that fire on the inner entry part, not the outer Frame.
_INNER_ENTRY_SEQUENCES = frozenset({
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
    "change":   "<<Change>>",
    "valid":    "<<Valid>>",
    "invalid":  "<<Invalid>>",
    "validate": "<<Validate>>",
    "submit":   "<Return>",
}


class TextField(PublicWidgetBase):
    """Single-line text input with optional label, message, and validation.

    Args:
        value: Initial text value.
        text_signal: Reactive `Signal` linked to the field text.
        label: Label displayed above the input.
        message: Hint text displayed below the input.
        required: If True, marks the field as required and prevents empty submission.
        mask_char: Character used to mask input (e.g. `'*'` for passwords).
        read_only: If True, text is visible but not editable.
        disabled: If True, field is non-interactive.
        width: Width in character cells.
        justify: Text alignment — `'left'`, `'center'`, or `'right'`.
        font: Font token string.
        color: Text color.
        accent: Accent token for the focus ring.
        density: Widget density — `'default'` or `'compact'`.
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
        mask_char: str | None = None,
        read_only: bool = False,
        disabled: bool = False,
        width: int | None = None,
        justify: str | None = None,
        font: Any = None,
        color: str | None = None,
        accent: str | None = None,
        density: str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {}
        if value:
            internal_kwargs["value"] = value
        if text_signal is not None:
            internal_kwargs["textsignal"] = text_signal
        if label is not None:
            internal_kwargs["label"] = label
        if message is not None:
            internal_kwargs["message"] = message
        if required:
            internal_kwargs["required"] = True
        if mask_char is not None:
            internal_kwargs["show"] = mask_char
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
        if color is not None:
            internal_kwargs["foreground"] = color
        if accent is not None:
            internal_kwargs["accent"] = accent
        if density is not None:
            internal_kwargs["density"] = density
        internal_kwargs.update(kwargs)

        self._internal = _InternalTextEntry(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Event routing -----

    def _entry_widget(self) -> tkinter.Misc:
        """Return the inner entry widget where input events actually fire."""
        return self._internal._entry

    def on(self, event: str, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        sequence = resolve_event(self, str(event))
        widget = self._entry_widget() if sequence in _INNER_ENTRY_SEQUENCES else self._internal
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

    # ----- Methods -----

    def clear(self) -> None:
        """Clear the field text."""
        self._internal.value = ""

    def select_all(self) -> None:
        """Select all text in the field."""
        self._entry_widget().selection_range(0, "end")

    def select_range(self, start: int, end: int) -> None:
        """Select text between `start` and `end` character positions."""
        self._entry_widget().selection_range(start, end)

    def set_cursor(self, index: int) -> None:
        """Move the insertion cursor to `index`."""
        self._entry_widget().icursor(index)

    def insert(self, index: int, text: str) -> None:
        """Insert `text` at `index`."""
        self._entry_widget().insert(index, text)

    def delete(self, start: int, end: int | None = None) -> None:
        """Delete characters from `start` to `end` (or just `start` if `end` is None)."""
        self._entry_widget().delete(start, "end" if end is None else end)

    # ----- Event shorthands -----

    def on_change(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback for `<<Change>>` events (fires on commit).

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("change", handler)

    def on_submit(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback for `<Return>` (Enter key) events.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("submit", handler)

    def on_validate(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired after any validation run.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("validate", handler)


register_widget_events(TextField, _TEXTFIELD_EVENTS)
