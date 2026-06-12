:html_theme.sidebar_secondary.remove: true

API Reference
=============

The complete reference for the public API, grouped by concept. Every public
class, function, and type has exactly one page here, titled by its full import
path — so you can confirm an exact signature, read the full member list, or
discover what lives alongside what.

Everything exposed at the top level — every widget, the application shells,
reactive ``Signal`` state, and the dialog and theme verbs — is public and
importable directly as ``bootstack.<name>`` (commonly ``import bootstack as bs``).
The following submodules are also public; import the names you need from each
(e.g. ``from bootstack.data import col``):

- ``bootstack.data`` — Data sources and the ``col()`` query language behind
  tables, lists, and trees.
- ``bootstack.events`` — Event objects and the typed payloads ``on_*`` handlers
  receive.
- ``bootstack.streams`` — Composable event pipelines — debounce, filter, map.
- ``bootstack.images`` — Image handles, themed icons, and application icons.
- ``bootstack.style`` — Color themes, runtime theme switching, and fonts.
- ``bootstack.validation`` — Rules that validate what a user enters.
- ``bootstack.i18n`` — Translatable text and locale-aware formatting.
- ``bootstack.scheduling`` — Running work after a delay or on a repeating interval.
- ``bootstack.shortcuts`` — Registering application keyboard shortcuts.
- ``bootstack.store`` — A small file-backed preferences store.
- ``bootstack.errors`` — The exception types the framework raises.
- ``bootstack.types`` — Token and keyword types for annotating your own code.
- ``bootstack.dialogs`` — Reusable dialog classes, when a one-shot verb isn't enough.

Everything else is internal. Modules and names beginning with an underscore —
``_core``, ``_impl``, ``_runtime``, and the like — are implementation detail and
may change at any time; the public API is exactly what this reference documents.

This is the lookup layer. For task-oriented introductions and worked examples,
start from the :doc:`/widgets/index` catalog and the :doc:`/user-guide/index`,
which cross-link into the pages here.

Building the interface
----------------------

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: Application
      :link: application
      :link-type: doc

      The app frame — ``App``, ``AppShell``, and secondary windows.

   .. grid-item-card:: Widgets
      :link: widgets
      :link-type: doc

      Every visual component — actions, inputs, selection controls, data
      displays, layout containers, and navigation.

   .. grid-item-card:: Reactivity
      :link: reactivity
      :link-type: doc

      Signals and event streams — bind application state to widgets and compose
      change pipelines.

   .. grid-item-card:: Events
      :link: events
      :link-type: doc

      The typed payloads every ``on_*`` handler receives.

   .. grid-item-card:: Dialogs
      :link: dialogs
      :link-type: doc

      One-shot prompt verbs (``alert``, ``confirm``, ``ask_*``) and the dialog
      classes behind them.

Data and validation
-------------------

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: Data
      :link: data
      :link-type: doc

      Data sources, the ``col()`` query language, and the file reader/writer
      registry behind tables, lists, and trees.

   .. grid-item-card:: Validation
      :link: validation
      :link-type: doc

      Field validation rules and the results they produce.

Appearance and locale
---------------------

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: Images
      :link: images
      :link-type: doc

      Image handles, theme-aware icons, and generated application icons.

   .. grid-item-card:: Theming
      :link: theming
      :link-type: doc

      Color themes, runtime theme switching, and fonts.

   .. grid-item-card:: Localization
      :link: i18n
      :link-type: doc

      Translatable strings and locale-aware formatting.

Services and reference
----------------------

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: Scheduling
      :link: scheduling
      :link-type: doc

      Run callbacks after a delay or on a repeating interval.

   .. grid-item-card:: Shortcuts
      :link: shortcuts
      :link-type: doc

      Register and query application keyboard shortcuts.

   .. grid-item-card:: Storage
      :link: store
      :link-type: doc

      A persistent, file-backed preferences store.

   .. grid-item-card:: Errors
      :link: errors
      :link-type: doc

      The exception types bootstack raises.

   .. grid-item-card:: Types
      :link: types
      :link-type: doc

      Token and keyword types for annotating your own code.

.. toctree::
   :hidden:
   :maxdepth: 1

   application
   widgets
   reactivity
   events
   dialogs
   data
   validation
   images
   theming
   i18n
   scheduling
   shortcuts
   store
   errors
   types
