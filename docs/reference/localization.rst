Localization
============

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

Common format specs:

.. list-table::
   :header-rows: 1
   :widths: 22 78

   * - Spec
     - Formats…
   * - ``"decimal"``
     - a number with the locale's grouping and decimal marks.
   * - ``"currency"``
     - money in the locale's default currency.
   * - ``"percent"``
     - a fraction as a percentage (``0.42`` → ``42%``).
   * - ``"thousands"`` / ``"largeNumber"``
     - a compact number (``12000`` → ``12K``).
   * - ``"shortDate"`` / ``"longDate"``
     - a date, numeric or spelled out.
   * - ``"shortTime"`` / ``"longTime"``
     - a time of day.

A CLDR pattern string (e.g. ``"yyyy-MM-dd"``) is also accepted for full control.

Locale-aware input widgets — :doc:`/widgets/numberfield`,
:doc:`/widgets/datefield`, :doc:`/widgets/timefield` — read user input back in the
active locale automatically, so a German user can type ``1.234,56`` and you get
``1234.56``.

Marking text for translation
----------------------------

Wrap a message key in ``L(...)`` wherever a widget takes text and it resolves in
the active locale, re-translating itself on a locale change:

.. code-block:: python

   from bootstack.i18n import L

   bs.Label(L("greeting"))
   bs.Button(L("button.save"), on_click=save)

bootstack's own widget text is translated for every bundled locale out of the
box (see below). A first-class API for registering your *own* application
translation catalogs is still being finalized; until it lands, ``LV`` already
covers locale-aware *values* in full, and ``L`` resolves the bundled strings.

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
