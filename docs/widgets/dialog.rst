Dialog
======

``Dialog`` creates a fully custom modal window. Provide a
``content_builder=`` function to lay out any widgets, and a ``buttons=`` list
to define the footer.

.. image:: /_static/examples/dialog-hero-light.png
   :class: bs-screenshot-light bs-dialog-screenshot
   :alt: Dialog — light theme

.. image:: /_static/examples/dialog-hero-dark.png
   :class: bs-screenshot-dark bs-dialog-screenshot
   :alt: Dialog — dark theme

Usage
-----

Content builder
~~~~~~~~~~~~~~~

The dialog's content area is set as the active parent, so ``content_builder``
fills it like an :class:`App <bootstack.App>` body — no ``parent=`` needed.
``padding=`` and ``gap=`` configure the content area:

.. code-block:: python

   from bootstack.dialogs import Dialog

   def build():
       bs.Label("New version available", font="heading-sm")
       bs.Label("bootstack 2.1.0 is ready to install.")

   dlg = Dialog(title="Update", content_builder=build, padding=24, gap=12)
   dlg.show()

Declare a single parameter (``def build(content):``) if you want an explicit
handle to the content container — for example to nest a :class:`Row
<bootstack.Row>` or pass it as a ``parent=``.

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

   dlg = Dialog(
       title="Save changes?",
       content_builder=build,
       buttons=[
           DialogButton("Save",    role="primary", result="save",    default=True),
           DialogButton("Discard", role="danger",  result="discard"),
           DialogButton("Cancel",  role="cancel"),
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

The complete reference for :class:`Dialog <bootstack.dialogs.Dialog>` and
:class:`DialogButton <bootstack.dialogs.DialogButton>` lives on the
:doc:`Dialogs </api-reference/dialogs>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.dialogs.Dialog
   ~bootstack.dialogs.DialogButton

Full Example
------------

.. literalinclude:: ../../docs/examples/dialog.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs