Workspaces
==========

Several distinct areas behind a VS Code-style icon **rail** — a mail + calendar +
contacts suite, an IDE, a creative tool. Each area is a *workspace* with its own
sidebar, and each can use a different navigation pattern.

.. image:: /_static/examples/navigation-workspaces-light.png
   :class: bs-screenshot-light bs-window-screenshot
   :alt: Workspace rail (mail suite) — light theme

.. image:: /_static/examples/navigation-workspaces-dark.png
   :class: bs-screenshot-dark bs-window-screenshot
   :alt: Workspace rail (mail suite) — dark theme

How it works
------------

The two-tier shell is :class:`Workbench <bootstack.Workbench>`.
`add_workspace(key, *, text, icon)` adds a rail icon and returns a workspace that
exposes the **same sidebar front doors as a single-tier app** — `page_nav`,
`list_nav`, `tree_nav`, and `custom_nav`. So a workspace is authored just like an
:class:`AppShell <bootstack.AppShell>`; the rail appears once there is more than
one workspace. `pin_to_footer=True` pins a workspace (Settings, Account) to the
rail bottom.

.. code-block:: python

   with bs.Workbench(title="Suite") as shell:
       with shell.add_workspace("mail", text="Mail", icon="envelope") as ws:
           ws.list_nav(inbox)
           @ws.detail
           def read(message): ...

       with shell.add_workspace("calendar", text="Calendar", icon="calendar3") as ws:
           with ws.page_nav() as nav:
               with nav.add_page("today", text="Today", icon="calendar-day", padding=20):
                   ...

Clicking the active rail icon hides the sidebar; clicking a different one
switches workspace and shows it (the VS Code gesture). `navigate(workspace, page)`
jumps to a page in a specific workspace. Each workspace remembers its own active
page, so switching back and forth is lossless.

Example
-------

.. literalinclude:: ../../examples/navigation/workspaces.py
   :language: python
   :linenos:

When to use
-----------

Use a `Workbench` when the app has several distinct areas, each warranting its own
sidebar — especially when those areas want *different* navigation shapes (a list
here, authored pages there). With a single area, skip the rail and use a
:doc:`single-tier app <single-tier>` (`AppShell`) instead.
