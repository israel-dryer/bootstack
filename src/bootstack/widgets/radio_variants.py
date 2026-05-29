from __future__ import annotations

import tkinter
from typing import Any, Callable

from bootstack.widgets._impl.primitives.radiobutton import RadioButton as _InternalRadioButton
from bootstack.widgets._impl.primitives.radiotoggle import RadioToggle as _InternalRadioToggle
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._core.subscription import Subscription

_RADIO_EVENTS: dict[str, str] = {
    "change": "<<Change>>",
    "select": "<<Select>>",
}


class _RadioBase(PublicWidgetBase):
    """Shared base for Radio and RadioToggleButton."""

    _internal_class: type

    def __init__(
        self,
        label: str = "",
        value: Any = None,
        *,
        signal: Any = None,
        text_signal: Any = None,
        on_change: Callable[[], Any] | None = None,
        icon: str | None = None,
        selected_icon: str | None = None,
        unselected_icon: str | None = None,
        icon_only: bool = False,
        show_indicator: bool = True,
        compound: str | None = None,
        disabled: bool = False,
        accent: str | None = None,
        density: str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        _ctor_callback = on_change

        internal_kwargs: dict[str, Any] = {}
        if label:
            internal_kwargs["text"] = label
        if value is not None:
            internal_kwargs["value"] = value
        if signal is not None:
            internal_kwargs["signal"] = signal
        if text_signal is not None:
            internal_kwargs["textsignal"] = text_signal
        if icon is not None:
            internal_kwargs["icon"] = icon
        if selected_icon is not None:
            internal_kwargs["on_icon"] = selected_icon
        if unselected_icon is not None:
            internal_kwargs["off_icon"] = unselected_icon
        if icon_only:
            internal_kwargs["icon_only"] = True
        if not show_indicator:
            internal_kwargs["show_indicator"] = False
        if compound is not None:
            internal_kwargs["compound"] = compound
        if disabled:
            internal_kwargs["state"] = "disabled"
        if accent is not None:
            internal_kwargs["accent"] = accent
        if density is not None:
            internal_kwargs["density"] = density
        internal_kwargs.update(kwargs)

        self._internal = self._internal_class(tk_master, **internal_kwargs)

        def _command():
            self._internal.event_generate("<<Change>>")
            self._internal.event_generate("<<Select>>")
            if _ctor_callback is not None:
                _ctor_callback()

        self._internal.configure(command=_command)
        self._attach_to_parent(layout_kw)

    # ----- Properties -----

    @property
    def selected(self) -> bool:
        """True if this radio is the currently selected option in its group."""
        return self._internal.get() == self._internal.cget("value")

    @property
    def disabled(self) -> bool:
        return str(self._internal.cget("state")) == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    # ----- Methods -----

    def select(self) -> None:
        """Programmatically select this radio button."""
        self._internal.invoke()

    # ----- Event shorthands -----

    def on_change(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired when this radio is selected.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("change", handler)

    def on_select(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired when this radio is selected.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("select", handler)


class Radio(_RadioBase):
    """A single radio button — one selectable option in a mutually-exclusive group.

    Radio buttons in a group share a `signal`; clicking one sets the signal
    to the radio's `value`.

    Usage::

        sig = bs.Signal("a")
        bs.Radio("Option A", "a", signal=sig)
        bs.Radio("Option B", "b", signal=sig)

    Args:
        label: Text displayed beside the radio indicator.
        value: The value written to `signal` when this radio is selected.
        signal: Shared `Signal` that holds the group's current value.
        text_signal: Reactive `Signal` linked to the label text.
        on_change: Callback fired when this radio is selected.
        icon: Icon shown for all states.
        selected_icon: Icon shown when this radio is selected.
        unselected_icon: Icon shown when this radio is not selected.
        icon_only: If True, removes extra padding reserved for the label.
        show_indicator: If False, hides the circular indicator.
        compound: Image placement relative to text.
        disabled: If True, widget is non-interactive.
        accent: Accent token, e.g. `'primary'`, `'success'`.
        density: Widget density — `'default'` or `'compact'`.
        parent: Override the context-stack parent.
    """
    _internal_class = _InternalRadioButton


class RadioToggleButton(_RadioBase):
    """A radio button that renders as a toggle button — toolbar/segmented-control style.

    Behaves identically to `Radio` but renders as a depressed button when
    selected rather than showing the circular indicator.

    Args:
        label: Text displayed on the button.
        value: The value written to `signal` when this button is selected.
        signal: Shared `Signal` that holds the group's current value.
        text_signal: Reactive `Signal` linked to the label text.
        on_change: Callback fired when this button is selected.
        icon: Icon shown for all states.
        selected_icon: Icon shown when selected.
        unselected_icon: Icon shown when not selected.
        icon_only: If True, removes extra label padding.
        disabled: If True, widget is non-interactive.
        accent: Accent token, e.g. `'primary'`, `'success'`.
        density: Widget density — `'default'` or `'compact'`.
        parent: Override the context-stack parent.
    """
    _internal_class = _InternalRadioToggle


register_widget_events(Radio, _RADIO_EVENTS)
register_widget_events(RadioToggleButton, _RADIO_EVENTS)