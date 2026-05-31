Button
======

A clickable action trigger. Accepts the button label as the first positional
argument.

.. code-block:: python

   bs.Button("Save", accent="primary", on_click=handle_save)

Usage
-----

Accent colors
~~~~~~~~~~~~~

Use ``accent=`` to express intent. The button renders correctly across all
themes without hard-coding any color.

.. code-block:: python

   with bs.HStack(gap=8):
       bs.Button("Default")
       bs.Button("Primary",  accent="primary")
       bs.Button("Success",  accent="success")
       bs.Button("Warning",  accent="warning")
       bs.Button("Danger",   accent="danger")
       bs.Button("Secondary",accent="secondary")

Style variants
~~~~~~~~~~~~~~

Use ``variant=`` to control visual weight. Useful for distinguishing primary
actions from secondary ones.

.. code-block:: python

   with bs.HStack(gap=8):
       bs.Button("Solid",   accent="primary", variant="solid")
       bs.Button("Outline", accent="primary", variant="outline")
       bs.Button("Ghost",   accent="primary", variant="ghost")

Icons
~~~~~

Pass any `Bootstrap Icons <https://icons.getbootstrap.com>`_ name to ``icon=``.
The icon appears to the left of the label by default.

.. code-block:: python

   bs.Button("Save",   icon="save")
   bs.Button("Delete", icon="trash", accent="danger")
   bs.Button("Export", icon="download", accent="secondary", variant="outline")

Icon-only
~~~~~~~~~

Set ``icon_only=True`` to show just the icon with no label text. Use for
compact toolbars and action rows.

.. code-block:: python

   with bs.HStack(gap=4):
       bs.Button(icon="plus-lg",  icon_only=True, accent="success")
       bs.Button(icon="dash-lg",  icon_only=True, accent="danger")
       bs.Button(icon="pencil",   icon_only=True, accent="secondary", variant="outline")

Disabled state
~~~~~~~~~~~~~~

.. code-block:: python

   bs.Button("Disabled Solid",   accent="primary",  disabled=True)
   bs.Button("Disabled Outline", accent="primary",   variant="outline", disabled=True)

Handling clicks
~~~~~~~~~~~~~~~

Pass a callable to ``on_click=``. The callback receives no arguments.

.. code-block:: python

   def handle_save():
       print("Saved!")

   bs.Button("Save", accent="primary", on_click=handle_save)

   # Or inline with a lambda
   bs.Button("Cancel", on_click=lambda: print("Cancelled"))

API
---

.. autoclass:: bootstack.widgets.button.Button
   :members:
   :undoc-members:

Full Example
------------

A complete runnable app demonstrating all Button features.

.. code-block:: python

   import bootstack as bs

   with bs.App(title="Button Demo", padding=20, gap=16) as app:

       bs.Label("Accent Colors", font="heading-sm[bold]")
       with bs.HStack(gap=8):
           for accent in ("primary", "secondary", "success", "warning", "danger"):
               bs.Button(accent.title(), accent=accent)

       bs.Label("Style Variants", font="heading-sm[bold]")
       with bs.HStack(gap=8):
           bs.Button("Solid",   accent="primary", variant="solid")
           bs.Button("Outline", accent="primary", variant="outline")
           bs.Button("Ghost",   accent="primary", variant="ghost")

       bs.Label("Icons", font="heading-sm[bold]")
       with bs.HStack(gap=8):
           bs.Button("Save",   icon="save")
           bs.Button("Delete", icon="trash",    accent="danger")
           bs.Button("Export", icon="download", accent="secondary", variant="outline")
           bs.Button(icon="plus-lg", icon_only=True, accent="success")
           bs.Button(icon="x-lg",   icon_only=True, accent="danger", variant="outline")

       bs.Label("Disabled", font="heading-sm[bold]")
       with bs.HStack(gap=8):
           bs.Button("Disabled Solid",   accent="primary", disabled=True)
           bs.Button("Disabled Outline", accent="primary", variant="outline", disabled=True)

   app.run()
