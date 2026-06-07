"""Tests for the streaming writer registry and source-level save()/export.

Writers consume a lazy iterable of records and write them out; they mirror the
readers, so write→read round-trips. `save()` streams a source's records (public
records, active view respected) into the writer chosen by extension. Headless.
"""
from __future__ import annotations

import importlib.util

import pytest

from bootstack.data import (
    MemoryDataSource,
    SqliteDataSource,
    get_writer,
    read_records,
    register_writer,
    supported_write_extensions,
    write_records,
)

ROWS = [{"id": 1, "name": "Ada", "tags": ["x"]}, {"id": 2, "name": "Bob", "tags": ["y", "z"]}]


def _has(module: str) -> bool:
    return importlib.util.find_spec(module) is not None


# --------------------------------------------------------------------------- registry


def test_supported_write_extensions():
    exts = supported_write_extensions()
    for e in (".csv", ".tsv", ".json", ".jsonl", ".xml", ".parquet", ".feather", ".h5"):
        assert e in exts


def test_unknown_extension_raises():
    with pytest.raises(ValueError, match="No writer registered"):
        get_writer("out.zzz")


def test_register_custom_writer(tmp_path):
    @register_writer(".upper")
    def _w(path, records, config=None):
        with open(path, "w", encoding="utf-8") as f:
            for r in records:
                f.write(str(r.get("name", "")).upper())

    p = tmp_path / "x.upper"
    write_records(p, iter([{"name": "ada"}]))
    assert p.read_text(encoding="utf-8") == "ADA"


# --------------------------------------------------------------------------- round-trips


@pytest.mark.parametrize("ext", [".csv", ".tsv", ".jsonl", ".json", ".xml"])
def test_roundtrip_count_and_names(tmp_path, ext):
    p = tmp_path / f"out{ext}"
    write_records(p, iter(ROWS))
    back = list(read_records(p))
    assert [r["name"] for r in back] == ["Ada", "Bob"]


@pytest.mark.parametrize("ext", [".jsonl", ".json"])
def test_json_formats_preserve_structure(tmp_path, ext):
    p = tmp_path / f"out{ext}"
    write_records(p, iter(ROWS))
    back = list(read_records(p))
    assert back[1]["tags"] == ["y", "z"]  # lists survive in JSON


def test_csv_stringifies_non_scalar(tmp_path):
    p = tmp_path / "out.csv"
    write_records(p, iter(ROWS))
    back = list(read_records(p))
    assert back[0]["tags"] == "['x']"  # flat text format → str


def test_empty_export_writes_a_file(tmp_path):
    p = tmp_path / "empty.csv"
    write_records(p, iter([]))
    assert p.exists()


def test_format_override(tmp_path):
    from bootstack.data import FileSourceConfig

    p = tmp_path / "data.dat"  # extension the registry doesn't know
    write_records(p, iter(ROWS), format="csv")  # forced CSV
    assert [r["name"] for r in read_records(p, FileSourceConfig(file_format="csv"))] == ["Ada", "Bob"]


# --------------------------------------------------------------------------- save() from a source


def test_save_streams_public_records(tmp_path):
    ds = SqliteDataSource().load(ROWS)
    p = tmp_path / "src.jsonl"
    ds.save(p)
    back = list(read_records(p))
    assert back[1]["tags"] == ["y", "z"]
    # internal bookkeeping never leaks into the export
    assert "_bs_row_id" not in back[0] and "selected" not in back[0]
    assert "id" in back[0]


def test_export_csv_strips_internal_fields(tmp_path):
    ds = SqliteDataSource().load(ROWS)
    p = tmp_path / "src.csv"
    ds.export_csv(str(p))
    header = p.read_text(encoding="utf-8").splitlines()[0]
    assert "_bs" not in header and "selected" not in header
    assert header.split(",")[:2] == ["id", "name"]


def test_save_selected_only(tmp_path):
    ds = SqliteDataSource().load(ROWS)
    ds.select(2)
    p = tmp_path / "sel.json"
    ds.save(p, selected_only=True)
    back = list(read_records(p))
    assert [r["id"] for r in back] == [2]


def test_save_respects_active_filter(tmp_path):
    from bootstack import col

    ds = SqliteDataSource().load(ROWS)
    ds.where(col("name") == "Bob")
    p = tmp_path / "filtered.jsonl"
    ds.save(p)
    back = list(read_records(p))
    assert [r["name"] for r in back] == ["Bob"]


def test_memory_source_save(tmp_path):
    ds = MemoryDataSource().load(ROWS)
    p = tmp_path / "mem.jsonl"
    ds.save(p)
    assert len(list(read_records(p))) == 2


def test_save_roundtrips_through_a_file_source(tmp_path):
    from bootstack.data import FileDataSource

    src = SqliteDataSource().load(ROWS)
    p = tmp_path / "dump.jsonl"
    src.save(p)
    fds = FileDataSource(p)
    fds.load()
    assert fds.count == 2
    assert fds.get(2)["tags"] == ["y", "z"]
    fds.close()


# --------------------------------------------------------------------------- optional formats


def test_parquet_without_dep_raises_install_hint(tmp_path):
    if _has("pyarrow"):
        pytest.skip("pyarrow installed — gating path not exercised")
    with pytest.raises(ImportError, match=r"bootstack\[parquet\]"):
        write_records(tmp_path / "x.parquet", iter(ROWS))


def test_hdf5_without_dep_raises_install_hint(tmp_path):
    if _has("pandas"):
        pytest.skip("pandas installed — gating path not exercised")
    with pytest.raises(ImportError, match=r"bootstack\[hdf5\]"):
        write_records(tmp_path / "x.h5", iter(ROWS))


@pytest.mark.skipif(not _has("pyarrow"), reason="needs pyarrow")
def test_parquet_roundtrip(tmp_path):
    p = tmp_path / "out.parquet"
    write_records(p, iter([{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]))
    assert [r["name"] for r in read_records(p)] == ["A", "B"]
