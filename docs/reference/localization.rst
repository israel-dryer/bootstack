Localization (i18n)
===================

bootstack apps can speak the user's language and follow their regional
conventions. There are two halves:

- **Value formatting** — rendering numbers, dates, times, and money the way a
  locale writes them (``LV``).
- **Translation** — showing text in the active language. The framework's own
  strings (dialog buttons, built-in labels) are translated into the bundled
  locales automatically, and ``L`` marks your own text for translation.

Most of this happens for free once you set a locale.

Setting the locale
------------------

Pass ``locale=`` to the app. Omit it and bootstack auto-detects the system
locale; ``localize_mode=`` controls whether localization is active at all:

.. code-block:: python

   import bootstack as bs

   with bs.App(locale="de_DE") as app:          # explicit locale
       ...
   app.run()

   bs.App()                                      # auto-detect from the system
   bs.App(localize_mode=True)                    # force on
   bs.App(localize_mode=False)                   # force off (use source strings)

``localize_mode`` accepts ``"auto"`` (the default — localize when a locale is
detected), ``True`` (always), or ``False`` (never). Read or change the active
locale at runtime through ``app.locale``:

.. code-block:: python

   app.locale            # "de_DE"
   app.locale = "fr_FR"  # switch at runtime (see "Reacting to locale changes")

Formatting numbers, dates, and money
------------------------------------

``LV(value, spec)`` formats a value for the active locale. Drop it anywhere a
widget takes text, and it re-formats itself when the locale changes:

.. code-block:: python

   from datetime import date
   from bootstack.i18n import LV

   bs.Label(LV(1234.56, "currency"))        # "$1,234.56" en_US · "1.234,56 €" de_DE
   bs.Label(LV(0.42, "percent"))            # "42%"
   bs.Label(LV(date(2025, 9, 2), "longDate"))

For a value that **changes** — bound to a :class:`~bootstack.Signal` — use the
widget's ``value_format=`` instead. It applies the same spec to the signal's
value and re-formats live as either the value or the locale changes:

.. code-block:: python

   total = bs.Signal(1234.56)
   bs.Label(textsignal=total, value_format="currency")   # re-formats when total changes

So ``LV`` formats a one-off value and ``value_format=`` formats a reactive one;
both take the same format specs below.

.. _value-formats:

Format specs
~~~~~~~~~~~~

A format spec — accepted by ``LV(value, spec)`` and by a widget's
``value_format=`` — is a **named preset**, a **custom pattern**, or an options
**dict**.

**Number presets:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Preset
     - Formats…
   * - ``"decimal"``
     - a number with the locale's grouping and decimal marks.
   * - ``"fixedPoint"``
     - a number with a fixed number of decimal places.
   * - ``"currency"``
     - money in the locale's default currency.
   * - ``"percent"``
     - a fraction as a percentage (``0.42`` → ``42%``).
   * - ``"exponential"``
     - scientific notation.
   * - ``"thousands"`` / ``"millions"`` / ``"billions"`` / ``"trillions"``
     - a number scaled to that unit with a short suffix (``12000`` → ``12K``).
   * - ``"largeNumber"``
     - a compact number, choosing the unit automatically.

**Date and time presets:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Preset
     - Formats…
   * - ``"shortDate"`` / ``"longDate"``
     - a date, numeric or spelled out.
   * - ``"shortTime"`` / ``"longTime"``
     - a time of day.
   * - ``"shortDateShortTime"`` / ``"longDateLongTime"``
     - a date and time together.
   * - ``"monthAndDay"`` / ``"monthAndYear"`` / ``"quarterAndYear"``
     - a partial date.
   * - ``"year"`` / ``"quarter"`` / ``"month"`` / ``"day"`` / ``"dayOfWeek"`` / ``"hour"`` / ``"minute"`` / ``"second"`` / ``"millisecond"``
     - a single date or time component.

**Custom patterns** — for full control, pass a CLDR/Babel pattern string,
applied in the active locale: ``"#,##0"`` / ``"#,##0.00"`` (numbers),
``"yyyy-MM-dd"`` / ``"dd.MM.yy"`` (dates).

**Options dict** — pass a dict for fine control, e.g.
``{"type": "currency", "currency": "EUR", "precision": 2}`` or
``{"type": "custom", "pattern": "#,##0.0"}``.

Locale-aware input widgets — :doc:`/widgets/numberfield`,
:doc:`/widgets/datefield`, :doc:`/widgets/timefield` — read user input back in the
active locale automatically, so a German user can type ``1.234,56`` and you get
``1234.56``.

Translating your own text
-------------------------

Widget text is translated **automatically**. In the default
``localize_mode="auto"``, a plain string is translated when a translation is
registered for the active locale, and shown as-is otherwise — so ordinary text
needs no wrapping:

.. code-block:: python

   bs.Label("Save")        # renders the translation of "Save" if one is registered
   bs.Button("Cancel")     # same — no L() needed

Register your own translations with the catalog functions (inside a running app):

.. code-block:: python

   from bootstack.i18n import add_translations

   add_translations("es", {"Save": "Guardar", "Cancel": "Cancelar"})
   add_translations("de", {"Save": "Speichern", "Cancel": "Abbrechen"})

- ``add_translation(locale, source, translated)`` — register one string.
- ``add_translations(locale, mapping)`` — register a ``{source: translated}`` batch.
- ``load_translations(directory)`` — load ``.msg`` catalog files from a folder.

Use ``L(...)`` when you need **interpolation** — it looks up the translation and
fills in ``{}``-style placeholders with `str.format` (positional or named):

.. code-block:: python

   from bootstack.i18n import L

   bs.Label(L("Hello, {0}", name))         # positional
   bs.Label(L("Hello, {name}", name=user)) # named

Opting a widget out
~~~~~~~~~~~~~~~~~~~

Every text widget takes a ``localize=`` argument — ``True``, ``False``, or
``"auto"`` — to override the app default for one widget. Set ``False`` to keep a
proper noun, brand name, or identifier from being translated:

.. code-block:: python

   bs.Label("Acme Corp", localize=False)   # never translated

bootstack's own widget text (dialog buttons, built-in labels) is already
translated for every bundled locale out of the box — see below.

Reading locale conventions
--------------------------

When you need a locale's raw conventions — to configure a custom widget, say —
the app exposes them as read-only properties derived from ``app.locale``:

.. code-block:: python

   app.locale_language       # "de"      — the base language
   app.locale_decimal        # ","       — decimal separator
   app.locale_thousands      # "."       — grouping separator
   app.locale_date_format    # "dd.MM.yy"
   app.locale_time_format    # "HH:mm"

Reacting to locale changes
--------------------------

Setting ``app.locale`` switches the locale **live**: text and values bound with
``L`` / ``LV`` re-resolve themselves, the framework's own strings update, and
``on_locale_change`` fires with the new code. A language switcher needs no manual
rebuild — just set the locale:

.. code-block:: python

   def switch_language(code):
       app.locale = code          # L/LV-bound widgets refresh automatically

   app.on_locale_change(lambda code: print("now speaking", code))

.. note::

   Automatic refresh covers text and values bound through ``L`` / ``LV`` (and a
   ``Signal`` with a ``value_format``). Text you set imperatively — e.g.
   ``label.text = "…"`` — is a plain string with no locale binding, so re-apply it
   yourself from ``on_locale_change`` if it needs to follow the switch.

Bundled translations
---------------------

bootstack ships its own UI strings translated into a range of locales — Arabic,
Chinese (Simplified and Traditional), Czech, Danish, Dutch, English, French,
German, Hebrew, Hindi, Italian, Japanese, Korean, Norwegian, Polish, Portuguese
(and Brazilian), Spanish, Swedish, Turkish, and more. Selecting one of these
locales translates the built-in widgets automatically.

See also
--------

- :doc:`/reference/typography` — fonts and the ``font=`` token system.
- :doc:`/widgets/datefield` — date input that respects the locale's date format.
- :doc:`/widgets/numberfield` — number input parsed in the active locale.

API reference
-------------

The complete reference lives in :doc:`/api-reference/i18n`. At a glance:

.. currentmodule:: bootstack.i18n

.. autosummary::
   :nosignatures:

   L
   LV
   add_translation
   add_translations
   load_translations
