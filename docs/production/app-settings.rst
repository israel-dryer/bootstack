App Configuration
=================

An app is configured entirely through flat constructor keyword arguments, and
that same configuration is read and changed at runtime through matching ``app.*``
properties. What goes in comes back out symmetrically — ``bs.App(theme=...)`` in,
``app.theme`` out — so there is no separate settings object to construct, inject,
or look up. The same surface is shared by :class:`App
<bootstack.widgets.app.App>` and :class:`AppShell
<bootstack.widgets.appshell.AppShell>`.

.. code-block:: python

   import bootstack as bs

   with bs.App(
       title="My App",
       theme="bootstrap-dark",
       locale="de_DE",
       size=(900, 600),
   ) as app:
       bs.Label("Hallo!")
   app.run()

Reading and changing configuration
----------------------------------

Every configuration option is a property on the app. Reading returns the current
value; assigning changes it, and for the options the toolkit can change live
(theme, locale, title) the change takes effect immediately:

.. code-block:: python

   app.theme                       # 'bootstrap-dark'
   app.theme = "bootstrap-light"   # switches the theme now
   app.title = "Renamed window"    # updates the title bar now
   app.locale = "fr_FR"            # re-localizes now

The available options:

.. list-table::
   :header-rows: 1
   :widths: 30 18 52

   * - Property
     - Access
     - Meaning
   * - ``title``
     - read/write
     - Window title bar text and the app's display name.
   * - ``theme``
     - read/write
     - Active theme name; assigning switches the theme live.
   * - ``light_theme`` / ``dark_theme``
     - read/write
     - The pair ``toggle_theme()`` and system-appearance tracking switch between.
   * - ``follow_system_appearance``
     - read/write
     - Track the OS light/dark setting (currently effective on macOS).
   * - ``locale``
     - read/write
     - Active locale (e.g. ``'en_US'``); assigning re-localizes live.
   * - ``locale_language``
     - read-only
     - Base language derived from the locale (e.g. ``'de'``).
   * - ``locale_date_format`` / ``locale_time_format``
     - read-only
     - Short date / time pattern for the active locale.
   * - ``locale_decimal`` / ``locale_thousands``
     - read-only
     - Decimal / thousands separator for the active locale.
   * - ``window_style``
     - read/write
     - Windows-only window effect (``'mica'``, ``'acrylic'``, …) or ``None``.
   * - ``remember_window_state``
     - read/write
     - Save the window geometry on close and restore it next launch.

Construction-only options
-------------------------

Some configuration is set once at construction and has no live ``app.*`` property
(changing it at runtime would be incomplete or meaningless): ``localize_mode``,
``macos_quit_behavior``, ``state_path``, ``available_themes``, and the window
geometry options (``size``, ``position``, ``min_size``, ``max_size``,
``resizable``, ``scaling``, ``hdpi``). Pass them to ``App(...)`` / ``AppShell(...)``.
The exposed theme list is read at runtime via :func:`get_themes
<bootstack.style.get_themes>`.

Theme and appearance
--------------------

Set the startup theme with ``theme=``; switch it later through ``app.theme`` or
the global ``bs.toggle_theme()`` / ``bs.set_theme()`` helpers. ``toggle_theme``
flips between the ``light_theme`` and ``dark_theme`` pair:

.. code-block:: python

   app = bs.App(theme="bootstrap-light",
                light_theme="bootstrap-light",
                dark_theme="bootstrap-dark")

   bs.Button("Toggle", on_click=bs.toggle_theme)

On macOS, ``follow_system_appearance=True`` switches between the light and dark
themes automatically when the user changes the OS appearance. See
:doc:`/reference/theming` for defining and installing custom themes.

Localization
------------

``locale=`` sets the active locale. ``localize_mode=`` controls automatic text
translation for the whole app — ``"auto"`` (the default — translate when a
translation is registered for the locale, otherwise show the literal), ``True``
(always), or ``False`` (never); an individual widget overrides it with
``localize=``. Register your own translations with
:func:`~bootstack.i18n.add_translations` — see :doc:`/reference/localization`.

The locale-derived formatting values are exposed as read-only properties (they
are computed from the locale, so they update whenever ``app.locale`` changes):

.. code-block:: python

   app = bs.App(locale="de_DE")
   app.locale_date_format    # 'dd.MM.yy'
   app.locale_decimal        # ','

   app.locale = "en_US"
   app.locale_decimal        # '.'

Reacting to changes
-------------------

Subscribe to configuration changes to keep other state in sync — the handler
receives the new value directly:

.. code-block:: python

   app.on_theme_change(lambda theme: print("theme is now", theme))
   app.on_locale_change(lambda locale: print("locale is now", locale))

Like other event hooks, calling these without a handler returns a composable
:doc:`stream </reference/streams>`.

Persisting configuration
------------------------

Because configuration is flat keyword arguments and a :class:`Store
<bootstack.store.Store>` is a flat dict, persistence is symmetric: splat the
store in to restore on startup, and write each value back when it changes.
``App.from_store()`` does the restore and *tolerantly ignores keys that are not
valid configuration*, so a settings file from an older or newer version (with
renamed or removed keys) still loads cleanly instead of raising:

.. code-block:: python

   from bootstack.store import Store

   store = Store("settings")          # app config, in its own store

   app = bs.App.from_store(store)        # restore; empty store → defaults
   app.on_theme_change(lambda theme: store.update(theme=theme))
   app.on_locale_change(lambda locale: store.update(locale=locale))
   app.run()

``AppShell.from_store()`` works the same way. A few practices keep this clean:

- **Keep app *config* separate from app *state*.** Put restorable configuration
  (theme, locale) in one store and transient state (recent files, last-opened
  tab) in another, so ``from_store`` only ever sees real configuration keys.
- **Window geometry is the one exception.** It is a fiddly ``"WxH+X+Y"`` string
  updated continuously as the window moves, not a clean keyword — let the
  built-in ``remember_window_state=True`` flag handle it rather than the store.
- **Per-value write-back, not a config dump.** React to the specific change
  events and write just that key.

Window state persistence
------------------------

``remember_window_state=True`` saves the window's size and position when it
closes and restores them on the next launch (off-screen positions are clamped
back onto a visible monitor). It is stored in a per-app file under the OS config
directory; pass ``state_path=`` to override the location.

.. code-block:: python

   bs.App(title="My App", remember_window_state=True)

See also
--------

- :doc:`/reference/theming` — defining themes and the values worth persisting.
- :doc:`/reference/store` — the preferences store and persistence patterns.
