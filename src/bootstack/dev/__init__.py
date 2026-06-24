"""Developer tooling for bootstack — hot reload.

.. warning::

   **Provisional.** This module ships in 0.1.0 but is *carved out of the API
   freeze*: unlike the ``bootstack`` compose surface, it may change in a minor
   release while the dev workflow settles. Pin a version if you depend on it.

Run an app with live reload::

    bootstack dev app.py

On save, a module-level ``with bs.App()`` app updates in place — the window,
your signals, and any module-level datasources survive; only the UI the body
built is rebuilt. State that should persist across reloads lives **above** the
``with`` block (module level); the block body is what reloads.

For multi-file apps, mark a page builder so only its region rebuilds when its
file changes::

    from bootstack.dev import reloadable

    @reloadable
    def build_dashboard(db):
        bs.Label("Dashboard", font="heading-lg")
        bs.DataTable(data_source=db)

Outside ``bootstack dev`` everything here is inert: :func:`reloadable` returns
the function unchanged and :func:`is_dev_mode` is False.
"""
from __future__ import annotations

from bootstack.dev._env import is_dev_mode
from bootstack.dev._registry import reloadable

__all__ = ["reloadable", "is_dev_mode"]