"""Public data source API surface.

Provides unified interface for data management with multiple backend implementations.
"""

from __future__ import annotations

from bootstack.datasource.base import BaseDataSource
from bootstack.datasource.memory_source import MemoryDataSource
from bootstack.datasource.sqlite_source import SqliteDataSource
from bootstack.datasource.file_source import FileDataSource, FileSourceConfig
from bootstack.datasource.types import DataSourceProtocol, Primitive, Record

__all__ = [
    "BaseDataSource",
    "MemoryDataSource",
    "SqliteDataSource",
    "FileDataSource",
    "FileSourceConfig",
    "DataSourceProtocol",
    "Primitive",
    "Record",
]