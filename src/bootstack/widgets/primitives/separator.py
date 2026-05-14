from __future__ import annotations

from tkinter import ttk
from typing import Any, TypedDict
from typing_extensions import Unpack

from bootstack.core.mixins.ttk_state import TtkStateMixin
from bootstack.core.mixins.widget import WidgetCapabilitiesMixin
from bootstack.widgets.internal.wrapper_base import TTKWrapperBase
from bootstack.widgets.types import Master


class SeparatorKwargs(TypedDict, total=False):
    # Standard ttk.Separator options
    orient: Any
    style: str
    class_: str
    cursor: str
    name: str

    # bootstack-specific extensions
    accent: str
    surface: str
    thickness: int
    length: int
    style_options: dict[str, Any]


class Separator(TTKWrapperBase, WidgetCapabilitiesMixin, TtkStateMixin, ttk.Separator):
    """bootstack wrapper for `ttk.Separator` with bootstyle support."""

    _ttk_base = ttk.Separator

    def __init__(self, master: Master = None, **kwargs: Unpack[SeparatorKwargs]) -> None:
        """Create a themed bootstack Separator.

        Args:
            master: Parent widget. If None, uses the default root window.

        Other Parameters:
            orient (str): Orientation of the separator ('horizontal' or 'vertical').
            style (str): Explicit ttk style name (overrides accent/variant).
            accent (str): Accent token for styling, e.g. 'primary', 'secondary' otherwise derived from inherited surface.
                Combined style tokens.
            surface (str): Optional surface token; otherwise inherited.
            thickness (int): Thickness of the separator.
            length (int): Fixed length of the separator in pixels. If None,
                stretches to fill available space.
            style_options (dict): Optional dict forwarded to the style builder.
        """
        kwargs.update(style_options=self._capture_style_options(['thickness', 'length'], kwargs))
        super().__init__(master, **kwargs)


