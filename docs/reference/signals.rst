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

   name = bs.Signal("World")     # text signal — fine at module level
   count = bs.Signal(0)          # integer signal
   enabled = bs.Signal(True)     # boolean signal

   with bs.App() as app:
       bs.TextField(textsignal=name)
   app.run()

.. note::

   Signals can be created at module level, before ``bs.App()`` exists. The
   backing Tk variable is created lazily on the first widget binding and is
   transparent to callers — ``signal()``, ``set()``, ``subscribe()``, and
   ``map()`` all work before any ``App`` is running.

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

   name = bs.Signal("World")   # defined at module level

   with bs.App(gap=8) as app:
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
   for widgets that carry a typed value — boolean, numeric, date, and time
   (:class:`~bootstack.Checkbox`, :class:`~bootstack.Slider`,
   :class:`~bootstack.NumberField`, :class:`~bootstack.DateField`,
   :class:`~bootstack.TimeField`). A value-bound signal carries the typed value
   itself: a :class:`~bootstack.DateField` ``signal=`` reads back a ``date``, not
   a string.

Typed value signals
-------------------

A signal is not limited to text. ``signal=`` binds the widget's *typed* value, so
a date, time, or number round-trips as itself — never as a string. Bind a
``Signal`` holding a ``date`` to a :class:`~bootstack.DateField`, and reading the
signal back gives you a ``date``:

.. code-block:: python

   from datetime import date, timedelta

   due = bs.Signal(date(2026, 1, 15))   # defined at module level

   with bs.App(gap=8) as app:
       bs.DateField(signal=due)
       bs.Button("Next day", on_click=lambda: due.set(due() + timedelta(days=1)))
   app.run()

   due()              # datetime.date(2026, 1, 15) — a date, not "2026-01-15"

To show a typed value *as text* — a caption or summary label — derive a text
signal with ``map()`` and bind it with ``textsignal=``:

.. code-block:: python

   due = bs.Signal(date(2026, 1, 15))
   due_text = due.map(lambda d: d.strftime("%b %d, %Y") if d else "")

   bs.Label(textsignal=due_text)      # "Jan 15, 2026", re-derived on every change

The ``if d else ""`` is worth keeping even when the value cannot be empty today.
A transform runs on whatever the source holds, so a source that later becomes
:ref:`nullable <signals-empty>` hands it ``None``, and the derived signal's type
is fixed by the first result it produces. Returning a value of the same type for
the empty case keeps the derived signal bindable throughout.

.. _signals-empty:

Empty values
------------

A signal holds one type, decided by the value it is created with — so by default
it has no way to say "nothing". A field bound to such a signal keeps its last
value when it is cleared, rather than reporting the clear.

Pass ``nullable=True`` when the value can also be empty:

.. code-block:: python

   due = bs.Signal(date(2026, 1, 15), nullable=True)

   bs.DateField(signal=due)

   due.set(None)       # allowed — subscribers receive None
   due()               # None

A nullable signal may also start empty, in which case the first real value
decides its type. Its ``type`` is ``None`` until then:

.. code-block:: python

   due = bs.Signal(None, nullable=True)
   due.type            # None

   due.set(date(2026, 1, 15))
   due.type            # <class 'datetime.date'>
   due.set(7)          # TypeError — the type is fixed from the first value on

Clearing a bound field now reaches the signal, in both directions:

.. code-block:: python

   field = bs.DateField(signal=due)

   field.value = None  # due() is None, and subscribers are notified
   due.set(None)       # the field is emptied

.. note::

   ``nullable=True`` is for fields that carry a *typed value* — ``NumberField``,
   ``DateField``, ``TimeField``, ``Select`` and ``SelectButton``. A text field is
   already empty at ``""`` and a checkbox at ``False``, so they do not need it,
   and binding a nullable signal to one raises: those widgets store the value
   themselves and have no way to hold an empty one.

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
