Toolbar
=======

A horizontal strip of buttons, labels, **menus**, and other widgets — the
multi-purpose chrome primitive. Items are added left-to-right via
``add_button()``, ``add_label()``, ``add_menu()``, ``add_separator()``,
``add_spacer()``, and ``add_widget()``. A window's top region is a *stack* of
toolbars you build with ``add_toolbar()`` (see :ref:`toolbars-in-a-window`).

.. image:: /_static/examples/toolbar-hero-light.png
   :class: bs-screenshot-light
   :alt: Toolbar demo — light theme

.. image:: /_static/examples/toolbar-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Toolbar demo — dark theme

Usage
-----

Adding buttons
~~~~~~~~~~~~~~

Pass ``label=`` for text, ``icon=`` for an icon, or both for a text-and-icon
button. Omit ``label=`` to get an icon-only button.

.. code-block:: python

   tb = bs.Toolbar(fill="x")

   tb.add_button("Save", icon="floppy")           # text + icon
   tb.add_button(icon="gear")                      # icon-only
   tb.add_button("Cancel")                         # text-only

Use ``on_click=`` to attach a callback, and ``accent=`` to apply a color
intent to individual buttons.

.. code-block:: python

   tb.add_button("Publish", icon="cloud-upload", accent="primary", on_click=publish)
   tb.add_button("Preview", icon="eye")
   tb.add_button("Draft",   icon="pencil")
   tb.add_spacer()
   tb.add_button("Discard", icon="trash", accent="danger", on_click=discard)

.. image:: /_static/examples/toolbar-accents-light.png
   :class: bs-screenshot-light
   :alt: Toolbar accent buttons — light theme

.. image:: /_static/examples/toolbar-accents-dark.png
   :class: bs-screenshot-dark
   :alt: Toolbar accent buttons — dark theme

Separators and spacers
~~~~~~~~~~~~~~~~~~~~~~~

``add_separator()`` inserts a thin vertical rule between item groups.
``add_spacer()`` inserts a flexible gap that pushes everything added after it
to the right side.

.. code-block:: python

   tb.add_button("Bold",   icon="type-bold")
   tb.add_button("Italic", icon="type-italic")
   tb.add_separator()
   tb.add_button("Align left",   icon="text-left")
   tb.add_button("Align center", icon="text-center")
   tb.add_button("Align right",  icon="text-right")
   tb.add_spacer()
   tb.add_button(icon="gear")          # pinned to the right

.. image:: /_static/examples/toolbar-separators-light.png
   :class: bs-screenshot-light
   :alt: Toolbar separators and spacers — light theme

.. image:: /_static/examples/toolbar-separators-dark.png
   :class: bs-screenshot-dark
   :alt: Toolbar separators and spacers — dark theme

Labels
~~~~~~

``add_label()`` adds non-interactive text, optionally with an icon. Use it
for the application name or section titles.

.. code-block:: python

   tb.add_label("My App", font="heading-md")
   tb.add_separator()
   tb.add_button("New", icon="file-earmark-plus")

Adding menus
~~~~~~~~~~~~

A menu (File / Edit / …) is just another toolbar item. ``add_menu()`` returns a
context-manager builder — add ``add_action`` / ``add_check`` / ``add_radio`` /
``add_separator`` items inside the ``with`` block. A ``shortcut=`` is shown beside
the item **and** bound for you. On Windows/Linux the menu renders as an in-window
dropdown; on macOS it bridges to the native global menu bar.

.. code-block:: python

   with tb.add_menu("File") as file:
       file.add_action("New",  shortcut="Mod+N", on_click=new_doc)
       file.add_action("Open", shortcut="Mod+O", on_click=open_doc)
       file.add_separator()
       file.add_action("Quit", shortcut="Mod+Q", on_click=app.close)
   with tb.add_menu("View") as view:
       view.add_check("Status bar", checked=True, on_click=toggle_status)

Menus and command buttons can share one toolbar — that is the whole point of the
unified toolbar.

Density
~~~~~~~

The ``Toolbar`` is multi-purpose, so the right density depends on the role:

- ``"default"`` (the standalone ``bs.Toolbar`` default) — roomier buttons and
  padding. Use it for a **primary command bar** where the buttons are the focus.
- ``"compact"`` — a tight strip. Use it for **window chrome** (menu bars, title
  bars), **secondary** bars (a rich-text formatting strip), or anywhere vertical
  space is tight. Items packed on it — buttons, menu triggers, the theme toggle —
  all follow the bar's density automatically.

Window chrome added with ``add_toolbar()`` defaults to ``"compact"`` (window
bars read as tight strips); pass ``density="default"`` for a roomier one. A
standalone ``bs.Toolbar`` defaults to ``"default"``.

.. code-block:: python

   tb = bs.Toolbar(fill="x", density="compact")
   tb.add_button(icon="type-bold")
   tb.add_button(icon="type-italic")
   tb.add_button(icon="type-underline")
   tb.add_separator()
   tb.add_button(icon="text-left")
   tb.add_button(icon="text-center")
   tb.add_button(icon="text-right")
   tb.add_separator()
   tb.add_button(icon="list-ul")
   tb.add_button(icon="list-ol")
   tb.add_spacer()
   tb.add_button(icon="arrow-counterclockwise")
   tb.add_button(icon="arrow-clockwise")

.. image:: /_static/examples/toolbar-density-light.png
   :class: bs-screenshot-light
   :alt: Toolbar compact density — light theme

.. image:: /_static/examples/toolbar-density-dark.png
   :class: bs-screenshot-dark
   :alt: Toolbar compact density — dark theme

Button variant
~~~~~~~~~~~~~~

``button_variant=`` sets the default variant for all buttons added to the
toolbar. Override per-button with the ``variant=`` argument on
``add_button()``.

.. code-block:: python

   tb = bs.Toolbar(fill="x", button_variant="outline")
   tb.add_button("Save", icon="floppy")        # outline
   tb.add_button("Run", variant="solid")       # override to solid

Border and surface
~~~~~~~~~~~~~~~~~~

``show_border=True`` draws a border around the toolbar. ``surface=`` controls
the background token — ``'card'`` lifts it slightly from the page background.

.. code-block:: python

   tb = bs.Toolbar(fill="x", show_border=True, surface="card")
   tb.add_button("New",  icon="file-earmark-plus")
   tb.add_button("Open", icon="folder2-open")
   tb.add_button("Save", icon="floppy")
   tb.add_spacer()
   tb.add_button(icon="gear")

.. image:: /_static/examples/toolbar-surface-light.png
   :class: bs-screenshot-light
   :alt: Toolbar with border and card surface — light theme

.. image:: /_static/examples/toolbar-surface-dark.png
   :class: bs-screenshot-dark
   :alt: Toolbar with border and card surface — dark theme

Custom widgets
~~~~~~~~~~~~~~

Use ``add_widget()`` to embed any widget (a
:class:`Select <bootstack.widgets.select.Select>`, a
:class:`TextField <bootstack.TextField>`, …). Pass the widget **class** and let
the toolbar build it — it applies the bar's ``density`` and ``surface`` (for any
the class accepts), so the widget matches the rest of the bar:

.. code-block:: python

   tb = bs.Toolbar(fill="x", density="compact")
   tb.add_widget(bs.Select, options=["main", "dev", "feat/new-ui"], value="main")
   tb.add_widget(bs.TextField, placeholder="Search", width=24)

(An already-built *instance* — ``tb.add_widget(my_widget)`` — is added as-is and
does **not** inherit the bar's density/surface; prefer the class form for that.)

.. _toolbars-in-a-window:

Toolbars in a window
~~~~~~~~~~~~~~~~~~~~~~

A window's top chrome is a **stack of toolbars**, added with
``app.add_toolbar()`` (the same on ``Window`` and ``AppShell``). Each call stacks
a new full-width band, top to bottom; ``divider=True`` draws a hairline beneath a
band. The returned ``Toolbar`` is a *scoping* context manager — ``with
app.add_toolbar() as bar:`` reads naturally and hands back the handle, but you
fill the bar only through its ``add_*`` methods (so each item inherits the bar's
density and surface).

.. code-block:: python

   with bs.AppShell(title="My App") as shell:
       # A menu row.
       with shell.add_toolbar() as menus:
           with menus.add_menu("File") as file:
               file.add_action("Quit", shortcut="Mod+Q", on_click=shell.close)
           with menus.add_menu("View") as view:
               view.add_action("Refresh", shortcut="Mod+R", on_click=refresh)
           menus.add_spacer()
           menus.add_theme_toggle()
       # A command row beneath it, separated by a hairline.
       with shell.add_toolbar(divider=True) as commands:
           commands.add_button("Run", icon="play", accent="primary", on_click=run)

Window chrome defaults to ``surface='chrome'`` and ``density='compact'``; override
either per call.

Window controls
~~~~~~~~~~~~~~~~

``show_window_controls=True`` adds minimize / maximize / close at the right edge
and lets the toolbar drag the window (double-click maximizes). This is how you
build the title bar of an **undecorated window** — see the *Undecorated window*
section on the :doc:`App </widgets/app>` page for the full example and screenshot.

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

:class:`AppShell <bootstack.widgets.appshell.AppShell>` —
full application scaffold with a built-in toolbar, sidebar, and page stack.

:class:`Button <bootstack.widgets.button.Button>` —
standalone button widget.

API
---

The complete reference for :class:`Toolbar <bootstack.Toolbar>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Toolbar

Full Example
------------

.. literalinclude:: ../../docs/examples/toolbar.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
