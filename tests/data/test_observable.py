"""Tests for DataSource change broadcasting — on_change / observe.

The headless tests (no App) exercise the synchronous-degrade path: with no
active App the hub delivers each emit immediately on the calling thread, which
makes assertions deterministic. The gui-marked tests cover the coalescing and
thread-marshaling behavior that only exists under a running event loop.
"""
from __future__ import annotations

import threading
import time

import pytest

from bootstack import col
from bootstack.data import MemoryDataSource, SqliteDataSource


SOURCES = [MemoryDataSource, SqliteDataSource]


def _seed(cls):
    return cls().load(
        [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 20},
            {"name": "Carol", "age": 40},
        ]
    )


# ---------------------------------------------------------------------------
# Layer 1 — on_change (headless, synchronous)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", SOURCES)
def test_on_change_fires_per_mutation(cls):
    ds = _seed(cls)
    kinds = []
    ds.on_change(lambda e: kinds.append(e.kind))

    rid = ds.insert({"name": "Dan", "age": 50})
    ds.update(rid, {"age": 51})
    ds.delete(rid)
    ds.where(col("age") >= 30)
    ds.order("-age")

    assert kinds == ["insert", "update", "delete", "filter", "sort"]


@pytest.mark.parametrize("cls", SOURCES)
def test_failed_mutation_does_not_emit(cls):
    ds = _seed(cls)
    kinds = []
    ds.on_change(lambda e: kinds.append(e.kind))

    assert ds.update(999_999, {"age": 1}) is False
    assert ds.delete(999_999) is False
    assert kinds == []


@pytest.mark.parametrize("cls", SOURCES)
def test_silence_suppresses_emission(cls):
    ds = _seed(cls)
    kinds = []
    ds.on_change(lambda e: kinds.append(e.kind))

    with ds._silence():
        ds.insert({"name": "Dan", "age": 50})
        ds.where(col("age") > 0)

    assert kinds == []
    # Emission resumes after the block.
    ds.insert({"name": "Eve", "age": 60})
    assert kinds == ["insert"]


@pytest.mark.parametrize("cls", SOURCES)
def test_subscription_cancel_stops_delivery(cls):
    ds = _seed(cls)
    kinds = []
    sub = ds.on_change(lambda e: kinds.append(e.kind))
    ds.insert({"name": "Dan", "age": 50})
    sub.cancel()
    ds.insert({"name": "Eve", "age": 60})
    assert kinds == ["insert"]


@pytest.mark.parametrize("cls", SOURCES)
def test_insert_event_carries_id(cls):
    ds = _seed(cls)
    seen = []
    ds.on_change(lambda e: seen.append(e))
    rid = ds.insert({"name": "Dan", "age": 50})
    assert seen[-1].kind == "insert"
    assert seen[-1].id == rid


def test_reentrant_handler_does_not_loop():
    ds = MemoryDataSource().load([{"n": 1}])
    calls = []

    def handler(e):
        calls.append(e.kind)
        if len(calls) < 3:
            ds.insert({"n": len(calls) + 1})

    ds.on_change(handler)
    ds.insert({"n": 2})
    # Drains the cascade without recursing forever.
    assert calls == ["insert", "insert", "insert"]


# ---------------------------------------------------------------------------
# Layer 2 — observe (read-only query primitive, headless)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", SOURCES)
def test_query_does_not_disturb_view_state(cls):
    ds = _seed(cls)
    ds.where(col("age") > 100)
    ds.order("name")
    filter_before, sort_before = ds._filter, ds._sort

    rows = ds._query(col("age") > 0, [])

    assert len(rows) == 3
    assert ds._filter is filter_before
    assert ds._sort is sort_before
    # The active (empty) view is unchanged — pagination still sees the filter.
    assert ds.count == 0


@pytest.mark.parametrize("cls", SOURCES)
def test_query_applies_condition_and_order(cls):
    ds = _seed(cls)
    rows = ds._query(col("age") >= 30, [])
    names = {r["name"] for r in rows}
    assert names == {"Alice", "Carol"}


# ---------------------------------------------------------------------------
# gui-marked — coalescing, observe stream, thread marshaling (needs an App)
# ---------------------------------------------------------------------------


def _drain(root, ms=80):
    """Pump the event loop so scheduled after_idle flushes run."""
    deadline = time.time() + ms / 1000.0
    while time.time() < deadline:
        root.update()
        root.update_idletasks()
        time.sleep(0.005)


@pytest.mark.gui
def test_coalesces_burst_into_one_notification(tmp_tk_root):
    ds = MemoryDataSource().load([])
    notifications = []
    ds.on_change(lambda e: notifications.append(e))

    for i in range(20):
        ds.insert({"n": i})

    _drain(tmp_tk_root)
    # 20 inserts in one turn coalesce into a single coarse notification.
    assert len(notifications) == 1
    assert ds.count == 20


@pytest.mark.gui
def test_observe_emits_initial_then_on_change(tmp_tk_root):
    ds = MemoryDataSource().load([{"name": "A", "status": "active"}])
    results = []
    sub = ds.observe(col("status") == "active").listen(lambda rows: results.append(rows))

    # Immediate emit on subscribe.
    assert len(results) == 1
    assert len(results[0]) == 1

    ds.insert({"name": "B", "status": "active"})
    _drain(tmp_tk_root)
    assert len(results) == 2
    assert len(results[-1]) == 2

    # A non-matching row does not change the result set → no new emit.
    ds.insert({"name": "C", "status": "inactive"})
    _drain(tmp_tk_root)
    assert len(results) == 2

    sub.cancel()


@pytest.mark.gui
def test_observe_ignores_selection_changes(tmp_tk_root):
    ds = MemoryDataSource().load([{"name": "A"}, {"name": "B"}])
    results = []
    ds.observe().listen(lambda rows: results.append(rows))
    assert len(results) == 1  # initial

    ids = [r["id"] for r in ds.page_slice(0, ds.count)]
    ds.select(ids[0])
    _drain(tmp_tk_root)
    # Selection is not a row-set change — observe does not re-emit.
    assert len(results) == 1


@pytest.mark.gui
def test_background_thread_mutation_marshals_to_main(tmp_tk_root):
    ds = MemoryDataSource().load([])
    threads_seen = []
    ds.on_change(lambda e: threads_seen.append(threading.current_thread()))

    def worker():
        ds.insert({"n": 1})

    t = threading.Thread(target=worker)
    t.start()
    t.join()
    _drain(tmp_tk_root)

    assert len(threads_seen) == 1
    # The handler ran on the main thread, not the worker thread.
    assert threads_seen[0] is threading.main_thread()
