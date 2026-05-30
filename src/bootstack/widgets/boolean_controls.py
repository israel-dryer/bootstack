from __future__ import annotations

import tkinter
from typing import overload, Any, Callable

from bootstack.widgets._impl.primitives.checkbutton import CheckButton as _InternalCheckButton
from bootstack.widgets._impl.primitives.switch import Switch as _InternalSwitch
from bootstack.widgets._impl.primitives.checktoggle import CheckToggle as _InternalCheckToggle
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._core.subscription import Subscription
from bootstack.widgets._core.stream import Stream

_BOOLEAN_EVENTS: dict[str, str] = {
    "change":   "<<Change>>",
    "check":    "<<ToggleOn>>",
    "uncheck":  "<<ToggleOff>>",
}


class _BooleanControlBase(PublicWidgetBase):
    """Shared base for Checkbox, Switch, and ToggleButton."""

    _internal_class: type  # set by subclass

    def __init__(
        self,
        label: str = "",
        *,
        signal: Any = None,
        value: Any = None,
        checked_value: Any = True,
        unchecked_value: Any = False,
        on_change: Callable[[], Any] | None = None,
        icon: str | None = None,
        icon_only: bool = False,
        show_indicator: bool = True,
        disabled: bool = False,
        accent: str | None = None,
        variant: str | None = None,
        density: str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        self._checked_value = checked_value

        tk_master = self._parent._child_master() if self._parent else None

        # Ctor on_change callback — stored so the command wrapper can call it.
        _ctor_callback = on_change

        internal_kwargs: dict[str, Any] = {}
        if label:
            internal_kwargs["text"] = label
        if signal is not None:
            internal_kwargs["signal"] = signal
        if checked_value is not True:
            internal_kwargs["onvalue"] = checked_value
        if unchecked_value is not False:
            internal_kwargs["offvalue"] = unchecked_value
        if icon is not None:
            internal_kwargs["icon"] = icon
        if icon_only:
            internal_kwargs["icon_only"] = True
        if not show_indicator:
            internal_kwargs["show_indicator"] = False
        if disabled:
            internal_kwargs["state"] = "disabled"
        if accent is not None:
            internal_kwargs["accent"] = accent
        if variant is not None:
            internal_kwargs["variant"] = variant
        if density is not None:
            internal_kwargs["density"] = density
        internal_kwargs.update(kwargs)

        self._internal = self._internal_class(tk_master, **internal_kwargs)

        # Seed initial value only when no signal was passed (mirrors internal behaviour).
        if value is not None and signal is None:
            self._internal.set(value)

        # Wire command → virtual events so on_change() / on_check() subscriptions work.
        def _command():
            v = self._internal.get()
            self._internal.event_generate("<<Change>>")
            if v == self._checked_value:
                self._internal.event_generate("<<ToggleOn>>")
            else:
                self._internal.event_generate("<<ToggleOff>>")
            if _ctor_callback is not None:
                _ctor_callback()

        self._internal.configure(command=_command)
        self._attach_to_parent(layout_kw)

    # ----- Properties -----

    @property
    def value(self) -> Any:
        return self._internal.get()

    @value.setter
    def value(self, v: Any) -> None:
        self._internal.set(v)

    @property
    def checked(self) -> bool:
        return self._internal.get() == self._checked_value

    @checked.setter
    def checked(self, v: bool) -> None:
        self._internal.set(self._checked_value if v else self._internal.cget("offvalue"))

    @property
    def disabled(self) -> bool:
        return str(self._internal.cget("state")) == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    # ----- Methods -----

    def toggle(self) -> None:
        """Toggle the control's state programmatically."""
        self._internal.invoke()

    # ----- Event shorthands -----

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[tkinter.Event], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[tkinter.Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired whenever the value changes.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("change", handler)

    @overload
    def on_check(self) -> Stream: ...
    @overload
    def on_check(self, handler: Callable[[tkinter.Event], Any]) -> Subscription: ...
    def on_check(self, handler: Callable[[tkinter.Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the control is checked/selected.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("check", handler)

    @overload
    def on_uncheck(self) -> Stream: ...
    @overload
    def on_uncheck(self, handler: Callable[[tkinter.Event], Any]) -> Subscription: ...
    def on_uncheck(self, handler: Callable[[tkinter.Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the control is unchecked/deselected.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("uncheck", handler)


class Checkbox(_BooleanControlBase):
    """A labelled checkbox — checked or unchecked.

    Args:
        label: Label text displayed beside the checkbox.
        signal: Reactive `Signal` controlling the checked state.
        value: Initial value (ignored when `signal=` is passed).
        checked_value: Value that represents the checked state. Default `True`.
        unchecked_value: Value that represents the unchecked state. Default `False`.
        on_change: Callback fired on every toggle.
        show_indicator: If False, hides the box indicator (use with `icon=`).
        disabled: If True, widget is non-interactive.
        accent: Accent token, e.g. `'primary'`, `'success'`.
        variant: Style variant, e.g. `'round'`, `'square'`.
        parent: Override the context-stack parent.
    """
    _internal_class = _InternalCheckButton


class Switch(_BooleanControlBase):
    """A toggle switch — on or off.

    Same kwargs as `Checkbox`. Visual difference only: renders as a
    sliding track-and-thumb instead of a box.
    """
    _internal_class = _InternalSwitch


class ToggleButton(_BooleanControlBase):
    """A button that stays pressed when active — toolbar-style toggle.

    Same kwargs as `Checkbox`. Visual difference only: renders as a
    depressed button rather than a checkbox or switch.
    """
    _internal_class = _InternalCheckToggle


register_widget_events(Checkbox, _BOOLEAN_EVENTS)
register_widget_events(Switch, _BOOLEAN_EVENTS)
register_widget_events(ToggleButton, _BOOLEAN_EVENTS)
