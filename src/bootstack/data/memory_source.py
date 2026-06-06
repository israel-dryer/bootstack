"""In-memory data source implementation with filtering, sorting, and pagination.

Provides a pure-Python in-memory data manager that supports:
    - Pagination with configurable page size
    - Filtering with `col`-based conditions
    - Multi-column sorting
    - Full CRUD operations (insert, get, update, delete)
    - Record selection tracking
    - CSV export
    - Inferred schema from data

The MemoryDataSource stores all data in memory and provides fast access for
small to medium datasets. For larger datasets or persistence requirements,
consider using SqliteDataSource instead.

Filtering and sorting:
    Conditions are built with `col` (see `bootstack.data.query`) and evaluated
    in pure Python:

    .. code-block:: python

        from bootstack import col

        ds.where((col("status") == "active") & (col("age") >= 18))
        ds.where(col("name").startswith("John"))
        ds.order("last_name", "-age")

Data Format:
    - Records must be dictionaries or will be auto-wrapped as {"text": str(value)}
    - Each record automatically gets an 'id' field (integer, auto-generated if missing)
    - Each record automatically gets a 'selected' field (0 or 1)
"""

from __future__ import annotations

import csv
from collections.abc import Sequence
from typing import Any, Dict, List, Optional, Union, Mapping, Iterable

from bootstack.data.base import BaseDataSource
from bootstack.data.query import Condition, SortKey, normalize_sort_keys
from bootstack.data.types import Primitive
from bootstack.errors import DuplicateIdError
from bootstack.events import DataChangeEvent


class MemoryDataSource(BaseDataSource):
    """In-memory data manager with pagination, filtering, sorting, and CRUD operations.

    Stores all records in memory as dictionaries with automatic ID generation and
    selection tracking. Provides SQL-like filtering and sorting syntax for intuitive
    data manipulation.

    The datasource maintains an internal index for O(1) ID lookups and supports
    dynamic schema inference from provided data.

    Args:
        page_size: Number of records per page (default: 10)

    Attributes:
        page_size: Current page size setting

    Example:
        .. code-block:: python

            ds = MemoryDataSource(page_size=20)
            ds.load([
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
            ])
            ds.where(col("age") >= 30)
            first = ds.page(0)

    """

    def __init__(self, page_size: int = 10, id_field: str = "id"):
        """Initialize the in-memory datasource with defaults.

        Args:
            page_size: Number of records returned per page when paginating.
            id_field: Record field used as the stable row identity. A record's own
                value for this field is kept as its id; otherwise one is assigned.
        """
        super().__init__(page_size)
        self._table = "records"
        self._id_field = id_field
        self._columns: List[str] = []
        self._data: List[Dict[str, Any]] = []
        self._id_index: Dict[Any, int] = {}
        self._filter: Optional[Condition] = None
        self._sort: List[SortKey] = []

    def _rebuild_id_index(self) -> None:
        """Rebuild the ID-to-position index for fast lookups."""
        self._id_index.clear()
        for i, rec in enumerate(self._data):
            self._id_index[rec.get(self._id_field)] = i

    def _ensure_selected_column(self) -> None:
        """Ensure all records have a 'selected' field."""
        if "selected" not in self._columns:
            self._columns.append("selected")
            for r in self._data:
                r.setdefault("selected", 0)

    def _ensure_id(self) -> None:
        """Ensure all records have unique integer IDs.

        Records whose `id` is already an int and not a duplicate are
        preserved as-is. Records with missing, non-integer, or duplicate
        IDs get a freshly-allocated integer ID.
        """
        used: set[int] = set()
        needs_id: list[Dict[str, Any]] = []
        max_id = 0
        for r in self._data:
            rid = r.get(self._id_field)
            if isinstance(rid, int) and rid not in used:
                used.add(rid)
                if rid > max_id:
                    max_id = rid
            else:
                needs_id.append(r)
        for r in needs_id:
            max_id += 1
            while max_id in used:
                max_id += 1
            r[self._id_field] = max_id
            used.add(max_id)
        self._rebuild_id_index()

    @staticmethod
    def _sort_rows(rows: List[Dict[str, Any]], sort_keys: List[SortKey]) -> List[Dict[str, Any]]:
        """Stable multi-key sort in place — first key wins (applied right-to-left)."""
        for key in reversed(sort_keys):
            rows.sort(
                key=lambda r, c=key.column: (r.get(c) is None, r.get(c)),
                reverse=key.descending,
            )
        return rows

    def _apply_filter_and_sort(self, rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply the current filter and sort to a row collection."""
        if self._filter is not None:
            rows = [r for r in rows if self._filter.matches(r)]
        else:
            rows = list(rows)
        return self._sort_rows(rows, self._sort)

    def _query(self, condition: Optional[Condition], sort_keys: List[SortKey]) -> List[Dict[str, Any]]:
        """Run a one-off filtered/sorted read without touching view state."""
        rows = [r for r in self._data if condition is None or condition.matches(r)]
        return [dict(r) for r in self._sort_rows(rows, sort_keys)]

    def load(self, records: Union[Sequence[Primitive], Sequence[Dict[str, Any]]]) -> "MemoryDataSource":
        """Load records into datasource.

        Args:
            records: Sequence of dicts or primitives (auto-wrapped as {"text": str(x)})

        Returns:
            Self for method chaining
        """
        if not records:
            self._data = []
            self._columns = []
            self._rebuild_id_index()
            self._hub.emit(DataChangeEvent(kind="load"))
            return self

        if records and not self._is_mapping(records[0]):
            records = [dict(text=str(x)) for x in records]

        data: List[Dict[str, Any]] = []
        seen_ids: set = set()
        for i, rec in enumerate(records):
            r = dict(rec)
            r.setdefault(self._id_field, i)
            rid = r[self._id_field]
            if rid in seen_ids:
                raise DuplicateIdError(
                    f"Duplicate value {rid!r} in id field {self._id_field!r} — record "
                    f"ids must be unique."
                )
            seen_ids.add(rid)
            r.setdefault("selected", 0)
            data.append(r)

        self._data = data
        self._columns = list(self._data[0].keys())
        self._ensure_id()
        self._ensure_selected_column()
        self._hub.emit(DataChangeEvent(kind="load"))
        return self

    def where(self, condition: Optional[Condition] = None) -> "MemoryDataSource":
        """Filter rows by a condition built with `col` (None clears the filter)."""
        self._filter = condition
        self._hub.emit(DataChangeEvent(kind="filter"))
        return self

    def order(self, *keys) -> "MemoryDataSource":
        """Sort rows by one or more keys (no arguments clears sorting)."""
        self._sort = normalize_sort_keys(keys)
        self._hub.emit(DataChangeEvent(kind="sort"))
        return self

    def _filtered_sorted_rows(self) -> List[Dict[str, Any]]:
        """Get all rows with current filter and sort applied."""
        return self._apply_filter_and_sort(self._data)

    def page(self, page: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get records for specified page."""
        if page is not None:
            self._page = max(0, int(page))
        rows = self._filtered_sorted_rows()
        start = self._page * self.page_size
        end = start + self.page_size
        return [dict(r) for r in rows[start:end]]

    def next_page(self) -> List[Dict[str, Any]]:
        """Advance to next page and return its records."""
        if self.has_next_page():
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
        return len(self._filtered_sorted_rows())

    def _generate_new_id(self) -> int:
        """Generate next available integer ID."""
        if not self._data:
            return 1
        try:
            return max(int(r.get(self._id_field, 0)) for r in self._data) + 1
        except (TypeError, ValueError):
            raise DuplicateIdError(
                f"Cannot auto-assign an id: existing ids in field {self._id_field!r} are "
                f"non-integer. Provide an explicit {self._id_field!r} on every inserted "
                f"record when using custom ids."
            )

    def insert(self, record: Dict[str, Any]) -> int:
        """Create new record and return its ID."""
        r = dict(record)
        if self._id_field not in r:
            r[self._id_field] = self._generate_new_id()
        elif r[self._id_field] in self._id_index:
            raise DuplicateIdError(
                f"A record with id {r[self._id_field]!r} already exists — record ids "
                f"must be unique."
            )
        if "selected" not in r:
            r["selected"] = 0
        self._data.append(r)
        self._columns = list(set(self._columns) | set(r.keys()))
        self._id_index[r[self._id_field]] = len(self._data) - 1
        self._hub.emit(DataChangeEvent(kind="insert", id=r[self._id_field], record=dict(r)))
        return r[self._id_field]

    def get(self, record_id: Any) -> Optional[Dict[str, Any]]:
        """Retrieve single record by ID."""
        idx = self._id_index.get(record_id)
        if idx is None:
            return None
        return dict(self._data[idx])

    def update(self, record_id: Any, updates: Dict[str, Any]) -> bool:
        """Update record fields by ID."""
        if not updates:
            return False
        idx = self._id_index.get(record_id)
        if idx is None:
            return False
        self._data[idx].update(updates)
        self._columns = list(set(self._columns) | set(updates.keys()))
        self._hub.emit(DataChangeEvent(kind="update", id=record_id, record=dict(updates)))
        return True

    def delete(self, record_id: Any) -> bool:
        """Delete record by ID."""
        idx = self._id_index.get(record_id)
        if idx is None:
            return False
        self._data.pop(idx)
        self._rebuild_id_index()
        self._hub.emit(DataChangeEvent(kind="delete", id=record_id))
        return True

    def is_selected(self, record_id: Any) -> bool:
        """Check whether a record is currently selected."""
        idx = self._id_index.get(record_id)
        if idx is None:
            return False
        return bool(self._data[idx].get("selected", 0))

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
            ids = [r[self._id_field] for r in self.page()]
            count = 0
            idset = set(ids)
            for r in self._data:
                if r[self._id_field] in idset and r.get("selected") != 1:
                    r["selected"] = 1
                    count += 1
        else:
            count = 0
            for r in self._data:
                if r.get("selected") != 1:
                    r["selected"] = 1
                    count += 1
        if count:
            self._hub.emit(DataChangeEvent(kind="select"))
        return count

    def deselect_all(self, current_page_only: bool = False) -> int:
        """Deselect all records (optionally only current page)."""
        self._ensure_selected_column()
        if current_page_only:
            ids = [r[self._id_field] for r in self.page()]
            count = 0
            idset = set(ids)
            for r in self._data:
                if r[self._id_field] in idset and r.get("selected") != 0:
                    r["selected"] = 0
                    count += 1
        else:
            count = 0
            for r in self._data:
                if r.get("selected") != 0:
                    r["selected"] = 0
                    count += 1
        if count:
            self._hub.emit(DataChangeEvent(kind="select"))
        return count

    def move(self, record_id: Any, target_index: int) -> bool:
        """Reorder a record within the in-memory list."""
        if not self._data:
            return False

        source_index = self._id_index.get(record_id)
        if source_index is None:
            return False

        clamped_target = max(0, min(int(target_index), len(self._data) - 1))
        if source_index == clamped_target:
            return False

        record = self._data.pop(source_index)
        if clamped_target > source_index:
            clamped_target -= 1
        self._data.insert(clamped_target, record)

        start = min(source_index, clamped_target)
        end = max(source_index, clamped_target) + 1
        for i in range(start, end):
            self._id_index[self._data[i][self._id_field]] = i
        self._hub.emit(DataChangeEvent(kind="move", id=record_id))
        return True

    def _set_selected_flag(self, record_id: Any, flag: int) -> bool:
        """Set selection flag for record by ID."""
        self._ensure_selected_column()
        idx = self._id_index.get(record_id)
        if idx is None:
            return False
        self._data[idx]["selected"] = 1 if flag else 0
        return True

    def selected(self, page: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get selected records, optionally paginated."""
        self._ensure_selected_column()
        rows = [r for r in self._data if r.get("selected") == 1]
        rows = self._apply_filter_and_sort(rows)
        if page is None:
            return [dict(r) for r in rows]
        start = max(0, int(page)) * self.page_size
        end = start + self.page_size
        return [dict(r) for r in rows[start:end]]

    @property
    def selected_count(self) -> int:
        """Number of selected records."""
        self._ensure_selected_column()
        return sum(1 for r in self._data if r.get("selected") == 1)

    def export_csv(self, filepath: str, include_all: bool = True) -> None:
        """Export records to CSV file."""
        rows = self._data if include_all else [r for r in self._data if r.get("selected") == 1]
        if not rows:
            return
        fieldnames = list(self._columns) if self._columns else list(rows[0].keys())
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in rows:
                writer.writerow({k: r.get(k) for k in fieldnames})

    def page_slice(self, start_index: int, count: int) -> List[Dict[str, Any]]:
        """Get records by start index and count (respects filter/sort)."""
        rows = self._filtered_sorted_rows()
        start = max(0, int(start_index))
        end = start + max(0, int(count))
        return [dict(r) for r in rows[start:end]]
