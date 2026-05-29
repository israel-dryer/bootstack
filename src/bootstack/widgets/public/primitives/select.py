from __future__ import annotations

import tkinter
from typing import Any, Callable

from bootstack.widgets.composites.selectbox import SelectBox as _InternalSelectBox
from bootstack.widgets.public.base import PublicWidgetBase
from bootstack.widgets.public.events import register_widget_events
from bootstack.widgets.public.subscription import Subscription
from bootstack.widgets.public.primitives.textfield import _INNER_ENTRY_SEQUENCES

_SELECT_EVENTS: dict[str, str] = {
    "change": "<<Change>>",
}


class Select(PublicWidgetBase):
    """A single-selection dropdown field.

    Args:
        options: List of string choices presented in the popup.
        value: Initially selected value.
        text_signal: Reactive `Signal` linked to the selected text.
        label: Label displayed above the field.
        message: Hint text displayed below the field.
        required: If True, field cannot be left empty.
        searchable: If True, typing filters the option list.
        allow_custom_values: If True, users may type values not in `options`.
        disabled: If True, field is non-interactive.
        read_only: If True, value is visible but the popup cannot be opened.
        width: Width in character cells.
        accent: Accent token for the focus ring.
        density: Widget density — `'default'` or `'compact'`.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        options: list[str] | None = None,
        *,
        value: str | None = None,
        text_signal: Any = None,
        label: str | None = None,
        message: str | None = None,
        required: bool = False,
        searchable: bool = False,
        allow_custom_values: bool = False,
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
            "items": options or [],
            "enable_search": searchable,
            "allow_custom_values": allow_custom_values,
        }
        if value is not None:
            internal_kwargs["value"] = value
        if text_signal is not None:
            internal_kwargs["textsignal"] = text_signal
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

        self._internal = _InternalSelectBox(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Event routing -----

    def _entry_widget(self) -> tkinter.Misc:
        return self._internal._entry

    def on(self, event: str, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        from bootstack.widgets.public.events import resolve_event
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
    def options(self) -> list[str]:
        return list(self._internal._items)

    @options.setter
    def options(self, items: list[str]) -> None:
        self._internal._items = list(items)

    @property
    def disabled(self) -> bool:
        return str(self._internal._entry.cget("state")) == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    # ----- Event shorthands -----

    def on_change(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired when the selection changes.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("change", handler)


register_widget_events(Select, _SELECT_EVENTS)
