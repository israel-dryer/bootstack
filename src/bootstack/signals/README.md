Signals for bootstack
=====================

Lightweight reactive state. A ``Signal[T]`` holds a value, notifies subscribers
when it changes, and can be bound two-way to widgets. It is backed by a Tk
variable, but that variable is created lazily, so the Tk surface never leaks
into the public API.

> The user-facing guide is ``docs/reference/signals.rst`` (teaching) and the
> API Reference page for ``bootstack.signals`` (lookup). This README covers the
> package internals; keep it in sync with ``signal.py``.

Architecture
- ``Signal[T]`` (public): the reactive cell — ``signal()`` to read, ``set()`` to
  write, ``subscribe()`` to observe, ``map()`` to derive.
- Lazy Tk-var realization: ``Signal(...)`` creates **no** Tk variable at
  construction, so a signal can be created at module level (before any ``App``).
  The backing variable is realized on first bind/escape-hatch access against the
  running interpreter, and re-realized cleanly across ``App`` lifecycles.
- Object mode: values that are not Tk-native (anything other than
  ``bool``/``int``/``float``/``str``/``set`` — e.g. a ``date`` or a dataclass)
  are held as the authoritative Python object; the Tk variable is used only as a
  change-notification bus. Native values are stored in the Tk variable directly.
- ``_SignalTrace`` (internal): manages the Tcl variable trace
  (``trace_add``/``trace_remove``).

Key behaviors
- Read / write: ``signal()`` returns the current value; ``signal.set(v)`` updates
  it. A ``set()`` to an equal value is a no-op (no notification).
- Subscriptions: ``subscribe(callback, *, immediate=False)`` returns a
  ``streams.Handle``; call ``handle.cancel()`` to unsubscribe. ``immediate=True``
  fires the callback once with the current value at subscribe time.
- Derived signals: ``map(transform)`` returns a new signal that follows this one.
  A weak reference keeps the parent from holding the derived signal alive.
- Robustness: the last value is cached and returned even if the backing variable
  has been dropped (e.g. between ``App`` lifecycles).
- Escape hatch: ``Signal.from_variable(tk_var)`` wraps an existing Tk variable,
  and ``signal.var`` exposes the backing variable. These are the only Tk-aware
  paths; everything else stays Tk-free.

Usage
1) Quick start (works at module level — no ``App`` required)
```python
from bootstack.signals import Signal

count = Signal(0)
print(count())        # -> 0
count.set(1)
print(count())        # -> 1
```

2) Two-way binding to a widget
```python
import bootstack as bs

with bs.App() as app:
    name = bs.Signal("")
    bs.TextField(textsignal=name)          # edits flow into the signal
    bs.Label(textsignal=name.map(lambda v: f"Hello, {v}!"))  # derived display
app.run()
```

3) Subscribing and unsubscribing
```python
import bootstack as bs

with bs.App() as app:
    flag = bs.Signal(False)

    def on_flag(value):
        print("flag:", value)

    handle = flag.subscribe(on_flag, immediate=True)  # prints: flag: False
    flag.set(True)                                     # prints: flag: True
    handle.cancel()                                    # stop observing
app.run()
```

4) Typed (object-mode) values
```python
from datetime import date
import bootstack as bs

with bs.App():
    due = bs.Signal(date.today())
    bs.DateField(signal=due)        # binds the typed value
    print(type(due()))              # -> <class 'datetime.date'> (not str)
```

Import path
- ``import bootstack as bs; bs.Signal``
- ``from bootstack.signals import Signal``

Notes
- The UI toolkit is not thread-safe. Marshal cross-thread updates onto the UI
  via the framework's scheduling, not by touching the signal from a worker
  thread.
- Keep subscriber callbacks fast; offload long-running work.
