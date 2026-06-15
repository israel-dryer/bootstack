Quick Start
===========

Your first app takes about 60 seconds.

Hello bootstack
---------------

.. code-block:: python

   import bootstack as bs

   with bs.App(title="Hello", padding=16, gap=16) as app:
       bs.Label("Hello from bootstack!")
       bs.Button("Primary", accent="primary")
       bs.Button("Success", accent="success")
       bs.Button("Danger Outline", accent="danger", variant="outline")

   app.run()

.. image:: /_static/examples/quickstart-hello-light.png
   :class: bs-screenshot-light bs-window-screenshot
   :alt: The Hello bootstack window — light theme

.. image:: /_static/examples/quickstart-hello-dark.png
   :class: bs-screenshot-dark bs-window-screenshot
   :alt: The Hello bootstack window — dark theme

A few things to notice:

- ``with bs.App(...) as app:`` creates the window and pushes it onto the
  layout context. Widgets created inside the block automatically become
  children — no ``parent=`` argument needed.
- ``bs.Label`` and ``bs.Button`` accept their primary content as the first
  positional argument.
- ``accent=`` sets the color intent; ``variant=`` sets the visual weight.
  The same code looks correct across all themes.
- ``app.run()`` starts the event loop. It goes *after* the ``with`` block.

Navigation apps
---------------

For apps with a sidebar and multiple pages, use ``AppShell``:

.. code-block:: python

   import bootstack as bs

   with bs.AppShell(title="My App") as shell:
       with shell.add_page("home", text="Home", icon="house"):
           with bs.VStack(padding=20, gap=8):
               bs.Label("Welcome!", font="heading-lg")
               bs.Label("Select a page from the sidebar.", accent="secondary")

       with shell.add_page("data", text="Data", icon="table"):
           with bs.VStack(padding=20, gap=8):
               bs.Label("Your data goes here.", font="heading-lg")

       shell.navigate("home")

   shell.run()

.. image:: /_static/examples/quickstart-navigation-light.png
   :class: bs-screenshot-light bs-window-screenshot
   :alt: An AppShell navigation window — light theme

.. image:: /_static/examples/quickstart-navigation-dark.png
   :class: bs-screenshot-dark bs-window-screenshot
   :alt: An AppShell navigation window — dark theme

``shell.add_page()`` returns a page container. Use it as a context manager
to place widgets inside it. ``shell.navigate()`` sets the initially visible
page.

Reactive state
--------------

When the same value needs to drive multiple widgets, use a ``Signal``:

.. code-block:: python

   import bootstack as bs

   with bs.App(title="Signals", padding=20, gap=12) as app:
       name = bs.Signal("World")
       bs.Label("Live preview:", font="caption", accent="secondary")
       bs.Label(textsignal=name, font="heading-md", accent="primary")
       bs.TextField(placeholder="Type a name…", textsignal=name)

   app.run()

``Signal`` holds a value. Any widget bound with ``textsignal=`` updates
automatically when the signal changes — no manual callbacks needed.

Next steps
----------

- :doc:`app-structures` — choose the right container for your app
- :doc:`../tasks/layout` — arrange widgets with stacks and grids
- :doc:`../tasks/getting-input` — text fields, sliders, and date pickers
- :doc:`../tasks/dialogs` — alerts, confirmations, and input dialogs
