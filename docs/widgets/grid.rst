Grid
====

A container that arranges children in rows and columns. Children are
auto-placed left-to-right, top-to-bottom by default. Column and row sizes
are defined with ``columns=`` and ``rows=``; omitting them lets the grid
size itself to fit its content.

.. image:: /_static/examples/grid-hero-light.png
   :class: bs-screenshot-light
   :alt: Grid — light theme

.. image:: /_static/examples/grid-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Grid — dark theme

Usage
-----

Column definitions
~~~~~~~~~~~~~~~~~~

``columns=`` accepts an integer or a list of per-column sizes:

- **Integer** (shorthand) — creates that many equal-weight columns.
  ``columns=3`` is equivalent to ``columns=[1, 1, 1]``.
- **Integer weight in a list** — relative share of available space
  (e.g. ``1``, ``2``). Weight ``0`` is equivalent to ``'auto'`` — prefer
  ``'auto'`` for clarity.
- ``'auto'`` — sized to the widest child in that column; does not grow.
- ``'Npx'`` — fixed pixel width (e.g. ``'120px'``).

.. code-block:: python

   # Three equal-weight columns (columns=3 is the same shorthand)
   with bs.Grid(columns=[1, 1, 1], gap=8, horizontal="stretch"):
       for label in ("Equal", "Weight", "Columns"):
           bs.Button(label)

   # Label column sizes to content; field column takes the rest
   with bs.Grid(columns=["auto", 1], gap=8, horizontal="stretch"):
       bs.Button("auto")
       bs.Button("weight=1 (fills remaining)")

   # Fixed sidebar, flexible content, fixed panel
   with bs.Grid(columns=["120px", 1, "80px"], gap=8, horizontal="stretch"):
       bs.Button("120px")
       bs.Button("weight=1")
       bs.Button("80px")

.. image:: /_static/examples/grid-columns-light.png
   :class: bs-screenshot-light
   :alt: Grid column definitions — light theme

.. image:: /_static/examples/grid-columns-dark.png
   :class: bs-screenshot-dark
   :alt: Grid column definitions — dark theme

Row definitions
~~~~~~~~~~~~~~~

``rows=`` follows the same format as ``columns=``. When omitted, rows are
added automatically as children are placed.

- **Integer** (shorthand) — creates that many equal-weight rows.
  ``rows=3`` is equivalent to ``rows=[1, 1, 1]``.
- **Integer weight in a list** — relative share of available vertical space.
- ``'auto'`` — sized to the tallest child in that row; does not grow.
- ``'Npx'`` — fixed pixel height (e.g. ``'80px'``).

.. code-block:: python

   # Three equal rows — integer shorthand
   bs.Grid(rows=3)

   # Mixed: two auto-height rows, one that fills remaining space
   bs.Grid(rows=["auto", 1, "auto"])

Gap
~~~

``gap=`` sets spacing between cells. An integer applies to both axes;
a 2-tuple ``(col_gap, row_gap)`` sets them independently.

.. code-block:: python

   # 8 px between all cells
   with bs.Grid(columns=[1, 1], gap=8):
       for label in ("A", "B", "C", "D"):
           bs.Button(label)

   # 32 px between columns, 8 px between rows
   with bs.Grid(columns=[1, 1], gap=(32, 8)):
       for label in ("A", "B", "C", "D"):
           bs.Button(label)

.. image:: /_static/examples/grid-gap-light.png
   :class: bs-screenshot-light
   :alt: Grid gap — light theme

.. image:: /_static/examples/grid-gap-dark.png
   :class: bs-screenshot-dark
   :alt: Grid gap — dark theme

In-cell alignment
~~~~~~~~~~~~~~~~~~

``horizontal_items=`` and ``vertical_items=`` control how children align
within their cell. Both default to ``'stretch'`` (the child fills the cell on
that axis); set either to ``'left'`` / ``'center'`` / ``'right'`` or ``'top'`` /
``'center'`` / ``'bottom'`` to place the child at its natural size instead.

Individual children can override the defaults with their own ``horizontal=`` /
``vertical=``.

.. code-block:: python

   # stretch horizontally — natural height
   with bs.Grid(columns=[1, 1], gap=8, vertical_items="center", height=80):
       bs.Button("A"); bs.Button("B")

   # center in cell at natural size
   with bs.Grid(columns=[1, 1], gap=8,
                horizontal_items="center", vertical_items="center", height=80):
       bs.Button("A"); bs.Button("B")

   # fill the entire cell (the default on both axes)
   with bs.Grid(columns=[1, 1], gap=8, height=80):
       bs.Button("A"); bs.Button("B")

.. image:: /_static/examples/grid-sticky-light.png
   :class: bs-screenshot-light
   :alt: Grid sticky — light theme

.. image:: /_static/examples/grid-sticky-dark.png
   :class: bs-screenshot-dark
   :alt: Grid sticky — dark theme

Auto-flow
~~~~~~~~~

``auto_flow=`` controls the direction children are placed when auto-flowing
across the grid. Default is ``'row'`` (left-to-right, then next row).
Use ``'column'`` to fill down first, then move to the next column.
The ``'-dense'`` variants back-fill gaps left by larger spanning children.

.. code-block:: python

   bs.Grid(columns=[1, 1, 1], auto_flow="row")     # 1 2 3 / 4 5 6
   bs.Grid(rows=[1, 1, 1], auto_flow="column")      # fills columns first

In context
~~~~~~~~~~

The most common Grid pattern is a two-column form layout with an ``'auto'``
label column and a ``1``-weight field column:

.. code-block:: python

   with bs.Grid(columns=["auto", 1], gap=8, horizontal="stretch"):
       bs.Label("First name")
       bs.TextField()
       bs.Label("Last name")
       bs.TextField()
       bs.Label("Email")
       bs.TextField()
       bs.Label("Role")
       bs.TextField()

.. image:: /_static/examples/grid-form-light.png
   :class: bs-screenshot-light
   :alt: Grid form layout — light theme

.. image:: /_static/examples/grid-form-dark.png
   :class: bs-screenshot-dark
   :alt: Grid form layout — dark theme

Background
~~~~~~~~~~

``surface=`` sets the container background. It accepts a surface token
(``'content'``, ``'card'``, ``'chrome'``, ``'overlay'``) or any accent token
(``'primary'``, ``'success'``, etc.) with optional modifiers:

.. code-block:: python

   with bs.Grid(columns=2, surface="card", padding=12, gap=8):
       bs.Label("Sits on card surface")

   with bs.Grid(columns=2, surface="primary[subtle]", padding=12, gap=8):
       bs.Label("Accent-tinted background")

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

:class:`Card <bootstack.widgets.card.Card>` and
:class:`GroupBox <bootstack.widgets.groupbox.GroupBox>` both support
``layout='grid'`` to arrange their children with the same column/row
options.

API
---

The complete reference for :class:`Grid <bootstack.Grid>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Grid

Full Example
------------

.. literalinclude:: ../../docs/examples/grid.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs