"""Streaming record writers — the export counterpart of `readers`.

A *writer* consumes a lazy iterable of record dicts and writes them to a file,
streaming where the format allows so a large export does not materialize the
whole dataset. Writers are keyed by file extension in a registry: the stdlib
formats (CSV / TSV / JSON / JSONL / XML) are always available, and the optional
columnar/scientific formats (Parquet / Feather / HDF5) register too but raise a
clear "install the extra" error when used without their dependency.

The contract mirrors the readers — `writer(path, records, config) -> None` — so
it pairs with `read_records` for round-trips, and backs the source-level
`save()` / `export_csv()`.

Register a custom writer for your own extension::

    from bootstack.data.writers import register_writer

    @register_writer(".myfmt")
    def write_myfmt(path, records, config=None):
        with open(path, "w") as f:
            for record in records:
                f.write(serialize(record))
"""

from __future__ import annotations

import csv
import importlib
import json
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Dict, Iterable, List, Optional
from xml.sax.saxutils import escape as _xml_escape

from bootstack.data.types import Record

if TYPE_CHECKING:
    from bootstack.data.file_source import FileSourceConfig

# A writer consumes record dicts: (path, records, config) -> None.
Writer = Callable[..., None]

_WRITERS: Dict[str, Writer] = {}

# Format-name aliases (FileSourceConfig.file_format) → canonical extension.
_FORMAT_ALIASES: Dict[str, str] = {
    "csv": ".csv",
    "tsv": ".tsv",
    "json": ".json",
    "jsonl": ".jsonl",
    "ndjson": ".jsonl",
    "xml": ".xml",
    "parquet": ".parquet",
    "feather": ".feather",
    "hdf5": ".h5",
}


def _norm_ext(ext: str) -> str:
    ext = ext.lower()
    return ext if ext.startswith(".") else "." + ext


def register_writer(*extensions: str, writer: Optional[Writer] = None):
    """Register a writer for one or more file extensions (decorator or direct)."""

    def _apply(fn: Writer) -> Writer:
        for ext in extensions:
            _WRITERS[_norm_ext(ext)] = fn
        return fn

    return _apply(writer) if writer is not None else _apply


def supported_write_extensions() -> List[str]:
    """Return the sorted list of registered writer extensions."""
    return sorted(_WRITERS)


def get_writer(path_or_ext: "str | Path") -> Writer:
    """Resolve the writer for a path or extension.

    Raises:
        ValueError: If no writer is registered for the extension.
    """
    suffix = Path(str(path_or_ext)).suffix or str(path_or_ext)
    ext = _norm_ext(suffix)
    try:
        return _WRITERS[ext]
    except KeyError:
        raise ValueError(
            f"No writer registered for {ext!r}. Supported formats: "
            f"{', '.join(supported_write_extensions())}."
        ) from None


def write_records(
    path: "str | Path",
    records: "Iterable[Record]",
    config: "Optional[FileSourceConfig]" = None,
    *,
    format: Optional[str] = None,
) -> None:
    """Write records to a file, choosing the writer by `format` or extension.

    Args:
        path: Destination file path.
        records: An iterable of record dicts (consumed lazily).
        config: Optional formatting configuration (encoding, delimiter, …).
        format: Explicit format name overriding the path extension.
    """
    if format:
        writer = get_writer(_FORMAT_ALIASES.get(format, format))
    else:
        writer = get_writer(path)
    writer(path, records, config)


def _require(module: str, extra: str):
    """Import an optional dependency or raise a clear install hint."""
    try:
        return importlib.import_module(module)
    except ImportError as exc:
        raise ImportError(
            f"Writing this format needs the optional {module!r} dependency. "
            f"Install it with:  pip install bootstack[{extra}]"
        ) from exc


def _encoding(config: "Optional[FileSourceConfig]") -> str:
    return getattr(config, "encoding", "utf-8") or "utf-8"


# --------------------------------------------------------------------------- stdlib


@register_writer(".csv", ".tsv", ".txt")
def write_csv(path: "str | Path", records: "Iterable[Record]", config: "Optional[FileSourceConfig]" = None) -> None:
    """Write records to CSV/TSV, streaming a row at a time.

    Column headers are taken from the first record; later records are written with
    those columns (missing fields blank, extra fields ignored).
    """
    delimiter = getattr(config, "delimiter", None)
    if not delimiter:
        delimiter = "\t" if _norm_ext(Path(path).suffix) == ".tsv" else ","

    it = iter(records)
    try:
        first = next(it)
    except StopIteration:
        open(path, "w", encoding=_encoding(config)).close()  # empty export
        return

    fieldnames = list(first.keys())
    with open(path, "w", newline="", encoding=_encoding(config)) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter, extrasaction="ignore")
        writer.writeheader()
        writer.writerow(first)
        for record in it:
            writer.writerow(record)


@register_writer(".jsonl", ".ndjson")
def write_jsonl(path: "str | Path", records: "Iterable[Record]", config: "Optional[FileSourceConfig]" = None) -> None:
    """Write records as line-delimited JSON (one object per line) — fully streamed."""
    with open(path, "w", encoding=_encoding(config)) as f:
        for record in records:
            f.write(json.dumps(record))
            f.write("\n")


@register_writer(".json")
def write_json(path: "str | Path", records: "Iterable[Record]", config: "Optional[FileSourceConfig]" = None) -> None:
    """Write records as a JSON array, streamed element by element."""
    with open(path, "w", encoding=_encoding(config)) as f:
        f.write("[")
        first = True
        for record in records:
            if not first:
                f.write(", ")
            f.write(json.dumps(record))
            first = False
        f.write("]")


@register_writer(".xml")
def write_xml(path: "str | Path", records: "Iterable[Record]", config: "Optional[FileSourceConfig]" = None) -> None:
    """Write records as XML, streaming one record element at a time.

    Each record becomes a ``<record>`` element (or ``config.xml_record_tag``) whose
    child elements are the record's fields.
    """
    record_tag = getattr(config, "xml_record_tag", None) or "record"
    root_tag = "records"
    with open(path, "w", encoding=_encoding(config)) as f:
        f.write(f"<{root_tag}>")
        for record in records:
            f.write(f"<{record_tag}>")
            for key, value in record.items():
                text = "" if value is None else _xml_escape(str(value))
                f.write(f"<{key}>{text}</{key}>")
            f.write(f"</{record_tag}>")
        f.write(f"</{root_tag}>")


# --------------------------------------------------------------------------- optional


@register_writer(".parquet")
def write_parquet(path: "str | Path", records: "Iterable[Record]", config: "Optional[FileSourceConfig]" = None) -> None:
    """Write records to a Parquet file (needs pyarrow)."""
    pa = _require("pyarrow", "parquet")
    import pyarrow.parquet as pq

    pq.write_table(pa.Table.from_pylist(list(records)), str(path))


@register_writer(".feather", ".arrow")
def write_feather(path: "str | Path", records: "Iterable[Record]", config: "Optional[FileSourceConfig]" = None) -> None:
    """Write records to a Feather/Arrow IPC file (needs pyarrow)."""
    pa = _require("pyarrow", "parquet")
    import pyarrow.feather as feather

    feather.write_feather(pa.Table.from_pylist(list(records)), str(path))


@register_writer(".h5", ".hdf5", ".hdf")
def write_hdf5(path: "str | Path", records: "Iterable[Record]", config: "Optional[FileSourceConfig]" = None) -> None:
    """Write records to a tabular HDF5 file (needs pandas + tables)."""
    pd = _require("pandas", "hdf5")
    key = getattr(config, "hdf5_key", None) or "data"
    pd.DataFrame(list(records)).to_hdf(str(path), key=key, format="table")
