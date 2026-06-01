from __future__ import annotations

import tkinter
from typing import overload, Any, Callable, Literal

from bootstack.widgets._impl.composites.togglegroup import ToggleGroup as _InternalToggleGroup
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._core.subscription import Subscription
from bootstack.widgets._core.stream import Stream
from bootstack.widgets.types import AccentToken, Event, VariantToken, Orient

_TOGGLEGROUP_EVENTS: dict[str, str] = {
    "change": "<<Change>>",
}


class ToggleGroup(PublicWidgetBase):
    """A group of toggle buttons — single-select or multi-select.

    Options are supplied at construction via ``options=`` and can be added
    at runtime with ``add()``. In ``'single'`` mode exactly one button is
    active at a time; in ``'multi'`` mode any combination can be active.

    Args:
        options: Choices for the group. Each item is either a plain string
            (label and value are the same) or a ``(label, value)`` tuple,
            e.g. ``["Grid", "List"]`` or
            ``[("Grid view", "grid"), ("List view", "list")]``.
        mode: Selection behaviour. ``'single'`` (default) enforces mutual
            exclusivity like a radio group; ``'multi'`` allows any number
            of buttons to be active simultaneously.
        signal: Reactive ``Signal`` holding the selected value(s). In
            ``'single'`` mode the signal value is a ``str``; in ``'multi'``
            mode it is a ``set[str]``. When provided, ``value=`` is ignored
            — seed the Signal directly.
        value: Initial selection. A ``str`` for ``'single'`` mode or a
            ``set[str]`` for ``'multi'`` mode. Ignored when ``signal=`` is
            passed.
        orient: Layout direction. ``'horizontal'`` (default) or
            ``'vertical'``.
        accent: Accent token applied to all buttons. One of ``'primary'``,
            ``'secondary'``, ``'info'``, ``'success'``, ``'warning'``,
            ``'danger'``, ``'default'``.
        variant: Style variant. ``'solid'`` (default), ``'outline'``, or
            ``'ghost'``.
        disabled: If ``True``, all buttons are non-interactive and dimmed.
            Defaults to ``False``.
        parent: Explicit parent widget. If omitted, the current
            context-stack container is used.
    """

    def __init__(
        self,
        options: list[str | tuple[str, Any]] | None = None,
        *,
        mode: Literal["single", "multi"] = "single",
        signal: Any = None,
        value: Any = None,
        orient: Orient = "horizontal",
        accent: AccentToken | str | None = None,
        variant: VariantToken | str | None = None,
        disabled: bool = False,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "mode": mode,
            "orient": orient,
        }
        if signal is not None:
            internal_kwargs["signal"] = signal
        if value is not None:
            internal_kwargs["value"] = value
        if accent is not None:
            internal_kwargs["accent"] = accent
        if variant is not None:
            internal_kwargs["variant"] = variant
        if disabled:
            internal_kwargs["state"] = "disabled"
        internal_kwargs.update(kwargs)

        self._internal = _InternalToggleGroup(tk_master, **internal_kwargs)

        # Populate options passed at construction.
        if options:
            for opt in options:
                if isinstance(opt, str):
                    self._internal.add(text=opt, value=opt)
                else:
                    lbl, val = opt
                    self._internal.add(text=lbl, value=val)

        # Trace signal → <<Change>> for consistent Subscription-based on_change().
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
        """The current selection. A ``str`` in single mode, ``set[str]`` in multi mode."""
        return self._internal.get()

    @value.setter
    def value(self, v: Any) -> None:
        self._internal.set(v)

    @property
    def disabled(self) -> bool:
        """Whether all buttons in the group are non-interactive."""
        return self._internal._state == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    # ----- Methods -----

    def add(self, label: str, value: Any | None = None, **kwargs: Any) -> None:
        """Add a toggle button at runtime.

        Args:
            label: Display text.
            value: Value this button represents. Defaults to `label`.
        """
        self._internal.add(text=label, value=value if value is not None else label, **kwargs)

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


register_widget_events(ToggleGroup, _TOGGLEGROUP_EVENTS)
