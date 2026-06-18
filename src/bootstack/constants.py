"""Runtime string constants for bootstack.

This module provides symbolic string constants for use with tkinter geometry
managers, widget states, and other APIs that accept fixed string values.

Type aliases (Literal types for type checking) live in
`bootstack.widgets.types` and are re-exported here for convenience.

Example::

    import bootstack as bs
    from bootstack.constants import LEFT, X, NORMAL

    btn = bs.Button(root, text="OK")
    btn.pack(side=LEFT, fill=X, padx=10)
"""
from __future__ import annotations

from typing import Final, Literal

# Re-export type aliases from widgets.types so `from bootstack.constants import *`
# continues to work as before.
from bootstack.widgets.types import (
    Anchor,
    BorderMode,
    CompoundMode,
    Fill,
    Justify,
    Orient,
    Relief,
    Side,
    Sticky,
    AccentToken,
    SurfaceToken,
    WidgetDensity,
    WidgetState,
)

# ---------------------------------------------------------------------------
# Literal types that remain canonical here (not in widgets.types)
# ---------------------------------------------------------------------------

TkBoolean = Literal[0, 1, True, False]
"""Tk-style boolean: 0/1 or True/False."""

State = Literal['normal', 'disabled', 'active', 'hidden', 'readonly']
"""Full widget state set including `'hidden'` (Canvas) and `'readonly'` (ttk).
For ttk widget construction kwargs prefer `WidgetState` from `bootstack.widgets.types`.
"""

MenuItemType = Literal['cascade', 'checkbutton', 'command', 'radiobutton', 'separator']
"""Menu item type for `tk.Menu.add_*` calls."""

ActiveStyle = Literal['none', 'dotbox', 'underline']
"""Active-item highlight style for `tk.Listbox`."""

PieStyle = Literal['pieslice', 'chord', 'arc']
"""Arc/pie style for `Canvas.create_arc`."""

LineCap = Literal['butt', 'projecting', 'round']
"""Line cap style for Canvas lines."""

LineJoin = Literal['bevel', 'miter', 'round']
"""Line join style for Canvas lines."""

IndexPos = Literal['first', 'last']
"""Named index positions used by several widget methods."""

ViewArg = Literal['moveto', 'scroll', 'units', 'pages']
"""Arguments accepted by `xview()` / `yview()` scroll methods."""

TtkTheme = Literal['clam', 'alt', 'default']
"""Built-in base ttk theme names."""

Tabs = Literal['numeric']
"""Tab alignment mode for the Text widget."""

Align = Literal['baseline']
"""Text alignment for embedded windows/images in the Text widget."""

Wrap = Literal['none', 'char', 'word']
"""Text wrapping mode for the `tk.Text` widget."""

SelectMode = Literal['single', 'browse', 'multiple', 'extended']
"""Item selection mode for `tk.Listbox`."""

ProgressMode = Literal['determinate', 'indeterminate']
"""Progress mode for the Progressbar widget."""

# ---------------------------------------------------------------------------
# Booleans (legacy Tk style)
# ---------------------------------------------------------------------------

NO: Final[TkBoolean] = 0
FALSE: Final[TkBoolean] = 0
OFF: Final[TkBoolean] = 0
YES: Final[TkBoolean] = 1
TRUE: Final[TkBoolean] = 1
ON: Final[TkBoolean] = 1

# ---------------------------------------------------------------------------
# -anchor / -sticky
# ---------------------------------------------------------------------------

N: Final[Anchor] = 'n'
S: Final[Anchor] = 's'
W: Final[Anchor] = 'w'
E: Final[Anchor] = 'e'
NW: Final[Anchor] = 'nw'
SW: Final[Anchor] = 'sw'
NE: Final[Anchor] = 'ne'
SE: Final[Anchor] = 'se'
NS: Final[str] = 'ns'
EW: Final[str] = 'ew'
NSEW: Final[str] = 'nsew'
CENTER: Final[Anchor] = 'center'

# ---------------------------------------------------------------------------
# -fill
# ---------------------------------------------------------------------------

NONE: Final[Fill] = 'none'
X: Final[Fill] = 'x'
Y: Final[Fill] = 'y'
BOTH: Final[Fill] = 'both'

# ---------------------------------------------------------------------------
# -side
# ---------------------------------------------------------------------------

LEFT: Final[Side] = 'left'
TOP: Final[Side] = 'top'
RIGHT: Final[Side] = 'right'
BOTTOM: Final[Side] = 'bottom'

# ---------------------------------------------------------------------------
# -relief
# ---------------------------------------------------------------------------

RAISED: Final[Relief] = 'raised'
SUNKEN: Final[Relief] = 'sunken'
FLAT: Final[Relief] = 'flat'
RIDGE: Final[Relief] = 'ridge'
GROOVE: Final[Relief] = 'groove'
SOLID: Final[Relief] = 'solid'

# ---------------------------------------------------------------------------
# -orient
# ---------------------------------------------------------------------------

HORIZONTAL: Final[Orient] = 'horizontal'
VERTICAL: Final[Orient] = 'vertical'

# ---------------------------------------------------------------------------
# -wrap (Text widget)
# ---------------------------------------------------------------------------

CHAR: Final[Wrap] = 'char'
WORD: Final[Wrap] = 'word'

# ---------------------------------------------------------------------------
# -tabs (Text widget)
# ---------------------------------------------------------------------------

NUMERIC: Final[Tabs] = 'numeric'

# ---------------------------------------------------------------------------
# -align (Text widget)
# ---------------------------------------------------------------------------

BASELINE: Final[Align] = 'baseline'

# ---------------------------------------------------------------------------
# -bordermode (place geometry manager)
# ---------------------------------------------------------------------------

INSIDE: Final[BorderMode] = 'inside'
OUTSIDE: Final[BorderMode] = 'outside'

# ---------------------------------------------------------------------------
# Special tags / marks / positions
# ---------------------------------------------------------------------------

SEL: Final[str] = 'sel'
SEL_FIRST: Final[str] = 'sel.first'
SEL_LAST: Final[str] = 'sel.last'
END: Final[str] = 'end'
INSERT: Final[str] = 'insert'
CURRENT: Final[str] = 'current'
ANCHOR: Final[str] = 'anchor'
ALL: Final[str] = 'all'

# ---------------------------------------------------------------------------
# States
# ---------------------------------------------------------------------------

NORMAL: Final[State] = 'normal'
DISABLED: Final[State] = 'disabled'
ACTIVE: Final[State] = 'active'
HIDDEN: Final[State] = 'hidden'
READONLY: Final[State] = 'readonly'

# ---------------------------------------------------------------------------
# Menu item types
# ---------------------------------------------------------------------------

CASCADE: Final[MenuItemType] = 'cascade'
CHECKBUTTON: Final[MenuItemType] = 'checkbutton'
COMMAND: Final[MenuItemType] = 'command'
RADIOBUTTON: Final[MenuItemType] = 'radiobutton'
SEPARATOR: Final[MenuItemType] = 'separator'

# ---------------------------------------------------------------------------
# Listbox modes / styles
# ---------------------------------------------------------------------------

SINGLE: Final[SelectMode] = 'single'
BROWSE: Final[SelectMode] = 'browse'
MULTIPLE: Final[SelectMode] = 'multiple'
EXTENDED: Final[SelectMode] = 'extended'

DOTBOX: Final[ActiveStyle] = 'dotbox'
UNDERLINE: Final[ActiveStyle] = 'underline'

# ---------------------------------------------------------------------------
# Canvas styles
# ---------------------------------------------------------------------------

PIESLICE: Final[PieStyle] = 'pieslice'
CHORD: Final[PieStyle] = 'chord'
ARC: Final[PieStyle] = 'arc'

FIRST: Final[IndexPos] = 'first'
LAST: Final[IndexPos] = 'last'

BUTT: Final[LineCap] = 'butt'
PROJECTING: Final[LineCap] = 'projecting'
ROUND: Final[LineCap] = 'round'

BEVEL: Final[LineJoin] = 'bevel'
MITER: Final[LineJoin] = 'miter'

# ---------------------------------------------------------------------------
# xview / yview args
# ---------------------------------------------------------------------------

MOVETO: Final[ViewArg] = 'moveto'
SCROLL: Final[ViewArg] = 'scroll'
UNITS: Final[ViewArg] = 'units'
PAGES: Final[ViewArg] = 'pages'

# ---------------------------------------------------------------------------
# Themes / layout defaults
# ---------------------------------------------------------------------------

DEFAULT: Final[str] = 'default'
DEFAULT_THEME: Final[str] = 'bootstrap-light'
DEFAULT_MIN_COL_WIDTH: Final[int] = 275

TTK_CLAM: Final[TtkTheme] = 'clam'
TTK_ALT: Final[TtkTheme] = 'alt'
TTK_DEFAULT: Final[TtkTheme] = 'default'

# ---------------------------------------------------------------------------
# Progressbar modes
# ---------------------------------------------------------------------------

DETERMINATE: Final[ProgressMode] = 'determinate'
INDETERMINATE: Final[ProgressMode] = 'indeterminate'

# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------

__all__ = [
    # Re-exported type aliases (canonical source: bootstack.widgets.types)
    'Anchor', 'AccentToken', 'BorderMode', 'CompoundMode', 'Fill', 'Justify',
    'Orient', 'Relief', 'Side', 'Sticky', 'SurfaceToken',
    'WidgetDensity', 'WidgetState',
    # Literal types canonical to this module
    'ActiveStyle', 'Align', 'IndexPos', 'LineJoin', 'LineCap', 'MenuItemType',
    'PieStyle', 'ProgressMode', 'SelectMode', 'State', 'Tabs', 'TkBoolean',
    'TtkTheme', 'ViewArg', 'Wrap',
    # Boolean sentinels
    'NO', 'FALSE', 'OFF', 'YES', 'TRUE', 'ON',
    # Anchor / sticky
    'N', 'S', 'W', 'E', 'NW', 'SW', 'NE', 'SE', 'NS', 'EW', 'NSEW', 'CENTER',
    # Fill
    'NONE', 'X', 'Y', 'BOTH',
    # Side
    'LEFT', 'TOP', 'RIGHT', 'BOTTOM',
    # Relief
    'RAISED', 'SUNKEN', 'FLAT', 'RIDGE', 'GROOVE', 'SOLID',
    # Orient
    'HORIZONTAL', 'VERTICAL',
    # Text widget
    'CHAR', 'WORD', 'NUMERIC', 'BASELINE',
    # Place geometry
    'INSIDE', 'OUTSIDE',
    # Tags / marks
    'SEL', 'SEL_FIRST', 'SEL_LAST', 'END', 'INSERT', 'CURRENT', 'ANCHOR', 'ALL',
    # States
    'NORMAL', 'DISABLED', 'ACTIVE', 'HIDDEN', 'READONLY',
    # Menu
    'CASCADE', 'CHECKBUTTON', 'COMMAND', 'RADIOBUTTON', 'SEPARATOR',
    # Listbox
    'SINGLE', 'BROWSE', 'MULTIPLE', 'EXTENDED', 'DOTBOX', 'UNDERLINE',
    # Canvas
    'PIESLICE', 'CHORD', 'ARC', 'FIRST', 'LAST',
    'BUTT', 'PROJECTING', 'ROUND', 'BEVEL', 'MITER',
    # Scroll
    'MOVETO', 'SCROLL', 'UNITS', 'PAGES',
    # Themes / defaults
    'DEFAULT', 'DEFAULT_THEME', 'DEFAULT_MIN_COL_WIDTH',
    'TTK_CLAM', 'TTK_ALT', 'TTK_DEFAULT',
    # Progressbar
    'DETERMINATE', 'INDETERMINATE',
]
