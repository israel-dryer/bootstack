from __future__ import annotations

import tkinter
from typing import overload, Any, Callable, Literal, TYPE_CHECKING

from bootstack.widgets._impl.composites.togglegroup import ToggleGroup as _InternalToggleGroup
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.selection_group import SelectionGroupMixin
from bootstack.widgets._core.options import normalize_options
from bootstack.widgets._core.events import register_widget_events
from bootstack.events import Subscription, ChangeEvent
from bootstack.streams import Stream
from bootstack.widgets.types import AccentToken, Event, Option, Orient, ButtonVariant

if TYPE_CHECKING:
    from bootstack.signals import Signal

_TOGGLEGROUP_EVENTS: dict[str, str] = {
    "change": "<<Change>>",
}


class ToggleGroup(SelectionGroupMixin, PublicWidgetBase):
    """A group of toggle buttons — single-select or multi-select.

    Options are supplied at construction via `options=` and can be added
    at runtime with `add()`. In `'single'` mode exactly one button is
    active at a time; in `'multi'` mode any combination can be active.

    Args:
        options: Choices for the group. Each item is a plain string (text and
            value are the same), a `(text, value)` tuple, or a
            `{'text': ..., 'value': ...}` dict — e.g. `["Grid", "List"]` or
            `[("Grid view", "grid"), ("List view", "list")]`.
        mode: Selection behavior. `'single'` (default) enforces mutual
            exclusivity like a radio group; `'multi'` allows any number
            of buttons to be active simultaneously.
        signal: Reactive `Signal` holding the selected value(s). In
            `'single'` mode the signal value is a `str`; in `'multi'`
            mode it is a `set[str]`. When provided, `value=` is ignored
            — seed the Signal directly.
        value: Initial selection. A `str` for `'single'` mode or a
            `set[str]` for `'multi'` mode. Ignored when `signal=` is
            passed.
        orient: Layout direction. Default `'horizontal'`.
        accent: Accent token applied to all buttons.
        variant: Button style variant. Default `'solid'`.
        disabled: If `True`, all buttons are non-interactive and dimmed.
            Defaults to `False`.
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
        mode: Literal["single", "multi"] = "single",
        signal: "Signal | None" = None,
        value: Any = None,
        orient: Orient = "horizontal",
        accent: AccentToken | str | None = None,
        variant: ButtonVariant = "default",
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

        self._internal = _InternalToggleGroup(tk_master, **internal_kwargs)

        # Populate options passed at construction; keep the records (the data
        # bag) so `selection` can return each option's full dict.
        records = normalize_options(options)
        self._set_option_records(records)
        for record in records:
            self._internal.add(text=record.text, value=record.value)

        # Trace signal → <<Change>> for consistent Subscription-based on_change().
        self._prev_value = self._internal.signal()

        def _on_value_change(new_value: Any) -> None:
            try:
                prev, self._prev_value = self._prev_value, new_value
                self._internal.event_generate(
                    "<<Change>>", data=ChangeEvent(value=new_value, prev_value=prev)
                )
            except tkinter.TclError:
                pass

        self._trace_id = self._internal.signal.subscribe(_on_value_change)
        self._attach_to_parent(layout_kw)

    # ----- Properties -----

    @property
    def value(self) -> Any:
        """The current selection. A `str` in single mode, `set[str]` in multi mode."""
        return self._internal.get()

    @value.setter
    def value(self, v: Any) -> None:
        self._internal.set(v)

    @property
    def text(self) -> str | set[str] | None:
        """The label(s) of the selected option(s) — the display complement of `value`.

        In single mode, the selected option's label (or `None` if nothing is
        selected). In multi mode, a `set` of the selected options' labels.
        Read-only.
        """
        value = self._internal.get()
        if isinstance(value, set):
            return {t for v in value if (t := self._internal.text_for(v)) is not None}
        return self._internal.text_for(value)

    @property
    def selection(self) -> dict | list[dict] | None:
        """The selected option(s) as full record dicts — the data bag.

        In single mode, the selected option's `{text, value, ...extras}` dict
        (or `None`). In multi mode, a `list` of those dicts. Read-only.
        """
        value = self._internal.get()
        if isinstance(value, set):
            return [d for v in value if (d := self._record_dict_for(v)) is not None]
        return self._record_dict_for(value)

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
        resolved = value if value is not None else label
        self._internal.add(text=label, value=resolved, **kwargs)
        self._add_option_record(label, resolved)

    # ----- Event shorthands -----

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[ChangeEvent], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[ChangeEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired whenever the selection changes.

        Args:
            handler: Called with a :class:`~bootstack.events.ChangeEvent`; the
                current value is also available via `group.value`. Omit to get
                a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("change", handler)


register_widget_events(ToggleGroup, _TOGGLEGROUP_EVENTS)
