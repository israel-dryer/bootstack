"""Type definitions and protocols for bootstack datasource module.

This module defines the core protocol that all datasource implementations must follow,
enabling consistent data management across different backends (memory, SQLite, web, etc.).

The DataSourceProtocol provides a unified interface for:
    - Data loading and configuration (load, where, order)
    - Pagination (page, next_page, prev_page, has_next_page)
    - CRUD operations (insert, get, update, delete)
    - Selection management (is_selected, select/deselect records)
    - Data export (CSV export)
    - Index-based access (page_slice)
    - Lifecycle and reorder (reload, move)

All datasource implementations should conform to this protocol to ensure
compatibility with datasource-aware widgets and utilities.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING, Any, Dict, List, Optional, Protocol, Sequence, Mapping,
    runtime_checkable,
)

if TYPE_CHECKING:
    from bootstack.data.query import Column, Condition, SortKey

# Type aliases for clarity
Primitive = Any  # Can be str, int, float, bool, None, etc.
Record = Dict[str, Any]


@runtime_checkable
class DataSourceProtocol(Protocol):
    """Protocol defining the interface for data source implementations.

    This protocol establishes a contract that all datasource backends must implement,
    ensuring consistent behavior across different storage mechanisms (memory, database,
    web API, etc.).

    All datasource implementations must support:
        - Pagination with configurable page size
        - Filtering with `col`-based conditions (see `bootstack.data.query`)
        - Sorting by one or more columns
        - Full CRUD operations on records
        - Selection tracking for multi-select scenarios
        - CSV export capabilities
        - Direct index-based data access

    Attributes:
        page_size: Number of records per page

    Notes:
        - Records are represented as Dict[str, Any] with at least 'id' and 'selected' fields
        - Filtering and sorting are expressed with the `col` expression API, not SQL
        - All methods preserve immutability - operations return new data or modify in-place
    """

    # public attrs
    page_size: int

    # ---------- data & view config ----------
    def load(self, records: Sequence[Primitive] | Sequence[Mapping[str, Any]]) -> DataSourceProtocol:
        """Load data records into the datasource.

        Args:
            records: Sequence of records (dicts) or primitives (auto-wrapped)

        Returns:
            Self for method chaining
        """
        ...

    def where(self, condition: "Condition | None" = None) -> DataSourceProtocol:
        """Filter rows by a condition built with `col`.

        Args:
            condition: A filter condition (e.g. `col("age") >= 25`), or `None`
                / no argument to clear the filter.

        Returns:
            Self for method chaining
        """
        ...

    def order(self, *keys: "str | Column | SortKey") -> DataSourceProtocol:
        """Sort rows by one or more keys.

        Args:
            keys: Column names (`"name"`), descending names (`"-name"`), or
                `col(...)` specs (`col("salary").desc()`). With no arguments,
                clears sorting.

        Returns:
            Self for method chaining
        """
        ...

    # ---------- pagination ----------
    def page(self, page: Optional[int] = None) -> List[Record]:
        """Get records for specified page (or current page if None).

        Args:
            page: Page number (0-indexed); updates current page if provided

        Returns:
            List of record dictionaries for the page
        """
        ...

    def next_page(self) -> List[Record]:
        """Advance to next page and return its records.

        Returns:
            List of record dictionaries for the new page
        """
        ...

    def prev_page(self) -> List[Record]:
        """Move to previous page and return its records.

        Returns:
            List of record dictionaries for the new page
        """
        ...

    def has_next_page(self) -> bool:
        """Check if more pages exist after current page.

        Returns:
            True if next page exists, False otherwise
        """
        ...

    @property
    def count(self) -> int:
        """Total number of records matching the current filter."""
        ...

    # ---------- CRUD ----------
    def insert(self, record: Dict[str, Any]) -> int:
        """Create new record and return its ID.

        Args:
            record: Dictionary with record data

        Returns:
            The ID assigned to the new record
        """
        ...

    def get(self, record_id: Any) -> Optional[Record]:
        """Retrieve single record by ID.

        Args:
            record_id: Unique identifier of the record

        Returns:
            Record dictionary or None if not found
        """
        ...

    def update(self, record_id: Any, updates: Dict[str, Any]) -> bool:
        """Update record fields by ID.

        Args:
            record_id: Unique identifier of the record
            updates: Dictionary with fields to update

        Returns:
            True if record was updated, False if not found
        """
        ...

    def delete(self, record_id: Any) -> bool:
        """Delete record by ID.

        Args:
            record_id: Unique identifier of the record

        Returns:
            True if record was deleted, False if not found
        """
        ...

    # ---------- selection ----------
    def is_selected(self, record_id: Any) -> bool:
        """Check whether a record is currently selected.

        Args:
            record_id: Unique identifier of the record

        Returns:
            True if the record is selected, False otherwise (including missing records)
        """
        ...

    def select(self, record_id: Any) -> bool:
        """Mark record as selected.

        Args:
            record_id: Unique identifier of the record

        Returns:
            True if record was selected, False if not found
        """
        ...

    def deselect(self, record_id: Any) -> bool:
        """Mark record as unselected.

        Args:
            record_id: Unique identifier of the record

        Returns:
            True if record was deselected, False if not found
        """
        ...

    def select_all(self, current_page_only: bool = False) -> int:
        """Select all records (optionally only current page).

        Args:
            current_page_only: If True, select only records on current page

        Returns:
            Number of records selected
        """
        ...

    def deselect_all(self, current_page_only: bool = False) -> int:
        """Deselect all records (optionally only current page).

        Args:
            current_page_only: If True, deselect only records on current page

        Returns:
            Number of records deselected
        """
        ...

    def selected(self, page: Optional[int] = None) -> List[Record]:
        """Get selected records, optionally paginated.

        Args:
            page: Optional page number for paginating selected records

        Returns:
            List of selected record dictionaries
        """
        ...

    @property
    def selected_count(self) -> int:
        """Number of selected records."""
        ...

    # ---------- lifecycle / reorder ----------
    def reload(self) -> None:
        """Re-read data from the underlying source.

        For in-memory implementations this is typically a no-op. For
        file- or database-backed sources, this re-queries or re-reads.
        """
        ...

    def close(self) -> None:
        """Release any resources held by the source (a connection, file handle).

        A no-op for in-memory sources. Sources are also context managers, so a
        `with` block closes automatically. Safe to call more than once.
        """
        ...

    def move(self, record_id: Any, target_index: int) -> bool:
        """Reorder a record to a new position.

        Args:
            record_id: Unique identifier of the record to move
            target_index: Zero-based destination index (clamped to valid range)

        Returns:
            True if the record was moved, False if not supported or not found
        """
        ...

    # ---------- export ----------
    def save(self, path: str, *, selected_only: bool = False, format: Optional[str] = None, config: Any = None) -> None:
        """Export records to a file, format chosen by the path extension (or `format`).

        Records are streamed into the writer; the active `where`/`order` view is
        respected. Built-in formats: CSV, TSV, JSON, JSONL, XML — plus Parquet,
        Feather, and HDF5 with the matching extra installed.
        """
        ...

    def export_csv(self, filepath: str, include_all: bool = True) -> None:
        """Export records to CSV file.

        Args:
            filepath: Path to output CSV file
            include_all: If True, export all records; if False, export only selected
        """
        ...

    # ---------- index-based paging ----------
    def page_slice(self, start_index: int, count: int) -> List[Record]:
        """Get records by start index and count (respects filter/sort).

        Args:
            start_index: Starting record index
            count: Number of records to retrieve

        Returns:
            List of record dictionaries
        """
        ...

    # ---------- row identity ----------
    @property
    def id_field(self) -> str:
        """Name of the record field that holds the stable row identity."""
        ...

    def _internal_fields(self) -> "frozenset[str]":
        """Raw-record keys that are implementation-internal and hidden from
        users. Datasource-aware widgets strip these from columns and exports."""
        ...

    def _record_id(self, record: Any) -> Any:
        """Stable identity of a raw record — what `get`/`update`/`delete`/
        `select` accept and what is surfaced publicly as `id`."""
        ...

    def _public_record(self, record: Any) -> Record:
        """User-facing copy of a raw record: internal fields stripped, `id`
        surfaced."""
        ...

    # ---------- change broadcasting ----------
    def on_change(self, handler: Any = None) -> Any:
        """Subscribe to changes. Returns a `Stream` (no handler) or a
        cancellable subscription (with handler). The handler receives a
        `DataChangeEvent`."""
        ...

    def observe(self, condition: "Condition | None" = None, *order: Any) -> Any:
        """Observe a live result set for a `where`/`order` query. Returns a
        `Stream` of result sets that re-emits on relevant changes."""
        ...

    def _query(self, condition: "Condition | None", sort_keys: List[Any]) -> List[Record]:
        """Run a one-off filtered/sorted read without disturbing the source's
        active `where`/`order` view state. Backs `observe()`."""
        ...