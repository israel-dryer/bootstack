"""Field widget module.

Provides a flexible generic entry field composite widget used as the foundation
for creating specialized entry widgets like TextEntry, PasswordEntry, NumberEntry, etc.
"""

from tkinter import TclError, Variable
from typing import Any, Callable, Literal, Type, TypedDict, cast

from bootstack.signals import Signal
from bootstack.validation.types import RuleType
from bootstack.widgets.primitives.button import Button
from bootstack.widgets.primitives.frame import Frame
from bootstack.widgets.primitives.label import Label
from bootstack.widgets.primitives.checkbutton import CheckButton
from bootstack.widgets.primitives.checktoggle import CheckToggle
from bootstack.widgets.mixins import configure_delegate
from bootstack.widgets.mixins.entry_mixin import EntryMixin
from bootstack.widgets._parts.numberentry_part import NumberEntryPart
from bootstack.widgets._parts.textentry_part import TextEntryPart
from bootstack.widgets._parts.spinnerentry_part import SpinnerEntryPart
from bootstack.widgets.types import Master, AccentToken, Justify, VariantToken, WidgetDensity, WidgetState

FieldKind = Literal['text', 'numeric', 'spinbox']

EntryWidget = TextEntryPart | NumberEntryPart | SpinnerEntryPart
"""The internal entry widget used by a Field — one of the three entry part types."""

FieldAddonWidget = Button | Label | CheckToggle
"""Widget types supported by `Field.insert_addon`."""
"""Type alias for field kind specification.

Determines which entry part widget to use:
    - 'text': Uses TextEntryPart for text input with formatting support
    - 'numeric': Uses NumberEntryPart for numeric input with bounds and stepping
    - 'spinbox': Uses SpinnerEntryPart for spinner input (supports text or numeric values)
"""


class InputEventData(TypedDict):
    """Payload for `<<Input>>` events — fires on each keystroke."""
    text: str
    """Current raw text in the entry field."""


class ChangeEventData(TypedDict):
    """Payload for `<<Change>>` events — fires on commit (blur or Enter)."""
    value: Any
    """Committed (parsed) value."""
    prev_value: Any
    """Previous committed value."""
    text: str
    """Raw display string."""


class EnterEventData(TypedDict):
    """Payload for `<Return>` key events."""
    value: Any
    """Committed (parsed) value."""
    text: str
    """Raw display string."""


class ValidationEventData(TypedDict):
    """Payload for `<<Valid>>`, `<<Invalid>>`, and `<<Validate>>` events."""
    value: Any
    """Committed (parsed) value."""
    is_valid: bool
    """Whether validation passed."""
    message: str
    """Validation error text, or empty string on pass."""


class FieldOptions(TypedDict, total=False):
    """Type hints for Field widget configuration options.

    Attributes:
        allow_blank: If True, empty input is allowed. If False, empty input preserves previous value.
        accent: Accent token for the focus ring and active border of the input.
        density: Widget density. 'default' for normal size, 'compact' for smaller size.
        variant: Style variant (if applicable).
        cursor: Cursor to display when hovering over the widget.
        value_format: ICU format pattern for parsing/formatting (e.g., '$#,##0.00' for currency).
        exportselection: If True, selected text is exported to X selection.
        font: Font to use for text display.
        foreground: Text color.
        initial_focus: If True, widget receives focus when created.
        justify: Text justification ('left', 'center', 'right').
        show_message: If True, displays message text below the field.
        padding: Padding around the entry widget.
        show: Character to display instead of typed characters (for password fields).
        state: The widget state. One of 'normal', 'disabled', or 'readonly'.
        takefocus: If True, widget can receive focus via Tab key.
        textvariable: Tkinter Variable to link with the entry text.
            See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
        textsignal: Signal object for reactive text updates.
        width: Width of the entry in characters.
        required: If True, field cannot be empty (adds validation rule).
        xscrollcommand: Callback for horizontal scrolling.
        localize: Determines the field label localization mode. 'auto', True, False.
    """
    allow_blank: bool
    accent: AccentToken | str
    density: WidgetDensity
    variant: VariantToken | str
    cursor: str
    value_format: str
    exportselection: bool
    font: str
    foreground: str
    initial_focus: bool
    justify: Justify
    show_message: bool
    padding: str
    show: str
    state: WidgetState
    takefocus: bool
    textvariable: Variable
    textsignal: Signal
    width: int
    required: bool
    xscrollcommand: Callable[[int, int], None]
    localize: bool | Literal['auto']


class Field(EntryMixin, Frame):
    """A flexible generic composite entry field widget.

    Field is a base composite widget that combines a label, entry input, and
    message area into a complete input field component. It serves as the foundation
    for creating specialized entry widgets like TextEntry, PasswordEntry, NumberEntry,
    and other custom entry types.

    The widget automatically handles layout, focus states, validation feedback, and
    provides a consistent API for all entry-based components. It supports both text
    and numeric input types through the `kind` parameter.
    """

    def __init__(
            self,
            master: Master = None,
            *,
            value: str | int | float = None,
            label: str = None,
            message: str = None,
            show_message: bool = False,
            required: bool = False,
            kind: FieldKind = "text",
            **kwargs: Any
    ):
        """Args:
            master: Parent widget. If None, uses the default root window.
            value: Initial value to display. Can be str, int, or float depending
                on the field kind. For 'text' kind, should be a string. For
                'numeric' kind, can be int or float. Default is None.
            label: Optional label text to display above the entry field.
                If required=True, an asterisk (*) is automatically appended to
                indicate the field is mandatory.
            message: Optional message text to display below the entry field.
                Used for hints, instructions, or help text. This text is replaced
                by validation error messages when validation fails, and restored
                when validation passes. Default is None (no message).
            show_message: If True, displays the message area below the field.
                If False, hides the message area entirely (validation errors
                won't be shown). Defaults to False, but auto-enables when
                `message=` or `required=True` is set.
            required: If True, marks the field as required and automatically adds
                a 'required' validation rule. An asterisk (*) is appended to the
                label. The field cannot be left empty. Default is False.
            kind: Type of entry field to create. Either 'text' for text input
                (uses TextEntryPart) or 'numeric' for numeric input (uses
                NumberEntryPart). Default is 'text'.

        Other Parameters:
            accent: Accent token for the focus ring and active border.
            density: Widget density — 'default' or 'compact'.
            state: Initial widget state — 'normal', 'disabled', or 'readonly'.
            value_format: ICU format pattern for parsing/formatting.
            allow_blank: Allow empty input.
            initial_focus: Focus on creation.
            show: Character to mask input (e.g., '*' for passwords).
            width: Width in characters.
            font: Font specification.
            justify: Text alignment ('left', 'center', 'right').
            textvariable: Tkinter Variable linked to entry text.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            textsignal: Signal for reactive text updates.
            minvalue: Minimum allowed value (numeric kind only).
            maxvalue: Maximum allowed value (numeric kind only).
            increment: Step size for up/down arrows (numeric kind only).
            wrap: Wrap around at boundaries (numeric kind only).
        """
        # Accept legacy parameter name and prevent it from reaching the Tk widget.
        if 'show_messages' in kwargs:
            show_message = kwargs.pop('show_messages')
        # Track if user explicitly provided show_message
        show_message_explicit = 'show_message' in kwargs
        show_message = kwargs.pop('show_message', show_message)

        # Auto-enable show_message if there is any chance a message will be shown
        if (message or required) and not show_message_explicit:
            show_message = True

        accent = kwargs.pop('accent', None)
        self._density = kwargs.pop('density', 'default')
        self._localize = cast(bool | Literal['auto'], kwargs.pop('localize', 'auto'))

        # Field itself (outer Frame) doesn't need styling - only pass master
        super().__init__(master)

        # Set accent AFTER super().__init__ to avoid being overwritten by wrapper
        self._accent = accent

        # configuration
        self._message_text = message
        self._show_messages = show_message
        self._addons: dict[str, Button | Label | CheckToggle] = {}
        self._required = required
        self._kind = kind
        self._label_text = label
        self._value = value

        self._entry: EntryWidget
        self._addons: dict[str, Button | Label | CheckToggle] = {}

        # layout
        label_text = self._label_text or ''
        self._label_lbl = Label(
            self,
            localize=self._localize,
            text=f"{label_text}*" if required else label_text,
            font="label[normal]"
        )
        self._message_lbl = Label(self, localize=self._localize, text=message or '', font="caption", accent="secondary")

        # field container & field - pass density for styling via style_options
        field_padding = 5
        self._field = Frame(self, accent=self._accent, padding=field_padding, ttk_class="TField", style_options={'density': self._density})

        if kind == "numeric":
            self._entry = NumberEntryPart(self._field, value=value, density=self._density, **kwargs)
        elif kind == "spinbox":
            self._entry = SpinnerEntryPart(self._field, value=value, density=self._density, **kwargs)
        else:
            self._entry = TextEntryPart(self._field, value=value, density=self._density, **kwargs)

        # attach widgets
        if label:
            self._label_lbl.pack(side='top', fill='x', padx=(4, 0))

        self._field.pack(side='top', fill='x', expand=True)
        self._entry.pack(side='left', fill='x', expand=True, padx=(0, 6) if kind == "spinbox" else 0, pady=0)

        self._entry.bind('<<StateChanged>>', self._sync_addon_state, add=True)
        self._sync_addon_state()

        if self._show_messages:
            self._message_lbl.pack(side='top', fill='x', padx=4)

        self._entry.bind('<<Invalid>>', self._show_error, add=True)
        self._entry.bind('<<Valid>>', self._clear_error, add=True)

        # bind focus styling to the field frame
        self._entry.bind('<FocusIn>', lambda _: self._field.state(['focus']), add=True)
        self._entry.bind('<FocusOut>', lambda _: self._field.state(['!focus']), add=True)

        # add required validation
        if required:
            self._entry.add_validation_rule("required")


        self.validation = self._entry.validate

        # Copy Field's delegate handlers to entry for configuration forwarding
        for key, method_name in self._configure_delegate_map.items():
            if hasattr(self, method_name):
                # Attach the Field's handler method to the entry instance
                setattr(self._entry, method_name, getattr(self, method_name))
                # Add to entry's delegate map
                self._entry._configure_delegate_map[key] = method_name

        # Forward configuration methods to entry widget
        self.configure = self._entry.configure
        self.config = self._entry.config
        self.cget = self._entry.cget
        self.__getitem__ = self._entry.__getitem__
        self.__setitem__ = self._entry.__setitem__

    @property
    def value(self) -> Any:
        """Get or set the parsed value via the underlying entry widget."""
        return self._entry.value()

    @value.setter
    def value(self, value: Any) -> None:
        self._entry.value(value)

    def get(self) -> str:
        """Return the raw text from the underlying entry widget."""
        return self._entry.get()

    @property
    def entry_widget(self) -> EntryWidget:
        """Get the underlying entry widget."""
        return self._entry

    @property
    def label_widget(self) -> Label:
        """Get the label widget."""
        return self._label_lbl

    @property
    def message_widget(self) -> Label:
        """Get the message widget."""
        return self._message_lbl

    @property
    def addons(self) -> dict[str, FieldAddonWidget]:
        """Get the dictionary of inserted addon widgets."""
        return self._addons

    @property
    def variable(self) -> Variable:
        """The `StringVar` linked to the entry text.

        Use when bridging to a plain tkinter widget that requires `textvariable=`,
        or for direct read/write access to the raw string value. For reactive
        bindings between bootstack widgets, prefer `signal` instead.
        See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
        """
        return self._entry.textvariable

    @property
    def signal(self) -> Signal:
        """The `Signal[str]` linked to the entry text.

        Pass as `textsignal=` to any other bootstack widget to keep its text
        in sync with this field's value, or call `signal.subscribe(callback)`
        to observe changes programmatically. See the
        [Reactivity guide](../../guides/reactivity.md) for patterns.
        """
        return self._entry.textsignal

    @configure_delegate
    def _config_accent(self, value=None):
        if value is None:
            return self._accent
        else:
            self._accent = value
            self._field['accent'] = value
        return None


    # ------ Event registration ------

    def on_input(self, callback: Callable) -> str:
        """Register a callback for `<<Input>>` events (fires on each keystroke).

        Args:
            callback: Receives a Tkinter `Event` object whose `event.data` is an
                `InputEventData` dict with key `text` (current raw text).

        Returns:
            Bind ID — pass to `off_input()` to unsubscribe.
        """
        return self._entry.on_input(callback)

    def off_input(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<Input>>`.

        Args:
            bind_id: ID returned by `on_input()`.
        """
        self._entry.off_input(bind_id)

    def on_changed(self, callback: Callable) -> str:
        """Register a callback for `<<Change>>` events (fires on commit).

        Args:
            callback: Receives a Tkinter `Event` object whose `event.data` is a
                `ChangeEventData` dict with keys `value` (committed value),
                `prev_value` (previous value), and `text` (raw display string).

        Returns:
            Bind ID — pass to `off_changed()` to unsubscribe.
        """
        return self._entry.on_changed(callback)

    def off_changed(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<Change>>`.

        Args:
            bind_id: ID returned by `on_changed()`.
        """
        self._entry.off_changed(bind_id)

    def on_enter(self, callback: Callable) -> str:
        """Register a callback for `<Return>` key events.

        Args:
            callback: Receives a Tkinter `Event` object whose `event.data` is an
                `EnterEventData` dict with keys `value` (committed value)
                and `text` (raw display string).

        Returns:
            Bind ID — pass to `off_enter()` to unsubscribe.
        """
        return self._entry.on_enter(callback)

    def off_enter(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<Return>`.

        Args:
            bind_id: ID returned by `on_enter()`.
        """
        self._entry.off_enter(bind_id)

    def on_valid(self, callback: Callable[[ValidationEventData], None]) -> None:
        """Register a callback for `<<Valid>>` events (fires when validation passes).

        Args:
            callback: Receives a `ValidationEventData` dict with keys
                `value` (committed value), `is_valid` (`True`), and
                `message` (empty string on pass).
        """
        self._entry.on_valid(callback)

    def off_valid(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<Valid>>`.

        Args:
            bind_id: Bind ID from a direct `widget.bind()` call, or `None`
                to remove all `<<Valid>>` bindings.
        """
        self._entry.off_valid(bind_id)

    def on_invalid(self, callback: Callable[[ValidationEventData], None]) -> None:
        """Register a callback for `<<Invalid>>` events (fires when validation fails).

        Args:
            callback: Receives a `ValidationEventData` dict with keys
                `value` (committed value), `is_valid` (`False`), and
                `message` (validation error text).
        """
        self._entry.on_invalid(callback)

    def off_invalid(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<Invalid>>`.

        Args:
            bind_id: Bind ID from a direct `widget.bind()` call, or `None`
                to remove all `<<Invalid>>` bindings.
        """
        self._entry.off_invalid(bind_id)

    def on_validated(self, callback: Callable[[ValidationEventData], None]) -> None:
        """Register a callback for `<<Validate>>` events (fires after any validation).

        Args:
            callback: Receives a `ValidationEventData` dict with keys
                `value` (committed value), `is_valid` (bool), and
                `message` (validation message or empty string).
        """
        self._entry.on_validated(callback)

    def off_validated(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<Validate>>`.

        Args:
            bind_id: Bind ID from a direct `widget.bind()` call, or `None`
                to remove all `<<Validate>>` bindings.
        """
        self._entry.off_validated(bind_id)

    # ------ Validation ------

    def add_validation_rule(
        self,
        rule_type: RuleType,
        **kwargs,
    ) -> None:
        """Add a validation rule to the field.

        Rules are evaluated on blur and on Enter. When a rule fails the field
        emits `<<Invalid>>`; when all rules pass it emits `<<Valid>>`. Both
        carry a `ValidationEventData` payload.

        Args:
            rule_type: Rule type. One of:

                - `"required"` — field must not be empty.
                - `"email"` — value must be a valid email address.
                - `"pattern"` — value must match a regex. Pass `pattern=`.
                - `"stringLength"` — length bounds. Pass `min=` and/or `max=`.
                - `"compare"` — must match another field's value. Pass `other_field=`.
                - `"custom"` — arbitrary logic. Pass `func=`, a callable that
                  receives the value and returns `bool` or `(bool, message)`.

            **kwargs: Rule-specific options. `message=` is accepted by all rule
                types to override the default failure message.
        """
        self._reserve_message_space()
        self._entry.add_validation_rule(rule_type, **kwargs)

    def disable(self):
        """Disable the field, preventing user input."""
        self._entry.state(['disabled !readonly'])
        self._field.state(['disabled'])
        self._set_addons_state(True)

    def enable(self):
        """Enable the field, allowing user input."""
        self._entry.state(['!disabled !readonly'])
        self._field.state(['!disabled'])
        self._set_addons_state(False)

    def readonly(self, value: bool = None):
        """Set or toggle the readonly state of the field."""
        if value == False:
            self._field.state(['disabled'])
            self._entry.state(['readonly'])
        elif value:
            self._field.state(['!disabled'])
            self._entry.state(['readonly'])
        else:
            self._entry.state(['readonly !disabled'])
            self._field.state(['disabled'])
        self._sync_addon_state()

    def insert_addon(
            self,
            widget: Type[FieldAddonWidget],
            position: Literal['before', 'after'],
            name: str | None = None,
            accent: str | None = None,
            pack_options: dict[str, Any] = None,
            **kwargs: Any
    ) -> FieldAddonWidget:
        """Insert a widget addon before or after the entry input.

        Addons are Button, Label, or CheckToggle widgets positioned inside the field container,
        either before (left of) or after (right of) the entry input. Common use
        cases include search buttons, icons, clear buttons, or status indicators.

        The addon widget automatically:
        - Inherits the field's disabled state
        - Participates in focus state styling (highlights field on addon focus)
        - Is stored in the addons dictionary for later reference

        Args:
            widget: Widget class to instantiate. Must be Button, Label, or CheckToggle.
            position: Position relative to the entry input:

                - 'before': Insert to the left of the entry (prefix)
                - 'after': Insert to the right of the entry (suffix)
            name: Optional name for the addon. If provided, the addon can be
                retrieved from the addons dictionary using this name. If None,
                the widget's string representation is used as the key.
            accent: Optional accent color for the addon. Default to surface color. Prefer to use an accent if using
                a text-only button.
            pack_options: Optional dictionary of additional pack() options to apply when placing the addon widget.
                Common options include padx, pady, etc. The side and after/before options are set automatically based
                on position.
            **kwargs: Additional keyword arguments passed to the widget constructor.
                For Button: text, command, icon, accent, variant, etc.
                For Label: text, icon, image, accent, etc.
                For CheckToggle: text, icon, signal, command, accent, etc.
                Note: variant and takefocus are set automatically but can be
                overridden.
        """
        variant = "suffix" if position == "after" else "prefix"
        kwargs.setdefault('ttk_class', 'TField')
        kwargs.setdefault('variant', variant)
        kwargs.setdefault('takefocus', False)
        kwargs.setdefault('density', self._density)
        kwargs.setdefault('anchor', 'center')
        if 'icon' in kwargs and 'text' not in kwargs:
            kwargs.setdefault('compound', 'image')

        if issubclass(widget, (Button, CheckButton)):
            icon_only = kwargs.get('icon_only', False)
            if 'style_options' in kwargs:
                kwargs['style_options'].update(use_active_states=True, density=self._density, icon_only=icon_only)
            else:
                kwargs['style_options'] = dict(use_active_states=True, density=self._density, icon_only=icon_only)
        instance = widget(master=self._field, accent=accent, **kwargs)
        key = name or str(instance)
        self._addons[key] = instance

        # configure layout
        options = pack_options or {}
        if position == "after":
            options.update(side="right", after=self._entry)
        else:
            options.update(side="left", before=self._entry)
        instance.pack(**options)

        # match parent disabled state
        self._sync_addon_state()

        # bind focus events to field frame
        instance.bind('<FocusIn>', lambda _: self._field.state(['focus']), add=True)
        instance.bind('<FocusOut>', lambda _: self._field.state(['!focus']), add=True)

        return instance

    def _reserve_message_space(self) -> None:
        if not self._show_messages:
            self._show_messages = True
            self._message_lbl.pack(side='top', fill='x', padx=4)

    def _show_error(self, event: Any) -> None:
        """Display a validation error message below the input field."""
        self._message_lbl['text'] = event.data['message']
        self._message_lbl['accent'] = "danger"
        self._message_lbl.pack(side='top', after=self._field, padx=4)

    def _clear_error(self, _: Any) -> None:
        """Clear the error message and restore the original message text."""
        self._message_lbl['text'] = self._message_text or ''
        self._message_lbl['accent'] = "secondary"

    def _set_addons_state(self, disabled: bool) -> None:
        """Configure addon widgets based on whether the entry is interactive."""
        state_value = 'disabled' if disabled else '!disabled'
        for item in self._addons.values():
            try:
                item.configure(state=state_value)
            except TclError:
                pass

    def _sync_addon_state(self, event: Any = None) -> None:
        """Ensure addons match the entry's interactivity state."""
        entry_states = self._entry.state()
        disabled = 'disabled' in entry_states or 'readonly' in entry_states
        self._set_addons_state(disabled)
