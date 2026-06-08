Shortcuts
=========

Register named keyboard shortcuts with platform-agnostic patterns, bind them to
your app, and let menus display the resolved shortcut text. A pattern like
``Mod+S`` becomes ``Ctrl+S`` on Windows and Linux and ``⌘S`` on macOS, so you
write the shortcut once and it reads correctly everywhere.

A shortcut has three parts: a **key** (your own identifier, e.g. ``"save"``), a
**pattern** (the key combination), and a **command** (the function to run).

The shortcut service
--------------------

``get_shortcuts()`` returns the shared service. Register your shortcuts, then
call ``bind_to(app)`` once to make them live. ``register()`` returns the created
:class:`Shortcut <bootstack.shortcuts.Shortcut>`, and raises ``ValueError`` if
the key is already taken — so each key is registered exactly once:

.. code-block:: python

   from bootstack.shortcuts import get_shortcuts

   import bootstack as bs

   with bs.App(title="Editor") as app:
       shortcuts = get_shortcuts()
       shortcuts.register("save", "Mod+S", save_file)
       shortcuts.register("find", "Mod+F", open_search)
       shortcuts.register("quit", "Mod+Q", app.quit)

       shortcuts.bind_to(app)        # activate the bindings on the app window
   app.run()

Shortcuts registered *after* ``bind_to`` are bound to that window automatically,
so you can register more as your app grows without binding again.

Patterns
--------

A pattern is modifier names joined to a key with ``+``. Use ``Mod`` for the
primary modifier and the framework picks the right one per platform:

- ``Mod`` — the primary modifier: ``Ctrl`` on Windows/Linux, ``Command`` on macOS.
- ``Shift``, ``Alt`` (``Option`` on macOS), ``Ctrl``.
- Function keys (``F1``–``F12``) and ordinary letters/digits, with or without
  modifiers.

.. code-block:: python

   shortcuts.register("new",        "Mod+N",        new_doc)
   shortcuts.register("new_window", "Mod+Shift+N",  new_window)
   shortcuts.register("refresh",    "F5",           reload_data)
   shortcuts.register("close",      "Alt+F4",       close_window)

Showing shortcuts in menus
--------------------------

``display(key)`` returns the platform-formatted label for a registered key, so
menus and tooltips can show the shortcut alongside the action:

.. code-block:: python

   shortcuts.display("save")     # "Ctrl+S"  (Windows/Linux)  ·  "⌘S" (macOS)

Menu items accept a registered key directly and format it for you — no need to
call ``display`` yourself:

.. code-block:: python

   menu.add_command(text="Save", shortcut="save", command=save_file)

Inspecting and removing shortcuts
---------------------------------

Look a shortcut up by key, enumerate everything registered, or remove one. A
:class:`Shortcut <bootstack.shortcuts.Shortcut>` exposes its ``key``,
``pattern``, ``command``, and the read-only ``display`` label:

.. code-block:: python

   sc = shortcuts.get("save")     # the Shortcut, or None if unregistered
   sc.pattern                     # "Mod+S"
   sc.display                     # "Ctrl+S" / "⌘S"

   for key, sc in shortcuts.all().items():
       print(key, "→", sc.display)

   shortcuts.unregister("find")   # remove one (KeyError if not registered)
   shortcuts.unbind_from(app)     # detach every binding from a window

See also
--------

- :doc:`/widgets/menubutton` — menus that display registered shortcuts.

API reference
-------------

.. autoclass:: bootstack.shortcuts.Shortcuts
   :members:

.. autoclass:: bootstack.shortcuts.Shortcut
   :members:
