"""Common type aliases and base TypedDicts for bootstack widgets."""

import tkinter
from typing import Any, Callable, Literal, TypedDict

# ---------------------------------------------------------------------------
# Primitive aliases
# ---------------------------------------------------------------------------

Master = tkinter.Misc | None
"""Parent widget. Pass any tkinter widget or `None` to use the default root window."""

EventCallback = Callable[[tkinter.Event], None]
"""Callback that receives a Tkinter `Event` object."""

CommandCallback = Callable[[], Any]
"""Callback invoked with no arguments, e.g. a button `command=`."""

# ---------------------------------------------------------------------------
# Tkinter geometry / layout literals
# ---------------------------------------------------------------------------

Anchor = Literal['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'center']
"""Standard Tkinter anchor positions."""

Orient = Literal['horizontal', 'vertical']
"""Widget orientation."""

Justify = Literal['left', 'center', 'right']
"""Text justification within a widget."""

Relief = Literal['flat', 'raised', 'sunken', 'groove', 'ridge', 'solid']
"""Border relief style."""

CompoundMode = Literal['text', 'image', 'top', 'bottom', 'left', 'right', 'center', 'none']
"""Relative position of image to text when both are displayed."""

# ---------------------------------------------------------------------------
# Widget state
# ---------------------------------------------------------------------------

WidgetState = Literal['normal', 'active', 'disabled', 'readonly']
"""Widget interaction state."""

WidgetDensity = Literal['default', 'compact']
"""Widget density — `'default'` for normal sizing, `'compact'` for reduced padding."""

# ---------------------------------------------------------------------------
# bootstack styling tokens
# ---------------------------------------------------------------------------

AccentToken = Literal['primary', 'secondary', 'success', 'warning', 'danger', 'info', 'light', 'dark']
"""Semantic color accent token. Accepts modifiers: `'primary[+1]'`, `'primary[500]'`, `'primary[subtle]'`."""

VariantToken = Literal['solid', 'outline', 'ghost', 'link', 'toggle']
"""Widget style variant."""

SurfaceToken = Literal['content', 'card', 'chrome', 'overlay', 'input']
"""Background surface context token."""

# ---------------------------------------------------------------------------
# Base TypedDicts
# ---------------------------------------------------------------------------

class BaseWidgetKwargs(TypedDict, total=False):
    """Tkinter-level options shared by all bootstack widget wrappers."""
    style: str
    class_: str
    cursor: str
    name: str
    takefocus: bool


class StyledKwargs(BaseWidgetKwargs, total=False):
    """Extends BaseWidgetKwargs with bootstack styling tokens."""
    accent: AccentToken | str
    variant: VariantToken | str
    surface: SurfaceToken | str
    style_options: dict[str, Any]
