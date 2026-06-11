from __future__ import annotations

from typing import overload, Any, Callable, TYPE_CHECKING

from bootstack.widgets._impl.primitives.optionmenu import OptionMenu as _InternalOptionMenu
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._core.options import record_to_dict
from bootstack.events import ChangeEvent, Subscription
from bootstack.streams import Stream
from bootstack.widgets.types import AccentToken, Event, Option, OptionDict, WidgetDensity, ButtonVariant

if TYPE_CHECKING:
    from bootstack.signals import Signal

_SELECTBUTTON_EVENTS: dict[str, str] = {
    "change": "<<Change>>",
}


class SelectButton(PublicWidgetBase):
    """A button that opens a dropdown value list — a button-styled alternative to `Select`.

    Clicking the button opens a popup list of options. The selected value is
    displayed on the button face. Unlike `Select`, there is no text field —
    the button is the only interaction point.

    Args:
        options: Choices shown in the popup. Each item is a plain string, a
            `(text, value)` tuple, or a `{'text': ..., 'value': ...}` dict — so
            an option's displayed label can differ from its stored value, e.g.
            `["Light", "Dark"]` or `[("Light theme", "light")]`.
        value: Initially selected value (value-space — matches an option's
            value, not its label). Must match one of the options.
        signal: Reactive `Signal[str]` controlling the selected value. When
            provided, `value=` is ignored — seed the Signal directly.
        disabled: If `True`, the button is non-interactive and dimmed.
            Defaults to `False`.
        accent: Accent token applied to the button.
        variant: Button style variant. Default `'solid'`.
        density: Padding density.
        icon: Bootstrap Icons name shown on the button beside the value.
        parent: Explicit parent widget. If omitted, the current
            context-stack container is used.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        options: list[Option] | None = None,
        *,
        value: Any = None,
        signal: "Signal[str] | None" = None,
        disabled: bool = False,
        accent: AccentToken | str | None = None,
        variant: ButtonVariant = "default",
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

        self._internal = _InternalOptionMenu(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Properties -----

    @property
    def value(self) -> Any:
        """The currently selected value, or `None` if unselected.

        This is the option's *value* (value-space). For the displayed label, see
        `text`.
        """
        return self._internal.get()

    @value.setter
    def value(self, v: Any) -> None:
        self._internal.set(v)

    @property
    def text(self) -> str:
        """The label currently shown on the button — the selected option's text.

        Read-only; the complement of `value`. Assign to `value` to change the
        selection.
        """
        return self._internal.text

    @property
    def selection(self) -> dict | None:
        """The selected option as a full record dict — the data bag — or `None`.

        `{'text': ..., 'value': ..., ...any extra keys}`, indexed by key like
        any record. Read-only.
        """
        return self._internal.selection

    @property
    def options(self) -> list[OptionDict]:
        """The available options as normalized `{'text', 'value'}` records.

        Assigning a new list rebuilds the dropdown. Accepts the same `Option`
        forms as the constructor (strings, `(text, value)` tuples, or dicts).
        """
        return [record_to_dict(r) for r in self._internal.cget("options")]

    @options.setter
    def options(self, items: list[Option]) -> None:
        self._internal.configure(options=list(items))

    @property
    def signal(self) -> "Signal[str] | None":
        """The reactive `Signal` linked to this button, or `None`."""
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

        Args:
            handler: Called with a :class:`~bootstack.events.ChangeEvent`. Omit
                to get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("change", handler)


register_widget_events(SelectButton, _SELECTBUTTON_EVENTS)
