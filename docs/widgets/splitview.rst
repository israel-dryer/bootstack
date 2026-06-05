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

   sv = bs.SplitView(fill="both", expand=True)
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

   # Side-by-side (default)
   sv = bs.SplitView(orient="horizontal", fill="both", expand=True)

   # Stacked
   sv = bs.SplitView(orient="vertical", fill="both", expand=True)

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

   sv = bs.SplitView(fill="both", expand=True)
   with sv.add(weight=1):   # one third
       ...
   with sv.add(weight=2):   # two thirds
       ...

Three or more panes
~~~~~~~~~~~~~~~~~~~

Call `.add()` for each pane. Each pair of adjacent panes gets its own
independently draggable sash.

.. code-block:: python

   sv = bs.SplitView(fill="both", expand=True)
   with sv.add(weight=1):
       bs.Label("Left")
   with sv.add(weight=2):
       bs.Label("Center")
   with sv.add(weight=1):
       bs.Label("Right")

Minimum pane size
~~~~~~~~~~~~~~~~~

``min_size=`` prevents a sash from being dragged so far that the pane
collapses below the given pixel width (or height for vertical splits).

.. code-block:: python

   sv = bs.SplitView(fill="both", expand=True)
   with sv.add(min_size=120):
       bs.Label("Cannot shrink below 120 px")
   with sv.add():
       bs.Label("Unconstrained pane")

Pane layout
~~~~~~~~~~~

Each pane supports an independent internal layout via ``layout=``.

.. code-block:: python

   sv = bs.SplitView(fill="both", expand=True)

   # Default: children stacked top-to-bottom
   with sv.add(layout="vstack", gap=8):
       bs.Label("Row 1")
       bs.Label("Row 2")

   # Children placed left-to-right
   with sv.add(layout="hstack", gap=8):
       bs.Label("Col A")
       bs.Label("Col B")

   # Grid layout
   with sv.add(layout="grid", columns=["auto", 1], gap=8, sticky_items="ew"):
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

   sv = bs.SplitView(fill="both", expand=True)
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

:class:`VStack <bootstack.widgets.stacks.VStack>`,
:class:`HStack <bootstack.widgets.stacks.HStack>`, and
:class:`Grid <bootstack.widgets.grid.Grid>` —
non-resizable layout containers.

API
---

.. autoclass:: bootstack.widgets.splitview.SplitView
   :members:
   :undoc-members:

.. autoclass:: bootstack.widgets.splitview.SplitPane
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/splitview.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
