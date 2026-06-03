Button
======

A clickable action trigger. Accepts the button text as the first positional
argument.

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/button-hero-light.png"
        alt="Button — light theme" style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/button-hero-dark.png"
        alt="Button — dark theme" style="max-width:100%;">

Usage
-----

Accent colors
~~~~~~~~~~~~~

Use ``accent=`` to express intent. The button renders correctly across all
themes without hard-coding any color.

.. code-block:: python

   bs.Button("Default")
   bs.Button("Primary",   accent="primary")
   bs.Button("Secondary", accent="secondary")
   bs.Button("Info",      accent="info")
   bs.Button("Success",   accent="success")
   bs.Button("Warning",   accent="warning")
   bs.Button("Danger",    accent="danger")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/button-accents-light.png"
        alt="Button accent colors — light theme" style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/button-accents-dark.png"
        alt="Button accent colors — dark theme" style="max-width:100%;">

Style variants
~~~~~~~~~~~~~~

Use ``variant=`` to control visual weight. Useful for distinguishing primary
actions from secondary ones.

.. code-block:: python

   bs.Button("Solid",   accent="primary", variant="solid")
   bs.Button("Outline", accent="primary", variant="outline")
   bs.Button("Ghost",   accent="primary", variant="ghost")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/button-variants-light.png"
        alt="Button style variants — light theme" style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/button-variants-dark.png"
        alt="Button style variants — dark theme" style="max-width:100%;">

Icons
~~~~~

Pass any `Bootstrap Icons <https://icons.getbootstrap.com>`_ name to ``icon=``.
The icon appears to the left of the text by default.

.. code-block:: python

   bs.Button("Save",   icon="save")
   bs.Button("Delete", icon="trash",    accent="danger")
   bs.Button("Export", icon="download", accent="secondary", variant="outline")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/button-icons-light.png"
        alt="Button icons — light theme" style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/button-icons-dark.png"
        alt="Button icons — dark theme" style="max-width:100%;">

Icon position
~~~~~~~~~~~~~

Use ``icon_position=`` to control where the icon sits relative to the text.
Defaults to ``'left'``.

.. code-block:: python

   bs.Button("Left",   icon="arrow-left",  icon_position="left")
   bs.Button("Right",  icon="arrow-right", icon_position="right")
   bs.Button("Top",    icon="arrow-up",    icon_position="top")
   bs.Button("Bottom", icon="arrow-down",  icon_position="bottom")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/button-icon-position-light.png"
        alt="Button icon position — light theme" style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/button-icon-position-dark.png"
        alt="Button icon position — dark theme" style="max-width:100%;">

Icon-only
~~~~~~~~~

Omit the text to show only the icon — ``icon_only`` is inferred
automatically. Pass ``icon_only=True`` explicitly when you want to be
clear about intent.

.. code-block:: python

   # icon_only inferred — no text provided
   bs.Button(icon="plus-lg",  accent="success")
   bs.Button(icon="dash-lg",  accent="danger")
   bs.Button(icon="pencil",   accent="secondary", variant="outline")
   bs.Button(icon="trash",    accent="danger",    variant="outline")

   # explicit form — equivalent, states intent clearly
   bs.Button("Delete", icon="trash", icon_only=True, accent="danger")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/button-icon-only-light.png"
        alt="Button icon-only — light theme" style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/button-icon-only-dark.png"
        alt="Button icon-only — dark theme" style="max-width:100%;">

Uniform width
~~~~~~~~~~~~~

Use ``width=`` (in character units) to make a row of buttons the same width.

.. code-block:: python

   bs.Button("Save",   accent="primary", width=10)
   bs.Button("Cancel",                   width=10)
   bs.Button("Reset",  accent="danger",  width=10)

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/button-width-light.png"
        alt="Button uniform width — light theme" style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/button-width-dark.png"
        alt="Button uniform width — dark theme" style="max-width:100%;">

Compact density
~~~~~~~~~~~~~~~

Use ``density='compact'`` to reduce padding — useful in toolbars where
space is tight.

.. code-block:: python

   bs.Button("Cut",   icon="scissors",  density="compact")
   bs.Button("Copy",  icon="copy",      density="compact")
   bs.Button("Paste", icon="clipboard", density="compact")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/button-density-light.png"
        alt="Button compact density — light theme" style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/button-density-dark.png"
        alt="Button compact density — dark theme" style="max-width:100%;">

Disabled state
~~~~~~~~~~~~~~

.. code-block:: python

   bs.Button("Disabled Solid",   accent="primary",                    disabled=True)
   bs.Button("Disabled Outline", accent="primary", variant="outline", disabled=True)

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/button-disabled-light.png"
        alt="Button disabled — light theme" style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/button-disabled-dark.png"
        alt="Button disabled — dark theme" style="max-width:100%;">

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

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

API
---

.. autoclass:: bootstack.widgets.button.Button
   :members:
   :undoc-members:
   :inherited-members:
   :exclude-members: tk

Full Example
------------

.. literalinclude:: ../../docs/examples/button.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs