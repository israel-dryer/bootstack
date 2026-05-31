from __future__ import annotations

import tkinter
from typing import overload, Any, Callable, TYPE_CHECKING

from bootstack.widgets._impl.composites.selectbox import SelectBox as _InternalSelectBox
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import resolve_event, register_widget_events
from bootstack.widgets._core.subscription import Subscription
from bootstack.widgets._core.stream import Stream
from bootstack.widgets.textfield import _INNER_ENTRY_SEQUENCES
from bootstack.widgets.types import AccentToken, WidgetDensity

if TYPE_CHECKING:
    from bootstack.signals import Signal

_SELECT_EVENTS: dict[str, str] = {
    "change": "<<Change>>",
}


class Select(PublicWidgetBase):
    """A single-selection dropdown field.

    The options list is the first positional argument. All options are
    keyword-only.

    Args:
        options: List of string choices presented in the popup. Defaults to
            an empty list.
        value: Initially selected value.
        signal: Reactive ``Signal[str]`` linked to the selected value. The
            field and signal stay in sync automatically.
        label: Label displayed above the field.
        message: Hint or helper text displayed below the field.
        required: If ``True``, marks the field as required and prevents
            empty submission.
        searchable: If ``True``, typing in the field filters the option
            list. Defaults to ``False``.
        allow_custom_values: If ``True``, users may type values not in
            ``options``. Defaults to ``False``.
        read_only: If ``True``, value is visible but the popup cannot be
            opened.
        disabled: If ``True``, field is fully non-interactive and dimmed.
        width: Width in character units.
        accent: Accent token applied to the focus ring. One of
            ``'primary'``, ``'secondary'``, ``'info'``, ``'success'``,
            ``'warning'``, ``'danger'``, ``'default'``.
        density: Padding density. ``'default'`` or ``'compact'``.
        parent: Explicit parent widget. If omitted, the current
            context-stack container is used.
    """

    def __init__(
        self,
        options: list[str] | None = None,
        *,
        value: str | None = None,
        signal: "Signal[str] | None" = None,
        label: str | None = None,
        message: str | None = None,
        required: bool = False,
        searchable: bool = False,
        allow_custom_values: bool = False,
        read_only: bool = False,
        disabled: bool = False,
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
            "items":              options or [],
            "enable_search":      searchable,
            "allow_custom_values": allow_custom_values,
        }
        if value is not None:
            internal_kwargs["value"] = value
        if signal is not None:
            internal_kwargs["textsignal"] = signal
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

        self._internal = _InternalSelectBox(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Event routing -----

    def _entry_widget(self) -> tkinter.Misc:
        return self._internal._entry

    @overload
    def on(self, event: str) -> Stream: ...
    @overload
    def on(self, event: str, handler: Callable[[tkinter.Event], Any]) -> Subscription: ...
    def on(self, event: str, handler: Callable[[tkinter.Event], Any] | None = None) -> Stream | Subscription:
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
        """The currently selected value."""
        return self._internal.value

    @value.setter
    def value(self, v: str) -> None:
        self._internal.value = v

    @property
    def options(self) -> list[str]:
        """The list of available options."""
        return list(self._internal._items)

    @options.setter
    def options(self, items: list[str]) -> None:
        self._internal._items = list(items)

    @property
    def selected_index(self) -> int:
        """Zero-based index of the selected option, or ``-1`` if none selected."""
        return self._internal.selected_index

    @selected_index.setter
    def selected_index(self, v: int) -> None:
        self._internal.selected_index = v

    @property
    def read_only(self) -> bool:
        """Whether the field is visible but the popup cannot be opened."""
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

    # ----- Event shorthands -----

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[tkinter.Event], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[tkinter.Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the selection changes.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("change", handler)


register_widget_events(Select, _SELECT_EVENTS)
