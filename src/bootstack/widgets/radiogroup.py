from __future__ import annotations

import tkinter
from typing import overload, Any, Callable, TYPE_CHECKING

from bootstack.widgets._impl.composites.radiogroup import RadioGroup as _InternalRadioGroup
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.selection_group import SelectionGroupMixin
from bootstack.widgets._core.options import normalize_options, option_display
from bootstack.widgets._core.events import register_widget_events
from bootstack.events import Subscription, ChangeEvent
from bootstack.streams import Stream
from bootstack.widgets.types import AccentToken, Event, Option, Orient

if TYPE_CHECKING:
    from bootstack.signals import Signal

_RADIOGROUP_EVENTS: dict[str, str] = {
    "change": "<<Change>>",
}


class RadioGroup(SelectionGroupMixin, PublicWidgetBase):
    """A group of mutually exclusive radio buttons.

    Exactly one option can be selected at a time. Options are supplied at
    construction via `options=` and can be added or removed at runtime
    using `add()` and `remove()`.

    Args:
        options: Choices for the group. Each item is a plain string (text and
            value are the same), a `(text, value)` tuple, or a
            `{'text': ..., 'value': ...}` dict — e.g. `["S", "M", "L"]` or
            `[("Small", "s"), ("Medium", "m"), ("Large", "l")]`. A dict option
            may also carry `'icon'` (a glyph rendered beside the label) and
            `'disabled'` (when `True` the option is dimmed and cannot be
            selected); any other keys ride along as carried data on `selection`.
            An option with an `'icon'` and no text — e.g.
            `{'icon': 'star', 'value': 's'}` — renders as an icon-only button.
        signal: Reactive `Signal` holding the selected value. When
            provided, `value=` is ignored — seed the Signal directly.
        value: Initially selected value. Ignored when `signal=` is passed.
        orient: Layout direction. Default `'horizontal'`.
        title: Optional label rendered above the button group.
        accent: Accent token applied to all buttons.
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
        signal: "Signal | None" = None,
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

        self._internal = _InternalRadioGroup(tk_master, **internal_kwargs)

        # Populate options passed at construction; keep the records (the data
        # bag) so `selection` can return each option's full dict.
        records = normalize_options(options)
        self._set_option_records(records)
        for record in records:
            icon, disabled = option_display(record)
            add_kwargs, _ = self._option_render(icon, disabled, record.text)
            self._internal.add(text=record.text, value=record.value, **add_kwargs)

        # Trace the signal so <<Change>> fires on the internal Frame whenever
        # the value changes — this lets on_change() use standard Subscription binding.
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
        """The currently selected value, or `None` if nothing is selected."""
        return self._internal.value

    @value.setter
    def value(self, v: Any) -> None:
        self._internal.value = v

    @property
    def text(self) -> str | None:
        """The label of the selected option, or `None` if nothing is selected.

        Read-only; the display complement of `value` (the selection's value).
        """
        return self._internal.text_for(self._internal.value)

    @property
    def selection(self) -> dict | None:
        """The selected option as a full record dict — the data bag — or `None`.

        `{'text': ..., 'value': ..., ...any extra keys}`, indexed by key like any
        record. Read-only.
        """
        return self._record_dict_for(self._internal.value)

    @property
    def disabled(self) -> bool:
        """Whether all buttons in the group are non-interactive."""
        return self._internal._state == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    @property
    def title(self) -> str | None:
        """The label rendered above the group. Assigning to it updates it live.

        Set to `None` (or `''`) to remove the label entirely.
        """
        return self._internal.cget("text") or None

    @title.setter
    def title(self, value: str | None) -> None:
        self._internal.configure(text=value or "")

    # ----- Methods -----

    def add(
        self,
        label: str,
        value: Any | None = None,
        *,
        icon: Any = None,
        disabled: bool = False,
        **kwargs: Any,
    ) -> None:
        """Add a radio button to the group at runtime.

        Args:
            label: Display text for the button. Pass `''` with an `icon` for an
                icon-only button.
            value: Value assigned when this button is selected. Defaults to `label`.
            icon: Optional icon spec rendered beside the label (alone when
                `label` is blank).
            disabled: If `True`, the option is dimmed and cannot be selected.
        """
        resolved = value if value is not None else label
        add_kwargs, extras = self._option_render(icon, disabled, label)
        self._internal.add(text=label, value=resolved, **add_kwargs, **kwargs)
        self._add_option_record(label, resolved, extras)

    # ----- Event shorthands -----

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[ChangeEvent], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[ChangeEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired whenever the selection changes.

        Args:
            handler: Called with a :class:`~bootstack.events.ChangeEvent`; the
                selected value is also available via `group.value`. Omit to get
                a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("change", handler)


register_widget_events(RadioGroup, _RADIOGROUP_EVENTS)
