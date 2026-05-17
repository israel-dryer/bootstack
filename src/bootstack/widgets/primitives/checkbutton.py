from __future__ import annotations

from tkinter import ttk
from typing import Any, Callable, Literal, TYPE_CHECKING

from typing_extensions import Unpack

from bootstack._core.mixins.ttk_state import TtkStateMixin
from bootstack._core.mixins.widget import WidgetCapabilitiesMixin
from bootstack.widgets._internal.wrapper_base import TTKWrapperBase
from bootstack.widgets.mixins import IconMixin, LocalizationMixin, SignalMixin, TextSignalMixin
from bootstack.widgets.mixins.configure_mixin import configure_delegate
from bootstack.widgets.types import Master, StyledKwargs, Anchor, CompoundMode, WidgetState

if TYPE_CHECKING:
    from bootstack.signals import Signal


class CheckButtonKwargs(StyledKwargs, total=False):
    # Standard ttk.Checkbutton options
    text: Any
    command: Callable[[], Any] | None
    image: Any
    icon: Any
    on_icon: Any
    off_icon: Any
    icon_only: bool
    show_indicator: bool
    compound: CompoundMode
    variable: Any
    signal: Signal[Any]
    value: Any
    onvalue: Any
    offvalue: Any
    padding: Any
    anchor: Anchor
    width: int
    underline: int
    state: WidgetState
    textvariable: Any
    textsignal: Signal[str]

    # bootstack-specific extensions
    localize: bool | Literal['auto']


class CheckButton(LocalizationMixin, SignalMixin, TextSignalMixin, IconMixin, TTKWrapperBase, WidgetCapabilitiesMixin, TtkStateMixin, ttk.Checkbutton):
    """bootstack wrapper for `ttk.Checkbutton` with themed styling and icon support."""

    _ttk_base = ttk.Checkbutton

    def __init__(self, master: Master = None, **kwargs: Unpack[CheckButtonKwargs]) -> None:
        """Create a themed bootstack Checkbutton.

        Args:
            master: Parent widget. If None, uses the default root window.

        Other Parameters:
            text: Text to display.
            textvariable: Tk variable linked to the text.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            textsignal: Reactive Signal linked to the text (auto-synced with textvariable).
            command: Callable invoked when the value toggles.
            image: Image to display.
            icon: Icon shown in the label area for all states. Color shifts
                from foreground (unselected) to accent (selected) automatically.
            on_icon: Icon shown in the label area when the button is selected.
                Shortcut for `state=[("selected", name)]` inside a full icon spec.
            off_icon: Icon shown in the label area when the button is unselected.
                Used as the base icon when `on_icon` is also provided.
            icon_only: If True, removes the additional padding reserved for text.
            show_indicator: Whether to show the standard checkbox indicator. Defaults
                to True. Set to False to hide the indicator (e.g. when using icons alone).
            compound: Placement of the image relative to text.
            variable: Linked variable controlling the on/off state.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            localize: Determines the widget's localization mode.
            signal: Reactive Signal controlling the on/off state (auto-synced with variable).
            value: Initial state for the widget's associated variable (defaults to None when unset).
            onvalue: Value set in `variable` when selected.
            offvalue: Value set in `variable` when deselected.
            padding: Extra space around the content.
            anchor: Determines how the content is aligned in the container. Combination of 'n', 's', 'e', 'w', or 'center' (default).
            width: Width of the control in characters.
            underline: Index of character to underline in `text`.
            state: Widget state.
            takefocus: Whether the widget participates in focus traversal.
            style: Explicit ttk style name (overrides accent/variant).
            accent: Accent token for styling, e.g. 'primary', 'success', 'danger'.
            variant: Style variant, e.g. 'default', 'round', 'square'.
            surface: Optional surface token; otherwise inherited.
            style_options: Optional dict forwarded to the style builder.
        """
        signal_provided = 'signal' in kwargs
        variable_provided = 'variable' in kwargs
        initial_value = kwargs.pop('value', None)
        kwargs.update(style_options=self._capture_style_options(['icon_only', 'icon', 'on_icon', 'off_icon', 'show_indicator', 'anchor'], kwargs))
        super().__init__(master, **kwargs)
        if initial_value is not None and not signal_provided and not variable_provided:
            self.variable.set(initial_value)

    def get(self) -> Any:
        """Return the current value of the checkbutton."""
        return self.variable.get()

    def set(self, value: Any) -> None:
        """Set the value of the checkbutton."""
        self.variable.set(value)

    @property
    def value(self) -> Any:
        """Get or set the checkbutton's value."""
        return self.get()

    @value.setter
    def value(self, value: Any) -> None:
        self.set(value)

    @configure_delegate('value')
    def _delegate_value(self, value=None):
        """Get or set the value via configure."""
        if value is None:
            return self.get()
        self.set(value)
