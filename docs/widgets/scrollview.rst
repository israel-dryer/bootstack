ScrollView
==========

A canvas-backed scrollable container. Place child widgets inside the context
block; they are stacked vertically inside the scrollable area by default.
Mouse-wheel scrolling is automatically enabled for all descendants.

.. image:: /_static/examples/scrollview-hero-light.png
   :class: bs-screenshot-light
   :alt: ScrollView — light theme

.. image:: /_static/examples/scrollview-hero-dark.png
   :class: bs-screenshot-dark
   :alt: ScrollView — dark theme

Usage
-----

Basic vertical scroll
~~~~~~~~~~~~~~~~~~~~~

Children are packed top-to-bottom inside the scrollable area. Add
``fill="both", expand=True`` to let the ScrollView fill its parent and
provide a height boundary for scrolling to begin.

.. code-block:: python

   with bs.VStack(fill="both", expand=True, gap=8):
       bs.Label("Log output", font="heading-md")
       with bs.ScrollView(scroll_direction="vertical", fill="both", expand=True):
           for line in log_lines:
               bs.Label(line)

You can also constrain the height directly with ``height=``:

.. code-block:: python

   with bs.ScrollView(height=200, fill="x"):
       for i in range(30):
           bs.Label(f"Item {i}")

Scroll direction
~~~~~~~~~~~~~~~~

``scroll_direction=`` controls which axis scrolls. ``'vertical'`` (default
for most use cases), ``'horizontal'``, or ``'both'``.

.. code-block:: python

   # Vertical only
   with bs.ScrollView(scroll_direction="vertical", fill="both", expand=True):
       ...

   # Horizontal — useful for wide content like a row of cards
   with bs.ScrollView(scroll_direction="horizontal", fill="x"):
       with bs.HStack(gap=8, padding=8):
           for card in cards:
               bs.Card(...)

   # Both axes
   with bs.ScrollView(scroll_direction="both", fill="both", expand=True):
       ...

.. image:: /_static/examples/scrollview-horizontal-light.png
   :class: bs-screenshot-light
   :alt: ScrollView horizontal — light theme

.. image:: /_static/examples/scrollview-horizontal-dark.png
   :class: bs-screenshot-dark
   :alt: ScrollView horizontal — dark theme

.. note::

   Shift + scroll wheel scrolls horizontally on all platforms.

Scrollbar visibility
~~~~~~~~~~~~~~~~~~~~

``scrollbar_visibility=`` controls when the scrollbars appear.

.. list-table::
   :widths: 15 85

   * - ``'always'``
     - Scrollbars are always visible (default).
   * - ``'never'``
     - Scrollbars are always hidden; scrolling still works via mouse wheel.
   * - ``'hover'``
     - Scrollbars appear when the mouse enters the widget.
   * - ``'scroll'``
     - Scrollbars appear while scrolling, then auto-hide after
       ``autohide_delay`` ms of inactivity.

.. code-block:: python

   # Always-visible scrollbar (default)
   bs.ScrollView(scrollbar_visibility="always")

   # Hidden scrollbar — content scrolls via mouse wheel
   bs.ScrollView(scrollbar_visibility="never")

   # Scrollbar appears on hover
   bs.ScrollView(scrollbar_visibility="hover")

   # Scrollbar appears during scroll, hides after 1.5 s
   bs.ScrollView(scrollbar_visibility="scroll", autohide_delay=1500)

Border
~~~~~~

``show_border=True`` draws a 1 px border around the ScrollView frame.
Pair it with ``padding=`` to prevent content from sitting flush against
the border.

.. code-block:: python

   with bs.ScrollView(show_border=True, padding=4, fill="both", expand=True):
       for i in range(30):
           bs.Label(f"Row {i}")

Programmatic scroll control
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Navigate content without user interaction:

.. code-block:: python

   sv = bs.ScrollView(fill="both", expand=True)
   with sv:
       ...

   sv.scroll_to_top()        # jump to top
   sv.scroll_to_bottom()     # jump to bottom
   sv.scroll_to_left()       # jump to left edge
   sv.scroll_to_right()      # jump to right edge

   sv.yview_moveto(0.5)      # 50 % of the way down
   sv.xview_moveto(0.25)     # 25 % of the way across

Mouse-wheel scrolling
~~~~~~~~~~~~~~~~~~~~~

Mouse-wheel scrolling is enabled automatically for the canvas and all
descendants. To toggle it programmatically:

.. code-block:: python

   sv.disable_scrolling()    # pause scrolling
   sv.enable_scrolling()     # resume

After adding a large batch of widgets dynamically (outside the context
block), call ``refresh_bindings()`` to ensure all new descendants are
wired up:

.. code-block:: python

   sv = bs.ScrollView()
   with sv:
       bs.Label("Static row")

   # Later, add more rows dynamically
   with sv:
       for i in range(100):
           bs.Label(f"Dynamic row {i}")
   sv.refresh_bindings()

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

:class:`VStack <bootstack.widgets.stacks.VStack>` —
non-scrolling vertical container.

:class:`HStack <bootstack.widgets.stacks.HStack>` —
non-scrolling horizontal container.

:class:`Card <bootstack.widgets.card.Card>` and
:class:`GroupBox <bootstack.widgets.groupbox.GroupBox>` —
framed containers that can be combined with ScrollView.

API
---

The complete reference for :class:`ScrollView <bootstack.ScrollView>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.ScrollView

Full Example
------------

.. literalinclude:: ../../docs/examples/scrollview.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
