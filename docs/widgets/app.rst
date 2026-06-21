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

Beyond hosting the UI, the ``App`` is your configuration home — set the theme,
locale, size, and window-state persistence as constructor kwargs, then read or
change them live through ``app.*`` properties (``app.theme``, ``app.title``, …).

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

Toolbars
~~~~~~~~

The window's top region is a stack of :class:`Toolbar <bootstack.Toolbar>` bands
you add with ``app.add_toolbar()``. A toolbar holds buttons, labels, widgets,
**and menus** — a menu (File / Edit / …) is just another item, added with
``toolbar.add_menu(...)``. Each ``add_toolbar()`` call stacks a new full-width
band, top to bottom.

.. code-block:: python

   with bs.App(title="Editor") as app:
       with app.add_toolbar() as bar:
           with bar.add_menu("File") as file:
               file.add_action("Quit", shortcut="Mod+Q", on_click=app.close)
           bar.add_spacer()                  # push trailing items to the right
           bar.add_theme_toggle()
   app.run()

For a separate command row beneath the menus, just add a second toolbar:

.. code-block:: python

   with app.add_toolbar() as menus:
       menus.add_menu("File")
       menus.add_menu("Edit")
   with app.add_toolbar(divider=True) as commands:
       commands.add_button("Run", icon="play", accent="primary")

Each toolbar takes the usual ``Toolbar`` options — ``surface`` (default
``'chrome'``), ``density``, ``button_variant`` — so you control each band's look
independently. On macOS, a toolbar's menus bridge to the native global menu bar
(opt out per toolbar with ``use_macos_menus=False``).

Undecorated window
~~~~~~~~~~~~~~~~~~~

``undecorated=True`` removes the OS title bar and border (ignored on macOS). The
window is not left stranded: it gets a built-in title bar with minimize /
maximize / close at the right edge and window dragging (double-click maximizes),
labeled with the window title. The same applies to
:class:`Window <bootstack.Window>` and :class:`AppShell <bootstack.AppShell>`
(:class:`Window <bootstack.Window>` can opt out with ``window_controls=False``
for a chromeless splash or popover).

To take over the chrome — add a logo, menus, a theme toggle — build your own
title bar instead: make the first toolbar an
``add_toolbar(show_window_controls=True)``. Adding any chrome toolbar suppresses
the built-in one, so you keep full control of the bar's contents.

.. code-block:: python

   with bs.AppShell(title="My App", size=(720, 480), undecorated=True) as shell:
       with shell.add_toolbar(show_window_controls=True) as title:
           title.add_label("My App", icon="stack", font="caption")
           title.add_spacer()
           title.add_theme_toggle()
       with shell.add_toolbar() as bar:
           with bar.add_menu("File") as file:
               file.add_action("Quit", shortcut="Mod+Q", on_click=shell.close)
       ...
   shell.run()

.. image:: /_static/examples/undecorated-hero-light.png
   :class: bs-screenshot-light bs-window-screenshot
   :alt: Undecorated window with a custom title bar — light theme

.. image:: /_static/examples/undecorated-hero-dark.png
   :class: bs-screenshot-dark bs-window-screenshot
   :alt: Undecorated window with a custom title bar — dark theme

See also
--------

:class:`~bootstack.AppShell` — an ``App`` with sidebar navigation and a page
stack: the standard desktop-app scaffold (and the same ``add_toolbar()`` chrome).

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
