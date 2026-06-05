"""Change broadcasting for data sources — the reactive engine behind
`DataSource.on_change` and `DataSource.observe`.

A `_ChangeHub` is composed into every `BaseDataSource` (as `self._hub`). It is
plain Python — no Tkinter dependency of its own — so the data layer stays
testable headless. The hub does three things:

1. **Broadcast** — fan a `DataChangeEvent` out to coarse listeners
   (`on_change`) and to live result-set queries (`observe`).
2. **Marshal** — when a mutation happens on a background thread (a web feed,
   a file load), defer delivery to the Tk main thread so bound widgets update
   safely. With no active App it degrades to synchronous, in-thread delivery.
3. **Coalesce** — collapse a burst of mutations in one event-loop turn into a
   single recompute/notification (invalidate-and-refetch, à la TanStack Query).

`silence()` suppresses emission for the duration of a `with` block. Widgets use
it to wrap mutations they make to their *own* bound source, so a widget does not
broadcast a change back to itself.
"""

from __future__ import annotations

import contextlib
import logging
import threading
import warnings
from typing import TYPE_CHECKING, Any, Callable, List

from bootstack.events import DataChangeEvent

if TYPE_CHECKING:
    from bootstack.data.query import Condition, SortKey
    from bootstack.data.types import DataSourceProtocol, Record

logger = logging.getLogger(__name__)

# Safety net: if a change handler mutates the source on every flush it would
# loop forever. Drain at most this many ticks per flush, then bail with a warning.
_MAX_FLUSH_ITERATIONS = 100


class _ObservedQuery:
    """A live `where`/`order` slice registered with a `_ChangeHub`.

    Holds its own filter/sort (independent of the source's pagination view
    state) and re-runs against the source on each relevant change, emitting a
    fresh result-set to its handler only when the rows actually change.
    """

    __slots__ = ("_source", "_condition", "_sort_keys", "_emit", "_signature", "_last")

    def __init__(
        self,
        source: "DataSourceProtocol",
        condition: "Condition | None",
        sort_keys: "List[SortKey]",
        emit: Callable[[list], Any],
    ) -> None:
        self._source = source
        self._condition = condition
        self._sort_keys = sort_keys
        self._emit = emit
        self._signature: Any = None
        self._last: "List[Record] | None" = None

    def current(self) -> "List[Record]":
        """Run the query against the source and return the result-set."""
        return self._source._query(self._condition, self._sort_keys)

    def start(self) -> "List[Record]":
        """Compute, cache, and return the initial result-set (on subscribe)."""
        rows = self.current()
        self._signature = self._signature_of(rows)
        self._last = rows
        return rows

    def recompute(self) -> None:
        """Re-run the query; emit to the handler only if the result changed."""
        rows = self.current()
        sig = self._signature_of(rows)
        if sig == self._signature and rows == self._last:
            return
        self._signature = sig
        self._last = rows
        self._emit(rows)

    @staticmethod
    def _signature_of(rows: "List[Record]") -> Any:
        """A cheap identity for fast change detection (len + id tuple)."""
        return (len(rows), tuple(r.get("id") for r in rows))


class _ChangeHub:
    """Per-source pub/sub with thread marshaling and coalescing.

    Args:
        source: The data source that owns this hub. Used to run observed
            queries via its `_query` method.
    """

    __slots__ = (
        "_source",
        "_listeners",
        "_queries",
        "_pending",
        "_flush_scheduled",
        "_silence",
        "_in_flush",
        "_lock",
    )

    def __init__(self, source: "DataSourceProtocol") -> None:
        self._source = source
        self._listeners: List[Callable[[DataChangeEvent], Any]] = []
        self._queries: List[_ObservedQuery] = []
        self._pending: List[DataChangeEvent] = []
        self._flush_scheduled = False
        # Silencing is thread-local: a widget silencing its own main-thread write
        # must not suppress a concurrent background-thread mutation (which is a
        # genuinely external change that bound widgets need to see).
        self._silence = threading.local()
        self._in_flush = False
        self._lock = threading.Lock()

    def _silence_depth(self) -> int:
        return getattr(self._silence, "depth", 0)

    # ----- registration ------------------------------------------------------

    def add_listener(self, fn: Callable[[DataChangeEvent], Any]) -> Callable[[], None]:
        """Register a coarse change listener; returns an unregister callable."""
        self._listeners.append(fn)

        def _remove() -> None:
            try:
                self._listeners.remove(fn)
            except ValueError:
                pass

        return _remove

    def add_query(self, query: _ObservedQuery) -> Callable[[], None]:
        """Register a live observed query; returns an unregister callable."""
        self._queries.append(query)

        def _remove() -> None:
            try:
                self._queries.remove(query)
            except ValueError:
                pass

        return _remove

    # ----- silencing ---------------------------------------------------------

    @contextlib.contextmanager
    def silence(self):
        """Suppress emission on the current thread for the block (nestable)."""
        self._silence.depth = self._silence_depth() + 1
        try:
            yield
        finally:
            self._silence.depth = self._silence_depth() - 1

    # ----- emission ----------------------------------------------------------

    def emit(self, event: DataChangeEvent) -> None:
        """Broadcast a change, marshaling to the main thread and coalescing.

        A no-op while `silence()` is active. With no active App, delivers
        synchronously on the calling thread (deterministic for headless use).
        """
        if self._silence_depth() > 0:
            return

        # Lazy import to avoid a load-time cycle with the runtime/app module.
        from bootstack._runtime.app import get_current_app, has_current_app

        app = None
        schedule = False
        flush_now = False
        with self._lock:
            self._pending.append(event)
            if not has_current_app():
                flush_now = True
            elif not self._flush_scheduled:
                self._flush_scheduled = True
                schedule = True
                app = get_current_app()
            # else: a flush is already queued — this event rides along (coalesce).

        if flush_now:
            self._flush()
        elif schedule:
            on_main = threading.current_thread() is threading.main_thread()
            try:
                # after_idle coalesces naturally on the main thread; from a
                # worker thread hop onto the loop with after(0, ...).
                if on_main:
                    app.after_idle(self._flush)
                else:
                    app.after(0, self._flush)
            except Exception:
                # App is tearing down or the loop is gone — drop the schedule.
                with self._lock:
                    self._flush_scheduled = False

    def _flush(self) -> None:
        """Drain pending events: recompute queries, then notify listeners once.

        Runs on the Tk main thread (scheduled via the App) whenever an App is
        active; only the headless path runs it on the emitting thread. The
        `_in_flush` / `_pending`-swap bookkeeping outside the lock relies on that
        single-threaded-under-an-App invariant.
        """
        if self._in_flush:
            # Re-entrant call (a handler mutated the source) — the running loop
            # will pick up the newly queued events.
            return
        self._in_flush = True
        try:
            iterations = 0
            while True:
                with self._lock:
                    if not self._pending:
                        self._flush_scheduled = False
                        break
                    events = self._pending
                    self._pending = []
                iterations += 1
                if iterations > _MAX_FLUSH_ITERATIONS:
                    with self._lock:
                        self._pending.clear()
                        self._flush_scheduled = False
                    warnings.warn(
                        "DataSource change flush exceeded its iteration limit; "
                        "a change handler may be mutating the source in a loop.",
                        RuntimeWarning,
                        stacklevel=2,
                    )
                    break
                self._dispatch(events)
        finally:
            self._in_flush = False

    def _dispatch(self, events: List[DataChangeEvent]) -> None:
        """Recompute observed queries, then fire coarse listeners once."""
        kinds = {e.kind for e in events}
        row_changed = bool(kinds - {"select"})  # selection is not a row-set change

        if self._queries and row_changed:
            for query in list(self._queries):
                try:
                    query.recompute()
                except Exception:
                    logger.exception("observe() query handler raised; continuing")

        if self._listeners:
            rep = self._representative(events)
            for fn in list(self._listeners):
                try:
                    fn(rep)
                except Exception:
                    logger.exception("on_change() handler raised; continuing")

    @staticmethod
    def _representative(events: List[DataChangeEvent]) -> DataChangeEvent:
        """Pick one event to stand for the batch.

        A single coalesced kind keeps its last event; a mix collapses to a
        coarse `reload`.
        """
        kinds = {e.kind for e in events}
        if len(kinds) == 1:
            return events[-1]
        return DataChangeEvent(kind="reload")
