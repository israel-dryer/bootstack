VStack
======

A container that stacks children top-to-bottom using the pack geometry manager.
Use ``gap=`` for even spacing, ``fill_items='x'`` to stretch children to the
full width, and ``fill='both', expand=True`` to let the stack grow with the window.

.. code-block:: python

   with bs.VStack(gap=12, fill_items="x", padding=16):
       bs.Label("Title", font="heading-md[bold]")
       bs.TextField()
       bs.Button("Submit", accent="primary")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/vstack-light.png"
        alt="VStack demo — light theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/vstack-dark.png"
        alt="VStack demo — dark theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">

Usage
-----

Gap
~~~

``gap=`` sets uniform spacing in pixels between children.

.. code-block:: python

   with bs.VStack(gap=8):
       bs.Label("First")
       bs.Label("Second")   # 8 px below First

Child fill
~~~~~~~~~~

``fill_items='x'`` stretches every child to the full container width. Individual
children can override this with their own ``fill=``.

.. code-block:: python

   with bs.VStack(gap=8, fill_items="x"):
       bs.TextField()          # fills horizontally by default
       bs.Button("Submit", accent="primary")

Child alignment
~~~~~~~~~~~~~~~

``anchor_items=`` controls horizontal alignment of children that do not fill
the full width. Use ``'w'`` (left), ``'center'``, or ``'e'`` (right).

.. code-block:: python

   with bs.VStack(gap=8, anchor_items="center"):
       bs.Button("Centered")
       bs.Button("Also centered")

Fixed height
~~~~~~~~~~~~

.. note::

   ``height=`` and ``width=`` fix the container size and prevent children
   from resizing it. Setting **both** is the simplest path — the frame is
   fully constrained and works without any extra kwargs:

   .. code-block:: python

      with bs.VStack(height=200, width=300, show_border=True):
          bs.Button("Fully fixed")

   When only **one** dimension is set, the other axis collapses to zero.
   Add ``fill=`` and ``expand=`` to let the parent control the open axis:

   .. code-block:: python

      # height only — width comes from parent
      with bs.VStack(height=120, fill="x", gap=8):
          bs.Button("Fixed height, fills parent width")

.. code-block:: python

   with bs.VStack(height=120, gap=8, anchor_items="center"):
       bs.Label("Fixed 120 px tall, fills parent width")

Border
~~~~~~

``show_border=True`` draws a 1 px border along the inside edge of the frame.
Without padding, children render flush against it. Use at least ``padding=1``
to give the border visual clearance.

.. code-block:: python

   with bs.VStack(gap=8, show_border=True, padding=8):
       bs.Label("Bordered section")
       bs.Button("Action")

Self-placement
~~~~~~~~~~~~~~

``fill=``, ``expand=``, and ``anchor=`` control how the VStack itself is placed
within its parent — separate from how it arranges its own children.

.. code-block:: python

   # Fill the parent and grow with the window
   with bs.VStack(fill="both", expand=True, gap=8):
       bs.Label("Grows with window")

See also
--------

:class:`HStack <bootstack.widgets.stacks.HStack>` — horizontal equivalent.
:class:`Grid <bootstack.widgets.grid.Grid>` — row and column layout.
:class:`Card <bootstack.widgets.card.Card>` and
:class:`GroupBox <bootstack.widgets.groupbox.GroupBox>` — VStack with an
elevated background or labelled border.

API
---

.. autoclass:: bootstack.widgets.stacks.VStack
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/vstack.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs