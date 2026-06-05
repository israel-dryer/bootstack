from __future__ import annotations

import tkinter as tk
from typing import Any, Callable, Generic, Optional, TypeVar

from bootstack.events import Subscription

T = TypeVar("T")
U = TypeVar("U")


class Handle:
    """Cancellable handle returned by stream terminal operators.

    Duck-type compatible with `Subscription` — supports `.cancel()`,
    context manager protocol, and `.cancelled` property.

    Returned by `Stream.listen()` and time-based stream operators
    (`debounce`, `throttle`, `delay`).
    """

    __slots__ = ("_fn", "_cancelled")

    def __init__(self, cancel_fn: Callable[[], None]) -> None:
        self._fn = cancel_fn
        self._cancelled = False

    def cancel(self) -> None:
        """Detach the handler and clean up all resources in the chain."""
        if self._cancelled:
            return
        self._cancelled = True
        try:
            self._fn()
        except Exception:
            pass

    def __enter__(self) -> "Handle":
        return self

    def __exit__(self, *_: Any) -> None:
        self.cancel()

    @property
    def cancelled(self) -> bool:
        """True once `.cancel()` has been called."""
        return self._cancelled


class _Scheduler:
    """Timer adapter for stream operators.

    Tracks all pending tokens and cancels them when the owner widget is
    destroyed, preventing callbacks from firing on dead widgets.
    """

    __slots__ = ("_w", "_tokens")

    def __init__(self, widget: tk.Misc) -> None:
        self._w = widget
        self._tokens: set = set()
        try:
            widget.bind("<Destroy>", self._on_destroy, add=True)
        except Exception:
            pass

    def call_later(self, ms: int, fn: Callable[[], None]) -> Any:
        tok = self._w.after(max(0, int(ms)), fn)
        self._tokens.add(tok)
        return tok

    def cancel(self, token: Any) -> None:
        self._tokens.discard(token)
        try:
            self._w.after_cancel(token)
        except Exception:
            pass

    def _on_destroy(self, *_: Any) -> None:
        for tok in list(self._tokens):
            try:
                self._w.after_cancel(tok)
            except Exception:
                pass
        self._tokens.clear()


# Union of the two subscription-compatible types.
AnySubscription = Subscription | Handle


class Stream(Generic[T]):
    """A composable push-stream for widget events.

    Created by `widget.on(event)` (no handler). Chain operators to transform
    or filter events, then call `.listen(handler)` to attach a handler and
    activate the upstream event binding.

    Usage::

        # Simple — bind immediately, return Subscription
        sub = widget.on("change", handler)

        # Composed — lazy bind, activated by .listen()
        sub = (
            widget.on("change")
            .debounce(300)
            .filter(lambda e: len(e.value or "") > 1)
            .listen(on_search)
        )

        sub.cancel()   # detach handler and remove the event binding

    All operator methods return a new `Stream` — they do not consume the
    original. `.listen()` is the only terminal; it activates the binding and
    returns a cancellable handle.

    Args:
        owner: Widget used for timer scheduling (debounce/throttle delays).
        _source: Internal — callable that, given a downstream handler,
            installs the upstream binding and returns a handle.
    """

    def __init__(
        self,
        owner: tk.Misc,
        *,
        _source: Optional[Callable[[Callable[[T], Any]], AnySubscription]] = None,
        _scheduler: Optional[_Scheduler] = None,
    ) -> None:
        self._owner = owner
        self._source = _source
        self._sched = _scheduler or _Scheduler(owner)

    # ----- operators ---------------------------------------------------------

    def map(self, fn: Callable[[T], U]) -> "Stream[U]":
        """Transform each event value through `fn`.

        Args:
            fn: Mapping function applied to each value.

        Returns:
            New stream emitting transformed values.
        """
        parent = self

        def _source(handler: Callable[[U], Any]) -> AnySubscription:
            return parent.listen(lambda v: handler(fn(v)))

        return Stream(self._owner, _source=_source, _scheduler=self._sched)

    def filter(self, pred: Callable[[T], bool]) -> "Stream[T]":
        """Emit only values for which `pred(value)` is `True`.

        Args:
            pred: Predicate — values returning `False` are dropped.

        Returns:
            New stream emitting only matching values.
        """
        parent = self

        def _source(handler: Callable[[T], Any]) -> AnySubscription:
            return parent.listen(lambda v: handler(v) if pred(v) else None)

        return Stream(self._owner, _source=_source, _scheduler=self._sched)

    def tap(self, fn: Callable[[T], Any]) -> "Stream[T]":
        """Call `fn` for side-effects on each value; forward value unchanged.

        Args:
            fn: Side-effect function (result is ignored).

        Returns:
            New stream emitting the original values.
        """
        parent = self

        def _source(handler: Callable[[T], Any]) -> AnySubscription:
            def _tap(v: T) -> None:
                fn(v)
                handler(v)
            return parent.listen(_tap)

        return Stream(self._owner, _source=_source, _scheduler=self._sched)

    def debounce(self, ms: int) -> "Stream[T]":
        """Emit after `ms` milliseconds of silence — resets on each new value.

        Useful for search-as-you-type: only fires after the user stops typing.

        Args:
            ms: Quiet period in milliseconds before emission.

        Returns:
            New stream emitting debounced values.
        """
        parent = self
        sched = self._sched

        def _source(handler: Callable[[T], Any]) -> AnySubscription:
            state: dict[str, Any] = {"token": None, "last": None}

            def _fire() -> None:
                state["token"] = None
                handler(state["last"])

            def _on_value(v: T) -> None:
                state["last"] = v
                if state["token"] is not None:
                    sched.cancel(state["token"])
                state["token"] = sched.call_later(ms, _fire)

            upstream = parent.listen(_on_value)

            def _cancel() -> None:
                if state["token"] is not None:
                    sched.cancel(state["token"])
                    state["token"] = None
                upstream.cancel()

            return Handle(_cancel)

        return Stream(self._owner, _source=_source, _scheduler=self._sched)

    def throttle(self, ms: int) -> "Stream[T]":
        """Emit at most once per `ms` milliseconds (leading edge).

        Args:
            ms: Minimum interval between emissions in milliseconds.

        Returns:
            New stream emitting throttled values.
        """
        parent = self
        sched = self._sched

        def _source(handler: Callable[[T], Any]) -> AnySubscription:
            state: dict[str, Any] = {"open": True, "token": None}

            def _reopen() -> None:
                state["open"] = True
                state["token"] = None

            def _on_value(v: T) -> None:
                if state["open"]:
                    state["open"] = False
                    handler(v)
                    state["token"] = sched.call_later(ms, _reopen)

            upstream = parent.listen(_on_value)

            def _cancel() -> None:
                if state["token"] is not None:
                    sched.cancel(state["token"])
                    state["token"] = None
                upstream.cancel()

            return Handle(_cancel)

        return Stream(self._owner, _source=_source, _scheduler=self._sched)

    def delay(self, ms: int) -> "Stream[T]":
        """Re-emit each value after a fixed `ms` millisecond delay.

        Args:
            ms: Delay in milliseconds applied to each value.

        Returns:
            New stream emitting delayed values.
        """
        parent = self
        sched = self._sched

        def _source(handler: Callable[[T], Any]) -> AnySubscription:
            tokens: set[Any] = set()

            def _on_value(v: T) -> None:
                tok_holder: list[Any] = [None]

                def _fire() -> None:
                    tokens.discard(tok_holder[0])
                    handler(v)

                tok = sched.call_later(ms, _fire)
                tok_holder[0] = tok
                tokens.add(tok)

            upstream = parent.listen(_on_value)

            def _cancel() -> None:
                for tok in list(tokens):
                    sched.cancel(tok)
                tokens.clear()
                upstream.cancel()

            return Handle(_cancel)

        return Stream(self._owner, _source=_source, _scheduler=self._sched)

    # ----- terminal ----------------------------------------------------------

    def listen(self, handler: Callable[[T], Any]) -> AnySubscription:
        """Attach `handler` and activate the upstream event binding.

        This is the only terminal operator. Returns a cancellable handle —
        call `.cancel()` to detach the handler and clean up all resources
        (event binding, pending timers) in the operator chain.

        Args:
            handler: Callable invoked for each event value.

        Returns:
            Cancellable handle.
        """
        if self._source is None:
            raise RuntimeError(
                "Stream has no source. Use widget.on(event) to create a stream."
            )
        return self._source(handler)
