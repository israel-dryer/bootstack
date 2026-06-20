from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Mapping, Sequence, overload

from bootstack.constants import DEFAULT_MIN_COL_WIDTH
from bootstack.widgets._impl.composites.form import Form as _InternalForm
from bootstack.widgets._impl.composites.form import (
    FormItem, FieldItem, GroupItem, TabsItem, TabItem,
)
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.streams import Stream
from bootstack.events import Subscription
from bootstack.signals import Signal
from bootstack.widgets.types import AccentToken

if TYPE_CHECKING:
    from bootstack.dialogs import DialogButton


class Form(PublicWidgetBase):
    """Data-entry form built from data or explicit field definitions.

    Args:
        data: Initial data dict. Keys become field names; types are inferred
            when `items` is not provided.
        items: Explicit form layout as `FieldItem`/`GroupItem`/`TabsItem`
            instances or equivalent dicts.
        col_count: Number of top-level columns. Default `1`.
        min_col_width: Minimum column width in pixels.
        on_data_change: Callback invoked with the updated data dict on each
            field change. Equivalent to calling `on_data_change()` after
            construction.
        width: Fixed form width in pixels.
        height: Fixed form height in pixels.
        accent: Accent token for the form container.
        buttons: Footer buttons — strings, `DialogButton` instances, or dicts.
        parent: Override the context-stack parent.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        *,
        data: dict[str, Any] | None = None,
        items: Sequence[FormItem | Mapping[str, Any]] | None = None,
        col_count: int = 1,
        min_col_width: int = DEFAULT_MIN_COL_WIDTH,
        on_data_change: Callable[[dict[str, Any]], Any] | None = None,
        width: int | None = None,
        height: int | None = None,
        accent: AccentToken | str | None = None,
        buttons: Sequence[str | DialogButton | dict[str, Any]] | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        kw: dict[str, Any] = {"col_count": col_count, "min_col_width": min_col_width}
        if data is not None:
            kw["data"] = data
        if items is not None:
            kw["items"] = items
        if on_data_change is not None:
            kw["on_data_change"] = on_data_change
        if width is not None:
            kw["width"] = width
        if height is not None:
            kw["height"] = height
        if accent is not None:
            kw["accent"] = accent
        if buttons is not None:
            kw["buttons"] = buttons

        self._internal = _InternalForm(tk_master, **kw)
        self._attach_to_parent(layout_kw)

    # ----- Value API -----

    @property
    def value(self) -> dict[str, Any]:
        """All field values as a dictionary."""
        return self._internal.value

    @value.setter
    def value(self, values: Mapping[str, Any]) -> None:
        self._internal.value = values

    @property
    def data(self) -> dict[str, Any]:
        """Current form data dict."""
        return self._internal.data

    @property
    def result(self) -> Any:
        """Value set by button commands. None until a button is pressed."""
        return self._internal.result

    def get(self) -> dict[str, Any]:
        """Return all field values as a dictionary."""
        return self._internal.get()

    def set(self, values: Mapping[str, Any]) -> None:
        """Set multiple field values from a dictionary."""
        self._internal.set(values)

    def validate(self) -> bool:
        """Run validation rules; returns True if all fields pass."""
        return self._internal.validate()

    @property
    def valid(self) -> Signal:
        """Reactive `Signal[bool]` — `True` when every field passes validation.

        AND-ed over the fields' own `valid` signals and recomputed whenever any
        field's validity changes, so a submit button can react to it directly::

            form = bs.Form(items=[...])
            submit = bs.Button("Save", on_click=save)

            def gate(ok):
                submit.disabled = not ok

            form.valid.subscribe(gate)

        A field is valid until proven otherwise, so this reads `True` before any
        rule has run — call `validate()` to force a full pass (for example, to
        gate the submit button's initial state).
        """
        return self._internal.valid

    @property
    def errors(self) -> dict[str, str]:
        """Current validation errors keyed by field key; empty when all valid.

        Read live from the fields' `error` signals, so it always reflects the
        latest validation run.
        """
        return self._internal.errors

    # ----- Field access -----

    def field(self, key: str) -> Any:
        """Return the Field widget for the given key."""
        return self._internal.field(key)

    def fields(self) -> tuple:
        """Return all field widgets in insertion order."""
        return self._internal.fields()

    def keys(self) -> tuple[str, ...]:
        """Return all field keys in insertion order."""
        return self._internal.keys()

    def get_field_value(self, key: str) -> Any:
        """Return the current value of the named field."""
        return self._internal.get_field_value(key)

    def set_field_value(self, key: str, value: Any) -> None:
        """Set the value of the named field."""
        self._internal.set_field_value(key, value)

    # ----- Signal access -----

    def field_signal(self, key: str) -> Any:
        """Return the Signal for the named field value."""
        return self._internal.field_signal(key)

    def field_textsignal(self, key: str) -> Any:
        """Return the text Signal for the named field."""
        return self._internal.field_textsignal(key)

    # ----- Events -----

    @overload
    def on_data_change(self) -> Stream: ...
    @overload
    def on_data_change(self, handler: Callable[[dict[str, Any]], Any]) -> Subscription: ...
    def on_data_change(self, handler: Callable[[dict[str, Any]], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired whenever any field value changes.

        The handler receives the current form data as a dict. Called with no
        handler, returns a composable `Stream`.

        Args:
            handler: Called with the updated data dict on each field change.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        if handler is None:
            return self.on("data_change")
        return self.on("data_change", lambda _e: handler(self.value))


register_widget_events(Form, {"data_change": "<<BsDataChange>>"})
