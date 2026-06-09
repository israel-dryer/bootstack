"""Common type aliases and base TypedDicts for bootstack widgets."""

import tkinter
from typing import Any, Callable, Literal, TypedDict

# ---------------------------------------------------------------------------
# Primitive aliases
# ---------------------------------------------------------------------------

# Internal: parent-widget type. Not part of the public API.
Master = tkinter.Misc | None

# `Event` lives in the public `bootstack.events` package; re-imported here so the
# many widget modules that pull it alongside the layout aliases keep working.
from bootstack.events import Event  # noqa: E402

EventCallback = Callable[["Event"], None]
"""Callback that receives an `Event` object."""

CommandCallback = Callable[[], Any]
"""Callback invoked with no arguments, e.g. a button `command=`."""

# ---------------------------------------------------------------------------
# Layout literals
# ---------------------------------------------------------------------------

Anchor = Literal['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'center']
"""Alignment anchor position."""

Orient = Literal['horizontal', 'vertical']
"""Widget orientation."""

Justify = Literal['left', 'center', 'right']
"""Text justification within a widget."""

Relief = Literal['flat', 'raised', 'sunken', 'groove', 'ridge', 'solid']
"""Border relief style."""

CompoundMode = Literal['text', 'image', 'top', 'bottom', 'left', 'right', 'center', 'none']
"""Relative position of image to text when both are displayed."""

Padding = int | tuple[int, int] | tuple[int, int, int, int]
"""Widget padding in pixels — a single value for all sides, `(x, y)` for the
horizontal and vertical amounts, or `(left, top, right, bottom)`."""

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

AccentToken = Literal['primary', 'secondary', 'info', 'success', 'warning', 'danger']
"""A semantic color accent. The accent params widen this with `| str`, so
`'default'`, `'muted'`, and modifiers (`'primary[+1]'`, `'primary[500]'`,
`'primary[subtle]'`) are also accepted."""

VariantToken = Literal['solid', 'outline', 'ghost', 'toggle']
"""Widget style variant."""

SurfaceToken = Literal['content', 'card', 'card_raised', 'chrome', 'overlay']
"""Background surface context token."""

WindowStyle = Literal['mica', 'acrylic', 'aero', 'transparent', 'win7']
"""A Windows-only window effect (no-op elsewhere). These are the common effects;
the underlying pywinstyles library accepts more (pass any as a plain string).
See https://pypi.org/project/pywinstyles/ for the full set."""

# ---------------------------------------------------------------------------
# Geometry manager literals
# ---------------------------------------------------------------------------

Fill = Literal['none', 'x', 'y', 'both', 'horizontal', 'vertical', 'all']
"""Fill axis for stack layout. `'horizontal'`/`'vertical'`/`'all'` are readable
aliases for `'x'`/`'y'`/`'both'`."""

Sticky = Literal['n', 's', 'e', 'w', 'ns', 'ew', 'nsew', 'ne', 'nw', 'se', 'sw', 'nse', 'nsw', 'new', 'sew', '']
"""Cell alignment for Grid layout. Any combination of ``'n'``, ``'s'``, ``'e'``, ``'w'``."""

Side = Literal['left', 'top', 'right', 'bottom']
"""Side placement for stack layout."""

Direction = Literal['vertical', 'horizontal', 'row', 'column', 'row-reverse', 'column-reverse']
"""Layout direction."""

BorderMode = Literal['inside', 'outside']
"""Border mode for the place geometry manager."""

# ---------------------------------------------------------------------------
# Base TypedDicts
# ---------------------------------------------------------------------------

class BaseWidgetKwargs(TypedDict, total=False):
    """Low-level options shared by all bootstack widget wrappers."""
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
