CommandBar
==========

A horizontal strip of buttons, labels, separators, and other widgets.
Items are added left-to-right via ``add_button()``, ``add_label()``,
``add_separator()``, ``add_spacer()``, and ``add_widget()``.

.. image:: /_static/examples/commandbar-hero-light.png
   :class: bs-screenshot-light
   :alt: CommandBar demo — light theme

.. image:: /_static/examples/commandbar-hero-dark.png
   :class: bs-screenshot-dark
   :alt: CommandBar demo — dark theme

Usage
-----

Adding buttons
~~~~~~~~~~~~~~

Pass ``label=`` for text, ``icon=`` for an icon, or both for a text-and-icon
button. Omit ``label=`` to get an icon-only button.

.. code-block:: python

   tb = bs.CommandBar(fill="x")

   tb.add_button("Save", icon="floppy")           # text + icon
   tb.add_button(icon="gear")                      # icon-only
   tb.add_button("Cancel")                         # text-only

Use ``on_click=`` to attach a callback, and ``accent=`` to apply a color
intent to individual buttons.

.. code-block:: python

   tb.add_button("Publish", icon="cloud-upload", accent="primary", on_click=publish)
   tb.add_button("Discard", icon="trash", accent="danger", on_click=discard)

.. image:: /_static/examples/commandbar-accents-light.png
   :class: bs-screenshot-light
   :alt: CommandBar accent buttons — light theme

.. image:: /_static/examples/commandbar-accents-dark.png
   :class: bs-screenshot-dark
   :alt: CommandBar accent buttons — dark theme

Separators and spacers
~~~~~~~~~~~~~~~~~~~~~~~

``add_separator()`` inserts a thin vertical rule between item groups.
``add_spacer()`` inserts a flexible gap that pushes everything added after it
to the right side.

.. code-block:: python

   tb.add_button("Bold", icon="type-bold")
   tb.add_button("Italic", icon="type-italic")
   tb.add_separator()
   tb.add_button("Align left", icon="text-left")
   tb.add_spacer()
   tb.add_button(icon="gear")          # pinned to the right

.. image:: /_static/examples/commandbar-separators-light.png
   :class: bs-screenshot-light
   :alt: CommandBar separators and spacers — light theme

.. image:: /_static/examples/commandbar-separators-dark.png
   :class: bs-screenshot-dark
   :alt: CommandBar separators and spacers — dark theme

Labels
~~~~~~

``add_label()`` adds non-interactive text, optionally with an icon. Use it
for the application name or section titles.

.. code-block:: python

   tb.add_label("My App", font="heading-md")
   tb.add_separator()
   tb.add_button("New", icon="file-earmark-plus")

Density
~~~~~~~

``density="compact"`` reduces padding and button size — useful for secondary
command bars such as a rich-text formatting strip.

.. code-block:: python

   tb = bs.CommandBar(fill="x", density="compact")
   tb.add_button(icon="type-bold")
   tb.add_button(icon="type-italic")
   tb.add_button(icon="type-underline")

.. image:: /_static/examples/commandbar-density-light.png
   :class: bs-screenshot-light
   :alt: CommandBar compact density — light theme

.. image:: /_static/examples/commandbar-density-dark.png
   :class: bs-screenshot-dark
   :alt: CommandBar compact density — dark theme

Button variant
~~~~~~~~~~~~~~

``button_variant=`` sets the default variant for all buttons added to the
command bar. Override per-button with the ``variant=`` argument on
``add_button()``.

.. code-block:: python

   tb = bs.CommandBar(fill="x", button_variant="outline")
   tb.add_button("Save", icon="floppy")        # outline
   tb.add_button("Run", variant="solid")       # override to solid

Border and surface
~~~~~~~~~~~~~~~~~~

``show_border=True`` draws a border around the command bar. ``surface=`` controls
the background token — ``'card'`` lifts it slightly from the page background.

.. code-block:: python

   tb = bs.CommandBar(fill="x", show_border=True, surface="card")
   tb.add_button("New",  icon="file-earmark-plus")
   tb.add_button("Open", icon="folder2-open")
   tb.add_button("Save", icon="floppy")

.. image:: /_static/examples/commandbar-surface-light.png
   :class: bs-screenshot-light
   :alt: CommandBar with border and card surface — light theme

.. image:: /_static/examples/commandbar-surface-dark.png
   :class: bs-screenshot-dark
   :alt: CommandBar with border and card surface — dark theme

Custom widgets
~~~~~~~~~~~~~~

Use ``add_widget()`` to embed any widget (e.g. a
:class:`Select <bootstack.widgets.select.Select>`) in the command bar. Create the
widget with the command bar as its parent first.

.. code-block:: python

   tb = bs.CommandBar(fill="x")
   branch = bs.Select(
       ["main", "dev", "feat/new-ui"],
       parent=tb,
   )
   tb.add_widget(branch)

Custom titlebar
~~~~~~~~~~~~~~~

Set ``show_window_controls=True`` to add minimize, maximize, and close buttons
on the right, and ``draggable=True`` to let the user drag the window by the
command bar. Pair with ``undecorated=True`` on the App to remove the OS title bar.

.. code-block:: python

   with bs.App(title="My App", undecorated=True) as app:
       tb = bs.CommandBar(
           fill="x",
           show_window_controls=True,
           draggable=True,
       )
       tb.add_label("My App", font="heading-md")
       tb.add_spacer()
       ...
   app.run()

Command bar inside AppShell
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:class:`AppShell <bootstack.widgets.appshell.AppShell>` includes a built-in
command bar. Access it via ``shell.commandbar`` and call the same ``add_*`` methods.
Use ``command=`` (not ``on_click=``) when calling ``add_button()`` on the
AppShell command bar.

.. code-block:: python

   with bs.AppShell(title="My App") as shell:
       shell.commandbar.add_spacer()
       shell.commandbar.add_button(icon="circle-half", command=bs.toggle_theme)
       ...

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

:class:`AppShell <bootstack.widgets.appshell.AppShell>` —
full application scaffold with a built-in command bar, sidebar, and page stack.

:class:`Button <bootstack.widgets.button.Button>` —
standalone button widget.

:class:`SideNav <bootstack.widgets.sidenav.SideNav>` —
sidebar navigation panel.

API
---

The complete reference for :class:`CommandBar <bootstack.CommandBar>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.CommandBar

Full Example
------------

.. literalinclude:: ../../docs/examples/commandbar.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
