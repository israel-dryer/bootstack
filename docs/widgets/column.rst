Column
======

A container that arranges children top to bottom along the vertical axis.
Use ``gap=`` for even spacing, ``vertical_items=`` to arrange the whole group
(``'top'``, ``'center'``, ``'bottom'``, or a ``'space-*'`` mode),
``horizontal_items=`` to align children left and right (use ``'stretch'`` for a
full-width form column), and ``grow`` / ``weights`` to let children share the
available height. Drop a :class:`Spacer <bootstack.Spacer>` between children to
push a footer down without a fixed height.

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

.. code-block:: python

   with bs.Column(vertical_items="space-between", height=140,
                  show_border=True, padding=8, horizontal_items="stretch"):
       bs.Button("Header")
       bs.Button("Footer")

.. image:: /_static/examples/column-arrange-light.png
   :class: bs-screenshot-light
   :alt: Column arrangement — light theme

.. image:: /_static/examples/column-arrange-dark.png
   :class: bs-screenshot-dark
   :alt: Column arrangement — dark theme

Growing children
~~~~~~~~~~~~~~~~~

``grow`` lets a child claim and fill the leftover height — useful for a content
area between a fixed header and footer. ``weights=[1, 2, 1]`` sizes children in
a fixed ratio.

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

``grow``, ``horizontal``, and ``vertical`` control how the Column *itself* is
placed within its parent — separate from how it arranges its own children. In a
horizontal parent, ``grow=True`` lets a Column claim the leftover width.

.. code-block:: python

   # A sidebar column beside a growing content area
   with bs.Row(gap=12, horizontal="stretch"):
       with bs.Column(gap=8, width=200):
           bs.Button("Inbox"); bs.Button("Drafts")
       with bs.Column(grow=True, horizontal_items="stretch"):
           bs.Label("Content", font="heading-md")

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
