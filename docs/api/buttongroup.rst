ButtonGroup
===========

A row (or column) of visually-connected buttons sharing a common accent and
variant. Buttons are added one at a time via ``add()``.

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/buttongroup-hero-light.png"
        alt="ButtonGroup — light theme" style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/buttongroup-hero-dark.png"
        alt="ButtonGroup — dark theme" style="max-width:100%;">

Usage
-----

Basic usage
~~~~~~~~~~~

Create a group and add buttons with ``add()``. The group handles layout and
shared styling automatically.

.. code-block:: python

   bg = bs.ButtonGroup()
   bg.add("Save")
   bg.add("Cancel")
   bg.add("Reset")

Accent colors
~~~~~~~~~~~~~

Set ``accent=`` on the group to apply a color intent to every button. Each
button inherits the group accent unless you override it individually via
``**kwargs`` in ``add()``.

.. code-block:: python

   bg = bs.ButtonGroup(accent="primary")
   bg.add("Save")
   bg.add("Cancel")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/buttongroup-accents-light.png"
        alt="ButtonGroup accent colors — light theme" style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/buttongroup-accents-dark.png"
        alt="ButtonGroup accent colors — dark theme" style="max-width:100%;">

Style variants
~~~~~~~~~~~~~~

Use ``variant=`` to control visual weight across the whole group.

.. code-block:: python

   bs.ButtonGroup(accent="primary", variant="solid")    # default
   bs.ButtonGroup(accent="primary", variant="outline")
   bs.ButtonGroup(accent="primary", variant="ghost")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/buttongroup-variants-light.png"
        alt="ButtonGroup style variants — light theme" style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/buttongroup-variants-dark.png"
        alt="ButtonGroup style variants — dark theme" style="max-width:100%;">

Icons
~~~~~

Pass ``icon=`` to ``add()`` to show a Bootstrap Icon alongside the label.

.. code-block:: python

   bg = bs.ButtonGroup(accent="primary", variant="outline")
   bg.add("Bold",      icon="type-bold")
   bg.add("Italic",    icon="type-italic")
   bg.add("Underline", icon="type-underline")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/buttongroup-icons-light.png"
        alt="ButtonGroup icons — light theme" style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/buttongroup-icons-dark.png"
        alt="ButtonGroup icons — dark theme" style="max-width:100%;">

Icon-only
~~~~~~~~~

Omit the label to show only the icon — ``icon_only`` is inferred
automatically, same as for :doc:`button`.

.. code-block:: python

   bg = bs.ButtonGroup(variant="outline", accent="primary")
   bg.add(icon="type-bold")
   bg.add(icon="type-italic")
   bg.add(icon="type-underline")
   bg.add(icon="type-strikethrough")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/buttongroup-icon-only-light.png"
        alt="ButtonGroup icon-only — light theme" style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/buttongroup-icon-only-dark.png"
        alt="ButtonGroup icon-only — dark theme" style="max-width:100%;">

Vertical orientation
~~~~~~~~~~~~~~~~~~~~

Pass ``'vertical'`` as the first argument (or ``orient='vertical'``) to stack
buttons top-to-bottom instead of left-to-right.

.. code-block:: python

   bg = bs.ButtonGroup("vertical", accent="primary", variant="outline")
   bg.add("Cut",   icon="scissors")
   bg.add("Copy",  icon="copy")
   bg.add("Paste", icon="clipboard")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/buttongroup-vertical-light.png"
        alt="ButtonGroup vertical — light theme" style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/buttongroup-vertical-dark.png"
        alt="ButtonGroup vertical — dark theme" style="max-width:100%;">

Compact density
~~~~~~~~~~~~~~~

Use ``density='compact'`` to reduce button padding — useful inside toolbars.

.. code-block:: python

   bg = bs.ButtonGroup(accent="primary", density="compact")
   bg.add("Cut",   icon="scissors")
   bg.add("Copy",  icon="copy")
   bg.add("Paste", icon="clipboard")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/buttongroup-density-light.png"
        alt="ButtonGroup compact density — light theme" style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/buttongroup-density-dark.png"
        alt="ButtonGroup compact density — dark theme" style="max-width:100%;">

Disabled state
~~~~~~~~~~~~~~

Set ``disabled=True`` to make all buttons in the group non-interactive at
once. Toggle the ``disabled`` property at runtime to re-enable.

.. code-block:: python

   bg = bs.ButtonGroup(accent="primary", disabled=True)
   bg.add("Save")
   bg.add("Cancel")

   # Toggle at runtime
   bg.disabled = False

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/buttongroup-disabled-light.png"
        alt="ButtonGroup disabled — light theme" style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/buttongroup-disabled-dark.png"
        alt="ButtonGroup disabled — dark theme" style="max-width:100%;">

Handling clicks
~~~~~~~~~~~~~~~

Use ``on_click()`` on the group to handle any button press in one place.
The handler receives an event with ``event.data`` containing ``'key'``,
``'text'``, and ``'icon'`` for the clicked button.

.. code-block:: python

   bg = bs.ButtonGroup(accent="primary")
   bg.add("Save",   icon="save",  key="save")
   bg.add("Cancel", icon="x-lg", key="cancel")
   bg.add("Delete", icon="trash", key="delete")

   def handle_click(e):
       print(e.data["key"], e.data["text"], e.data["icon"])

   bg.on_click(handle_click)

   # As a subscription (cancellable)
   sub = bg.on_click(handle_click)
   sub.cancel()

   # As a Stream (composable)
   bg.on_click().listen(handle_click)

Managing items
~~~~~~~~~~~~~~

``add()`` and ``add_all()`` return the key(s) assigned to each button.
Keys are auto-generated (``'widget_0'``, ``'widget_1'``, …) unless you
provide them explicitly. Use keys with ``remove()``, ``update_item()``,
``query_item()``, and ``item()``.

.. code-block:: python

   bg = bs.ButtonGroup(accent="primary")

   # Add one at a time
   bg.add("Save",   icon="save",  key="save")
   bg.add("Cancel", icon="x-lg", key="cancel")

   # Or all at once
   bg.add_all([
       dict(label="Cut",   icon="scissors", key="cut"),
       dict(label="Copy",  icon="copy",     key="copy"),
       dict(label="Paste", icon="clipboard"),
   ])

   # Inspect
   print(bg.keys)         # ('save', 'cancel', 'cut', 'copy', 'widget_0')
   print(len(bg))         # 5
   print("save" in bg)    # True

   # Query a button's current value
   bg.query_item("save", "text")          # 'Save'

   # Reconfigure after creation
   bg.update_item("save", text="Saving…", state="disabled")

   # Remove a button
   bg.remove("cancel")

   # Access the underlying button widget
   btn = bg.item("save")

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

* :doc:`button` — standalone button
* :doc:`togglegroup` — button group with selection state tracking

API
---

.. autoclass:: bootstack.widgets.buttongroup.ButtonGroup
   :members:
   :undoc-members:
   :inherited-members:
   :exclude-members: tk

Full Example
------------

.. literalinclude:: ../../docs/examples/buttongroup.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
