from __future__ import annotations

from typing import overload, Any, Callable, TYPE_CHECKING

from bootstack.widgets._impl.primitives.optionmenu import OptionMenu as _InternalOptionMenu
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.events import ChangeEvent, Subscription
from bootstack.streams import Stream
from bootstack.widgets.types import AccentToken, Event, VariantToken, WidgetDensity

if TYPE_CHECKING:
    from bootstack.signals import Signal

_SELECTBUTTON_EVENTS: dict[str, str] = {
    "change": "<<Change>>",
}


class SelectButton(PublicWidgetBase):
    """A button that opens a dropdown value list — a button-styled alternative to ``Select``.

    Clicking the button opens a popup list of options. The selected value is
    displayed on the button face. Unlike ``Select``, there is no text field —
    the button is the only interaction point.

    Args:
        options: Values to display in the list. Each item is converted to a
            string for display, e.g. ``["Light", "Dark", "Auto"]``.
        value: Initially selected value.
        signal: Reactive ``Signal[str]`` controlling the selected value. When
            provided, ``value=`` is ignored — seed the Signal directly.
        disabled: If ``True``, the button is non-interactive and dimmed.
            Defaults to ``False``.
        accent: Accent token. One of ``'primary'``, ``'secondary'``,
            ``'info'``, ``'success'``, ``'warning'``, ``'danger'``,
            ``'default'``.
        variant: Style variant token. ``'solid'`` (default), ``'outline'``,
            or ``'ghost'``.
        density: Padding density. ``'default'`` or ``'compact'``.
        icon: Bootstrap Icons name shown on the button beside the value.
        parent: Explicit parent widget. If omitted, the current
            context-stack container is used.
    """

    def __init__(
        self,
        options: list[Any] | None = None,
        *,
        value: Any = None,
        signal: "Signal[str] | None" = None,
        disabled: bool = False,
        accent: AccentToken | str | None = None,
        variant: VariantToken | str | None = None,
        density: WidgetDensity | None = None,
        icon: str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "options": options or [],
        }
        if value is not None:
            internal_kwargs["value"] = value
        if signal is not None:
            internal_kwargs["textsignal"] = signal
        if disabled:
            internal_kwargs["state"] = "disabled"
        if accent is not None:
            internal_kwargs["accent"] = accent
        if variant is not None:
            internal_kwargs["variant"] = variant
        if density is not None:
            internal_kwargs["density"] = density
        if icon is not None:
            internal_kwargs["icon"] = icon
        internal_kwargs.update(kwargs)

        self._internal = _InternalOptionMenu(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Properties -----

    @property
    def value(self) -> str:
        """The currently selected value."""
        return self._internal.get()

    @value.setter
    def value(self, v: Any) -> None:
        self._internal.set(v)

    @property
    def signal(self) -> "Signal[str] | None":
        """The reactive ``Signal`` linked to this button, or ``None``."""
        return getattr(self._internal, 'textsignal', None)

    @property
    def disabled(self) -> bool:
        """Whether the button is non-interactive."""
        return str(self._internal.cget("state")) == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    # ----- Event shorthands -----

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[ChangeEvent], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[ChangeEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired whenever the selected value changes.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("change", handler)


register_widget_events(SelectButton, _SELECTBUTTON_EVENTS)
