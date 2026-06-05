from __future__ import annotations

import tkinter
from typing import overload, Any, Callable

from bootstack.widgets._impl.composites.radiogroup import RadioGroup as _InternalRadioGroup
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.events import Subscription
from bootstack.streams import Stream
from bootstack.widgets.types import AccentToken, Event, Orient

_RADIOGROUP_EVENTS: dict[str, str] = {
    "change": "<<Change>>",
}


class RadioGroup(PublicWidgetBase):
    """A group of mutually exclusive radio buttons.

    Exactly one option can be selected at a time. Options are supplied at
    construction via ``options=`` and can be added or removed at runtime
    using ``add()`` and ``remove()``.

    Args:
        options: Choices for the group. Each item is either a plain string
            (label and value are the same) or a ``(label, value)`` tuple,
            e.g. ``["S", "M", "L"]`` or
            ``[("Small", "s"), ("Medium", "m"), ("Large", "l")]``.
        signal: Reactive ``Signal`` holding the selected value. When
            provided, ``value=`` is ignored — seed the Signal directly.
        value: Initially selected value. Ignored when ``signal=`` is passed.
        orient: Layout direction. ``'horizontal'`` (default) or
            ``'vertical'``.
        title: Optional label rendered above the button group.
        accent: Accent token applied to all buttons. One of ``'primary'``,
            ``'secondary'``, ``'info'``, ``'success'``, ``'warning'``,
            ``'danger'``, ``'default'``.
        disabled: If ``True``, all buttons are non-interactive and dimmed.
            Defaults to ``False``.
        parent: Explicit parent widget. If omitted, the current
            context-stack container is used.
    """

    def __init__(
        self,
        options: list[str | tuple[str, Any]] | None = None,
        *,
        signal: Any = None,
        value: Any = None,
        orient: Orient = "horizontal",
        title: str | None = None,
        accent: AccentToken | str | None = None,
        disabled: bool = False,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {"orient": orient}
        if signal is not None:
            internal_kwargs["signal"] = signal
        if value is not None:
            internal_kwargs["value"] = value
        if title is not None:
            internal_kwargs["text"] = title
        if accent is not None:
            internal_kwargs["accent"] = accent
        if disabled:
            internal_kwargs["state"] = "disabled"
        internal_kwargs.update(kwargs)

        self._internal = _InternalRadioGroup(tk_master, **internal_kwargs)

        # Populate options passed at construction.
        if options:
            for opt in options:
                if isinstance(opt, str):
                    self._internal.add(text=opt, value=opt)
                else:
                    lbl, val = opt
                    self._internal.add(text=lbl, value=val)

        # Trace the signal so <<Change>> fires on the internal Frame whenever
        # the value changes — this lets on_change() use standard Subscription binding.
        def _on_value_change(_new_value: Any) -> None:
            try:
                self._internal.event_generate("<<Change>>")
            except tkinter.TclError:
                pass

        self._trace_id = self._internal.signal.subscribe(_on_value_change)
        self._attach_to_parent(layout_kw)

    # ----- Properties -----

    @property
    def value(self) -> Any:
        """The currently selected value, or ``None`` if nothing is selected."""
        return self._internal.value

    @value.setter
    def value(self, v: Any) -> None:
        self._internal.value = v

    @property
    def disabled(self) -> bool:
        """Whether all buttons in the group are non-interactive."""
        return self._internal._state == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    # ----- Methods -----

    def add(self, label: str, value: Any | None = None, **kwargs: Any) -> None:
        """Add a radio button to the group at runtime.

        Args:
            label: Display text for the button.
            value: Value assigned when this button is selected. Defaults to `label`.
        """
        self._internal.add(text=label, value=value if value is not None else label, **kwargs)

    def remove(self, value: Any) -> None:
        """Remove the button identified by `value`."""
        self._internal.remove(str(value))

    # ----- Event shorthands -----

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired whenever the selection changes.

        The current value is available via ``group.value`` inside the handler.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("change", handler)


register_widget_events(RadioGroup, _RADIOGROUP_EVENTS)
