Arranging Widgets
=================

bootstack arranges widgets with **container** widgets. A container both *holds*
its children and decides how they are placed; a widget is parented to the nearest
enclosing container — the `with` block it is created in. There is no `parent=`
wiring in the common case and no manual coordinates.

There are three containers:

- :class:`~bootstack.Column` stacks its children top to bottom.
- :class:`~bootstack.Row` stacks them left to right.
- :class:`~bootstack.Grid` places them in rows and columns.

Nest them to build any layout — a toolbar (`Row`) above a body (`Column`), a
form laid out in a `Grid`, and so on.

.. code-block:: python

   with bs.Column(gap=8, padding=16, horizontal_items="stretch"):
       bs.Label("Name")
       bs.TextField()
       with bs.Row(gap=8):
           bs.Button("OK", grow=True)
           bs.Button("Cancel")

The screen axes
---------------

Placement is described against the **screen**, not the flow direction: the
``horizontal`` axis runs left–right and the ``vertical`` axis runs top–bottom, in
every container. You never flip axes when you switch from a Row to a Column —
``horizontal`` always means horizontal.

Each axis takes a concrete edge value:

- horizontal: ``'left'`` · ``'center'`` · ``'right'`` · ``'stretch'``
- vertical: ``'top'`` · ``'center'`` · ``'bottom'`` · ``'stretch'``

``'stretch'`` makes a child fill that axis; the edge values size it to its
content and pin it to that edge.

Self versus items
-----------------

Two layers of placement share these words, distinguished by a suffix:

- **Bare** keys (``horizontal``, ``vertical``, ``grow``) place the widget
  *itself* within its parent.
- The **``_items``** keys (``horizontal_items``, ``vertical_items``,
  ``grow_items``) set the default for a container's *children*. Any child
  overrides the default with its own bare key.

Because a container is also a widget, it can set both — how it sits in its parent
and how it arranges its own children:

.. code-block:: python

   # This Column fills its parent's width (self), and stretches every
   # child to its own width (items).
   with bs.Column(horizontal="stretch", horizontal_items="stretch", gap=8):
       bs.TextField()
       bs.TextField()

Arranging the group
-------------------

On a stack's **stacking axis** (vertical for a Column, horizontal for a Row),
the ``_items`` key arranges the whole group: cluster it at an edge
(``'top'``/``'center'``/``'bottom'`` or ``'left'``/``'center'``/``'right'``) or
distribute it with ``'space-between'``, ``'space-around'``, or
``'space-evenly'``.

.. code-block:: python

   # Push a group to the right end of a toolbar
   with bs.Row(horizontal_items="right", gap=8):
       bs.Button("Cancel")
       bs.Button("Save", accent="primary")

On the **cross axis**, the ``_items`` key aligns each child — ``'center'`` (the
default) lines up mixed-height widgets, ``'stretch'`` makes them fill, and
``'left'``/``'right'`` (or ``'top'``/``'bottom'``) pin to an edge:

.. code-block:: python

   with bs.Row(gap=8, vertical_items="center"):   # label and field share a center line
       bs.Label("Search:")
       bs.TextField(grow=True)

Growing children
----------------

``grow`` lets a child claim and fill leftover space along the stacking axis —
the equivalent of a flexible region. ``grow=True`` takes one share; ``grow=N``
takes ``N`` shares; ``weights=[1, 2, 1]`` on the container sets every child's
share positionally.

.. code-block:: python

   with bs.Column(gap=8, padding=8, horizontal_items="stretch"):
       bs.Label("Header")
       bs.ListView(items=rows, grow=True)   # takes all leftover height
       bs.Button("Add")                     # stays its natural size

.. note::

   **Data and canvas widgets** — ``ListView``, ``DataTable``, ``Tree``,
   ``Gallery``, ``Carousel``, ``Picture``, ``CodeEditor`` — have no natural size
   of their own and collapse without a directive. Give them ``grow=True`` (and
   ``horizontal="stretch"`` in a Column) to claim space.

.. image:: /_static/examples/row-grow-light.png
   :class: bs-screenshot-light
   :alt: A text field growing to fill a row — light theme

.. image:: /_static/examples/row-grow-dark.png
   :class: bs-screenshot-dark
   :alt: A text field growing to fill a row — dark theme

Spacer
------

A :class:`~bootstack.Spacer` is a composable break that pushes its neighbors
apart. Where ``horizontal_items``/``vertical_items`` move the *whole* group, a
``Spacer`` opens a gap at *one* point — ideal for clustered toolbars and pinned
footers, with no nesting:

.. code-block:: python

   with bs.Row(gap=4):
       bs.Button("New"); bs.Button("Open")
       bs.Spacer()                 # everything after is pushed to the right
       bs.Button("Settings")

``Spacer(size=N)`` is instead a fixed gap, and ``Spacer(weight=N)`` shares slack
with other spacers in proportion.

Spacing: padding versus gap versus margin
-----------------------------------------

Three knobs control whitespace, and keeping them straight removes most layout
fiddling:

- `padding` — space *inside* a container, between its edge and its children. Set
  it on the container.
- `gap` — space *between* a container's children. Set it on the container.
- `margin` (and `margin_x` / `margin_y`) — extra space around *one* child,
  overriding the container's `gap` for that widget. Set it on the child.

.. code-block:: python

   with bs.Column(padding=16, gap=8):     # 16px inset, 8px between rows
       bs.Label("Settings", font="heading-md")
       bs.Switch("Dark mode", margin_y=12)   # extra breathing room around this one

When a widget needs different spacing on each axis, use `margin_x` for left/right
and `margin_y` for top/bottom; each also accepts a `(before, after)` pair for
asymmetric spacing.

Grids
-----

:class:`~bootstack.Grid` places children in cells. The `columns=` argument sets
the column sizing: a list of weights (`[1, 2]` makes the second column twice as
wide), or the shorthand `columns=3` for three equal columns (`"auto"` sizes a
column to its content, `"120px"` fixes a pixel width). Children flow into cells
automatically, or you can pin them with `row=`/`column=` and span with
`rowspan=`/`columnspan=`.

.. code-block:: python

   with bs.Grid(columns=["auto", 1], gap=8):
       bs.Label("Name");  bs.TextField()
       bs.Label("Email"); bs.TextField()

In-cell alignment uses the same axis words: ``horizontal_items`` and
``vertical_items`` set how every child sits in its cell (both default to
``'stretch'``, so children fill their cells), overridable per child with
``horizontal``/``vertical``.

.. code-block:: python

   with bs.Grid(columns=[1, 1, 1], gap=8, vertical_items="center"):
       for label in ("Equal", "Weight", "Columns"):
           bs.Button(label)

.. image:: /_static/examples/grid-columns-light.png
   :class: bs-screenshot-light
   :alt: Grid column weights — light theme

.. image:: /_static/examples/grid-columns-dark.png
   :class: bs-screenshot-dark
   :alt: Grid column weights — dark theme

Bordered containers
-------------------

For a visually grouped region, use :class:`~bootstack.Card` (an elevated panel)
or :class:`~bootstack.GroupBox` (a labeled border). Both lay out their children
like a `Column` by default (pass `layout="row"` or `layout="grid"` to switch).
Give them `padding` — a border drawn flush against its content looks cramped:

.. code-block:: python

   with bs.GroupBox("Account", padding=16, gap=8, horizontal_items="stretch"):
       bs.TextField(label="Username")
       bs.PasswordField(label="Password")

Common quirks
-------------

A handful of behaviors trip people up the first time:

- **Children center on the cross axis by default.** A Column centers its
  children horizontally and a Row centers them vertically, so a label and a field
  in a Row line up on a center line with no kwarg. For a full-width form column
  set ``horizontal_items="stretch"``; to left-align, ``horizontal_items="left"``.
  The *stacking* axis still starts at the top/left — use ``horizontal_items`` /
  ``vertical_items`` or a ``Spacer`` to move the whole group.
- **Data and canvas widgets collapse without `grow`.** A ``ListView`` or
  ``Tree`` with no ``grow``/``stretch`` shrinks to nothing — give it
  ``grow=True`` (and ``horizontal="stretch"`` in a Column).
- **Setting `width=`/`height=` on a stack fixes that size.** Use `grow` and
  `horizontal`/`vertical="stretch"` for the axes you still want to flex rather
  than a hard size.
- **A bordered container needs `padding`.** Without it, `Card` / `GroupBox` draw
  their border directly against the content.
- **Legacy placement kwargs raise.** Passing `fill=`/`expand=`/`anchor=`/
  `sticky=` to a Row/Column/Grid child raises a clear error instead of silently
  collapsing it — use `grow` / `horizontal` / `vertical` instead.

Placement options reference
---------------------------

Every widget accepts these self-placement options as keyword arguments. Which
ones apply depends on the parent container.

.. include:: ../shared/widget-sizing.rst

See also
--------

- :doc:`/widgets/column` · :doc:`/widgets/row` · :doc:`/widgets/grid` — the
  container widgets.
- :doc:`/widgets/card` · :doc:`/widgets/groupbox` — bordered containers.
- :doc:`/getting-started/app-structures` — the top-level containers these nest in.
