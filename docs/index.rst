:html_theme.sidebar_secondary.remove: true

bootstack
=========

.. rst-class:: bs-lead

From idea to a shipped desktop app — fast.

bootstack gives engineers, data scientists, and hobbyists everything to build a
polished desktop interface and package it into a standalone executable —
declarative, reactive, and batteries-included, all in pure Python.

.. container:: hero-ctas

   .. button-ref:: getting-started/quickstart
      :ref-type: doc
      :color: primary
      :class: sd-px-4 sd-fs-5

      Get started

   .. button-ref:: widgets/index
      :ref-type: doc
      :color: secondary
      :outline:
      :class: sd-px-4 sd-fs-5

      Browse widgets

.. image:: /_static/examples/home-hero-light.png
   :class: bs-screenshot-light bs-window-screenshot
   :alt: A bootstack analytics dashboard — light theme

.. image:: /_static/examples/home-hero-dark.png
   :class: bs-screenshot-dark bs-window-screenshot
   :alt: A bootstack analytics dashboard — dark theme

Why bootstack
-------------

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: :octicon:`code;1.5em;sd-mr-1` Declarative and reactive

      Your code mirrors the interface — nested ``with`` blocks *are* the layout —
      and state bound once flows to every widget that uses it. No geometry math,
      no manual wiring.

   .. grid-item-card:: :octicon:`package;1.5em;sd-mr-1` Batteries included

      50+ themed widgets — tables, trees, calendars, a syntax-highlighting code
      editor, forms with validation, and data sources — plus icons and
      localization. The pieces of a real application, already built.

   .. grid-item-card:: :octicon:`paintbrush;1.5em;sd-mr-1` Looks right by default

      Semantic styling — ``accent="primary"``, ``variant="outline"`` — instead of
      hand-picked colors, so the same code looks correct across eight light/dark
      themes and switches at runtime.

   .. grid-item-card:: :octicon:`terminal;1.5em;sd-mr-1` Ready to ship

      Lightweight to install with no heavy runtime, and a CLI that scaffolds,
      runs, and packages your project into a standalone executable.

A glimpse
---------

A complete window is a handful of lines — the structure you read is the structure
you get:

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

Start here
----------

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: :octicon:`rocket;1.5em;sd-mr-1` Quick Start
      :link: getting-started/quickstart
      :link-type: doc

      Your first window in minutes — then navigation apps and reactive state.

   .. grid-item-card:: :octicon:`book;1.5em;sd-mr-1` User Guide
      :link: user-guide/index
      :link-type: doc

      Goal-oriented how-to guides and subsystem topics.

   .. grid-item-card:: :octicon:`apps;1.5em;sd-mr-1` Widgets
      :link: widgets/index
      :link-type: doc

      The visual catalog — every component with examples and screenshots.

   .. grid-item-card:: :octicon:`code;1.5em;sd-mr-1` API Reference
      :link: api-reference/index
      :link-type: doc

      The complete public API, grouped by concept.

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
