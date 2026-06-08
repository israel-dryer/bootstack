API Overview
============

This page maps the public API — where each piece lives.

The widgets and other building blocks of a UI are available at the top level.
Import the package once as ``import bootstack as bs`` and use them as
``bs.Button`` or ``bs.App``. The framework primitives — data sources, themes,
validation, and the like — live in dedicated submodules.

Top level
---------

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - Group
     - Includes
   * - Widgets
     - Every widget — buttons, inputs, tables, trees, layout, navigation,
       overlays, and forms (see :doc:`/widgets/index`)
   * - Application
     - ``App``, ``AppShell``, ``Window``
   * - State
     - ``Signal``, the reactive value behind two-way binding
   * - Dialogs
     - The one-shot helpers ``alert``, ``confirm``, the ``ask_*`` family, and
       ``toast``
   * - Theme switching
     - ``set_theme`` and ``toggle_theme``

Submodules
----------

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - Module
     - What it's for
   * - ``bootstack.data``
     - Data sources and the ``col`` filter language — :doc:`/reference/data-sources`
   * - ``bootstack.style``
     - Themes, colors, and fonts — :doc:`/reference/theming`,
       :doc:`/reference/typography`
   * - ``bootstack.i18n``
     - Translating text and formatting values per locale — :doc:`/reference/localization`
   * - ``bootstack.events``
     - Event objects and the typed payloads handlers receive — :doc:`/reference/events`
   * - ``bootstack.streams``
     - Shaping events into pipelines (debounce, filter, map) — :doc:`/reference/streams`
   * - ``bootstack.validation``
     - Rules that check what a user types — :doc:`/reference/validation`
   * - ``bootstack.scheduling``
     - Running work later or on a repeat — :doc:`/reference/scheduling`
   * - ``bootstack.shortcuts``
     - Registering keyboard shortcuts — :doc:`/reference/shortcuts`
   * - ``bootstack.store``
     - A small file-backed settings store — :doc:`/reference/store`
   * - ``bootstack.errors``
     - The exceptions the framework raises — :doc:`/reference/errors`
   * - ``bootstack.types``
     - Token and keyword types for annotating your own code
   * - ``bootstack.widgets.dialogs``
     - Reusable dialog classes, when a one-shot verb isn't enough
