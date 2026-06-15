AppShell
========

A full application scaffold: a menu / command bar across the top, a navigation
sidebar on the left, and a content area that swaps as you navigate. With a single
set of pages it is a plain sidebar app; add more than one *workspace* and a
VS Code-style icon **rail** appears to switch between them. A full-width status
band can run along the bottom.

.. image:: /_static/examples/appshell-hero-light.png
   :class: bs-screenshot-light bs-window-screenshot
   :alt: AppShell demo — light theme

.. image:: /_static/examples/appshell-hero-dark.png
   :class: bs-screenshot-dark bs-window-screenshot
   :alt: AppShell demo — dark theme

Usage
-----

Static pages
~~~~~~~~~~~~

`add_page(key, text=, icon=)` registers a sidebar nav item and its content page
together. Use the returned value as a context manager to place child widgets on
that page. `navigate()` selects the active page (the sidebar selection follows).

.. code-block:: python

   with bs.AppShell(title="My App") as shell:
       with shell.add_page("dashboard", text="Dashboard", icon="house"):
           bs.Label("Dashboard content")
       with shell.add_page("settings", text="Settings", icon="gear"):
           bs.Label("Settings content")
       shell.navigate("dashboard")
   shell.run()

Headers, separators, and footer items
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Chunk a flat list with `add_header()` (a quiet section label) and
`add_separator()` (a divider). Pin an item to the bottom of the sidebar with
`add_footer_page()` — handy for a Settings or Account entry.

.. code-block:: python

   with shell.add_page("dashboard", text="Dashboard", icon="house"):
       ...
   with shell.add_page("inbox", text="Inbox", icon="inbox"):
       ...

   shell.add_separator()
   shell.add_header("Documents")
   with shell.add_page("files", text="Files", icon="folder"):
       ...

   with shell.add_footer_page("settings", text="Settings", icon="gear"):
       ...

For a collapsible sub-list, compose an :class:`Accordion
<bootstack.widgets.accordion.Accordion>` inside a custom panel (see *Custom
panel* below) — the static sidebar itself stays flat by design.

Scrollable pages
~~~~~~~~~~~~~~~~~

Pass ``scrollable=True`` to wrap a page's content in a vertical scroll area.

.. code-block:: python

   with shell.add_page("log", text="Log", icon="list", scrollable=True):
       for i in range(100):
           bs.Label(f"Log entry {i}")

Data-bound sidebar (master–detail)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of authored pages, fill the sidebar straight from a data source with
`list_nav()` (a flat list) or `tree_nav()` (a hierarchy). Decorate a builder with
`@shell.detail` to render the body for the selected record — it receives the
record as a dict. The first item is selected automatically.

.. code-block:: python

   from bootstack.data import MemoryDataSource

   devices = MemoryDataSource().load([
       {"id": 1, "title": "Sensor A", "text": "online"},
       {"id": 2, "title": "Sensor B", "text": "offline"},
   ])

   with bs.AppShell(title="Devices") as shell:
       shell.list_nav(devices)

       @shell.detail
       def show(record):
           with bs.VStack(fill="both", gap=12, padding=24):
               bs.Label(record["title"], font="heading-lg")
               bs.Label(record["text"])
   shell.run()

A workspace is filled by exactly one provider — static `add_page` *or*
`list_nav` *or* `tree_nav` *or* a custom `panel()`. Mixing them raises.

Workspaces (the rail)
~~~~~~~~~~~~~~~~~~~~~~

Add named *workspaces* with `add_workspace()` — each gets its own rail icon and
its own sidebar, authored with the very same page API. The rail appears
automatically once there is more than one workspace, so single-tier and two-tier
apps are written the same way. `add_footer_workspace()` pins a workspace (e.g.
Settings) to the bottom of the rail. Shell-level page methods and
`add_workspace()` are mutually exclusive — use one style or the other.

.. code-block:: python

   with bs.AppShell(title="Console", size=(960, 600)) as shell:
       with shell.add_workspace("acquire", text="Acquire", icon="cpu") as ws:
           with ws.add_page("sensors", text="Sensors", icon="thermometer-half"):
               bs.Label("Sensors", font="heading-lg")
           ws.add_header("Hardware")
           with ws.add_page("ports", text="Ports", icon="usb-symbol"):
               bs.Label("Ports", font="heading-lg")

       with shell.add_workspace("devices", text="Devices", icon="hdd-stack") as ws:
           ws.list_nav(devices)
           @ws.detail
           def show(record):
               bs.Label(record["title"], font="heading-lg")

       with shell.add_footer_workspace("settings", text="Settings", icon="gear") as ws:
           with ws.add_page("general", text="General", icon="sliders"):
               bs.Label("Settings", font="heading-lg")

       shell.navigate("acquire", "sensors")   # workspace first, then page
   shell.run()

Custom panel
~~~~~~~~~~~~

`panel()` claims the sidebar as a blank container you fill yourself — the escape
hatch when none of the providers fit. Drive the content region with
``shell.content`` (or a workspace's ``ws.content``).

.. code-block:: python

   with shell.panel():
       bs.Label("Filters", font="heading-md")
       with bs.Accordion():
           ...

Command bar
~~~~~~~~~~~

``shell.commandbar`` is the built-in :class:`Toolbar <bootstack.Toolbar>`,
in the top chrome row. Add buttons, labels, separators, and an ``add_spacer()``
to push trailing items to the right.

.. code-block:: python

   shell.commandbar.add_spacer()
   shell.commandbar.add_theme_toggle()
   shell.commandbar.add_button(label="Save", icon="save", on_click=save)

Menu bar
~~~~~~~~

``shell.menubar`` is the application :doc:`menu bar </widgets/menubar>` — the same
API as on :class:`App <bootstack.widgets.app.App>`. It shares the top chrome row
with the command bar on Windows/Linux and relocates to the native global menu bar
on macOS.

.. code-block:: python

   with bs.AppShell(title="My App") as shell:
       with shell.menubar.add_menu("File") as file:
           file.add_action("Quit", shortcut="Mod+Q", on_click=shell.close)
       ...

Status bar
~~~~~~~~~~

``shell.statusbar`` is a full-width band along the bottom, intended for
**passive** status — counts, sync state, a ready message. Interactive controls
(buttons, a search box) belong on the command bar by convention; the status bar
reads best as a quiet display strip. It renders only once a segment is added, or
when the shell is built with ``show_statusbar=True``. ``add_spacer()`` (or
``side="right"``) pushes following segments to the right cluster.

.. code-block:: python

   shell.statusbar.add_text("Ready")
   shell.statusbar.add_spacer()
   shell.statusbar.add_text("v1.0", side="right")

Pass ``textsignal=`` to make a segment **reactive** — bind it to a
:class:`Signal <bootstack.Signal>` and it updates live as the value changes:

.. code-block:: python

   selected = bs.Signal("0 selected")
   shell.statusbar.add_text(textsignal=selected)
   ...
   selected.set("3 selected")   # the status updates automatically

The :class:`~bootstack.StatusBar` handle also supports
``add_widget()`` (a custom passive widget), ``add_spacer()``, and ``clear()``;
or use it as a container — ``with shell.statusbar:`` parents widgets into the
left cluster.

Sidebar visibility
~~~~~~~~~~~~~~~~~~~

``sidebar_mode=`` sets the initial sidebar state; the property reads and writes it
live. ``Ctrl/Cmd-B`` toggles it (when ``collapsible=True``), and the explicit
``toggle_sidebar()`` / ``show_sidebar()`` / ``hide_sidebar()`` verbs control
visibility directly.

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Mode
     - Behavior
   * - ``'expanded'``
     - Full-width sidebar with icons and labels (default).
   * - ``'compact'``
     - Narrow, icon-only sidebar (a standalone static sidebar only).
   * - ``'hidden'``
     - Sidebar hidden; the rail (if present) remains as navigation.

.. code-block:: python

   shell = bs.AppShell(sidebar_mode="compact")
   shell.sidebar_mode = "expanded"   # change it live
   shell.toggle_sidebar()

Styling
~~~~~~~

Each region's background is a :doc:`surface token </reference/theming>` you can
override; the defaults give the shell its layered look (the rail and status band
sit on the elevated ``chrome`` surface, the sidebar a step below). The dividers
and the nav-item selection wash blend against these automatically.

.. list-table::
   :header-rows: 1
   :widths: 28 22 50

   * - Kwarg
     - Default
     - Region
   * - ``chrome_surface``
     - ``'chrome'``
     - The top menu / command-bar band.
   * - ``rail_surface``
     - ``'chrome'``
     - The workspace rail.
   * - ``sidebar_surface``
     - ``'raised'``
     - The navigation sidebar.
   * - ``statusbar_surface``
     - ``'chrome'``
     - The bottom status band.

The selected nav item is **neutral** by default. Set ``nav_accent`` to tint the
selection (and the rail's indicator) with an accent, and ``nav_selection`` to
choose how the accent reads:

.. code-block:: python

   # subtle accent wash + accent text (the default emphasis)
   bs.AppShell(nav_accent="primary")

   # a filled accent pill with on-accent (white) text — higher emphasis
   bs.AppShell(nav_accent="primary", nav_selection="solid")

``nav_accent`` colors the rail indicator bar, the static nav pills/rows, and the
``list_nav`` / ``tree_nav`` selection wash; ``nav_selection`` (``'ghost'`` default
or ``'solid'``) applies to the static nav items.

Navigation
~~~~~~~~~~

`navigate()` switches the active page (single-tier) or workspace + page
(two-tier). Read the current selection from ``current`` / ``current_workspace``.

.. code-block:: python

   shell.navigate("dashboard")          # page in the active workspace
   shell.navigate("devices", "sensor1") # workspace, then page
   shell.current                        # active page key
   shell.current_workspace              # active workspace key

Events
~~~~~~

All shorthands take a handler (returns a cancellable
:class:`Subscription <bootstack.events.Subscription>`) or no argument (returns a
composable :class:`Stream <bootstack.streams.Stream>`).

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - Shorthand
     - Handler receives
   * - ``on_page_change``
     - :class:`~bootstack.events.PageChangeEvent`
   * - ``on_workspace_change``
     - :class:`~bootstack.events.WorkspaceChangeEvent`
   * - ``on_sidebar_toggle``
     - :class:`~bootstack.events.PaneToggleEvent`
   * - ``on_sidebar_mode_change``
     - :class:`~bootstack.events.DisplayModeEvent`

.. code-block:: python

   shell.on_page_change(lambda e: print("now on:", e.page))
   shell.on_workspace_change().listen(lambda e: print("workspace:", e.workspace))

Theme, locale, and configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Like :class:`App <bootstack.widgets.app.App>`, an ``AppShell`` is configured
through flat constructor keyword arguments, and the same options are read and
changed at runtime through ``shell.*`` properties. Assigning ``shell.theme`` or
``shell.locale`` takes effect live.

.. code-block:: python

   shell = bs.AppShell(
       title="My App",
       theme="bootstrap-dark",
       light_theme="nord-light",
       dark_theme="nord-dark",
       locale="de_DE",
   )

   shell.theme = "bootstrap-light"     # switch the theme now

React to changes and persist them across launches with a :class:`Store
<bootstack.store.Store>` — ``from_store()`` restores configuration and tolerates
version skew, and the change events write each value back:

.. code-block:: python

   from bootstack.store import Store

   store = Store("settings")
   shell = bs.AppShell.from_store(store, title="My App")
   shell.on_theme_change(lambda theme: store.update(theme=theme))

See :doc:`/production/app-settings` for the full configuration reference —
every option, the locale-derived read-only properties, and window-state
persistence.

Window options
~~~~~~~~~~~~~~~

.. code-block:: python

   bs.AppShell(
       title="My App",
       icon="assets/app.ico",        # icon file, an Image, or an AppIcon
       size=(1024, 768),
       min_size=(640, 480),
       resizable=(True, True),
   )

   # Custom chrome (no OS title bar; draws a themed border instead)
   bs.AppShell(undecorated=True)

See also
--------

:class:`PageStack <bootstack.widgets.pagestack.PageStack>` —
page navigation without a built-in sidebar.

:class:`Tabs <bootstack.widgets.tabs.Tabs>` —
tab-strip navigation.

:class:`Toolbar <bootstack.Toolbar>` —
the standalone toolbar widget.

API
---

The complete reference for :class:`AppShell <bootstack.AppShell>` lives on the
:doc:`Application </api-reference/application>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.AppShell

Full Example
------------

.. literalinclude:: ../../docs/examples/appshell.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
