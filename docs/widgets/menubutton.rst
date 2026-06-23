MenuButton
==========

A button that opens a dropdown menu when clicked.

.. image:: /_static/examples/menubutton-hero-light.png
   :class: bs-screenshot-light
   :alt: MenuButton demo — light theme

.. image:: /_static/examples/menubutton-hero-dark.png
   :class: bs-screenshot-dark
   :alt: MenuButton demo — dark theme

Usage
-----

A menu button opens a dropdown of *actions* when clicked. It is for commands, not
selection — reach for a :doc:`selectbutton` or :doc:`select` when you need to pick
and remember a value.

Basic
~~~~~

Pass the button ``text`` and use ``add_item()`` to populate the menu.
Items can have an ``icon=`` and an ``on_click=`` callback.

.. code-block:: python

   mb = bs.MenuButton("Actions")
   mb.add_item("Edit",      icon="pencil",  on_click=edit)
   mb.add_item("Duplicate", icon="copy",    on_click=duplicate)
   mb.add_item("Archive",   icon="archive", on_click=archive)
   mb.add_divider()
   mb.add_item("Delete",    icon="trash",   on_click=delete)

Checkbox and radio items
~~~~~~~~~~~~~~~~~~~~~~~~~

``add_check_item()`` adds a toggle item; ``add_radio_item()`` adds a mutually
exclusive choice item. Both return the item key that can be used with
``update_item()`` later.

.. code-block:: python

   mb = bs.MenuButton("View", icon="eye")
   mb.add_check_item("Show toolbar",   value=True)
   mb.add_check_item("Show sidebar",   value=True)
   mb.add_check_item("Show status bar")

   mb2 = bs.MenuButton("Zoom")
   mb2.add_radio_item("100%", value=100)
   mb2.add_radio_item("150%", value=150, selected=True)
   mb2.add_radio_item("200%", value=200)

.. image:: /_static/examples/menubutton-check-radio-light.png
   :class: bs-screenshot-light
   :alt: MenuButton check and radio items — light theme

.. image:: /_static/examples/menubutton-check-radio-dark.png
   :class: bs-screenshot-dark
   :alt: MenuButton check and radio items — dark theme

Global item callback
~~~~~~~~~~~~~~~~~~~~

Pass ``on_select=`` to register a single callback for every item click.
The callback receives a :class:`~bootstack.events.MenuSelectEvent` with
``type``, ``text``, and ``value`` attributes.

.. code-block:: python

   def on_action(event):
       print("selected:", event.text, "→", event.value)

   mb = bs.MenuButton("Actions", on_select=on_action)
   mb.add_item("Delete", value="delete")
   mb.add_item("Archive", value="archive")

Keyboard shortcuts
~~~~~~~~~~~~~~~~~~

Pass ``shortcut=`` to display a key hint on the right side of an item.
This is a display label only — it does not bind a keyboard handler.
Three forms are accepted:

- **Modifier pattern** — ``"Mod+S"``, ``"Mod+Shift+N"``, ``"F5"`` — translated
  to the platform-correct string automatically (``"Ctrl+S"`` on Windows,
  ``"⌘S"`` on macOS). No registration required.
- **Registered key** — a name previously passed to ``get_shortcuts().register()``
  (e.g. ``"save"``). Resolved via the Shortcuts service.
- **Literal string** — anything else is shown as-is (e.g. ``"Ctrl+S"``).

Keyboard bindings must be set up separately via the Shortcuts service.
Shortcuts are most useful when ``MenuButton`` is used in a menubar context:

.. code-block:: python

   mb = bs.MenuButton("File", icon="folder2")
   mb.add_item("New",  icon="file-earmark-plus",  shortcut="Mod+N", on_click=new_file)
   mb.add_item("Open", icon="folder2-open",       shortcut="Mod+O", on_click=open_file)
   mb.add_item("Save", icon="floppy",             shortcut="Mod+S", on_click=save_file)
   mb.add_divider()
   mb.add_item("Exit", icon="box-arrow-right", on_click=app.quit)

.. image:: /_static/examples/menubutton-shortcuts-light.png
   :class: bs-screenshot-light
   :alt: MenuButton keyboard shortcuts — light theme

.. image:: /_static/examples/menubutton-shortcuts-dark.png
   :class: bs-screenshot-dark
   :alt: MenuButton keyboard shortcuts — dark theme

Icon button
~~~~~~~~~~~

Omit the ``text`` to get an icon-only button — ``icon_only`` is inferred
automatically when ``icon=`` is set and no text is provided. Set
``show_arrow=False`` to hide the chevron.

.. code-block:: python

   bs.MenuButton(icon="three-dots",          show_arrow=False)
   bs.MenuButton(icon="three-dots-vertical", show_arrow=False)
   bs.MenuButton(icon="grid",                show_arrow=False)
   bs.MenuButton(icon="gear",                show_arrow=False)

.. image:: /_static/examples/menubutton-icon-only-light.png
   :class: bs-screenshot-light
   :alt: MenuButton icon-only — light theme

.. image:: /_static/examples/menubutton-icon-only-dark.png
   :class: bs-screenshot-dark
   :alt: MenuButton icon-only — dark theme

Accent colors
~~~~~~~~~~~~~

Use ``accent=`` to apply a color intent to the button face.

.. code-block:: python

   bs.MenuButton("Primary",   accent="primary")
   bs.MenuButton("Secondary", accent="secondary")
   bs.MenuButton("Success",   accent="success")
   bs.MenuButton("Warning",   accent="warning")
   bs.MenuButton("Danger",    accent="danger")

.. image:: /_static/examples/menubutton-accents-light.png
   :class: bs-screenshot-light
   :alt: MenuButton accents — light theme

.. image:: /_static/examples/menubutton-accents-dark.png
   :class: bs-screenshot-dark
   :alt: MenuButton accents — dark theme

Style variants
~~~~~~~~~~~~~~

``variant=`` controls the visual weight of the button. ``'ghost'`` (default) blends
into the background; ``'outline'`` adds a border; ``'solid'`` fills the button with
the accent color.

.. code-block:: python

   bs.MenuButton("Solid",   accent="primary", variant="solid")
   bs.MenuButton("Outline", accent="primary", variant="outline")
   bs.MenuButton("Ghost",   accent="primary", variant="ghost")

.. image:: /_static/examples/menubutton-variants-light.png
   :class: bs-screenshot-light
   :alt: MenuButton variants — light theme

.. image:: /_static/examples/menubutton-variants-dark.png
   :class: bs-screenshot-dark
   :alt: MenuButton variants — dark theme

Disabled state
~~~~~~~~~~~~~~

Set ``disabled=True`` to prevent the button from being clicked. The menu
will not open while the button is disabled. The ``disabled`` property can
also be toggled after construction.

.. code-block:: python

   mb_a = bs.MenuButton("Enabled")
   mb_b = bs.MenuButton("Disabled", disabled=True)
   mb_c = bs.MenuButton("Disabled", accent="primary", variant="outline", disabled=True)

   mb_b.disabled = False   # re-enable later

.. image:: /_static/examples/menubutton-states-light.png
   :class: bs-screenshot-light
   :alt: MenuButton states — light theme

.. image:: /_static/examples/menubutton-states-dark.png
   :class: bs-screenshot-dark
   :alt: MenuButton states — dark theme

Reactive text
~~~~~~~~~~~~~

The button label is a live property. Read or set ``mb.text`` after
construction to relabel the button — useful when the action it triggers
changes (for example, an "Actions" button that becomes "Apply").

.. code-block:: python

   mb = bs.MenuButton("Actions")
   mb.text = "Apply"

Bind a ``Signal[str]`` to ``textsignal=`` to drive the label reactively. The
``.text`` setter writes through a bound signal, so the two stay in sync.

.. code-block:: python

   label = bs.Signal("Actions")
   mb = bs.MenuButton(textsignal=label)

   label.set("Apply")   # updates the button
   mb.text = "Reset"    # flows back into the signal

Dynamic item management
~~~~~~~~~~~~~~~~~~~~~~~

Items can be added, updated, or removed at any time after construction.

.. code-block:: python

   mb = bs.MenuButton("Actions")
   key = mb.add_item("Archive")

   mb.update_item(key, disabled=True)   # grey out the item
   mb.remove_item(key)                  # remove it entirely

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

:class:`Toolbar <bootstack.Toolbar>` —
horizontal strip for grouping buttons and menus.

:class:`SelectButton <bootstack.widgets.selectbutton.SelectButton>` —
button-styled value picker (non-editable dropdown list).

:class:`Button <bootstack.widgets.button.Button>` —
standalone action button.

API
---

The complete reference for :class:`MenuButton <bootstack.MenuButton>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.MenuButton

Full Example
------------

.. literalinclude:: ../../docs/examples/menubutton.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
