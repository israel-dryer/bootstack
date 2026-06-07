"""Streaming record readers for file-backed data sources.

A *reader* turns a file into a lazy iterator of record dicts, parsed a row at a
time so large files stream with bounded memory rather than loading all at once.
Readers are keyed by file extension in a registry: the stdlib formats
(CSV / TSV / JSON / JSONL / XML) are always available, and the optional columnar
and scientific formats (Parquet / Feather / HDF5) register too but raise a clear
"install the extra" error when used without their dependency.

The reader contract is intentionally small — `reader(path, config) ->
Iterator[Record]` — so it composes directly with the streaming
`SqliteDataSource.load(...)`, which chunks the iterator itself.

Register a custom reader for your own extension::

    from bootstack.data.readers import register_reader

    @register_reader(".myfmt")
    def read_myfmt(path, config):
        for record in parse(path):
            yield record
"""

from __future__ import annotations

import csv
import importlib
import json
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Dict, Iterator, List, Optional

from bootstack.data.types import Record

if TYPE_CHECKING:
    from bootstack.data.file_source import FileSourceConfig

# A reader yields record dicts lazily: (path, config) -> Iterator[Record].
Reader = Callable[..., Iterator[Record]]

_READERS: Dict[str, Reader] = {}

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
    """Normalize an extension to lowercase with a leading dot."""
    ext = ext.lower()
    return ext if ext.startswith(".") else "." + ext


def register_reader(*extensions: str, reader: Optional[Reader] = None):
    """Register a reader for one or more file extensions.

    Use as a decorator (`@register_reader(".csv", ".tsv")`) or call directly with
    `reader=`. Extensions may be given with or without the leading dot.

    Args:
        extensions: File extensions the reader handles.
        reader: The reader callable, when not used as a decorator.

    Returns:
        The reader (so it works as a decorator).
    """

    def _apply(fn: Reader) -> Reader:
        for ext in extensions:
            _READERS[_norm_ext(ext)] = fn
        return fn

    return _apply(reader) if reader is not None else _apply


def supported_extensions() -> List[str]:
    """Return the sorted list of registered file extensions."""
    return sorted(_READERS)


def get_reader(path_or_ext: "str | Path") -> Reader:
    """Resolve the reader for a path or extension.

    Args:
        path_or_ext: A file path or a bare extension (e.g. `".csv"` or `"csv"`).

    Returns:
        The registered reader callable.

    Raises:
        ValueError: If no reader is registered for the extension.
    """
    suffix = Path(str(path_or_ext)).suffix or str(path_or_ext)
    ext = _norm_ext(suffix)
    try:
        return _READERS[ext]
    except KeyError:
        raise ValueError(
            f"No reader registered for {ext!r}. Supported formats: "
            f"{', '.join(supported_extensions())}."
        ) from None


def read_records(path: "str | Path", config: "Optional[FileSourceConfig]" = None) -> Iterator[Record]:
    """Stream records from a file, choosing the reader by format or extension.

    Honors `config.file_format` when set to something other than `'auto'`,
    otherwise resolves the reader from the path's extension.

    Args:
        path: Path to the data file.
        config: Parsing configuration (a default `FileSourceConfig` is used if
            omitted).

    Returns:
        A lazy iterator of record dicts.
    """
    from bootstack.data.file_source import FileSourceConfig

    cfg = config or FileSourceConfig()
    fmt = getattr(cfg, "file_format", "auto")
    if fmt and fmt != "auto":
        reader = get_reader(_FORMAT_ALIASES.get(fmt, fmt))
    else:
        reader = get_reader(path)
    return reader(path, cfg)


def _require(module: str, extra: str):
    """Import an optional dependency or raise a clear install hint."""
    try:
        return importlib.import_module(module)
    except ImportError as exc:
        raise ImportError(
            f"Reading this format needs the optional {module!r} dependency. "
            f"Install it with:  pip install bootstack[{extra}]"
        ) from exc


# --------------------------------------------------------------------------- stdlib


@register_reader(".csv", ".tsv", ".txt")
def read_csv(path: "str | Path", config: "FileSourceConfig") -> Iterator[Record]:
    """Stream records from a CSV/TSV file, one row at a time."""
    delimiter = config.delimiter
    if delimiter is None:
        delimiter = "\t" if _norm_ext(Path(path).suffix) == ".tsv" else ","
    with open(path, "r", encoding=config.encoding, newline="") as f:
        for _ in range(config.skip_rows or 0):
            next(f, None)
        reader = csv.DictReader(f, delimiter=delimiter, quotechar=config.quotechar)
        for row in reader:
            yield dict(row)


@register_reader(".jsonl", ".ndjson")
def read_jsonl(path: "str | Path", config: "FileSourceConfig") -> Iterator[Record]:
    """Stream records from a line-delimited JSON file (one object per line)."""
    with open(path, "r", encoding=config.encoding) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            yield obj if isinstance(obj, dict) else {"value": obj}


@register_reader(".json")
def read_json(path: "str | Path", config: "FileSourceConfig") -> Iterator[Record]:
    """Read records from a JSON file.

    Supported shapes:

    - a top-level **array of objects** → one record per element;
    - a top-level **object** with its records under `config.json_records_key`
      (e.g. an API response like `{"data": [...]}`) → that list;
    - any other top-level **object** → a single record.

    A JSON array is parsed in full — the stdlib parser cannot stream an array, so
    prefer JSONL / `.ndjson` (or set `config.json_lines`) for very large data.
    """
    if getattr(config, "json_lines", False):
        yield from read_jsonl(path, config)
        return
    with open(path, "r", encoding=config.encoding) as f:
        data = json.load(f)

    key = getattr(config, "json_records_key", None)
    if key is not None:
        items = data.get(key) if isinstance(data, dict) else None
        if not isinstance(items, list):
            raise ValueError(
                f"json_records_key={key!r} did not resolve to a list of records in {path}."
            )
        for item in items:
            yield item if isinstance(item, dict) else {"value": item}
        return

    if isinstance(data, list):
        for item in data:
            yield item if isinstance(item, dict) else {"value": item}
    elif isinstance(data, dict):
        yield data


@register_reader(".xml")
def read_xml(path: "str | Path", config: "FileSourceConfig") -> Iterator[Record]:
    """Stream records from an XML file using incremental parsing.

    Each record element (those matching `config.xml_record_tag`, or the direct
    children of the root when it is unset) becomes one record: its attributes and
    the text of its leaf child elements become fields. Parsed elements are cleared
    so memory stays bounded. Nested/repeated children are skipped in this version.
    """
    import xml.etree.ElementTree as ET

    record_tag = getattr(config, "xml_record_tag", None)
    depth = 0
    root = None
    for event, elem in ET.iterparse(path, events=("start", "end")):
        if event == "start":
            if depth == 0:
                root = elem
            depth += 1
            continue
        # end event
        depth -= 1
        is_record = (elem.tag == record_tag) if record_tag else (depth == 1)
        if not is_record:
            continue
        record: Record = dict(elem.attrib)
        for child in elem:
            if len(child) == 0:  # leaf element → a scalar field
                record[child.tag] = child.text
        yield record
        elem.clear()
        if root is not None:
            root.clear()  # drop processed siblings to keep memory bounded


# --------------------------------------------------------------------------- optional


@register_reader(".parquet")
def read_parquet(path: "str | Path", config: "FileSourceConfig") -> Iterator[Record]:
    """Stream records from a Parquet file in row-group batches (needs pyarrow)."""
    pq = _require("pyarrow.parquet", "parquet")
    parquet_file = pq.ParquetFile(str(path))
    for batch in parquet_file.iter_batches():
        for row in batch.to_pylist():
            yield row


@register_reader(".feather", ".arrow")
def read_feather(path: "str | Path", config: "FileSourceConfig") -> Iterator[Record]:
    """Stream records from a Feather/Arrow IPC file in batches (needs pyarrow)."""
    feather = _require("pyarrow.feather", "parquet")
    table = feather.read_table(str(path))
    for batch in table.to_batches():
        for row in batch.to_pylist():
            yield row


@register_reader(".h5", ".hdf5", ".hdf")
def read_hdf5(path: "str | Path", config: "FileSourceConfig") -> Iterator[Record]:
    """Stream records from a tabular HDF5 file in chunks (needs pandas + tables)."""
    pd = _require("pandas", "hdf5")
    key = getattr(config, "hdf5_key", None)
    store = pd.HDFStore(str(path), mode="r")
    try:
        if key is None:
            keys = store.keys()
            if not keys:
                return
            key = keys[0]
        for chunk in store.select(key, chunksize=10_000):
            for record in chunk.to_dict(orient="records"):
                yield record
    finally:
        store.close()
