from __future__ import annotations

from tkinter import ttk
from typing import Any, Literal, TypedDict, TYPE_CHECKING
from typing_extensions import Unpack

from bootstack.core.mixins.ttk_state import TtkStateMixin
from bootstack.core.mixins.widget import WidgetCapabilitiesMixin
from bootstack.widgets._internal.wrapper_base import TTKWrapperBase
from bootstack.widgets.mixins.configure_mixin import configure_delegate
from bootstack.widgets.types import Master
from ..mixins import SignalMixin

if TYPE_CHECKING:
    from bootstack.core.signals import Signal


class ProgressbarKwargs(TypedDict, total=False):
    # Standard ttk.Progressbar options
    mode: Literal['determinate', 'indeterminate'] | str
    orient: Any
    length: Any
    maximum: float
    value: float
    variable: Any
    signal: Signal[Any]
    phase: int
    style: str
    class_: str
    cursor: str
    name: str

    # bootstack-specific extensions
    accent: str
    variant: str
    surface: str
    style_options: dict[str, Any]


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
            signal: Reactive Signal linked to the value (auto-synced with variable).
            phase: Animation phase for indeterminate mode.
            style: Explicit ttk style name (overrides accent/variant).
            accent: Accent token for styling, e.g. 'primary', 'success', 'danger'.
            variant: Style variant, e.g. 'default', 'striped', 'thin'.
            surface: Optional surface token; otherwise inherited.
            style_options: Optional dict forwarded to the style builder.
        """
        super().__init__(master, **kwargs)

    def get(self) -> float:
        """Return the current progress value."""
        return self.cget('value')

    def set(self, value: float) -> None:
        """Set the progress value."""
        self.configure(value=value)

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


