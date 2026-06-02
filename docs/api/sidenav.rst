SideNav
=======

A sidebar navigation panel with a scrollable item list, collapsible groups,
section headers, separators, and a pinned footer. The pane can be toggled
between expanded, compact, and minimal display modes at runtime.

.. code-block:: python

   nav = bs.SideNav(title="My App", fill="y")
   nav.add_item("home", "Home", icon="house")
   nav.add_item("settings", "Settings", icon="gear")
   nav.select("home")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/sidenav-light.png"
        alt="SideNav demo — light theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/sidenav-dark.png"
        alt="SideNav demo — dark theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">

Usage
-----

Basic items
~~~~~~~~~~~

Call `add_item(key, text)` to add a navigation entry. Pass ``icon=`` for an
icon alongside the label. The key uniquely identifies the item for selection,
removal, and event payloads.

.. code-block:: python

   nav = bs.SideNav(title="My App", fill="y")
   nav.add_item("home", "Home", icon="house")
   nav.add_item("inbox", "Inbox", icon="inbox")
   nav.select("home")

Alongside content
~~~~~~~~~~~~~~~~~

SideNav is a panel widget — pair it with a content area inside an ``HStack``.

.. code-block:: python

   with bs.HStack(fill="both", expand=True):
       nav = bs.SideNav(title="My App", fill="y")
       nav.add_item("home", "Home", icon="house")
       nav.select("home")

       with bs.VStack(fill="both", expand=True, padding=20):
           bs.Label("Content area")

Groups
~~~~~~

Use `add_group()` to create a collapsible section, then pass ``group=`` to
`add_item()` to nest items inside it.

.. code-block:: python

   nav.add_group("docs", "Documents", icon="folder", is_expanded=True)
   nav.add_item("files", "Files", group="docs")
   nav.add_item("images", "Images", group="docs")

Headers and separators
~~~~~~~~~~~~~~~~~~~~~~

`add_header()` inserts a non-selectable label. `add_separator()` inserts a
thin visual divider. Both can appear anywhere in the item list.

.. code-block:: python

   nav.add_item("home", "Home", icon="house")
   nav.add_separator()
   nav.add_header("Documents")
   nav.add_item("files", "Files", icon="folder")

Footer items
~~~~~~~~~~~~

`add_footer_item()` pins an item to the bottom of the pane, below the
scrollable main area.

.. code-block:: python

   nav.add_footer_item("settings", "Settings", icon="gear")
   nav.add_footer_item("help", "Help", icon="question-circle")

Display modes
~~~~~~~~~~~~~

``display_mode=`` controls how the pane renders. Switch modes at runtime with
`set_display_mode()`.

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Mode
     - Behavior
   * - ``'expanded'``
     - Full-width pane with icons and labels (default).
   * - ``'compact'``
     - Narrow pane showing icons only; labels appear as tooltips.
   * - ``'minimal'``
     - Pane is hidden by default; toggling overlays it on top of the content.

.. code-block:: python

   nav = bs.SideNav(display_mode="compact", fill="y")
   nav.set_display_mode("expanded")

Collapsible pane
~~~~~~~~~~~~~~~~

When ``collapsible=True`` (default), a hamburger button in the header lets
users toggle the pane. Control it programmatically with `toggle_pane()`,
`open_pane()`, and `close_pane()`.

.. code-block:: python

   nav.toggle_pane()          # expanded ↔ compact, or show/hide in minimal
   nav.open_pane()
   nav.close_pane()
   nav.is_pane_open           # True / False

Selection
~~~~~~~~~

Call `select()` to set the active item. Read it back via ``current_key``.

.. code-block:: python

   nav.select("home")
   nav.selected_key           # 'home'

Events
~~~~~~

``on_selection_changed`` fires when the user clicks an item. The payload
contains the newly selected key.

.. code-block:: python

   def on_select(event):
       key = event.data["key"]   # e.g. 'home'

   nav.on_selection_changed(on_select)

   # Stream form
   nav.on_selection_changed().listen(lambda e: print(e.data["key"]))

Other events:

.. code-block:: python

   nav.on_pane_toggled(lambda e: print("open:", e.data["is_open"]))
   nav.on_display_mode_changed(lambda e: print("mode:", e.data["mode"]))
   nav.on_back_requested(lambda e: ...)   # show_back_button=True only

Reactive signal
~~~~~~~~~~~~~~~

Pass a ``Signal[str]`` to keep the selected key in sync with application state.

.. code-block:: python

   with bs.App() as app:
       current_page = bs.Signal("home")
       nav = bs.SideNav(signal=current_page, fill="y")
       nav.add_item("home", "Home")
       nav.add_item("settings", "Settings")

       current_page.subscribe(lambda key: print("navigated to", key))

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

:class:`Tabs <bootstack.widgets.tabs.Tabs>` —
tabbed container with a visible tab strip.

:class:`PageStack <bootstack.widgets.pagestack.PageStack>` —
page navigation without a visible navigation panel.

:class:`Accordion <bootstack.widgets.expander.Accordion>` —
collapsible sections in a vertical list.

API
---

.. autoclass:: bootstack.widgets.sidenav.SideNav
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/sidenav.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
