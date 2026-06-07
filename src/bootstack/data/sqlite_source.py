"""SQLite-backed data source implementation with persistence, filtering, and pagination.

Provides a database-backed data manager that supports:
    - Persistent storage using SQLite
    - All features of MemoryDataSource (pagination, filtering, sorting, CRUD)
    - Efficient handling of large datasets
    - SQL-native filtering and sorting
    - Automatic schema inference
    - Data persistence across application restarts

The SqliteDataSource is ideal for:
    - Large datasets that don't fit comfortably in memory
    - Applications requiring data persistence
    - Scenarios needing SQL query capabilities
    - Multi-user or multi-session data sharing

For in-memory, lightweight scenarios, consider MemoryDataSource instead.

Example:
    .. code-block:: python

        ds = SqliteDataSource("mydata.db", page_size=50)
        ds.load([{"name": "Alice", "age": 30}])
        ds.where(col("age") >= 25)
        first = ds.page(0)

"""

from __future__ import annotations

import csv
import json
import sqlite3
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union, Sequence

from bootstack.data.base import BaseDataSource
from bootstack.data.query import Condition, SortKey, normalize_sort_keys
from bootstack.data.types import Primitive
from bootstack.errors import DuplicateIdError, SerializationError
from bootstack.events import DataChangeEvent

# Internal column names — reserved by SqliteDataSource, never exposed to user data.
_ROW_ID = "_bs_row_id"
_ROW_SEL = "_bs_selected"
# Hidden JSON column carrying every non-scalar record field (the data bag). SQL
# columns are scalar-only, so lists/dicts/etc. ride here and are merged back into
# the record transparently on read. See `_split_for_write` / `_row_to_record`.
_ROW_DATA = "_bs_data"
_INTERNAL_COLUMNS = (_ROW_ID, _ROW_SEL, _ROW_DATA)

# Values storable directly in a SQL column. Everything else is bagged as JSON.
_SCALAR_TYPES = (str, bytes, bytearray, bool, int, float, type(None))


class SqliteDataSource(BaseDataSource):
    """SQLite-backed data manager with pagination, filtering, sorting, and CRUD operations.

    Provides persistent storage using SQLite database with automatic schema inference.
    Filtering and sorting use the `col` expression API (rendered to parameterized
    SQL internally). Supports all operations defined in DataSourceProtocol.

    Args:
        name: Database file path or ":memory:" for in-memory database (default: ":memory:")
        page_size: Number of records per page (default: 10)

    Attributes:
        conn: SQLite database connection
        page_size: Current page size setting

    Example:
        .. code-block:: python

            ds = SqliteDataSource("data.db", page_size=20)
            ds.load([{"name": "Alice", "age": 30}])
            ds.where(col("age") > 25)
            first = ds.page(0)


    Note:
        - The database connection persists for the lifetime of the object
        - Close the connection explicitly with conn.close() if needed
        - Schema is inferred from first record's data types
        - An internal row-identity column (_bs_row_id) is added automatically as PRIMARY KEY
        - An internal selection column (_bs_selected) is added automatically for selection tracking
        - These internal columns are filtered out of the display column list automatically
    """

    def __init__(self, name: str = ":memory:", page_size: int = 10, id_field: str = "id"):
        """Create SQLite datasource and set initial pagination state.

        Args:
            name: Database file path or ':memory:' for an in-memory database.
            page_size: Number of records returned per page during pagination.
            id_field: Record field used as the stable row identity. When a record
                carries this field, its value becomes the row id (so selection and
                events round-trip your own ids); otherwise an id is auto-assigned.
        """
        super().__init__(page_size)
        self.conn = sqlite3.connect(name)
        self.conn.row_factory = sqlite3.Row
        self._table = "records"
        self._id_field = id_field
        self._filter: Optional[Condition] = None
        self._sort: List[SortKey] = []
        self._columns = []

    # ---- internal query-fragment builders -------------------------------

    def _where_clause(self) -> tuple[str, list]:
        """Return `(" WHERE ...", params)` for the active filter, or `("", [])`."""
        if self._filter is None:
            return "", []
        clause, params = self._filter.to_sql()
        return f" WHERE {clause}", params

    def _order_clause(self) -> str:
        """Return `" ORDER BY ..."` for the active sort, or `""`."""
        if not self._sort:
            return ""
        terms = [
            f"{self._quote_identifier(k.column)} {'DESC' if k.descending else 'ASC'}"
            for k in self._sort
        ]
        return " ORDER BY " + ", ".join(terms)

    @staticmethod
    def _quote_identifier(name: str) -> str:
        """Safely quote an identifier (column/table) for SQLite."""
        text = str(name).replace('"', '""')
        return f'"{text}"'

    # ---- data bag (hidden JSON column) ----------------------------------

    @staticmethod
    def _is_scalar(value: Any) -> bool:
        """Whether a value can live directly in a SQL column (vs. the JSON bag)."""
        return isinstance(value, _SCALAR_TYPES)

    @staticmethod
    def _dumps_bag(bag: Dict[str, Any]) -> Optional[str]:
        """Serialize the non-scalar field bag to JSON (or None when empty)."""
        if not bag:
            return None
        try:
            return json.dumps(bag)
        except (TypeError, ValueError) as exc:
            raise SerializationError(
                f"A record field could not be stored in this SQLite-backed source: "
                f"{exc}. Persistent sources carry non-scalar fields as JSON, so values "
                f"must be JSON-serializable (scalars, lists, dicts). To carry arbitrary "
                f"Python objects, use an in-memory source instead."
            ) from exc

    def _split_for_write(
        self, record: Dict[str, Any], column_fields: Sequence[str], default_id: Any = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any], Any]:
        """Split a record into (scalar column values, JSON bag, row id).

        Scalar values for known column fields stay as real columns; every other
        field — non-scalar values, or keys without a column — rides the JSON bag.

        Args:
            record: The user record to write.
            column_fields: Field names backed by real (scalar) columns.
            default_id: Row id to use when the record carries none.

        Returns:
            A `(column_values, bag, row_id)` tuple.
        """
        col_set = set(column_fields)
        col_vals: Dict[str, Any] = {}
        bag: Dict[str, Any] = {}
        for key, value in record.items():
            if key in _INTERNAL_COLUMNS:
                continue
            if key in col_set and self._is_scalar(value):
                col_vals[key] = value
            else:
                bag[key] = value

        if record.get(_ROW_ID) is not None:
            row_id = record[_ROW_ID]
        elif self._id_field in record and self._is_scalar(record[self._id_field]):
            row_id = record[self._id_field]
        else:
            row_id = default_id
        return col_vals, bag, row_id

    def _row_to_record(self, row: Any) -> Dict[str, Any]:
        """Convert a raw SQL row to a record, merging the JSON bag back in.

        Keeps the internal identity/selection columns (widgets read them); only
        the JSON bag column is consumed — its keys are merged in where the row
        has no scalar value, so the record reads back flat and complete.
        """
        rec = dict(row)
        blob = rec.pop(_ROW_DATA, None)
        if blob:
            try:
                extra = json.loads(blob)
            except (TypeError, ValueError):
                extra = None
            if isinstance(extra, dict):
                for key, value in extra.items():
                    if rec.get(key) is None:
                        rec[key] = value
        return rec

    def _query(self, condition: Optional[Condition], sort_keys: List[SortKey]) -> List[Dict[str, Any]]:
        """Run a one-off filtered/sorted read without touching view state."""
        where, params = "", []
        if condition is not None:
            clause, params = condition.to_sql()
            where = f" WHERE {clause}"
        order = ""
        if sort_keys:
            terms = [
                f"{self._quote_identifier(k.column)} {'DESC' if k.descending else 'ASC'}"
                for k in sort_keys
            ]
            order = " ORDER BY " + ", ".join(terms)
        try:
            cursor = self.conn.execute(f"SELECT * FROM {self._table}{where}{order}", params)
            return [self._row_to_record(row) for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            # Table does not exist yet (no data loaded).
            return []

    def load(
        self,
        records: "Iterable[Primitive] | Iterable[dict[str, Any]] | Iterable[Sequence[Any]]",
        column_keys: Optional[Sequence[str]] = None,
        *,
        chunk_size: int = 10_000,
        on_progress: Optional[Callable[[int], None]] = None,
    ) -> "SqliteDataSource":
        """Load records into the database, creating the table with an inferred schema.

        Records are consumed as a stream and inserted in chunks within a single
        transaction, so a lazy iterator of millions of rows loads with bounded
        memory — only `chunk_size` rows are held at a time. The whole load is
        atomic: if any row fails (for example a duplicate id), the table is rolled
        back to its prior state.

        Args:
            records: An iterable of dicts, primitives, or row sequences — a list,
                a generator, or any other iterable.
            column_keys: Optional column names when supplying row sequences
                (lists/tuples).
            chunk_size: Number of rows buffered per `executemany` batch.
            on_progress: Optional callback invoked after each chunk with the
                running count of rows inserted so far.

        Returns:
            Self for method chaining
        """
        it = iter(records)
        try:
            first = next(it)
        except StopIteration:
            return self  # empty input — leave any existing data untouched

        # Apply fast, in-memory friendly pragmas when using ":memory:" to speed up bulk loads
        try:
            if self.conn.execute("PRAGMA database_list").fetchone()[2] == ":memory:":
                self.conn.execute("PRAGMA synchronous = OFF")
                self.conn.execute("PRAGMA journal_mode = MEMORY")
                self.conn.execute("PRAGMA temp_store = MEMORY")
        except Exception:
            pass

        # Build a per-item normalizer to a dict from the first item's shape (the
        # input is assumed homogeneous). We never mutate the caller's records.
        if isinstance(first, dict):
            def to_dict(item: Any) -> Dict[str, Any]:
                return dict(item)
        elif isinstance(first, (list, tuple)):
            keys = list(column_keys or [str(i) for i in range(len(first))])

            def to_dict(item: Any) -> Dict[str, Any]:
                values = list(item)
                if len(values) < len(keys):
                    values += [None] * (len(keys) - len(values))
                return dict(zip(keys, values))
        else:
            def to_dict(item: Any) -> Dict[str, Any]:
                return {"text": str(item)}

        # Real (scalar) columns come from the first record; every other field —
        # non-scalar values, and keys absent from the first record — rides the
        # hidden JSON data column instead.
        first_rec = to_dict(first)
        column_fields = [
            k for k, v in first_rec.items()
            if k not in _INTERNAL_COLUMNS and self._is_scalar(v)
        ]
        self._columns = column_fields + list(_INTERNAL_COLUMNS)

        col_types = {col: self._infer_type(first_rec.get(col)) for col in column_fields}
        if self._id_field in column_fields:
            # Type the identity from the adopted id value (e.g. TEXT for UUIDs).
            col_types[_ROW_ID] = self._infer_type(first_rec.get(self._id_field))
        else:
            col_types[_ROW_ID] = "INTEGER"
        col_types[_ROW_SEL] = "INTEGER"
        col_types[_ROW_DATA] = "TEXT"

        col_definitions = ", ".join(
            f"{self._quote_identifier(col)} {col_types[col]}" + (" PRIMARY KEY" if col == _ROW_ID else "")
            for col in self._columns
        )
        placeholders = ", ".join("?" for _ in self._columns)
        insert_sql = f"INSERT INTO {self._table} VALUES ({placeholders})"

        def row_for(record: Dict[str, Any], index: int) -> tuple:
            col_vals, bag, row_id = self._split_for_write(record, column_fields, default_id=index)
            values = [col_vals.get(col) for col in column_fields]
            values.append(row_id)
            values.append(0)
            values.append(self._dumps_bag(bag))
            return tuple(values)

        # Recreate the table and stream-insert in chunks within one transaction:
        # bounded Python memory (one chunk at a time) and atomic (rolls back on
        # any error). SQLite buffers the pending rows itself, not Python. We drive
        # the transaction explicitly (autocommit off) so the DROP/CREATE are part
        # of it too — Python's sqlite3 otherwise auto-commits DDL, which would
        # leave the table dropped if a later row failed.
        original_row_factory = self.conn.row_factory
        original_isolation = self.conn.isolation_level
        inserted = 0
        try:
            self.conn.row_factory = None  # avoid row wrapping overhead during inserts
            self.conn.isolation_level = None  # manual transaction control
            self.conn.execute("BEGIN")
            self.conn.execute(f"DROP TABLE IF EXISTS {self._table}")
            self.conn.execute(f"CREATE TABLE {self._table} ({col_definitions})")

            buffer = [row_for(first_rec, 0)]
            index = 1
            for raw in it:
                buffer.append(row_for(to_dict(raw), index))
                index += 1
                if len(buffer) >= chunk_size:
                    self.conn.executemany(insert_sql, buffer)
                    inserted += len(buffer)
                    buffer = []
                    if on_progress is not None:
                        on_progress(inserted)
            if buffer:
                self.conn.executemany(insert_sql, buffer)
                inserted += len(buffer)
                if on_progress is not None:
                    on_progress(inserted)
            self.conn.execute("COMMIT")
        except sqlite3.IntegrityError as exc:
            self._safe_rollback()
            raise DuplicateIdError(
                f"Duplicate value in id field {self._id_field!r} — record ids must be "
                f"unique. ({exc})"
            ) from exc
        except BaseException:
            # Any other failure (serialization error, a raising progress callback,
            # cancellation) must roll the whole load back too.
            self._safe_rollback()
            raise
        finally:
            self.conn.row_factory = original_row_factory
            self.conn.isolation_level = original_isolation
        self._hub.emit(DataChangeEvent(kind="load"))
        return self

    def _safe_rollback(self) -> None:
        """Roll back the active transaction, swallowing any rollback error."""
        try:
            self.conn.execute("ROLLBACK")
        except sqlite3.Error:
            pass

    def where(self, condition: Optional[Condition] = None) -> "SqliteDataSource":
        """Filter rows by a condition built with `col` (None clears the filter).

        The condition is rendered to a parameterized query — values are always
        bound, never interpolated — so user input cannot inject SQL.
        """
        self._filter = condition
        self._hub.emit(DataChangeEvent(kind="filter"))
        return self

    def order(self, *keys) -> "SqliteDataSource":
        """Sort rows by one or more keys (no arguments clears sorting)."""
        self._sort = normalize_sort_keys(keys)
        self._hub.emit(DataChangeEvent(kind="sort"))
        return self

    def page(self, page: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get records for specified page."""
        if page is not None:
            self._page = page
        offset = self._page * self.page_size

        where, params = self._where_clause()
        query = (
            f"SELECT * FROM {self._table}{where}{self._order_clause()}"
            f" LIMIT {self.page_size} OFFSET {offset}"
        )
        cursor = self.conn.execute(query, params)
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def next_page(self) -> List[Dict[str, Any]]:
        """Advance to next page and return its records."""
        self._page += 1
        return self.page()

    def prev_page(self) -> List[Dict[str, Any]]:
        """Move to previous page and return its records."""
        self._page = max(0, self._page - 1)
        return self.page()

    def has_next_page(self) -> bool:
        """Check if more pages exist after current page."""
        return (self._page + 1) * self.page_size < self.count

    @property
    def count(self) -> int:
        """Total number of records matching the current filter."""
        where, params = self._where_clause()
        query = f"SELECT COUNT(*) FROM {self._table}{where}"
        return self.conn.execute(query, params).fetchone()[0]

    # === CRUD OPERATIONS ===

    def insert(self, record: Dict[str, Any]) -> int:
        """Create new record and return its ID."""
        # Field names backed by real columns: the established schema, or — for a
        # still-empty source — this record's own scalar fields.
        if self._user_column_fields:
            column_fields = self._user_column_fields
        else:
            column_fields = [
                k for k, v in record.items()
                if k not in _INTERNAL_COLUMNS and self._is_scalar(v)
            ]

        col_vals, bag, row_id = self._split_for_write(record, column_fields)
        if row_id is None:
            row_id = self._generate_new_id()

        # Ensure table exists (handles empty datasources)
        self._ensure_table(column_fields, sample=record)

        keys = list(col_vals.keys()) + list(_INTERNAL_COLUMNS)
        values = [col_vals[k] for k in col_vals] + [row_id, 0, self._dumps_bag(bag)]
        cols = ", ".join(self._quote_identifier(k) for k in keys)
        placeholders = ", ".join("?" for _ in keys)

        try:
            with self.conn:
                self.conn.execute(
                    f"INSERT INTO {self._table} ({cols}) VALUES ({placeholders})", tuple(values)
                )
        except sqlite3.IntegrityError as exc:
            raise DuplicateIdError(
                f"A record with id {row_id!r} already exists — record ids "
                f"must be unique. ({exc})"
            ) from exc
        self._hub.emit(DataChangeEvent(kind="insert", id=row_id, record=dict(record)))
        return row_id

    def get(self, record_id: Any) -> Optional[Dict[str, Any]]:
        """Retrieve single record by ID."""
        cursor = self.conn.execute(f"SELECT * FROM {self._table} WHERE {_ROW_ID} = ?", (record_id,))
        row = cursor.fetchone()
        return self._row_to_record(row) if row else None

    @property
    def _user_column_fields(self) -> List[str]:
        """The real (scalar) column field names, excluding internal columns."""
        return [c for c in self._columns if c not in _INTERNAL_COLUMNS]

    # ---------- row identity ----------
    def _internal_fields(self) -> "frozenset[str]":
        """Hide the internal identity, selection, and data-bag columns from users."""
        return frozenset(_INTERNAL_COLUMNS)

    def _record_id(self, record: Any) -> Any:
        """Identity is the internal `_bs_row_id` column."""
        if not record:
            return None
        return record.get(_ROW_ID)

    def update(self, record_id: Any, updates: Dict[str, Any]) -> bool:
        """Update record fields by ID."""
        if not updates:
            return False

        col_set = set(self._user_column_fields)
        set_parts: List[str] = []
        params: List[Any] = []
        bag_updates: Dict[str, Any] = {}
        for key, value in updates.items():
            if key in _INTERNAL_COLUMNS:
                continue
            if key in col_set and self._is_scalar(value):
                set_parts.append(f"{self._quote_identifier(key)} = ?")
                params.append(value)
            else:
                # A non-scalar value (or a field without a column) rides the bag.
                # If the field also has a real column, null it so the bag wins on read.
                if key in col_set:
                    set_parts.append(f"{self._quote_identifier(key)} = NULL")
                bag_updates[key] = value

        if bag_updates:
            self._ensure_data_column()
            row = self.conn.execute(
                f"SELECT {_ROW_DATA} FROM {self._table} WHERE {_ROW_ID} = ?", (record_id,)
            ).fetchone()
            if row is None:
                return False
            existing: Dict[str, Any] = {}
            blob = row[0]
            if blob:
                try:
                    parsed = json.loads(blob)
                    if isinstance(parsed, dict):
                        existing = parsed
                except (TypeError, ValueError):
                    pass
            existing.update(bag_updates)
            set_parts.append(f"{self._quote_identifier(_ROW_DATA)} = ?")
            params.append(self._dumps_bag(existing))

        if not set_parts:
            return False

        params.append(record_id)
        with self.conn:
            cur = self.conn.execute(
                f"UPDATE {self._table} SET {', '.join(set_parts)} WHERE {_ROW_ID} = ?", params
            )
            changed = cur.rowcount > 0
        if changed:
            self._hub.emit(DataChangeEvent(kind="update", id=record_id, record=dict(updates)))
        return changed

    def delete(self, record_id: Any) -> bool:
        """Delete record by ID."""
        with self.conn:
            cur = self.conn.execute(f"DELETE FROM {self._table} WHERE {_ROW_ID} = ?", (record_id,))
            changed = cur.rowcount > 0
        if changed:
            self._hub.emit(DataChangeEvent(kind="delete", id=record_id))
        return changed

    def _generate_new_id(self) -> int:
        """Generate next available integer ID."""
        try:
            cursor = self.conn.execute(f"SELECT MAX({_ROW_ID}) FROM {self._table}")
            max_id = cursor.fetchone()[0]
        except Exception:
            max_id = 0
        if max_id is None:
            return 1
        if not isinstance(max_id, int):
            raise DuplicateIdError(
                f"Cannot auto-assign an id: existing ids in field {self._id_field!r} are "
                f"non-integer (e.g. {max_id!r}). Provide an explicit {self._id_field!r} "
                f"on every inserted record when using custom ids."
            )
        return max_id + 1

    # ------------------------------------------------------------------ helpers
    def _ensure_table(self, column_fields: Sequence[str], sample: Dict[str, Any]) -> None:
        """Create the table if it does not yet exist, inferring scalar columns.

        Args:
            column_fields: Scalar field names that become real columns.
            sample: A representative record used for column-type inference.
        """
        try:
            # Quick existence check
            self.conn.execute(f"SELECT 1 FROM {self._table} LIMIT 1")
            return
        except Exception:
            pass

        cols = list(column_fields) + list(_INTERNAL_COLUMNS)
        self._columns = cols

        col_types: Dict[str, str] = {}
        for c in cols:
            if c == _ROW_SEL:
                col_types[c] = "INTEGER"
            elif c == _ROW_DATA:
                col_types[c] = "TEXT"
            elif c == _ROW_ID:
                if self._id_field in sample and self._is_scalar(sample[self._id_field]):
                    col_types[c] = self._infer_type(sample[self._id_field])
                else:
                    col_types[c] = "INTEGER"
            else:
                col_types[c] = self._infer_type(sample.get(c))

        col_definitions = ", ".join(
            f"{self._quote_identifier(col)} {col_types[col]}" + (" PRIMARY KEY" if col == _ROW_ID else "")
            for col in cols
        )
        with self.conn:
            self.conn.execute(f"CREATE TABLE IF NOT EXISTS {self._table} ({col_definitions})")

    def _ensure_data_column(self) -> None:
        """Add the hidden JSON data column if it is missing (legacy tables)."""
        if _ROW_DATA in self._columns:
            return
        try:
            with self.conn:
                self.conn.execute(f"ALTER TABLE {self._table} ADD COLUMN {_ROW_DATA} TEXT")
        except sqlite3.OperationalError:
            pass  # no table yet, or column already present
        if _ROW_DATA not in self._columns:
            self._columns.append(_ROW_DATA)

    # === SELECTION ====

    def is_selected(self, record_id: Any) -> bool:
        """Check whether a record is currently selected."""
        if _ROW_SEL not in self._columns:
            return False
        row = self.conn.execute(
            f"SELECT {_ROW_SEL} FROM {self._table} WHERE {_ROW_ID} = ?",
            (record_id,),
        ).fetchone()
        if row is None:
            return False
        return bool(row[0])

    def select(self, record_id: Any) -> bool:
        """Mark record as selected."""
        changed = self._set_selected_flag(record_id, 1)
        if changed:
            self._hub.emit(DataChangeEvent(kind="select", id=record_id))
        return changed

    def deselect(self, record_id: Any) -> bool:
        """Mark record as unselected."""
        changed = self._set_selected_flag(record_id, 0)
        if changed:
            self._hub.emit(DataChangeEvent(kind="select", id=record_id))
        return changed

    def select_all(self, current_page_only: bool = False) -> int:
        """Select all records (optionally only current page)."""
        self._ensure_selected_column()
        if current_page_only:
            ids = [row[_ROW_ID] for row in self.page()]
            if not ids:
                return 0
            placeholders = ", ".join("?" for _ in ids)
            query = f"UPDATE {self._table} SET {_ROW_SEL} = 1 WHERE {_ROW_ID} IN ({placeholders})"
            with self.conn:
                cur = self.conn.execute(query, ids)
                count = cur.rowcount
        else:
            with self.conn:
                cur = self.conn.execute(f"UPDATE {self._table} SET {_ROW_SEL} = 1")
                count = cur.rowcount
        if count:
            self._hub.emit(DataChangeEvent(kind="select"))
        return count

    def deselect_all(self, current_page_only: bool = False) -> int:
        """Deselect all records (optionally only current page)."""
        self._ensure_selected_column()
        if current_page_only:
            ids = [row[_ROW_ID] for row in self.page()]
            if not ids:
                return 0
            placeholders = ", ".join("?" for _ in ids)
            query = f"UPDATE {self._table} SET {_ROW_SEL} = 0 WHERE {_ROW_ID} IN ({placeholders})"
            with self.conn:
                cur = self.conn.execute(query, ids)
                count = cur.rowcount
        else:
            with self.conn:
                cur = self.conn.execute(f"UPDATE {self._table} SET {_ROW_SEL} = 0")
                count = cur.rowcount
        if count:
            self._hub.emit(DataChangeEvent(kind="select"))
        return count

    def selected(self, page: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get selected records, optionally paginated."""
        self._ensure_selected_column()
        query = f"SELECT * FROM {self._table} WHERE {_ROW_SEL} = 1"

        if page is not None:
            offset = page * self.page_size
            query += f" LIMIT {self.page_size} OFFSET {offset}"

        cursor = self.conn.execute(query)
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def _ensure_selected_column(self):
        """Add selection column to table if it doesn't exist."""
        if _ROW_SEL not in self._columns:
            with self.conn:
                self.conn.execute(f"ALTER TABLE {self._table} ADD COLUMN {_ROW_SEL} INTEGER DEFAULT 0")
            self._columns.append(_ROW_SEL)

    @property
    def selected_count(self) -> int:
        """Number of selected records."""
        self._ensure_selected_column()
        query = f"SELECT COUNT(*) FROM {self._table} WHERE {_ROW_SEL} = 1"
        return self.conn.execute(query).fetchone()[0]

    def _set_selected_flag(self, record_id: Any, flag: int) -> bool:
        """Set selection flag for record by ID."""
        if _ROW_SEL not in self._columns:
            with self.conn:
                self.conn.execute(f"ALTER TABLE {self._table} ADD COLUMN {_ROW_SEL} INTEGER DEFAULT 0")
            self._columns.append(_ROW_SEL)

        with self.conn:
            cur = self.conn.execute(
                f"UPDATE {self._table} SET {_ROW_SEL} = ? WHERE {_ROW_ID} = ?",
                (flag, record_id),
            )
            return cur.rowcount > 0

    # === DATA EXPORT ===

    def export_csv(self, filepath: str, include_all: bool = True):
        """Export records to CSV file."""
        self._ensure_selected_column()
        query = f"SELECT * FROM {self._table}"
        if not include_all:
            query += f" WHERE {_ROW_SEL} = 1"

        cursor = self.conn.execute(query)
        rows = cursor.fetchall()

        if not rows:
            return

        # Emit public records — internal columns stripped, the JSON bag merged
        # back into flat fields — over the union of all keys.
        records = [self._public_record(self._row_to_record(row)) for row in rows]
        fieldnames: List[str] = []
        seen: set = set()
        for rec in records:
            for key in rec.keys():
                if key not in seen:
                    seen.add(key)
                    fieldnames.append(key)

        with open(filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for rec in records:
                writer.writerow({k: rec.get(k) for k in fieldnames})

    def page_slice(self, start_index: int, count: int) -> List[Dict[str, Any]]:
        """Get records by start index and count (respects filter/sort)."""
        where, params = self._where_clause()
        query = (
            f"SELECT * FROM {self._table}{where}{self._order_clause()}"
            f" LIMIT {count} OFFSET {start_index}"
        )
        cursor = self.conn.execute(query, params)
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def get_distinct_values(self, column: str, limit: int = 1000) -> List[Any]:
        """Get distinct values for a column.

        Args:
            column: Column name to get distinct values from.
            limit: Maximum number of distinct values to return.

        Returns:
            List of distinct values sorted alphabetically.
        """
        quoted_col = self._quote_identifier(column)
        query = f"SELECT DISTINCT {quoted_col} FROM {self._table}"
        query += f" ORDER BY {quoted_col} LIMIT {limit}"
        cursor = self.conn.execute(query)
        return [row[0] for row in cursor.fetchall()]
