"""Tests for the unified data bag — undisplayed / non-scalar record fields.

A record should never lose user data: fields the widget does not display are
still carried through and handed back. Fidelity is tiered by storage:

- In-memory sources (``MemoryDataSource``) hold *anything*, including live Python
  objects, by reference.
- SQLite-backed sources (``SqliteDataSource``, and ``FileDataSource`` which
  ingests into SQLite) store non-scalar fields (lists/dicts) in a hidden JSON
  column that round-trips transparently. Values must be JSON-serializable; live
  objects raise ``SerializationError``.

These are headless (no App) — the data layer is App-independent.
"""
from __future__ import annotations

import json

import pytest

from bootstack import col
from bootstack.data import FileDataSource, MemoryDataSource, SqliteDataSource
from bootstack.errors import SerializationError


# ---------------------------------------------------------------------------
# Cross-source: undisplayed scalar fields are never dropped
# ---------------------------------------------------------------------------

ALL_SOURCES = [MemoryDataSource, SqliteDataSource]


@pytest.mark.parametrize("cls", ALL_SOURCES)
def test_undisplayed_scalar_field_survives(cls):
    ds = cls().load([{"id": 1, "name": "Alice", "secret": 42}])
    rec = ds.get(1)
    assert rec["name"] == "Alice"
    assert rec["secret"] == 42  # not a "display" field, still carried


@pytest.mark.parametrize("cls", ALL_SOURCES)
def test_nonscalar_fields_roundtrip(cls):
    ds = cls().load(
        [
            {"id": 1, "name": "Alice", "tags": ["vip", "beta"], "meta": {"score": 9}},
            {"id": 2, "name": "Bob", "tags": [], "meta": {"score": 3}},
        ]
    )
    rec = ds.get(1)
    assert rec["tags"] == ["vip", "beta"]
    assert rec["meta"] == {"score": 9}

    # And through paging / index slicing.
    page = ds.page(0)
    assert page[0]["tags"] == ["vip", "beta"]
    sliced = ds.page_slice(0, 2)
    assert sliced[1]["meta"] == {"score": 3}


@pytest.mark.parametrize("cls", ALL_SOURCES)
def test_public_record_keeps_bag_strips_internals(cls):
    ds = cls().load([{"id": 7, "name": "Alice", "tags": ["x"]}])
    raw = ds.get(7)
    pub = ds._public_record(raw)
    assert pub["id"] == 7
    assert pub["name"] == "Alice"
    assert pub["tags"] == ["x"]
    # No bookkeeping leaks into the public-facing record.
    for f in ds._internal_fields():
        assert f not in pub


@pytest.mark.parametrize("cls", ALL_SOURCES)
def test_scalar_fields_stay_queryable_with_bag_present(cls):
    ds = cls().load(
        [
            {"id": 1, "name": "Alice", "age": 30, "tags": ["a"]},
            {"id": 2, "name": "Bob", "age": 20, "tags": ["b"]},
            {"id": 3, "name": "Carol", "age": 40, "tags": ["c"]},
        ]
    )
    ds.where(col("age") >= 30).order("-age")
    rows = ds.page(0)
    assert [r["name"] for r in rows] == ["Carol", "Alice"]
    # The bag rode along through the filtered/sorted read.
    assert rows[0]["tags"] == ["c"]


@pytest.mark.parametrize("cls", ALL_SOURCES)
def test_insert_with_nonscalar(cls):
    ds = cls().load([{"id": 1, "name": "Alice", "tags": ["x"]}])
    rid = ds.insert({"name": "Bob", "tags": ["y", "z"], "meta": {"k": 1}})
    rec = ds.get(rid)
    assert rec["tags"] == ["y", "z"]
    assert rec["meta"] == {"k": 1}


@pytest.mark.parametrize("cls", ALL_SOURCES)
def test_update_bag_field(cls):
    ds = cls().load([{"id": 1, "name": "Alice", "tags": ["x"], "meta": {"k": 1}}])
    assert ds.update(1, {"tags": ["x", "y"]}) is True
    assert ds.get(1)["tags"] == ["x", "y"]
    # An untouched bag field is preserved across the update.
    assert ds.get(1)["meta"] == {"k": 1}


@pytest.mark.parametrize("cls", ALL_SOURCES)
def test_update_scalar_preserves_bag(cls):
    ds = cls().load([{"id": 1, "name": "Alice", "tags": ["x"]}])
    assert ds.update(1, {"name": "Alice B."}) is True
    rec = ds.get(1)
    assert rec["name"] == "Alice B."
    assert rec["tags"] == ["x"]


@pytest.mark.parametrize("cls", ALL_SOURCES)
def test_selected_records_carry_bag(cls):
    ds = cls().load(
        [
            {"id": 1, "name": "Alice", "tags": ["x"]},
            {"id": 2, "name": "Bob", "tags": ["y"]},
        ]
    )
    ds.select(2)
    sel = ds.selected()
    assert len(sel) == 1
    assert sel[0]["tags"] == ["y"]


# ---------------------------------------------------------------------------
# SqliteDataSource specifics — JSON storage, scalar columns, error contract
# ---------------------------------------------------------------------------


def test_sqlite_scalar_stays_real_column():
    ds = SqliteDataSource()
    ds.load([{"id": 1, "name": "Alice", "tags": ["x"]}])
    # A scalar field is a real column (filterable); the non-scalar one is bagged.
    cols = ds._user_column_fields
    assert "name" in cols
    assert "tags" not in cols


def test_sqlite_stores_bag_as_json_blob():
    ds = SqliteDataSource()
    ds.load([{"id": 1, "name": "Alice", "tags": ["x", "y"]}])
    blob = ds.conn.execute("SELECT _bs_data FROM records WHERE _bs_row_id = 1").fetchone()[0]
    assert json.loads(blob) == {"tags": ["x", "y"]}


def test_sqlite_extra_scalar_key_after_load_is_bagged():
    # A scalar key absent from the schema-defining first row has no column, so it
    # rides the bag rather than being dropped.
    ds = SqliteDataSource()
    ds.load([{"id": 1, "name": "Alice"}])
    rid = ds.insert({"name": "Bob", "nickname": "Bobby"})
    assert ds.get(rid)["nickname"] == "Bobby"


def test_sqlite_live_object_raises_serialization_error():
    class Widget:
        pass

    ds = SqliteDataSource()
    with pytest.raises(SerializationError):
        ds.load([{"id": 1, "name": "Alice", "obj": Widget()}])


def test_sqlite_insert_live_object_raises_serialization_error():
    class Widget:
        pass

    ds = SqliteDataSource().load([{"id": 1, "name": "Alice", "tags": ["x"]}])
    with pytest.raises(SerializationError):
        ds.insert({"name": "Bob", "obj": Widget()})


# ---------------------------------------------------------------------------
# In-memory fidelity — live objects by reference
# ---------------------------------------------------------------------------


def test_memory_carries_live_object_by_reference():
    class Widget:
        pass

    obj = Widget()
    ds = MemoryDataSource().load([{"id": 1, "name": "Alice", "obj": obj}])
    assert ds.get(1)["obj"] is obj
    assert ds._public_record(ds.get(1))["obj"] is obj


def test_file_source_carries_lists_and_dicts(tmp_path):
    path = tmp_path / "data.json"
    path.write_text(
        json.dumps([{"id": 1, "name": "Alice", "tags": ["x", "y"], "meta": {"k": 1}}]),
        encoding="utf-8",
    )
    ds = FileDataSource(str(path))
    ds.load()
    rec = ds.get(1)
    assert rec["tags"] == ["x", "y"]
    assert rec["meta"] == {"k": 1}
