AppShell
========

A single-tier application scaffold: a stack of toolbars across the top, one
navigation sidebar on the left, and a content area that swaps as you navigate. A
full-width status band can run along the bottom. For a multi-section app with a
VS Code-style workspace **rail**, use :class:`Workbench <bootstack.Workbench>`
instead.

.. image:: /_static/examples/appshell-hero-light.png
   :class: bs-screenshot-light bs-window-screenshot
   :alt: AppShell demo — light theme

.. image:: /_static/examples/appshell-hero-dark.png
   :class: bs-screenshot-dark bs-window-screenshot
   :alt: AppShell demo — dark theme

Usage
-----

Sidebars at a glance
~~~~~~~~~~~~~~~~~~~~~~

The sidebar is filled by exactly one **provider**, declared with one of four
front doors — they are mutually exclusive (a sidebar is one of these, not a mix).
Each is shown below; the linked guide walks through building it. The same four
front doors work inside a :class:`Workbench <bootstack.Workbench>` workspace.

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: page_nav() — authored pages
      :link: /tasks/navigation/single-tier
      :link-type: doc

      .. image:: /_static/examples/navigation-single-tier-light.png
         :class: bs-screenshot-light bs-window-screenshot
         :alt: A page-nav sidebar — light theme
      .. image:: /_static/examples/navigation-single-tier-dark.png
         :class: bs-screenshot-dark bs-window-screenshot
         :alt: A page-nav sidebar — dark theme

      A flat list of authored pages (`add_page` / `add_header` / `add_divider`).

   .. grid-item-card:: list_nav() — master–detail list
      :link: /tasks/navigation/master-detail-list
      :link-type: doc

      .. image:: /_static/examples/navigation-master-detail-list-light.png
         :class: bs-screenshot-light bs-window-screenshot
         :alt: A list-nav sidebar — light theme
      .. image:: /_static/examples/navigation-master-detail-list-dark.png
         :class: bs-screenshot-dark bs-window-screenshot
         :alt: A list-nav sidebar — dark theme

      A data-bound list of records driving a detail view.

   .. grid-item-card:: tree_nav() — master–detail tree
      :link: /tasks/navigation/master-detail-tree
      :link-type: doc

      .. image:: /_static/examples/navigation-master-detail-tree-light.png
         :class: bs-screenshot-light bs-window-screenshot
         :alt: A tree-nav sidebar — light theme
      .. image:: /_static/examples/navigation-master-detail-tree-dark.png
         :class: bs-screenshot-dark bs-window-screenshot
         :alt: A tree-nav sidebar — dark theme

      A data-bound hierarchy driving a detail view.

   .. grid-item-card:: custom_nav() — build it yourself
      :link: /tasks/navigation/custom-sidebar
      :link-type: doc

      .. image:: /_static/examples/navigation-custom-sidebar-light.png
         :class: bs-screenshot-light bs-window-screenshot
         :alt: A custom sidebar — light theme
      .. image:: /_static/examples/navigation-custom-sidebar-dark.png
         :class: bs-screenshot-dark bs-window-screenshot
         :alt: A custom sidebar — dark theme

      A bespoke sidebar you fill by hand — the escape hatch.

Page nav
~~~~~~~~

`page_nav()` declares an authored page list and returns a handle; each
`add_page(key, text=, icon=)` registers a sidebar item and its content page
together. A page **is** a column, so set ``padding`` / ``gap`` (and ``layout`` /
``columns`` …) on ``add_page`` — no inner wrapper. `navigate()` selects the active
page (the sidebar selection follows).

.. code-block:: python

   with bs.AppShell(title="My App") as shell:
       with shell.page_nav() as nav:
           with nav.add_page("dashboard", text="Dashboard", icon="house", padding=24, gap=12):
               bs.Label("Dashboard content")
           with nav.add_page("settings", text="Settings", icon="gear", padding=24, gap=12):
               bs.Label("Settings content")
       shell.navigate("dashboard")
   shell.run()

Headers, dividers, and footer items
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Chunk the list with `add_header()` (a quiet section label) and `add_divider()`.
Pin an item to the bottom of the sidebar with ``pin_to_footer=True`` — handy for a
Settings or Account entry.

.. code-block:: python

   with shell.page_nav() as nav:
       with nav.add_page("dashboard", text="Dashboard", icon="house"):
           ...
       with nav.add_page("inbox", text="Inbox", icon="inbox"):
           ...

       nav.add_divider()
       nav.add_header("Documents")
       with nav.add_page("files", text="Files", icon="folder"):
           ...

       with nav.add_page("settings", text="Settings", icon="gear", pin_to_footer=True):
           ...

For a collapsible sub-list, compose an :class:`Accordion
<bootstack.widgets.accordion.Accordion>` inside a custom sidebar (see *Custom
sidebar* below) — the page nav itself stays flat by design.

Higher-emphasis selection
~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default the selected item gets a subtle accent **wash** (``variant="ghost"``).
Pass ``variant="solid"`` to `page_nav()` for a filled-accent item with on-accent
(white) text — the higher-emphasis look. (It needs ``nav_accent``; with
``nav_accent=None`` it falls back to a neutral wash.)

.. code-block:: python

   with shell.page_nav(variant="solid") as nav:
       ...

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - ``"ghost"`` (default)
     - ``"solid"``
   * - .. image:: /_static/examples/appshell-selection-ghost-light.png
          :class: bs-screenshot-light bs-window-screenshot
          :alt: Ghost selection wash — light theme

       .. image:: /_static/examples/appshell-selection-ghost-dark.png
          :class: bs-screenshot-dark bs-window-screenshot
          :alt: Ghost selection wash — dark theme
     - .. image:: /_static/examples/appshell-selection-solid-light.png
          :class: bs-screenshot-light bs-window-screenshot
          :alt: Solid selection fill — light theme

       .. image:: /_static/examples/appshell-selection-solid-dark.png
          :class: bs-screenshot-dark bs-window-screenshot
          :alt: Solid selection fill — dark theme

Scrollable pages
~~~~~~~~~~~~~~~~~

Pass ``scrollable=True`` to wrap a page's content in a vertical scroll area.

.. code-block:: python

   with nav.add_page("log", text="Log", icon="list", scrollable=True, padding=16):
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
           with bs.Column(grow=True, horizontal="stretch", gap=12, padding=24):
               bs.Label(record["title"], font="heading-lg")
               bs.Label(record["text"])
   shell.run()

Custom sidebar
~~~~~~~~~~~~~~

`custom_nav()` claims the sidebar as a blank container you fill yourself — the
escape hatch when none of the providers fit. Drive the content region with
``shell.content``.

.. code-block:: python

   with shell.custom_nav():
       bs.Label("Filters", font="heading-md")
       with bs.Accordion():
           ...

Toolbars
~~~~~~~~

The shell's top region is a stack of :class:`Toolbar <bootstack.Toolbar>` bands,
added with ``shell.add_toolbar()`` — the same chrome as on
:class:`App <bootstack.widgets.app.App>`. A toolbar holds buttons, labels,
widgets, **and menus** (``toolbar.add_menu(...)``); each ``add_toolbar()`` call
stacks a new full-width band above the sidebar / content body. On macOS a
toolbar's menus bridge to the native global menu bar.

.. code-block:: python

   with bs.AppShell(title="My App") as shell:
       with shell.add_toolbar() as bar:
           with bar.add_menu("File") as file:
               file.add_action("Quit", shortcut="Mod+Q", on_click=shell.close)
           bar.add_spacer()
           bar.add_theme_toggle()
           bar.add_button(label="Save", icon="save", on_click=save)

Status bar
~~~~~~~~~~

``shell.statusbar`` is a full-width band along the bottom, intended for
**passive** status — counts, sync state, a ready message. Interactive controls
(buttons, a search box) belong on a toolbar by convention; the status bar
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
     - Narrow, icon-only sidebar (a `page_nav` sidebar only).
   * - ``'hidden'``
     - Sidebar hidden.

.. code-block:: python

   shell = bs.AppShell(sidebar_mode="compact")
   shell.sidebar_mode = "expanded"   # change it live
   shell.toggle_sidebar()

In ``'compact'`` a `page_nav` sidebar collapses to an icon-only rail (the labels
hide; footer items stay pinned):

.. image:: /_static/examples/appshell-compact-light.png
   :class: bs-screenshot-light bs-window-screenshot
   :alt: AppShell compact (icon-only) sidebar — light theme

.. image:: /_static/examples/appshell-compact-dark.png
   :class: bs-screenshot-dark bs-window-screenshot
   :alt: AppShell compact (icon-only) sidebar — dark theme

Styling
~~~~~~~

Each region's background is a :doc:`surface token </reference/theming>` you can
override; the defaults give the shell its layered look (the status band sits on
the elevated ``chrome`` surface, the sidebar a step below). The dividers and the
nav-item selection wash blend against these automatically.

.. list-table::
   :header-rows: 1
   :widths: 28 22 50

   * - Kwarg
     - Default
     - Region
   * - ``sidebar_surface``
     - ``'raised'``
     - The navigation sidebar.
   * - ``statusbar_surface``
     - ``'chrome'``
     - The bottom status band.

The selected nav item is **neutral** by default. Set ``nav_accent`` to tint the
selection with an accent (``None`` keeps it neutral); the per-sidebar
``page_nav(variant=...)`` then chooses how the accent reads — a subtle ``'ghost'``
wash (default) or a filled ``'solid'`` item.

.. code-block:: python

   bs.AppShell(nav_accent="primary")   # accent the selection; ghost wash by default

Navigation
~~~~~~~~~~

`navigate()` switches the active page; read the current page from ``current``.

.. code-block:: python

   shell.navigate("dashboard")
   shell.current               # active page key

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
   * - ``on_sidebar_toggle``
     - :class:`~bootstack.events.PaneToggleEvent`
   * - ``on_sidebar_mode_change``
     - :class:`~bootstack.events.DisplayModeEvent`

.. code-block:: python

   shell.on_page_change(lambda e: print("now on:", e.page))

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

:class:`Workbench <bootstack.Workbench>` —
the two-tier shell: a workspace rail plus per-workspace sidebars.

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