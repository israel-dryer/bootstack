Workbench
=========

A two-tier application scaffold: a VS Code-style icon **rail** of workspaces down
the far left, each revealing its own navigation sidebar and content area, plus an
optional toolbar stack and status band. Use it when an app has several distinct
sections — Mail, Calendar, Contacts — each with its own navigation. For a single
sidebar with no rail, use :class:`AppShell <bootstack.AppShell>` instead.

Usage
-----

Think of a Workbench as several :doc:`AppShell <appshell>` sidebars behind one
rail: you add each section as a *workspace* with its own navigation and content,
and the rail switches between them.

Workspaces
~~~~~~~~~~

Add a workspace with `add_workspace(key, text=, icon=)`. Each returns a
:class:`Workspace <bootstack.widgets.appshell.Workspace>` — a *sidebar host*
authored with the exact same front doors as a single-tier ``AppShell``:
`page_nav()` / `list_nav()` / `tree_nav()` / `custom_nav()`. The rail appears once
there is more than one workspace, and each workspace can use a *different*
provider.

.. code-block:: python

   with bs.Workbench(title="Console", size=(960, 600)) as shell:
       # An authored page nav.
       with shell.add_workspace("acquire", text="Acquire", icon="cpu") as ws:
           with ws.page_nav() as nav:
               with nav.add_page("sensors", text="Sensors", icon="thermometer-half", padding=20):
                   bs.Label("Sensors", font="heading-lg")
               nav.add_header("Hardware")
               with nav.add_page("ports", text="Ports", icon="usb-symbol", padding=20):
                   bs.Label("Ports", font="heading-lg")

       # A data-bound master–detail list.
       with shell.add_workspace("devices", text="Devices", icon="hdd-stack") as ws:
           ws.list_nav(devices)

           @ws.detail
           def show(record):
               bs.Label(record["title"], font="heading-lg")

       shell.navigate("acquire", "sensors")   # workspace first, then page
   shell.run()

Footer workspaces
~~~~~~~~~~~~~~~~~~

Pin a workspace (Settings, Account) to the bottom of the rail with
``pin_to_footer=True`` — the conventional spot, separated from the top cluster.

.. code-block:: python

   with shell.add_workspace("settings", text="Settings", icon="gear", pin_to_footer=True) as ws:
       with ws.page_nav() as nav:
           with nav.add_page("general", text="General", icon="sliders", padding=20):
               bs.Label("Settings", font="heading-lg")

Navigation
~~~~~~~~~~

`navigate(workspace, page)` switches the active workspace and selects a page in
it. Read the current selection from ``current`` / ``current_workspace``, and use
``shell.rail`` to switch workspaces programmatically or observe changes.

.. code-block:: python

   shell.navigate("devices", "sensor1")   # workspace, then page
   shell.current                          # active page key
   shell.current_workspace                # active workspace key
   shell.rail.select("acquire")           # switch workspace

Rail labels
~~~~~~~~~~~

By default the rail shows icons only. Pass ``rail_labels=True`` to caption each
icon (this widens the rail); ``rail_width`` sets the width explicitly.

.. code-block:: python

   bs.Workbench(rail_labels=True)

Sidebar visibility
~~~~~~~~~~~~~~~~~~~

The per-workspace sidebar is either **shown** or **hidden** — ``Ctrl/Cmd-B``
toggles it (when ``collapsible=True``), and ``toggle_sidebar()`` /
``show_sidebar()`` / ``hide_sidebar()`` control it directly; hidden leaves just the
rail + content. There is no icon-only *compact* mode here: the rail already serves
as the icon tier, so an icon-compacted sidebar would duplicate it. (Compact is a
single-tier :class:`AppShell <bootstack.AppShell>` feature.)

Toolbars, status bar, and configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A ``Workbench`` shares the rest of its surface with :class:`AppShell
<bootstack.AppShell>` — ``add_toolbar()``, ``shell.statusbar``, the flat
configuration kwargs and live ``shell.*`` properties, ``from_store()``, and the
window options all work identically. See the :doc:`AppShell guide </widgets/appshell>`
for those.

Styling
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 28 22 50

   * - Kwarg
     - Default
     - Region
   * - ``rail_surface``
     - ``'chrome'``
     - The workspace rail.
   * - ``sidebar_surface``
     - ``'raised'``
     - The per-workspace navigation sidebar.
   * - ``statusbar_surface``
     - ``'chrome'``
     - The bottom status band.

``nav_accent`` colors the rail indicator bar and the sidebar selection wash
(``None`` keeps it neutral). Under-rail sidebars always use the subtle wash — the
filled ``solid`` selection is reserved for the standalone ``AppShell`` page nav.

Events
~~~~~~

In addition to the shell events (``on_page_change`` / ``on_sidebar_toggle`` /
``on_sidebar_mode_change``), a ``Workbench`` fires ``on_workspace_change`` when
the rail switches workspace.

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

   shell.on_workspace_change(lambda e: print("workspace:", e.workspace))

See also
--------

:class:`AppShell <bootstack.AppShell>` —
the single-tier shell: one navigation sidebar, no rail.

:class:`PageStack <bootstack.widgets.pagestack.PageStack>` —
page navigation without a built-in sidebar.

API
---

The complete reference for :class:`Workbench <bootstack.Workbench>` lives on the
:doc:`Application </api-reference/application>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Workbench

Full Example
------------

.. literalinclude:: ../../docs/examples/navigation/workspaces.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs