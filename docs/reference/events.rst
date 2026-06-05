Events
======

Widgets announce what they do as named events — a button reports a ``click``,
a field reports a ``change`` when its value is committed. You respond by binding
a handler. Each widget exposes ``on_*()`` shorthands for the events it supports,
and every handler can be detached again through the subscription it returns.

Listening for an event
----------------------

Call the matching ``on_*()`` shorthand with a handler. It binds immediately and
returns a :class:`Subscription <bootstack.events.Subscription>`:

.. code-block:: python

   field = bs.TextField()

   field.on_change(lambda e: print("committed:", e.data["value"]))
   field.on_input(lambda e: print("typed:", e.data["text"]))

A button's click handler is called with **no arguments** — a click carries no
payload worth passing:

.. code-block:: python

   bs.Button("Save", on_click=lambda: save())

Every shorthand is a thin wrapper over the generic ``on()`` method, which takes
the event name as a string. Use it for events without a dedicated shorthand:

.. code-block:: python

   widget.on("right_click", show_context_menu)

The event object
----------------

Handlers that receive an argument are passed an :class:`Event
<bootstack.events.Event>`. Its most useful attribute is ``data`` — the
payload attached when the event fired. For input widgets the payload is a small
dictionary; a ``change`` event, for example, carries the committed ``value``,
the ``prev_value``, and the raw ``text``:

.. code-block:: python

   def on_change(e):
       print(e.data["value"], "was", e.data["prev_value"])

   field.on_change(on_change)

The same object also exposes the originating ``widget`` and, for pointer and
keyboard events, the cursor position (``x``, ``y``) and key (``keysym``).

Cancelling a subscription
-------------------------

The :class:`Subscription <bootstack.events.Subscription>` returned by a handler
binding detaches it when you
call ``cancel()``. This matters for handlers that outlive the thing they watch:

.. code-block:: python

   sub = item.on_click(handle_select)
   sub.cancel()          # stop listening

A subscription is also a context manager — the binding lasts only for the block:

.. code-block:: python

   with widget.on("hover", preview):
       ...               # preview is active here
   # unbound on exit

Emitting your own events
------------------------

Use ``emit()`` to fire an event yourself, optionally with a ``data`` payload.
This is how composite widgets surface high-level activity to their listeners:

.. code-block:: python

   widget.emit("change", data={"value": new_value})

See also
--------

- :doc:`/reference/streams` — chain operators (``debounce``, ``filter``, …)
  onto an event before handling it.
- :doc:`/reference/signals` — bind state to a widget without writing change
  handlers at all.

API reference
-------------

.. autoclass:: bootstack.events.Event
   :members:
   :undoc-members:
   :exclude-members: type, state, keysym_num, num, serial, time, send_event

.. autoclass:: bootstack.events.Subscription
   :members:
   :undoc-members:
   :exclude-members: __init__

Full Example
------------

.. literalinclude:: ../examples/events.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs