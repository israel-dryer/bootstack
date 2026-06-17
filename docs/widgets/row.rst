Row
===

A container that lays out its children in a single horizontal row, left to
right. By default each child keeps its natural size and the group sits against
the left edge.

.. image:: /_static/examples/row-hero-light.png
   :class: bs-screenshot-light
   :alt: Row — light theme

.. image:: /_static/examples/row-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Row — dark theme

Usage
-----

Gap
~~~

``gap=`` sets uniform spacing in pixels between children.

.. code-block:: python

   # gap=4 — items close together
   with bs.Row(gap=4, show_border=True, padding=8):
       for i in range(1, 4):
           bs.Button(f"Item {i}")

   # gap=24 — items spread apart
   with bs.Row(gap=24, show_border=True, padding=8):
       for i in range(1, 4):
           bs.Button(f"Item {i}")

.. image:: /_static/examples/row-gap-light.png
   :class: bs-screenshot-light
   :alt: Row gap — light theme

.. image:: /_static/examples/row-gap-dark.png
   :class: bs-screenshot-dark
   :alt: Row gap — dark theme

Arranging the group
~~~~~~~~~~~~~~~~~~~~~

``horizontal_items=`` positions the whole group of children along the row.
``'left'`` (the default), ``'center'``, and ``'right'`` cluster them at one
edge; ``'space-between'``, ``'space-around'``, and ``'space-evenly'`` distribute
them across the full width. (It has no effect once a child grows.)

Arrangement only has room to act when the row is wider than its children, so
these rows use ``horizontal="stretch"`` to span their parent.

.. code-block:: python

   # cluster the group at one edge
   with bs.Row(horizontal_items="center", horizontal="stretch", show_border=True, padding=8):
       bs.Button("One"); bs.Button("Two"); bs.Button("Three")

   # distribute the group across the full width
   with bs.Row(horizontal_items="space-evenly", horizontal="stretch", show_border=True, padding=8):
       bs.Button("One"); bs.Button("Two"); bs.Button("Three")

.. image:: /_static/examples/row-arrange-light.png
   :class: bs-screenshot-light
   :alt: Row arrangement — light theme

.. image:: /_static/examples/row-arrange-dark.png
   :class: bs-screenshot-dark
   :alt: Row arrangement — dark theme

Cross-axis alignment
~~~~~~~~~~~~~~~~~~~~~~

``vertical_items=`` aligns children up and down within the row. ``'center'``
(the default) lines up mixed-height widgets (e.g. a label next to a text field);
``'top'`` or ``'bottom'`` pin them to an edge, and ``'stretch'`` makes every
child fill the row height. Override a single child with ``vertical=``.

.. code-block:: python

   with bs.Row(vertical_items="center", gap=8, height=90, show_border=True, padding=8):
       bs.Button("A")
       bs.Label("tall\nlabel")

.. image:: /_static/examples/row-align-light.png
   :class: bs-screenshot-light
   :alt: Row alignment — light theme

.. image:: /_static/examples/row-align-dark.png
   :class: bs-screenshot-dark
   :alt: Row alignment — dark theme

Growing a child
~~~~~~~~~~~~~~~

``grow=True`` lets one child claim and fill the leftover width while the others
keep their natural size. A search field between a fixed label and button is the
classic case.

.. code-block:: python

   with bs.Row(gap=8, vertical_items="center"):
       bs.Label("Search:")
       bs.TextField(grow=True)          # fills the leftover width
       bs.Button("Go", accent="primary")

.. image:: /_static/examples/row-grow-light.png
   :class: bs-screenshot-light
   :alt: Row grow — light theme

.. image:: /_static/examples/row-grow-dark.png
   :class: bs-screenshot-dark
   :alt: Row grow — dark theme

Proportional widths
~~~~~~~~~~~~~~~~~~~~

``weights=`` sizes children by a fixed ratio rather than by content.
``weights=[1, 2, 1]`` makes the middle child twice as wide as each neighbor, the
three together filling the row.

.. code-block:: python

   with bs.Row(gap=8, weights=[1, 2, 1], horizontal="stretch"):
       bs.Button("One"); bs.Button("Two"); bs.Button("Three")

.. image:: /_static/examples/row-weights-light.png
   :class: bs-screenshot-light
   :alt: Row proportional widths — light theme

.. image:: /_static/examples/row-weights-dark.png
   :class: bs-screenshot-dark
   :alt: Row proportional widths — dark theme

Spacer
~~~~~~

A :class:`Spacer <bootstack.Spacer>` is a local break that pushes its neighbors
apart — use it to split a row into clusters without nesting. Where
``horizontal_items`` moves the *whole* group, a ``Spacer`` opens a gap at *one*
point.

.. code-block:: python

   with bs.Row(gap=4):
       bs.Button("New")
       bs.Button("Open")
       bs.Spacer()                      # everything after is pushed right
       bs.Button("Settings")
       bs.Button("Profile")

.. image:: /_static/examples/row-spacer-light.png
   :class: bs-screenshot-light
   :alt: Row spacer — light theme

.. image:: /_static/examples/row-spacer-dark.png
   :class: bs-screenshot-dark
   :alt: Row spacer — dark theme

Background
~~~~~~~~~~

``surface=`` sets the container background. It accepts a surface token
(``'content'``, ``'card'``, ``'chrome'``, ``'overlay'``) or any accent token
(``'primary'``, ``'success'``, etc.) with optional modifiers:

.. code-block:: python

   with bs.Row(surface="card", padding=12, gap=8):
       bs.Label("Sits on card surface")

   with bs.Row(surface="primary[subtle]", padding=12, gap=8):
       bs.Label("Accent-tinted background")

Border
~~~~~~

``show_border=True`` draws a 1 px border along the inside edge of the frame.
Without padding, children render flush against it. Use at least ``padding=1``
to give the border visual clearance.

.. code-block:: python

   with bs.Row(gap=8, show_border=True, padding=8):
       bs.Button("A")
       bs.Button("B")
       bs.Button("C")

.. image:: /_static/examples/row-border-light.png
   :class: bs-screenshot-light
   :alt: Row border — light theme

.. image:: /_static/examples/row-border-dark.png
   :class: bs-screenshot-dark
   :alt: Row border — dark theme

Self-placement
~~~~~~~~~~~~~~~

``horizontal``, ``vertical``, and ``grow`` control how the Row places *itself*
within its parent — separate from how it arranges its own children. By default a
Row sits at its natural width; ``horizontal="stretch"`` makes it span the parent,
which is what lets a command bar fill the window.

.. code-block:: python

   # Natural width — sits against the left edge
   with bs.Row(gap=8, show_border=True, padding=8):
       bs.Button("File"); bs.Button("Edit"); bs.Button("View")

   # horizontal="stretch" — spans the full window width
   with bs.Row(gap=8, show_border=True, padding=8, horizontal="stretch"):
       bs.Button("File"); bs.Button("Edit"); bs.Button("View")

.. image:: /_static/examples/row-self-light.png
   :class: bs-screenshot-light
   :alt: Row self-placement — light theme

.. image:: /_static/examples/row-self-dark.png
   :class: bs-screenshot-dark
   :alt: Row self-placement — dark theme

Widget sizing
~~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

:class:`Column <bootstack.widgets.stacks.Column>` — vertical equivalent.
:class:`Spacer <bootstack.widgets.stacks.Spacer>` — a composable break that
pushes neighbors apart.
:class:`Grid <bootstack.widgets.grid.Grid>` — row and column layout.
:class:`Card <bootstack.widgets.card.Card>` and
:class:`GroupBox <bootstack.widgets.groupbox.GroupBox>` — a Row/Column with
an elevated background or labelled border.

API
---

The complete reference for :class:`Row <bootstack.Row>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Row

Full Example
------------

.. literalinclude:: ../../docs/examples/row.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
