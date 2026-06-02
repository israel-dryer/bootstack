Dialogs
=======

Blocking dialogs for alerts, confirmations, and user input. All convenience
functions open a modal window and return when the user responds.

.. code-block:: python

   bs.alert("File saved.", severity="success")

   if bs.confirm("Delete this item?", confirm_text="Delete", severity="danger"):
       delete_item()

   name = bs.ask_string("Enter your name:")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/dialogs-light.png"
        alt="Dialogs demo — light theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/dialogs-dark.png"
        alt="Dialogs demo — dark theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">

Usage
-----

Alert
~~~~~

``bs.alert()`` shows an informational message with an OK button.

.. code-block:: python

   bs.alert("File saved successfully.", title="Done")

Customize the button label or add an icon:

.. code-block:: python

   bs.alert("Your session has expired.", ok_text="Sign in again",
            icon="exclamation-circle")

Alert sound
^^^^^^^^^^^

``severity="warning"`` and ``severity="danger"`` ring the system bell by
default. All other severities are silent. Override with ``sound=``:

.. code-block:: python

   bs.alert("Low battery.", severity="warning")          # rings bell
   bs.alert("File saved.", severity="success")           # silent
   bs.alert("Background sync complete.", sound=False)    # force silent
   bs.alert("Critical failure!", sound=True)             # force bell

Confirm
~~~~~~~

``bs.confirm()`` shows a confirmation dialog. Returns ``True`` if the user
clicked the confirm button, ``False`` otherwise.

.. code-block:: python

   if bs.confirm("Overwrite existing file?"):
       save_file()

For destructive actions use ``confirm_role="danger"`` — the button turns red
and is not focused by default so :kbd:`Enter` does not trigger it accidentally.

.. code-block:: python

   if bs.confirm(
       "Delete 3 items permanently?",
       title="Confirm Delete",
       confirm_text="Delete",
       confirm_role="danger",
       icon="trash",
   ):
       delete_items()

Ask for text
~~~~~~~~~~~~

``bs.ask_string()`` shows a text-input dialog. Returns the entered string,
or ``None`` if canceled.

.. code-block:: python

   name = bs.ask_string("Enter your name:", title="Name")
   if name:
       greet(name)

Pass ``value=`` to pre-fill the field.

.. code-block:: python

   new_name = bs.ask_string("Rename:", value=current_name)

Ask for a number
~~~~~~~~~~~~~~~~

``bs.ask_integer()`` and ``bs.ask_float()`` show a numeric input with
optional range validation and a stepper. Both return ``None`` if canceled.

.. code-block:: python

   age = bs.ask_integer("Enter age:", min_value=0, max_value=120)

   price = bs.ask_float("Enter price:", min_value=0.0, step=0.5)

Ask for a date
~~~~~~~~~~~~~~

``bs.ask_date()`` opens a calendar picker. Returns a ``datetime.date``, or
``None`` if canceled.

.. code-block:: python

   from datetime import date

   picked = bs.ask_date(title="Select date", value=date.today())

Restrict the selectable range with ``min_date=`` and ``max_date=``:

.. code-block:: python

   deadline = bs.ask_date(title="Pick a deadline", min_date=date.today())

Ask for a date range
~~~~~~~~~~~~~~~~~~~~

``bs.ask_date_range()`` opens the same calendar in range-selection mode.
Returns a ``(start, end)`` tuple of ``date`` objects, or ``None`` if canceled.

.. code-block:: python

   result = bs.ask_date_range(title="Report period")
   if result:
       start, end = result

Ask from a list
~~~~~~~~~~~~~~~

``bs.ask_item()`` shows a dropdown populated with ``options``. Returns the
selected string, or ``None`` if canceled.

.. code-block:: python

   country = bs.ask_item(
       "Select your country:",
       ["Canada", "UK", "USA", "Other"],
       title="Country",
   )

Custom dialogs
~~~~~~~~~~~~~~

Use ``bs.Dialog`` with a ``content_builder=`` function to create any dialog
layout. Pass ``buttons=`` as a list of ``bs.DialogButton`` specs.

.. code-block:: python

   def build_content(frame):
       with bs.VStack(padding=20, gap=8, parent=frame):
           bs.Label("Delete 3 selected items?")
           bs.Label("This action cannot be undone.", font="caption")

   dlg = bs.Dialog(
       title="Confirm deletion",
       content_builder=build_content,
       buttons=[
           bs.DialogButton("Delete", role="danger", result="delete", default=True),
           bs.DialogButton("Cancel", role="cancel"),
       ],
   )
   dlg.show()

   if dlg.result == "delete":
       delete_items()

``content_builder`` receives an empty ``Frame`` — place any bootstack widgets
inside it using ``parent=frame``.

Button roles
^^^^^^^^^^^^

``role=`` controls styling and keyboard shortcuts automatically.

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Role
     - Behavior
   * - ``'primary'``
     - Blue solid. Focused by default; triggered by :kbd:`Enter` when
       ``default=True``.
   * - ``'secondary'``
     - Gray solid. For neutral actions (OK, Dismiss, Done).
   * - ``'danger'``
     - Red solid. For destructive actions. Not focused by default.
   * - ``'cancel'``
     - Gray outline. Triggered by :kbd:`Escape`.

Dialog modes
^^^^^^^^^^^^

``mode=`` controls how the dialog interacts with the rest of the app.

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Mode
     - Behavior
   * - ``'modal'``
     - Blocks the parent window until closed. Default.
   * - ``'popover'``
     - Closes automatically when focus leaves the dialog.
   * - ``'sheet'``
     - Like ``'modal'`` on Windows/Linux; renders as a Cocoa sheet on macOS.

Positioning
^^^^^^^^^^^

By default, dialogs center on the parent window. Override with
``anchor_to=`` to position relative to a widget, the cursor, or the screen.

.. code-block:: python

   dlg.show(anchor_to=my_button, anchor_point="s", window_point="n")

   dlg.show(anchor_to="cursor")

   dlg.show(position=(400, 300))

Form dialogs
~~~~~~~~~~~~

``bs.FormDialog`` embeds a :class:`Form <bootstack.widgets.forms.Form>` in a
dialog. Pass ``data=`` to generate fields automatically from a dict, or
``items=`` for an explicit layout.

.. code-block:: python

   dlg = bs.FormDialog(
       title="New Contact",
       data={"name": "", "email": "", "phone": ""},
   )
   dlg.show()

   if dlg.result:
       save_contact(dlg.result)

The returned ``result`` is a dict with the same keys as ``data``, filled with
the user's input. It is ``None`` when the user cancels.

Use ``col_count=`` to lay fields out in multiple columns.

.. code-block:: python

   dlg = bs.FormDialog(
       title="Address",
       data={"street": "", "city": "", "state": "", "zip": ""},
       col_count=2,
   )
   dlg.show()

See also
--------

:class:`Form <bootstack.widgets.forms.Form>` —
standalone form widget for embedding form inputs inside an app window.

:class:`Calendar <bootstack.widgets.calendar.Calendar>` —
standalone calendar widget.

API
---

.. autofunction:: bootstack.widgets.dialogs.alert

.. autofunction:: bootstack.widgets.dialogs.confirm

.. autofunction:: bootstack.widgets.dialogs.ask_string

.. autofunction:: bootstack.widgets.dialogs.ask_integer

.. autofunction:: bootstack.widgets.dialogs.ask_float

.. autofunction:: bootstack.widgets.dialogs.ask_date

.. autofunction:: bootstack.widgets.dialogs.ask_date_range

.. autofunction:: bootstack.widgets.dialogs.ask_item

.. autoclass:: bootstack.dialogs.dialog.Dialog
   :members:
   :undoc-members:

.. autoclass:: bootstack.dialogs.dialog.DialogButton
   :members:

.. autoclass:: bootstack.widgets.dialogs.FormDialog
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/dialogs.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs