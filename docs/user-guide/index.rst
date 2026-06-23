User Guide
==========

Everything you need to build real applications with bootstack — start with setup
and the basics, reach for a how-to when you have a specific task in mind, or read
a topic guide to learn a subsystem end to end. For the complete lookup of every
public name, see the :doc:`/api-reference/index`; for the visual widget catalog,
see :doc:`/widgets/index`.

Getting started
---------------

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: :octicon:`download;1.5em;sd-mr-1` Installation
      :link: /getting-started/installation
      :link-type: doc

      Install bootstack and confirm your environment is ready.

   .. grid-item-card:: :octicon:`rocket;1.5em;sd-mr-1` Quick Start
      :link: /getting-started/quickstart
      :link-type: doc

      Your first window, a navigation app, and reactive state — in a few minutes.

   .. grid-item-card:: :octicon:`device-desktop;1.5em;sd-mr-1` App Structures
      :link: /getting-started/app-structures
      :link-type: doc

      Choose the right top-level container: App, AppShell, or Window.

How-to guides
-------------

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: :octicon:`columns;1.5em;sd-mr-1` Arranging Widgets
      :link: /tasks/layout
      :link-type: doc

      Arrange widgets with stacks and grids; fill, expand, and anchor.

   .. grid-item-card:: :octicon:`pencil;1.5em;sd-mr-1` Getting Input
      :link: /tasks/getting-input
      :link-type: doc

      Text, numbers, dates, choices, and sliders — and binding them to state.

   .. grid-item-card:: :octicon:`zap;1.5em;sd-mr-1` Handling Actions
      :link: /tasks/handling-actions
      :link-type: doc

      Buttons, events, debounced streams, shortcuts, and menus.

   .. grid-item-card:: :octicon:`copy;1.5em;sd-mr-1` Using the Clipboard
      :link: /tasks/clipboard
      :link-type: doc

      Read and write the system clipboard.

   .. grid-item-card:: :octicon:`table;1.5em;sd-mr-1` Displaying Data
      :link: /tasks/displaying-data
      :link-type: doc

      Labels, lists, tables, trees, and the data sources behind them.

   .. grid-item-card:: :octicon:`graph;1.5em;sd-mr-1` Visualizing Data
      :link: /tasks/visualizing-data/index
      :link-type: doc

      Embed themed matplotlib/seaborn charts that update from a signal or source.

   .. grid-item-card:: :octicon:`plus-circle;1.5em;sd-mr-1` Composing Fields
      :link: /tasks/composing-fields
      :link-type: doc

      Add icons, labels, buttons, and toggles inside a field to specialize it.

   .. grid-item-card:: :octicon:`checklist;1.5em;sd-mr-1` Building Forms
      :link: /tasks/building-forms
      :link-type: doc

      Lay out fields and validate them before submit.

   .. grid-item-card:: :octicon:`comment-discussion;1.5em;sd-mr-1` Showing Dialogs
      :link: /tasks/dialogs
      :link-type: doc

      Alerts, confirmations, prompts, toasts, and custom dialogs.

   .. grid-item-card:: :octicon:`arrow-switch;1.5em;sd-mr-1` Navigating Views
      :link: /tasks/navigation/index
      :link-type: doc

      Sidebar, master–detail, and workspace navigation shapes.

   .. grid-item-card:: :octicon:`image;1.5em;sd-mr-1` Setting App Icons
      :link: /tasks/application-icons
      :link-type: doc

      Set the runtime and distribution icons from a single glyph.

   .. grid-item-card:: :octicon:`rocket;1.5em;sd-mr-1` Showing Splash Screens
      :link: /tasks/splash-screens
      :link-type: doc

      Intro screens that cover startup — timed branding, welcome, real progress.

Topics
------

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: :octicon:`paintbrush;1.5em;sd-mr-1` Theming
      :link: /reference/theming
      :link-type: doc

      Color themes, runtime switching, and custom themes.

   .. grid-item-card:: :octicon:`typography;1.5em;sd-mr-1` Typography
      :link: /reference/typography
      :link-type: doc

      Fonts and the text-style tokens.

   .. grid-item-card:: :octicon:`image;1.5em;sd-mr-1` Images
      :link: /reference/images
      :link-type: doc

      Image handles and theme-aware icons.

   .. grid-item-card:: :octicon:`globe;1.5em;sd-mr-1` Localization
      :link: /reference/localization
      :link-type: doc

      Translatable text and locale-aware formatting.

   .. grid-item-card:: :octicon:`broadcast;1.5em;sd-mr-1` Signals
      :link: /reference/signals
      :link-type: doc

      Reactive state that flows between widgets.

   .. grid-item-card:: :octicon:`bell;1.5em;sd-mr-1` Events
      :link: /reference/events
      :link-type: doc

      The ``on_*`` model and the typed payloads handlers receive.

   .. grid-item-card:: :octicon:`git-merge;1.5em;sd-mr-1` Streams
      :link: /reference/streams
      :link-type: doc

      Compose, filter, debounce, and throttle event pipelines.

   .. grid-item-card:: :octicon:`check-circle;1.5em;sd-mr-1` Validation
      :link: /reference/validation
      :link-type: doc

      Rules that check what a user enters.

   .. grid-item-card:: :octicon:`database;1.5em;sd-mr-1` Data Sources
      :link: /reference/data-sources
      :link-type: doc

      Sources, the ``col()`` query language, filtering, and paging.

   .. grid-item-card:: :octicon:`archive;1.5em;sd-mr-1` Storage
      :link: /reference/store
      :link-type: doc

      A file-backed preferences store.

   .. grid-item-card:: :octicon:`command-palette;1.5em;sd-mr-1` Shortcuts
      :link: /reference/shortcuts
      :link-type: doc

      Register application keyboard shortcuts.

   .. grid-item-card:: :octicon:`clock;1.5em;sd-mr-1` Scheduling
      :link: /reference/scheduling
      :link-type: doc

      Run work after a delay or on a repeating interval.

   .. grid-item-card:: :octicon:`alert;1.5em;sd-mr-1` Errors
      :link: /reference/errors
      :link-type: doc

      The exception types bootstack raises.

.. toctree::
   :caption: Getting started
   :hidden:

   /getting-started/installation
   /getting-started/quickstart
   /getting-started/app-structures

.. toctree::
   :caption: How-to guides
   :hidden:

   /tasks/layout
   /tasks/getting-input
   /tasks/handling-actions
   /tasks/clipboard
   /tasks/displaying-data
   /tasks/visualizing-data/index
   /tasks/composing-fields
   /tasks/building-forms
   /tasks/dialogs
   /tasks/navigation/index
   /tasks/application-icons
   /tasks/splash-screens

.. toctree::
   :caption: Topics
   :hidden:

   /reference/theming
   /reference/typography
   /reference/images
   /reference/localization
   /reference/signals
   /reference/events
   /reference/streams
   /reference/validation
   /reference/data-sources
   /reference/store
   /reference/shortcuts
   /reference/scheduling
   /reference/errors
