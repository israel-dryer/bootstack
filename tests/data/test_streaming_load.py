"""Tests for SqliteDataSource streaming chunked load.

`load()` consumes its input as a stream and inserts in chunks within a single
transaction, so a lazy iterator of many rows loads with bounded memory, and the
whole load is atomic — a mid-stream failure rolls the table back to its prior
state. These are headless (no App).
"""
from __future__ import annotations

import pytest

from bootstack.data import MemoryDataSource, SqliteDataSource
from bootstack.errors import DuplicateIdError, SerializationError


def _gen(n, *, start=0):
    for i in range(start, start + n):
        yield {"id": i, "name": f"p{i}", "tags": [i]}


def test_loads_from_a_generator():
    ds = SqliteDataSource().load(_gen(2500), chunk_size=1000)
    assert ds.count == 2500
    assert ds.get(7)["name"] == "p7"


def test_progress_callback_reports_running_total():
    seen = []
    SqliteDataSource().load(_gen(2500), chunk_size=1000, on_progress=seen.append)
    assert seen == [1000, 2000, 2500]


def test_final_progress_equals_count():
    seen = []
    ds = SqliteDataSource().load(_gen(1234), chunk_size=500, on_progress=seen.append)
    assert seen[-1] == ds.count == 1234


def test_chunk_size_does_not_change_result():
    a = SqliteDataSource().load(_gen(300), chunk_size=7)
    b = SqliteDataSource().load(_gen(300), chunk_size=10_000)
    assert a.count == b.count == 300
    assert a.get(150)["name"] == b.get(150)["name"] == "p150"


def test_data_bag_survives_streaming_load():
    ds = SqliteDataSource().load(
        iter([{"id": 1, "name": "Alice", "tags": ["x", "y"], "meta": {"k": 1}}])
    )
    rec = ds.get(1)
    assert rec["tags"] == ["x", "y"]
    assert rec["meta"] == {"k": 1}


def test_sequence_rows_stream_with_column_keys():
    rows = ((i, f"p{i}") for i in range(50))
    ds = SqliteDataSource().load(rows, column_keys=["id", "name"], chunk_size=10)
    assert ds.count == 50
    assert ds.get(3)["name"] == "p3"


def test_duplicate_id_mid_stream_rolls_back():
    ds = SqliteDataSource().load([{"id": 100, "name": "keep"}])

    def bad():
        yield {"id": 1, "name": "a"}
        yield {"id": 1, "name": "dup"}

    with pytest.raises(DuplicateIdError):
        ds.load(bad(), chunk_size=1)

    # The failed load is atomic — the prior table is restored intact.
    assert ds.count == 1
    assert ds.get(100)["name"] == "keep"


def test_serialization_error_mid_stream_rolls_back():
    ds = SqliteDataSource().load([{"id": 100, "name": "keep"}])

    def bad():
        yield {"id": 1, "name": "a"}
        yield {"id": 2, "name": "b", "obj": object()}  # not JSON-serializable

    with pytest.raises(SerializationError):
        ds.load(bad(), chunk_size=10)

    assert ds.count == 1
    assert ds.get(100)["name"] == "keep"


def test_memory_load_accepts_a_generator():
    # Consistency with SqliteDataSource: both load() methods accept any iterable,
    # so a streaming reader generator works with either source.
    ds = MemoryDataSource().load(_gen(50))
    assert ds.count == 50
    assert ds.get(7)["name"] == "p7"
    assert ds.get(7)["tags"] == [7]


def test_fresh_source_reads_empty_not_raise():
    # A fresh SqliteDataSource (no table yet) reads as empty, like MemoryDataSource —
    # it must not raise "no such table".
    ds = SqliteDataSource()
    assert ds.count == 0
    assert ds.page(0) == []
    assert ds.page_slice(0, 10) == []
    assert ds.selected() == []
    assert ds.selected_count == 0
    assert ds.has_next_page() is False
    assert ds.get(1) is None
    assert ds.update(1, {"x": 1}) is False
    assert ds.delete(1) is False
    assert ds.is_selected(1) is False
    assert ds.select_all() == 0


@pytest.mark.parametrize("cls", [MemoryDataSource, SqliteDataSource])
def test_empty_load_clears_and_reads_empty(cls):
    ds = cls().load([{"id": 1, "name": "A"}, {"id": 2, "name": "B"}])
    assert ds.count == 2
    ds.load([])  # empty load clears — same contract on both sources
    assert ds.count == 0
    assert ds.page(0) == []


def test_insert_works_after_empty_load():
    ds = SqliteDataSource().load([{"id": 1, "name": "A"}])
    ds.load([])
    rid = ds.insert({"id": 5, "name": "fresh"})
    assert ds.count == 1 and ds.get(rid)["name"] == "fresh"


def test_connection_usable_after_rolled_back_load():
    ds = SqliteDataSource().load([{"id": 1, "name": "A"}])

    def bad():
        yield {"id": 2, "name": "b", "obj": object()}

    with pytest.raises(SerializationError):
        ds.load(bad())

    # Isolation level was restored, so normal writes still work.
    ds.insert({"id": 2, "name": "B"})
    assert ds.count == 2
