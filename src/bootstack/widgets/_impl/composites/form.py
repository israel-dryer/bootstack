"""Dynamic form widget for building data entry layouts quickly."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from tkinter import Variable
from typing import Any, Callable, Iterable, Literal, Mapping, Sequence, TYPE_CHECKING

from bootstack.constants import DEFAULT_MIN_COL_WIDTH
from bootstack.signals import Signal
from bootstack.widgets._impl.primitives.button import Button
from bootstack.widgets._impl.primitives.frame import Frame
from bootstack.widgets._impl.primitives.label import Label
from bootstack.widgets._impl.primitives.labelframe import LabelFrame
from bootstack.widgets._impl.mixins import configure_delegate
from bootstack.widgets._impl.composites.tabs.tabview import TabView
from bootstack.widgets._core.kwargs import merge_kwargs
from bootstack.widgets.types import EditorType, Master

# Structural keys an editor_options bag may not set — the form's field
# container owns where the editor is placed.
_RESERVED_EDITOR_OPTIONS = {
    'parent': 'the form places each editor in its own field container',
}

if TYPE_CHECKING:
    from bootstack.dialogs._impl.dialog import DialogButton
    ButtonInput = str | Mapping[str, Any] | DialogButton

DType = Literal['int', 'float', 'bool', 'date', 'datetime', 'password', 'str'] | type | None


@dataclass
class FieldItem:
    """A single field in a `Form`, addressed by its `key`."""

    key: str
    """Unique field identifier — used to read and write the field value."""
    label: str | None = None
    """Display label shown above the field. Defaults to the capitalized `key`."""
    dtype: DType = None
    """Type hint controlling the default editor — `'str'`, `'int'`, `'float'`,
    `'bool'`, `'date'`, `'datetime'`, or `'password'`. `None` infers the type from
    the initial value."""
    readonly: bool = False
    """Render the field read-only. Default `False`."""
    required: bool = False
    """Mark the field as required — adds a `'required'` validation rule and appends
    an asterisk to the label. Honored by the text, number, password, date, select,
    textarea, and spinner editors; has no effect on boolean or slider editors.
    Default `False`."""
    visible: bool = True
    """Show the field. Set `False` to hide it. Default `True`."""
    column: int | None = None
    """Zero-based grid column. Auto-placed when `None`."""
    row: int | None = None
    """Zero-based grid row. Auto-placed when `None`."""
    columnspan: int = 1
    """Number of grid columns to span. Default `1`."""
    rowspan: int = 1
    """Number of grid rows to span. Default `1`."""
    editor: EditorType | None = None
    """Force a specific editor widget (see `EditorType`). `None` infers it from
    `dtype`."""
    editor_options: dict[str, Any] = field(default_factory=dict)
    """Keyword arguments for the editor widget, using its public `bs.*` parameter
    names — e.g. `{"step": 10}` for a `numberfield`, `{"show_border": True}` for a
    `textarea`, `{"mask": "*"}` for a `textfield`. For `'select'`, pass the choices
    as `{"values": ["A", "B", "C"]}` (or `{"items": [...]}`); add
    `{"allow_custom_values": True}` for an editable combobox."""
    type: Literal['field'] = "field"
    """Item-type discriminator. Set automatically; only needed when building items
    as plain dicts."""


@dataclass
class GroupItem:
    """A labeled group of fields with its own column layout, placed in a `Form`."""

    items: list[FieldItem | Mapping[str, Any] | GroupItem | TabsItem] = field(default_factory=list)
    """Child `FieldItem`, `GroupItem`, or `TabsItem` instances (or equivalent dicts)."""
    label: str | None = None
    """Section heading shown above the group border. No border is drawn when `None`."""
    col_count: int = 1
    """Number of columns within the group. Default `1`."""
    min_col_width: int = DEFAULT_MIN_COL_WIDTH
    """Minimum column width in pixels."""
    width: int | None = None
    """Fixed width for the group container."""
    height: int | None = None
    """Fixed height for the group container."""
    column: int | None = None
    """Zero-based grid column in the parent form. Auto-placed when `None`."""
    row: int | None = None
    """Zero-based grid row in the parent form. Auto-placed when `None`."""
    columnspan: int = 1
    """Columns to span in the parent grid. Default `1`."""
    rowspan: int = 1
    """Rows to span in the parent grid. Default `1`."""
    padding: int | str | tuple[int, int] | tuple[int, int, int, int] | None = 8
    """Internal padding inside the group border. Default `8`."""
    type: Literal['group'] = "group"
    """Item-type discriminator. Set automatically; only needed when building items
    as plain dicts."""


@dataclass
class TabItem:
    """A single tab within a `TabsItem`."""

    label: str
    """Tab button label."""
    items: list[FieldItem | Mapping[str, Any] | GroupItem | TabsItem] = field(default_factory=list)
    """`FieldItem`, `GroupItem`, or `TabsItem` instances for this tab's content."""
    padding: int | str | tuple[int, int] | tuple[int, int, int, int] | None = 8
    """Internal padding inside the tab body. Default `8`."""


@dataclass
class TabsItem:
    """A tab container holding one or more `TabItem` entries, placed in a `Form`."""

    tabs: list[TabItem | Mapping[str, Any]] = field(default_factory=list)
    """`TabItem` instances (or equivalent dicts) defining each tab."""
    label: str | None = None
    """Optional heading shown above the tab bar."""
    width: int | None = None
    """Fixed width for the tab container."""
    height: int | None = None
    """Fixed height for the tab container."""
    column: int | None = None
    """Zero-based grid column in the parent form. Auto-placed when `None`."""
    row: int | None = None
    """Zero-based grid row in the parent form. Auto-placed when `None`."""
    columnspan: int = 1
    """Columns to span in the parent grid. Default `1`."""
    rowspan: int = 1
    """Rows to span in the parent grid. Default `1`."""
    type: Literal['tabs'] = "tabs"
    """Item-type discriminator. Set automatically; only needed when building items
    as plain dicts."""


FormItem = FieldItem | GroupItem | TabsItem


class Form(Frame):
    """A configurable form that can be generated from data or explicit items.

    Form is a *field manager* that provides a domain-specific API for accessing
    and manipulating form fields and their values.

    Field Access:
        - `field(key)` — returns the field widget for a key
        - `fields()` — returns all field widgets in order
        - `keys()` — returns all field keys in order

    Value Operations:
        - `get_field_value(key)` — get a single field's value
        - `set_field_value(key, value)` — set a single field's value
        - `get()` / `set(values)` — get/set all values as a dict
        - `value` property — get/set all values as a dict

    Variable & Signal Access:
        - `field_variable(key)` — get Tk Variable for a field
        - `field_signal(key)` — get Signal for a field's value
        - `field_textsignal(key)` — get Signal for a field's text

    Attributes:
        result: Result value set by button commands. None until a button with a
            `result` or `command` is pressed.

    Args:
        master: Parent widget.
        data: Initial data backing the form. If items are not provided,
            field items are inferred from the keys and value types.
        items: Optional explicit form definition. Accepts dictionaries that
            match the FieldItem/GroupItem/TabsItem shapes or the dataclass
            instances directly.
        col_count: Number of columns at the top level.
        min_col_width: Minimum width for each column in pixels.
        on_data_change: Optional callback invoked with the updated data dict
            whenever a field value changes.
        width: Requested width for the form container.
        height: Requested height for the form container.
        accent: Accent token for the form container (e.g., 'primary', 'secondary').
        buttons: Optional footer buttons. Accepts plain strings, DialogButton
            instances, or dictionaries that map to DialogButton kwargs.
        **kwargs: Additional Frame configuration options.
    """

    def __init__(
            self,
            master: Master = None,
            *,
            data: dict[str, Any] | None = None,
            items: Sequence[FormItem | Mapping[str, Any]] | None = None,
            col_count: int = 1,
            min_col_width: int = DEFAULT_MIN_COL_WIDTH,
            on_data_change: Callable[[dict[str, Any]], Any] | None = None,
            width: int | None = None,
            height: int | None = None,
            accent: str | None = None,
            buttons: Sequence[ButtonInput] | None = None,
            **kwargs: Any,
    ) -> None:
        """Build a configurable form from data or explicit items.

        Args:
            master: Parent widget.
            data: Initial data backing the form; keys become field names.
            items: Explicit form layout (FieldItem/GroupItem/TabsItem or mappings).
            col_count: Number of columns at the top level.
            min_col_width: Minimum width per column in pixels.
            on_data_change: Callback invoked with updated data when a field changes.
            width: Requested form width; if None, size naturally.
            height: Requested form height; if None, size naturally.
            accent: Accent token for the form container.
            buttons: Optional footer buttons (DialogButton, mapping, or string).
            **kwargs: Additional Frame configuration options.
        """
        super().__init__(master=master, width=width, height=height, accent=accent, **kwargs)

        self._data: dict[str, Any] = dict(data) if data else {}
        self.result: Any = None
        self._on_data_change = on_data_change
        self._col_count = col_count
        self._min_col_width = min_col_width
        self._widgets: dict[str, Any] = {}
        self._variables: dict[str, Variable] = {}
        self._signals: dict[str, Any] = {}
        self._textsignals: dict[str, Any] = {}
        self._items_by_key: dict[str, FieldItem] = {}
        self._suspend_sync = False

        normalized_items = self._normalize_items(items or self._infer_items_from_data(self._data))

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        container = Frame(self)
        container.grid(row=0, column=0, sticky='nsew')
        self._content_frame = Frame(container)
        self._content_frame.pack(fill='both', expand=True)

        # Respect explicit width/height by preventing geometry propagation.
        if width or height:
            if width:
                self.configure(width=width)
                container.configure(width=width)
            if height:
                self.configure(height=height)
                container.configure(height=height)
            self.grid_propagate(False)
            self.pack_propagate(False)
            container.grid_propagate(False)

        self._build_items(
            self._content_frame, normalized_items, col_count=self._col_count, min_col_width=self._min_col_width)

        if buttons:
            footer = Frame(self)
            footer.grid(row=1, column=0, sticky='ew', pady=(8, 0))
            footer.columnconfigure(0, weight=1)
            self._build_buttons(footer, buttons)

        # Reactive form-level validity aggregate. AND of the member fields'
        # `valid` signals; recomputed whenever any field's validity changes.
        self._valid_signal: Signal = Signal(True)
        self._validity_entries: list[Any] = []
        self._register_validity_aggregate()

    @property
    def data(self) -> dict[str, Any]:
        """Current data backing the form."""
        return dict(self._collect_data())

    @property
    def valid(self) -> Signal:
        """Reactive `Signal[bool]` — True when every field passes validation.

        AND-ed over the member fields' reactive `valid` signals and recomputed
        whenever any field's validity changes (a blur, a key for key-triggered
        rules, or a manual validate). A field is valid until proven otherwise,
        so this reads `True` before any rule has run — call `validate()` to force
        a full pass (for example, to gate a submit button's initial state).
        """
        return self._valid_signal

    @property
    def errors(self) -> dict[str, str]:
        """Current validation errors keyed by field key; empty when all valid.

        Read live from the fields' reactive `error` signals, so it always
        reflects the latest validation run.
        """
        out: dict[str, str] = {}
        for key, widget in self._widgets.items():
            entry = self._validity_entry(widget)
            if entry is not None and not entry._valid_signal():
                out[key] = entry._error_signal()
        return out

    @staticmethod
    def _validity_entry(widget: Any) -> Any | None:
        """Return a field's validation-bearing entry, or None if it has none.

        Resolves through a public wrapper's internal widget: a field editor's
        internal `Field` exposes the validity signals on its `_entry`, while the
        text-area composite carries them directly.
        """
        internal = getattr(widget, "_internal", widget)
        entry = getattr(internal, "_entry", None)
        if entry is not None and hasattr(entry, "_valid_signal"):
            return entry
        if hasattr(internal, "_valid_signal"):
            return internal
        return None

    def _register_validity_aggregate(self) -> None:
        """Subscribe each field's validity signal into the form `valid` aggregate."""
        for widget in self._widgets.values():
            entry = self._validity_entry(widget)
            if entry is not None:
                self._validity_entries.append(entry)
                entry._valid_signal.subscribe(lambda *_: self._recompute_validity())
        self._recompute_validity()

    def _recompute_validity(self) -> None:
        """Recompute the form `valid` aggregate from its fields' signals."""
        # Signal.set dedupes unchanged values, so this won't re-notify needlessly.
        self._valid_signal.set(all(e._valid_signal() for e in self._validity_entries))

    def validate(self) -> bool:
        """Run validation rules on all field widgets; returns True if all pass."""
        all_valid = True
        first_invalid_widget = None

        def _validate_entry(entry: Any) -> bool:
            if not getattr(entry, "_rules", None):
                return True
            # Delegate to the entry's own validator. An explicit form.validate()
            # is a manual action, so the "manual" trigger runs every rule; the
            # entry validates its typed value, updates the field's reactive
            # validity signals, and emits the validation events. The text-area
            # composite exposes a no-argument validate().
            if hasattr(entry, "_get_validation_value"):
                return entry.validate(entry._get_validation_value(), trigger="manual")
            return entry.validate()

        for widget in self._widgets.values():
            entry = self._validity_entry(widget)
            if entry is None:
                continue
            ok = _validate_entry(entry)
            if not ok and first_invalid_widget is None:
                first_invalid_widget = widget
            all_valid = all_valid and ok
        if first_invalid_widget is not None:
            try:
                first_invalid_widget.focus()
            except Exception:
                try:
                    first_invalid_widget._internal.focus_set()
                except Exception:
                    pass
        return all_valid

    # --- Field access API (v2) -------------------------------------------

    def field(self, key: str) -> Any:
        """Return the field widget for the given key.

        Args:
            key: The field key.

        Returns:
            The public field widget instance (e.g. `NumberField`, `TextArea`).

        Raises:
            KeyError: If no field with the given key exists.
        """
        if key not in self._widgets:
            raise KeyError(f"No field with key '{key}'")
        return self._widgets[key]

    def fields(self) -> tuple[Any, ...]:
        """Return all field widgets in insertion order.

        Returns:
            Tuple of public field widget instances.
        """
        return tuple(self._widgets[k] for k in self._items_by_key.keys() if k in self._widgets)

    def keys(self) -> tuple[str, ...]:
        """Return all field keys in insertion order.

        Returns:
            Tuple of field key strings.
        """
        return tuple(self._items_by_key.keys())

    # --- Value helpers (explicit, no overloading) -------------------------

    def get_field_value(self, key: str) -> Any:
        """Return the current value of the field.

        Args:
            key: The field key.

        Returns:
            The current field value.

        Raises:
            KeyError: If no field with the given key exists.
        """
        if key not in self._widgets:
            raise KeyError(f"No field with key '{key}'")
        return self._read_value_from_widget(key)

    def set_field_value(self, key: str, value: Any) -> None:
        """Set the value of the field.

        Args:
            key: The field key.
            value: The new value to set.

        Raises:
            KeyError: If no field with the given key exists.
        """
        if key not in self._items_by_key:
            raise KeyError(f"No field with key '{key}'")
        item = self._items_by_key[key]
        self._apply_value_to_widget(key, item, value)
        self._data[key] = value

    # --- Variable & signal accessors (v2 short names) ---------------------

    def field_variable(self, key: str) -> Variable | None:
        """Return the Tk Variable for the field.

        Args:
            key: The field key.

        Returns:
            The Tk Variable, or None if not available.
        """
        return self._variables.get(key)

    def field_signal(self, key: str):
        """Return the Signal for the field value.

        Args:
            key: The field key.

        Returns:
            The Signal, or None if not available.
        """
        return self._signals.get(key)

    def field_textsignal(self, key: str):
        """Return the Signal for the field text.

        Args:
            key: The field key.

        Returns:
            The text Signal, or None if not available.
        """
        return self._textsignals.get(key)

    # --- Legacy variable/signal accessors (backward compatibility) --------

    def get_field_variable(self, key: str) -> Variable | None:
        """Return the Tk variable associated with a field key, if any.

        Deprecated:
            Use `field_variable(key)` instead.
        """
        return self.field_variable(key)

    def get_field_signal(self, key: str):
        """Return the Signal associated with a field key, if any.

        Deprecated:
            Use `field_signal(key)` instead.
        """
        return self.field_signal(key)

    def get_field_textsignal(self, key: str):
        """Return the TextSignal associated with a field key, if any.

        Deprecated:
            Use `field_textsignal(key)` instead.
        """
        return self.field_textsignal(key)

    # --- Form-level value API (v2 standardization) ------------------------

    def get(self) -> dict[str, Any]:
        """Return all field values as a dictionary.

        Returns:
            Dictionary mapping field keys to their current values.
        """
        return self.data

    def set(self, values: Mapping[str, Any]) -> None:
        """Set multiple field values from a dictionary.

        Args:
            values: Dictionary mapping field keys to values.
        """
        self._data = dict(values)
        self._suspend_sync = True
        try:
            for key, item in self._items_by_key.items():
                value = self._data.get(key)
                self._apply_value_to_widget(key, item, value)
        finally:
            self._suspend_sync = False

    @property
    def value(self) -> dict[str, Any]:
        """Get or set all form field values as a dictionary."""
        return self.get()

    @value.setter
    def value(self, values: Mapping[str, Any]) -> None:
        self.set(values)

    @configure_delegate('data')
    def _delegate_data(self, value: Mapping[str, Any] = None):
        if value is None:
            return dict(self._collect_data())
        else:
            self._data = dict(value)
            self._suspend_sync = True
            try:
                for key, item in self._items_by_key.items():
                    value = self._data.get(key)
                    self._apply_value_to_widget(key, item, value)
            finally:
                self._suspend_sync = False
            return None

    def _build_items(self, parent: Frame, items: Sequence[FormItem], *, col_count: int, min_col_width: int) -> None:
        for col in range(col_count):
            parent.columnconfigure(col, weight=1, minsize=min_col_width)

        auto_row = 0
        auto_col = 0

        for item in items:
            widget = None
            columnspan = 1
            rowspan = 1

            if isinstance(item, FieldItem):
                widget = self._build_field(parent, item)
                columnspan = item.columnspan
                rowspan = item.rowspan
            elif isinstance(item, GroupItem):
                container = LabelFrame(parent, text=item.label, padding=item.padding) if item.label else Frame(
                    parent, padding=item.padding)
                if item.width:
                    container.configure(width=item.width)
                if item.height:
                    container.configure(height=item.height)
                nested_items = self._normalize_items(item.items)
                self._build_items(
                    container,
                    nested_items,
                    col_count=item.col_count or col_count,
                    min_col_width=item.min_col_width or min_col_width,
                )
                widget = container
                columnspan = item.columnspan
                rowspan = item.rowspan
            elif isinstance(item, TabsItem):
                tv_kwargs = {}
                if item.width is not None:
                    tv_kwargs['width'] = item.width
                if item.height is not None:
                    tv_kwargs['height'] = item.height
                tabview = TabView(parent, **tv_kwargs)
                for i, tab in enumerate(self._normalize_tabs(item.tabs)):
                    page = tabview.add(f'tab_{i}', text=tab.label)
                    if tab.padding is not None:
                        page.configure(padding=tab.padding)
                    self._build_items(
                        page, self._normalize_items(tab.items), col_count=col_count, min_col_width=min_col_width)
                widget = tabview
                columnspan = item.columnspan
                rowspan = item.rowspan

            if widget is None:
                continue

            row = item.row if isinstance(item, (FieldItem, GroupItem, TabsItem)) and item.row is not None else auto_row
            column = item.column if isinstance(
                item, (FieldItem, GroupItem, TabsItem)) and item.column is not None else auto_col

            widget.grid(row=row, column=column, columnspan=columnspan, rowspan=rowspan, sticky='nsew', padx=6, pady=4)

            if isinstance(item, (FieldItem, GroupItem, TabsItem)) and item.row is None and item.column is None:
                auto_col += columnspan
                if auto_col >= col_count:
                    auto_col = 0
                    auto_row += 1

    # Editors that render something other than a validating field, so `required`
    # and friends are dropped for them. Anything NOT named here — including a
    # misspelled editor name — falls back to a text field, which does validate.
    _NON_VALIDATING_EDITORS = frozenset({'checkbox', 'switch', 'slider'})

    def _build_field(self, parent: Frame, item: FieldItem):
        if not item.visible:
            return None

        editor = item.editor or self._default_editor_for_dtype(item.dtype, self._data.get(item.key))
        options = dict(item.editor_options or {})
        # Gate on what does NOT validate, not on what does: an unrecognized
        # editor name falls back to a text field, so testing membership of the
        # validating set silently dropped `required` on a typo and let the form
        # submit empty.
        if item.required and editor not in self._NON_VALIDATING_EDITORS:
            options["required"] = True
        initial_value = self._data.get(item.key)
        label_text = item.label if item.label is not None else item.key.replace("_", " ").title()

        container = Frame(parent)
        container.columnconfigure(0, weight=1)  # Allow field widgets to expand horizontally

        # Build the public wrapper. `editor_options` are that widget's public
        # kwargs (issue #353) — the wrapper is the single translation layer to
        # the internal Tk options, so `step`, `show_border`, `mask`, etc. work.
        field_widget = self._construct_editor(editor, container, label_text, initial_value, options)

        # Commit sync: mirror the field's committed value into the form data.
        try:
            field_widget.on_change(lambda *_a, k=item.key: self._sync_value_from_widget(k))
        except Exception:
            pass

        # Preserve field_variable(): adopt the internal tk variable when present.
        internal = getattr(field_widget, "_internal", None)
        try:
            var = getattr(internal, "variable", None)
        except Exception:
            var = None
        if var is not None:
            self._variables[item.key] = var

        # Record signals the wrapper exposes (for field_signal/field_textsignal).
        signal_obj = getattr(field_widget, "signal", None)
        if signal_obj is not None:
            self._signals[item.key] = signal_obj

        if item.readonly:
            self._set_readonly(field_widget)

        self._widgets[item.key] = field_widget
        return container

    def _construct_editor(self, editor: str, container: Frame, label_text: str, initial: Any, options: dict):
        """Construct the public wrapper widget for an editor, parented to `container`.

        `options` are the wrapper's public keyword arguments; a few documented
        aliases (`values`/`items` for the option list) are normalized to the
        wrapper's parameter name. The wrapper auto-attaches to `container`.
        """
        # Local imports: the public wrappers depend on this package, so import
        # them lazily to avoid import-time cycles (mirrors _normalize_buttons).
        from bootstack.widgets.textfield import TextField
        from bootstack.widgets.numberfield import NumberField
        from bootstack.widgets.passwordfield import PasswordField
        from bootstack.widgets.datefield import DateField
        from bootstack.widgets.textarea import TextArea
        from bootstack.widgets.select import Select
        from bootstack.widgets.spinnerfield import SpinnerField
        from bootstack.widgets.boolean_controls import Checkbox, Switch
        from bootstack.widgets.slider import Slider

        opts = dict(options)
        # Internal-only options the public wrappers don't accept. Dropping them
        # keeps the strict boolean controls from raising and matches the old
        # per-editor filtering (a required/message field auto-reserves its
        # message row, so `show_message` is no longer needed here).
        for internal_only in ("show_message", "validator"):
            opts.pop(internal_only, None)

        # `value` in editor_options seeds the editor when the form data carries
        # nothing for the key; the data wins when it does. Every editor below
        # passes `value=` positionally-by-keyword, so leaving it in `opts` would
        # raise "got multiple values for keyword argument 'value'".
        seed_value = opts.pop('value', None)
        if initial is None:
            initial = seed_value

        def build(cls, *args, **defaults):
            """Construct `cls`, letting `editor_options` override the defaults."""
            merged = merge_kwargs(defaults, opts, reserved=_RESERVED_EDITOR_OPTIONS,
                                  context='Form editor_options')
            merged['parent'] = container
            return cls(*args, **merged)

        def choice_list():
            """Pop the documented `items`/`values` aliases for the option list."""
            choices = opts.pop('items', None)
            if choices is None:
                choices = opts.pop('values', None)
            return choices

        # Test against None, not truthiness: a falsy-but-real datum (0, False)
        # is a value, not an absent one, and blanking it here would write the
        # blank straight back into the form data. Pass the datum through as it
        # came, too — `data` is the caller's record, and stringifying it here
        # would flip a Decimal or a date to `str` in `form.data` before the
        # user has edited anything.
        text_value = initial if initial is not None else ""

        if editor == 'textfield':
            return build(TextField, value=text_value, label=label_text)
        if editor == 'numberfield':
            return build(NumberField, value=initial if initial is not None else 0,
                         label=label_text)
        if editor == 'passwordfield':
            return build(PasswordField, value=text_value, label=label_text)
        if editor == 'datefield':
            return build(DateField, value=initial, label=label_text)
        if editor == 'textarea':
            return build(TextArea, value=text_value, label=label_text)
        if editor == 'select':
            choices = [str(i) for i in (choice_list() or [])]
            return build(Select, options=choices, label=label_text,
                         value=initial if initial is not None else "")
        if editor == 'spinnerfield':
            choices = choice_list()
            if choices is not None:
                opts['options'] = [str(i) for i in choices]
            return build(SpinnerField, value=initial if initial is not None else "",
                         label=label_text)
        if editor in ('checkbox', 'switch'):
            # The boolean controls call their caption `label`, so pass it by
            # keyword — passing it positionally would collide with a `label`
            # option instead of letting it override, and `text` is the alias a
            # caller reaches for first.
            caption = opts.pop('text', None) or label_text
            # `None` stays `None` so a tristate checkbox starts indeterminate;
            # the widget maps `None` to unchecked when tristate is off.
            cls = Checkbox if editor == 'checkbox' else Switch
            return build(cls, label=caption,
                         value=bool(initial) if initial is not None else None)
        if editor == 'slider':
            # Slider has no label parameter, so render a stacked caption above it
            # (the field wrappers render their own label internally).
            if label_text:
                Label(container, text=label_text).pack(anchor='w', pady=(0, 2))
            return build(Slider, value=initial if initial is not None else 0)
        # Fallback: treat any unknown editor as a text field.
        return build(TextField, value=text_value, label=label_text)

    def _build_buttons(self, parent: Frame, buttons: Sequence[ButtonInput]) -> None:
        parsed = self._normalize_buttons(buttons)
        for spec in reversed(parsed):
            btn_color = getattr(spec, 'accent', None) or getattr(spec, 'color', None)
            btn_variant = getattr(spec, 'variant', None)

            if not btn_color:
                # Get color and variant from role
                btn_color, btn_variant = self._style_for_role(spec.role)

            btn = Button(parent, text=spec.text, accent=btn_color, variant=btn_variant)
            btn.configure(command=self._make_button_command(spec))
            btn.pack(side='right', padx=(4, 0))

    # --- normalization --------------------------------------------------
    def _normalize_items(self, items: Iterable[FormItem | Mapping[str, Any]]) -> list[FormItem]:
        normalized: list[FormItem] = []
        for raw in items:
            item: FormItem | None = None
            if isinstance(raw, (FieldItem, GroupItem, TabsItem)):
                item = raw
            elif isinstance(raw, Mapping):
                type_hint = raw.get('type', 'field')
                if type_hint == 'group':
                    item = GroupItem(
                        items=list(raw.get('items', [])),
                        label=raw.get('label'),
                        col_count=raw.get('col_count', 1),
                        min_col_width=raw.get('min_col_width', DEFAULT_MIN_COL_WIDTH),
                        width=raw.get('width'),
                        height=raw.get('height'),
                        column=raw.get('column'),
                        row=raw.get('row'),
                        columnspan=raw.get('columnspan', 1),
                        rowspan=raw.get('rowspan', 1),
                    )
                elif type_hint == 'tabs':
                    item = TabsItem(
                        tabs=list(raw.get('tabs', [])),
                        label=raw.get('label'),
                        width=raw.get('width'),
                        height=raw.get('height'),
                        column=raw.get('column'),
                        row=raw.get('row'),
                        columnspan=raw.get('columnspan', 1),
                        rowspan=raw.get('rowspan', 1),
                    )
                else:
                    key_value = raw.get('key')
                    if key_value is None:
                        continue
                    item = FieldItem(
                        key=str(key_value),
                        label=raw.get('label'),
                        dtype=raw.get('dtype'),
                        readonly=raw.get('readonly', False),
                        required=raw.get('required', False),
                        visible=raw.get('visible', True),
                        column=raw.get('column'),
                        row=raw.get('row'),
                        columnspan=raw.get('columnspan', 1),
                        rowspan=raw.get('rowspan', 1),
                        editor=raw.get('editor'),
                        editor_options=dict(raw.get('editor_options', {}) or {}),
                    )

            if isinstance(item, GroupItem):
                item.items = self._normalize_items(item.items)
            if isinstance(item, TabsItem):
                item.tabs = self._normalize_tabs(item.tabs)
            if isinstance(item, FieldItem):
                self._items_by_key[item.key] = item

            if item:
                normalized.append(item)
        return normalized

    def _normalize_tabs(self, tabs: Iterable[TabItem | Mapping[str, Any]]) -> list[TabItem]:
        normalized: list[TabItem] = []
        for raw in tabs:
            if isinstance(raw, TabItem):
                normalized.append(raw)
            elif isinstance(raw, Mapping):
                normalized.append(TabItem(label=str(raw.get('label', 'Tab')), items=list(raw.get('items', []))))
        return normalized

    def _normalize_buttons(self, buttons: Sequence[ButtonInput]) -> list["DialogButton"]:
        from bootstack.dialogs._impl.dialog import DialogButton  # local import to avoid circular init

        normalized: list[DialogButton] = []
        for raw in buttons:
            if isinstance(raw, DialogButton):
                normalized.append(raw)
            elif isinstance(raw, Mapping):
                normalized.append(DialogButton(**raw))  # type: ignore[arg-type]
            elif isinstance(raw, str):
                normalized.append(DialogButton(text=raw))
        return normalized

    # --- data helpers ---------------------------------------------------
    def _collect_data(self) -> dict[str, Any]:
        current: dict[str, Any] = dict(self._data)
        for key in self._widgets.keys():
            current[key] = self._read_value_from_widget(key)
        return current

    def _read_value_from_widget(self, key: str) -> Any:
        widget = self._widgets.get(key)
        if widget is None:
            return self._data.get(key)

        # Every public wrapper exposes a `.value` property.
        try:
            value = widget.value
        except Exception:
            if key in self._variables:
                value = self._variables[key].get()
            else:
                value = self._data.get(key)

        item = self._items_by_key.get(key)
        if item:
            value = self._coerce_value(item.dtype, value)
        return value

    def _apply_value_to_widget(self, key: str, item: FieldItem, value: Any) -> None:
        widget = self._widgets.get(key)
        if widget is None:
            return

        # Programmatic writes must not echo back as a user change. Suspend sync
        # around the assignment so a wrapper that emits <<Change>> synchronously
        # doesn't re-enter _sync_value_from_widget.
        previous_suspend = self._suspend_sync
        self._suspend_sync = True
        try:
            widget.value = value
        except Exception:
            if key in self._variables:
                try:
                    self._variables[key].set("" if value is None else value)
                except Exception:
                    pass
        finally:
            self._suspend_sync = previous_suspend

    def _sync_value_from_widget(self, key: str) -> None:
        if self._suspend_sync:
            return
        if key not in self._items_by_key:
            return
        new_value = self._read_value_from_widget(key)
        # Notify only on a real change. This also drops a spurious echo from an
        # editor that emits its change event asynchronously (e.g. Select fires
        # `<<Change>>` with when="tail"), which lands after a programmatic write
        # has already restored `_suspend_sync` and stored the value.
        if key in self._data and new_value == self._data[key]:
            return
        self._data[key] = new_value
        if self._on_data_change:
            self._on_data_change(dict(self._data))
        self.event_generate("<<BsDataChange>>")

    def _default_editor_for_dtype(self, dtype: Any, value: Any) -> EditorType:
        if dtype in ('int', int, 'float', float):
            return 'numberfield'
        if dtype in ('bool', bool):
            return 'checkbox'
        if dtype in ('date', 'datetime', date, datetime):
            return 'datefield'
        if dtype in ('password',):
            return 'passwordfield'
        if value is not None:
            if isinstance(value, (int, float)):
                return 'numberfield'
            if isinstance(value, (bool,)):
                return 'checkbox'
            if isinstance(value, (date, datetime)):
                return 'datefield'
        return 'textfield'

    def _coerce_value(self, dtype: Any, value: Any) -> Any:
        if dtype in ('int', int):
            try:
                return int(value)
            except Exception:
                return value
        if dtype in ('float', float):
            try:
                return float(value)
            except Exception:
                return value
        if dtype in ('bool', bool):
            return bool(value)
        if dtype in ('date', 'datetime', date, datetime):
            return value
        return value


    def _set_readonly(self, widget: Any) -> None:
        # Field editors expose a live `read_only` property; boolean and slider
        # editors have no read-only state, so they fall back to `disabled`
        # (matching the pre-rewrite behavior for those editors).
        if hasattr(widget, "read_only"):
            try:
                widget.read_only = True
                return
            except Exception:
                pass
        if hasattr(widget, "disabled"):
            try:
                widget.disabled = True
            except Exception:
                pass

    # --- button helpers -------------------------------------------------
    def _make_button_command(self, spec: DialogButton):
        def command():
            if spec.command:
                spec.command(self)  # type: ignore[arg-type]
            self.result = spec.result if spec.result is not None else self.data

        return command

    def _style_for_role(self, role: str) -> tuple[str, str | None]:
        """Get color and variant for a button role.

        Returns:
            Tuple of (color, variant) for the role.
        """
        if role == "primary":
            return ("primary", None)
        if role == "secondary":
            return ("default", None)
        if role == "danger":
            return ("danger", None)
        if role == "cancel":
            return ("default", "outline")
        if role == "help":
            return ("primary", "link")
        return ("default", None)

    # --- inference ------------------------------------------------------
    def _infer_items_from_data(self, data: Mapping[str, Any]) -> list[FieldItem]:
        inferred: list[FieldItem] = []
        for key, value in data.items():
            inferred.append(
                FieldItem(
                    key=str(key),
                    label=str(key).replace('_', ' ').title(),
                    dtype=self._infer_dtype_from_value(value),
                    editor=self._default_editor_for_dtype(self._infer_dtype_from_value(value), value),
                )
            )
        return inferred

    @staticmethod
    def _infer_dtype_from_value(value: Any) -> DType:
        if isinstance(value, bool):
            return 'bool'
        if isinstance(value, int) and not isinstance(value, bool):
            return 'int'
        if isinstance(value, float):
            return 'float'
        if isinstance(value, (date, datetime)):
            return 'date'
        return 'str'


__all__ = [
    "Form",
    "FormItem",
    "FieldItem",
    "GroupItem",
    "TabsItem",
    "TabItem",
]
