ToggleButton
============

A button that stays pressed when active — toolbar-style toggle.

.. image:: /_static/examples/togglebutton-hero-light.png
   :class: bs-screenshot-light
   :alt: ToggleButton — light theme

.. image:: /_static/examples/togglebutton-hero-dark.png
   :class: bs-screenshot-dark
   :alt: ToggleButton — dark theme

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
   bs.ToggleButton("Info",      accent="info",      value=True)
   bs.ToggleButton("Success",   accent="success",   value=True)
   bs.ToggleButton("Warning",   accent="warning",   value=True)
   bs.ToggleButton("Danger",    accent="danger",    value=True)

.. image:: /_static/examples/togglebutton-accents-light.png
   :class: bs-screenshot-light
   :alt: ToggleButton accent colors — light theme

.. image:: /_static/examples/togglebutton-accents-dark.png
   :class: bs-screenshot-dark
   :alt: ToggleButton accent colors — dark theme

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

.. image:: /_static/examples/togglebutton-variants-light.png
   :class: bs-screenshot-light
   :alt: ToggleButton style variants — light theme

.. image:: /_static/examples/togglebutton-variants-dark.png
   :class: bs-screenshot-dark
   :alt: ToggleButton style variants — dark theme

State icons
~~~~~~~~~~~

Use ``on_icon=`` and ``off_icon=`` to display different icons for each state.
Either argument can be used alone — ``on_icon=`` alone swaps the icon on
activation without needing a separate inactive icon.

.. code-block:: python

kt   bs.ToggleButton("Favorite", on_icon="star-fill", off_icon="star",
                   accent="warning", value=True)
   bs.ToggleButton("Favorite", on_icon="star-fill", off_icon="star",
                   accent="warning", value=False)
   bs.ToggleButton("Pin", on_icon="pin-fill", off_icon="pin",
                   accent="primary", value=True)
   bs.ToggleButton("Pin", on_icon="pin-fill", off_icon="pin",
                   accent="primary", value=False)

.. image:: /_static/examples/togglebutton-state-icons-light.png
   :class: bs-screenshot-light
   :alt: ToggleButton state icons — light theme

.. image:: /_static/examples/togglebutton-state-icons-dark.png
   :class: bs-screenshot-dark
   :alt: ToggleButton state icons — dark theme

Icon only
~~~~~~~~~

Set ``icon_only=True`` to show just the icon with no label text. Useful for
compact toolbars.

.. code-block:: python

   bs.ToggleButton(on_icon="star-fill",  off_icon="star",  accent="warning", value=True,  icon_only=True)
   bs.ToggleButton(on_icon="star-fill",  off_icon="star",  accent="warning", value=False, icon_only=True)
   bs.ToggleButton(on_icon="pin-fill",   off_icon="pin",   accent="primary", value=True,  icon_only=True)
   bs.ToggleButton(on_icon="heart-fill", off_icon="heart", accent="danger",  value=True,  icon_only=True)
   bs.ToggleButton(on_icon="heart-fill", off_icon="heart", accent="danger",  value=False, icon_only=True)

.. image:: /_static/examples/togglebutton-icon-only-light.png
   :class: bs-screenshot-light
   :alt: ToggleButton icon only — light theme

.. image:: /_static/examples/togglebutton-icon-only-dark.png
   :class: bs-screenshot-dark
   :alt: ToggleButton icon only — dark theme

Compact density
~~~~~~~~~~~~~~~

.. code-block:: python

   bs.ToggleButton("Compact", density="compact", value=False)
   bs.ToggleButton("Compact", density="compact", value=True, accent="primary")
   bs.ToggleButton(on_icon="star-fill", off_icon="star",
                   density="compact", accent="warning", value=True, icon_only=True)

.. image:: /_static/examples/togglebutton-density-light.png
   :class: bs-screenshot-light
   :alt: ToggleButton compact density — light theme

.. image:: /_static/examples/togglebutton-density-dark.png
   :class: bs-screenshot-dark
   :alt: ToggleButton compact density — dark theme

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

   bs.ToggleButton("Disabled inactive", disabled=True, value=False)
   bs.ToggleButton("Disabled active",   disabled=True, value=True)

.. image:: /_static/examples/togglebutton-disabled-light.png
   :class: bs-screenshot-light
   :alt: ToggleButton disabled — light theme

.. image:: /_static/examples/togglebutton-disabled-dark.png
   :class: bs-screenshot-dark
   :alt: ToggleButton disabled — dark theme

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