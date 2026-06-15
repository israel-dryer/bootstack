Menubar
========

A cross-platform application menu bar, built through ``app.menubar`` (also on
``window.menubar`` and ``shell.menubar``). On Windows and Linux it renders as a
themed strip at the top of the window; on macOS it relocates to the native
global menu bar at the top of the screen. You write the same code for both.

.. image:: /_static/examples/menubar-hero-light.png
   :class: bs-screenshot-light bs-window-screenshot
   :alt: Menubar with an open menu — light theme

.. image:: /_static/examples/menubar-hero-dark.png
   :class: bs-screenshot-dark bs-window-screenshot
   :alt: Menubar with an open menu — dark theme

The menu bar is **single layer** — a row of top-level menus, each holding a
flat list of items. There are no sub-menus inside menus, which keeps the API
small and the result consistent across platforms.

Usage
-----

Adding menus
~~~~~~~~~~~~

Open ``app.menubar.add_menu(...)`` as a context manager and add items to it.
Each menu becomes a top-level entry (File, Edit, …).

.. code-block:: python

   with bs.App(title="Editor") as app:
       with app.menubar.add_menu("File") as file:
           file.add_action("New",  shortcut="Mod+N", on_click=new_file)
           file.add_action("Open", shortcut="Mod+O", on_click=open_file)
           file.add_separator()
           file.add_action("Quit", shortcut="Mod+Q", on_click=app.close)

       with app.menubar.add_menu("Edit") as edit:
           edit.add_action("Undo", shortcut="Mod+Z", on_click=undo)
           edit.add_action("Redo", shortcut="Mod+Shift+Z", on_click=redo)
   app.run()

Item types
~~~~~~~~~~

A menu holds four kinds of item:

- ``add_action(text, ...)`` — a command that fires ``on_click`` when chosen.
- ``add_check(text, checked=...)`` — a toggle with an on/off state.
- ``add_radio(text, value=..., group=...)`` — one choice within a named group.
- ``add_separator()`` — a horizontal divider.

.. code-block:: python

   with app.menubar.add_menu("View") as view:
       view.add_check("Word wrap", checked=True, on_click=toggle_wrap)
       view.add_separator()
       view.add_radio("Light", value="light", group="theme",
                      on_click=lambda: bs.set_theme("bootstrap-light"))
       view.add_radio("Dark",  value="dark",  group="theme",
                      on_click=lambda: bs.set_theme("bootstrap-dark"))

Keyboard shortcuts
~~~~~~~~~~~~~~~~~~

``shortcut=`` both *displays* the accelerator beside the item and *binds* the
keypress so it actually fires:

- A **pattern** like ``"Mod+S"`` is registered and bound automatically (``Mod``
  is :kbd:`Ctrl` on Windows/Linux and :kbd:`⌘` on macOS).
- A **registered key** (one you set up yourself via the
  :doc:`Shortcuts service </reference/shortcuts>`) is shown as its accelerator
  but left bound where you registered it.

.. code-block:: python

   file.add_action("Save", shortcut="Mod+S", on_click=save)   # ⌘S / Ctrl+S, bound

Building from a dict
~~~~~~~~~~~~~~~~~~~~

``app.menubar.load([...])`` builds the whole bar declaratively — handy when the
structure is data-driven. It produces the same result as the imperative form.

.. code-block:: python

   app.menubar.load([
       {"text": "File", "items": [
           {"text": "Open", "shortcut": "Mod+O", "on_click": open_file},
           {"type": "separator"},
           {"text": "Quit", "shortcut": "Mod+Q", "on_click": app.close},
       ]},
       {"text": "Edit", "items": [
           {"text": "Undo", "shortcut": "Mod+Z", "on_click": undo},
       ]},
   ])

macOS: the native menu bar
~~~~~~~~~~~~~~~~~~~~~~~~~~~

On macOS the menus relocate to the **native global menu bar** at the top of the
screen, rendered as a real ``NSMenu`` — text-only, with ⌘-style accelerators,
exactly as macOS users expect. No code changes: the same ``app.menubar`` you build
on Windows/Linux materializes natively on Mac.

Because the menu bar takes *menus only*, it translates to the native bar
cleanly. Widgets (a theme toggle, a search box) go in the **command bar** instead —
see below.

The command bar (App and Window)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Widgets that aren't menus — a search box, a theme toggle — belong in the
**command bar** (``app.commandbar``), a :class:`Toolbar <bootstack.Toolbar>` that shares
the top row with the menu bar. On Windows/Linux you can fuse them into one row or
stack them, and recolor the whole bar, via the
``menu_layout`` / ``chrome_surface`` / ``chrome_divider`` options on
:class:`App <bootstack.App>` and :class:`Window <bootstack.Window>` — see the
:doc:`App </widgets/app>` page for the command bar, layout, and surface options.
(On :class:`AppShell <bootstack.AppShell>`, ``shell.menubar`` mounts above the
built-in command bar; the fused/stacked layout is specific to App/Window.)

See also
--------

:class:`Toolbar <bootstack.Toolbar>` —
the toolbar widget, usable standalone too.

:class:`MenuButton <bootstack.MenuButton>` —
a single button that opens an action menu.

:class:`ContextMenu <bootstack.ContextMenu>` —
right-click / popup menu.

:doc:`Keyboard shortcuts </reference/shortcuts>` —
the service behind ``shortcut=``.

Full Example
------------

.. literalinclude:: ../../docs/examples/menu.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs