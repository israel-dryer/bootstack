ToggleButton
============

A button that stays pressed when active — toolbar-style toggle.

.. code-block:: python

   bs.ToggleButton("Bold")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/togglebutton-light.png"
        alt="ToggleButton demo — light theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/togglebutton-dark.png"
        alt="ToggleButton demo — dark theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">

Usage
-----

Basic
~~~~~

.. code-block:: python

   bs.ToggleButton("Inactive", value=False)
   bs.ToggleButton("Active",   value=True)

Accent colors
~~~~~~~~~~~~~

.. code-block:: python

   bs.ToggleButton("Primary",   accent="primary",   value=True)
   bs.ToggleButton("Secondary", accent="secondary", value=True)
   bs.ToggleButton("Success",   accent="success",   value=True)
   bs.ToggleButton("Warning",   accent="warning",   value=True)
   bs.ToggleButton("Danger",    accent="danger",    value=True)

Style variants
~~~~~~~~~~~~~~

Use ``variant=`` to control visual weight. Each variant is shown inactive
then active so the state change is visible.

.. code-block:: python

   bs.ToggleButton("Solid off",   accent="primary", variant="solid",   value=False)
   bs.ToggleButton("Solid on",    accent="primary", variant="solid",   value=True)
   bs.ToggleButton("Outline off", accent="primary", variant="outline", value=False)
   bs.ToggleButton("Outline on",  accent="primary", variant="outline", value=True)
   bs.ToggleButton("Ghost off",   accent="primary", variant="ghost",   value=False)
   bs.ToggleButton("Ghost on",    accent="primary", variant="ghost",   value=True)

State icons
~~~~~~~~~~~

Use ``on_icon=`` and ``off_icon=`` to display different icons for each state.
Either argument can be used alone — ``on_icon=`` alone swaps the icon on
activation without needing a separate inactive icon.

.. code-block:: python

   bs.ToggleButton("Favorite",
       on_icon="star-fill", off_icon="star",
       accent="warning")

   # on_icon alone — icon changes shape when pressed
   bs.ToggleButton("Pin", on_icon="pin-fill", off_icon="pin", accent="primary")

Icon only
~~~~~~~~~

Set ``icon_only=True`` to show just the icon with no label text. Useful for
compact toolbars.

.. code-block:: python

   bs.ToggleButton(on_icon="star-fill", off_icon="star",
                   accent="warning", icon_only=True)

Compact density
~~~~~~~~~~~~~~~

.. code-block:: python

   bs.ToggleButton("Save", density="compact")
   bs.ToggleButton(on_icon="pin-fill", off_icon="pin",
                   density="compact", icon_only=True)

Reactive binding
~~~~~~~~~~~~~~~~

Bind a ``Signal`` with ``signal=``. The button and signal stay in sync.
When ``signal=`` is provided, ``value=`` is ignored — seed the Signal
directly.

.. code-block:: python

   bold = bs.Signal(False)
   bs.ToggleButton("Bold", signal=bold, on_icon="type-bold")
   bold.subscribe(lambda v: apply_bold(v))

Disabled
~~~~~~~~

.. code-block:: python

   bs.ToggleButton("Cannot toggle", disabled=True)
   bs.ToggleButton("Locked active", value=True, disabled=True)

Events
~~~~~~

.. code-block:: python

   btn = bs.ToggleButton("Option")

   # Fires on every toggle
   btn.on_change(lambda e: print("active:", btn.checked))

   # Fires only when pressed/activated
   btn.on_check(lambda e: print("activated"))

   # Fires only when released/deactivated
   btn.on_uncheck(lambda e: print("deactivated"))

   # As a Stream
   btn.on_change().debounce(200).listen(lambda e: save())

Programmatic control
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   btn = bs.ToggleButton("Option")

   btn.checked = True     # activate
   btn.value              # → True
   btn.toggle()           # flip state

   btn.disabled = True    # lock the button

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

API
---

.. autoclass:: bootstack.widgets.boolean_controls.ToggleButton
   :members:
   :undoc-members:
   :inherited-members: PublicWidgetBase

Full Example
------------

.. literalinclude:: ../../docs/examples/togglebutton.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
