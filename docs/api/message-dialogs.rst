Message Dialogs
===============

``bs.alert()`` and ``bs.confirm()`` open modal windows for notifications and
yes/no decisions. Both are one-liners — no setup required.

.. image:: /_static/examples/message-dialogs-hero-light.png
   :class: bs-screenshot-light bs-dialog-screenshot
   :alt: Message Dialogs — confirm dialog, light theme

.. image:: /_static/examples/message-dialogs-hero-dark.png
   :class: bs-screenshot-dark bs-dialog-screenshot
   :alt: Message Dialogs — confirm dialog, dark theme

Usage
-----

Alert
~~~~~

``bs.alert()`` shows a message with an OK button. It returns ``None`` when the
user dismisses it.

.. code-block:: python

   bs.alert("File saved successfully.", title="Done")

Customize the button label or add an icon:

.. code-block:: python

   bs.alert("Session expired.", ok_text="Sign in again", icon="exclamation-circle")

.. image:: /_static/examples/message-dialogs-alert-light.png
   :class: bs-screenshot-light bs-dialog-screenshot
   :alt: Message Dialogs — alert dialog, light theme

.. image:: /_static/examples/message-dialogs-alert-dark.png
   :class: bs-screenshot-dark bs-dialog-screenshot
   :alt: Message Dialogs — alert dialog, dark theme

Alert sound
^^^^^^^^^^^

``severity="warning"`` and ``severity="danger"`` ring the system bell by
default. All other severities are silent. Override with ``sound=``:

.. code-block:: python

   bs.alert("Low battery.", severity="warning")        # rings bell
   bs.alert("File saved.", severity="success")         # silent
   bs.alert("Background sync done.", sound=False)      # force silent
   bs.alert("Critical failure!", sound=True)           # force bell

Confirm
~~~~~~~

``bs.confirm()`` shows a question with Confirm and Cancel buttons. Returns
``True`` when the user confirms, ``False`` when they cancel or close the dialog.

.. code-block:: python

   if bs.confirm("Overwrite existing file?"):
       save_file()

For destructive actions, use ``confirm_role="danger"`` — the button turns red
and is not focused by default, so :kbd:`Enter` does not accidentally trigger it:

.. code-block:: python

   if bs.confirm(
       "Delete 3 items permanently?",
       title="Confirm Delete",
       confirm_text="Delete",
       confirm_role="danger",
       icon="trash",
   ):
       delete_items()

The ``severity=`` parameter auto-derives the confirm button color:

.. code-block:: python

   # danger severity → red Confirm button
   bs.confirm("Remove all data?", severity="danger", confirm_text="Remove")

   # warning severity → warning-tinted Confirm button
   bs.confirm("This will close all tabs.", severity="warning")

See also
--------

:doc:`input-dialogs` — dialogs that collect text, numbers, dates, and list selections.

:doc:`dialog` — ``Dialog`` class for fully custom layouts and button sets.

API
---

.. autofunction:: bootstack.widgets.dialogs.alert

.. autofunction:: bootstack.widgets.dialogs.confirm

Full Example
------------

.. literalinclude:: ../../docs/examples/message-dialogs.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs