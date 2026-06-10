Types
=====

.. currentmodule:: bootstack.types

Token and keyword types for annotating your own helpers and widget subclasses.
These are the names that appear in widget signatures — the accent/variant/surface
tokens, the layout literals, density, and the keyword ``TypedDict``\ s. Import them
from ``bootstack.types`` when you annotate code that builds on bootstack::

    from bootstack.types import AccentToken, WidgetDensity

Style and state tokens
----------------------

Semantic tokens for color, variant, and surface, plus density, state, and the
lower-level appearance literals.

.. py:type:: AccentToken

   A semantic color accent — `'primary'`, `'secondary'`, `'info'`, `'success'`,
   `'warning'`, `'danger'`. Accent params widen it with `| str`, also accepting
   `'default'`, `'muted'`, and modifiers like `'primary[500]'`.

.. py:type:: AccordionVariant

   Accordion header style — `'solid'`, or `'default'` for a ghost/transparent
   header.

.. py:type:: BorderMode

   Border placement for the place geometry manager — `'inside'` or `'outside'`.

.. py:type:: ButtonVariant

   Style variant shared by the button family (Button, ButtonGroup, MenuButton,
   SelectButton, ToggleButton, ToggleGroup, Toolbar) — `'default'`, `'solid'`,
   `'outline'`, or `'ghost'`.

.. py:type:: CompoundMode

   Position of an image relative to its text — `'text'`, `'image'`, `'top'`,
   `'bottom'`, `'left'`, `'right'`, `'center'`, `'none'`.

.. py:type:: Relief

   Border relief style — `'flat'`, `'raised'`, `'sunken'`, `'groove'`,
   `'ridge'`, `'solid'`.

.. py:type:: SurfaceToken

   Background surface context — `'content'`, `'card'`, `'card_raised'`,
   `'chrome'`, `'overlay'`.

.. py:type:: VariantToken

   Widget style variant — `'solid'`, `'outline'`, `'ghost'`, `'toggle'`.

.. py:type:: WidgetDensity

   Sizing density — `'default'`, or `'compact'` for reduced padding.

.. py:type:: WidgetState

   Widget interaction state — `'normal'`, `'active'`, `'disabled'`, `'readonly'`.

.. py:type:: WindowStyle

   A Windows-only window effect (no-op elsewhere) — `'mica'`, `'acrylic'`,
   `'aero'`, `'transparent'`, `'win7'`. The underlying pywinstyles library
   accepts more, passed as a plain string.

Layout literals
---------------

The placement and sizing literals accepted by container and ``**kwargs`` layout
options.

.. py:type:: Anchor

   Alignment anchor position — `'n'`, `'ne'`, `'e'`, `'se'`, `'s'`, `'sw'`,
   `'w'`, `'nw'`, `'center'`.

.. py:type:: AutoFlow

   Grid auto-placement direction — `'row'`, `'column'`, `'row-dense'`,
   `'column-dense'`, `'none'`.

.. py:type:: Direction

   Layout direction — `'vertical'`, `'horizontal'`, `'row'`, `'column'`,
   `'row-reverse'`, `'column-reverse'`.

.. py:type:: Fill

   Fill axis for stack layout — `'none'`, `'x'`, `'y'`, `'both'`, with readable
   aliases `'horizontal'`, `'vertical'`, `'all'`.

.. py:type:: IconPosition

   Position of an icon relative to a widget's text — `'left'`, `'right'`,
   `'top'`, or `'bottom'`.

.. py:type:: Justify

   Text justification within a widget — `'left'`, `'center'`, `'right'`.

.. py:type:: LayoutKind

   A container's internal layout manager — `'vstack'`, `'hstack'`, `'grid'`.

.. py:type:: Orient

   Widget orientation — `'horizontal'`, `'vertical'`.

.. py:type:: Padding

   Widget padding in pixels — a single `int` for all sides, `(x, y)` for the
   horizontal and vertical amounts, or `(left, top, right, bottom)`.

.. py:type:: Region

   Placement region within a menu bar — `'before'`, `'center'`, or `'after'`.

.. py:type:: Side

   Side placement for stack layout — `'left'`, `'top'`, `'right'`, `'bottom'`.

.. py:type:: Sticky

   Cell alignment for Grid layout — any combination of `'n'`, `'s'`, `'e'`,
   `'w'` (e.g. `'nsew'`).

Data and selection
------------------

Literals for selection behavior and tabular data export.

.. py:type:: ExportFormat

   A tabular export format — `'csv'`, `'tsv'`, or `'xlsx'`.

.. py:type:: ExportScope

   Which rows an export covers — `'all'` rows, the current `'page'`, or the
   current `'selection'`.

.. py:type:: SelectionMode

   How many rows or items can be selected — `'none'`, `'single'`, or `'multi'`.

Keyword and config types
------------------------

The ``TypedDict`` shapes for low-level widget options and the data-entry config
that ``DataTable`` and ``Form`` accept.

.. autoclass:: BaseWidgetKwargs
   :members:

.. autoclass:: ColumnSpec
   :members:

.. py:type:: EditorType

   The field type used to edit a value in a `Form` or `DataTable` add/edit
   dialog, inferred from the value's `dtype` when omitted — `'textfield'`,
   `'numberfield'`, `'passwordfield'`, `'datefield'`, `'textarea'`, `'select'`,
   `'spinnerfield'`, `'switch'`, `'checkbox'`, `'slider'`.

.. autoclass:: FormOptions
   :members:

.. autoclass:: StyledKwargs
   :members:
