from __future__ import annotations

from tkinter import ttk
from typing import Any, TypedDict
from typing_extensions import Unpack

from bootstack.core.mixins.ttk_state import TtkStateMixin
from bootstack.core.mixins.widget import WidgetCapabilitiesMixin
from bootstack.widgets._internal.wrapper_base import TTKWrapperBase
from bootstack.widgets.types import Master


class ScrollbarKwargs(TypedDict, total=False):
    # Standard ttk.Scrollbar options
    orient: Any
    command: Any
    takefocus: Any
    style: str
    class_: str
    cursor: str
    name: str

    # bootstack-specific extensions
    accent: str
    variant: str
    surface: str
    style_options: dict[str, Any]


class Scrollbar(TTKWrapperBase, WidgetCapabilitiesMixin, TtkStateMixin, ttk.Scrollbar):
    """bootstack wrapper for `ttk.Scrollbar` with themed styling support."""

    _ttk_base = ttk.Scrollbar

    def __init__(self, master: Master = None, **kwargs: Unpack[ScrollbarKwargs]) -> None:
        """Create a themed bootstack Scrollbar.

        Args:
            master: Parent widget. If None, uses the default root window.

        Other Parameters:
            orient: Orientation of the scrollbar ('horizontal' or 'vertical').
            command: Scroll command callback.
            takefocus: Whether the widget participates in focus traversal.
            style: Explicit ttk style name (overrides accent/variant).
            accent: Accent token for styling, e.g. 'primary', 'danger', 'success'.
            variant: Style variant, e.g. 'default', 'round', 'square'.
            surface: Optional surface token; otherwise inherited.
            style_options: Optional dict forwarded to the style builder.
        """
        super().__init__(master, **kwargs)


