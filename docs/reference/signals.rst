Signals
=======

A ``Signal`` is a reactive value. Bind one to a widget and the two stay in
sync automatically: when the user edits the widget the signal updates, and when
you call ``signal.set(...)`` the widget redraws. Signals are how you connect
application state to the interface without wiring up change callbacks by hand.

Creating a signal
------------------

Construct a ``Signal`` with its initial value. The value's type is fixed at
creation — passing a string makes a text signal, an ``int`` makes a numeric
one, a ``bool`` makes a boolean one:

.. code-block:: python

   import bootstack as bs

   with bs.App() as app:
       name = bs.Signal("World")     # text signal
       count = bs.Signal(0)          # integer signal
       enabled = bs.Signal(True)     # boolean signal
   app.run()

.. note::

   A signal must be created **inside** a running ``App``. Creating one at module
   level — before ``bs.App()`` exists — raises an error, because a signal is
   backed by the application's variable system.

Reading and writing
--------------------

Call the signal to read its current value. Use ``set()`` to update it:

.. code-block:: python

   name()              # "World"  — call to read
   name.set("Universe")

``set()`` enforces the signal's type. Assigning a value of a different type
raises ``TypeError`` — a ``Signal(0)`` accepts ``set(5)`` but rejects
``set(1.5)``. The one exception is numeric widening: a ``float`` signal also
accepts an ``int`` (``bs.Signal(0.0).set(5)`` stores ``5.0``). Setting the same
value the signal already holds is a no-op and does not notify subscribers.

Binding to widgets
------------------

Pass a signal to a widget to create a two-way binding. Text-bearing widgets use
``textsignal=``; boolean and numeric widgets use ``signal=``:

.. code-block:: python

   with bs.App(gap=8) as app:
       name = bs.Signal("World")

       bs.TextField(textsignal=name)
       bs.Label(textsignal=name)         # mirrors the field as you type

       bs.Button("Greet", on_click=lambda: print(f"Hello, {name()}!"))
   app.run()

Typing in the field updates ``name``; calling ``name.set(...)`` updates the
field. The same signal can drive several widgets at once, keeping them all
consistent.

.. seealso::

   ``textsignal=`` is for widgets that carry text
   (:class:`~bootstack.TextField`, :class:`~bootstack.TextArea`). ``signal=`` is
   for boolean and numeric widgets (:class:`~bootstack.Checkbox`,
   :class:`~bootstack.Slider`, :class:`~bootstack.Switch`).

Reacting to changes
-------------------

Subscribe a callback to run whenever the value changes. The callback receives
the new value, and ``subscribe`` returns a cancellable handle:

.. code-block:: python

   sub = count.subscribe(lambda value: print(f"count is now {value}"))

   count.set(1)        # prints "count is now 1"

   sub.cancel()        # stop listening

The handle is also a context manager, so a subscription can be scoped to a block
and cancelled automatically on exit:

.. code-block:: python

   with count.subscribe(on_change):
       ...             # listening here
   # cancelled on exit

Pass ``immediate=True`` to fire the callback once with the current value at
subscription time, in addition to future changes:

.. code-block:: python

   count.subscribe(update_total, immediate=True)

Derived signals
---------------

``map()`` returns a new, read-only signal whose value is computed from the
source. It recomputes automatically whenever the source changes:

.. code-block:: python

   name = bs.Signal("world")
   shout = name.map(str.upper)

   shout()             # "WORLD"
   name.set("hello")
   shout()             # "HELLO"

.. note::

   A derived signal is held *weakly* by its source. Keep a reference to it —
   assign it to a variable or bind it to a widget. If it is garbage-collected it
   silently stops updating.

See also
--------

- :doc:`/reference/events` — the ``subscribe`` / ``Stream`` model for widget events.
- :doc:`/widgets/textfield` — an input widget that accepts ``textsignal=`` / ``signal=``.

API reference
-------------

The complete reference — every method on :class:`Signal <bootstack.Signal>` —
lives on the :doc:`Reactivity </api-reference/reactivity>` API page (``Signal`` is
part of the top-level compose surface). At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Signal
