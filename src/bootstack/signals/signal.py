import tkinter as tk
import weakref
from itertools import count
from typing import Any, Callable, Generic, Type, TypeVar

from bootstack.errors import BootstackError
from bootstack.signals.types import TraceOperation
from bootstack._core.variables import SetVar
from bootstack.streams import Handle

T = TypeVar("T")
U = TypeVar("U")

# Weak registry of all realized signals. Cleared on App.destroy() (when no
# other App is live) so module-level signals can be re-realized against the
# next App's interpreter without dangling against a dead one.
_realized: "weakref.WeakSet[Signal]" = weakref.WeakSet()

# Global subscriber ID counter — unique across all Signal instances so that
# Handle cancellation never accidentally removes the wrong entry.
_sub_counter = count(1)


def reset_realized_signals() -> None:
    """Drop the Tk var from every realized signal.

    Called on App.destroy() when no other App is live. Module-level signals
    return to pending (unrealized) state and re-realize transparently the next
    time a widget inside a new App binds them via .var / .name / .tk.
    """
    for sig in list(_realized):
        try:
            sig._drop_var()
        except Exception:
            pass


class _SignalTrace:
    """Manages the single bridge Tk trace on a realized Signal."""

    def __init__(self, tk_var: tk.Variable):
        self._var = tk_var
        self._traces: dict[str, tuple[TraceOperation, Callable[..., Any]]] = {}

    def add(
            self,
            operation: TraceOperation,
            callback: Callable[[T], Any],
            get_value: Callable[[], T],
    ) -> str:
        def traced_callback(name: str, index: str, mode: str) -> None:
            callback(get_value())

        try:
            fid = self._var.trace_add(operation, traced_callback)
        except tk.TclError as e:
            raise RuntimeError(f"failed to add trace: {e}") from e
        self._traces[fid] = (operation, traced_callback)
        return fid

    def remove(self, fid: str) -> None:
        op_cb = self._traces.pop(fid, None)
        if op_cb is None:
            return
        operation, _ = op_cb
        try:
            self._var.trace_remove(operation, fid)
        except tk.TclError:
            pass


class Signal(Generic[T]):
    """
    A reactive value that widgets can bind to.

    Holds a typed value and notifies subscribers when it changes. Read it by
    calling the signal, update it with `set()`, derive new signals with
    `map()`, and react to changes with `subscribe()`.

    Bind a signal to a widget by passing it as `textsignal=` for text-bearing
    widgets, or `signal=` for boolean and numeric widgets.

    A signal holds one type, decided by the value it is created with. Pass
    `nullable=True` when the value can also be empty — a field bound to a
    nullable signal reports being cleared, where one bound to an ordinary signal
    silently keeps its last value. A nullable signal may be seeded with `None`,
    in which case the first real value decides its type.

    Signals may be constructed at module level (before `bs.App()` exists). The
    backing Tk variable is created lazily on the first widget binding and torn
    down when the App is destroyed, so the same signal can be reused across
    successive App lifecycles.
    """

    _cnt = count(1)

    def __init__(
            self,
            value: T,
            name: str | None = None,
            master: tk.Misc | None = None,
            *,
            nullable: bool = False,
    ):
        self._name = name or f"SIG{next(self._cnt)}"
        self._master: tk.Misc | None = master
        self._nullable = nullable
        if value is None and nullable:
            # Seeded empty, so there is nothing to infer from yet. The type is
            # locked by the first non-None set(), and stays monomorphic after.
            self._type: Type[T] | None = None
            self._object_mode = False
        else:
            self._type = type(value)
            self._object_mode = not self._is_tk_native(value)
        # _last is always the authoritative Python value — before realization it
        # is the only store; after realization it stays in sync via the bridge.
        self._last: T = value
        # Tk var and bridge trace — None until the first widget binding.
        self._var: tk.Variable | None = None
        self._trace: _SignalTrace | None = None
        self._bridge_fid: str | None = None
        # Python-owned subscriber list (int id → callback). The bridge trace fans
        # these out when a widget writes the Tk var; set() notifies them directly
        # while unrealized. Replaces the old one-Tk-trace-per-subscriber model.
        self._subscribers: dict[int, Callable[[T], Any]] = {}

    @staticmethod
    def _is_tk_native(value: Any) -> bool:
        """Whether a value maps to a Tk variable that round-trips it losslessly."""
        return isinstance(value, (bool, int, float, str, set))

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

    def _realize(self) -> None:
        """Create the backing Tk variable and wire the single bridge trace.

        Idempotent — safe to call multiple times. Only runs inside an App
        context (widget bindings are always inside one), so a live interpreter
        is guaranteed.
        """
        if self._var is not None:
            return
        # This is the Python/Tcl boundary. Tcl has no null — everything is a
        # string — so None cannot survive the crossing. Stop it here, not in the
        # widgets: _create_variable() below is the only other way in.
        if self._nullable:
            raise BootstackError(
                "A nullable Signal cannot be bound to a widget that stores its value "
                "directly, such as a text field or a checkbox, because the variable "
                "backing it cannot represent an empty value. Bind it to a field that "
                "carries a typed value instead (NumberField, DateField, TimeField, "
                "Select, SelectButton), or drop nullable=True — a text field is "
                "already empty at ''."
            )
        self._var = self._create_variable(self._last)
        self._trace = _SignalTrace(self._var)

        def _bridge(value: T) -> None:
            if not self._object_mode:
                self._last = value
            for cb in list(self._subscribers.values()):
                cb(self._last)

        self._bridge_fid = self._trace.add("write", _bridge, self)
        _realized.add(self)

    def _drop_var(self) -> None:
        """Release the Tk var and bridge trace (called by reset_realized_signals)."""
        if self._trace is not None and self._bridge_fid is not None:
            self._trace.remove(self._bridge_fid)
        self._var = None
        self._trace = None
        self._bridge_fid = None

    def __call__(self) -> T:
        """Get the current value of the signal."""
        if self._var is None or self._object_mode:
            return self._last
        try:
            value = self._var.get()
            self._last = value
            return value
        except tk.TclError:
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

        self = cls.__new__(cls)
        self._name = name or getattr(tk_var, "_name", str(tk_var))
        self._type = py_type  # type: ignore[assignment]
        self._object_mode = False
        # The var already exists and is the widget's, so it can never be nullable.
        self._nullable = False
        self._master = getattr(tk_var, "_master", None)
        self._subscribers = {}
        try:
            current = tk_var.get()  # type: ignore[assignment]
        except tk.TclError:
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

        # from_variable is immediately realized — the var already exists.
        self._var = tk_var
        self._trace = _SignalTrace(self._var)

        def _bridge(value: T) -> None:
            self._last = value
            for cb in list(self._subscribers.values()):
                cb(self._last)

        self._bridge_fid = self._trace.add("write", _bridge, self)
        _realized.add(self)
        return self

    def set(self, value: T) -> None:
        """
        Set the signal to a new value and notify subscribers.

        Args:
            value: The new value. Must match the signal's type, except that an
                `int` may be set on a `float`-typed signal (it is widened), and
                that `None` is accepted on a signal declared `nullable=True`.

        Raises:
            TypeError: If the value type does not match the signal's type (and is
                not an `int` widened to a `float`), or if it is `None` on a
                signal that was not declared nullable.
        """
        if value is None:
            # A signal whose type IS NoneType has always taken None (map() makes
            # one whenever the transform returns None for the first value seen).
            if not self._nullable and self._type is not type(None):
                raise TypeError(
                    f"Expected {self._type.__name__}, got NoneType. Pass "
                    f"nullable=True to Signal() if this value can be empty."
                )
        elif self._type is None:
            # Seeded empty — the first real value decides the type from here on.
            self._type = type(value)
            self._object_mode = not self._is_tk_native(value)
        elif type(value) is not self._type:
            if self._type is float and type(value) is int:
                value = float(value)  # type: ignore[assignment]
            else:
                raise TypeError(
                    f"Expected {self._type.__name__}, got {type(value).__name__}"
                )

        if self._var is None:
            # Unrealized — notify Python subscribers directly.
            if self._last == value:
                return
            self._last = value
            for cb in list(self._subscribers.values()):
                cb(self._last)
            return

        if self._object_mode:
            if self._last == value:
                return
            self._last = value
            try:
                self._var.set(str(value))
            except tk.TclError:
                pass
            # Bridge trace fires from var.set() → notifies subscribers.
            return

        # Native-type, realized — let the Tk var fire the bridge trace.
        try:
            if self._var.get() == value:
                return
        except tk.TclError:
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
        weak_derived = weakref.ref(derived)

        def update(value: T) -> None:
            d = weak_derived()
            if d is None:
                return
            d.set(transform(value))

        self.subscribe(update)
        return derived

    def subscribe(self, callback: Callable[[T], Any], *, immediate: bool = False) -> Handle:
        """
        Subscribe to value changes of this signal.

        Args:
            callback: A function called with the new value whenever it changes.
            immediate: When True, also call `callback` once with the current
                value at subscription time. Defaults to False.

        Returns:
            A cancellable `Handle` — call `.cancel()` to stop listening, or use
            it as a context manager to unsubscribe on exit.
        """
        fid = next(_sub_counter)
        self._subscribers[fid] = callback
        if immediate:
            callback(self())
        return Handle(lambda: self._subscribers.pop(fid, None))

    @property
    def name(self) -> str:
        """The internal Tcl variable name. Accessing this realizes the signal."""
        self._realize()
        return self._name

    @property
    def type(self) -> Type[T] | None:
        """The type of the signal value.

        `None` on a nullable signal seeded empty, until the first real value
        sets it.
        """
        return self._type

    @property
    def nullable(self) -> bool:
        """Whether this signal can hold an empty value.

        A nullable signal accepts `set(None)`, so a field bound to it reports
        being cleared instead of silently keeping its last value. Declare it at
        construction with `bs.Signal(value, nullable=True)`.
        """
        return self._nullable

    @property
    def var(self) -> tk.Variable:
        """The backing `tk.Variable`. Accessing this realizes the signal."""
        self._realize()
        return self._var  # type: ignore[return-value]

    @property
    def tk(self) -> tk.Variable:
        """Underlying `tk.Variable`. UNSUPPORTED — escape-hatch use only."""
        self._realize()
        return self._var  # type: ignore[return-value]

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return self._name