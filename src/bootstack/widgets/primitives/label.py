from __future__ import annotations

from tkinter import ttk
from typing import Any, Literal, TYPE_CHECKING, TypedDict

from typing_extensions import Unpack

from bootstack.core.mixins.ttk_state import TtkStateMixin
from bootstack.core.mixins.widget import WidgetCapabilitiesMixin
from bootstack.widgets._internal.wrapper_base import TTKWrapperBase
from bootstack.widgets.mixins import IconMixin, LocalizationMixin, TextSignalMixin
from bootstack.widgets.types import Master

if TYPE_CHECKING:
    from bootstack.core.signals import Signal


class LabelKwargs(TypedDict, total=False):
    # Standard ttk.Label options
    text: Any
    image: Any
    icon: Any
    icon_only: bool
    compound: Literal['text', 'image', 'top', 'bottom', 'left', 'right', 'center', 'none'] | str
    anchor: Any
    justify: Any
    padding: Any
    width: int
    wraplength: Any
    font: Any
    foreground: str
    background: str
    relief: Any
    localize: bool | Literal['auto']
    value_format: dict | str
    state: Literal['normal', 'active', 'disabled', 'readonly'] | str
    takefocus: Any
    format_spec: str | dict
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


class Label(LocalizationMixin, TextSignalMixin, IconMixin, TTKWrapperBase, WidgetCapabilitiesMixin, TtkStateMixin, ttk.Label):
    """bootstack wrapper for `ttk.Label` with themed styling and icon support."""

    _ttk_base = ttk.Label

    def __init__(self, master: Master = None, **kwargs: Unpack[LabelKwargs]) -> None:
        """Create a themed bootstack Label.

        Args:
            master: Parent widget. If None, uses the default root window.

        Other Parameters:
            text: Text to display in the label.
            textvariable: Tk variable linked to the label text.
            textsignal: Reactive Signal linked to the label text (auto-synced with textvariable).
            image: Image to display.
            icon: Theme-aware icon spec handled by the style system.
            icon_only: If True, removes the additional padding reserved for label text.
            compound: Placement of the image relative to text.
            anchor: Alignment of the label's content within its area.
            justify: How to justify multiple lines of text.
            localize: Determines the widget's localization mode.
            value_format: Format specification for the label value.
            padding: Extra space around the label content.
            width: Width of the label in characters.
            wraplength: Maximum width before wrapping text.
            font: Font for text.
            foreground: Text color.
            background: Background color.
            relief: Border style.
            state: Widget state.
            takefocus: Whether the widget participates in focus traversal.
            style: Explicit ttk style name (overrides accent/variant).
            accent: Accent token for styling, e.g. 'primary', 'danger', 'success'.
            variant: Style variant, e.g. 'default', 'inverse'.
            surface: Optional surface token; otherwise inherited.
            style_options: Optional dict forwarded to the style builder.
        """
        kwargs.update(style_options=self._capture_style_options(['icon_only', 'icon', 'density'], kwargs))
        super().__init__(master, **kwargs)
