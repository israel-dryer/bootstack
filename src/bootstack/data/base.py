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
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Sequence, Mapping

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
        # Reactive change broadcasting (on_change / observe). Lazy import keeps
        # the data layer free of a load-time dependency on the runtime layer.
        from bootstack.data._observable import _ChangeHub

        self._hub = _ChangeHub(self)

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

    # Observable query — read-only filtered/sorted read
    @abstractmethod
    def _query(self, condition: "Condition | None", sort_keys: "List[SortKey]") -> List[Record]:
        """Run a one-off filtered and sorted read, returning fresh records.

        Unlike `page`, this does NOT use or modify the source's active
        `where`/`order` view state — it answers an `observe()` query in
        isolation so pagination is undisturbed.

        Args:
            condition: Filter condition (or `None` for all rows).
            sort_keys: Ordering to apply (empty for source/natural order).

        Returns:
            List of matching record dictionaries.
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

    # ========== ROW IDENTITY (for datasource-aware widgets) ==========

    @property
    def id_field(self) -> str:
        """Name of the record field that holds the stable row identity."""
        return getattr(self, "_id_field", "id")

    def _internal_fields(self) -> "frozenset[str]":
        """Raw-record keys that are implementation-internal and hidden from users.

        Datasource-aware widgets (for example `Table`) strip these from displayed
        columns, exports, and the records they hand back. The default is none;
        sources that carry bookkeeping columns override this.

        Returns:
            A set of record keys to treat as private.
        """
        return frozenset()

    def _record_id(self, record: "Mapping[str, Any] | None") -> Any:
        """Return the stable identity of a raw record.

        The returned value is what `get`/`update`/`delete`/`select` accept and
        what is surfaced publicly as the record's `id`. The default reads the
        configured `id_field`; sources with a separate identity column override.

        Args:
            record: A raw record as returned by `page`/`page_slice`.

        Returns:
            The record's identity, or `None` when it cannot be determined.
        """
        if not record:
            return None
        return record.get(self.id_field)

    def _public_record(self, record: "Mapping[str, Any] | None") -> Record:
        """Return a user-facing copy of a raw record.

        Internal bookkeeping fields are stripped and the stable identity is
        surfaced as `id`, so widgets and callers see a clean record regardless
        of how the source stores it.

        Args:
            record: A raw record as returned by `page`/`page_slice`.

        Returns:
            A new dict with internal fields removed and `id` populated.
        """
        if not record:
            return {}
        internal = self._internal_fields()
        out = {k: v for k, v in record.items() if k not in internal}
        rid = self._record_id(record)
        if rid is not None:
            out["id"] = rid
        return out

    # ========== CHANGE BROADCASTING (on_change / observe) ==========

    def on_change(self, handler: "Callable[[Any], Any] | None" = None) -> Any:
        """Subscribe to changes to this source.

        Call with no argument to get a composable `Stream` of coarse change
        events; chain `map`/`filter`/`debounce` and `listen` to drive any
        widget (for example, a dashboard badge bound to the row count). Call
        with a handler to subscribe directly and get back a cancellable
        subscription.

        The handler receives a `DataChangeEvent`. Rapid mutations are coalesced
        into a single notification per event-loop turn, and mutations made from
        a background thread are delivered on the main thread automatically — so
        a bound widget can refresh from a worker-thread feed with no extra work.

        Args:
            handler: Change handler. Omit to receive a `Stream` instead.

        Returns:
            A `Stream` when `handler` is omitted, otherwise a cancellable
            subscription handle.

        Example:
            .. code-block:: python

                ds.on_change(lambda e: print("changed:", e.kind))

                # Feed a dashboard badge with the live row count.
                ds.on_change().map(lambda e: ds.count).listen(badge.set_value)
        """
        from bootstack.streams import Handle, Stream

        hub = self._hub
        if handler is not None:
            return Handle(hub.add_listener(handler))

        from bootstack._runtime.app import get_current_app, has_current_app

        if not has_current_app():
            raise RuntimeError(
                "on_change() with no handler returns a Stream, which requires an "
                "active App. Pass a handler — on_change(fn) — for headless use."
            )
        owner = get_current_app()

        def _source(downstream):
            return Handle(hub.add_listener(downstream))

        return Stream(owner, _source=_source)

    def observe(self, condition: "Condition | None" = None, *order: "str | Column | SortKey") -> Any:
        """Observe a live result set for a `where`/`order` query.

        Returns a `Stream` that emits the matching records immediately, then a
        fresh result set whenever a relevant change occurs. Each subscriber
        observes its own slice — declare the query once, react to its results
        over time (the "observable query" pattern).

        Selection toggles do not re-emit (selection is not a row-set change).
        Unlike `where`/`order`, observing does not disturb the source's own
        pagination view.

        Performance: each relevant change re-runs the whole query and re-emits
        the full result set. Use `observe` for *small* derived sets — dashboard
        metrics, a short pinned list, a filtered side panel. For large or
        virtualized views (`Table`, `ListView`) do NOT observe the full set;
        bind those widgets to the source directly — they listen via `on_change`
        and refetch only their visible window with `page`/`page_slice`.

        Args:
            condition: Filter condition built with `col` (or `None` for all rows).
            order: Sort keys — column names, `"-name"` for descending, or
                `col(...)` specs.

        Returns:
            A `Stream` of result sets (each a list of record dictionaries).

        Example:
            .. code-block:: python

                ds.observe(col("status") == "active", "-created").listen(
                    lambda rows: gauge.set_value(len(rows))
                )
        """
        from bootstack.data._observable import _ObservedQuery
        from bootstack.data.query import normalize_sort_keys
        from bootstack.streams import Handle, Stream
        from bootstack._runtime.app import get_current_app, has_current_app

        if not has_current_app():
            raise RuntimeError(
                "observe() returns a Stream, which requires an active App."
            )
        owner = get_current_app()
        sort_keys = normalize_sort_keys(order)
        hub = self._hub
        source = self

        def _source(downstream):
            query = _ObservedQuery(source, condition, sort_keys, downstream)
            remove = hub.add_query(query)
            try:
                downstream(query.start())
            except Exception:
                pass
            return Handle(remove)

        return Stream(owner, _source=_source)

    def _silence(self):
        """Context manager that suppresses change emission within its block.

        Used internally by widgets to mutate their own bound source without
        broadcasting the change back to themselves.
        """
        return self._hub.silence()

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