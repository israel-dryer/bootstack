from __future__ import annotations

from tkinter import ttk
from typing import Any, Literal, TYPE_CHECKING
from typing_extensions import Unpack

from bootstack._core.mixins.ttk_state import TtkStateMixin
from bootstack._core.mixins.widget import WidgetCapabilitiesMixin
from bootstack.widgets._internal.wrapper_base import TTKWrapperBase
from bootstack.widgets.mixins.configure_mixin import configure_delegate
from bootstack.widgets.types import Master, StyledKwargs, Orient
from ..mixins import SignalMixin

if TYPE_CHECKING:
    from bootstack.signals import Signal


class ProgressbarKwargs(StyledKwargs, total=False):
    # Standard ttk.Progressbar options
    mode: Literal['determinate', 'indeterminate'] | str
    orient: Orient
    length: Any
    maximum: float
    value: float
    variable: Any
    signal: Signal[Any]
    phase: int

    # bootstack-specific extensions


class Progressbar(SignalMixin, TTKWrapperBase, WidgetCapabilitiesMixin, TtkStateMixin, ttk.Progressbar):
    """bootstack wrapper for `ttk.Progressbar` with themed styling support."""

    _ttk_base = ttk.Progressbar

    def __init__(self, master: Master = None, **kwargs: Unpack[ProgressbarKwargs]) -> None:
        """Create a themed bootstack Progressbar.

        Args:
            master: Parent widget. If None, uses the default root window.

        Other Parameters:
            mode: Progress mode ('determinate' or 'indeterminate').
            orient: Orientation of the bar ('horizontal' or 'vertical').
            length: Requested length of the progress bar in pixels.
            maximum: Maximum value.
            value: Current value.
            variable: Tk variable linked to the value.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            signal: Reactive Signal linked to the value (auto-synced with variable).
            phase: Animation phase for indeterminate mode.
            style: Explicit ttk style name (overrides accent/variant).
            accent: Accent token for styling, e.g. 'primary', 'success', 'danger'.
            variant: Style variant, e.g. 'default', 'thin'.
            surface: Optional surface token; otherwise inherited.
            style_options: Optional dict forwarded to the style builder.
        """
        super().__init__(master, **kwargs)

    def get(self) -> float:
        """Return the current progress value."""
        return float(ttk.Progressbar.cget(self, 'value'))

    def set(self, value: float) -> None:
        """Set the progress value."""
        ttk.Progressbar.configure(self, value=value)

    @property
    def value(self) -> float:
        """Get or set the progress value."""
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
