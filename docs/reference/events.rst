Events
======

Widgets announce what they do as named events — a button reports a ``click``,
a field reports a ``change`` when its value is committed. You respond by binding
a handler. Each widget exposes ``on_*()`` shorthands for the events it supports,
and every handler can be detached again through the subscription it returns.

What a handler receives
-----------------------

There are two kinds of event, and the handler argument differs accordingly:

- **Data-carrying events** (``change``, ``input``, ``select``, …) hand the
  handler a typed *payload* object directly — the argument **is** the payload.
  Read its attributes straight off: ``e.value``, ``e.text``, ``e.record``.
- **Native events** (``click``, ``hover``, ``focus``, ``blur``, ``resize``,
  key and scroll events) carry no payload, so the handler receives a curated
  :class:`Event <bootstack.events.Event>` describing where it happened and which
  modifier keys were held.

Every payload type is catalogued in this module, so editors can autocomplete the
attributes available on each event.

Listening for an event
----------------------

Call the matching ``on_*()`` shorthand with a handler. It binds immediately and
returns a :class:`Subscription <bootstack.events.Subscription>`:

.. code-block:: python

   field = bs.TextField()

   field.on_change(lambda e: print("committed:", e.value))
   field.on_input(lambda e: print("typed:", e.text))

For a simple button action, the ``on_click=`` constructor argument takes a
**no-argument** callback:

.. code-block:: python

   bs.Button("Save", on_click=lambda: save())

Every shorthand is a thin wrapper over the generic ``on()`` method, which takes
the event name as a string. Use it for events without a dedicated shorthand:

.. code-block:: python

   widget.on("right_click", show_context_menu)

Reading a payload
-----------------

For a data-carrying event the handler argument is the payload itself. A
``change`` event, for example, is a :class:`ChangeEvent
<bootstack.events.ChangeEvent>` carrying the committed ``value``, the
``prev_value``, and the raw ``text``:

.. code-block:: python

   def on_change(e):
       print(e.value, "was", e.prev_value)

   field.on_change(on_change)

The curated Event
-----------------

Native events hand the handler a frozen :class:`Event
<bootstack.events.Event>`. It exposes the originating ``widget``, the pointer
position (``x``, ``y``, ``x_root``, ``y_root``), the widget ``width`` and
``height``, scroll ``delta``, modifier-key booleans (``ctrl``, ``shift``,
``alt``, ``meta``), and — for keyboard events — a clean ``key`` and ``char``.
None of the underlying toolkit's bitmask or serial-number plumbing leaks
through.

.. code-block:: python

   button.on_click(lambda e: print("clicked at", e.x, e.y, "ctrl:", e.ctrl))

Cancelling a subscription
-------------------------

The :class:`Subscription <bootstack.events.Subscription>` returned by a handler
binding detaches it when you call ``cancel()``. This matters for handlers that
outlive the thing they watch:

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

Use ``emit()`` to fire an event yourself, optionally with a payload. This is how
composite widgets surface high-level activity to their listeners:

.. code-block:: python

   widget.emit("change", data=bs.events.ChangeEvent(value=new_value))

See also
--------

- :doc:`/reference/streams` — chain operators (``debounce``, ``filter``, …)
  onto an event before handling it.
- :doc:`/reference/signals` — bind state to a widget without writing change
  handlers at all.

API reference
-------------

Everything in the ``bootstack.events`` catalog: the curated :class:`Event` for
native events, the :class:`Subscription` handle returned by every binding, and
the typed payload classes handed to data-carrying handlers.

The curated event handed to native/context handlers:

.. autoclass:: bootstack.events.Event
   :members:

The cancellable handle returned by every binding:

.. autoclass:: bootstack.events.Subscription
   :members:
   :exclude-members: __init__

The typed payloads handed to data-carrying handlers. Import them from
``bootstack.events`` (e.g. ``from bootstack.events import ChangeEvent``).

**Fields and input**

.. autoclass:: bootstack.events.ChangeEvent
   :members:
.. autoclass:: bootstack.events.InputEvent
   :members:
.. autoclass:: bootstack.events.ValidationEvent
   :members:

**Sliders and meters**

.. autoclass:: bootstack.events.SliderEvent
   :members:
.. autoclass:: bootstack.events.SliderCommitEvent
   :members:
.. autoclass:: bootstack.events.RangeSliderEvent
   :members:
.. autoclass:: bootstack.events.RangeSliderCommitEvent
   :members:

**Calendar**

.. autoclass:: bootstack.events.DateSelectEvent
   :members:

**Expander and accordion**

.. autoclass:: bootstack.events.ToggleEvent
   :members:
.. autoclass:: bootstack.events.AccordionChangeEvent
   :members:

**Navigation**

.. autoclass:: bootstack.events.PageChangeEvent
   :members:
.. autoclass:: bootstack.events.NavEvent
   :members:
.. autoclass:: bootstack.events.PaneToggleEvent
   :members:
.. autoclass:: bootstack.events.DisplayModeEvent
   :members:

**Tabs**

.. autoclass:: bootstack.events.TabRef
   :members:
.. autoclass:: bootstack.events.TabChangeEvent
   :members:
.. autoclass:: bootstack.events.TabActivateEvent
   :members:
.. autoclass:: bootstack.events.TabDeactivateEvent
   :members:
.. autoclass:: bootstack.events.TabCloseEvent
   :members:

**Table**

.. autoclass:: bootstack.events.RowEvent
   :members:
.. autoclass:: bootstack.events.RowsEvent
   :members:
.. autoclass:: bootstack.events.SelectionEvent
   :members:

**Text area**

.. autoclass:: bootstack.events.TextModifiedEvent
   :members:

**Button group**

.. autoclass:: bootstack.events.ButtonGroupClickEvent
   :members:

Full Example
------------

.. literalinclude:: ../examples/events.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
