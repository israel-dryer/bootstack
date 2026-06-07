"""File-backed data source — streams a file into a SQLite working store.

`FileDataSource` reads CSV / TSV / JSON / JSONL (and, with the optional extras,
Parquet / Feather / HDF5) and ingests it — a chunk at a time, with bounded
memory — into a SQLite working store. After loading it *is* a
`SqliteDataSource`, so paging, filtering, sorting, and CRUD are all fast SQL at
flat memory, no matter how large the file.

The original file is treated as **read-only input**: edits live in the working
store, never written back. Save changes by exporting to a new file.

Working store (where the ingested data lives):
    - default: a temporary on-disk SQLite file, removed on `close()` — bounded
      memory even for millions of rows.
    - ``cache="path.db"``: a named, persistent store. Edits survive restarts, and
      re-opening skips re-ingest while the cache is newer than the source file.
    - ``cache=":memory:"``: an in-memory store — compact, but RAM-bound.

Transformation pipeline (applied per record during ingest):
    column selection / renames / default values / type conversions / per-column
    transforms / row filter / row transform.

Example:
    .. code-block:: python

        ds = FileDataSource("data.csv")
        ds.load()
        ds.where(col("age") > 25)
        first = ds.page(0)
        ds.close()          # or use `with FileDataSource(...) as ds:`
"""

from __future__ import annotations

import os
import sqlite3
import tempfile
import weakref
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Literal, Optional

from bootstack.data.sqlite_source import SqliteDataSource
from bootstack.data.types import Record


def _cleanup_temp_store(conn: "sqlite3.Connection", path: str) -> None:
    """Close the connection and remove a temporary working-store file.

    Registered as a `weakref.finalize` callback so a `FileDataSource` whose
    `close()` was never called still cleans up its temp file when garbage
    collected or at interpreter exit — no orphaned files left behind. Takes the
    connection and path directly (never the source) so it holds no strong
    reference that would keep the source alive.
    """
    try:
        conn.close()
    except Exception:
        pass
    try:
        os.remove(path)
    except OSError:
        pass


@dataclass
class FileSourceConfig:
    """Configuration for file parsing and the per-record transformation pipeline.

    Attributes:
        file_format: Format override; auto-detected from the extension if 'auto'.
        encoding: Character encoding for reading the file.
        delimiter: Field separator (None = auto: ',' for CSV, tab for TSV).
        quotechar: Quote character for fields containing the delimiter.
        skip_rows: Number of leading rows to skip before the header (CSV/TSV).
        header_row: Row index containing column names (None = no header).
        has_header: Whether the first row contains column names.
        json_lines: True for line-delimited JSON (JSONL/NDJSON).
        json_records_key: Key whose value is the records list in a JSON object
            (e.g. "data" for {"data": [...]}); None = a top-level array, or the
            object itself as one record.
        xml_record_tag: Element tag that marks one record (None = direct children of the root).
        hdf5_key: Dataset/table key to read from an HDF5 file (None = the first key).
        column_renames: Map {old_name: new_name} for renaming columns.
        column_types: Map {column: type} for type conversions.
        column_transforms: Map {column: func} for custom transformations.
        columns_to_load: List of columns to keep (None = all columns).
        default_values: Map {column: value} for missing/null values.
        row_filter: Function(row_dict) -> bool to filter rows during load.
        row_transform: Function(row_dict) -> row_dict for row-level transforms.
        chunk_size: Rows ingested per batch (bounds memory during load).
        progress_callback: Function(count) called after each ingested chunk with
            the running total of rows loaded so far.

    Example:
        .. code-block:: python

            config = FileSourceConfig(
                column_renames={'emp_id': 'id'},
                column_types={'age': int},
            )

    """

    file_format: Literal[
        'auto', 'csv', 'tsv', 'json', 'jsonl', 'ndjson', 'xml', 'parquet', 'feather', 'hdf5'
    ] = 'auto'
    encoding: str = 'utf-8'
    delimiter: Optional[str] = None
    quotechar: str = '"'
    skip_rows: int = 0
    header_row: Optional[int] = 0
    has_header: bool = True
    json_lines: bool = False
    json_records_key: Optional[str] = None
    xml_record_tag: Optional[str] = None
    hdf5_key: Optional[str] = None
    column_renames: Optional[Dict[str, str]] = None
    column_types: Optional[Dict[str, type]] = None
    column_transforms: Optional[Dict[str, Callable[[Any], Any]]] = None
    columns_to_load: Optional[List[str]] = None
    default_values: Optional[Dict[str, Any]] = None
    row_filter: Optional[Callable[[Dict[str, Any]], bool]] = None
    row_transform: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
    chunk_size: int = 10_000
    progress_callback: Optional[Callable[[int], None]] = None


class FileDataSource(SqliteDataSource):
    """A `SqliteDataSource` whose data is streamed in from a file.

    Reads a CSV / TSV / JSON / JSONL file (or an optional Parquet / Feather /
    HDF5 file) and ingests it chunk-by-chunk into a SQLite working store, so even
    a multi-million-row file loads with bounded memory. Once loaded it behaves
    exactly like a `SqliteDataSource` — fast SQL paging, filtering, sorting, CRUD.

    The original file is read-only input; edits live in the working store and are
    never written back. Export to save changes.

    Args:
        filepath: Path to the data file.
        config: Optional `FileSourceConfig` for parsing and transforms.
        page_size: Number of records returned per page.
        cache: Working store location. None (default) uses a temporary on-disk
            file removed on `close()`. A path names a persistent store whose data
            survives restarts (and is reused without re-ingest while it is newer
            than the source). ``":memory:"`` keeps the store in memory.
        id_field: Record field used as the stable row identity.

    Attributes:
        filepath: Path to the data file.
        config: Active configuration.
        is_loaded: Whether the file has been ingested (or a fresh cache adopted).

    Example:
        .. code-block:: python

            with FileDataSource("people.csv") as ds:
                ds.load()
                ds.where(col("age") > 25)
                first = ds.page(0)

    Note:
        - `reload()` re-ingests from the file.
        - Background-thread ingest and progressive display are a planned follow-up;
          `load()` is currently synchronous (but streamed, so memory stays bounded).
    """

    def __init__(
        self,
        filepath: str | Path,
        config: Optional[FileSourceConfig] = None,
        page_size: int = 10,
        *,
        cache: Optional[str] = None,
        id_field: str = "id",
    ):
        """Configure a file-backed source and open its SQLite working store.

        Raises:
            FileNotFoundError: If the supplied file path cannot be found.
        """
        self.filepath = Path(filepath)
        self.config = config or FileSourceConfig()
        if not self.filepath.exists():
            raise FileNotFoundError(f"File not found: {self.filepath}")

        # Choose the working store.
        self._is_temp = False
        self._cache_path: Optional[Path] = None
        if cache is None:
            fd, tmp = tempfile.mkstemp(suffix=".bsdb")
            os.close(fd)
            store_name = tmp
            self._is_temp = True
        elif cache == ":memory:":
            store_name = ":memory:"
        else:
            store_name = str(cache)
            self._cache_path = Path(cache)
        self._store_name = store_name

        super().__init__(name=store_name, page_size=page_size, id_field=id_field)

        # Safety net: a temp store is removed even if close() is never called —
        # the finalizer runs on garbage collection and at interpreter exit, so no
        # orphaned temp files accumulate.
        self._finalizer: Optional[weakref.finalize] = None
        if self._is_temp:
            self._finalizer = weakref.finalize(
                self, _cleanup_temp_store, self.conn, store_name
            )

        # Reuse a fresh persistent cache without re-ingesting.
        self.is_loaded = False
        if self._cache_is_fresh():
            self._adopt_existing_schema()
            self.is_loaded = True

    # ------------------------------------------------------------------ loading

    def load(self, *, force: bool = False) -> "FileDataSource":
        """Ingest the file into the working store (streamed, in chunks).

        Unlike other sources, a `FileDataSource` draws its records from the file
        given at construction, so `load()` takes no records. It is a no-op when a
        fresh persistent cache was adopted, unless `force=True`.

        Args:
            force: Re-ingest even if data is already present (used by `reload`).

        Returns:
            Self for method chaining.
        """
        if self.is_loaded and not force:
            return self
        super().load(
            self._iter_records(),
            chunk_size=self.config.chunk_size,
            on_progress=self._on_progress,
        )
        self.is_loaded = True
        return self

    def reload(self) -> None:
        """Re-ingest the file from disk, replacing the working store's contents."""
        self.load(force=True)

    def _iter_records(self) -> Iterator[Record]:
        """Stream parsed, transformed records from the file."""
        from bootstack.data.readers import read_records

        for raw in read_records(self.filepath, self.config):
            record = self._apply_transformations(raw)
            if record is not None:
                yield record

    def _on_progress(self, count: int) -> None:
        if self.config.progress_callback:
            self.config.progress_callback(count)

    # ------------------------------------------------------------------ cache

    def _cache_is_fresh(self) -> bool:
        """Whether a named cache already holds up-to-date data for the source."""
        if self._cache_path is None:
            return False
        try:
            if not self._cache_path.exists() or self._cache_path.stat().st_size == 0:
                return False
            if self._cache_path.stat().st_mtime < self.filepath.stat().st_mtime:
                return False
            count = self.conn.execute(f"SELECT COUNT(*) FROM {self._table}").fetchone()[0]
            return count > 0
        except sqlite3.Error:
            return False
        except OSError:
            return False

    def _adopt_existing_schema(self) -> None:
        """Populate the column list from an existing cache table (no re-ingest)."""
        try:
            cur = self.conn.execute(f"PRAGMA table_info({self._table})")
            self._columns = [row["name"] for row in cur.fetchall()]
        except sqlite3.Error:
            self._columns = []

    # ------------------------------------------------------------------ lifecycle

    def close(self) -> None:
        """Close the working store, removing the temporary file if one was used.

        Idempotent. A temporary store is also cleaned automatically if this is
        never called (see the finalizer registered in `__init__`).
        """
        if self._finalizer is not None:
            self._finalizer()  # closes the connection and removes the temp file (once)
        else:
            super().close()

    # ------------------------------------------------------------------ transforms

    def _apply_transformations(self, record: Record) -> Optional[Record]:
        """Apply the configured transformation pipeline to a single record.

        Returns:
            The transformed record, or None if filtered out.
        """
        # Apply row filter first.
        if self.config.row_filter and not self.config.row_filter(record):
            return None

        # Column selection.
        if self.config.columns_to_load:
            record = {k: v for k, v in record.items() if k in self.config.columns_to_load}

        # Column renames.
        if self.config.column_renames:
            for old_name, new_name in self.config.column_renames.items():
                if old_name in record:
                    record[new_name] = record.pop(old_name)

        # Default values.
        if self.config.default_values:
            for col, default in self.config.default_values.items():
                if col not in record or record[col] is None:
                    record[col] = default

        # Type conversions.
        if self.config.column_types:
            for col, col_type in self.config.column_types.items():
                if col in record and record[col] is not None:
                    try:
                        record[col] = col_type(record[col])
                    except (ValueError, TypeError):
                        pass  # Keep original value if conversion fails

        # Per-column transforms.
        if self.config.column_transforms:
            for col, transform_func in self.config.column_transforms.items():
                if col in record:
                    try:
                        record[col] = transform_func(record[col])
                    except Exception:
                        pass  # Keep original value if transform fails

        # Row-level transform.
        if self.config.row_transform:
            record = self.config.row_transform(record)

        return record
