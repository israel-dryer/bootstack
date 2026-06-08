Preferences Store
=================

``Store`` is a small, file-backed key-value store for the bits of state an app
wants to remember between runs — the chosen theme, a "show tips on startup"
flag, recent files, the last-opened tab. It behaves like a dictionary, persists
to a JSON file under the OS configuration directory, and saves on every change.

It is deliberately *not* a data source: there are no rows, ids, pagination, or
queries. Use :doc:`/reference/data-sources` for record-oriented data, and
``Store`` for "remember this setting".

Creating a store
----------------

Give the store a logical name. Its file lives under the per-platform config
directory (``Library/Application Support`` on macOS, ``%APPDATA%`` on Windows,
``$XDG_CONFIG_HOME`` on Linux), in a sub-directory named for your app:

.. code-block:: python

   from bootstack.store import Store

   import bootstack as bs

   store = Store("settings")     # <config>/<app>/settings.json

Pass ``path=`` for an explicit location, or ``app_name=`` to override the
sub-directory. A ``Store`` does not need a running ``App`` — it is plain file
I/O — so you can create one before constructing the app (handy for restoring the
startup theme).

Reading and writing
-------------------

Read with ``get()`` (with an optional default) and write with ``set()``. The
mapping syntax works too:

.. code-block:: python

   store.set("theme", "bootstrap-dark")
   store.get("theme", "bootstrap-light")   # default if absent

   store["sidebar_open"] = True
   store["sidebar_open"]                    # KeyError if absent
   "theme" in store
   del store["theme"]                       # KeyError if absent
   store.delete("theme")                    # no-op if absent

By default every change is written immediately, with an atomic write (a
temporary file renamed over the target) so a crash mid-write cannot corrupt the
file. Values must be JSON-serializable — scalars, lists, and dicts; anything
else raises ``SerializationError``. Keys must be strings.

.. code-block:: python

   store.set("recent_files", ["a.txt", "b.txt"])   # lists/dicts are fine
   store.set("handle", open("x"))                   # SerializationError

Bulk and dict-like operations
-----------------------------

``Store`` supports the familiar mapping methods; ``update()`` writes once at the
end rather than per key, and accepts a mapping, keyword arguments, or both:

.. code-block:: python

   store.update({"theme": "dark", "font_scale": 1.2})
   store.update(theme="dark", locale="de_DE")     # keyword form
   store.setdefault("locale", "en_US")
   store.keys(); store.values(); store.items()
   len(store); list(store)
   store.as_dict()        # a plain-dict copy
   store.clear()

Deferring writes
----------------

Pass ``autosave=False`` to batch changes in memory and flush them yourself with
``save()`` — useful when applying many settings at once:

.. code-block:: python

   store = Store("settings", autosave=False)
   store.update(collected_settings)
   store.save()

Call ``reload()`` to discard in-memory state and re-read the file (for example
if another process may have written it).

Remembering the theme
---------------------

A common use is restoring the user's theme across launches — read it before
creating the app, and write it whenever it changes:

.. code-block:: python

   store = Store("settings")

   with bs.App(theme=store.get("theme", "bootstrap-light")) as app:
       app.on_theme_change(lambda theme: store.update(theme=theme))
       bs.Button("Toggle theme", on_click=bs.toggle_theme)
   app.run()

Persisting app configuration
----------------------------

Because app configuration is flat ``App(...)`` kwargs and a ``Store`` is a flat
dict, the whole persistence story is symmetric: splat the store in to restore,
and write each value back when it changes. ``App.from_store()`` does the restore
and *tolerantly ignores keys that are not valid configuration*, so a settings
file written by an older or newer version (with renamed or removed keys) still
loads cleanly instead of raising:

.. code-block:: python

   store = Store("settings")          # app config, in its own store

   app = bs.App.from_store(store)        # restore; empty store → defaults
   app.on_theme_change(lambda theme: store.update(theme=theme))
   app.on_locale_change(lambda locale: store.update(locale=locale))
   app.run()

A few practices keep this clean:

- **Keep app *config* separate from app *state*.** Put restorable configuration
  (theme, locale) in one store and transient state (recent files, last-opened
  tab) in another, so ``App.from_store`` only ever sees real config keys.
- **Window geometry is the one exception.** It is a fiddly ``"WxH+X+Y"`` string
  updated continuously as the window moves, not a clean kwarg — let the built-in
  ``remember_window_state=True`` flag handle it rather than the store.
- **Per-value write-back, not a config dump.** React to the specific change
  events (``on_theme_change``/``on_locale_change``) and write just that key.

See also
--------

- :doc:`/reference/data-sources` — record-oriented data with querying and paging.
- :doc:`/reference/theming` — themes and the values worth persisting with a store.
- :doc:`/reference/errors` — ``SerializationError`` and the other public errors.

API reference
-------------

The complete reference for :class:`Store <bootstack.store.Store>` — every mapping
method — lives in :doc:`/api-reference/store`. At a glance:

.. currentmodule:: bootstack.store

.. autosummary::
   :nosignatures:

   Store
