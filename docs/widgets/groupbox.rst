GroupBox
========

A labelled container that groups related content inside a bordered frame.
The title is embedded in the top border line, giving the classic fieldset
look familiar from HTML ``<fieldset>`` and desktop dialog panels.

.. image:: /_static/examples/groupbox-hero-light.png
   :class: bs-screenshot-light
   :alt: GroupBox — light theme

.. image:: /_static/examples/groupbox-hero-dark.png
   :class: bs-screenshot-dark
   :alt: GroupBox — dark theme

Usage
-----

A group box is a layout container with a titled border — the same
``layout=``/``gap=``/``padding=`` as a :doc:`Column <column>`, framed with a
caption set into the top edge. Reach for it to label a group of fields; an
unlabelled :doc:`card` when you just need a surface.

Accent borders
~~~~~~~~~~~~~~

Pass an ``accent=`` token to color the border and title label. The title text
automatically inherits the accent color.

.. code-block:: python

   for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
       with bs.GroupBox(accent.title(), accent=accent, padding=10, gap=4):
           bs.Label("Item one")
           bs.Label("Item two")
.. image:: /_static/examples/groupbox-accent-light.png
   :class: bs-screenshot-light
   :alt: GroupBox accent borders — light theme

.. image:: /_static/examples/groupbox-accent-dark.png
   :class: bs-screenshot-dark
   :alt: GroupBox accent borders — dark theme

Layout modes
~~~~~~~~~~~~

``layout='column'`` (default) stacks children vertically. ``'row'`` places
them side by side. ``'grid'`` arranges children in a column-row grid.

.. code-block:: python

   # Default vertical column
   with bs.GroupBox("Column (default)", gap=8):
       bs.Label("First")
       bs.Label("Second")
       bs.Label("Third")

   # Horizontal row
   with bs.GroupBox("Row", layout="row", gap=12, vertical_items="center"):
       bs.Label("A")
       bs.Label("B")
       bs.Label("C")

   # Grid — two columns, key/value pairs
   with bs.GroupBox("Grid", layout="grid", columns=[1, 1], gap=8, horizontal_items="stretch"):
       bs.Label("Name:")  ; bs.Label("Ada Lovelace")
       bs.Label("Role:")  ; bs.Label("Engineer")

.. image:: /_static/examples/groupbox-layout-light.png
   :class: bs-screenshot-light
   :alt: GroupBox layout modes — light theme

.. image:: /_static/examples/groupbox-layout-dark.png
   :class: bs-screenshot-dark
   :alt: GroupBox layout modes — dark theme

Child defaults
~~~~~~~~~~~~~~

Use ``horizontal_items``, ``vertical_items``, and ``grow_items`` to apply a
uniform layout behavior to all children without repeating it on each widget.

.. code-block:: python

   with bs.GroupBox("Filters", gap=8, horizontal_items="stretch"):
       bs.TextField()   # fills horizontally by default
       bs.TextField()

In context
~~~~~~~~~~

GroupBox is commonly used to visually separate settings panels or summary
sections within a larger form or dashboard.

.. code-block:: python

   with bs.GroupBox("Connection", accent="primary", padding=12, gap=8):
       with bs.Row(gap=8):
           bs.Label("Host:")
           bs.Label("localhost")
       with bs.Row(gap=8):
           bs.Label("Status:")
           bs.Label("Connected", accent="success")

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

:class:`Column <bootstack.widgets.stacks.Column>`,
:class:`Row <bootstack.widgets.stacks.Row>`, and
:class:`Grid <bootstack.widgets.grid.Grid>` are the plain (no border) layout
containers. Use ``GroupBox`` when you want a labelled border around a group
of related content.

API
---

The complete reference for :class:`GroupBox <bootstack.GroupBox>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.GroupBox

Full Example
------------

.. literalinclude:: ../../docs/examples/groupbox.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs