PageStack
=========

A browser-style navigation container that shows one page at a time. Add named
pages with `.add()`, place child widgets inside each page using the returned
context manager, then call `navigate()` to switch between them. Forward and back
navigation is tracked automatically.

.. raw:: html

   <video class="bs-video-light" autoplay loop muted playsinline controls
          aria-label="PageStack — navigating between pages">
     <source src="../_static/examples/pagestack-video-light.mp4" type="video/mp4">
   </video>
   <video class="bs-video-dark" autoplay loop muted playsinline controls
          aria-label="PageStack — navigating between pages">
     <source src="../_static/examples/pagestack-video-dark.mp4" type="video/mp4">
   </video>

Usage
-----

Adding pages
~~~~~~~~~~~~

Call `.add(key)` once per page. Use the returned ``StackPage`` as a context
manager — child widgets created inside the ``with`` block are placed on that
page.

.. code-block:: python

   ps = bs.PageStack(fill="both", expand=True)

   with ps.add("home"):
       bs.Label("Home page content")

   with ps.add("settings"):
       bs.Label("Settings page content")

   ps.navigate("home")

Navigating between pages
~~~~~~~~~~~~~~~~~~~~~~~~

Call `navigate()` with the target page key to switch the visible page. Only one
page is visible at a time; the previous page is hidden automatically.

.. code-block:: python

   ps.navigate("home")
   ps.navigate("settings")

Back and forward
~~~~~~~~~~~~~~~~

Every `navigate()` call pushes a history entry. Use `back()` and `forward()`
to move through history, guarded by `can_back` and `can_forward`.

.. code-block:: python

   ps.navigate("home")
   ps.navigate("settings")

   ps.can_back    # True
   ps.back()      # → "home"

   ps.can_forward # True
   ps.forward()   # → "settings"

Page layout modes
~~~~~~~~~~~~~~~~~

Each page has an independent internal layout controlled by the ``layout=``
argument of `add()`. The default is ``'vstack'`` (vertical stack).

.. code-block:: python

   # Vertical stack (default)
   with ps.add("home", layout="vstack", gap=8):
       bs.Label("Row 1")
       bs.Label("Row 2")

   # Horizontal stack
   with ps.add("toolbar", layout="hstack", gap=6):
       bs.Button("Cut")
       bs.Button("Copy")
       bs.Button("Paste")

   # Grid
   with ps.add("form", layout="grid", columns=["auto", 1], gap=8, sticky_items="ew"):
       bs.Label("Username")
       bs.TextField()
       bs.Label("Password")
       bs.PasswordField()

Passing data to pages
~~~~~~~~~~~~~~~~~~~~~

Pass an optional ``data`` dict to `navigate()`. The dict is forwarded to the
page's `on_page_mount` event payload so the receiving page can act on it.

.. code-block:: python

   ps.navigate("detail", data={"record_id": 42})

   def on_mount(event):
       record_id = event.data.get("record_id")

   ps.on_page_mount(on_mount)

Events
~~~~~~

``on_page_change`` fires after every navigation. ``on_page_mount`` fires when
a page becomes visible. Both receive a :class:`PageChangeEvent
<bootstack.events.PageChangeEvent>` with context about the transition — the
``page`` and ``prev_page`` keys, the ``nav`` direction, and any ``data`` passed
to ``navigate()``.

.. code-block:: python

   def on_change(event):
       page = event.page        # current page key
       prev = event.prev_page   # previous page key (or None)
       nav  = event.nav         # 'push', 'back', or 'forward'

   ps.on_page_change(on_change)

   # Stream form — compose with operators
   ps.on_page_change().listen(lambda e: print(e.page))

Introspection
~~~~~~~~~~~~~

.. code-block:: python

   ps.current        # key of the visible page, or None
   ps.can_back       # True if back() would succeed
   ps.can_forward    # True if forward() would succeed
   ps.page_keys()    # ('home', 'settings', 'about')

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

:class:`ScrollView <bootstack.widgets.scrollview.ScrollView>` —
scrollable container with vertical and/or horizontal scrollbars.

:class:`SplitView <bootstack.widgets.splitview.SplitView>` —
resizable split container with draggable sashes.

:class:`Accordion <bootstack.widgets.expander.Accordion>` —
collapsible section container.

:class:`VStack <bootstack.widgets.stacks.VStack>`,
:class:`HStack <bootstack.widgets.stacks.HStack>`, and
:class:`Grid <bootstack.widgets.grid.Grid>` —
non-navigating layout containers.

API
---

The complete reference for :class:`PageStack <bootstack.PageStack>` and its
:class:`StackPage <bootstack.StackPage>` handles lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.PageStack
   ~bootstack.StackPage

Full Example
------------

.. literalinclude:: ../../docs/examples/pagestack.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
