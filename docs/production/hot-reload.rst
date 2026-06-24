Hot Reload
==========

Hot reload updates a running app from your source as you edit it: save a file
and the window refreshes in place, without a restart.

.. raw:: html

   <video class="bs-video" autoplay loop muted playsinline controls
          aria-label="Editing a bootstack app and seeing it reload live on save">
     <source src="../_static/examples/live-reload.mp4" type="video/mp4">
   </video>

Run it with ``bootstack dev``:

.. code-block:: console

   $ bootstack dev app.py

Save a source file and the app updates in place: the window stays put, your
module-level state survives, and only the UI rebuilds. The file you run is
identical in development and production — only the launch differs (``python
app.py`` versus ``bootstack dev app.py``).

.. note::

   **Provisional.** The dev workflow ships in 0.1.0 but is carved out of the API
   freeze — unlike the ``bootstack`` compose surface, ``bootstack dev`` and
   ``bootstack.dev`` may change in a minor release while the workflow settles.

The mental model
----------------

Hot reload is built around a single, visible boundary in your source:

   **Code above the** ``with bs.App()`` **block is stable. The body of the block
   is what rebuilds on save.**

.. code-block:: python

   import bootstack as bs
   from bootstack.data import SqliteDataSource

   notes = SqliteDataSource().load(load_notes())  # stable — survives reloads
   query = bs.Signal("")                          # stable — value survives reloads

   with bs.App(title="Notes") as app:             # the body reloads on save
       bs.TextField(textsignal=query, placeholder="Search...")
       bs.DataTable(data_source=notes)

   app.run()

Because the ``with`` body is re-executed in place, anything declared **above** it
is built once and kept. The window itself is owned by ``App``, so it is never
torn down either — only what the body built is rebuilt inside it.

What survives a reload
----------------------

The boundary above decides what is preserved:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Preserved
     - Reset on each save
   * - Module-level signals, data sources, and stores
     - Signals or widgets created *inside* the ``with`` body
   * - The window (position, size)
     - Scroll position, focus, unbound text typed into a field
   * - The selected page / route (``AppShell`` and ``Workbench``)
     - —

The rule of thumb: **if a value must survive reloads, lift it above the** ``with``
**block.** A counter you want to keep across edits is a module-level
:doc:`Signal </reference/signals>`; a query result you want to keep is a
module-level :doc:`data source </reference/data-sources>`.

Multi-file apps
---------------

Body re-execution picks up edits in the entry file. For an app split across page
files, mark each page's builder so a save to that file rebuilds only its region:

.. code-block:: python

   # pages/dashboard.py
   import bootstack as bs
   from bootstack.dev import reloadable

   @reloadable
   def build_dashboard(db):
       bs.Label("Dashboard", font="heading-lg")
       bs.DataTable(data_source=db)

.. code-block:: python

   # main.py
   import bootstack as bs
   import pages.dashboard as dashboard      # import the MODULE, not the name

   db = build_data_source()                 # module level -> stable

   with bs.AppShell(title="My App") as shell:
       with shell.page_nav() as nav:
           with nav.add_page("dash", text="Dashboard", icon="speedometer2"):
               dashboard.build_dashboard(db)
       shell.navigate("dash")
   shell.run()

Editing ``pages/dashboard.py`` rebuilds **only** the dashboard region (the rest
of the running app is untouched); editing ``main.py`` reloads the whole body.

``@reloadable`` decorates a :doc:`builder function </tasks/composing-with-builders>`
— that is the primitive that makes per-page reload possible. Two practical notes:

- **Import the module, not the name.** ``import pages.dashboard as dashboard``
  always reaches the current code after a reload. A ``@reloadable`` builder is
  robust either way, but a ``from pages.dashboard import helper`` binding for a
  plain function is captured once and won't refresh on save — importing the
  module is the one habit that keeps *everything* in that file live.
- **Page files are pure view builders.** Reloading a page file re-runs its top
  level, so keep durable state (signals, data sources) in the entry module and
  pass it in — exactly the
  :doc:`builder-function </tasks/composing-with-builders>` discipline.

Outside ``bootstack dev``, ``@reloadable`` returns the function unchanged — it
costs nothing in production.

When an edit is broken
----------------------

A save that does not parse, or that raises while rebuilding, does **not** crash
the process. The error is shown as a banner in the window and the app keeps
running; fix the file and save again to recover.

This is the in-process behavior. Under the restart fallback described below, a
broken edit cannot show the banner — the app exits with the error in the
terminal, and the session relaunches it when you fix the file and save.

The restart fallback
--------------------

In-process reload needs a module-level ``with bs.App()`` block. An app authored
inside a function can't be re-executed safely in place, so ``bootstack dev``
**falls back to a process restart automatically** (window geometry is persisted
so it re-opens where it was) — you do not have to ask for it.

You can also force a restart for any app with ``--restart``:

.. code-block:: console

   $ bootstack dev --restart app.py

When to force it
~~~~~~~~~~~~~~~~~

Reach for ``--restart`` only when you want a full cold start on every save:

- **You are editing the stable header** — the setup *above* the ``with`` block.
  In-process reload keeps that frozen (data sources, module constants, and
  startup logic are built once and preserved), so edits there are not picked up.
  A restart re-runs the whole file.
- **You want a guaranteed clean slate** — to check first-run behavior, or because
  module-level state has drifted and you want it rebuilt from zero.
- **In-process reload misbehaves** for your app — a rare global side effect that
  does not reset cleanly in place. Restart is the robust floor.

The trade-off: a restart is slower (a full relaunch, with a brief window blink)
and preserves nothing across the save. A broken edit cannot show the in-window
banner either — the app exits with the error printed to the terminal, and the
session stays up and relaunches when you fix the file and save. For everyday UI
work the default in-process reload is faster and more forgiving; prefer it unless
you specifically need the cold start.

Gating dev-only code
--------------------

``is_dev_mode()`` reports whether the app is running under ``bootstack dev``. Use
it to gate instrumentation you only want while developing — extra logging, a debug
panel, or seeded sample data:

.. code-block:: python

   from bootstack.dev import is_dev_mode

   if is_dev_mode():
       bs.Label("DEV BUILD", accent="warning")

It returns ``False`` under a normal ``python app.py`` run, so the guarded code
costs nothing in production.

Platform support
----------------

The capture, file watching, and in-process reload are pure-Python and
cross-platform. A few platform notes:

- **macOS menu bar.** Menus bridge to the native global menu bar, and a reload
  rebuilds it correctly. macOS shows the menu of the *frontmost* app, so after a
  save in your editor you may need to click the app window to bring it forward
  before the updated menus appear — the rebuild already happened.
- **Restart fallback** works the same on Windows, macOS, and Linux — ``bootstack
  dev`` supervises the app and relaunches it on save.
- **File watching** polls modification times and file sizes a few times a second
  over your project's ``src/`` tree (or the entry file's directory when you run a
  loose script outside a project), so edits to any module are picked up — not just
  the entry file. On filesystems with coarse timestamp resolution, two saves within
  the same tick may still coalesce into one reload; the next save always catches up.
  Symlinked directories are not followed.

See also
--------

- :doc:`/tasks/composing-with-builders` — the composition pattern behind
  ``@reloadable`` and per-page reload.
- :doc:`/production/cli` — the full ``bootstack`` command-line reference.
- :doc:`/reference/signals` — module-level signals are the way to keep state
  across reloads.
