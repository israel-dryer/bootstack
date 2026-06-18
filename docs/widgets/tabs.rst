Tabs
====

A tabbed container that shows one page at a time. Add named tabs with `.add()`,
place child widgets inside each page using the returned context manager, then
switch between pages by clicking tabs or calling `select()`.

.. image:: /_static/examples/tabs-hero-light.png
   :class: bs-screenshot-light
   :alt: Tabs demo — light theme

.. image:: /_static/examples/tabs-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Tabs demo — dark theme

Usage
-----

Adding tabs
~~~~~~~~~~~

Call `.add(key, label=)` once per tab. Use the returned ``TabPage`` as a
context manager — child widgets created inside the ``with`` block are placed on
that tab's page.

.. code-block:: python

   tabs = bs.Tabs(grow=True)

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

   with tabs.add("settings", label="Settings", icon="gear"):
       bs.Label("Settings")

.. image:: /_static/examples/tabs-icons-light.png
   :class: bs-screenshot-light
   :alt: Tabs with icons — light theme

.. image:: /_static/examples/tabs-icons-dark.png
   :class: bs-screenshot-dark
   :alt: Tabs with icons — dark theme

Orientation
~~~~~~~~~~~

``orient='vertical'`` places the tab strip on the left side with pages to the
right. The default is ``'horizontal'`` (tabs above content).

.. code-block:: python

   tabs = bs.Tabs(orient="vertical", grow=True)

   with tabs.add("editor", label="Editor", icon="code-slash"):
       bs.Label("Editor panel")

   with tabs.add("preview", label="Preview", icon="eye"):
       bs.Label("Preview panel")

   with tabs.add("console", label="Console", icon="terminal"):
       bs.Label("Console panel")

.. image:: /_static/examples/tabs-vertical-light.png
   :class: bs-screenshot-light
   :alt: Tabs vertical orientation — light theme

.. image:: /_static/examples/tabs-vertical-dark.png
   :class: bs-screenshot-dark
   :alt: Tabs vertical orientation — dark theme

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

   with tabs.add("report", label="Report.pdf"):
       bs.Label("Annual report content.")

   with tabs.add("notes", label="Notes.txt"):
       bs.Label("Your notes.")

   with tabs.add("draft", label="Draft.md"):
       bs.Label("Work in progress.")

.. image:: /_static/examples/tabs-closable-light.png
   :class: bs-screenshot-light
   :alt: Tabs with close buttons — light theme

.. image:: /_static/examples/tabs-closable-dark.png
   :class: bs-screenshot-dark
   :alt: Tabs with close buttons — dark theme

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

Overflow
~~~~~~~~

When the tabs exceed the strip, ``overflow='scroll'`` (the default) keeps them in
a single scrolling line — there is no scrollbar; the mouse wheel scrolls along
the strip, and selecting a tab scrolls it into view. A trailing chevron button
appears only while tabs overflow: it lists the off-screen tabs and scrolls the
one you pick into view. This works the same in both orientations — horizontal
scrolls left and right, vertical scrolls up and down.

.. code-block:: python

   tabs = bs.Tabs(allow_add=True)          # overflow='scroll' by default
   for i in range(20):
       with tabs.add(f"file{i}", label=f"source-file-{i}.py", icon="file-earmark-code"):
           bs.Label(f"Contents of source-file-{i}.py")

Pass ``overflow='clip'`` to keep the older behavior, where tabs past the edge are
clipped. Overflow scrolling does not apply when ``tab_width='stretch'`` — stretched
tabs always fit.

Limiting the tab count
~~~~~~~~~~~~~~~~~~~~~~~

``max_tabs=`` caps how many tabs can be open. When the count reaches the limit the
add button is disabled; it re-enables when a tab is removed.

.. code-block:: python

   tabs = bs.Tabs(allow_add=True, max_tabs=8)

Page layout modes
~~~~~~~~~~~~~~~~~

Each tab page has an independent internal layout via the ``layout=`` argument
of `add()`. The default is ``'column'``.

.. code-block:: python

   # Grid layout
   with tabs.add("form", label="Form", layout="grid",
                 columns=["auto", 1], gap=8, horizontal_items="stretch"):
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

The complete reference for :class:`Tabs <bootstack.Tabs>` and its
:class:`TabPage <bootstack.TabPage>` handles lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Tabs
   ~bootstack.TabPage

Full Example
------------

.. literalinclude:: ../../docs/examples/tabs.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
