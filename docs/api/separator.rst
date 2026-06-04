Separator
=========

A thin themed line used to visually divide sections of a layout. Renders
horizontally by default and stretches to fill the available space.

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/separator-hero-light.png"
        alt="Separator — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/separator-hero-dark.png"
        alt="Separator — dark theme"
        style="max-width:100%;">

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

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/separator-vertical-light.png"
        alt="Separator vertical — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/separator-vertical-dark.png"
        alt="Separator vertical — dark theme"
        style="max-width:100%;">

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

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/separator-accents-light.png"
        alt="Separator accents — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/separator-accents-dark.png"
        alt="Separator accents — dark theme"
        style="max-width:100%;">

Thickness
~~~~~~~~~

The default thickness is 1 px (theme-controlled). Use ``thickness=`` for a
heavier rule.

.. code-block:: python

   bs.Separator(accent="primary", thickness=1)
   bs.Separator(accent="primary", thickness=2)
   bs.Separator(accent="primary", thickness=4)

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/separator-thickness-light.png"
        alt="Separator thickness — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/separator-thickness-dark.png"
        alt="Separator thickness — dark theme"
        style="max-width:100%;">

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

API
---

.. autoclass:: bootstack.widgets.separator.Separator
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/separator.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs