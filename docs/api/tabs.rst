Tabs
====

A tabbed container that shows one page at a time. Add named tabs with `.add()`,
place child widgets inside each page using the returned context manager, then
switch between pages by clicking tabs or calling `select()`.

.. code-block:: python

   tabs = bs.Tabs(fill="both", expand=True)

   with tabs.add("home", label="Home"):
       bs.Label("Welcome")

   with tabs.add("settings", label="Settings"):
       bs.Label("Adjust your preferences.")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/tabs-light.png"
        alt="Tabs demo — light theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/tabs-dark.png"
        alt="Tabs demo — dark theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">

Usage
-----

Adding tabs
~~~~~~~~~~~

Call `.add(key, label=)` once per tab. Use the returned ``TabPage`` as a
context manager — child widgets created inside the ``with`` block are placed on
that tab's page.

.. code-block:: python

   tabs = bs.Tabs(fill="both", expand=True)

   with tabs.add("home", label="Home"):
       bs.Label("Home page content")

   with tabs.add("settings", label="Settings"):
       bs.Label("Settings page content")

Tab icons
~~~~~~~~~

Pass ``icon=`` to show an icon alongside the tab label.

.. code-block:: python

   with tabs.add("home", label="Home", icon="house"):
       bs.Label("Home")

   with tabs.add("files", label="Files", icon="folder"):
       bs.Label("Files")

Orientation
~~~~~~~~~~~

``orient='vertical'`` places the tab strip on the left side with pages to the
right. The default is ``'horizontal'`` (tabs above content).

.. code-block:: python

   tabs = bs.Tabs(orient="vertical", fill="both", expand=True)

   with tabs.add("editor", label="Editor"):
       bs.Label("Editor panel")

   with tabs.add("preview", label="Preview"):
       bs.Label("Preview panel")

Tab width
~~~~~~~~~

``tab_width='stretch'`` distributes the full tab bar width equally among all
tabs. Pass an integer to fix every tab to that pixel width. The default sizes
each tab to its content.

.. code-block:: python

   bs.Tabs(tab_width="stretch")   # equal-width tabs filling the bar
   bs.Tabs(tab_width=120)         # fixed 120 px per tab

Closable tabs
~~~~~~~~~~~~~

``allow_close=True`` shows a close button on every tab. ``'hover'`` reveals
it only on mouse-over. Individual tabs can override this with the ``closable=``
argument of `add()`.

.. code-block:: python

   # All tabs closable
   tabs = bs.Tabs(allow_close=True)

   # Per-tab override
   with tabs.add("pinned", label="Pinned", closable=False):
       bs.Label("This tab cannot be closed.")

   with tabs.add("doc", label="Document", closable=True):
       bs.Label("Close button always visible.")

Add-tab button
~~~~~~~~~~~~~~

``allow_add=True`` shows a ``+`` button at the end of the tab strip. Clicking
it fires the ``on_tab_add`` event — your handler creates the new tab
programmatically.

.. code-block:: python

   tabs = bs.Tabs(allow_add=True)

   def add_tab(event):
       key = f"tab_{len(tabs.tab_keys())}"
       with tabs.add(key, label=f"Tab {key[-1]}"):
           bs.Label(f"Content for {key}")
       tabs.select(key)

   tabs.on_tab_add(add_tab)

Page layout modes
~~~~~~~~~~~~~~~~~

Each tab page has an independent internal layout via the ``layout=`` argument
of `add()`. The default is ``'vstack'``.

.. code-block:: python

   # Grid layout
   with tabs.add("form", label="Form", layout="grid",
                 columns=["auto", 1], gap=8, sticky_items="ew"):
       bs.Label("Username")
       bs.TextField()
       bs.Label("Password")
       bs.PasswordField()

Tab visibility
~~~~~~~~~~~~~~

Hide a tab without removing it, then restore it later.

.. code-block:: python

   tabs.hide_tab("settings")   # tab disappears from the strip
   tabs.show_tab("settings")   # tab reappears

   tabs.forget_tab("temp")     # remove tab and page permanently

Events
~~~~~~

``on_change`` fires when the selected tab changes. ``on_tab_close`` fires when
a close button is clicked. ``on_tab_add`` fires when the add-tab button is
clicked.

.. code-block:: python

   def on_change(event):
       print("switched to:", tabs.current)

   tabs.on_change(on_change)

   # Stream form — compose with operators
   tabs.on_change().listen(lambda e: print(tabs.current))

Introspection
~~~~~~~~~~~~~

.. code-block:: python

   tabs.current        # key of the active tab, or None
   tabs.tab_keys()     # ('home', 'files', 'settings')
   tabs.select("files")

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

:class:`PageStack <bootstack.widgets.pagestack.PageStack>` —
page navigation without a visible tab strip.

:class:`Accordion <bootstack.widgets.expander.Accordion>` —
collapsible sections, all visible simultaneously in a vertical list.

:class:`SplitView <bootstack.widgets.splitview.SplitView>` —
resizable split container showing multiple panes at once.

API
---

.. autoclass:: bootstack.widgets.tabs.Tabs
   :members:
   :undoc-members:

.. autoclass:: bootstack.widgets.tabs.TabPage
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/tabs.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
