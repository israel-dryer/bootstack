"""Tests for FileDataSource — streaming file ingest into a SQLite working store.

FileDataSource reads a file and ingests it (a chunk at a time) into a SQLite
store, so after `load()` it behaves like a `SqliteDataSource`. The original file
is read-only input; the working store is a temp file by default (removed on
`close()`), a named persistent cache, or in-memory. Headless (no App).
"""
from __future__ import annotations

import os
import time
from pathlib import Path

import pytest

from bootstack.data import col, FileDataSource, FileSourceConfig


def _csv(tmp_path, text="id,name,age\n1,Ada,40\n2,Bob,25\n3,Cy,33\n"):
    p = tmp_path / "people.csv"
    p.write_text(text, encoding="utf-8")
    return p


def test_loads_and_queries_via_sql(tmp_path):
    ds = FileDataSource(_csv(tmp_path))
    ds.load()
    assert ds.count == 3
    ds.where(col("age") >= 33).order("-age")
    assert [r["name"] for r in ds.page(0)] == ["Ada", "Cy"]
    ds.close()


def test_default_store_is_temp_and_removed_on_close(tmp_path):
    ds = FileDataSource(_csv(tmp_path))
    ds.load()
    store = ds._store_name
    assert ds._is_temp and os.path.exists(store)
    ds.close()
    assert not os.path.exists(store)


def test_context_manager_cleans_up(tmp_path):
    with FileDataSource(_csv(tmp_path)) as ds:
        ds.load()
        assert ds.count == 3
        store = ds._store_name
    assert not os.path.exists(store)


def test_temp_store_cleaned_on_gc_without_close(tmp_path):
    # Safety net: a forgotten FileDataSource (never closed) still removes its temp
    # file when garbage collected — no orphaned files.
    import gc

    ds = FileDataSource(_csv(tmp_path))
    ds.load()
    store = ds._store_name
    assert os.path.exists(store)
    del ds
    gc.collect()
    assert not os.path.exists(store)


def test_close_is_idempotent_for_temp(tmp_path):
    ds = FileDataSource(_csv(tmp_path))
    ds.load()
    store = ds._store_name
    ds.close()
    ds.close()  # no error on a second close
    assert not os.path.exists(store)


def test_transform_pipeline(tmp_path):
    cfg = FileSourceConfig(column_renames={"name": "full_name"}, column_types={"age": int})
    ds = FileDataSource(_csv(tmp_path), cfg)
    ds.load()
    rec = ds.get(1)
    assert rec["full_name"] == "Ada"
    assert rec["age"] == 40 and isinstance(rec["age"], int)
    ds.close()


def test_row_filter(tmp_path):
    cfg = FileSourceConfig(row_filter=lambda r: int(r["age"]) >= 30)
    ds = FileDataSource(_csv(tmp_path), cfg)
    ds.load()
    assert sorted(r["name"] for r in ds.page(0)) == ["Ada", "Cy"]
    ds.close()


def test_jsonl_non_scalar_bag_roundtrips(tmp_path):
    p = tmp_path / "x.jsonl"
    p.write_text('{"id":1,"name":"A","tags":["x","y"]}\n{"id":2,"name":"B","tags":[]}\n', encoding="utf-8")
    ds = FileDataSource(p)
    ds.load()
    assert ds.get(1)["tags"] == ["x", "y"]
    ds.close()


def test_json_records_key(tmp_path):
    p = tmp_path / "api.json"
    p.write_text('{"data": [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]}', encoding="utf-8")
    ds = FileDataSource(p, FileSourceConfig(json_records_key="data"))
    ds.load()
    assert ds.count == 2 and ds.get(1)["name"] == "A"
    ds.close()


def test_memory_store(tmp_path):
    ds = FileDataSource(_csv(tmp_path), cache=":memory:")
    ds.load()
    assert ds.count == 3 and ds._store_name == ":memory:" and not ds._is_temp
    ds.close()


def test_named_cache_persists_and_skips_reingest(tmp_path):
    src = _csv(tmp_path)
    cache = tmp_path / "cache.db"

    first = FileDataSource(src, cache=str(cache))
    first.load()
    assert first.count == 3 and not first._is_temp
    first.close()
    assert cache.exists()

    # Reopen: a fresh cache is adopted without re-ingest.
    again = FileDataSource(src, cache=str(cache))
    assert again.is_loaded is True
    assert again.count == 3
    again.load()  # no-op while fresh
    assert again.count == 3
    again.close()


def test_named_cache_reingests_when_source_is_newer(tmp_path):
    src = _csv(tmp_path)
    cache = tmp_path / "cache.db"
    FileDataSource(src, cache=str(cache)).load()

    time.sleep(0.01)
    src.write_text("id,name,age\n1,Ada,40\n2,Bob,25\n3,Cy,33\n4,Dee,50\n", encoding="utf-8")
    os.utime(src, None)

    ds = FileDataSource(src, cache=str(cache))
    assert ds.is_loaded is False  # stale → not adopted
    ds.load()
    assert ds.count == 4
    ds.close()


def test_reload_reingests(tmp_path):
    ds = FileDataSource(_csv(tmp_path))
    ds.load()
    assert ds.count == 3
    ds.reload()
    assert ds.count == 3
    ds.close()


def test_progress_callback(tmp_path):
    rows = "\n".join(f"{i},n{i}" for i in range(2500))
    p = tmp_path / "big.csv"
    p.write_text("id,name\n" + rows + "\n", encoding="utf-8")
    seen = []
    cfg = FileSourceConfig(chunk_size=1000, progress_callback=seen.append)
    ds = FileDataSource(p, cfg)
    ds.load()
    assert seen == [1000, 2000, 2500]
    assert ds.count == 2500
    ds.close()


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        FileDataSource(tmp_path / "nope.csv")
