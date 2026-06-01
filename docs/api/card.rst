Card
====

A container that groups related content with an elevated background and border.
Uses the ``card`` surface token so the background steps up automatically from
the parent surface (``background`` → ``card`` → ``overlay``).

.. code-block:: python

   with bs.Card(accent="primary", padding=16, gap=8):
       bs.Label("Title", font="heading-md[bold]")
       bs.Label("Body text goes here.")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/card-light.png"
        alt="Card demo — light theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/card-dark.png"
        alt="Card demo — dark theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">

Usage
-----

Accent borders
~~~~~~~~~~~~~~

Pass an ``accent=`` token to tint the card border and give the interior a
subtle accent wash. Without ``accent=`` the card renders with a neutral border
and the next surface step.

.. code-block:: python

   with bs.Card(accent="primary", padding=12, gap=4):
       bs.Label("Primary")

   with bs.Card(accent="success", padding=12, gap=4):
       bs.Label("Success")

   with bs.Card(accent="danger", padding=12, gap=4):
       bs.Label("Danger")

Layout modes
~~~~~~~~~~~~

``layout='vstack'`` (default) stacks children vertically. ``'hstack'`` places
them side by side. ``'grid'`` arranges children in a column-row grid.

.. code-block:: python

   # Default vertical stack
   with bs.Card(gap=8):
       bs.Label("First")
       bs.Label("Second")

   # Horizontal stack
   with bs.Card(layout="hstack", gap=12, anchor_items="center"):
       bs.Label("A")
       bs.Label("B")

   # Grid — two equal columns
   with bs.Card(layout="grid", columns=[1, 1], gap=8, sticky_items="ew"):
       bs.Label("Name:")    ; bs.Label("Ada Lovelace")
       bs.Label("Role:")    ; bs.Label("Engineer")

Child defaults
~~~~~~~~~~~~~~

Use ``fill_items``, ``expand_items``, and ``anchor_items`` to set a default
layout behavior for all children without repeating it on each widget.

.. code-block:: python

   with bs.Card(gap=8, fill_items="x"):
       bs.TextField()   # fills horizontally — no fill="x" needed
       bs.TextField()

Nested cards
~~~~~~~~~~~~

Placing a ``Card`` inside another ``Card`` automatically advances the surface
token so each level has a visually distinct background.

.. code-block:: python

   with bs.Card(padding=12, gap=8):          # card surface
       bs.Label("Outer")
       with bs.Card(padding=8, gap=4):        # overlay surface
           bs.Label("Inner")

API
---

.. autoclass:: bootstack.widgets.card.Card
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/card.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs