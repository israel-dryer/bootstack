"""Abstract base class for datasource implementations.

Provides a common foundation for all datasource implementations with:
    - Abstract method definitions enforcing the DataSourceProtocol interface
    - Shared utility methods for type inference, literal parsing, and validation
    - Template methods for common operations
    - Hook methods for extensibility

Subclasses must implement storage-specific operations (load, page, CRUD, etc.)
while inheriting common utilities and patterns.

This base class makes it easier to:
    - Create custom datasource implementations
    - Reduce code duplication across implementations
    - Ensure consistent behavior across all datasources
    - Extend datasource functionality through hooks
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Mapping

from bootstack.data.types import Primitive, Record

if TYPE_CHECKING:
    from bootstack.data.query import Column, Condition, SortKey


class BaseDataSource(ABC):
    """Abstract base class for datasource implementations.

    Provides shared utilities and enforces the DataSourceProtocol interface through
    abstract methods. Subclasses implement storage-specific logic while inheriting
    common functionality.

    Args:
        page_size(int): Number of records per page (default: 10)

    Attributes:
        page_size: Current page size setting

    Example:
        .. code-block:: python

            class RedisDataSource(BaseDataSource):
                def __init__(self, redis_client, page_size=10):
                    super().__init__(page_size)
                    self.redis = redis_client

                def load(self, records):
                    pass  # Redis-specific implementation

                def page(self, page=None):
                    pass  # Redis-specific implementation

    """

    def __init__(self, page_size: int = 10):
        """Initialize base datasource with pagination settings.

        Args:
            page_size: Number of records returned per page when paginating.
        """
        self.page_size = page_size
        self._page = 0

    # ========== ABSTRACT METHODS - MUST BE IMPLEMENTED ==========

    # Data & View Configuration
    @abstractmethod
    def load(self, records: Sequence[Primitive] | Sequence[Mapping[str, Any]]) -> 'BaseDataSource':
        """Load data records into the datasource.

        Args:
            records: Sequence of records (dicts) or primitives (auto-wrapped)

        Returns:
            Self for method chaining
        """
        ...

    @abstractmethod
    def where(self, condition: "Condition | None" = None) -> "BaseDataSource":
        """Filter rows by a condition built with `col`.

        Args:
            condition: A filter condition (e.g. `col("age") >= 25`), or `None`
                / no argument to clear the filter.

        Returns:
            Self for method chaining
        """
        ...

    @abstractmethod
    def order(self, *keys: "str | Column | SortKey") -> "BaseDataSource":
        """Sort rows by one or more keys.

        Args:
            keys: Column names (`"name"`), descending names (`"-name"`), or
                `col(...)` specs. With no arguments, clears sorting.

        Returns:
            Self for method chaining
        """
        ...

    # Pagination
    @abstractmethod
    def page(self, page: Optional[int] = None) -> List[Record]:
        """Get records for specified page (or current page if None).

        Args:
            page: Page number (0-indexed); updates current page if provided

        Returns:
            List of record dictionaries for the page
        """
        ...

    @abstractmethod
    def next_page(self) -> List[Record]:
        """Advance to next page and return its records.

        Returns:
            List of record dictionaries for the new page
        """
        ...

    @abstractmethod
    def prev_page(self) -> List[Record]:
        """Move to previous page and return its records.

        Returns:
            List of record dictionaries for the new page
        """
        ...

    @abstractmethod
    def has_next_page(self) -> bool:
        """Check if more pages exist after current page.

        Returns:
            True if next page exists, False otherwise
        """
        ...

    @property
    @abstractmethod
    def count(self) -> int:
        """Total number of records matching the current filter."""
        ...

    # CRUD Operations
    @abstractmethod
    def insert(self, record: Dict[str, Any]) -> int:
        """Create new record and return its ID.

        Args:
            record: Dictionary with record data

        Returns:
            The ID assigned to the new record
        """
        ...

    @abstractmethod
    def get(self, record_id: Any) -> Optional[Record]:
        """Retrieve single record by ID.

        Args:
            record_id: Unique identifier of the record

        Returns:
            Record dictionary or None if not found
        """
        ...

    @abstractmethod
    def update(self, record_id: Any, updates: Dict[str, Any]) -> bool:
        """Update record fields by ID.

        Args:
            record_id: Unique identifier of the record
            updates: Dictionary with fields to update

        Returns:
            True if record was updated, False if not found
        """
        ...

    @abstractmethod
    def delete(self, record_id: Any) -> bool:
        """Delete record by ID.

        Args:
            record_id: Unique identifier of the record

        Returns:
            True if record was deleted, False if not found
        """
        ...

    # Selection Management
    @abstractmethod
    def is_selected(self, record_id: Any) -> bool:
        """Check whether a record is currently selected.

        Args:
            record_id: Unique identifier of the record

        Returns:
            True if the record is selected, False otherwise (including missing records)
        """
        ...

    @abstractmethod
    def select(self, record_id: Any) -> bool:
        """Mark record as selected.

        Args:
            record_id: Unique identifier of the record

        Returns:
            True if record was selected, False if not found
        """
        ...

    @abstractmethod
    def deselect(self, record_id: Any) -> bool:
        """Mark record as unselected.

        Args:
            record_id: Unique identifier of the record

        Returns:
            True if record was deselected, False if not found
        """
        ...

    @abstractmethod
    def select_all(self, current_page_only: bool = False) -> int:
        """Select all records (optionally only current page).

        Args:
            current_page_only: If True, select only records on current page

        Returns:
            Number of records selected
        """
        ...

    @abstractmethod
    def deselect_all(self, current_page_only: bool = False) -> int:
        """Deselect all records (optionally only current page).

        Args:
            current_page_only: If True, deselect only records on current page

        Returns:
            Number of records deselected
        """
        ...

    @abstractmethod
    def selected(self, page: Optional[int] = None) -> List[Record]:
        """Get selected records, optionally paginated.

        Args:
            page: Optional page number for paginating selected records

        Returns:
            List of selected record dictionaries
        """
        ...

    @property
    @abstractmethod
    def selected_count(self) -> int:
        """Number of selected records."""
        ...

    # Export
    @abstractmethod
    def export_csv(self, filepath: str, include_all: bool = True) -> None:
        """Export records to CSV file.

        Args:
            filepath: Path to output CSV file
            include_all: If True, export all records; if False, export only selected
        """
        ...

    # Index-based Access
    @abstractmethod
    def page_slice(self, start_index: int, count: int) -> List[Record]:
        """Get records by start index and count (respects filter/sort).

        Args:
            start_index: Starting record index
            count: Number of records to retrieve

        Returns:
            List of record dictionaries
        """
        ...

    # Lifecycle / reorder — concrete defaults; subclasses may override
    def reload(self) -> None:
        """Re-read data from the underlying source.

        Default is a no-op suitable for in-memory implementations.
        File- and database-backed sources should override to re-query.
        """
        return None

    def move(self, record_id: Any, target_index: int) -> bool:
        """Reorder a record to a new position.

        Default returns False (not supported). Subclasses that maintain
        an explicit ordering should override.

        Args:
            record_id: Unique identifier of the record to move
            target_index: Zero-based destination index (clamped to valid range)

        Returns:
            True if the record was moved, False if not supported or not found
        """
        return False

    # ========== SHARED UTILITY METHODS ==========

    @staticmethod
    def _infer_type(value: Any) -> str:
        """Infer SQL-compatible type from Python value.

        Args:
            value: Python value to infer type from

        Returns:
            SQL type string ('INTEGER', 'REAL', 'BLOB', or 'TEXT')

        Examples:
            >>> BaseDataSource._infer_type(42)
            'INTEGER'
            >>> BaseDataSource._infer_type(3.14)
            'REAL'
            >>> BaseDataSource._infer_type("hello")
            'TEXT'
        """
        if isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "REAL"
        elif isinstance(value, (bytes, bytearray)):
            return "BLOB"
        return "TEXT"

    @staticmethod
    def _is_mapping(x: Any) -> bool:
        """Check if value is a mapping (dict-like).

        Args:
            x: Value to check

        Returns:
            True if value is a mapping, False otherwise

        Examples:
            >>> BaseDataSource._is_mapping({'a': 1})
            True
            >>> BaseDataSource._is_mapping([1, 2, 3])
            False
        """
        return isinstance(x, Mapping)

    @staticmethod
    def _coerce_literal(s: str) -> Any:
        """Parse string literal into Python value (int, float, bool, None, or str).

        Converts SQL/JSON-like literal strings into appropriate Python types:
            - Quoted strings ('foo', "bar") -> str
            - true/false -> bool
            - null/none -> None
            - Numeric strings -> int or float
            - Everything else -> str

        Args:
            s: String literal to parse

        Returns:
            Parsed Python value

        Examples:
            >>> BaseDataSource._coerce_literal("'hello'")
            'hello'
            >>> BaseDataSource._coerce_literal("42")
            42
            >>> BaseDataSource._coerce_literal("3.14")
            3.14
            >>> BaseDataSource._coerce_literal("true")
            True
            >>> BaseDataSource._coerce_literal("null")
            None
        """
        t = s.strip()

        # Handle quoted strings
        if len(t) >= 2 and ((t[0] == t[-1] == "'") or (t[0] == t[-1] == '"')):
            return t[1:-1]

        # Handle booleans
        if t.lower() == "true":
            return True
        if t.lower() == "false":
            return False

        # Handle null/none
        if t.lower() in ("null", "none"):
            return None

        # Try numeric conversion
        try:
            return int(t)
        except Exception:
            pass

        try:
            return float(t)
        except Exception:
            pass

        # Default to string
        return t

    @staticmethod
    def _validate_record(record: Any) -> None:
        """Validate that a record is a dictionary.

        Args:
            record: Value to validate

        Raises:
            ValueError: If record is not a dictionary
        """
        if not isinstance(record, dict):
            raise ValueError(f"Record must be a dictionary, got {type(record).__name__}")

    # ========== HOOK METHODS (Can be overridden by subclasses) ==========

    def _before_create(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Hook called before creating a record.

        Subclasses can override this to perform validation, transformation,
        or side effects before record creation.

        Args:
            record: Record about to be created

        Returns:
            Modified record (or original if no changes)
        """
        return record

    def _after_create(self, record_id: int, record: Dict[str, Any]) -> None:
        """Hook called after creating a record.

        Subclasses can override this to perform logging, caching updates,
        or other side effects after record creation.

        Args:
            record_id: ID of the created record
            record: The created record
        """
        pass

    def _before_update(self, record_id: Any, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Hook called before updating a record.

        Args:
            record_id: ID of record being updated
            updates: Updates to apply

        Returns:
            Modified updates (or original if no changes)
        """
        return updates

    def _after_update(self, record_id: Any, updates: Dict[str, Any], success: bool) -> None:
        """Hook called after updating a record.

        Args:
            record_id: ID of updated record
            updates: Updates that were applied
            success: Whether the update succeeded
        """
        pass

    def _before_delete(self, record_id: Any) -> None:
        """Hook called before deleting a record.

        Args:
            record_id: ID of record about to be deleted
        """
        pass

    def _after_delete(self, record_id: Any, success: bool) -> None:
        """Hook called after deleting a record.

        Args:
            record_id: ID of deleted record
            success: Whether the deletion succeeded
        """
        pass