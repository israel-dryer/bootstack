Shortcuts
=========

Register named keyboard shortcuts with platform-agnostic patterns, bind them to
your app, and let menus display the resolved shortcut text. A pattern like
``Mod+S`` becomes ``Ctrl+S`` on Windows and Linux and ``⌘S`` on macOS, so you
write the shortcut once and it reads correctly everywhere.

The shortcut service
--------------------

``bs.get_shortcuts()`` returns the shared service. Register a shortcut with a
``key`` (your own identifier), a ``pattern``, and a command, then bind the
service to the app so the keys become live:

.. code-block:: python

   import bootstack as bs

   shortcuts = bs.get_shortcuts()
   shortcuts.register("save", "Mod+S", save_file)
   shortcuts.register("find", "Mod+F", open_search)
   shortcuts.register("quit", "Mod+Q", app.quit)

   shortcuts.bind_to(app)        # activate the bindings on the app window

Patterns
--------

A pattern is modifier names joined to a key with ``+``:

- ``Mod`` — the primary modifier: ``Ctrl`` on Windows/Linux, ``Command`` on macOS.
- ``Shift``, ``Alt`` (``Option`` on macOS), ``Ctrl``.

.. code-block:: python

   shortcuts.register("new",       "Mod+N",        new_doc)
   shortcuts.register("new_window","Mod+Shift+N",  new_window)
   shortcuts.register("close",     "Alt+F4",       close_window)

Showing shortcuts in menus
--------------------------

``display(key)`` returns the platform-formatted label for a registered key, so
menus and tooltips can show the shortcut alongside the action:

.. code-block:: python

   shortcuts.display("save")     # "Ctrl+S"  (Windows/Linux)  ·  "⌘S" (macOS)

Menu items accept a registered key directly and format it for you:

.. code-block:: python

   menu.add_command(text="Save", shortcut="save", command=save_file)

Managing bindings
-----------------

.. code-block:: python

   shortcuts.get("save")          # the Shortcut object, or None
   shortcuts.all()                # {key: Shortcut} for everything registered
   shortcuts.unregister("find")   # remove one
   shortcuts.unbind_from(app)     # detach all bindings from a window

See also
--------

- :doc:`/widgets/menubutton` — menus that display registered shortcuts.

API reference
-------------

.. autoclass:: bootstack.shortcuts.Shortcuts
   :members:

.. autoclass:: bootstack.shortcuts.Shortcut
   :members:
