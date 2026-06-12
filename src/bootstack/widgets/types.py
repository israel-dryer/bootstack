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

LayoutKind = Literal['vstack', 'hstack', 'grid']
"""Internal layout manager for a container — `'vstack'`/`'hstack'` pack children
top-to-bottom / left-to-right; `'grid'` arranges them in rows and columns."""

AutoFlow = Literal['row', 'column', 'row-dense', 'column-dense', 'none']
"""Grid auto-placement direction. `'row'`/`'column'` fill along that axis;
the `'-dense'` variants backfill gaps; `'none'` disables auto-placement."""

BorderMode = Literal['inside', 'outside']
"""Border mode for the place geometry manager."""

ButtonVariant = Literal['default', 'solid', 'outline', 'ghost']
"""Style variant shared by the button family (Button, ButtonGroup, MenuButton,
SelectButton, ToggleButton, ToggleGroup, CommandBar) — `'default'`, `'solid'`,
`'outline'`, or `'ghost'`."""

AccordionVariant = Literal['solid', 'default']
"""Accordion header style — `'solid'`, or `'default'` for a ghost/transparent header."""

Region = Literal['before', 'center', 'after']
"""Placement region within a menu bar — `'before'`, `'center'`, or `'after'`."""

IconPosition = Literal['left', 'right', 'top', 'bottom']
"""Position of an icon relative to a widget's text — `'left'`, `'right'`,
`'top'`, or `'bottom'`."""

SelectionMode = Literal['none', 'single', 'multi']
"""How many rows/items can be selected — `'none'`, `'single'`, or `'multi'`."""

ExportScope = Literal['all', 'page', 'selection']
"""Which rows an export covers — `'all'` rows, the current `'page'`, or the
current `'selection'`."""

ExportFormat = Literal['csv', 'tsv', 'xlsx']
"""A tabular export format — `'csv'`, `'tsv'`, or `'xlsx'`."""

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


# ---------------------------------------------------------------------------
# Data-entry config types (DataTable columns + add/edit form)
# ---------------------------------------------------------------------------

EditorType = Literal[
    'textfield',
    'numberfield',
    'passwordfield',
    'datefield',
    'textarea',
    'select',
    'spinnerfield',
    'switch',
    'checkbox',
    'slider',
]
"""The field type used to edit a value in a `Form` or `DataTable` add/edit
dialog. Inferred from the value's `dtype` when omitted."""


class ColumnSpec(TypedDict, total=False):
    """A column definition for `DataTable(columns=...)`.

    Columns may be plain key strings or these dicts. Only `key` is required; the
    editor keys (`editor`, `editor_options`, `dtype`, `readonly`, `required`)
    shape how the column appears in the built-in add/edit dialog.
    """

    key: str
    """Record field this column reads and writes."""
    text: str
    """Header label. Defaults to `key`."""
    width: int
    """Column width in pixels."""
    minwidth: int
    """Minimum column width in pixels."""
    anchor: str
    """Cell alignment — `'w'`, `'center'`, or `'e'`."""
    format: "str | Callable[[Any], str]"
    """Display formatter for the cell — a format-spec string applied as
    `spec.format(value)` (e.g. `'${:,.0f}'` → `$70,000`) or a callable
    `(value) -> str`. Display only: sorting, filtering, editing, and export use
    the raw value."""
    dtype: str
    """Value type hint (e.g. `'int'`, `'text'`); drives alignment and the editor."""
    editor: EditorType
    """Field type used to edit this column in the add/edit dialog. Inferred from
    `dtype` when omitted."""
    editor_options: dict
    """Keyword options passed to the editor field."""
    readonly: bool
    """Show the column but make it non-editable in the dialog."""
    required: bool
    """Require a value in the add/edit dialog."""


class FormOptions(TypedDict, total=False):
    """Layout options for the built-in add/edit dialog (`DataTable(form=...)`)."""

    col_count: int
    """Number of columns the form fields are laid out in. Default `2`."""
    min_col_width: int
    """Minimum width in pixels of each form column. Default `260`."""
    scrollable: bool
    """Scroll the form when it is taller than the dialog. Default `True`."""
    resizable: bool
    """Allow the dialog to be resized. Default `True`."""


# ---------------------------------------------------------------------------
# Selection options (the shared "data bag" option shape)
# ---------------------------------------------------------------------------

class OptionDict(TypedDict, total=False):
    """A single choice for a selection widget, in dict form.

    The dict form is a *data bag*: `text` is required (and `value` defaults to
    it) UNLESS the dict carries an `icon` and a `value`, in which case `text` may
    be omitted to request an icon-only option. `text`/`value` and the recognized
    `icon`/`disabled` keys act on rendering; every *other* key rides along as
    carried data — retrievable as the widget's `selection` (the selected
    option's full record). Unrecognized keys are accepted, not rejected, so the
    dict route trades key-typo safety for extensibility.
    """

    text: str
    """Display label. Required unless `icon` + `value` are given (icon-only)."""
    value: Any
    """Stored and emitted value. Defaults to `text` when omitted."""
    icon: str
    """Optional icon spec rendered beside the label — alone when `text` is blank."""
    disabled: bool
    """When `True`, the option is dimmed and cannot be selected by the user."""


Option = str | tuple[str, Any] | OptionDict
"""A single choice for `Select`, `SelectButton`, `RadioGroup`, or `ToggleGroup`.

Three interchangeable forms, all normalized to a `(text, value)` pair:

- a plain `str` — text and value are the same (`'Small'`);
- a `(text, value)` tuple — decoupled label and value (`('Small', 's')`);
- an `OptionDict` — `{'text': 'Small', 'value': 's'}`; the extensible form."""
