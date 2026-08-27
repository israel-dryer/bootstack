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
A transform runs on whatever the source holds, so a source that later
:ref:`allows an empty value <signals-empty>` hands it that empty, and the derived
signal's type is fixed by the first result it produces.

Return a value for the empty case, never ``None``. A derived signal is an
ordinary signal — nothing declared it able to be empty — so a transform that
returns ``None`` either raises or leaves the derived signal holding a value the
source no longer has. ``if d else ""`` is the whole fix.

.. _signals-empty:

Empty values
------------

A signal holds one type, decided by the value it is created with — so by default
it has no way to say "nothing". A field bound to such a signal keeps its last
value when it is cleared, rather than reporting the clear.

Pass ``allow_empty=True`` when the value can also be empty, and use ``clear()``
to empty it — the same verb the fields themselves use:

.. code-block:: python

   due = bs.Signal(date(2026, 1, 15), allow_empty=True)

   bs.DateField(signal=due)

   due.clear()         # allowed — subscribers are notified
   due()               # None

A signal that allows an empty value may also start empty. There is no value to
take a type from, so name it with ``dtype``:

.. code-block:: python

   due = bs.Signal(None, allow_empty=True, dtype=date)
   due.type            # <class 'datetime.date'>
   due()               # None

   due.set(date(2026, 1, 15))
   due.set(7)          # TypeError — a signal holds one type, empty or not

``dtype`` is honored whenever it is given, so a seed that may or may not be there
needs no second spelling — and a seed that contradicts it is reported where the
two disagree rather than at some later write:

.. code-block:: python

   due = bs.Signal(record.get("due"), allow_empty=True, dtype=date)

   bs.Signal(5, allow_empty=True, dtype=str)     # TypeError at construction

Clearing a bound field now reaches the signal, in both directions:

.. code-block:: python

   field = bs.DateField(signal=due)

   field.value = None  # due() is None, and subscribers are notified
   due.clear()         # the field is emptied

What "empty" means
~~~~~~~~~~~~~~~~~~

Empty is ``None`` — except where the signal *is* the widget's own variable, as it
is for a text field or a radio group. A variable holds only strings, so there
empty is ``""``:

.. code-block:: python

   name = bs.Signal("Ada", allow_empty=True)
   bs.TextField(textsignal=name)
   name.clear()
   name()              # "" — this signal is the field's variable

   pick = bs.Signal("1", allow_empty=True)
   bs.Select(options=[("One", "1"), ("Two", "2")], signal=pick)
   pick.clear()
   pick()              # None — a Select's signal carries the option's value

Both signals hold strings; what differs is where the value lives. Bind that same
``pick`` signal to a ``bs.Label`` as well and it empties to ``""`` too — it is
the label's variable now. Prefer a falsiness check — ``if not pick():`` — which
reads the same either way.

A signal holding a ``set``, as a multi-select ``bs.ToggleGroup`` does, is the one
exception: it empties to the empty set wherever it is bound, because an empty set
is a real value of the type rather than a stand-in for one. A falsiness check
covers that too.

.. note::

   Binding a signal that allows an empty value to a checkbox, switch, toggle
   button, slider or progress bar raises. Those widgets keep their value in the
   signal's own variable, and a boolean or numeric variable has no way to hold an
   empty one — ``False`` and ``0`` are real values, not absent ones. A tristate
   checkbox is the exception worth knowing about: it *does* have a third state,
   but it holds that state in the widget rather than in the variable, so a bound
   signal cannot report it. Read it from the checkbox's ``value``.

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
