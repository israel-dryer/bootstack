from __future__ import annotations

from tkinter import ttk
from typing import Any, Callable, Literal, Optional, TYPE_CHECKING, TypedDict

from typing_extensions import Unpack

from bootstack.core.mixins.ttk_state import TtkStateMixin
from bootstack.core.mixins.widget import WidgetCapabilitiesMixin
from bootstack.widgets.internal.wrapper_base import TTKWrapperBase
from bootstack.widgets.mixins import IconMixin, LocalizationMixin, SignalMixin, TextSignalMixin
from bootstack.widgets.mixins.configure_mixin import configure_delegate
from bootstack.widgets.types import Master

if TYPE_CHECKING:
    from bootstack.core.signals import Signal


class RadioButtonKwargs(TypedDict, total=False):
    # Standard ttk.Radiobutton options
    text: Any
    command: Optional[Callable[[], Any]]
    image: Any
    icon: Any
    on_icon: Any
    off_icon: Any
    icon_only: bool
    show_indicator: bool
    compound: Literal['text', 'image', 'top', 'bottom', 'left', 'right', 'center', 'none'] | str
    variable: Any
    signal: Signal[Any]
    value: Any
    padding: Any
    anchor: str
    width: int
    underline: int
    state: Literal['normal', 'active', 'disabled', 'readonly'] | str
    takefocus: Any
    style: str
    class_: str
    cursor: str
    name: str
    textvariable: Any
    textsignal: Signal[str]

    # bootstack-specific extensions
    accent: str
    variant: str
    surface: str
    style_options: dict[str, Any]
    localize: bool | Literal['auto']


class RadioButton(LocalizationMixin, SignalMixin, TextSignalMixin, IconMixin, TTKWrapperBase, WidgetCapabilitiesMixin, TtkStateMixin, ttk.Radiobutton):
    """bootstack wrapper for `ttk.Radiobutton` with bootstyle and icon support."""

    _ttk_base = ttk.Radiobutton

    def __init__(self, master: Master = None, **kwargs: Unpack[RadioButtonKwargs]) -> None:
        """Create a themed bootstack Radiobutton.

        Args:
            master: Parent widget. If None, uses the default root window.

        Other Parameters:
            text (str): Text to display.
            textvariable (Variable): Tk variable linked to the text.
            textsignal (Signal[str]): Reactive Signal linked to the text (auto-synced with textvariable).
            command (Callable): Callable invoked when the value is selected.
            image (PhotoImage): Image to display.
            icon (str | dict): Icon shown in the label area for all states. Color shifts
                from foreground (unselected) to accent (selected) automatically.
            on_icon (str | dict): Icon shown in the label area when the button is selected.
                Shortcut for `state=[("selected", name)]` inside a full icon spec.
            off_icon (str | dict): Icon shown in the label area when the button is unselected.
                Used as the base icon when `on_icon` is also provided.
            icon_only (bool): Removes the additional padding added for label.
            show_indicator (bool): Whether to show the standard radio indicator. Defaults
                to True. Set to False to hide the indicator (e.g. for icon-only radio groups).
            compound (str): Placement of the image relative to text.
            variable (Variable): Linked Tk variable that receives the selected value.
            signal (Signal): Reactive Signal that receives the selected value (auto-synced with variable).
            value (Any): The value assigned to `variable` when this radio is selected.
            padding (int | tuple): Extra space around the content.
            anchor (str): Determines how the content is aligned in the container. Combination of 'n', 's', 'e', 'w', or 'center' (default).
            width (int): Width of the control in characters.
            underline (int): Index of character to underline in `text`.
            state (str): Widget state.
            takefocus (bool): Whether the widget participates in focus traversal.
            style (str): Explicit ttk style name (overrides accent/variant).
            accent (str): Accent token for styling, e.g. 'primary', 'success', 'danger'.
            variant (str): Style variant, e.g. 'default'.
                Combined style tokens (e.g., 'primary', 'success').
            surface (str): Optional surface token; otherwise inherited.
            style_options (dict): Optional dict forwarded to the style builder.
            localize (bool | Literal['auto']): Determines the widget's localization mode.
        """
        kwargs.update(style_options=self._capture_style_options(['icon_only', 'icon', 'on_icon', 'off_icon', 'show_indicator', 'anchor'], kwargs))
        super().__init__(master, **kwargs)

    def get(self) -> Any:
        """Return the current selected value."""
        return self.variable.get()

    def set(self, value: Any) -> None:
        """Set the selected value."""
        self.variable.set(value)

    @property
    def value(self) -> Any:
        """Get or set the radiobutton's selected value."""
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
