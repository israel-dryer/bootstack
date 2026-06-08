"""Tests for the streaming file-reader registry.

Readers turn a file into a lazy iterator of record dicts, keyed by extension.
Stdlib formats (CSV/TSV/JSON/JSONL/XML) are always available and fully tested
here; the optional columnar/scientific formats are tested only when their
dependency is installed, and their "install the extra" error is always checked.
These are headless (no App).
"""
from __future__ import annotations

import importlib.util
import json

import pytest

from bootstack.data import (
    FileSourceConfig,
    SqliteDataSource,
    get_reader,
    read_records,
    register_reader,
    supported_read_extensions,
)


def _has(module: str) -> bool:
    return importlib.util.find_spec(module) is not None


# --------------------------------------------------------------------------- registry


def test_supported_extensions_includes_stdlib_and_optional():
    exts = supported_read_extensions()
    for e in (".csv", ".tsv", ".txt", ".json", ".jsonl", ".ndjson", ".xml",
              ".parquet", ".feather", ".h5"):
        assert e in exts


def test_get_reader_resolves_by_path_and_bare_ext():
    assert get_reader("data.csv") is get_reader(".csv") is get_reader("csv")


def test_unknown_extension_raises():
    with pytest.raises(ValueError, match="No reader registered"):
        get_reader("data.nope")


def test_register_custom_reader(tmp_path):
    @register_reader(".demo")
    def _read_demo(path, config):
        yield {"from": "demo"}

    p = tmp_path / "x.demo"
    p.write_text("ignored", encoding="utf-8")
    assert list(read_records(p)) == [{"from": "demo"}]


# --------------------------------------------------------------------------- csv / tsv


def test_csv(tmp_path):
    p = tmp_path / "p.csv"
    p.write_text("id,name\n1,Alice\n2,Bob\n", encoding="utf-8")
    assert list(read_records(p)) == [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
    ]


def test_tsv_uses_tab_by_default(tmp_path):
    p = tmp_path / "p.tsv"
    p.write_text("id\tname\n1\tAlice\n", encoding="utf-8")
    assert list(read_records(p))[0] == {"id": "1", "name": "Alice"}


def test_csv_skip_rows(tmp_path):
    p = tmp_path / "p.csv"
    p.write_text("# preamble\nid,name\n1,Alice\n", encoding="utf-8")
    rows = list(read_records(p, FileSourceConfig(skip_rows=1)))
    assert rows == [{"id": "1", "name": "Alice"}]


# --------------------------------------------------------------------------- json


def test_jsonl(tmp_path):
    p = tmp_path / "p.jsonl"
    p.write_text('{"id":1,"tags":["a"]}\n\n{"id":2}\n', encoding="utf-8")
    rows = list(read_records(p))
    assert rows == [{"id": 1, "tags": ["a"]}, {"id": 2}]


def test_json_array(tmp_path):
    p = tmp_path / "p.json"
    p.write_text(json.dumps([{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]), encoding="utf-8")
    assert [r["name"] for r in read_records(p)] == ["A", "B"]


def test_json_records_key(tmp_path):
    # Records nested under a key (e.g. an API response) — opt in explicitly.
    p = tmp_path / "p.json"
    p.write_text(json.dumps({"data": [{"id": 9}, {"id": 10}]}), encoding="utf-8")
    rows = list(read_records(p, FileSourceConfig(json_records_key="data")))
    assert rows == [{"id": 9}, {"id": 10}]


def test_json_records_key_must_resolve_to_a_list(tmp_path):
    p = tmp_path / "p.json"
    p.write_text(json.dumps({"data": "oops"}), encoding="utf-8")
    with pytest.raises(ValueError, match="json_records_key"):
        list(read_records(p, FileSourceConfig(json_records_key="data")))


def test_json_single_object(tmp_path):
    p = tmp_path / "p.json"
    p.write_text(json.dumps({"id": 1, "name": "solo"}), encoding="utf-8")
    assert list(read_records(p)) == [{"id": 1, "name": "solo"}]


def test_json_no_magic_records_key(tmp_path):
    # Without json_records_key, an object is one record — no implicit "records"
    # sniffing (explicit beats magic).
    p = tmp_path / "p.json"
    p.write_text(json.dumps({"records": [{"id": 9}]}), encoding="utf-8")
    assert list(read_records(p)) == [{"records": [{"id": 9}]}]


# --------------------------------------------------------------------------- xml


def test_xml_default_record_is_root_child(tmp_path):
    p = tmp_path / "p.xml"
    p.write_text(
        '<rows><row id="1"><name>Alice</name></row>'
        '<row id="2"><name>Bob</name></row></rows>',
        encoding="utf-8",
    )
    assert list(read_records(p)) == [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
    ]


def test_xml_explicit_record_tag(tmp_path):
    p = tmp_path / "p.xml"
    p.write_text(
        "<doc><group><item><k>v1</k></item><item><k>v2</k></item></group></doc>",
        encoding="utf-8",
    )
    rows = list(read_records(p, FileSourceConfig(xml_record_tag="item")))
    assert rows == [{"k": "v1"}, {"k": "v2"}]


# --------------------------------------------------------------------------- format override / integration


def test_file_format_overrides_extension(tmp_path):
    p = tmp_path / "data.dat"
    p.write_text("a,b\n1,2\n", encoding="utf-8")
    rows = list(read_records(p, FileSourceConfig(file_format="csv")))
    assert rows == [{"a": "1", "b": "2"}]


def test_reader_streams_into_sqlite_load(tmp_path):
    p = tmp_path / "p.jsonl"
    p.write_text('{"id":1,"tags":["a"]}\n{"id":2,"tags":["b"]}\n', encoding="utf-8")
    ds = SqliteDataSource().load(read_records(p), chunk_size=1)
    assert ds.count == 2
    assert ds.get(1)["tags"] == ["a"]  # bag survives the file → source path


# --------------------------------------------------------------------------- optional formats


def test_parquet_without_dep_raises_install_hint(tmp_path):
    if _has("pyarrow"):
        pytest.skip("pyarrow installed — gating path not exercised")
    p = tmp_path / "x.parquet"
    p.write_text("", encoding="utf-8")
    with pytest.raises(ImportError, match=r"bootstack\[parquet\]"):
        list(read_records(p))


def test_hdf5_without_dep_raises_install_hint(tmp_path):
    if _has("pandas"):
        pytest.skip("pandas installed — gating path not exercised")
    p = tmp_path / "x.h5"
    p.write_text("", encoding="utf-8")
    with pytest.raises(ImportError, match=r"bootstack\[hdf5\]"):
        list(read_records(p))


@pytest.mark.skipif(not _has("pyarrow"), reason="needs pyarrow")
def test_parquet_roundtrip(tmp_path):
    import pyarrow as pa
    import pyarrow.parquet as pq

    p = tmp_path / "p.parquet"
    pq.write_table(pa.table({"id": [1, 2], "name": ["A", "B"]}), str(p))
    rows = list(read_records(p))
    assert [r["name"] for r in rows] == ["A", "B"]


@pytest.mark.skipif(not _has("pyarrow"), reason="needs pyarrow")
def test_feather_roundtrip(tmp_path):
    import pyarrow as pa
    import pyarrow.feather as feather

    p = tmp_path / "p.feather"
    feather.write_feather(pa.table({"id": [1, 2], "name": ["A", "B"]}), str(p))
    rows = list(read_records(p))
    assert [r["name"] for r in rows] == ["A", "B"]


@pytest.mark.skipif(not (_has("pandas") and _has("tables")), reason="needs pandas + tables")
def test_hdf5_roundtrip(tmp_path):
    import pandas as pd

    p = tmp_path / "p.h5"
    pd.DataFrame({"id": [1, 2], "name": ["A", "B"]}).to_hdf(str(p), key="data", format="table")
    rows = list(read_records(p, FileSourceConfig(hdf5_key="data")))
    assert [r["name"] for r in rows] == ["A", "B"]
