bootstack.signals
=================

Reactive values. A signal holds a value, binds two-way to widgets, and notifies
subscribers when it changes — the link between application state and the
interface.

``Signal`` is part of the top-level compose surface, so its complete reference
lives on the :doc:`bootstack <bootstack>` page:

.. autosummary::
   :nosignatures:

   ~bootstack.Signal

For a task-oriented introduction — creating signals, binding them to widgets,
deriving one from another — see the :doc:`/reference/signals` guide.
