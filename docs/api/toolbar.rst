Toolbar
=======

A horizontal strip of buttons, labels, separators, and other widgets.
Items are added left-to-right via ``add_button()``, ``add_label()``,
``add_separator()``, ``add_spacer()``, and ``add_widget()``.

.. code-block:: python

   tb = bs.Toolbar(fill="x")
   tb.add_button("New", icon="file-earmark-plus")
   tb.add_button("Open", icon="folder2-open")
   tb.add_spacer()
   tb.add_button(icon="gear")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/toolbar-light.png"
        alt="Toolbar demo — light theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/toolbar-dark.png"
        alt="Toolbar demo — dark theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">

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

Use ``on_click=`` to attach a callback, and ``accent=`` / ``variant=`` to
style individual buttons differently from the toolbar default.

.. code-block:: python

   tb.add_button("Publish", icon="cloud-upload", accent="primary", on_click=publish)
   tb.add_button("Discard", icon="trash", accent="danger", on_click=discard)

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
toolbars such as a rich-text formatting strip.

.. code-block:: python

   tb = bs.Toolbar(fill="x", density="compact")
   tb.add_button(icon="type-bold")
   tb.add_button(icon="type-italic")
   tb.add_button(icon="type-underline")

Button variant
~~~~~~~~~~~~~~

``button_variant=`` sets the default variant for all buttons added to the
toolbar. Override per-button with the ``variant=`` argument on
``add_button()``.

.. code-block:: python

   tb = bs.Toolbar(fill="x", button_variant="outline")
   tb.add_button("Save", icon="floppy")        # outline
   tb.add_button("Run", variant="solid")       # override to solid

Custom widgets
~~~~~~~~~~~~~~

Use ``add_widget()`` to embed any widget (e.g. a
:class:`Select <bootstack.widgets.select.Select>`) in the toolbar. Create the
widget with the toolbar as its parent first.

.. code-block:: python

   tb = bs.Toolbar(fill="x")
   branch = bs.Select(
       ["main", "dev", "feat/new-ui"],
       parent=tb,
   )
   tb.add_widget(branch)

Custom titlebar
~~~~~~~~~~~~~~~

Set ``show_window_controls=True`` to add minimize, maximize, and close buttons
on the right, and ``draggable=True`` to let the user drag the window by the
toolbar. Pair with ``undecorated=True`` on the App to remove the OS title bar.

.. code-block:: python

   with bs.App(title="My App", undecorated=True) as app:
       tb = bs.Toolbar(
           fill="x",
           show_window_controls=True,
           draggable=True,
       )
       tb.add_label("My App", font="heading-md")
       tb.add_spacer()
       ...
   app.run()

Toolbar inside AppShell
~~~~~~~~~~~~~~~~~~~~~~~

:class:`AppShell <bootstack.widgets.appshell.AppShell>` includes a built-in
toolbar. Access it via ``shell.toolbar`` and call the same ``add_*`` methods.
Use ``command=`` (not ``on_click=``) when calling ``add_button()`` on the
AppShell toolbar.

.. code-block:: python

   with bs.AppShell(title="My App") as shell:
       shell.toolbar.add_spacer()
       shell.toolbar.add_button(icon="circle-half", command=bs.toggle_theme)
       ...

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

:class:`AppShell <bootstack.widgets.appshell.AppShell>` —
full application scaffold with a built-in toolbar, sidebar, and page stack.

:class:`Button <bootstack.widgets.button.Button>` —
standalone button widget.

:class:`SideNav <bootstack.widgets.sidenav.SideNav>` —
sidebar navigation panel.

API
---

.. autoclass:: bootstack.widgets.toolbar.Toolbar
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/toolbar.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs