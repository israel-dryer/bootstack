Preferences store
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

   import bootstack as bs

   store = bs.Store("settings")     # <config>/<app>/settings.json

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
end rather than per key:

.. code-block:: python

   store.update({"theme": "dark", "font_scale": 1.2})
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

   store = bs.Store("settings", autosave=False)
   store.update(collected_settings)
   store.save()

Call ``reload()`` to discard in-memory state and re-read the file (for example
if another process may have written it).

Remembering the theme
---------------------

A common use is restoring the user's theme across launches — read it before
creating the app, and write it whenever it changes:

.. code-block:: python

   store = bs.Store("settings")

   with bs.App(theme=store.get("theme", "bootstrap-light")) as app:
       def on_toggle():
           bs.toggle_theme()
           store.set("theme", bs.get_theme())
       bs.Button("Toggle theme", on_click=on_toggle)
   app.run()

See also
--------

- :doc:`/reference/data-sources` — record-oriented data with querying and paging.
- :doc:`/reference/theming` — themes and the values worth persisting with a store.
- :doc:`/reference/errors` — ``SerializationError`` and the other public errors.

API reference
-------------

.. autoclass:: bootstack.store.Store
   :members:
   :exclude-members: __init__
