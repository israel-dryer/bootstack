"""Data source abstraction for bootstack widgets.

Provides unified interface for data management with multiple backend implementations:
    - MemoryDataSource: Fast in-memory storage for small to medium datasets
    - SqliteDataSource: Persistent SQLite storage for large datasets
    - FileDataSource: File-based storage with support for CSV, JSON, and various formats

All datasources support:
    - Pagination with configurable page size
    - Filtering and sorting with the `col` expression API
    - Full CRUD operations (insert, get, update, delete)
    - Record selection tracking
    - CSV export

Usage:
    from bootstack.data import MemoryDataSource, SqliteDataSource, FileDataSource
    from bootstack import col

    # In-memory datasource
    ds = MemoryDataSource(page_size=20)
    ds.load([{"name": "Alice", "age": 30}, ...])

    # SQLite datasource (persistent)
    db = SqliteDataSource("mydata.db", page_size=50)
    db.load([{"name": "Bob", "age": 25}, ...])

    # File datasource (CSV, JSON, etc.)
    file_ds = FileDataSource("data.csv", page_size=25)
    file_ds.load()

    # Common operations (work with all)
    ds.where(col("age") >= 25)
    ds.order("name")
    first = ds.page(0)
"""

from bootstack.data.base import BaseDataSource
from bootstack.data.memory_source import MemoryDataSource
from bootstack.data.sqlite_source import SqliteDataSource
from bootstack.data.file_source import FileDataSource, FileSourceConfig
from bootstack.data.query import col, Column, Condition, SortKey, any_of, all_of
from bootstack.data.types import DataSourceProtocol, Record, Primitive

__all__ = [
    'BaseDataSource',
    'MemoryDataSource',
    'SqliteDataSource',
    'FileDataSource',
    'FileSourceConfig',
    'DataSourceProtocol',
    'Record',
    'Primitive',
    'col',
    'Column',
    'Condition',
    'SortKey',
    'any_of',
    'all_of',
]