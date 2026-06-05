AppShell
========

A full application scaffold with a toolbar across the top, a collapsible
sidebar navigation on the left, and a page stack for the content area. Add
pages with `.add_page()` — each page is also wired into the sidebar
automatically.

.. image:: /_static/examples/appshell-hero-light.png
   :class: bs-screenshot-light
   :alt: AppShell demo — light theme

.. image:: /_static/examples/appshell-hero-dark.png
   :class: bs-screenshot-dark
   :alt: AppShell demo — dark theme

Usage
-----

Adding pages
~~~~~~~~~~~~

`add_page(key, text=, icon=)` registers a sidebar nav item and a content
page together. Use the returned value as a context manager to place child
widgets on that page.

.. code-block:: python

   with bs.AppShell(title="My App") as shell:
       with shell.add_page("dashboard", text="Dashboard", icon="house"):
           bs.Label("Dashboard content")
       with shell.add_page("settings", text="Settings", icon="gear"):
           bs.Label("Settings content")
       shell.navigate("dashboard")
   shell.run()

Nav groups, headers, and separators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Organize sidebar items with collapsible groups, non-selectable section
headers, and visual separators — the same structural elements as
:class:`SideNav <bootstack.widgets.sidenav.SideNav>`.

.. code-block:: python

   shell.add_group("main", text="Main", expanded=True)
   with shell.add_page("dashboard", text="Dashboard", icon="house", group="main"):
       ...
   with shell.add_page("inbox", text="Inbox", icon="inbox", group="main"):
       ...

   shell.add_separator()
   shell.add_header("Documents")
   with shell.add_page("files", text="Files", icon="folder"):
       ...

Footer items
~~~~~~~~~~~~

Use `add_footer_page()` to pin a nav item to the bottom of the sidebar.

.. code-block:: python

   with shell.add_footer_page("settings", text="Settings", icon="gear"):
       bs.Label("Settings page")

Scrollable pages
~~~~~~~~~~~~~~~~

Pass ``scrollable=True`` to wrap a page's content in a vertical scroll area.

.. code-block:: python

   with shell.add_page("log", text="Log", icon="list", scrollable=True):
       for i in range(100):
           bs.Label(f"Log entry {i}")

Toolbar
~~~~~~~

``shell.toolbar`` exposes the built-in toolbar. Add buttons, labels,
separators, and spacers to it. Use ``command=`` (not ``on_click=``) when
calling ``add_button()`` on this object.

.. code-block:: python

   shell.toolbar.add_spacer()
   shell.toolbar.add_button(icon="sun-moon", command=bs.toggle_theme)
   shell.toolbar.add_button(label="Save", icon="save", command=save)

Sidebar display modes
~~~~~~~~~~~~~~~~~~~~~

``nav_display_mode=`` controls the initial sidebar appearance. It can also
be changed at runtime via ``shell.nav.set_display_mode()``.

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Mode
     - Behavior
   * - ``'expanded'``
     - Full-width sidebar with icons and labels (default).
   * - ``'compact'``
     - Narrow sidebar showing icons only.
   * - ``'minimal'``
     - Sidebar hidden; toggling overlays it on the content.

.. code-block:: python

   shell = bs.AppShell(nav_display_mode="compact")

.. image:: /_static/examples/appshell-compact-light.png
   :class: bs-screenshot-light
   :alt: AppShell compact sidebar — light theme

.. image:: /_static/examples/appshell-compact-dark.png
   :class: bs-screenshot-dark
   :alt: AppShell compact sidebar — dark theme

Navigation
~~~~~~~~~~

Call `navigate()` to switch the active page programmatically. The sidebar
selection updates automatically.

.. code-block:: python

   shell.navigate("dashboard")
   shell.current           # 'dashboard'

Events
~~~~~~

``on_page_change`` fires whenever the active page changes.

.. code-block:: python

   def on_change(event):
       print("now on:", shell.current)

   shell.on_page_change(on_change)

   # Stream form
   shell.on_page_change().listen(lambda e: print(shell.current))

Window options
~~~~~~~~~~~~~~

.. code-block:: python

   bs.AppShell(
       title="My App",
       size=(1024, 768),
       min_size=(640, 480),
       resizable=(True, True),
   )

   # Custom chrome (no OS title bar)
   bs.AppShell(
       undecorated=True,
       show_window_controls=True,
       draggable=True,
   )

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

:class:`SideNav <bootstack.widgets.sidenav.SideNav>` —
standalone sidebar navigation, for use without the full AppShell scaffold.

:class:`PageStack <bootstack.widgets.pagestack.PageStack>` —
page navigation without a built-in sidebar.

:class:`Tabs <bootstack.widgets.tabs.Tabs>` —
tab-strip navigation.

API
---

.. autoclass:: bootstack.widgets.appshell.AppShell
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/appshell.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
