StatusBar
=========

A horizontal band of passive status segments — counts, sync state, cursor
position, a ready message.

.. image:: /_static/examples/statusbar-hero-light.png
   :class: bs-screenshot-light bs-window-screenshot
   :alt: StatusBar at the bottom of an app window — light theme

.. image:: /_static/examples/statusbar-hero-dark.png
   :class: bs-screenshot-dark bs-window-screenshot
   :alt: StatusBar at the bottom of an app window — dark theme

Usage
-----

By convention the status bar reads as a *quiet display strip* — for interactive
controls (buttons, a search box) use a
:class:`Toolbar <bootstack.Toolbar>` instead. Nothing enforces it, but the
default ``'chrome'`` surface and compact density are tuned for passive status.
Segments add left-to-right; an ``add_spacer()`` (or ``side="right"``) splits the
band into a left and a right cluster.

Text segments
~~~~~~~~~~~~~~

``add_text()`` adds a text segment, optionally with an ``icon=`` and a ``font=``
token.

.. code-block:: python

   sb = bs.StatusBar(horizontal="stretch")
   sb.add_text("Ready", icon="check-circle")
   sb.add_text("Ln 12, Col 5", font="caption")

Left and right clusters
~~~~~~~~~~~~~~~~~~~~~~~~~

Pass ``side="right"`` to push a segment to the right cluster (the first one
inserts the flexible spacer automatically). Call ``add_spacer()`` explicitly to
split the band at a chosen point.

.. code-block:: python

   sb.add_text("Ready", icon="check-circle")   # left
   sb.add_text("Errors: 0", icon="x-circle", side="right")   # right cluster
   sb.add_text("Warnings: 2", icon="exclamation-triangle", side="right")
   sb.add_text("UTF-8", side="right")
   sb.add_text("main", icon="git", side="right")

.. image:: /_static/examples/statusbar-segments-light.png
   :class: bs-screenshot-light
   :alt: StatusBar segments split into left and right clusters — light theme

.. image:: /_static/examples/statusbar-segments-dark.png
   :class: bs-screenshot-dark
   :alt: StatusBar segments split into left and right clusters — dark theme

Reactive segments
~~~~~~~~~~~~~~~~~~~

Pass ``textsignal=`` to bind a segment to a :class:`Signal <bootstack.Signal>` —
the text follows the signal's value and updates live as it changes, ideal for a
running count or sync state.

.. code-block:: python

   issues = bs.Signal("0 issues")
   sb.add_text(textsignal=issues, icon="exclamation-triangle")

   issues.set("3 issues")   # the segment updates automatically

Embedding widgets
~~~~~~~~~~~~~~~~~~~

Pass a widget **class** to ``add_widget()`` (with ``side=`` to choose the
cluster) and the band builds it, or create any widget with ``parent=statusbar``
to add it to the left cluster. Useful for a slim progress indicator or a badge.

.. code-block:: python

   sb = bs.StatusBar(horizontal="stretch")
   sb.add_text("Syncing", icon="arrow-repeat")
   bs.ProgressBar(parent=sb, value=65)
   sb.add_text("main", icon="git", side="right")

.. image:: /_static/examples/statusbar-embedding-light.png
   :class: bs-screenshot-light
   :alt: StatusBar with an inline progress bar — light theme

.. image:: /_static/examples/statusbar-embedding-dark.png
   :class: bs-screenshot-dark
   :alt: StatusBar with an inline progress bar — dark theme

Clearing segments
~~~~~~~~~~~~~~~~~~

``clear()`` removes every segment, resetting the band to empty — useful when you
rebuild the status from scratch.

.. code-block:: python

   sb.clear()

Surface
~~~~~~~

``surface=`` sets the band's background token — the default ``'chrome'`` is a
quiet, recessed band; ``'card'`` lifts it from the page.

.. code-block:: python

   sb = bs.StatusBar(horizontal="stretch", surface="card")
   sb.add_text("Card surface", icon="layers")
   sb.add_text("3 warnings", icon="exclamation-triangle", side="right")
   sb.add_text("main", icon="git", side="right")

.. image:: /_static/examples/statusbar-surface-light.png
   :class: bs-screenshot-light
   :alt: StatusBar with card surface — light theme

.. image:: /_static/examples/statusbar-surface-dark.png
   :class: bs-screenshot-dark
   :alt: StatusBar with card surface — dark theme

Pinning to a window
~~~~~~~~~~~~~~~~~~~~~

Use ``horizontal="stretch"`` with ``side="bottom"`` to pin a status bar to the
bottom of any ``App`` or ``Window``.

.. code-block:: python

   with bs.App(title="My App", size=(800, 500)) as app:
       sb = bs.StatusBar(horizontal="stretch", side="bottom")
       sb.add_text("Ready", icon="check-circle")
       sb.add_text("main", icon="git", side="right")

       with bs.Column(grow=True, padding=16):
           bs.Label("Document", font="heading-lg")
   app.run()

Status bar inside AppShell
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:class:`AppShell <bootstack.widgets.appshell.AppShell>` includes a built-in
status band along the bottom. Access it via ``shell.statusbar`` and call the
same ``add_*`` methods — the band appears on the first segment added.

.. code-block:: python

   with bs.AppShell(title="My App") as shell:
       shell.statusbar.add_text("Ready", icon="check-circle")
       shell.statusbar.add_text("2 unread", side="right")
       ...

Widget sizing
~~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

:class:`Toolbar <bootstack.Toolbar>` —
the interactive sibling for buttons and controls in the window chrome.

:class:`AppShell <bootstack.widgets.appshell.AppShell>` —
full application scaffold with a built-in status bar, toolbars, and sidebar.

API
---

The complete reference for :class:`StatusBar <bootstack.StatusBar>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.StatusBar

Full Example
------------

.. literalinclude:: ../../docs/examples/statusbar.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
