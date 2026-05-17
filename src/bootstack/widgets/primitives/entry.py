from __future__ import annotations

from tkinter import ttk
from typing import Any, Literal, Optional, TYPE_CHECKING
from typing_extensions import Unpack

from bootstack._core.mixins.ttk_state import TtkStateMixin
from bootstack._core.mixins.widget import WidgetCapabilitiesMixin
from bootstack.widgets._internal.wrapper_base import TTKWrapperBase
from bootstack.widgets.types import Master, StyledKwargs, Justify, WidgetState, WidgetDensity
from ..mixins import TextSignalMixin, configure_delegate

if TYPE_CHECKING:
    from bootstack.signals import Signal


class EntryKwargs(StyledKwargs, total=False):
    # Standard ttk.Entry options
    textvariable: Any
    textsignal: Signal[str]
    show: Any
    width: int
    exportselection: bool
    justify: Justify
    validate: Any
    validatecommand: Any
    invalidcommand: Any
    xscrollcommand: Any
    font: Any
    foreground: str
    background: str
    state: WidgetState

    # bootstack-specific extensions
    density: WidgetDensity


class Entry(TextSignalMixin, TTKWrapperBase, WidgetCapabilitiesMixin, TtkStateMixin, ttk.Entry):
    """bootstack wrapper for `ttk.Entry` with themed styling support."""

    _ttk_base = ttk.Entry

    def __init__(self, master: Master = None, **kwargs: Unpack[EntryKwargs]) -> None:
        """Create a themed bootstack Entry.

        Args:
            master: Parent widget. If None, uses the default root window.

        Other Parameters:
            textvariable: Tk variable linked to the entry text.
            textsignal: Reactive Signal linked to the entry text (auto-synced with textvariable).
            show: Substitute character for masked input.
            width: Width in characters.
            exportselection: Whether selection is exported to X clipboard.
            justify: Text alignment inside the entry.
            validate: Validation mode.
            validatecommand: Validation callback.
            invalidcommand: Callback executed on validation failure.
            xscrollcommand: Horizontal scroll callback.
            font: Font for the entry text.
            foreground: Text color.
            background: Background color.
            state: Widget state.
            takefocus: Whether the widget participates in focus traversal.
            style: Explicit ttk style name (overrides accent/variant).
            accent: Accent token for styling, e.g. 'primary', 'danger', 'success'.
            variant: Style variant, e.g. 'default'.
            density: Vertical and horizontal compactness, e.g. 'default', 'compact'.
            surface: Optional surface token; otherwise inherited.
            style_options: Optional dict forwarded to the style builder.
        """
        if kwargs.get('density') == 'compact':
            kwargs['font'] = 'caption'
        kwargs.update(style_options=self._capture_style_options(['density'], kwargs))
        super().__init__(master, **kwargs)

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
