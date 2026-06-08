Scheduling
==========

Every widget has a ``schedule`` — a small scheduler for running work later or
repeatedly, tied to the widget's lifetime. When the widget is destroyed its
pending and repeating jobs are cancelled automatically, so a callback never fires
on a dead widget and you rarely have to clean up by hand. The ``App`` has one
too, which is the natural place for app-wide timers.

Running work later
------------------

``delay()`` runs a function once after a number of milliseconds; ``idle()`` runs
it as soon as the event loop is free; ``at()`` runs it at a specific
``datetime``. Each returns a :class:`Job <bootstack.scheduling.Job>` you can
cancel, and each forwards any extra arguments to your callback:

.. code-block:: python

   job = widget.schedule.delay(500, lambda: print("half a second later"))
   widget.schedule.idle(refresh)                 # when the loop next goes idle
   widget.schedule.at(deadline, on_due)          # at a datetime
   widget.schedule.delay(1000, save, document)   # extra args forwarded to save()

   job.cancel()                                  # call off a pending job

Use ``idle()`` to defer work until the UI has finished laying out — measuring a
widget, scrolling to a position, or moving focus all work better once the current
batch of events has drained:

.. code-block:: python

   with bs.App() as app:
       field = bs.TextField()
       field.schedule.idle(field.focus)   # focus after the window is shown
   app.run()

``at()`` takes an absolute time; a time already in the past simply runs as soon
as possible:

.. code-block:: python

   from datetime import datetime, timedelta

   reminder = datetime.now() + timedelta(minutes=5)
   widget.schedule.at(reminder, lambda: bs.alert("Five minutes are up."))

Repeating work
--------------

``every()`` runs a function on a fixed millisecond interval until cancelled. It
compensates for the callback's own run time to keep the interval from drifting:

.. code-block:: python

   from datetime import datetime

   clock = bs.Label("")

   def tick():
       clock.text = datetime.now().strftime("%H:%M:%S")

   ticker = clock.schedule.every(1000, tick)     # once a second
   ...
   ticker.cancel()                               # stop the repetition

If a repeating callback raises, the interval stops and the exception is re-raised
into the application's error handler — a broken tick won't silently keep firing.

A countdown combines the two: repeat on an interval, then cancel the job from
inside the callback when you're done.

.. code-block:: python

   remaining = bs.Signal(10)

   def countdown():
       remaining.set(remaining() - 1)
       if remaining() <= 0:
           job.cancel()
           bs.alert("Liftoff!")

   job = app.schedule.every(1000, countdown)

Cancelling jobs
---------------

A :class:`Job <bootstack.scheduling.Job>` is truthy while it is still pending and
falsy once it has fired or been cancelled, so you can guard a re-schedule:

.. code-block:: python

   if not job:
       job = widget.schedule.delay(500, run)

``cancel_all()`` clears every job on a widget's schedule at once:

.. code-block:: python

   widget.schedule.cancel_all()

Because the schedule is bound to the widget, destroying the widget (or its
window) cancels everything for you — manual cleanup is the exception, not the
rule.

See also
--------

- :doc:`/reference/streams` — ``debounce`` / ``throttle`` / ``delay`` operators
  time a *stream of events* rather than scheduling one-off work. Reach for a
  stream when you're reshaping events; for a plain timer, use ``schedule``.

API reference
-------------

.. autoclass:: bootstack.scheduling.Schedule
   :members:

.. autoclass:: bootstack.scheduling.Job
   :members:
