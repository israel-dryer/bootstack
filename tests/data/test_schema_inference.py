"""Tests for SqliteDataSource column-type (affinity) inference.

`load()` samples the leading rows to pick each column's SQL type, so a leading
NULL no longer forces TEXT affinity on an otherwise-numeric column (which would
silently store its integers as strings). These are headless (no App).
"""
from __future__ import annotations

from bootstack.data import SqliteDataSource
from bootstack.data.query import col


def _affinity(ds: SqliteDataSource, column: str) -> str:
    rows = ds.conn.execute(f"PRAGMA table_info({ds._table})").fetchall()
    for r in rows:
        # PRAGMA table_info columns: (cid, name, type, notnull, dflt, pk)
        name, ctype = r[1], r[2]
        if name == column:
            return ctype
    raise AssertionError(f"no column {column!r}")


def test_leading_null_does_not_force_text_affinity():
    # parent_id is None in the first row but integer afterwards.
    ds = SqliteDataSource().load([
        {"id": 1, "parent_id": None, "name": "root"},
        {"id": 2, "parent_id": 1, "name": "child"},
        {"id": 3, "parent_id": 1, "name": "child2"},
    ])
    assert _affinity(ds, "parent_id") == "INTEGER"
    # Values read back as ints, not strings — this is what broke tree backing.
    kids = ds._query(col("parent_id") == 1, [])
    assert [r["parent_id"] for r in kids] == [1, 1]
    assert all(isinstance(r["parent_id"], int) for r in kids)


def test_all_null_column_falls_back_to_text():
    ds = SqliteDataSource().load([
        {"id": 1, "note": None},
        {"id": 2, "note": None},
    ])
    assert _affinity(ds, "note") == "TEXT"


def test_integer_and_real_promote_to_real():
    ds = SqliteDataSource().load([
        {"id": 1, "amount": None},
        {"id": 2, "amount": 5},
        {"id": 3, "amount": 2.5},
    ])
    assert _affinity(ds, "amount") == "REAL"


def test_mixed_numeric_and_text_falls_back_to_text():
    ds = SqliteDataSource().load([
        {"id": 1, "code": None},
        {"id": 2, "code": 10},
        {"id": 3, "code": "A-12"},
    ])
    assert _affinity(ds, "code") == "TEXT"


def test_pure_integer_column_stays_integer():
    ds = SqliteDataSource().load([
        {"id": 1, "qty": 4},
        {"id": 2, "qty": 7},
    ])
    assert _affinity(ds, "qty") == "INTEGER"


def test_string_id_still_typed_text():
    ds = SqliteDataSource().load([
        {"id": "a1b2", "name": "x"},
        {"id": "c3d4", "name": "y"},
    ])
    assert _affinity(ds, "_bs_row_id") == "TEXT"


def test_sampling_is_bounded_but_covers_leading_run(monkeypatch):
    # Only the leading sample window is scanned; a column whose values are all
    # None within the sample types as TEXT. Use a tiny window to assert the bound.
    import bootstack.data.sqlite_source as mod

    monkeypatch.setattr(mod, "_SCHEMA_SAMPLE_SIZE", 2)
    rows = [{"id": i, "late": None} for i in range(2)]
    rows += [{"id": i, "late": i} for i in range(2, 6)]
    ds = SqliteDataSource().load(rows, chunk_size=10)
    # All sampled values were None -> TEXT (documented sampling bound).
    assert _affinity(ds, "late") == "TEXT"
    # But every row is still inserted and readable.
    assert ds.count == 6


def test_chunk_smaller_than_sample_still_infers_and_inserts_all():
    # chunk_size below the sample size must not drop rows or mis-type.
    rows = [{"id": 1, "parent_id": None, "name": "r"}]
    rows += [{"id": i, "parent_id": 1, "name": f"c{i}"} for i in range(2, 12)]
    ds = SqliteDataSource().load(rows, chunk_size=3)
    assert _affinity(ds, "parent_id") == "INTEGER"
    assert ds.count == 11
