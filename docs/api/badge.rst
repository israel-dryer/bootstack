Badge
=====

A compact styled chip for status indicators, counts, and tags. Inherits all
``Label`` kwargs but renders with a fixed pill or square shape.

.. code-block:: python

   bs.Badge("New",      accent="success", variant="pill")
   bs.Badge("99+",      accent="danger",  variant="pill")
   bs.Badge("Complete", accent="success")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/badge-light.png"
        alt="Badge demo — light theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/badge-dark.png"
        alt="Badge demo — dark theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">

Usage
-----

Variants
~~~~~~~~

``'square'`` (default) gives a rounded rectangle. ``'pill'`` gives a fully
rounded capsule shape, common for counts and status tags.

.. code-block:: python

   bs.Badge("Square",  accent="primary")
   bs.Badge("Pill",    accent="primary", variant="pill")
   bs.Badge("99+",     accent="danger",  variant="pill")

Accent colors
~~~~~~~~~~~~~

.. code-block:: python

   bs.Badge("Primary",   accent="primary")
   bs.Badge("Secondary", accent="secondary")
   bs.Badge("Success",   accent="success")
   bs.Badge("Warning",   accent="warning")
   bs.Badge("Danger",    accent="danger")

In context
~~~~~~~~~~

Badges are commonly placed inline with other widgets — next to a title,
in a table cell, or in a sidebar item.

.. code-block:: python

   # Next to a heading
   with bs.HStack(gap=8, anchor_items="center"):
       bs.Label("Inbox", font="heading-md")
       bs.Badge("12", accent="primary", variant="pill")

   # Status in a data row
   with bs.HStack(gap=8, anchor_items="center"):
       bs.Label("Run-A15")
       bs.Badge("Complete", accent="success", variant="pill")
       bs.Badge("2 warnings", accent="warning")

API
---

.. autoclass:: bootstack.widgets.label.Badge
   :members:
   :undoc-members:

Full Example
------------

Run with ``python docs/examples/badge.py``.

.. literalinclude:: ../../docs/examples/badge.py
   :language: python
   :start-after: import bootstack as bs
