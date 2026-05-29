from __future__ import annotations

from tkinter import ttk
from typing import Any
from typing_extensions import Unpack

from bootstack._core.mixins.ttk_state import TtkStateMixin
from bootstack._core.mixins.widget import WidgetCapabilitiesMixin
from bootstack.widgets._impl._internal.wrapper_base import TTKWrapperBase
from bootstack.widgets.types import Master, StyledKwargs, Orient


class PanedWindowKwargs(StyledKwargs, total=False):
    # Standard ttk.Panedwindow options
    orient: Orient
    padding: Any
    width: int
    height: int

    # bootstack-specific extensions


class PanedWindow(TTKWrapperBase, WidgetCapabilitiesMixin, TtkStateMixin, ttk.PanedWindow):
    """bootstack wrapper for `ttk.Panedwindow` with themed styling support."""

    _ttk_base = ttk.Panedwindow

    def __init__(self, master: Master = None, **kwargs: Unpack[PanedWindowKwargs]) -> None:
        """Create a themed bootstack Panedwindow.

        Args:
            master: Parent widget. If None, uses the default root window.

        Other Parameters:
            orient: Orientation of panes ('horizontal' or 'vertical').
            padding: Extra internal padding.
            width: Requested width in pixels.
            height: Requested height in pixels.
            style: Explicit ttk style name (overrides accent/variant).
            accent: Accent token for styling, e.g. 'primary', 'secondary'.
            variant: Style variant (if applicable).
            surface: Optional surface token; otherwise inherited.
            style_options: Optional dict forwarded to the style builder.
        """
        super().__init__(master, **kwargs)
