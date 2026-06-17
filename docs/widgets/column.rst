Column
======

A container that lays out its children in a single vertical column, top to
bottom. By default each child keeps its natural height and the group sits at the
top edge.

.. image:: /_static/examples/column-hero-light.png
   :class: bs-screenshot-light
   :alt: Column — light theme

.. image:: /_static/examples/column-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Column — dark theme

Usage
-----

Gap
~~~

``gap=`` sets uniform spacing in pixels between children.

.. code-block:: python

   # gap=8 — rows close together
   with bs.Column(gap=8, show_border=True, padding=8, horizontal_items="stretch"):
       for lbl in ("A", "B", "C"):
           bs.Button(lbl)

   # gap=24 — rows spread apart
   with bs.Column(gap=24, show_border=True, padding=8, horizontal_items="stretch"):
       for lbl in ("A", "B", "C"):
           bs.Button(lbl)

.. image:: /_static/examples/column-gap-light.png
   :class: bs-screenshot-light
   :alt: Column gap — light theme

.. image:: /_static/examples/column-gap-dark.png
   :class: bs-screenshot-dark
   :alt: Column gap — dark theme

Cross-axis alignment
~~~~~~~~~~~~~~~~~~~~~~

``horizontal_items=`` aligns children left and right within the column.
``'left'``, ``'center'`` (the default), and ``'right'`` size each child to its
content and pin it to that edge; ``'stretch'`` makes every child fill the column
width — the usual choice for a form column. Override a single child with
``horizontal=``.

.. code-block:: python

   with bs.Column(horizontal_items="center", show_border=True, padding=8):
       bs.Button("Save")

   with bs.Column(horizontal_items="stretch", show_border=True, padding=8):
       bs.Button("Save")          # fills the column width

.. image:: /_static/examples/column-align-light.png
   :class: bs-screenshot-light
   :alt: Column alignment — light theme

.. image:: /_static/examples/column-align-dark.png
   :class: bs-screenshot-dark
   :alt: Column alignment — dark theme

Arranging the group
~~~~~~~~~~~~~~~~~~~~~

``vertical_items=`` positions the whole group of children down the column.
``'top'`` (the default), ``'center'``, and ``'bottom'`` cluster them at one
edge; ``'space-between'``, ``'space-around'``, and ``'space-evenly'`` distribute
them across the full height. (It has no effect once a child grows.)

Arrangement only has room to act when the column is taller than its children, so
these examples set a fixed ``height=``.

.. code-block:: python

   # cluster the group at one edge
   with bs.Column(vertical_items="center", height=140,
                  show_border=True, padding=8, horizontal_items="stretch"):
       bs.Button("Header")
       bs.Button("Footer")

   # distribute the group across the full height
   with bs.Column(vertical_items="space-evenly", height=140,
                  show_border=True, padding=8, horizontal_items="stretch"):
       bs.Button("Header")
       bs.Button("Footer")

.. image:: /_static/examples/column-arrange-light.png
   :class: bs-screenshot-light
   :alt: Column arrangement — light theme

.. image:: /_static/examples/column-arrange-dark.png
   :class: bs-screenshot-dark
   :alt: Column arrangement — dark theme

Growing a child
~~~~~~~~~~~~~~~

``grow=True`` lets one child claim and fill the leftover height while the others
keep their natural size — ideal for a content area between a fixed header and
footer.

.. code-block:: python

   with bs.Column(gap=6, height=150, horizontal_items="stretch"):
       bs.Button("Header")
       bs.Button("Content", grow=True)   # fills the middle
       bs.Button("Footer")

.. image:: /_static/examples/column-grow-light.png
   :class: bs-screenshot-light
   :alt: Column grow — light theme

.. image:: /_static/examples/column-grow-dark.png
   :class: bs-screenshot-dark
   :alt: Column grow — dark theme

Proportional heights
~~~~~~~~~~~~~~~~~~~~~

``weights=`` sizes children by a fixed ratio rather than by content.
``weights=[1, 2, 1]`` makes the middle child twice as tall as each neighbor, the
three together filling the column.

.. code-block:: python

   with bs.Column(gap=8, weights=[1, 2, 1], height=220, horizontal_items="stretch"):
       bs.Button("One"); bs.Button("Two"); bs.Button("Three")

.. image:: /_static/examples/column-weights-light.png
   :class: bs-screenshot-light
   :alt: Column proportional heights — light theme

.. image:: /_static/examples/column-weights-dark.png
   :class: bs-screenshot-dark
   :alt: Column proportional heights — dark theme

Spacer
~~~~~~

A :class:`Spacer <bootstack.Spacer>` is a local break that pushes its neighbors
apart — drop one in to send a footer to the bottom without fixing the column
height. Where ``vertical_items`` moves the *whole* group, a ``Spacer`` opens a
gap at *one* point.

.. code-block:: python

   with bs.Column(gap=6, height=150, horizontal_items="stretch"):
       bs.Button("Header")
       bs.Spacer()                       # pushes the footer to the bottom
       bs.Button("Footer")

.. image:: /_static/examples/column-spacer-light.png
   :class: bs-screenshot-light
   :alt: Column spacer — light theme

.. image:: /_static/examples/column-spacer-dark.png
   :class: bs-screenshot-dark
   :alt: Column spacer — dark theme

Background
~~~~~~~~~~

``surface=`` sets the container background. It accepts a surface token
(``'content'``, ``'card'``, ``'chrome'``, ``'overlay'``) or any accent token
(``'primary'``, ``'success'``, etc.) with optional modifiers:

.. code-block:: python

   with bs.Column(surface="card", padding=12, gap=8):
       bs.Label("Sits on card surface")

   with bs.Column(surface="primary[subtle]", padding=12, gap=8):
       bs.Label("Accent-tinted background")

Border
~~~~~~

``show_border=True`` draws a 1 px border along the inside edge of the frame.
Without padding, children render flush against it. Use at least ``padding=1``
to give the border visual clearance.

.. code-block:: python

   with bs.Column(gap=8, show_border=True, padding=8, horizontal_items="stretch"):
       bs.Button("A")
       bs.Button("B")
       bs.Button("C")

Self-placement
~~~~~~~~~~~~~~~

``horizontal``, ``vertical``, and ``grow`` control how the Column places *itself*
within its parent — separate from how it arranges its own children. In a
horizontal parent, ``grow=True`` lets a Column claim the leftover width — a fixed
sidebar beside a growing content area.

.. code-block:: python

   with bs.Row(gap=12, horizontal="stretch"):
       with bs.Column(gap=8, width=180):              # fixed-width sidebar
           bs.Button("Inbox"); bs.Button("Drafts")
       with bs.Column(grow=True, horizontal_items="stretch"):
           bs.Label("Content", font="heading-md")     # claims the rest

.. image:: /_static/examples/column-self-light.png
   :class: bs-screenshot-light
   :alt: Column self-placement — light theme

.. image:: /_static/examples/column-self-dark.png
   :class: bs-screenshot-dark
   :alt: Column self-placement — dark theme

Widget sizing
~~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

:class:`Row <bootstack.widgets.stacks.Row>` — horizontal equivalent.
:class:`Spacer <bootstack.widgets.stacks.Spacer>` — a composable break that
pushes neighbors apart.
:class:`Grid <bootstack.widgets.grid.Grid>` — row and column layout.
:class:`Card <bootstack.widgets.card.Card>` and
:class:`GroupBox <bootstack.widgets.groupbox.GroupBox>` — a Row/Column with
an elevated background or labelled border.

API
---

The complete reference for :class:`Column <bootstack.Column>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Column

Full Example
------------

.. literalinclude:: ../../docs/examples/column.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
