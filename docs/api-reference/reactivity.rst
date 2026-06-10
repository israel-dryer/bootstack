Reactivity
==========

Reactive values and the event streams they compose into. A
:class:`Signal <bootstack.Signal>` holds a value, binds two-way to widgets, and
notifies subscribers when it changes; a :class:`Stream <bootstack.streams.Stream>`
is a composable pipeline of events you can filter, debounce, and map before
listening. Together they are the link between application state and the interface.

Signals
-------

The reactive value that binds application state to widgets.

.. autosummary::
   :toctree: generated
   :nosignatures:
   :template: signal

   bootstack.Signal

Streams
-------

Composable event pipelines and the handle that cancels a subscription.

.. autosummary::
   :toctree: generated
   :nosignatures:

   bootstack.streams.Stream
   bootstack.streams.Handle
