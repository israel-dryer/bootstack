App
===

The application window — the root of every bootstack program. ``App`` behaves
as an implicit vertical stack: widgets created inside its ``with`` block are
placed top-to-bottom in its content area. Build the window, then call ``run()``
to show it and start the event loop.

.. image:: /_static/examples/app-hero-light.png
   :class: bs-screenshot-light bs-window-screenshot
   :alt: A bootstack application window — light theme

.. image:: /_static/examples/app-hero-dark.png
   :class: bs-screenshot-dark bs-window-screenshot
   :alt: A bootstack application window — dark theme

Usage
-----

Building the window
~~~~~~~~~~~~~~~~~~~~

Open an ``App`` as a context manager, add content inside the block, and call
``run()`` afterwards. ``run()`` shows the window and blocks until it closes.

.. code-block:: python

   import bootstack as bs

   with bs.App(title="Notes", size=(800, 600), padding=16, gap=8) as app:
       bs.Label("Hello!", font="heading-lg")
       bs.Button("Quit", on_click=app.close)
   app.run()

``close()`` ends the program from code — the natural action for a Quit command
or menu item. It always closes (it does not run the ``on_close`` veto handlers
below).

Window controls
~~~~~~~~~~~~~~~

The window's show-state is controlled with these methods. They work the same on
``App``, :class:`~bootstack.AppShell`, and :class:`~bootstack.Window`.

.. list-table::
   :header-rows: 1
   :widths: 32 68

   * - Method
     - Effect
   * - ``close()``
     - Close the window and end ``run()``. Always closes — bypasses ``on_close``.
   * - ``hide()`` / ``show()``
     - Hide the window without destroying it, and bring it back.
   * - ``minimize()`` / ``maximize()``
     - Minimize to the taskbar/dock, or maximize where supported.
   * - ``set_fullscreen(value=True)``
     - Enter or leave fullscreen.
   * - ``set_topmost(value=True)``
     - Keep the window above all others, or release it.

.. code-block:: python

   app.set_fullscreen(True)     # kiosk / presentation mode
   app.minimize()
   app.hide()                   # later: app.show()

Closing and cleanup
~~~~~~~~~~~~~~~~~~~

Two hooks fire around the window going away, and they are distinct:

- ``on_close`` guards the window's *close button*. It runs before the window
  closes and can veto it — return ``False`` to keep the window open, or
  ``None`` / ``True`` to allow it.
- ``on_destroy`` fires once when the window (or any widget) is actually torn
  down — the place for cleanup. It cannot be canceled. See
  :doc:`/reference/events`.

.. code-block:: python

   with bs.App(title="Editor") as app:
       def confirm_quit():
           if document.modified and not bs.confirm("Discard unsaved changes?"):
               return False           # veto — the window stays open

       app.on_close(confirm_quit)
   app.run()

The handler can also be passed at construction with ``on_close=``. The
programmatic ``close()`` does not run these handlers — it always closes.

Window options
~~~~~~~~~~~~~~

Size and placement are constructor options:

.. code-block:: python

   bs.App(
       title="Notes",
       size=(800, 600),
       min_size=(480, 360),
       resizable=(True, True),
   )

Theme, locale, and configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An ``App`` is configured through flat constructor keyword arguments
(``theme``, ``locale``, …), and the same options are read and changed at runtime
through matching ``app.*`` properties — assigning ``app.theme`` or ``app.locale``
takes effect live.

.. code-block:: python

   with bs.App(title="Notes", theme="bootstrap-dark", locale="de_DE") as app:
       bs.ThemeToggle()
   app.run()

See :doc:`/production/app-settings` for the full configuration reference — every
option, the locale-derived read-only properties, persisting state across
launches with a :class:`Store <bootstack.store.Store>`, and ``App.from_store()``.

Menu bar and command bar
~~~~~~~~~~~~~~~~~~~~~~~~~

``app.menubar`` is the application :doc:`menu bar </widgets/menubar>` (File / Edit /
…). ``app.commandbar`` is the :class:`CommandBar <bootstack.CommandBar>` — for widgets
that aren't menus, such as a theme toggle or a search box. Both sit in a shared
row at the top of the window.

.. code-block:: python

   with bs.App(title="Editor") as app:
       with app.menubar.add_menu("File") as file:
           file.add_action("Quit", shortcut="Mod+Q", on_click=app.close)

       app.commandbar.add_spacer()                       # push trailing items right
       app.commandbar.add_theme_toggle()
   app.run()

Layout
^^^^^^

``menu_layout`` controls how the menu bar and command bar stack on Windows/Linux.
``"fused"`` (default) puts them in one row — menus on the left, the command bar
filling the right:

.. image:: /_static/examples/menubar-fused-light.png
   :class: bs-screenshot-light bs-window-screenshot
   :alt: Fused menu bar and command bar (one row) — light theme

.. image:: /_static/examples/menubar-fused-dark.png
   :class: bs-screenshot-dark bs-window-screenshot
   :alt: Fused menu bar and command bar (one row) — dark theme

``"stacked"`` gives the command bar its own row beneath the menus — better when it
carries many items:

.. code-block:: python

   bs.App(title="Editor", menu_layout="stacked")

.. image:: /_static/examples/menubar-stacked-light.png
   :class: bs-screenshot-light bs-window-screenshot
   :alt: Stacked menu bar and command bar (two rows) — light theme

.. image:: /_static/examples/menubar-stacked-dark.png
   :class: bs-screenshot-dark bs-window-screenshot
   :alt: Stacked menu bar and command bar (two rows) — dark theme

``menu_layout`` has no effect on macOS, where the menu bar moves to the global
bar and only the command bar stays in the window.

Surface
^^^^^^^

``chrome_surface`` recolors the whole bar — frame, menus, and command-bar buttons —
as one unit. It takes any surface or accent token:
``"background"`` blends the bar into the window body, the default ``"chrome"``
keeps it distinct, and an accent like ``"primary"`` makes a branded colored bar.
Pair it with ``chrome_divider=False`` to drop the hairline rule for a seamless
blend.

.. code-block:: python

   bs.App(title="Editor", chrome_surface="background", chrome_divider=False)

.. image:: /_static/examples/menubar-surface-light.png
   :class: bs-screenshot-light bs-window-screenshot
   :alt: Menu bar surface blended into the background — light theme

.. image:: /_static/examples/menubar-surface-dark.png
   :class: bs-screenshot-dark bs-window-screenshot
   :alt: Menu bar surface blended into the background — dark theme

See also
--------

:class:`~bootstack.AppShell` — an ``App`` with a built-in command bar, sidebar
navigation, and page stack: the standard desktop-app scaffold.

:class:`~bootstack.Window` — a secondary window opened from a running app.

API
---

The complete reference for :class:`App <bootstack.App>` lives on the
:doc:`Application </api-reference/application>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.App

Full Example
------------

.. literalinclude:: ../../docs/examples/app.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
