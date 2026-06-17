Divider
=======

A thin themed line used to visually divide sections of a layout. Renders
horizontally by default and stretches to fill the available space. (For
*invisible* flexible space between items, use :class:`Spacer <bootstack.Spacer>`
instead.)

.. image:: /_static/examples/divider-hero-light.png
   :class: bs-screenshot-light
   :alt: Divider — light theme

.. image:: /_static/examples/divider-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Divider — dark theme

Usage
-----

Orientation
~~~~~~~~~~~

The default orientation is ``'horizontal'``. Pass ``orient='vertical'`` for a
vertical divider; use ``length=`` to constrain its height.

.. code-block:: python

   # Vertical divider between breadcrumb items
   with bs.Row(gap=12, vertical_items="center"):
       bs.Label("Home")
       bs.Divider(orient="vertical", length=16)
       bs.Label("Products")
       bs.Divider(orient="vertical", length=16)
       bs.Label("About")
       bs.Divider(orient="vertical", length=16)
       bs.Label("Contact")

.. image:: /_static/examples/divider-vertical-light.png
   :class: bs-screenshot-light
   :alt: Divider vertical — light theme

.. image:: /_static/examples/divider-vertical-dark.png
   :class: bs-screenshot-dark
   :alt: Divider vertical — dark theme

Accent colors
~~~~~~~~~~~~~

By default the line color is derived from the active surface. Pass an
``accent=`` token to apply a semantic color.

.. code-block:: python

   bs.Divider(accent="default")
   bs.Divider(accent="primary")
   bs.Divider(accent="secondary")
   bs.Divider(accent="info")
   bs.Divider(accent="success")
   bs.Divider(accent="warning")
   bs.Divider(accent="danger")

.. image:: /_static/examples/divider-accents-light.png
   :class: bs-screenshot-light
   :alt: Divider accents — light theme

.. image:: /_static/examples/divider-accents-dark.png
   :class: bs-screenshot-dark
   :alt: Divider accents — dark theme

Thickness
~~~~~~~~~

The default thickness is 1 px (theme-controlled). Use ``thickness=`` for a
heavier rule.

.. code-block:: python

   bs.Divider(accent="primary", thickness=1)
   bs.Divider(accent="primary", thickness=2)
   bs.Divider(accent="primary", thickness=4)

.. image:: /_static/examples/divider-thickness-light.png
   :class: bs-screenshot-light
   :alt: Divider thickness — light theme

.. image:: /_static/examples/divider-thickness-dark.png
   :class: bs-screenshot-dark
   :alt: Divider thickness — dark theme

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

:class:`Spacer <bootstack.widgets.stacks.Spacer>` — *invisible* flexible or
fixed space between items (a ``Divider`` draws a visible line; a ``Spacer``
opens a gap).

API
---

The complete reference for :class:`Divider <bootstack.Divider>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Divider

Full Example
------------

.. literalinclude:: ../../docs/examples/divider.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
