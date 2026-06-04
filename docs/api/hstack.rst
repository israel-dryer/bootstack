HStack
======

A container that places children left-to-right using the pack geometry manager.
Use ``gap=`` for even spacing, ``anchor_items='center'`` to vertically center
mixed-height widgets, and ``fill_items='y'`` to stretch children to the full
row height.

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/hstack-hero-light.png"
        alt="HStack — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/hstack-hero-dark.png"
        alt="HStack — dark theme"
        style="max-width:100%;">

Usage
-----

Gap
~~~

``gap=`` sets uniform spacing in pixels between children.

.. code-block:: python

   # gap=4 — items close together
   with bs.HStack(gap=4, show_border=True, padding=8, fill="x"):
       for i in range(1, 4):
           bs.Button(f"Item {i}")

   # gap=24 — items spread apart
   with bs.HStack(gap=24, show_border=True, padding=8, fill="x"):
       for i in range(1, 4):
           bs.Button(f"Item {i}")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/hstack-gap-light.png"
        alt="HStack gap — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/hstack-gap-dark.png"
        alt="HStack gap — dark theme"
        style="max-width:100%;">

Child alignment
~~~~~~~~~~~~~~~

``anchor_items=`` controls vertical alignment of children within the row.
Use ``'center'`` to align mixed-height widgets (e.g. a label next to a text
field), ``'n'`` for top, or ``'s'`` for bottom.

.. code-block:: python

   with bs.HStack(gap=8, anchor_items="n",      show_border=True, padding=8, height=80):
       bs.Button("A"); bs.Button("B")

   with bs.HStack(gap=8, anchor_items="center", show_border=True, padding=8, height=80):
       bs.Button("A"); bs.Button("B")

   with bs.HStack(gap=8, anchor_items="s",      show_border=True, padding=8, height=80):
       bs.Button("A"); bs.Button("B")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/hstack-alignment-light.png"
        alt="HStack alignment — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/hstack-alignment-dark.png"
        alt="HStack alignment — dark theme"
        style="max-width:100%;">

Child fill
~~~~~~~~~~

``fill_items='y'`` stretches every child to the full row height. Useful for
making buttons or panels match the height of the tallest sibling.

.. code-block:: python

   with bs.HStack(gap=8, fill_items="y", height=60):
       bs.Button("A")   # stretches to 60 px tall
       bs.Button("B")
       bs.Button("C")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/hstack-fill-light.png"
        alt="HStack fill — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/hstack-fill-dark.png"
        alt="HStack fill — dark theme"
        style="max-width:100%;">

Fixed height
~~~~~~~~~~~~

.. note::

   ``height=`` and ``width=`` fix the container size and prevent children
   from resizing it. Setting **both** is the simplest path — the frame is
   fully constrained and works without any extra kwargs:

   .. code-block:: python

      with bs.HStack(height=200, width=300, show_border=True):
          bs.Button("Fully fixed", anchor="center")

   When only **one** dimension is set, the other axis collapses to zero.
   Add ``fill=`` and ``expand=`` to let the parent control the open axis:

   .. code-block:: python

      # height only — width comes from parent
      with bs.HStack(height=80, fill="x", expand=True, gap=8):
          bs.Button("Fixed height, flexible width")

Background
~~~~~~~~~~

``surface=`` sets the container background. It accepts a surface token
(``'content'``, ``'card'``, ``'chrome'``, ``'overlay'``) or any accent token
(``'primary'``, ``'success'``, etc.) with optional modifiers:

.. code-block:: python

   with bs.HStack(surface="card", padding=12, gap=8):
       bs.Label("Sits on card surface")

   with bs.HStack(surface="primary[subtle]", padding=12, gap=8):
       bs.Label("Accent-tinted background")

Border
~~~~~~

``show_border=True`` draws a 1 px border along the inside edge of the frame.
Without padding, children render flush against it. Use at least ``padding=1``
to give the border visual clearance.

.. code-block:: python

   with bs.HStack(gap=8, show_border=True, padding=8):
       bs.Button("A")
       bs.Button("B")
       bs.Button("C")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/hstack-border-light.png"
        alt="HStack border — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/hstack-border-dark.png"
        alt="HStack border — dark theme"
        style="max-width:100%;">

Self-placement
~~~~~~~~~~~~~~

``fill=``, ``expand=``, and ``anchor=`` control how the HStack itself is placed
within its parent — separate from how it arranges its own children.

.. code-block:: python

   # Toolbar row that fills the window width
   with bs.HStack(gap=8, fill="x", anchor_items="center"):
       bs.Button("File")
       bs.Button("Edit")
       bs.Button("View")

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

:class:`VStack <bootstack.widgets.stacks.VStack>` — vertical equivalent.
:class:`Grid <bootstack.widgets.grid.Grid>` — row and column layout.
:class:`Card <bootstack.widgets.card.Card>` and
:class:`GroupBox <bootstack.widgets.groupbox.GroupBox>` — VStack/HStack with
an elevated background or labelled border.

API
---

.. autoclass:: bootstack.widgets.stacks.HStack
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/hstack.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs