Scheduling
==========

.. currentmodule:: bootstack.scheduling

Timed callbacks tied to a widget's lifetime. ``Schedule`` runs work after a
delay, on idle, or on a repeating interval; each call returns a ``Job`` handle
you can cancel.

For a task-oriented introduction — one-shot, idle, and repeating patterns, and
``App.schedule`` — see the :doc:`/reference/scheduling` guide.

.. autosummary::
   :toctree: generated
   :nosignatures:

   Schedule
   Job
