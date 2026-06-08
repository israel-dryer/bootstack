The bootstack namespace
=======================

bootstack organizes its public API by *how you use it*.

**Compose** — what you reach for while building a UI — lives at the top level,
under ``import bootstack as bs``: every widget, the application objects, the
reactive ``Signal``, and a few imperative verbs.

**Configure** — the framework primitives you reference *by type* to shape
behavior (data sources, validation rules, themes, events, …) — lives in
submodules you import explicitly, e.g. ``from bootstack.data import
SqliteDataSource``.

This keeps ``bs.`` autocompletion focused on the widget palette and gives every
primitive a clear, discoverable home.

Top level — ``import bootstack as bs``
--------------------------------------

- **Widgets** — every widget: ``Button``, ``Label``, ``TextField``,
  ``DataTable``, ``Tree``, the layout containers, navigation, overlays, forms,
  and the rest. See :doc:`/widgets/index`.
- **Application & windows** — ``App``, ``AppShell``, ``Window``.
- **Reactive state** — ``Signal``.
- **Dialog verbs** — ``alert``, ``confirm``, ``ask_string``, ``ask_integer``,
  ``ask_float``, ``ask_date``, ``ask_date_range``, ``ask_item``, ``ask_color``,
  ``ask_font``, ``ask_filter``, and ``toast``.
- **Theme switching** — ``set_theme``, ``toggle_theme``.

Submodules — import explicitly
------------------------------

.. list-table::
   :header-rows: 1
   :widths: 32 68

   * - Import from
     - What lives there
   * - ``bootstack.data``
     - Data sources (``MemoryDataSource``, ``SqliteDataSource``,
       ``FileDataSource``), the ``col`` filter DSL (``col`` / ``any_of`` /
       ``all_of``), and the protocol + base class for custom sources.
       → :doc:`/reference/data-sources`
   * - ``bootstack.style``
     - ``Theme`` plus the theming and typography functions
       (``get_theme_color``, ``get_themes``, ``set_font_family``,
       ``update_font_token``, …). → :doc:`/reference/theming`,
       :doc:`/reference/typography`
   * - ``bootstack.i18n``
     - ``L`` (translated text) and ``LV`` (locale-formatted value).
       → :doc:`/reference/localization`
   * - ``bootstack.events``
     - ``Event``, ``Subscription``, and the typed event payloads.
       → :doc:`/reference/events`
   * - ``bootstack.streams``
     - ``Stream``, ``Handle``. → :doc:`/reference/streams`
   * - ``bootstack.validation``
     - ``ValidationRule``, ``ValidationResult``. → :doc:`/reference/validation`
   * - ``bootstack.scheduling``
     - ``Schedule``, ``Job``. → :doc:`/reference/scheduling`
   * - ``bootstack.shortcuts``
     - ``Shortcuts``, ``Shortcut``, ``get_shortcuts``.
       → :doc:`/reference/shortcuts`
   * - ``bootstack.store``
     - ``Store``. → :doc:`/reference/store`
   * - ``bootstack.errors``
     - ``BootstackError`` and its subclasses. → :doc:`/reference/errors`
   * - ``bootstack.signals``
     - ``Signal`` (also top level) and ``TraceOperation``.
       → :doc:`/reference/signals`
   * - ``bootstack.types``
     - Token Literals and keyword TypedDicts for annotations
       (``AccentToken``, ``VariantToken``, ``SurfaceToken``, ``WidgetDensity``,
       …).
   * - ``bootstack.widgets.dialogs``
     - The dialog *classes* (``Dialog``, ``FormDialog``, ``FontDialog``,
       ``ColorChooserDialog``, ``FilterDialog``, …) for when you want a reusable
       object instead of a one-shot verb.
   * - ``bootstack.widgets``
     - ``PublicWidgetBase`` / ``PublicContainer`` — base classes for building
       your own widgets.

.. note::

   A couple of high-traffic names are deliberately available in both places:
   ``Signal`` (top level *and* ``bootstack.signals``) and ``set_theme`` /
   ``toggle_theme`` (top level *and* ``bootstack.style``). They are common
   enough to promote, but their home module still holds them.
