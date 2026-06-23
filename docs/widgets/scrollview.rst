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

A ScrollView only scrolls once its size is **bounded** — otherwise it grows to
fit its content and never has overflow to scroll. Give it ``grow=True`` to fill
a sized parent, or a fixed ``height=``.

Basic vertical scroll
~~~~~~~~~~~~~~~~~~~~~

Children are packed top-to-bottom inside the scrollable area.

.. code-block:: python

   with bs.Column(grow=True, gap=8):
       bs.Label("Log output", font="heading-md")
       with bs.ScrollView(scroll_direction="vertical", grow=True, horizontal="stretch"):
           for line in log_lines:
               bs.Label(line)

You can also constrain the height directly with ``height=``:

.. code-block:: python

   with bs.ScrollView(height=200, horizontal="stretch"):
       for i in range(30):
           bs.Label(f"Item {i}")

Scroll direction
~~~~~~~~~~~~~~~~

``scroll_direction=`` controls which axis scrolls. ``'vertical'`` (default
for most use cases), ``'horizontal'``, or ``'both'``.

.. code-block:: python

   # Vertical only
   with bs.ScrollView(scroll_direction="vertical", grow=True):
       ...

   # Horizontal — useful for wide content like a row of buttons
   with bs.ScrollView(scroll_direction="horizontal", horizontal="stretch",
                      height=60, show_border=True):
       with bs.Row(gap=8, padding=8):
           for i in range(1, 20):
               bs.Button(f"Section {i:02d}", variant="outline")

   # Both axes
   with bs.ScrollView(scroll_direction="both", grow=True):
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

Scrollbar style
~~~~~~~~~~~~~~~

``scrollbar_variant=`` selects the bar style — ``'default'`` (the standard
rounded bar, used here) or ``'thin'`` (a slim square bar that suits compact
lists, panels, and popups). The list-style widgets (:class:`ListView
<bootstack.ListView>`, :class:`Tree <bootstack.Tree>`, :class:`Gallery
<bootstack.Gallery>`) default to ``'thin'``; ``ScrollView`` keeps the standard
bar by default since it is a general-purpose container.

.. code-block:: python

   with bs.ScrollView(scrollbar_variant="thin", grow=True):
       for i in range(30):
           bs.Label(f"Row {i:02d}")

.. image:: /_static/examples/scrollview-thin-light.png
   :class: bs-screenshot-light
   :alt: ScrollView thin scrollbar — light theme

.. image:: /_static/examples/scrollview-thin-dark.png
   :class: bs-screenshot-dark
   :alt: ScrollView thin scrollbar — dark theme

Border
~~~~~~

``show_border=True`` draws a 1 px border around the ScrollView frame.
Pair it with ``padding=`` to prevent content from sitting flush against
the border.

.. code-block:: python

   with bs.ScrollView(show_border=True, padding=4, grow=True):
       for i in range(30):
           bs.Label(f"Row {i}")

Programmatic scroll control
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Navigate content without user interaction:

.. code-block:: python

   sv = bs.ScrollView(grow=True)
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

Descendants added later — including a second pass through the context block —
are wired for wheel scrolling automatically as they lay out, so you normally
do not need to do anything. ``refresh_bindings()`` is a safety net for the rare
case where some new descendants miss scrolling after a large dynamic batch:

.. code-block:: python

   sv = bs.ScrollView()
   with sv:
       bs.Label("Static row")

   # Later, add more rows dynamically — wheel scrolling just works on them
   with sv:
       for i in range(100):
           bs.Label(f"Dynamic row {i}")

   sv.refresh_bindings()   # only if some rows missed scrolling

Scroll events and position
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``on_scroll()`` fires whenever the viewport moves — mouse-wheel, keyboard, or a
programmatic ``scroll_to_*`` / ``yview_moveto`` call. The handler receives a
:class:`~bootstack.events.ScrollEvent` with ``y`` and ``x`` fractions. Read
``scroll_position`` at any time for the same ``(y, x)`` pair.

.. code-block:: python

   sv = bs.ScrollView(grow=True)

   sv.on_scroll(lambda e: print(f"at {e.y:.0%} down, {e.x:.0%} across"))

   y, x = sv.scroll_position   # current position, e.g. (0.0, 0.0) at the top

Each fraction is the proportion of content scrolled past the viewport's top-left
edge: ``0.0`` at the start, climbing toward ``1.0`` as you near the end (it stops
short of ``1.0`` while content still fills the viewport). ``on_scroll()`` with no
handler returns a composable :class:`~bootstack.streams.Stream`, so you can
debounce a position readout. See :doc:`/reference/events` for the event model.

Keyboard scrolling
~~~~~~~~~~~~~~~~~~~

Once the canvas has keyboard focus (click inside it), arrow keys and the paging
keys scroll the viewport.

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Key
     - Action
   * - ``Up`` / ``Down``
     - Scroll one line vertically
   * - ``Left`` / ``Right``
     - Scroll one unit horizontally
   * - ``Page Up`` / ``Page Down``
     - Scroll one page vertically
   * - ``Home`` / ``End``
     - Jump to the top / bottom

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

:class:`Column <bootstack.widgets.stacks.Column>` —
non-scrolling vertical container.

:class:`Row <bootstack.widgets.stacks.Row>` —
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
