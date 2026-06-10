Separator
=========

A thin themed line used to visually divide sections of a layout. Renders
horizontally by default and stretches to fill the available space.

.. image:: /_static/examples/separator-hero-light.png
   :class: bs-screenshot-light
   :alt: Separator — light theme

.. image:: /_static/examples/separator-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Separator — dark theme

Usage
-----

Orientation
~~~~~~~~~~~

The default orientation is ``'horizontal'``. Pass ``orient='vertical'`` for a
vertical divider; use ``length=`` to constrain its height.

.. code-block:: python

   # Vertical divider between breadcrumb items
   with bs.HStack(gap=12, anchor_items="center"):
       bs.Label("Home")
       bs.Separator(orient="vertical", length=16)
       bs.Label("Products")
       bs.Separator(orient="vertical", length=16)
       bs.Label("About")
       bs.Separator(orient="vertical", length=16)
       bs.Label("Contact")

.. image:: /_static/examples/separator-vertical-light.png
   :class: bs-screenshot-light
   :alt: Separator vertical — light theme

.. image:: /_static/examples/separator-vertical-dark.png
   :class: bs-screenshot-dark
   :alt: Separator vertical — dark theme

Accent colors
~~~~~~~~~~~~~

By default the line color is derived from the active surface. Pass an
``accent=`` token to apply a semantic color.

.. code-block:: python

   bs.Separator(accent="default")
   bs.Separator(accent="primary")
   bs.Separator(accent="secondary")
   bs.Separator(accent="info")
   bs.Separator(accent="success")
   bs.Separator(accent="warning")
   bs.Separator(accent="danger")

.. image:: /_static/examples/separator-accents-light.png
   :class: bs-screenshot-light
   :alt: Separator accents — light theme

.. image:: /_static/examples/separator-accents-dark.png
   :class: bs-screenshot-dark
   :alt: Separator accents — dark theme

Thickness
~~~~~~~~~

The default thickness is 1 px (theme-controlled). Use ``thickness=`` for a
heavier rule.

.. code-block:: python

   bs.Separator(accent="primary", thickness=1)
   bs.Separator(accent="primary", thickness=2)
   bs.Separator(accent="primary", thickness=4)

.. image:: /_static/examples/separator-thickness-light.png
   :class: bs-screenshot-light
   :alt: Separator thickness — light theme

.. image:: /_static/examples/separator-thickness-dark.png
   :class: bs-screenshot-dark
   :alt: Separator thickness — dark theme

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

API
---

The complete reference for :class:`Separator <bootstack.Separator>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Separator

Full Example
------------

.. literalinclude:: ../../docs/examples/separator.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs