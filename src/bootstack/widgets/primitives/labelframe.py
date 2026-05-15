from __future__ import annotations

from tkinter import ttk
from typing import Any, Literal, TypedDict

from typing_extensions import Unpack

from bootstack.core.mixins.ttk_state import TtkStateMixin
from bootstack.core.mixins.widget import WidgetCapabilitiesMixin
from bootstack.widgets.internal.wrapper_base import TTKWrapperBase
from bootstack.widgets.mixins import LocalizationMixin
from bootstack.widgets.types import Master


class LabelFrameKwargs(TypedDict, total=False):
    # Standard ttk.Labelframe options
    text: Any
    labelanchor: Any
    padding: Any
    relief: Any
    borderwidth: Any
    width: int
    height: int
    style: str
    class_: str
    cursor: str
    name: str

    # bootstack-specific extensions
    accent: str
    surface: str
    style_options: dict[str, Any]
    localize: bool | Literal['auto']


class LabelFrame(LocalizationMixin, TTKWrapperBase, WidgetCapabilitiesMixin, TtkStateMixin, ttk.LabelFrame):
    """bootstack wrapper for `ttk.Labelframe` with themed styling support."""

    _ttk_base = ttk.Labelframe

    def __init__(self, master: Master = None, **kwargs: Unpack[LabelFrameKwargs]) -> None:
        """Create a themed bootstack Labelframe.

        Args:
            master: Parent widget. If None, uses the default root window.

        Other Parameters:
            text: Text for the embedded label.
            labelanchor: Position of the label relative to the frame.
            padding: Extra internal padding.
            relief: Border style.
            borderwidth: Border width.
            width: Requested width in pixels.
            height: Requested height in pixels.
            style: Explicit ttk style name (overrides accent/variant).
            accent: Accent token for styling, e.g. 'primary', 'secondary'.
            surface: Optional surface token; otherwise inherited.
            style_options: Optional dict forwarded to the style builder.
            localize: Determines the widget's localization mode.
        """
        super().__init__(master, **kwargs)
