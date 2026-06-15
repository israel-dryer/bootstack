App Structures
==============

Every bootstack program starts with one of three top-level containers. Picking
the right one is the first design decision you make — and the only one that is
hard to change later, so it is worth a minute up front.

- :class:`~bootstack.App` — a single window. Reach for it first.
- :class:`~bootstack.AppShell` — a window with a sidebar and swappable pages.
- :class:`~bootstack.Window` — a secondary window opened *from* an app.

All three share the same context-manager building model and the same window
controls; they differ only in the structure they give your content.

App — the single window
-----------------------

`App` is the starting point: one window that you fill with widgets. Create it with
a `with` block — every widget built inside the block becomes a child, with no
`parent=` wiring — then call `run()` *after* the block to start the event loop.

.. code-block:: python

   import bootstack as bs

   with bs.App(title="Notes", size=(600, 400), padding=16, gap=8) as app:
       bs.Label("Welcome to Notes", font="heading-lg")
       bs.TextField(placeholder="Jot something down…")
       bs.Button("Save", accent="primary", on_click=app.close)

   app.run()

.. image:: /_static/examples/app-structures-app-light.png
   :class: bs-screenshot-light bs-window-screenshot
   :alt: A single-window App — light theme

.. image:: /_static/examples/app-structures-app-dark.png
   :class: bs-screenshot-dark bs-window-screenshot
   :alt: A single-window App — dark theme

Use `App` for anything that fits on one screen: a form, a calculator, a
dashboard, a single-purpose tool. You can still open dialogs and secondary
windows from it — `App` is only the *primary* window, not your whole UI.

The window responds to method calls at runtime: `app.close()`, `app.minimize()`,
`app.maximize()`, `app.hide()` / `app.show()`, and `app.set_fullscreen()`.

To intercept a close, register `app.on_close(handler)` and return `False` to keep
the window open.

Settings such as `app.theme`, `app.locale`, and `app.title` are live properties —
assign to one and the window updates immediately.

AppShell — sidebar navigation
------------------------------

When your app has several distinct destinations, reach for `AppShell`. It is an
`App` with a built-in sidebar and a content area that swaps as the user
navigates. You register each destination with `add_page()` — which returns a
context manager for that page's content — and pick the starting page with
`navigate()`.

.. code-block:: python

   import bootstack as bs

   with bs.AppShell(title="Tasks") as shell:
       with shell.add_page("inbox", text="Inbox", icon="inbox"):
           bs.Label("Inbox", font="heading-lg")
           bs.Label("No new tasks", accent="secondary")

       with shell.add_page("done", text="Completed", icon="check-circle"):
           bs.Label("Completed", font="heading-lg")

       shell.navigate("inbox")

   shell.run()

.. image:: /_static/examples/app-structures-appshell-light.png
   :class: bs-screenshot-light bs-window-screenshot
   :alt: An AppShell with a sidebar — light theme

.. image:: /_static/examples/app-structures-appshell-dark.png
   :class: bs-screenshot-dark bs-window-screenshot
   :alt: An AppShell with a sidebar — dark theme

`add_footer_page()` pins an item (Settings, Account) to the bottom of the
sidebar; `add_header()` adds a section label above a group of items. For
record-driven sidebars (a list of messages, a tree of folders) and multi-area
apps with their own rails, see the :doc:`/tasks/navigation/index` patterns.

Because `AppShell` builds on `App`, it keeps the same window controls, the same
`menubar` and `commandbar`, and adds a `statusbar` along the bottom. What it adds
on top is the navigation — so choose it when you need that navigation, not for a
single-page app that `App` already handles.

Window — secondary windows
---------------------------

`Window` is a second (or third) window opened from a running app — a
preferences panel, an inspector, a tool palette, a detached editor. Build it the
same way you build an `App`, then `show()` it.

.. code-block:: python

   def rename(current: str) -> str | None:
       win = bs.Window(title="Rename", modal=True, padding=16, gap=12)
       with win:
           bs.Label("New name:")
           field = bs.TextField(value=current)

           def commit():
               win.result = field.value
               win.close()

           bs.Button("Rename", accent="primary", on_click=commit)

       return win.block_until_closed()

Pass `parent=` to tie the window to its opener (it closes with the parent and
centers over it), and `modal=True` to block interaction with the rest of the app
until it is dismissed. `win.show()` returns immediately; `win.block_until_closed()`
shows the window and waits, returning whatever you stored in `win.result`.

For a *quick* prompt — a confirmation, a string, a date — you usually do not
need a `Window` at all. The ready-made dialog verbs (`bs.confirm`,
`bs.ask_string`, …) are shorter and handle the result for you. Reach for
`Window` when the secondary surface has real content of its own. See
:doc:`/tasks/dialogs`.

Choosing between them
---------------------

.. list-table::
   :header-rows: 1
   :widths: 22 78

   * - Use
     - When
   * - :class:`~bootstack.App`
     - The whole UI fits in one window — a form, a tool, a dashboard. Start
       here; reach for the others only when you outgrow it.
   * - :class:`~bootstack.AppShell`
     - The app has several top-level destinations behind a sidebar, or a
       record-driven master/detail layout.
   * - :class:`~bootstack.Window`
     - You need a *second* window — preferences, an inspector, a detached
       editor — opened from a running app.

`AppShell` is an `App` with navigation baked in; you cannot upgrade an `App`
into one in place, so if you can see the sidebar coming, start with `AppShell`.

See also
--------

- :doc:`/getting-started/quickstart` — your first app in 60 seconds.
- :doc:`/tasks/layout` — arranging widgets inside any of these containers.
- :doc:`/tasks/navigation/index` — the full set of `AppShell` navigation patterns.
- :doc:`/widgets/app` · :doc:`/widgets/appshell` · :doc:`/widgets/window` — the
  container reference pages.
