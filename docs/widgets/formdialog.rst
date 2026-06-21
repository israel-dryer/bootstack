Form Dialog
===========

``FormDialog`` embeds a :class:`Form <bootstack.widgets.forms.Form>` in a
dialog. Pass ``data=`` to generate fields automatically from a dict, or
``items=`` for an explicit layout.

.. image:: /_static/examples/formdialog-hero-light.png
   :class: bs-screenshot-light bs-dialog-screenshot
   :alt: FormDialog — light theme

.. image:: /_static/examples/formdialog-hero-dark.png
   :class: bs-screenshot-dark bs-dialog-screenshot
   :alt: FormDialog — dark theme

Usage
-----

A ``FormDialog`` is a :doc:`Form <forms>` wrapped in a modal :doc:`dialog <dialog>`
with submit and cancel wired up — pass ``data=`` to generate fields from a dict or
``items=`` for an explicit layout, and ``show()`` returns the entered values (or
``None`` on cancel).

Auto-generated fields
~~~~~~~~~~~~~~~~~~~~~

Pass a dict to ``data=``. Keys become field labels; values are the initial
field contents:

.. code-block:: python

   from bootstack.dialogs import FormDialog

   dlg = FormDialog(
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

   dlg = FormDialog(
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

   dlg = FormDialog(
       title="Live Preview",
       data={"title": "", "description": ""},
       on_data_change=on_change,
   )
   dlg.show()

Resizable dialog
~~~~~~~~~~~~~~~~

Pass ``resizable=True`` to allow the user to resize the dialog window:

.. code-block:: python

   dlg = FormDialog(
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

The complete reference for :class:`FormDialog <bootstack.dialogs.FormDialog>` lives
on the :doc:`Dialogs </api-reference/dialogs>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.dialogs.FormDialog

Full Example
------------

.. literalinclude:: ../../docs/examples/formdialog.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs