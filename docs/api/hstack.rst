HStack
======

A container that places children left-to-right using the pack geometry manager.
Use ``gap=`` for even spacing, ``anchor_items='center'`` to vertically center
mixed-height widgets, and ``fill_items='y'`` to stretch children to the full
row height.

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/hstack-light.png"
        alt="HStack demo — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/hstack-dark.png"
        alt="HStack demo — dark theme"
        style="max-width:100%;">

Usage
-----

Gap
~~~

``gap=`` sets uniform spacing in pixels between children.

.. code-block:: python

   with bs.HStack(gap=12):
       bs.Button("Cancel")
       bs.Button("OK", accent="primary")

Child alignment
~~~~~~~~~~~~~~~

``anchor_items=`` controls vertical alignment of children within the row.
Use ``'center'`` to align mixed-height widgets (e.g. a label next to a text
field), ``'n'`` for top, or ``'s'`` for bottom.

.. code-block:: python

   with bs.HStack(gap=8, anchor_items="center"):
       bs.Label("Label")      # shorter
       bs.TextField()         # taller — both centered vertically

Child fill
~~~~~~~~~~

``fill_items='y'`` stretches every child to the full row height. Useful for
making buttons or panels match the height of the tallest sibling.

.. code-block:: python

   with bs.HStack(gap=8, fill_items="y", height=60):
       bs.Button("A")   # stretches to 60 px tall
       bs.Button("B")

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

Border
~~~~~~

``show_border=True`` draws a 1 px border along the inside edge of the frame.
Without padding, children render flush against it. Use at least ``padding=1``
to give the border visual clearance.

.. code-block:: python

   with bs.HStack(gap=8, show_border=True, padding=8):
       bs.Button("A")
       bs.Button("B")

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