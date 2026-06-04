Dialog
======

``bs.Dialog`` creates a fully custom modal window. Provide a
``content_builder=`` function to lay out any widgets, and a ``buttons=`` list
to define the footer.

.. raw:: html

   <img class="bs-screenshot-light bs-dialog-screenshot"
        src="/_static/examples/dialog-hero-light.png"
        alt="Dialog — light theme"
        style="max-width:100%; margin:1rem 0;">
   <img class="bs-screenshot-dark bs-dialog-screenshot"
        src="/_static/examples/dialog-hero-dark.png"
        alt="Dialog — dark theme"
        style="max-width:100%; margin:1rem 0;">

Usage
-----

Content builder
~~~~~~~~~~~~~~~

``content_builder`` receives an empty frame. Use it as a parent for any
bootstack layout or widget:

.. code-block:: python

   def build(frame):
       with bs.VStack(padding=24, gap=12, parent=frame):
           bs.Label("New version available", font="heading-sm")
           bs.Label("bootstack 2.1.0 is ready to install.")

   dlg = bs.Dialog(title="Update", content_builder=build)
   dlg.show()

Button roles
~~~~~~~~~~~~

``role=`` controls button styling and keyboard shortcuts automatically.

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Role
     - Behavior
   * - ``'primary'``
     - Blue solid. Focused by default; triggered by :kbd:`Enter` when
       ``default=True``.
   * - ``'secondary'``
     - Gray solid. For neutral actions (OK, Dismiss).
   * - ``'danger'``
     - Red solid. For destructive actions. Not focused by default.
   * - ``'cancel'``
     - Gray outline. Triggered by :kbd:`Escape`.

Reading the result
~~~~~~~~~~~~~~~~~~

Each ``DialogButton`` carries a ``result=`` value that ``dialog.result`` is set
to when that button is clicked:

.. code-block:: python

   dlg = bs.Dialog(
       title="Save changes?",
       content_builder=build,
       buttons=[
           bs.DialogButton("Save",    role="primary", result="save",    default=True),
           bs.DialogButton("Discard", role="danger",  result="discard"),
           bs.DialogButton("Cancel",  role="cancel"),
       ],
   )
   dlg.show()

   if dlg.result == "save":
       save()
   elif dlg.result == "discard":
       discard()

Dialog modes
~~~~~~~~~~~~

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
~~~~~~~~~~~

By default, dialogs center on the parent window. Override with ``anchor_to=``
to position relative to a widget, the cursor, or the screen:

.. code-block:: python

   dlg.show(anchor_to=my_button, anchor_point="s", window_point="n")

   dlg.show(anchor_to="cursor")

   dlg.show(position=(400, 300))

See also
--------

:doc:`message-dialogs` — ``alert()`` and ``confirm()`` for common notifications.

:doc:`formdialog` — ``FormDialog`` for structured data-entry forms.

:doc:`filter-dialog` — ``FilterDialog`` for multi-select list dialogs.

API
---

.. autoclass:: bootstack.dialogs.dialog.Dialog
   :members:
   :undoc-members:

.. autoclass:: bootstack.dialogs.dialog.DialogButton
   :members:

Full Example
------------

.. literalinclude:: ../../docs/examples/dialog.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs