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
    ```python
    ds = SqliteDataSource("mydata.db", page_size=50)
    ds.set_data([{"name": "Alice", "age": 30}])
    ds.set_filter("age >= 25")
    page = ds.get_page(0)
    ```
"""

from __future__ import annotations

import csv
import sqlite3
from typing import Any, Dict, List, Optional, Union, Sequence

from bootstack.data.base import BaseDataSource
from bootstack.data.types import Primitive, Record

# Internal column names — reserved by SqliteDataSource, never exposed to user data.
_ROW_ID = "_bs_row_id"
_ROW_SEL = "_bs_selected"


class SqliteDataSource(BaseDataSource):
    """SQLite-backed data manager with pagination, filtering, sorting, and CRUD operations.

    Provides persistent storage using SQLite database with automatic schema inference
    and SQL-native filtering/sorting. Supports all operations defined in DataSourceProtocol.

    Args:
        name: Database file path or ":memory:" for in-memory database (default: ":memory:")
        page_size: Number of records per page (default: 10)

    Attributes:
        conn: SQLite database connection
        page_size: Current page size setting

    Example:
        ```python
        ds = SqliteDataSource("data.db", page_size=20)
        ds.set_data([{"name": "Alice", "age": 30}])
        ds.set_filter("age > 25")
        page = ds.get_page(0)
        ```

    Note:
        - The database connection persists for the lifetime of the object
        - Close the connection explicitly with conn.close() if needed
        - Schema is inferred from first record's data types
        - An internal row-identity column (_bs_row_id) is added automatically as PRIMARY KEY
        - An internal selection column (_bs_selected) is added automatically for selection tracking
        - These internal columns are filtered out of the display column list automatically
    """

    def __init__(self, name: str = ":memory:", page_size: int = 10):
        """Create SQLite datasource and set initial pagination state.

        Args:
            name: Database file path or ':memory:' for an in-memory database.
            page_size: Number of records returned per page during pagination.
        """
        super().__init__(page_size)
        self.conn = sqlite3.connect(name)
        self.conn.row_factory = sqlite3.Row
        self._table = "records"
        self._where = ""
        self._order_by = ""
        self._columns = []

    @staticmethod
    def _quote_identifier(name: str) -> str:
        """Safely quote an identifier (column/table) for SQLite."""
        text = str(name).replace('"', '""')
        return f'"{text}"'

    def set_data(
        self,
        records: Union[Sequence[Primitive], Sequence[dict[str, Any]], Sequence[Sequence[Any]]],
        column_keys: Optional[Sequence[str]] = None,
    ) -> "SqliteDataSource":
        """Load records into database, creating table with inferred schema.

        Args:
            records: Sequence of dicts, primitives, or row sequences.
            column_keys: Optional column names when supplying row sequences (lists/tuples).

        Returns:
            Self for method chaining
        """
        if not records:
            return self

        # Apply fast, in-memory friendly pragmas when using ":memory:" to speed up bulk loads
        try:
            if self.conn.execute("PRAGMA database_list").fetchone()[2] == ":memory:":
                self.conn.execute("PRAGMA synchronous = OFF")
                self.conn.execute("PRAGMA journal_mode = MEMORY")
                self.conn.execute("PRAGMA temp_store = MEMORY")
        except Exception:
            pass

        # Normalize into a common structure: either dicts or row tuples with provided keys
        first = records[0]
        using_dicts = isinstance(first, dict)
        # Turn primitives into dicts
        if not using_dicts and not isinstance(first, (list, tuple)):
            records = [dict(text=str(x)) for x in records]
            using_dicts = True

        if using_dicts:
            # Ensure internal helper columns
            for i, record in enumerate(records):
                if _ROW_ID not in record:
                    record[_ROW_ID] = i
                if _ROW_SEL not in record:
                    record[_ROW_SEL] = 0

            self._columns = list(records[0].keys())
            col_types = {col: self._infer_type(records[0][col]) for col in self._columns}
            rows_to_insert = [tuple(row.get(col) for col in self._columns) for row in records]
        else:
            # Sequence rows with provided column keys
            keys = list(column_keys or [])
            if not keys:
                keys = [str(i) for i in range(len(first))]
            need_id = _ROW_ID not in keys
            need_sel = _ROW_SEL not in keys
            if need_id:
                keys.append(_ROW_ID)
            if need_sel:
                keys.append(_ROW_SEL)
            self._columns = keys

            # Infer types from first row (pad to keys length)
            padded_first = list(first) + [None] * (len(keys) - len(first))
            if need_id and _ROW_ID in keys:
                padded_first[keys.index(_ROW_ID)] = 0
            if need_sel and _ROW_SEL in keys:
                padded_first[keys.index(_ROW_SEL)] = 0
            col_types = {col: self._infer_type(padded_first[idx]) for idx, col in enumerate(keys)}

            rows_to_insert = []
            id_idx = keys.index(_ROW_ID) if _ROW_ID in keys else None
            sel_idx = keys.index(_ROW_SEL) if _ROW_SEL in keys else None
            value_len = len(keys)
            for i, row in enumerate(records):
                base_values = list(row[: value_len]) + [""] * (value_len - len(row))
                if id_idx is not None:
                    base_values[id_idx] = i
                if sel_idx is not None:
                    base_values[sel_idx] = 0
                rows_to_insert.append(tuple(base_values))

        col_definitions = ", ".join(
            f"{self._quote_identifier(col)} {col_types[col]}" + (" PRIMARY KEY" if col == _ROW_ID else "")
            for col in self._columns
        )
        placeholders = ", ".join("?" for _ in self._columns)

        # Recreate table and bulk insert in a single transaction for speed
        original_row_factory = self.conn.row_factory
        try:
            self.conn.row_factory = None  # avoid row wrapping overhead during inserts
            with self.conn:
                self.conn.execute(f"DROP TABLE IF EXISTS {self._table}")
                self.conn.execute(f"CREATE TABLE {self._table} ({col_definitions})")
                self.conn.executemany(f"INSERT INTO {self._table} VALUES ({placeholders})", rows_to_insert)
        finally:
            self.conn.row_factory = original_row_factory
        return self

    def set_filter(self, where_sql: str = ""):
        """Apply SQL WHERE clause filter.

        The fragment is interpolated into the query unmodified, so the caller
        is responsible for ensuring it is trusted/author-controlled. Do not
        pass strings built from end-user input — use parameterized queries
        directly via `self.conn` instead.
        """
        self._where = where_sql

    def set_sort(self, order_by_sql: str = ""):
        """Apply SQL ORDER BY clause for sorting.

        Same trust contract as `set_filter`: the fragment is interpolated
        verbatim, so it must be author-controlled, not user input.
        """
        self._order_by = order_by_sql

    def get_page(self, page: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get records for specified page."""
        if page is not None:
            self._page = page
        offset = self._page * self.page_size

        query = f"SELECT * FROM {self._table}"
        if self._where:
            query += f" WHERE {self._where}"
        if self._order_by:
            query += f" ORDER BY {self._order_by}"
        query += f" LIMIT {self.page_size} OFFSET {offset}"

        cursor = self.conn.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    def next_page(self) -> List[Dict[str, Any]]:
        """Advance to next page and return its records."""
        self._page += 1
        return self.get_page()

    def prev_page(self) -> List[Dict[str, Any]]:
        """Move to previous page and return its records."""
        self._page = max(0, self._page - 1)
        return self.get_page()

    def has_next_page(self) -> bool:
        """Check if more pages exist after current page."""
        return (self._page + 1) * self.page_size < self.total_count()

    def total_count(self) -> int:
        """Get total number of records matching current filter."""
        query = f"SELECT COUNT(*) FROM {self._table}"
        if self._where:
            query += f" WHERE {self._where}"
        return self.conn.execute(query).fetchone()[0]

    # === CRUD OPERATIONS ===

    def create_record(self, record: Dict[str, Any]) -> int:
        """Create new record and return its ID."""
        if _ROW_ID not in record:
            record[_ROW_ID] = self._generate_new_id()

        if _ROW_SEL not in record:
            record[_ROW_SEL] = 0

        # Ensure table exists (handles empty datasources)
        self._ensure_table_for_record(record)

        keys = list(record.keys())
        cols = ", ".join(self._quote_identifier(k) for k in keys)
        placeholders = ", ".join("?" for _ in keys)
        values = tuple(record[col] for col in keys)

        with self.conn:
            self.conn.execute(f"INSERT INTO {self._table} ({cols}) VALUES ({placeholders})", values)
        return record[_ROW_ID]

    def read_record(self, record_id: Any) -> Optional[Dict[str, Any]]:
        """Retrieve single record by ID."""
        cursor = self.conn.execute(f"SELECT * FROM {self._table} WHERE {_ROW_ID} = ?", (record_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_record(self, record_id: Any, updates: Dict[str, Any]) -> bool:
        """Update record fields by ID."""
        if not updates:
            return False
        set_clause = ", ".join(f"{self._quote_identifier(k)} = ?" for k in updates)
        values = tuple(updates.values()) + (record_id,)
        with self.conn:
            cur = self.conn.execute(f"UPDATE {self._table} SET {set_clause} WHERE {_ROW_ID} = ?", values)
            return cur.rowcount > 0

    def delete_record(self, record_id: Any) -> bool:
        """Delete record by ID."""
        with self.conn:
            cur = self.conn.execute(f"DELETE FROM {self._table} WHERE {_ROW_ID} = ?", (record_id,))
            return cur.rowcount > 0

    def _generate_new_id(self) -> int:
        """Generate next available integer ID."""
        try:
            cursor = self.conn.execute(f"SELECT MAX({_ROW_ID}) FROM {self._table}")
            max_id = cursor.fetchone()[0]
        except Exception:
            max_id = 0
        return (max_id or 0) + 1

    # ------------------------------------------------------------------ helpers
    def _ensure_table_for_record(self, record: Dict[str, Any]) -> None:
        """Create the table if it does not yet exist, inferring columns from record."""
        try:
            # Quick existence check
            self.conn.execute(f"SELECT 1 FROM {self._table} LIMIT 1")
            return
        except Exception:
            pass

        cols = list(self._columns) if self._columns else list(record.keys())
        if _ROW_ID not in cols:
            cols.append(_ROW_ID)
        if _ROW_SEL not in cols:
            cols.append(_ROW_SEL)
        self._columns = cols

        col_types = {}
        for c in cols:
            if c == _ROW_ID:
                col_types[c] = "INTEGER"
            elif c == _ROW_SEL:
                col_types[c] = "INTEGER"
            else:
                col_types[c] = self._infer_type(record.get(c))

        col_definitions = ", ".join(
            f"{self._quote_identifier(col)} {col_types[col]}" + (" PRIMARY KEY" if col == _ROW_ID else "")
            for col in cols
        )
        with self.conn:
            self.conn.execute(f"CREATE TABLE IF NOT EXISTS {self._table} ({col_definitions})")

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

    def select_record(self, record_id: Any) -> bool:
        """Mark record as selected."""
        return self._set_selected_flag(record_id, 1)

    def deselect_record(self, record_id: Any) -> bool:
        """Mark record as unselected."""
        return self._set_selected_flag(record_id, 0)

    def select_all(self, current_page_only: bool = False) -> int:
        """Select all records (optionally only current page)."""
        self._ensure_selected_column()
        if current_page_only:
            ids = [row[_ROW_ID] for row in self.get_page()]
            if not ids:
                return 0
            placeholders = ", ".join("?" for _ in ids)
            query = f"UPDATE {self._table} SET {_ROW_SEL} = 1 WHERE {_ROW_ID} IN ({placeholders})"
            with self.conn:
                cur = self.conn.execute(query, ids)
                return cur.rowcount
        else:
            with self.conn:
                cur = self.conn.execute(f"UPDATE {self._table} SET {_ROW_SEL} = 1")
                return cur.rowcount

    def deselect_all(self, current_page_only: bool = False) -> int:
        """Deselect all records (optionally only current page)."""
        self._ensure_selected_column()
        if current_page_only:
            ids = [row[_ROW_ID] for row in self.get_page()]
            if not ids:
                return 0
            placeholders = ", ".join("?" for _ in ids)
            query = f"UPDATE {self._table} SET {_ROW_SEL} = 0 WHERE {_ROW_ID} IN ({placeholders})"
            with self.conn:
                cur = self.conn.execute(query, ids)
                return cur.rowcount
        else:
            with self.conn:
                cur = self.conn.execute(f"UPDATE {self._table} SET {_ROW_SEL} = 0")
                return cur.rowcount

    def get_selected(self, page: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get selected records, optionally paginated."""
        self._ensure_selected_column()
        query = f"SELECT * FROM {self._table} WHERE {_ROW_SEL} = 1"

        if page is not None:
            offset = page * self.page_size
            query += f" LIMIT {self.page_size} OFFSET {offset}"

        cursor = self.conn.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    def _ensure_selected_column(self):
        """Add selection column to table if it doesn't exist."""
        if _ROW_SEL not in self._columns:
            with self.conn:
                self.conn.execute(f"ALTER TABLE {self._table} ADD COLUMN {_ROW_SEL} INTEGER DEFAULT 0")
            self._columns.append(_ROW_SEL)

    def selected_count(self) -> int:
        """Get total number of selected records."""
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

    def export_to_csv(self, filepath: str, include_all: bool = True):
        """Export records to CSV file."""
        self._ensure_selected_column()
        query = f"SELECT * FROM {self._table}"
        if not include_all:
            query += f" WHERE {_ROW_SEL} = 1"

        cursor = self.conn.execute(query)
        rows = cursor.fetchall()

        if not rows:
            return

        with open(filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            for row in rows:
                writer.writerow(dict(row))

    def get_page_from_index(self, start_index: int, count: int) -> List[Dict[str, Any]]:
        """Get records by start index and count (respects filter/sort)."""
        query = f"SELECT * FROM {self._table}"
        if self._where:
            query += f" WHERE {self._where}"
        if self._order_by:
            query += f" ORDER BY {self._order_by}"
        query += f" LIMIT {count} OFFSET {start_index}"
        cursor = self.conn.execute(query)
        return [dict(row) for row in cursor.fetchall()]

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
