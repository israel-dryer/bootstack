Dialogs
=======

One-shot dialog verbs for prompting the user, plus the reusable dialog classes
behind them. The verbs — ``alert``, ``confirm``, ``toast``, and the ``ask_*``
family — are on the top-level compose surface and cover the common cases in a
single call. The classes live in ``bootstack.dialogs`` for when a verb isn't
enough (a custom layout, a reusable instance, or direct control over the result).

For task-oriented introductions see the :doc:`/tasks/dialogs` guide and the
dialog pages in the :doc:`/widgets/index` catalog.

Verbs
-----

Show a dialog and get the result in one call. Each centers on the active window,
blocks until dismissed, and returns the user's choice (or ``None`` on cancel).

.. autosummary::
   :toctree: generated
   :nosignatures:

   bootstack.alert
   bootstack.ask_color
   bootstack.ask_date
   bootstack.ask_date_range
   bootstack.ask_filter
   bootstack.ask_float
   bootstack.ask_font
   bootstack.ask_integer
   bootstack.ask_item
   bootstack.ask_string
   bootstack.confirm
   bootstack.toast

Dialog classes
--------------

Construct a dialog directly for custom content, reuse, or explicit lifecycle
control. ``ColorChoice`` and ``FontChoice`` are the result values returned by the
color and font dialogs.

.. autosummary::
   :toctree: generated
   :nosignatures:

   bootstack.dialogs.ColorChooserDialog
   bootstack.dialogs.ColorChoice
   bootstack.dialogs.Dialog
   bootstack.dialogs.DialogButton
   bootstack.dialogs.FilterDialog
   bootstack.dialogs.FontChoice
   bootstack.dialogs.FontDialog
   bootstack.dialogs.FormDialog

Type aliases
------------

.. currentmodule:: bootstack.dialogs

.. py:type:: SeverityToken

   Severity level for an alert or toast — `'info'`, `'warning'`, `'danger'`,
   `'success'`.
