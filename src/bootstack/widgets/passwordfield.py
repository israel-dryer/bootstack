from __future__ import annotations

import tkinter
from typing import Any, Callable

from bootstack.widgets._impl.composites.passwordentry import PasswordEntry as _InternalPasswordEntry
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._core.subscription import Subscription
from bootstack.widgets.textfield import _INNER_ENTRY_SEQUENCES

_PASSWORD_FIELD_EVENTS: dict[str, str] = {
    "change": "<<Change>>",
    "submit": "<Return>",
}


class PasswordField(PublicWidgetBase):
    """A masked text field for password input with an optional visibility toggle.

    Args:
        value: Initial password value (displayed masked).
        label: Label displayed above the field.
        message: Hint text displayed below the field.
        required: If True, field cannot be left empty.
        mask_char: Character used to mask input. Default `'•'`.
        show_visibility_toggle: If True (default), shows the eye-icon visibility button.
        disabled: If True, field is non-interactive.
        read_only: If True, value is visible but not editable.
        width: Width in character cells.
        accent: Accent token for the focus ring.
        density: Widget density — `'default'` or `'compact'`.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        value: str = "",
        *,
        label: str | None = None,
        message: str | None = None,
        required: bool = False,
        mask_char: str = "•",
        show_visibility_toggle: bool = True,
        disabled: bool = False,
        read_only: bool = False,
        width: int | None = None,
        accent: str | None = None,
        density: str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "show": mask_char,
            "show_visibility_toggle": show_visibility_toggle,
        }
        if value:
            internal_kwargs["value"] = value
        if label is not None:
            internal_kwargs["label"] = label
        if message is not None:
            internal_kwargs["message"] = message
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
        internal_kwargs.update(kwargs)

        self._internal = _InternalPasswordEntry(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Event routing -----

    def _entry_widget(self) -> tkinter.Misc:
        return self._internal._entry

    def on(self, event: str, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        from bootstack.widgets._core.events import resolve_event
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
        return str(self._internal._entry.cget("state")) == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    # ----- Methods -----

    def reveal(self) -> None:
        """Remove character masking to show the password in plain text."""
        self._internal.reveal()

    def hide(self) -> None:
        """Restore character masking."""
        self._internal.hide()

    # ----- Event shorthands -----

    def on_change(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired when the value is committed.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("change", handler)


register_widget_events(PasswordField, _PASSWORD_FIELD_EVENTS)
