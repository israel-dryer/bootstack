SplitView
=========

A resizable split container. Panes are separated by draggable sashes that
can be moved at runtime to redistribute space.

.. image:: /_static/examples/splitview-hero-light.png
   :class: bs-screenshot-light
   :alt: SplitView — light theme

.. image:: /_static/examples/splitview-hero-dark.png
   :class: bs-screenshot-dark
   :alt: SplitView — dark theme

Usage
-----

Basic split
~~~~~~~~~~~

Call `.add()` once per pane. Use the returned value as a context manager
to place children inside that pane.

.. code-block:: python

   sv = bs.SplitView(grow=True)
   with sv.add():
       bs.Label("Pane 1")
   with sv.add():
       bs.Label("Pane 2")

Orientation
~~~~~~~~~~~

``orient='horizontal'`` (default) places panes side-by-side with a
vertical sash. ``orient='vertical'`` stacks panes top-to-bottom with a
horizontal sash.

.. code-block:: python

   # Stacked top-to-bottom with a horizontal sash
   sv = bs.SplitView(orient="vertical", grow=True)
   with sv.add(weight=1, padding=12, gap=4):
       bs.Label("Top pane", font="heading-md")
       bs.Label("Upper content area.")
   with sv.add(weight=1, padding=12, gap=4):
       bs.Label("Bottom pane", font="heading-md")
       bs.Label("Lower content area.")

.. image:: /_static/examples/splitview-vertical-light.png
   :class: bs-screenshot-light
   :alt: SplitView vertical — light theme

.. image:: /_static/examples/splitview-vertical-dark.png
   :class: bs-screenshot-dark
   :alt: SplitView vertical — dark theme

Pane weight
~~~~~~~~~~~

``weight=`` controls how space is distributed among panes when the
container is resized. A pane with ``weight=2`` takes twice the space of
one with ``weight=1``.

.. code-block:: python

   sv = bs.SplitView(grow=True)
   with sv.add(weight=1):   # one third
       ...
   with sv.add(weight=2):   # two thirds
       ...

Three or more panes
~~~~~~~~~~~~~~~~~~~

Call `.add()` for each pane. Each pair of adjacent panes gets its own
independently draggable sash.

.. code-block:: python

   sv = bs.SplitView(grow=True)
   with sv.add(weight=1):
       bs.Label("Left")
   with sv.add(weight=2):
       bs.Label("Center")
   with sv.add(weight=1):
       bs.Label("Right")

Managing panes
~~~~~~~~~~~~~~

`add()` returns a :class:`SplitPane <bootstack.widgets.splitview.SplitPane>`
handle. Give it a ``key=`` to address the pane later — look one up with
``item()``, enumerate them all with ``panes``, and drop one with ``remove()``.
The pane's ``weight`` is a live property, so you can re-balance the split at
runtime; for an exact sash position in pixels use ``sash_position()``.

.. code-block:: python

   sv = bs.SplitView(grow=True)
   with sv.add(key="sidebar", weight=1):
       bs.Label("Sidebar")
   with sv.add(key="main", weight=3):
       bs.Label("Main")

   sv.item("sidebar").weight = 2     # re-balance live
   sv.sash_position(0, 200)          # or place the sash exactly
   sv.remove("sidebar")              # drop a pane (and its content)

Pane layout
~~~~~~~~~~~

Each pane supports an independent internal layout via ``layout=``.

.. code-block:: python

   sv = bs.SplitView(grow=True)

   # Default: children stacked top-to-bottom
   with sv.add(layout="column", gap=8):
       bs.Label("Row 1")
       bs.Label("Row 2")

   # Children placed left-to-right
   with sv.add(layout="row", gap=8):
       bs.Label("Col A")
       bs.Label("Col B")

   # Grid layout
   with sv.add(layout="grid", columns=["auto", 1], gap=8, horizontal_items="stretch"):
       bs.Label("Name")
       bs.TextField()

Sash thickness
~~~~~~~~~~~~~~

``sash_thickness=`` sets the width (horizontal) or height (vertical) of
the draggable sash in pixels.

.. code-block:: python

   bs.SplitView(sash_thickness=2)   # hairline sash
   bs.SplitView(sash_thickness=10)  # wide, easy-to-grab sash

Sash control
~~~~~~~~~~~~

Read and set sash positions programmatically. Positions are measured in
pixels from the left (horizontal) or top (vertical) edge.

.. code-block:: python

   sv = bs.SplitView(grow=True)
   with sv.add(): ...
   with sv.add(): ...

   sv.sash_positions           # [240]  — current positions
   sv.sash_position(0, 300)    # move first sash to 300 px

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

:class:`ScrollView <bootstack.widgets.scrollview.ScrollView>` —
scrollable container.

:class:`Card <bootstack.widgets.card.Card>` and
:class:`GroupBox <bootstack.widgets.groupbox.GroupBox>` —
framed containers for use inside panes.

:class:`Column <bootstack.widgets.stacks.Column>`,
:class:`Row <bootstack.widgets.stacks.Row>`, and
:class:`Grid <bootstack.widgets.grid.Grid>` —
non-resizable layout containers.

API
---

The complete reference for :class:`SplitView <bootstack.SplitView>` and its
:class:`SplitPane <bootstack.SplitPane>` handles lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.SplitView
   ~bootstack.SplitPane

Full Example
------------

.. literalinclude:: ../../docs/examples/splitview.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
