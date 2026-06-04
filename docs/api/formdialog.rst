Form Dialog
===========

``bs.FormDialog`` embeds a :class:`Form <bootstack.widgets.forms.Form>` in a
dialog. Pass ``data=`` to generate fields automatically from a dict, or
``items=`` for an explicit layout.

.. raw:: html

   <img class="bs-screenshot-light bs-dialog-screenshot"
        src="/_static/examples/formdialog-hero-light.png"
        alt="FormDialog — light theme"
        style="max-width:100%; margin:1rem 0;">
   <img class="bs-screenshot-dark bs-dialog-screenshot"
        src="/_static/examples/formdialog-hero-dark.png"
        alt="FormDialog — dark theme"
        style="max-width:100%; margin:1rem 0;">

Usage
-----

Auto-generated fields
~~~~~~~~~~~~~~~~~~~~~

Pass a dict to ``data=``. Keys become field labels; values are the initial
field contents:

.. code-block:: python

   dlg = bs.FormDialog(
       title="Edit Profile",
       data={"username": "alice", "bio": "", "website": ""},
   )
   dlg.show()

   if dlg.result:
       update_profile(dlg.result)

The returned ``result`` is a dict with the same keys as ``data``, filled with
the user's input. It is ``None`` when the user cancels.

Multiple columns
~~~~~~~~~~~~~~~~

Use ``col_count=`` to lay fields out in multiple columns:

.. code-block:: python

   dlg = bs.FormDialog(
       title="Shipping Address",
       data={"street": "", "city": "", "state": "", "zip": ""},
       col_count=2,
   )
   dlg.show()

Reactive updates
~~~~~~~~~~~~~~~~

Use ``on_data_change=`` to respond to every field change while the dialog is
open:

.. code-block:: python

   def on_change(data):
       print(f"Current values: {data}")

   dlg = bs.FormDialog(
       title="Live Preview",
       data={"title": "", "description": ""},
       on_data_change=on_change,
   )
   dlg.show()

Resizable dialog
~~~~~~~~~~~~~~~~

Pass ``resizable=True`` to allow the user to resize the dialog window:

.. code-block:: python

   dlg = bs.FormDialog(
       title="Notes",
       data={"content": ""},
       resizable=True,
       min_size=(400, 200),
   )
   dlg.show()

See also
--------

:doc:`dialog` — ``Dialog`` for fully custom layouts without a built-in form.

:ref:`forms` — standalone ``Form`` widget for embedding inside an app window.

API
---

.. autoclass:: bootstack.widgets.dialogs.FormDialog
   :members:

Full Example
------------

.. literalinclude:: ../../docs/examples/formdialog.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs