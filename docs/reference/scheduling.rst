Scheduling
==========

Every widget has a ``schedule`` — a small scheduler for running work later or
repeatedly, tied to the widget's lifetime. When the widget is destroyed its
pending and repeating jobs are cancelled automatically, so callbacks never fire
on a dead widget.

Running work later
------------------

``delay()`` runs a function once after a number of milliseconds; ``idle()``
runs it as soon as the event loop is free; ``at()`` runs it at a specific
``datetime``. Each returns a :class:`Job <bootstack.scheduling.Job>` you can
cancel:

.. code-block:: python

   job = widget.schedule.delay(500, lambda: print("half a second later"))
   widget.schedule.idle(refresh)            # when the loop next goes idle
   widget.schedule.at(deadline, on_due)     # at a datetime

   job.cancel()                             # call off a pending job

Repeating work
--------------

``every()`` runs a function on a fixed millisecond interval until cancelled:

.. code-block:: python

   ticker = widget.schedule.every(1000, update_clock)   # once a second
   ...
   ticker.cancel()                          # stop the repetition

``cancel_all()`` cancels every job on that widget's schedule at once:

.. code-block:: python

   widget.schedule.cancel_all()

Because the schedule is bound to the widget, you rarely need to clean up
manually — destroying the widget (or its window) cancels everything for you.

See also
--------

- :doc:`/reference/streams` — ``debounce`` / ``throttle`` / ``delay`` operators
  time a stream of events rather than scheduling one-off work.

API reference
-------------

.. autoclass:: bootstack.scheduling.Schedule
   :members:

.. autoclass:: bootstack.scheduling.Job
   :members:
