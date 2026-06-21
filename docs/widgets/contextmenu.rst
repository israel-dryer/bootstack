ContextMenu
===========

A themed floating popup menu that attaches to any widget and opens on a
right-click, left-click, or a programmatic `show()` call.

.. image:: /_static/examples/contextmenu-hero-light.png
   :class: bs-screenshot-light
   :alt: ContextMenu demo — light theme

.. image:: /_static/examples/contextmenu-hero-dark.png
   :class: bs-screenshot-dark
   :alt: ContextMenu demo — dark theme

Usage
-----

A context menu is a right-click (or programmatic) popup bound to a target widget
— the on-demand counterpart to a :doc:`MenuButton <menubutton>`, which shows its
menu from a visible button. You populate both the same way, with ``add_item()``
and friends.

Basic
~~~~~

Pass a ``target=`` widget and ``trigger=`` to auto-bind the open gesture.
The default trigger is ``'right_click'``. Use ``add_item()`` to populate
the menu.

.. code-block:: python

   with bs.Card(horizontal="stretch") as card:
       bs.Label("Right-click here")

   menu = bs.ContextMenu(card)
   menu.add_item("Edit",      icon="pencil",  on_click=edit)
   menu.add_item("Duplicate", icon="copy",    on_click=duplicate)
   menu.add_divider()
   menu.add_item("Delete",    icon="trash",   on_click=delete)

Item types
~~~~~~~~~~

Four item types are available: command items, checkbutton items,
radiobutton items, and separators.

.. code-block:: python

   menu = bs.ContextMenu(target)
   menu.add_item("Command item", icon="pencil")          # command
   menu.add_divider()
   menu.add_check_item("Check item (on)", value=True)    # checkbutton
   menu.add_check_item("Check item (off)")
   menu.add_divider()
   menu.add_radio_item("Radio item A", value="a")        # radiobutton
   menu.add_radio_item("Radio item B", value="b")

.. image:: /_static/examples/contextmenu-item-types-light.png
   :class: bs-screenshot-light
   :alt: ContextMenu item types — light theme

.. image:: /_static/examples/contextmenu-item-types-dark.png
   :class: bs-screenshot-dark
   :alt: ContextMenu item types — dark theme

Global callback
~~~~~~~~~~~~~~~

Pass ``on_select=`` to register a single handler for all item activations.
The callback receives a :class:`~bootstack.events.MenuSelectEvent` with
``type``, ``text``, and ``value`` attributes.

.. code-block:: python

   def on_action(event):
       print("selected:", event.text)

   menu = bs.ContextMenu(card, on_select=on_action)
   menu.add_item("Archive")
   menu.add_item("Export")
   menu.add_item("Delete")

Manual show
~~~~~~~~~~~

Pass ``trigger=None`` to disable auto-binding. Call ``show()`` yourself,
passing the cursor position from a mouse event.

.. code-block:: python

   menu = bs.ContextMenu(trigger=None)
   menu.add_item("Cut",   icon="scissors")
   menu.add_item("Copy",  icon="copy")
   menu.add_item("Paste", icon="clipboard")

   def on_right_click(event):
       menu.show(position=(event.x_root, event.y_root))

   some_widget.tk.bind("<Button-3>", on_right_click)

Keyboard shortcuts
~~~~~~~~~~~~~~~~~~

Pass ``shortcut=`` to display a key hint on the right side of an item.
This is a display label only — it does not bind a keyboard handler.
Three forms are accepted:

- **Modifier pattern** — ``"Mod+S"``, ``"Mod+Shift+N"``, ``"F5"`` — translated
  to the platform-correct string automatically (``"Ctrl+S"`` on Windows,
  ``"⌘S"`` on macOS).
- **Registered key** — a name previously passed to ``get_shortcuts().register()``.
  Resolved to the platform display string automatically.
- **Literal string** — anything else is shown as-is (e.g. ``"Ctrl+S"``).

.. code-block:: python

   menu = bs.ContextMenu(target)
   menu.add_item("Cut",        icon="scissors",  shortcut="Mod+X")
   menu.add_item("Copy",       icon="copy",      shortcut="Mod+C")
   menu.add_item("Paste",      icon="clipboard", shortcut="Mod+V")
   menu.add_divider()
   menu.add_item("Select All",                   shortcut="Mod+A")

.. image:: /_static/examples/contextmenu-shortcuts-light.png
   :class: bs-screenshot-light
   :alt: ContextMenu keyboard shortcuts — light theme

.. image:: /_static/examples/contextmenu-shortcuts-dark.png
   :class: bs-screenshot-dark
   :alt: ContextMenu keyboard shortcuts — dark theme

See also
--------

:class:`MenuButton <bootstack.widgets.menubutton.MenuButton>` —
a button that opens a dropdown menu on click.

:class:`Toolbar <bootstack.Toolbar>` —
horizontal strip for grouping buttons and menus.

API
---

The complete reference for :class:`ContextMenu <bootstack.ContextMenu>` and its
:class:`ContextMenuItem <bootstack.ContextMenuItem>` entries lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.ContextMenu
   ~bootstack.ContextMenuItem

Full Example
------------

.. literalinclude:: ../../docs/examples/contextmenu.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
