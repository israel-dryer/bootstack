Grid
====

A container that arranges children in rows and columns. Children are
auto-placed left-to-right, top-to-bottom by default. Column and row sizes
are defined with ``columns=`` and ``rows=``; omitting them lets the grid
size itself to fit its content.

.. code-block:: python

   with bs.Grid(columns=["auto", 1], gap=8, sticky_items="ew", fill="x"):
       bs.Label("Name:")
       bs.TextField()
       bs.Label("Email:")
       bs.TextField()

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/grid-light.png"
        alt="Grid demo — light theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/grid-dark.png"
        alt="Grid demo — dark theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">

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

   # Three equal columns — integer shorthand
   bs.Grid(columns=3)

   # Same, written explicitly
   bs.Grid(columns=[1, 1, 1])

   # Label column sizes to content; field column takes the rest
   bs.Grid(columns=["auto", 1])

   # Fixed sidebar, flexible content, fixed panel
   bs.Grid(columns=["200px", 1, "160px"])

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

   bs.Grid(columns=[1, 1], gap=8)            # 8 px between all cells
   bs.Grid(columns=[1, 1], gap=(24, 8))      # 24 px between columns, 8 px between rows

Child alignment — sticky_items
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``sticky_items=`` controls how children fill their cell. Pass any
combination of ``'n'``, ``'s'``, ``'e'``, ``'w'``:

- ``'ew'`` — stretch horizontally, natural height (most common for forms)
- ``'nsew'`` — stretch to fill the entire cell
- ``''`` — center in cell at natural size

Individual children can override the default with their own ``sticky=``.

.. code-block:: python

   # All children fill cell width
   with bs.Grid(columns=[1, 1], gap=8, sticky_items="ew"):
       bs.Button("A")
       bs.Button("B")

   # Per-child override
   with bs.Grid(columns=[1, 1], gap=8, sticky_items="ew"):
       bs.Button("Normal")
       bs.Button("Centered", sticky="")

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

   with bs.Grid(columns=["auto", 1], gap=8, sticky_items="ew", fill="x"):
       bs.Label("First name")
       bs.TextField()
       bs.Label("Last name")
       bs.TextField()
       bs.Label("Email")
       bs.TextField()

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

.. autoclass:: bootstack.widgets.grid.Grid
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/grid.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs