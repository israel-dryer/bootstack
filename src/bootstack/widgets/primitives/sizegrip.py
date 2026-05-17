from __future__ import annotations

from tkinter import ttk
from typing import Any, TypedDict
from typing_extensions import Unpack

from bootstack._core.mixins.ttk_state import TtkStateMixin
from bootstack._core.mixins.widget import WidgetCapabilitiesMixin
from bootstack.widgets._internal.wrapper_base import TTKWrapperBase
from bootstack.widgets.types import Master


class SizeGripKwargs(TypedDict, total=False):
    # Standard ttk.Sizegrip options
    style: str
    class_: str
    cursor: str
    name: str

    # bootstack-specific extensions
    accent: str
    surface: str
    style_options: dict[str, Any]


class SizeGrip(TTKWrapperBase, WidgetCapabilitiesMixin, TtkStateMixin, ttk.Sizegrip):
    """bootstack wrapper for `ttk.Sizegrip` with themed styling support."""

    _ttk_base = ttk.Sizegrip

    def __init__(self, master: Master = None, **kwargs: Unpack[SizeGripKwargs]) -> None:
        """Create a themed bootstack Sizegrip.

        Args:
            master: Parent widget. If None, uses the default root window.

        Other Parameters:
            style: Explicit ttk style name (overrides accent/variant).
            accent: Accent token for styling.
            surface: Optional surface token; otherwise inherited.
            style_options: Optional dict forwarded to the style builder.
        """
        super().__init__(master, **kwargs)


