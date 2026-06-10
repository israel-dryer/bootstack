Badge
=====

A compact styled chip for status indicators, counts, and tags. Inherits all
``Label`` kwargs but renders with a fixed pill or square shape.

.. image:: /_static/examples/badge-hero-light.png
   :class: bs-screenshot-light
   :alt: Badge — light theme

.. image:: /_static/examples/badge-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Badge — dark theme

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
   bs.Badge("Info",      accent="info")
   bs.Badge("Success",   accent="success")
   bs.Badge("Warning",   accent="warning")
   bs.Badge("Danger",    accent="danger")

.. image:: /_static/examples/badge-accents-light.png
   :class: bs-screenshot-light
   :alt: Badge accent colors — light theme

.. image:: /_static/examples/badge-accents-dark.png
   :class: bs-screenshot-dark
   :alt: Badge accent colors — dark theme

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

.. image:: /_static/examples/badge-context-light.png
   :class: bs-screenshot-light
   :alt: Badge in context — light theme

.. image:: /_static/examples/badge-context-dark.png
   :class: bs-screenshot-dark
   :alt: Badge in context — dark theme

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

API
---

The complete reference for :class:`Badge <bootstack.Badge>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Badge

Full Example
------------

.. literalinclude:: ../../docs/examples/badge.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs