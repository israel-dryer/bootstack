from __future__ import annotations

from tkinter import ttk
from typing import Any, TypedDict
from typing_extensions import Unpack

from bootstack.core.mixins.ttk_state import TtkStateMixin
from bootstack.core.mixins.widget import WidgetCapabilitiesMixin
from bootstack.widgets.internal.wrapper_base import TTKWrapperBase
from bootstack.widgets.types import Master


class SizeGripKwargs(TypedDict, total=False):
    # Standard ttk.Sizegrip options
    style: str
    class_: str
    cursor: str
    name: str

    # bootstack-specific extensions
    bootstyle: str  # DEPRECATED: Use accent and variant instead
    accent: str
    surface: str
    style_options: dict[str, Any]


class SizeGrip(TTKWrapperBase, WidgetCapabilitiesMixin, TtkStateMixin, ttk.Sizegrip):
    """bootstack wrapper for `ttk.Sizegrip` with bootstyle support."""

    _ttk_base = ttk.Sizegrip

    def __init__(self, master: Master = None, **kwargs: Unpack[SizeGripKwargs]) -> None:
        """Create a themed bootstack Sizegrip.

        Args:
            master: Parent widget. If None, uses the default root window.

        Other Parameters:
            style (str): Explicit ttk style name (overrides accent/variant).
            accent (str): Accent token for styling.
            bootstyle (str): DEPRECATED - Use `accent` instead.
            surface (str): Optional surface token; otherwise inherited.
            style_options (dict): Optional dict forwarded to the style builder.
        """
        super().__init__(master, **kwargs)


