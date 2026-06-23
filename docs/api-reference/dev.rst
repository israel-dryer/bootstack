Developer Tools
===============

.. currentmodule:: bootstack.dev

.. warning::

   **Provisional.** ``bootstack.dev`` ships in 0.1.0 but is carved out of the
   API freeze — it may change in a minor release while the dev workflow settles.

Dev-time hot reload. Run an app with ``bootstack dev <file>`` and edits show up
in the running window on save; mark a page builder with ``reloadable`` so only
its region rebuilds.

For the workflow — the stable/reload boundary, multi-file apps, the error
banner, and the restart fallback — see the :doc:`/production/hot-reload` guide.

.. autosummary::
   :toctree: generated
   :nosignatures:

   reloadable
   is_dev_mode
