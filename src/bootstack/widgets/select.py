from __future__ import annotations

import tkinter
from typing import overload, Any, Callable, Literal, TYPE_CHECKING

from bootstack.widgets._impl.composites.selectbox import SelectBox as _InternalSelectBox
from bootstack.widgets._core.base import PublicWidgetBase, adapt_handler
from bootstack.widgets._core.events import resolve_event, register_widget_events
from bootstack.widgets._core.options import record_to_dict
from bootstack.events import ChangeEvent, Subscription
from bootstack.streams import Stream
from bootstack.widgets.textfield import _INNER_ENTRY_SEQUENCES
from bootstack.widgets.types import AccentToken, Event, Option, OptionDict, WidgetDensity

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
        options: Choices presented in the popup. Each item is a plain string,
            a `(text, value)` tuple, or a `{'text': ..., 'value': ...}` dict —
            so an option's displayed label can differ from its stored value.
            A dict option may also carry `'icon'` (a glyph rendered beside the
            row label) and `'disabled'` (when `True` the row is dimmed and
            cannot be chosen); any other keys ride along as carried data on
            `selection`. Defaults to an empty list.
        value: Initially selected value (value-space — matches an option's
            value, not its label).
        signal: Reactive `Signal` two-way bound to the field's displayed text.
            With decoupled options (text differs from value), bind to the value
            via `on_change`/`value`; the signal carries the display text.
        label: Label displayed above the field.
        message: Hint or helper text displayed below the field.
        required: If `True`, marks the field as required and prevents
            empty submission.
        searchable: If `True`, typing in the field filters the option
            list. Defaults to `False`.
        allow_custom_values: If `True`, users may type values not in
            `options`. Defaults to `False`.
        group_by: Name of an option field to cluster the popup rows under
            non-selectable group headers (e.g. `'category'`). The field is read
            from each option's flat record, so it may be any carried bag key (or
            `'text'`/`'value'`). Groups appear in first-appearance order; an
            option missing the field renders headerless. Grouping is
            presentational only — `value`/`selection` are unaffected. `None`
            (default) renders a flat list.
        max_visible_items: Approximate number of option rows the popup shows
            before it scrolls (height is `max_visible_items * row_height`).
            Group headers and separators consume some of that budget, so the
            count is approximate. `None` (default) uses the built-in cap.
        read_only: If `True`, value is visible but the popup cannot be
            opened.
        disabled: If `True`, field is fully non-interactive and dimmed.
        width: Width in character units.
        accent: Accent token applied to the focus ring.
        density: Padding density.
        localize: Whether option labels (in the popup and the selected label
            shown in the field) are translated through the catalog — `True`,
            `False`, or `'auto'` (translate when a translation is registered,
            otherwise show the literal). Defaults to the app's `localize_mode`.
            Set `False` to keep proper nouns untranslated; override a single
            option with its `localize` key. When searching is enabled, search
            matches the displayed (translated) labels.
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
        label: str | None = None,
        message: str | None = None,
        required: bool = False,
        searchable: bool = False,
        allow_custom_values: bool = False,
        group_by: str | None = None,
        max_visible_items: int | None = None,
        read_only: bool = False,
        disabled: bool = False,
        width: int | None = None,
        accent: AccentToken | str | None = None,
        density: WidgetDensity | None = None,
        localize: bool | Literal['auto'] | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "items":               options or [],
            "enable_search":       searchable,
            "allow_custom_values": allow_custom_values,
            "group_by":            group_by,
            "max_visible_items":   max_visible_items,
            # Public Select rejects an unknown value (unless custom values are
            # allowed); internal/embedded SelectBoxes stay lenient.
            "strict_value":        not allow_custom_values,
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
        if localize is not None:
            internal_kwargs["localize"] = localize

        self._internal = _InternalSelectBox(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Validation -----

    def add_validation_rule(
        self,
        rule: str,
        message: str | None = None,
        trigger: str = "change",
        **kwargs: Any,
    ) -> None:
        """Add a validation rule to the field.

        Args:
            rule: Validation rule name (e.g. ``'required'``).
            message: Custom error message shown when the rule fails.
            trigger: When to evaluate the rule (e.g. ``'blur'``, ``'change'``).
            **kwargs: Extra rule-specific options.
        """
        self._internal.add_validation_rule(rule, message=message, trigger=trigger, **kwargs)

    # ----- Event routing -----

    def _entry_widget(self) -> tkinter.Misc:
        return self._internal._entry

    @overload
    def on(self, event: str) -> Stream: ...
    @overload
    def on(self, event: str, handler: Callable[[Event], Any]) -> Subscription: ...
    def on(self, event: str, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback for an event by name.

        A generic, string-keyed escape hatch — prefer the typed `on_*`
        shorthands (e.g. `on_change`), which carry the precise payload type.
        Called with no handler, returns a composable `Stream`; with a handler,
        binds it and returns a `Subscription`.

        Args:
            event: Event name (for example `'change'` or `'focus'`).
            handler: Called with the event payload. Omit to get a composable
                :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        sequence = resolve_event(self, str(event))
        target = self._entry_widget() if sequence in _INNER_ENTRY_SEQUENCES else self._internal
        if handler is None:
            def _source(h):
                t = self._entry_widget() if sequence in _INNER_ENTRY_SEQUENCES else self._internal
                bid = t.bind(sequence, adapt_handler(h), add="+")
                return Subscription(t, sequence, bid)
            return Stream(self._internal, _source=_source)
        bid = target.bind(sequence, adapt_handler(handler), add="+")
        return Subscription(target, sequence, bid)

    # ----- Properties -----

    @property
    def value(self) -> Any:
        """The currently selected value, or `None` if unselected.

        This is the option's *value* (value-space). For the displayed label, see
        `text`.
        """
        return self._internal.value

    @value.setter
    def value(self, v: Any) -> None:
        self._internal.value = v

    @property
    def text(self) -> str:
        """The label currently shown in the field — the selected option's text.

        Read-only; the complement of `value` (the selection's value). Assign to
        `value` to change the selection.
        """
        return self._internal.text

    @property
    def selection(self) -> dict | None:
        """The selected option as a full record dict — the data bag — or `None`.

        `{'text': ..., 'value': ..., ...any extra keys}`, indexed by key like
        any record. `None` when nothing is selected or the value is a custom
        off-list one. Read-only.
        """
        return self._internal.selection

    @property
    def options(self) -> list[OptionDict]:
        """The available options as normalized `{'text', 'value'}` records.

        Assigning a new list rebuilds the popup. Accepts the same `Option`
        forms as the constructor (strings, `(text, value)` tuples, or dicts).
        """
        return [record_to_dict(r) for r in self._internal.cget("items")]

    @options.setter
    def options(self, items: list[Option]) -> None:
        self._internal.configure(items=list(items))

    @property
    def group_by(self) -> str | None:
        """Name of the option field the popup clusters rows under, or `None`.

        Assigning a field name groups the popup the next time it opens; assign
        `None` to render a flat list. Grouping is presentational only — it does
        not affect `value`, `selection`, or `options`.
        """
        return self._internal.cget("group_by")

    @group_by.setter
    def group_by(self, field: str | None) -> None:
        self._internal.configure(group_by=field or "")

    @property
    def max_visible_items(self) -> int | None:
        """Approximate option-row cap before the popup scrolls, or `None`.

        Assigning takes effect the next time the popup opens; assign `None` to
        restore the built-in cap. Height is `max_visible_items * row_height`,
        so group headers and separators make the count approximate.
        """
        return self._internal.cget("max_visible_items")

    @max_visible_items.setter
    def max_visible_items(self, n: int | None) -> None:
        self._internal.configure(max_visible_items=n or 0)

    @property
    def selected_index(self) -> int:
        """Zero-based index of the selected option, or `-1` if none selected."""
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
    def on_change(self, handler: Callable[[ChangeEvent], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[ChangeEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the selection changes.

        Args:
            handler: Called with a :class:`~bootstack.events.ChangeEvent`. Omit
                to get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("change", handler)


register_widget_events(Select, _SELECT_EVENTS)
