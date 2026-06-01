from __future__ import annotations

from typing import overload, Any, Callable, TYPE_CHECKING

from bootstack.widgets._impl.primitives.checkbutton import CheckButton as _InternalCheckButton
from bootstack.widgets._impl.primitives.switch import Switch as _InternalSwitch
from bootstack.widgets._impl.primitives.checktoggle import CheckToggle as _InternalCheckToggle
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._core.subscription import Subscription
from bootstack.widgets._core.stream import Stream
from bootstack.widgets.types import AccentToken, Event, VariantToken, WidgetDensity

if TYPE_CHECKING:
    from bootstack.signals import Signal

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
        signal: "Signal | None" = None,
        value: Any = None,
        checked_value: Any = True,
        unchecked_value: Any = False,
        tristate: bool = False,
        on_change: Callable[[], Any] | None = None,
        on_icon: str | None = None,
        off_icon: str | None = None,
        icon_only: bool = False,
        show_indicator: bool = True,
        disabled: bool = False,
        accent: AccentToken | str | None = None,
        variant: VariantToken | str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        self._checked_value = checked_value
        self._unchecked_value = unchecked_value
        self._tristate = tristate

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
        if on_icon is not None:
            internal_kwargs["on_icon"] = on_icon
        if off_icon is not None:
            internal_kwargs["off_icon"] = off_icon
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
        internal_kwargs.update(kwargs)

        self._internal = self._internal_class(tk_master, **internal_kwargs)

        # Seed initial value when no signal was passed.
        # tristate=False: default to unchecked_value so the box never shows the
        # indeterminate dash unexpectedly. tristate=True: leave unseeded so the
        # initial state is None (indeterminate) unless value= was explicitly given.
        if signal is None:
            if value is not None:
                self._internal.set(value)
            elif not tristate:
                self._internal.set(unchecked_value)

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
        """The current value.

        Returns ``checked_value`` when checked, ``unchecked_value`` when
        unchecked, or ``None`` when in the indeterminate state (only possible
        when ``tristate=True``).
        """
        v = self._internal.get()
        if v == self._checked_value:
            return self._checked_value
        if v == self._unchecked_value:
            return self._unchecked_value
        return None

    @value.setter
    def value(self, v: Any) -> None:
        self._internal.set(v)

    @property
    def checked(self) -> bool:
        """Whether the control is in the checked/on state."""
        return self._internal.get() == self._checked_value

    @checked.setter
    def checked(self, v: bool) -> None:
        self._internal.set(self._checked_value if v else self._internal.cget("offvalue"))

    @property
    def signal(self) -> "Signal | None":
        """The reactive ``Signal`` linked to this control, or ``None``."""
        return getattr(self._internal, 'signal', None)

    @property
    def disabled(self) -> bool:
        """Whether the control is non-interactive."""
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
    def on_change(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired whenever the value changes.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("change", handler)

    @overload
    def on_check(self) -> Stream: ...
    @overload
    def on_check(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_check(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the control becomes checked/selected.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("check", handler)

    @overload
    def on_uncheck(self) -> Stream: ...
    @overload
    def on_uncheck(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_uncheck(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the control becomes unchecked/deselected.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("uncheck", handler)


class Checkbox(_BooleanControlBase):
    """A labelled checkbox — checked or unchecked.

    The label is the first positional argument. All options are keyword-only.

    Args:
        label: Label text displayed beside the checkbox.
        signal: Reactive ``Signal`` controlling the checked state. When
            provided, ``value=`` is ignored — seed the Signal directly.
        value: Initial value. Ignored when ``signal=`` is passed.
        checked_value: Value representing the checked state. Defaults to
            ``True``.
        unchecked_value: Value representing the unchecked state. Defaults
            to ``False``.
        tristate: If ``True``, enables a third indeterminate state. When
            indeterminate the box shows a dash indicator and ``value``
            returns ``None``. If no ``value=`` or ``signal=`` is provided,
            the checkbox starts in the indeterminate state. Defaults to
            ``False``.
        on_change: Shorthand callback fired on every toggle. Equivalent to
            ``checkbox.on_change(fn)``.
        on_icon: Bootstrap Icons name shown when the checkbox is checked.
            Pair with ``off_icon=`` to display different icons per state,
            e.g. ``on_icon="check-circle-fill", off_icon="circle"``.
        off_icon: Bootstrap Icons name shown when the checkbox is unchecked.
        icon_only: If ``True``, hides the label text and shows only the icon.
            Combine with ``on_icon=``/``off_icon=`` and
            ``show_indicator=False`` for fully icon-driven checkboxes.
        show_indicator: If ``False``, hides the checkbox box indicator.
            Useful when ``on_icon=``/``off_icon=`` serve as the visual cue.
        disabled: If ``True``, widget is non-interactive and dimmed.
            Defaults to ``False``.
        accent: Accent token. One of ``'primary'``, ``'secondary'``,
            ``'info'``, ``'success'``, ``'warning'``, ``'danger'``,
            ``'default'``.
        variant: Style variant token (theme-defined, e.g. ``'round'``,
            ``'square'``).
        parent: Explicit parent widget. If omitted, the current
            context-stack container is used.
    """
    _internal_class = _InternalCheckButton


class Switch(_BooleanControlBase):
    """A toggle switch — on or off.

    Renders as a sliding track-and-thumb control. Use in place of a checkbox
    when the action takes effect immediately (e.g. enable/disable a setting).

    Args:
        label: Label text displayed beside the switch.
        signal: Reactive ``Signal`` controlling the on/off state. When
            provided, ``value=`` is ignored — seed the Signal directly.
        value: Initial value. Ignored when ``signal=`` is passed.
        checked_value: Value representing the on state. Defaults to
            ``True``.
        unchecked_value: Value representing the off state. Defaults to
            ``False``.
        on_change: Shorthand callback fired on every toggle. Equivalent to
            ``switch.on_change(fn)``.
        disabled: If ``True``, widget is non-interactive and dimmed.
            Defaults to ``False``.
        accent: Accent token. One of ``'primary'``, ``'secondary'``,
            ``'info'``, ``'success'``, ``'warning'``, ``'danger'``,
            ``'default'``.
        variant: Style variant token (theme-defined).
        parent: Explicit parent widget. If omitted, the current
            context-stack container is used.
    """
    _internal_class = _InternalSwitch


class ToggleButton(_BooleanControlBase):
    """A button that stays pressed when active — toolbar-style toggle.

    Renders as a depressed button rather than a checkbox or switch. Commonly
    used in toolbars and button groups to represent a persistent on/off state.

    Args:
        label: Button label text.
        signal: Reactive ``Signal`` controlling the pressed state. When
            provided, ``value=`` is ignored — seed the Signal directly.
        value: Initial value. Ignored when ``signal=`` is passed.
        checked_value: Value representing the pressed/active state. Defaults
            to ``True``.
        unchecked_value: Value representing the unpressed/inactive state.
            Defaults to ``False``.
        on_change: Shorthand callback fired on every toggle. Equivalent to
            ``btn.on_change(fn)``.
        on_icon: Bootstrap Icons name shown when the button is active/pressed.
            Use alone to swap icon on activation, or pair with ``off_icon=``
            to show different icons per state,
            e.g. ``on_icon="star-fill", off_icon="star"``.
        off_icon: Bootstrap Icons name shown when the button is inactive.
            Can be used alone or paired with ``on_icon=``.
        icon_only: If ``True``, shows only the icon with no label text.
            Requires ``on_icon=`` or ``off_icon=`` to be set.
        disabled: If ``True``, widget is non-interactive and dimmed.
            Defaults to ``False``.
        accent: Accent token. One of ``'primary'``, ``'secondary'``,
            ``'info'``, ``'success'``, ``'warning'``, ``'danger'``,
            ``'default'``.
        variant: Style variant token (theme-defined).
        density: Padding density. ``'default'`` or ``'compact'``.
        parent: Explicit parent widget. If omitted, the current
            context-stack container is used.
    """
    _internal_class = _InternalCheckToggle

    def __init__(
        self,
        label: str = "",
        *,
        signal: "Signal | None" = None,
        value: Any = None,
        checked_value: Any = True,
        unchecked_value: Any = False,
        on_change: Callable[[], Any] | None = None,
        on_icon: str | None = None,
        off_icon: str | None = None,
        icon_only: bool = False,
        disabled: bool = False,
        accent: AccentToken | str | None = None,
        variant: VariantToken | str | None = None,
        density: WidgetDensity | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            label,
            signal=signal,
            value=value,
            checked_value=checked_value,
            unchecked_value=unchecked_value,
            on_change=on_change,
            on_icon=on_icon,
            off_icon=off_icon,
            icon_only=icon_only,
            disabled=disabled,
            accent=accent,
            variant=variant,
            density=density,
            parent=parent,
            **kwargs,
        )


register_widget_events(Checkbox, _BOOLEAN_EVENTS)
register_widget_events(Switch, _BOOLEAN_EVENTS)
register_widget_events(ToggleButton, _BOOLEAN_EVENTS)
