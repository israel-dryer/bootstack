Card
====

A container that groups related content with an elevated background and border.
Cards automatically step the background surface at each nesting level,
alternating between ``card`` and ``card_raised`` to keep adjacent levels
visually distinct without runaway drift.

.. image:: /_static/examples/card-hero-light.png
   :class: bs-screenshot-light
   :alt: Card — light theme

.. image:: /_static/examples/card-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Card — dark theme

Usage
-----

Accents
~~~~~~~

Pass an ``accent=`` token to tint the card border and give the interior a
subtle accent wash. Without ``accent=`` the card renders with a neutral border
and the next surface step.

.. code-block:: python

   for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
       with bs.Card(accent=accent, padding=24, gap=4):
           bs.Label(accent.title(), accent=accent, font="heading-sm")
           bs.Label("Card content")

.. image:: /_static/examples/card-accent-light.png
   :class: bs-screenshot-light
   :alt: Card accent borders — light theme

.. image:: /_static/examples/card-accent-dark.png
   :class: bs-screenshot-dark
   :alt: Card accent borders — dark theme

Layout modes
~~~~~~~~~~~~

``layout='column'`` (default) stacks children vertically. ``'row'`` places
them side by side. ``'grid'`` arranges children in a column-row grid.

.. code-block:: python

    # Default vertical stack
    with bs.Card(padding=12, gap=8):
        bs.Label("Column (default)", font="heading-sm")
        bs.Label("First item")
        bs.Label("Second item")
        bs.Label("Third item")

    # Horizontal row
    with bs.Card(layout="row", padding=12, gap=12, vertical_items="center"):
        bs.Label("Row", font="heading-sm")
        bs.Label("A")
        bs.Label("B")
        bs.Label("C")

    # Grid - two equally weighted columns
    with bs.Card(layout="grid", columns=2, padding=12, gap=8, horizontal_items="stretch"):
        bs.Label("Grid", font="heading-sm")
        bs.Label("2 cols")
        bs.Label("Item A")
        bs.Label("Item B")
        bs.Label("Item C")
        bs.Label("Item D")

.. image:: /_static/examples/card-layout-light.png
   :class: bs-screenshot-light
   :alt: Card layout modes — light theme

.. image:: /_static/examples/card-layout-dark.png
   :class: bs-screenshot-dark
   :alt: Card layout modes — dark theme

Child defaults
~~~~~~~~~~~~~~

Use ``horizontal_items``, ``vertical_items``, and ``grow_items`` to set a
default layout behavior for all children without repeating it on each widget.

.. code-block:: python

   with bs.Card(gap=8, horizontal_items="stretch"):
       bs.TextField()   # fills horizontally — no horizontal="stretch" needed
       bs.TextField()

Nested cards
~~~~~~~~~~~~

Neutral cards alternate between the ``card`` and ``card_raised`` surface tokens
at each nesting level — the first card steps to ``card``, the next to
``card_raised``, the next back to ``card``, and so on. Every level is visually
distinct from its parent regardless of nesting depth.

Accent cards behave differently: the ``accent[subtle]`` tint is fixed and does
not change with depth. The accent color is the identity signal — elevation
stepping is not applied.

.. code-block:: python

    with bs.Card(padding=50):
        with bs.Card(padding=50):
            with bs.Card(padding=50):
                bs.Label("Nested Cards")

.. image:: /_static/examples/card-nested-light.png
   :class: bs-screenshot-light
   :alt: Card nested — light theme

.. image:: /_static/examples/card-nested-dark.png
   :class: bs-screenshot-dark
   :alt: Card nested — dark theme

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

:class:`Column <bootstack.widgets.stacks.Column>`,
:class:`Row <bootstack.widgets.stacks.Row>`, and
:class:`Grid <bootstack.widgets.grid.Grid>` are the plain (no border, no
surface) layout containers. Use ``Card`` when you want an elevated
background and border around a group of content.

API
---

The complete reference for :class:`Card <bootstack.Card>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Card

Full Example
------------

.. literalinclude:: ../../docs/examples/card.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs