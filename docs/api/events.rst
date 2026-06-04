Events & Streams
================

The event system underpins all widget callbacks. ``on_*()`` shorthands return
a ``Subscription`` when called with a handler, or a ``Stream`` when called
without one.

Event
-----

.. autoclass:: bootstack.widgets._core.events.Event
   :members:
   :undoc-members:

Subscription
------------

.. autoclass:: bootstack.widgets._core.subscription.Subscription
   :members:
   :undoc-members:

Stream
------

.. autoclass:: bootstack.widgets._core.stream.Stream
   :members:
   :undoc-members:

.. autoclass:: bootstack.widgets._core.stream.Handle
   :members:
   :undoc-members: