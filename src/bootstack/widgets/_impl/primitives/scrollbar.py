from __future__ import annotations

from tkinter import ttk
from typing import Any
from typing_extensions import Unpack

from bootstack._core.mixins.ttk_state import TtkStateMixin
from bootstack._core.mixins.widget import WidgetCapabilitiesMixin
from bootstack.widgets._impl._internal.wrapper_base import TTKWrapperBase
from bootstack.widgets.types import Master, StyledKwargs, Orient


class ScrollbarKwargs(StyledKwargs, total=False):
    # Standard ttk.Scrollbar options
    orient: Orient
    command: Any

    # bootstack-specific extensions


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
