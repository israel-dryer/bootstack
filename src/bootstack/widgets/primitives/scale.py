from __future__ import annotations

from tkinter import ttk
from typing import Any, TYPE_CHECKING
from typing_extensions import Unpack

from bootstack._core.mixins.ttk_state import TtkStateMixin
from bootstack._core.mixins.widget import WidgetCapabilitiesMixin
from bootstack.widgets._internal.wrapper_base import TTKWrapperBase
from bootstack.widgets.mixins.configure_mixin import configure_delegate
from bootstack.widgets.types import Master, StyledKwargs, Orient
from ..mixins import SignalMixin

if TYPE_CHECKING:
    from bootstack.signals import Signal


class ScaleKwargs(StyledKwargs, total=False):
    # Standard ttk.Scale options
    from_: float
    to: float
    value: float
    variable: Any
    signal: Signal[Any]
    orient: Orient
    length: Any
    command: Any

    # bootstack-specific extensions


class Scale(SignalMixin, TTKWrapperBase, WidgetCapabilitiesMixin, TtkStateMixin, ttk.Scale):
    """bootstack wrapper for `ttk.Scale` with themed styling support."""

    _ttk_base = ttk.Scale

    def __init__(self, master: Master = None, **kwargs: Unpack[ScaleKwargs]) -> None:
        """Create a themed bootstack Scale.

        Args:
            master: Parent widget. If None, uses the default root window.

        Other Parameters:
            from_: Minimum value.
            to: Maximum value.
            value: Initial value.
            variable: Tk variable linked to the value.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            signal: Reactive Signal linked to the value (auto-synced with variable).
            orient: Orientation of the scale ('horizontal' or 'vertical').
            length: Scale length in pixels.
            command: Callback on value change.
            takefocus: Whether the widget participates in focus traversal.
            accent: Accent token for styling, e.g. 'primary', 'success', 'danger'.
            surface: Optional surface token; otherwise inherited.
            style_options: Optional dict forwarded to the style builder.
        """
        super().__init__(master, **kwargs)

    @property
    def value(self) -> float:
        """Get or set the scale's current value."""
        return self.get()

    @value.setter
    def value(self, value: float) -> None:
        self.set(value)

    @configure_delegate('value')
    def _delegate_value(self, value=None):
        """Get or set the value via configure."""
        if value is None:
            return self.get()
        self.set(value)
