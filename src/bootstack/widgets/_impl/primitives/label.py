from __future__ import annotations

from tkinter import ttk
from typing import Any, Literal, TYPE_CHECKING

from typing_extensions import Unpack

from bootstack._core.mixins.ttk_state import TtkStateMixin
from bootstack._core.mixins.widget import WidgetCapabilitiesMixin
from bootstack.widgets._impl._internal.wrapper_base import TTKWrapperBase
from bootstack.widgets._impl.mixins import IconMixin, LocalizationMixin, TextSignalMixin
from bootstack.widgets.types import Master, StyledKwargs, Anchor, Justify, Relief, CompoundMode, WidgetState

if TYPE_CHECKING:
    from bootstack.signals import Signal


class LabelKwargs(StyledKwargs, total=False):
    # Standard ttk.Label options
    text: Any
    image: Any
    icon: Any
    icon_only: bool
    compound: CompoundMode
    anchor: Anchor
    justify: Justify
    padding: Any
    width: int
    wraplength: Any
    font: Any
    foreground: str
    background: str
    relief: Relief
    localize: bool | Literal['auto']
    value_format: dict | str
    state: WidgetState
    format_spec: str | dict
    textvariable: Any
    textsignal: Signal[str]

    # bootstack-specific extensions


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
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
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
