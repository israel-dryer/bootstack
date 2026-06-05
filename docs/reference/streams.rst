Streams
=======

A stream is an event pipeline. Where :doc:`/reference/events` binds a handler
directly, a stream lets you transform, filter, and time events *before* they
reach the handler — so the handler only sees what it cares about. Streams are
how you express "search once the user stops typing" or "ignore clicks fired
faster than twice a second" without hand-rolling timers and state.

Building a stream
-----------------

Call any ``on_*()`` shorthand (or the generic ``on()``) with **no handler**.
Instead of binding, it returns a :class:`Stream <bootstack.streams.Stream>`:

.. code-block:: python

   field = bs.TextField()

   stream = field.on_input()      # a Stream — nothing is bound yet

Nothing happens until you attach a handler with ``listen()`` (see below). Until
then the stream is just a recipe.

Transforming values
-------------------

Each operator returns a *new* stream, so they chain. ``map`` rewrites each
value, ``filter`` drops the ones you don't want, and ``tap`` runs a side effect
without changing the value:

.. code-block:: python

   (
       field.on_input()
       .map(lambda e: e.text)     # event -> text
       .filter(lambda text: len(text) >= 3)
       .tap(lambda text: log(text))       # peek, value passes through unchanged
       .listen(search)
   )

Operators never mutate the source stream — building a second chain from the
same ``field.on_input()`` gives an independent pipeline.

Timing
------

The time operators reshape *when* values arrive. They are the reason to reach
for a stream in the first place:

.. list-table::
   :header-rows: 1
   :widths: 18 82

   * - Operator
     - Behavior
   * - ``debounce(ms)``
     - Emit only after ``ms`` of silence — resets on each new value. The
       classic search-as-you-type operator.
   * - ``throttle(ms)``
     - Emit at most once per ``ms`` (leading edge). Caps the rate of a busy
       event such as resize or scroll.
   * - ``delay(ms)``
     - Re-emit each value after a fixed ``ms`` delay.

.. code-block:: python

   field.on_input().map(lambda e: e.text).debounce(300).listen(search)

Activating and cancelling
-------------------------

``listen()`` is the only terminal operator. It attaches the handler, installs
the underlying binding, and returns a cancellable :class:`Handle
<bootstack.streams.Handle>`. Calling
``cancel()`` tears down the whole chain — the binding and any pending timers:

.. code-block:: python

   handle = field.on_input().debounce(300).listen(search)
   handle.cancel()        # detach handler, cancel pending debounce timer

Like a subscription, a handle is also a context manager and exposes
``cancelled``. A :class:`Handle <bootstack.streams.Handle>` and a
:class:`Subscription <bootstack.events.Subscription>` are interchangeable
wherever a cancellable result is expected.

See also
--------

- :doc:`/reference/events` — bind a handler directly when you don't need to
  reshape the event first.
- :doc:`/reference/signals` — for keeping state and widgets in sync, a signal is
  usually simpler than a stream.

API reference
-------------

.. autoclass:: bootstack.streams.Stream
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: bootstack.streams.Handle
   :members:
   :undoc-members:
   :exclude-members: __init__
