GroupBox
========

A labelled container that groups related content inside a bordered frame.
The title is embedded in the top border line, giving the classic fieldset
look familiar from HTML ``<fieldset>`` and desktop dialog panels.

.. code-block:: python

   with bs.GroupBox("Connection", accent="primary", padding=12, gap=8):
       bs.Label("Host: localhost")
       bs.Label("Port: 5432")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/groupbox-light.png"
        alt="GroupBox demo — light theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/groupbox-dark.png"
        alt="GroupBox demo — dark theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">

Usage
-----

Accent borders
~~~~~~~~~~~~~~

Pass an ``accent=`` token to color the border and title label. The title text
automatically inherits the accent color.

.. code-block:: python

   with bs.GroupBox("Primary", accent="primary", padding=12, gap=4):
       bs.Label("Content")

   with bs.GroupBox("Warning", accent="warning", padding=12, gap=4):
       bs.Label("Content")

Layout modes
~~~~~~~~~~~~

``layout='vstack'`` (default) stacks children vertically. ``'hstack'`` places
them side by side. ``'grid'`` arranges children in a column-row grid.

.. code-block:: python

   # Default vertical stack
   with bs.GroupBox("Details", gap=8):
       bs.Label("First")
       bs.Label("Second")

   # Horizontal stack
   with bs.GroupBox("Steps", layout="hstack", gap=12, anchor_items="center"):
       bs.Label("A")
       bs.Label("B")
       bs.Label("C")

   # Grid — two columns, key/value pairs
   with bs.GroupBox("Info", layout="grid", columns=[1, 1], gap=8, sticky_items="ew"):
       bs.Label("Name:")  ; bs.Label("Ada Lovelace")
       bs.Label("Role:")  ; bs.Label("Engineer")

Child defaults
~~~~~~~~~~~~~~

Use ``fill_items``, ``expand_items``, and ``anchor_items`` to apply a uniform
layout behavior to all children without repeating it on each widget.

.. code-block:: python

   with bs.GroupBox("Filters", gap=8, fill_items="x"):
       bs.TextField()   # fills horizontally by default
       bs.TextField()

In context
~~~~~~~~~~

GroupBox is commonly used to visually separate settings panels or summary
sections within a larger form or dashboard.

.. code-block:: python

   with bs.GroupBox("Connection", accent="primary", padding=12, gap=8):
       with bs.HStack(gap=8):
           bs.Label("Host:")
           bs.Label("localhost")
       with bs.HStack(gap=8):
           bs.Label("Status:")
           bs.Label("Connected", accent="success")

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

:class:`VStack <bootstack.widgets.stacks.VStack>`,
:class:`HStack <bootstack.widgets.stacks.HStack>`, and
:class:`Grid <bootstack.widgets.grid.Grid>` are the plain (no border) layout
containers. Use ``GroupBox`` when you want a labelled border around a group
of related content.

API
---

.. autoclass:: bootstack.widgets.groupbox.GroupBox
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/groupbox.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs