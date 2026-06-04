VStack
======

A container that stacks children top-to-bottom using the pack geometry manager.
Use ``gap=`` for even spacing, ``fill_items='x'`` to stretch children to the
full width, and ``fill='both', expand=True`` to let the stack grow with the window.

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/vstack-hero-light.png"
        alt="VStack — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/vstack-hero-dark.png"
        alt="VStack — dark theme"
        style="max-width:100%;">

Usage
-----

Gap
~~~

``gap=`` sets uniform spacing in pixels between children.

.. code-block:: python

    # gap=4 - items close together
    with bs.VStack(gap=4, show_border=True, padding=8):
        for i in range(1, 5):
            bs.Button(f"Item {i}")

    # gap=16 - items spread apart
    with bs.VStack(gap=16, show_border=True, padding=8):
        for i in range(1, 5):
            bs.Button(f"Item {i}")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/vstack-gap-light.png"
        alt="VStack gap — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/vstack-gap-dark.png"
        alt="VStack gap — dark theme"
        style="max-width:100%;">

Child fill
~~~~~~~~~~

``fill_items='x'`` stretches every child to the full container width. Individual
children can override this with their own ``fill=``.

.. code-block:: python

   with bs.VStack(gap=8, fill_items="x"):
       bs.TextField()          # fills horizontally by default
       bs.Button("Submit", accent="primary")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/vstack-fill-light.png"
        alt="VStack fill — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/vstack-fill-dark.png"
        alt="VStack fill — dark theme"
        style="max-width:100%;">

Child alignment
~~~~~~~~~~~~~~~

``anchor_items=`` controls horizontal alignment of children that do not fill
the full width. Use ``'w'`` (left), ``'center'``, or ``'e'`` (right).

.. code-block:: python

   with bs.VStack(gap=8, anchor_items="w",      show_border=True, padding=8, width=180, height=120):
       bs.Button("A"); bs.Button("B")

   with bs.VStack(gap=8, anchor_items="center", show_border=True, padding=8, width=180, height=120):
       bs.Button("A"); bs.Button("B")

   with bs.VStack(gap=8, anchor_items="e",      show_border=True, padding=8, width=180, height=120):
       bs.Button("A"); bs.Button("B")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/vstack-alignment-light.png"
        alt="VStack alignment — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/vstack-alignment-dark.png"
        alt="VStack alignment — dark theme"
        style="max-width:100%;">

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

Background
~~~~~~~~~~

``surface=`` sets the container background. It accepts a surface token
(``'content'``, ``'card'``, ``'chrome'``, ``'overlay'``) or any accent token
(``'primary'``, ``'success'``, etc.) with optional modifiers:

.. code-block:: python

   with bs.VStack(surface="card", padding=12, gap=8):
       bs.Label("Sits on card surface")

   with bs.VStack(surface="primary[subtle]", padding=12, gap=8):
       bs.Label("Accent-tinted background")

Border
~~~~~~

``show_border=True`` draws a 1 px border along the inside edge of the frame.
Without padding, children render flush against it. Use at least ``padding=1``
to give the border visual clearance.

.. code-block:: python

   with bs.VStack(gap=8, show_border=True, padding=8):
       bs.Label("Bordered section")
       bs.Button("Action")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/vstack-border-light.png"
        alt="VStack border — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/vstack-border-dark.png"
        alt="VStack border — dark theme"
        style="max-width:100%;">

Self-placement
~~~~~~~~~~~~~~

``fill=``, ``expand=``, and ``anchor=`` control how the VStack itself is placed
within its parent — separate from how it arranges its own children.

.. code-block:: python

   # Fill the parent and grow with the window
   with bs.VStack(fill="both", expand=True, gap=8):
       bs.Label("Grows with window")

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

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