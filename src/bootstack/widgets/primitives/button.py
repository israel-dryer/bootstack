from __future__ import annotations

from tkinter import ttk
from typing import Any, Callable, Literal, Optional, TypedDict, TYPE_CHECKING
from typing_extensions import Unpack

from bootstack.core.mixins.ttk_state import TtkStateMixin
from bootstack.core.mixins.widget import WidgetCapabilitiesMixin
from bootstack.widgets.internal.wrapper_base import TTKWrapperBase
from bootstack.widgets.mixins import IconMixin, TextSignalMixin, LocalizationMixin
from bootstack.widgets.types import Master

if TYPE_CHECKING:
    from bootstack.core.signals import Signal


class ButtonKwargs(TypedDict, total=False):
    # Standard ttk.Button options
    text: Any
    command: Optional[Callable[[], Any]]
    image: Any
    icon: Any
    icon_only: bool
    anchor: str
    compound: Literal['text', 'image', 'top', 'bottom', 'left', 'right', 'center', 'none'] | str
    padding: Any
    width: int
    underline: int
    state: Literal['normal', 'active', 'disabled', 'readonly'] | str
    takefocus: Any
    localize: bool | Literal['auto']
    style: str
    class_: str
    cursor: str
    default: Any
    name: str
    textvariable: Any
    textsignal: Signal[str]

    # bootstack-specific extensions
    accent: str
    density: Literal['default', 'compact']
    variant: str
    surface: str
    style_options: dict[str, Any]


class Button(LocalizationMixin, TextSignalMixin, IconMixin, TTKWrapperBase, WidgetCapabilitiesMixin, TtkStateMixin, ttk.Button):
    """bootstack wrapper for `ttk.Button` with themed styling and icon support.
    """
    _ttk_base = ttk.Button

    def __init__(self, master: Master = None, **kwargs: Unpack[ButtonKwargs]) -> None:
        """Create a themed bootstack Button.

        Args:
            master: Parent widget. If None, uses the default root window.

        Other Parameters:
            text: Text to display on the button.
            textvariable: Tk variable linked to the button text.
            textsignal: Reactive Signal linked to the button text (auto-synced with textvariable).
            command: Callable invoked when the button is pressed.
            image: Image to display on the button.
            icon: Optional icon spec integrated via the style system.
            icon_only: If true, removes the extra padding reserved for the text labels.
            compound: Placement of the image relative to text (e.g., 'left').
            padding: Extra space around the button content.
            anchor: Determines how the content is aligned in the container. Combination of 'n', 's', 'e', 'w', or 'center' (default).
            localize: Determines the widgets localization mode.
            width: Width of the button in characters.
            underline: Index of the character to underline in `text`.
            state: Widget state — 'normal', 'active', 'disabled', or 'readonly'.
            takefocus: Whether the widget accepts focus during traversal.
            style: Explicit ttk style name to apply (overrides accent/variant).
            accent: Accent token for styling, e.g. 'primary', 'danger', 'success'.
            variant: Style variant, e.g. 'solid', 'outline', 'link', 'text'. Defaults to 'solid'.
            density: Widget density — 'default' or 'compact'.
            surface: Optional surface token to use for this button; if not provided, surface color is inherited from the parent.
            style_options: Optional dict forwarded to the style builder.
        """
        kwargs.setdefault('variant', 'solid')
        kwargs.update(style_options=self._capture_style_options(['icon_only', 'icon', 'anchor', 'density'], kwargs))
        super().__init__(master, **kwargs)
