Workspaces (rail)
=================

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

`add_workspace(key, *, text, icon)` adds a rail icon and returns a workspace that
exposes the **same content API the shell has** — `add_page`, `list_nav`,
`tree_nav`, `@detail`, headers, and `panel`. So a single-tier app and a workspace
are authored identically; the rail appears automatically once there is more than
one workspace. `add_footer_workspace()` pins one (Settings, Account) to the rail
bottom.

.. code-block:: python

   with shell.add_workspace("mail", text="Mail", icon="envelope") as ws:
       ws.list_nav(inbox)
       @ws.detail
       def read(message): ...

   with shell.add_workspace("calendar", text="Calendar", icon="calendar3") as ws:
       with ws.add_page("today", text="Today", icon="calendar-day"):
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

Use workspaces when the app has several distinct areas, each warranting its own
sidebar — especially when those areas want *different* navigation shapes (a list
here, authored pages there). With a single area, skip the rail and author pages at
the shell level (a :doc:`single-tier app <single-tier>`); the two styles are
mutually exclusive.
