Window
======

A secondary top-level window, opened from a running app — a settings window, a
tool palette, a custom prompt. Like :class:`~bootstack.App`, it behaves as an
implicit vertical stack: widgets created inside its ``with`` block are placed
top-to-bottom in its content area.

.. image:: /_static/examples/window-hero-light.png
   :class: bs-screenshot-light bs-window-screenshot
   :alt: A secondary bootstack window — light theme

.. image:: /_static/examples/window-hero-dark.png
   :class: bs-screenshot-dark bs-window-screenshot
   :alt: A secondary bootstack window — dark theme

Usage
-----

Opening a window
~~~~~~~~~~~~~~~~

Build a ``Window`` like an ``App``, then call ``show()`` to display it. Unlike
``App``, there is no ``run()`` — the window rides the app's existing event loop.

.. code-block:: python

   def open_preferences():
       win = bs.Window(title="Preferences", size=(420, 300), padding=24, gap=14)
       with win:
           bs.Label("Preferences", font="heading-md")
           bs.Switch("Enable notifications", value=True)
           bs.Button("Close", on_click=win.close)
       win.show()

Modal windows and results
~~~~~~~~~~~~~~~~~~~~~~~~~~

Pass ``modal=True`` to grab input until the window closes, and
``block_until_closed()`` to wait for it and read back a result. Set
``win.result`` before closing to choose what it returns.

.. code-block:: python

   win = bs.Window(title="Rename", modal=True)
   with win:
       field = bs.TextField(label="New name", value=current)
       def commit():
           win.result = field.value
           win.close()
       bs.Button("Rename", accent="primary", on_click=commit)

   new_name = win.block_until_closed()    # blocks; returns win.result
   if new_name:
       rename(new_name)

For the common prompts — text, numbers, dates, confirmation — reach for the
ready-made :doc:`dialogs </widgets/input-dialogs>` instead of building a
``Window`` by hand.

Live title
~~~~~~~~~~

``title`` is a live property — assign to it to update the title bar at runtime
(for example to reflect the document being edited).

.. code-block:: python

   win.title = f"Editing — {filename}"

Window controls and lifecycle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``Window`` shares the show-state controls (``hide``/``show``, ``minimize``,
``maximize``, ``set_fullscreen``, ``set_topmost``) and the close hooks
(``on_close`` to veto the close button, ``on_destroy`` for cleanup) with
:doc:`App </widgets/app>` — see that page for the full set. ``close()`` closes
the window immediately, bypassing the ``on_close`` veto.

.. code-block:: python

   win.on_close(lambda: bs.confirm("Close without saving?"))

See also
--------

:class:`~bootstack.App` — the main application window and the full window-control
reference.

:doc:`Dialogs </widgets/message-dialogs>` — ready-made modal prompts (alert,
confirm, ask) for the common cases.

API
---

The complete reference for :class:`Window <bootstack.Window>` lives on the
:doc:`Application </api-reference/application>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Window

Full Example
------------

.. literalinclude:: ../../docs/examples/window.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
