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

AccentToken = Literal['default', 'primary', 'success', 'warning', 'danger']
"""Semantic color accent token. Accepts modifiers: `'primary[+1]'`, `'primary[500]'`, `'primary[subtle]'`."""

VariantToken = Literal['solid', 'outline', 'ghost', 'toggle']
"""Widget style variant."""

SurfaceToken = Literal['content', 'card', 'chrome', 'overlay', 'input']
"""Background surface context token."""

# ---------------------------------------------------------------------------
# Geometry manager literals
# ---------------------------------------------------------------------------

Fill = Literal['none', 'x', 'y', 'both']
"""Fill axis for the pack geometry manager."""

Sticky = Literal['n', 's', 'e', 'w', 'ns', 'ew', 'nsew', 'ne', 'nw', 'se', 'sw', 'nse', 'nsw', 'new', 'sew', '']
"""Sticky directions for the grid geometry manager."""

Side = Literal['left', 'top', 'right', 'bottom']
"""Side placement for the pack geometry manager."""

Direction = Literal['vertical', 'horizontal', 'row', 'column', 'row-reverse', 'column-reverse']
"""Layout direction for PackFrame and GridFrame."""

BorderMode = Literal['inside', 'outside']
"""Border mode for the place geometry manager."""

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
