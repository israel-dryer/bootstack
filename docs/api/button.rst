Button
======

A clickable action trigger. Accepts the button text as the first positional
argument.

.. code-block:: python

   bs.Button("Save", accent="primary", on_click=handle_save)

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/button-light.png"
        alt="Button widget demo — light theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/button-dark.png"
        alt="Button widget demo — dark theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">

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
The icon appears to the left of the text by default.

.. code-block:: python

   bs.Button("Save",   icon="save")
   bs.Button("Delete", icon="trash", accent="danger")
   bs.Button("Export", icon="download", accent="secondary", variant="outline")

Icon position
~~~~~~~~~~~~~

Use ``icon_position=`` to control where the icon sits relative to the text.
Defaults to ``'left'``.

.. code-block:: python

   bs.Button("Download", icon="download", icon_position="left")   # default
   bs.Button("Next",     icon="arrow-right", icon_position="right")
   bs.Button("Upload",   icon="upload", icon_position="top")

Icon-only
~~~~~~~~~

Set ``icon_only=True`` to show just the icon with no text. Use for
compact toolbars and action rows.

.. code-block:: python

   with bs.HStack(gap=4):
       bs.Button(icon="plus-lg",  icon_only=True, accent="success")
       bs.Button(icon="dash-lg",  icon_only=True, accent="danger")
       bs.Button(icon="pencil",   icon_only=True, accent="secondary", variant="outline")

Custom image
~~~~~~~~~~~~

Pass a ``bs.Image`` object to ``image=`` when you need something other than a
Bootstrap Icon. ``bs.Image`` handles loading, caching, and DPI scaling.

.. code-block:: python

   img = bs.Image.open("logo.png")
   bs.Button("Launch", image=img, icon_position="left")

   # From bytes (e.g. an embedded resource)
   img = bs.Image.from_bytes(raw_bytes)
   bs.Button("Custom", image=img)

Uniform width
~~~~~~~~~~~~~

Use ``width=`` (in character units) to make a row of buttons the same width.

.. code-block:: python

   with bs.HStack(gap=8):
       bs.Button("Save",   accent="primary", width=10)
       bs.Button("Cancel", width=10)
       bs.Button("Reset",  accent="danger",  width=10)

Reactive text
~~~~~~~~~~~~~

Bind a ``Signal[str]`` to ``textsignal=`` so the button text updates
automatically.

.. code-block:: python

   running  = bs.Signal(False)
   btn_text = bs.Signal("Start")

   running.subscribe(lambda v: btn_text.set("Stop" if v else "Start"))

   bs.Button(textsignal=btn_text, accent="primary",
             on_click=lambda: running.set(not running.get()))

   # Or set directly via the .text property
   btn = bs.Button("Start", accent="primary")
   btn.text = "Stop"

Compact density
~~~~~~~~~~~~~~~

Use ``density='compact'`` to reduce padding — useful in toolbars where
space is tight.

.. code-block:: python

   with bs.HStack(gap=4):
       bs.Button("Cut",   icon="scissors", density="compact")
       bs.Button("Copy",  icon="copy",     density="compact")
       bs.Button("Paste", icon="clipboard",density="compact")

Disabled state
~~~~~~~~~~~~~~

.. code-block:: python

   bs.Button("Disabled Solid",   accent="primary",  disabled=True)
   bs.Button("Disabled Outline", accent="primary",   variant="outline", disabled=True)

Handling clicks
~~~~~~~~~~~~~~~

Pass a callable to ``on_click=`` at construction, or call ``.on_click()``
afterwards. The callback receives no arguments.

.. code-block:: python

   # At construction
   bs.Button("Save",   accent="primary", on_click=handle_save)
   bs.Button("Cancel", on_click=lambda: print("Cancelled"))

   # As a subscription (cancellable)
   btn = bs.Button("Save", accent="primary")
   sub = btn.on_click(handle_save)
   sub.cancel()  # unsubscribe

   # As a Stream (composable)
   btn.on_click().debounce(300).listen(lambda: handle_save())

API
---

.. autoclass:: bootstack.widgets.button.Button
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/button.py
   :language: python
   :start-after: import bootstack as bs
