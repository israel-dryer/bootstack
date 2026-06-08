import tkinter as tk
import weakref
from itertools import count
from typing import Any, Callable, Generic, Type, TypeVar

from bootstack.signals.types import TraceOperation
from bootstack._core.variables import SetVar

T = TypeVar("T")
U = TypeVar("U")


class _SignalTrace:
    """
    Internal helper to manage Tcl variable traces using tkinter's Variable API.
    This class encapsulates low-level `trace_add` and `trace_remove` logic.
    """

    def __init__(self, tk_var: tk.Variable):
        """
        Initialize a trace manager for a tkinter variable.

        Args:
            tk_var: A tkinter.Variable instance (e.g., StringVar, IntVar).
        """
        self._var = tk_var
        # Map trace id -> (operation, callback)
        self._traces: dict[str, tuple[TraceOperation, Callable[..., Any]]] = {}

    def callbacks(self) -> tuple[str, ...]:
        """
        Return all currently active trace IDs.

        Returns:
            A tuple of trace ID strings.
        """
        return tuple(self._traces.keys())

    def add(
            self,
            operation: TraceOperation,
            callback: Callable[[T], Any],
            get_value: Callable[[], T],
    ) -> str:
        """
        Add a new trace that calls a callback when the variable is written.
        """

        def traced_callback(name: str, index: str, mode: str) -> None:
            callback(get_value())

        try:
            fid = self._var.trace_add(operation, traced_callback)
        except tk.TclError as e:
            raise RuntimeError(f"failed to add trace: {e}") from e
        self._traces[fid] = (operation, traced_callback)
        return fid

    def remove(self, fid: str) -> None:
        """
        Remove a trace by ID. Safe if already removed or variable destroyed.
        """
        op_cb = self._traces.pop(fid, None)
        if op_cb is None:
            return
        operation, _ = op_cb
        try:
            self._var.trace_remove(operation, fid)
        except tk.TclError:
            # Variable may be unset/destroyed; ignore
            pass


class Signal(Generic[T]):
    """
    A reactive value that widgets can bind to.

    Holds a typed value and notifies subscribers when it changes. Read it by
    calling the signal, update it with `set()`, derive new signals with
    `map()`, and react to changes with `subscribe()`.

    Bind a signal to a widget by passing it as `textsignal=` for text-bearing
    widgets, or `signal=` for boolean and numeric widgets.
    """

    _cnt = count(1)

    def __init__(self, value: T, name: str | None = None, master: tk.Misc | None = None):
        self._name = name or f"SIG{next(self._cnt)}"
        self._type: Type[T] = type(value)
        self._master: tk.Misc | None = master
        self._var = self._create_variable(value)
        self._trace = _SignalTrace(self._var)
        # Map fid -> callback to allow multiple subscriptions of same function
        self._subscribers: dict[str, Callable[[T], Any]] = {}
        # Reverse index: callback -> set of fids
        self._callback_index: dict[Callable[[T], Any], set[str]] = {}
        # Cache last known value for robustness when Tcl variable is torn down
        self._last: T = value

    def _create_variable(self, value: T) -> tk.Variable:
        if isinstance(value, bool):
            return tk.BooleanVar(master=self._master, name=self._name, value=value)
        elif isinstance(value, int):
            return tk.IntVar(master=self._master, name=self._name, value=value)
        elif isinstance(value, float):
            return tk.DoubleVar(master=self._master, name=self._name, value=value)
        elif isinstance(value, set):
            return SetVar(master=self._master, name=self._name, value=value)
        else:
            return tk.StringVar(master=self._master, name=self._name, value=value)

    def __call__(self) -> T:
        """
        Get the current value of the signal.

        Returns:
            The current typed value.
        """
        try:
            value = self._var.get()
            self._last = value  # cache last good value
            return value
        except tk.TclError:
            # Return last known value when underlying var is destroyed/unset
            return self._last

    @classmethod
    def from_variable(
            cls,
            tk_var: tk.Variable,
            *,
            name: str | None = None,
            coerce: Type[T] | None = None,
    ) -> "Signal[T]":
        """
        Wrap an existing tkinter Variable as a Signal.

        Args:
            tk_var: An existing tkinter.Variable instance (StringVar, IntVar, etc.).
            name: Optional override of the Tcl variable name. Defaults to tk_var's name.
            coerce: Optional Python type to treat the signal as (e.g., int/float/bool/str).
                    If omitted, the type is inferred from the tk_var subclass.

        Returns:
            A Signal bound to the provided tk_var.
        """
        # Infer Python type from the tk variable if not explicitly provided
        if coerce is None:
            if isinstance(tk_var, tk.BooleanVar):
                py_type: Type[Any] = bool
            elif isinstance(tk_var, tk.IntVar):
                py_type = int
            elif isinstance(tk_var, tk.DoubleVar):
                py_type = float
            elif isinstance(tk_var, SetVar):
                py_type = set
            else:
                py_type = str
        else:
            py_type = coerce

        # Construct without creating a new tk.Variable
        self = cls.__new__(cls)  # bypass __init__
        self._name = name or getattr(tk_var, "_name", str(tk_var))
        self._type = py_type  # type: ignore[assignment]
        self._var = tk_var
        self._trace = _SignalTrace(self._var)
        self._subscribers = {}
        self._callback_index = {}
        # Best-effort capture of master/interpreter for reference
        self._master = getattr(tk_var, "_master", None)
        try:
            current = tk_var.get()  # type: ignore[assignment]
        except tk.TclError:
            # Fallback default per inferred type
            if py_type is float:  # type: ignore[comparison-overlap]
                current = 0.0
            elif py_type is int:  # type: ignore[comparison-overlap]
                current = 0
            elif py_type is bool:  # type: ignore[comparison-overlap]
                current = False
            elif py_type is set:
                current = set()
            else:
                current = ""
        self._last = current  # type: ignore[assignment]
        return self

    def set(self, value: T) -> None:
        """
        Set the signal to a new value and notify subscribers.

        Args:
            value: The new value. Must match the signal's type, except that an
                `int` may be set on a `float`-typed signal (it is widened).

        Raises:
            TypeError: If the value type does not match the signal's type (and is
                not an `int` widened to a `float`).
        """
        # Enforce the type to avoid surprises (e.g. a bool accepted for an int),
        # but widen an int into a float-typed signal — a Slider seeded at 0 and
        # later set to 0.5 is the common case. `type(value) is int` excludes bool.
        if type(value) is not self._type:
            if self._type is float and type(value) is int:
                value = float(value)  # type: ignore[assignment]
            else:
                raise TypeError(
                    f"Expected {self._type.__name__}, got {type(value).__name__}"
                )
        # Reduce redundant updates if value unchanged
        try:
            current = self._var.get()
            if current == value:
                return
        except tk.TclError:
            # If var is gone, proceed to set and let Tcl recreate path if possible
            pass
        self._var.set(value)
        self._last = value

    def map(self, transform: Callable[[T], U]) -> 'Signal[U]':
        """
        Create a derived signal that transforms this signal's value.

        The derived signal recomputes whenever this signal changes. It is held
        weakly, so keep a reference to it — for example, by binding it to a
        widget — or it will stop updating once garbage-collected.

        Args:
            transform: A function applied to the current and future values.

        Returns:
            A new read-only signal that stays updated with the transformed value.
        """
        derived = Signal(transform(self()))

        # Use weakref to avoid keeping derived alive solely via subscription
        weak_derived = weakref.ref(derived)

        def update(value: T) -> None:
            d = weak_derived()
            if d is None:
                # Auto-detach if derived is GC'd
                return
            d.set(transform(value))

        self.subscribe(update)
        return derived

    def subscribe(self, callback: Callable[[T], Any], *, immediate: bool = False) -> str:
        """
        Subscribe to value changes of this signal.

        Args:
            callback: A function called with the new value whenever it changes.
            immediate: When True, also call `callback` once with the current
                value at subscription time. Defaults to False.

        Returns:
            A subscription id — pass it to `unsubscribe()` to stop listening.
        """
        fid = self._trace.add("write", callback, self)
        self._subscribers[fid] = callback
        self._callback_index.setdefault(callback, set()).add(fid)
        if immediate:
            # Call synchronously at subscription time; let any error surface to
            # the caller rather than swallowing a real bug in the callback.
            callback(self())
        return fid

    def unsubscribe(self, funcid: str) -> None:
        """
        Remove a previously registered subscriber.

        Args:
            funcid: The function id returned from `subscribe()`.
        """
        self._subscribers.pop(funcid, None)
        self._trace.remove(funcid)

    def unsubscribe_all(self) -> None:
        """
        Remove all currently subscribed callbacks.
        """
        # Copy keys to avoid mutation during iteration
        for fid in list(self._subscribers.keys()):
            self._trace.remove(fid)
        self._subscribers.clear()
        self._callback_index.clear()

    @property
    def name(self) -> str:
        """
        The internal name of the signal, used when binding it to a widget.
        """
        return self._name

    @property
    def type(self) -> Type[T]:
        """
        The original type of the signal value.

        Returns:
            A Python type (e.g., int, str).
        """
        return self._type

    @property
    def var(self) -> tk.Variable:
        return self._var

    @property
    def tk(self) -> tk.Variable:
        """Underlying `tk.Variable`. UNSUPPORTED — escape-hatch use only."""
        return self._var

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return self._name
