Separator
=========

A thin themed line used to visually divide sections of a layout. Renders
horizontally by default and stretches to fill the available space.

.. code-block:: python

   bs.Separator()
   bs.Separator(orient="vertical", length=24)
   bs.Separator(accent="primary", thickness=2)

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/separator-light.png"
        alt="Separator demo — light theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/separator-dark.png"
        alt="Separator demo — dark theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">

Usage
-----

Orientation
~~~~~~~~~~~

The default orientation is ``'horizontal'``. Pass ``orient='vertical'`` for a
vertical divider; use ``length=`` to constrain its height.

.. code-block:: python

   bs.Separator()                              # horizontal, full width
   bs.Separator(orient="vertical", length=24)  # vertical, 24 px tall

Accent colors
~~~~~~~~~~~~~

By default the line color is derived from the active surface. Pass an
``accent=`` token to apply a semantic color.

.. code-block:: python

   bs.Separator(accent="primary")
   bs.Separator(accent="success")
   bs.Separator(accent="danger")

Thickness
~~~~~~~~~

The default thickness is 1 px (theme-controlled). Use ``thickness=`` for a
heavier rule.

.. code-block:: python

   bs.Separator(thickness=2)
   bs.Separator(accent="warning", thickness=4)

In context
~~~~~~~~~~

Separators are typically placed between content blocks inside a
:class:`VStack <bootstack.widgets.stacks.VStack>` or between items in an
:class:`HStack <bootstack.widgets.stacks.HStack>`.

.. code-block:: python

   with bs.VStack(gap=12):
       bs.Label("Profile", font="heading-md[bold]")
       bs.Separator()
       bs.Label("Name: Ada Lovelace")

   # Vertical divider between breadcrumb items
   with bs.HStack(gap=8, anchor_items="center"):
       bs.Label("Home")
       bs.Separator(orient="vertical", length=16)
       bs.Label("Settings")

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