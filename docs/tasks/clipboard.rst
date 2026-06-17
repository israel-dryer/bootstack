Using the Clipboard
===================

Read and write the system clipboard with two functions from
:mod:`bootstack.clipboard`. The clipboard is global to the application, so these
are plain functions rather than widget methods — call them from within a running
app:

.. code-block:: python

   import bootstack as bs
   from bootstack.clipboard import set_clipboard, get_clipboard

   with bs.App(title="Clipboard") as app:
       bs.Button("Copy", on_click=lambda: set_clipboard("sk-live-7f3a9c2b"))
       bs.Button("Paste", on_click=lambda: print(get_clipboard()))
   app.run()

Copy a field's value
--------------------

A common pattern is a read-only field with a copy button beside it — for an API
key, a token, or a generated value. The :doc:`/tasks/composing-fields` how-to
builds exactly this with an addon button:

.. code-block:: python

   from bootstack.clipboard import set_clipboard

   key = bs.TextField(value="sk-live-7f3a9c2b", label="API key",
                      read_only=True, horizontal="stretch")
   key.insert_addon("button", "after", name="copy", icon="clipboard",
                    on_click=lambda: set_clipboard(key.value),
                    active_when_readonly=True)

Reading the clipboard
---------------------

:func:`~bootstack.clipboard.get_clipboard` returns the current text, or an empty
string when the clipboard is empty, holds non-text data, or no app is running:

.. code-block:: python

   text = get_clipboard()
   if text:
       use(text)

Platform note
-------------

On Linux/X11 the clipboard is owned by the running process, so its contents are
cleared when the app exits unless a system clipboard manager is running. On
Windows and macOS the operating system owns the clipboard, so contents persist
after the app closes.

API reference
-------------

See :doc:`/api-reference/clipboard`.

.. currentmodule:: bootstack.clipboard

.. autosummary::
   :nosignatures:

   get_clipboard
   set_clipboard