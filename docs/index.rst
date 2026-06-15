:html_theme.sidebar_secondary.remove: true

bootstack
=========

*Python desktop apps without the ceremony.*

bootstack is a batteries-included framework for building desktop applications in
Python. You describe the interface with nested ``with`` blocks — the code
hierarchy *is* the layout — and bootstack handles spacing, theming, reactive
state, and packaging. No geometry math, no manual parenting, no CSS.

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
   :alt: A bootstack window with three accent buttons — light theme

.. image:: /_static/examples/quickstart-hello-dark.png
   :class: bs-screenshot-dark bs-window-screenshot
   :alt: A bootstack window with three accent buttons — dark theme

Why bootstack
-------------

- **Declarative layout** — ``VStack`` / ``HStack`` / ``Grid`` containers place and
  space children for you, and the ``with`` blocks mirror your UI.
- **Reactive signals** — bind a value once and it flows to every widget that uses
  it, in both directions.
- **Semantic styling** — ``accent="primary"``, ``variant="outline"``; the same
  code looks right across every theme and in light or dark mode.
- **60+ widgets** — inputs, tables, trees, calendars, a syntax-highlighting code
  editor, and more, out of the box.
- **A real CLI** — scaffold a project, run it, and package a standalone
  executable with ``bootstack build``.

Start here
----------

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: Quick Start
      :link: getting-started/quickstart
      :link-type: doc

      Your first window in 60 seconds — then navigation apps and reactive state.

   .. grid-item-card:: User Guide
      :link: user-guide/index
      :link-type: doc

      Goal-oriented how-to guides and subsystem topics: input, actions, data,
      forms, layout, navigation, theming, and more.

   .. grid-item-card:: Widgets
      :link: widgets/index
      :link-type: doc

      The visual catalog — every component with worked examples and screenshots.

   .. grid-item-card:: API Reference
      :link: api-reference/index
      :link-type: doc

      The complete public API, grouped by concept and titled by import path.

   .. grid-item-card:: Production
      :link: production/index
      :link-type: doc

      Packaging, the CLI, debugging, and application settings for shipping.

Install
-------

bootstack requires Python 3.12 or newer:

.. code-block:: bash

   pip install git+https://github.com/israel-dryer/bootstack.git

To tour everything bootstack ships without writing a line of code, launch the
gallery:

.. code-block:: bash

   bootstack gallery

.. toctree::
   :hidden:
   :maxdepth: 2

   user-guide/index
   widgets/index
   api-reference/index
   production/index
