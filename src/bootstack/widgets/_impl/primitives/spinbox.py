from __future__ import annotations

from tkinter import ttk
from typing import Any, TYPE_CHECKING
from typing_extensions import Unpack

from bootstack._runtime import wheel
from bootstack._core.mixins.ttk_state import TtkStateMixin
from bootstack._core.mixins.widget import WidgetCapabilitiesMixin
from bootstack.widgets._impl._internal.wrapper_base import TTKWrapperBase
from bootstack.widgets.types import Master, StyledKwargs, WidgetState, WidgetDensity
from ..mixins import TextSignalMixin, configure_delegate

if TYPE_CHECKING:
    from bootstack.signals import Signal

_TOUCHPAD_STEP_PX = 40
"""Trackpad travel, in pixels, that advances a stepper by one increment."""


class SpinboxKwargs(StyledKwargs, total=False):
    # Standard ttk.Spinbox options
    from_: float
    to: float
    increment: float
    values: Any
    wrap: bool
    command: Any
    font: Any
    textvariable: Any
    textsignal: Signal[Any]
    format: str
    width: int
    state: WidgetState

    # bootstack-specific extensions
    density: WidgetDensity


class Spinbox(TextSignalMixin, TTKWrapperBase, WidgetCapabilitiesMixin, TtkStateMixin, ttk.Spinbox):
    """bootstack wrapper for `ttk.Spinbox` with themed styling support."""

    _ttk_base = ttk.Spinbox

    def __init__(self, master: Master = None, **kwargs: Unpack[SpinboxKwargs]) -> None:
        """Create a themed bootstack Spinbox.

        Args:
            master: Parent widget. If None, uses the default root window.

        Other Parameters:
            from_: Minimum value.
            to: Maximum value.
            increment: Step size between values.
            values: Sequence of values to cycle through.
            wrap: Whether to wrap between min/max.
            command: Callback when the value changes.
            textvariable: Tk variable linked to the entry text.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            textsignal: Reactive Signal linked to the text (auto-synced with textvariable).
            format: Display format string.
            width: Widget width in characters.
            state: Widget state.
            takefocus: Whether the widget participates in focus traversal.
            style: Explicit ttk style name (overrides accent/variant).
            accent: Accent token for styling, e.g. 'primary', 'danger', 'success'.
            density: Vertical and horizontal compactness, e.g. 'default', 'compact'.
            surface: Optional surface token; otherwise inherited.
            style_options: Optional dict forwarded to the style builder.
        """
        if kwargs.get('density') == 'compact':
            kwargs['font'] = 'caption'
        kwargs.update(style_options=self._capture_style_options(['density'], kwargs))
        super().__init__(master, **kwargs)
        # Handle mousewheel explicitly so we can return "break" and stop the
        # event from leaking to parent scroll containers. Instance bindings run
        # before class bindings in Tk's chain, so we must do the spin ourselves.
        for seq in wheel.wheel_sequences(self):
            self.bind(seq, self._on_mousewheel)
        if wheel.has_touchpad_scroll():
            self._touchpad = wheel.PixelAccumulator()
            self.bind(wheel.TOUCHPAD_SCROLL, self._on_touchpad_scroll)

    def _on_mousewheel(self, event):
        notches = wheel.wheel_notches(self, event)
        if notches:
            self.event_generate("<Up>" if notches > 0 else "<Down>")
        return "break"

    def _on_touchpad_scroll(self, event):
        """Step once per `_TOUCHPAD_STEP_PX` of trackpad travel.

        A trackpad reports around sixty events a second; stepping on each
        one would run the value away from the user.
        """
        _dx, dy = wheel.precise_deltas(event)
        _sx, steps = self._touchpad.add(0, dy, 1, _TOUCHPAD_STEP_PX)
        for _ in range(abs(steps)):
            self.event_generate("<Up>" if steps > 0 else "<Down>")
        return "break"


    @configure_delegate('density')
    def _delegate_density(self, value=None):
        if value is None:
            return self.configure_style_options(value)
        else:
            if value == 'compact':
                self.configure(font='caption')
            else:
                self.configure(font='body')
            return self.configure_style_options(density=value)