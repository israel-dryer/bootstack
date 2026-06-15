from __future__ import annotations

from tkinter import StringVar
from typing import Any, Callable, Literal, TYPE_CHECKING

from typing_extensions import TypedDict, Unpack

from bootstack.widgets._impl.primitives.radiotoggle import RadioToggle
from bootstack.widgets._impl.primitives.checktoggle import CheckToggle
from bootstack._core.variables import SetVar
from bootstack.widgets._impl.mixins.configure_mixin import configure_delegate
from bootstack.widgets._impl.primitives import Frame
from bootstack.widgets.types import Orient, AccentToken, SurfaceToken

if TYPE_CHECKING:
    from bootstack.signals import Signal
    import tkinter as tk


class ToggleGroupKwargs(TypedDict, total=False):
    mode: Literal['single', 'multi']
    variable: Any
    signal: Signal[Any]
    value: str | set[str]
    orient: Orient
    accent: AccentToken | str
    variant: str
    show_border: bool
    surface: SurfaceToken | str
    style_options: dict[str, Any]
    # Frame options
    padding: Any
    width: int
    height: int


class ToggleGroup(Frame):
    """A group of toggle buttons with single or multi-selection support.

    The ToggleGroup widget provides a convenient way to create groups of toggle
    buttons with automatic position tracking and styling. It supports both single
    selection (radio button behavior) and multi-selection (checkbox behavior).
    """

    def __init__(self, master: Any = None, **kwargs: Unpack[ToggleGroupKwargs]):
        """Initialize the ToggleGroup.

        Args:
            master: Parent widget. If None, uses the default root window.

        Other Parameters:
            mode: Selection mode - 'single' for radio button behavior (default),
                or 'multi' for checkbox behavior allowing multiple selections.
            orient: Layout orientation - 'horizontal' (default) or 'vertical'.
            accent: Accent token for styling (e.g., 'primary', 'danger').
                Defaults to 'default' (a neutral selected state).
            variant: Style variant (e.g., 'outline', 'ghost').
            variable: Optional tk.Variable for controlling the value. For single mode,
                use StringVar; for multi mode, use SetVar.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            signal: Optional Signal instance for reactive programming.
            value: Initial value - string for single mode, set for multi mode.
            show_border: If True, draws a border around the group.
            surface: Optional surface token; otherwise inherited.
            style_options: Additional style options passed to child buttons.
            padding: Frame padding. Defaults to 1.
            width: Requested width in pixels.
            height: Requested height in pixels.
        """
        # Extract ToggleGroup-specific options before super().__init__
        self._mode = kwargs.pop('mode', 'single')
        self._orientation = kwargs.pop('orient', 'horizontal')
        accent = kwargs.pop('accent', None) or 'default'
        variant = kwargs.pop('variant', None)  # None (default), 'outline', or 'ghost'
        self._state = kwargs.pop('state', 'normal')

        # Handle signal/variable/value similar to CheckToggle pattern
        initial_value = kwargs.pop('value', None)

        style_options = kwargs.pop('style_options', {})

        # Initialize internal state
        self._buttons: dict[str, RadioToggle | CheckToggle] = {}

        # Extract signal/variable before Frame init
        signal_value = kwargs.pop('signal', None)
        variable_value = kwargs.pop('variable', None)

        # Call super().__init__() - just Frame now
        if 'padding' not in kwargs:
            kwargs['padding'] = 1
        super().__init__(master, style_options=style_options, **kwargs)

        # Restore accent/variant (super().__init__ overwrites them with None)
        self._accent = accent
        self._variant = variant

        # Handle variable/signal setup manually
        if signal_value is not None:
            # Signal provided - extract its variable
            self._signal = signal_value
            self._variable = signal_value.var
        elif variable_value is not None:
            # Variable provided - wrap in Signal
            from bootstack.signals import Signal
            self._variable = variable_value
            self._signal = Signal.from_variable(variable_value)
            # Set initial value if provided
            if initial_value is not None:
                self._variable.set(initial_value)
        else:
            # Neither provided - create internal variable
            from bootstack.signals import Signal
            if self._mode == 'single':
                internal_var = StringVar(value=initial_value or '')
            else:
                internal_var = SetVar(value=initial_value or set())
            self._variable = internal_var
            self._signal = Signal.from_variable(internal_var)

    @property
    def variable(self) -> 'tk.Variable':
        """Get the underlying tk.Variable.

        See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
        """
        return self._variable

    @variable.setter
    def variable(self, value: 'tk.Variable') -> None:
        """Set the variable."""
        from bootstack.signals import Signal
        self._variable = value
        self._signal = Signal.from_variable(value)

    @property
    def signal(self) -> Signal[Any]:
        """Get the signal."""
        return self._signal

    @signal.setter
    def signal(self, value: Signal[Any]) -> None:
        """Set the signal."""
        self._signal = value
        self._variable = value.var

    def add(self, text: str = None, value: Any = None, key: str | None = None, **kwargs: Any) -> RadioToggle | CheckToggle:
        """Add a toggle button to the group.

        Args:
            text: Text to display on the button.
            value: Value this button represents (required).
            key: Unique identifier. Defaults to value.
            **kwargs: Additional arguments passed to RadioToggle or CheckToggle.

        Returns:
            The created button widget.
        """
        if value is None:
            raise ValueError("The 'value' argument is required.")

        key = key or value
        if key in self._buttons:
            raise ValueError(f"A button with the key '{key}' already exists.")

        btn_kwargs = kwargs.copy()
        # Set the ToggleGroup ttk_class - position will be updated by _update_button_positions
        custom_accent = btn_kwargs.pop('accent', None) or self._accent
        btn_kwargs['accent'] = custom_accent
        btn_kwargs['ttk_class'] = 'ToggleGroup'
        if 'state' not in btn_kwargs:
            btn_kwargs['state'] = self._state
        # variant can be None (default), 'outline', or 'ghost' - use group's variant if not specified
        if 'variant' not in btn_kwargs:
            btn_kwargs['variant'] = self._variant
        # Merge orient and initial position into style_options
        existing_style_opts = btn_kwargs.get('style_options', {}).copy()
        existing_style_opts['orient'] = self._orientation
        existing_style_opts.setdefault('position', 'before')  # Default position, will be corrected later
        btn_kwargs['style_options'] = existing_style_opts

        if self._mode == 'single':
            button = RadioToggle(self, text=text, value=value, variable=self.variable, **btn_kwargs)
        else:  # multi
            button = CheckToggle(self, text=text, **btn_kwargs)

            # Set initial state based on current SetVar value
            current_set = self.variable.get()
            if not isinstance(current_set, set):
                current_set = set()
            button.variable.set(value in current_set)

            # Bind command to update SetVar
            # Pop command to avoid double-calling
            original_command = btn_kwargs.pop('command', None)

            def toggle_command():
                self._on_multi_toggle(value)
                if original_command:
                    original_command()

            button.configure(command=toggle_command)

        if self._orientation == 'horizontal':
            button.pack(side='left')
        else:  # vertical
            button.pack(side='top', fill='x')

        self._buttons[key] = button
        self._update_button_positions()
        return button

    def _update_button_positions(self):
        """Update button styles based on their position in the group.

        Note: Relies on dictionary insertion order (Python 3.7+) to maintain
        button order based on when they were added.
        """
        # List conversion maintains insertion order (Python 3.7+)
        button_list = list(self._buttons.values())
        num_buttons = len(button_list)

        if num_buttons == 0:
            return

        for idx, button in enumerate(button_list):
            if num_buttons == 1:
                # Single button - use 'before' position (fully rounded on left/top)
                position = 'before'
            elif idx == 0:
                # First button
                position = 'before'
            elif idx == num_buttons - 1:
                # Last button
                position = 'after'
            else:
                # Middle button
                position = 'center'

            # Update position and rebuild style
            button.configure_style_options(position=position)
            button.rebuild_style()

    def _on_multi_toggle(self, val: str):
        """Callback to update the SetVar when a CheckToggle is clicked."""
        current_set = self.get()
        if val in current_set:
            current_set.remove(val)
        else:
            current_set.add(val)
        self.set(current_set)

    def get(self) -> str | set[str]:
        """Return the current value (string for single mode, set for multi mode)."""
        return self.variable.get()

    def set(self, value: str | set[str]) -> None:
        """Set the value (string for single mode, set for multi mode).

        Args:
            value: The value to set.

        Raises:
            TypeError: If value type doesn't match the mode.
        """
        # Validate value type matches mode
        if self._mode == 'single':
            if not isinstance(value, str):
                raise TypeError(f"Single mode requires a string value, got {type(value).__name__}")
        else:  # multi mode
            if not isinstance(value, set):
                raise TypeError(f"Multi mode requires a set value, got {type(value).__name__}")

        self.variable.set(value)

        # For multi mode, update CheckToggle states to match new value
        if self._mode == 'multi':
            for key, button in self._buttons.items():
                button.variable.set(key in value)

    @property
    def value(self) -> str | set[str]:
        """Get or set the value (string for single mode, set for multi mode)."""
        return self.get()

    @value.setter
    def value(self, value: str | set[str]) -> None:
        self.set(value)

    def text_for(self, value: Any) -> str | None:
        """Return the display text of the option with the given value, or None.

        The selection variable coerces values to strings, so match on the
        stringified key when an exact lookup misses.
        """
        if value is None or value == "":
            return None
        button = self._buttons.get(value)
        if button is None:
            button = next((b for k, b in self._buttons.items() if str(k) == str(value)), None)
        return button.cget('text') if button is not None else None

    def remove(self, key: str):
        """Remove a button by its key."""
        if key in self._buttons:
            button = self._buttons.pop(key)
            button.destroy()
            self._update_button_positions()

    def items(self) -> tuple[RadioToggle | CheckToggle, ...]:
        """Get all button widgets in the group.

        Returns:
            A tuple of all button instances in the group.
        """
        return tuple(self._buttons.values())

    def item(self, key: str) -> RadioToggle | CheckToggle:
        """Get a button by its key.

        Args:
            key: The key of the button to retrieve.

        Returns:
            The button instance.

        Raises:
            KeyError: If no button with the given key exists.
        """
        if key not in self._buttons:
            raise KeyError(f"No button with key '{key}'")
        return self._buttons[key]

    def configure_item(self, key: str, option: str = None, **kwargs: Any):
        """Configure a specific button by its key.

        Args:
            key: The key of the button to configure.
            option: If provided, return the value of this option.
            **kwargs: Configuration options to apply to the button.

        Returns:
            If option is provided, returns the value of that option.
        """
        button = self.item(key)
        if option is not None:
            return button.cget(option)
        button.configure(**kwargs)

    def keys(self) -> tuple[str, ...]:
        """Get all button keys.

        Returns:
            A tuple of all button keys in the group.
        """
        return tuple(self._buttons.keys())

    def on_changed(self, callback: Callable) -> Any:
        """Subscribe to value changes.

        Args:
            callback: Called when the selection changes. Receives the new value
                directly (not a Tk event object): `str` in single mode,
                `set[str]` in multi mode.

        Returns:
            Subscription ID — pass to `off_changed()` to unsubscribe.
        """
        return self._signal.subscribe(callback)

    def off_changed(self, bind_id: Any) -> None:
        """Cancel a subscription created by `on_changed()`.

        Args:
            bind_id: The handle returned by `on_changed()`.
        """
        if bind_id is not None:
            bind_id.cancel()

    @configure_delegate('accent')
    def _delegate_accent(self, value=None):
        """Get or set the accent. Updates all buttons when changed."""
        if value is None:
            return self._accent

        self._accent = value
        # Update all buttons with new accent
        self._update_button_positions()

    @configure_delegate('orient')
    def _delegate_orient(self, value=None):
        """Get or set orientation ('horizontal' or 'vertical'). Repacks buttons when changed."""
        if value is None:
            return self._orientation

        if value not in ('horizontal', 'vertical'):
            raise ValueError("orient must be 'horizontal' or 'vertical'")

        self._orientation = value

        # Repack all buttons in new orientation
        for button in self._buttons.values():
            button.pack_forget()
            button.configure_style_options(orient=value)
            if self._orientation == 'horizontal':
                button.pack(side='left')
            else:
                button.pack(side='top', fill='x')

        # Update button styles with new orientation
        self._update_button_positions()

    @configure_delegate('value')
    def _delegate_value(self, value=None):
        """Get or set the value via configure."""
        if value is None:
            return self.get()
        self.set(value)
