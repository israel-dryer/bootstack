bootstack.streams
=================

.. currentmodule:: bootstack.streams

Event pipelines. A stream transforms, filters, and times events before they
reach a handler, so the handler sees only what it cares about — the basis for
"search once the user stops typing" or "ignore clicks faster than twice a
second" without hand-rolled timers.

For a task-oriented introduction — building a pipeline, the timing operators,
activating and cancelling — see the :doc:`/reference/streams` guide.

.. autosummary::
   :toctree: generated
   :nosignatures:

   Stream
   Handle