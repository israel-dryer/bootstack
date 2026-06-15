Showing Dialogs
===============

A dialog interrupts the app to tell the user something or to collect one quick
answer. bootstack ships ready-made dialog **verbs** for the common cases — each
is a single function that opens the dialog, waits, and returns the result — plus
a base :class:`~bootstack.dialogs.Dialog` for when you need to build your own.

Telling the user something
--------------------------

`bs.alert()` shows a message with one dismiss button. Add a `severity=` to color
it and pick a matching icon:

.. code-block:: python

   bs.alert("Your changes have been saved.", severity="success")
   bs.alert("The file could not be opened.", title="Error", severity="danger")

For a message that should *not* steal focus, reach for one of the transient
surfaces instead of a dialog. A :func:`bs.toast() <bootstack.toast>` slides into
a screen corner and dismisses itself — the passive "Saved" confirmation:

.. code-block:: python

   bs.toast("Document saved", accent="success")
   bs.toast("Upload failed — retrying", accent="warning", duration=5000)

When the message offers a single response — *"Message archived. [Undo]"* — that
is a :class:`bs.Snackbar <bootstack.Snackbar>`, not a dialog; when it should stay
until the user dismisses it, a :class:`bs.Notification <bootstack.Notification>`.
See :doc:`/widgets/toast` for all three.

Asking a yes/no question
------------------------

`bs.confirm()` returns a `bool`. Use it to gate a destructive action, and set
`severity="danger"` so the stakes read clearly:

.. code-block:: python

   if bs.confirm("Delete this project? This cannot be undone.", severity="danger"):
       delete_project()

Collecting one value
--------------------

The `ask_*` verbs each prompt for a single value and return it, or `None` if the
user cancels. Always handle the `None` case:

.. code-block:: python

   name = bs.ask_string("Project name:")
   if name is not None:
       create_project(name)

   age = bs.ask_integer("Age:", min_value=0, max_value=120)
   when = bs.ask_date("Start date:")
   pick = bs.ask_item("Choose a theme:", ["Light", "Dark", "System"])

Other verbs follow the same pattern for richer values:

- `bs.ask_float` for a decimal number, `bs.ask_color` for a color, `bs.ask_font`
  for a font.
- `bs.ask_open_file`, `bs.ask_open_files`, `bs.ask_save_file`, and
  `bs.ask_directory` open the native OS file choosers.

Collecting several values
-------------------------

When you need more than one field, reach for :class:`~bootstack.dialogs.FormDialog`
rather than chaining `ask_*` calls. It presents a small form and returns the whole
record as a dict — see :doc:`building-forms`:

.. code-block:: python

   from bootstack.dialogs import FormDialog

   dialog = FormDialog(
       title="New contact",
       items=[
           bs.FieldItem(key="name", label="Name"),
           bs.FieldItem(key="email", label="Email"),
       ],
   )
   dialog.show()
   if dialog.result:
       add_contact(dialog.result)

Building a custom dialog
------------------------

When none of the verbs fit, build a :class:`~bootstack.dialogs.Dialog` directly.
Provide a `content_builder` to fill the body, and a list of :class:`DialogButton
<bootstack.dialogs.DialogButton>` entries for the footer.

Each button carries a `role` (`"primary"`, `"secondary"`, `"danger"`, or
`"cancel"`) and an optional `result` that becomes `dialog.result` when clicked:

.. code-block:: python

   from bootstack.dialogs import Dialog, DialogButton

   def body(frame):
       with bs.VStack(padding=24, gap=8, parent=frame):
           bs.Label("Reset all settings to their defaults?")
           bs.Label("Your data is not affected.", accent="secondary", font="caption")

   dialog = Dialog(
       title="Reset settings",
       content_builder=body,
       buttons=[
           DialogButton("Cancel", role="cancel"),
           DialogButton("Reset", role="danger", result=True, default=True),
       ],
       min_size=(360, 160),
   )
   dialog.show()
   if dialog.result:
       reset_settings()

For a fully custom secondary window with persistent content — an inspector, a
preferences panel — use :class:`~bootstack.Window` instead of a dialog. See
:doc:`/getting-started/app-structures`.

See also
--------

- :doc:`building-forms` — `FormDialog` and multi-field collection.
- :doc:`/getting-started/app-structures` — dialogs versus secondary windows.
- :doc:`/widgets/dialog` — the custom-dialog reference; see also
  :doc:`/widgets/message-dialogs` and :doc:`/widgets/input-dialogs` for the verbs.
