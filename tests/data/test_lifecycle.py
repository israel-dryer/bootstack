"""Tests for data-source resource lifecycle — close() and context manager.

Sources follow the Python file-object convention: an explicit ``close()`` plus
``with`` support. In-memory sources have nothing to release (no-op close);
``SqliteDataSource`` closes its connection. Headless (no App).
"""
from __future__ import annotations

import sqlite3

import pytest

from bootstack.data import MemoryDataSource, SqliteDataSource


def test_sqlite_context_manager_returns_self_and_works():
    with SqliteDataSource() as ds:
        ds.load([{"id": 1, "name": "A"}])
        assert ds.count == 1


def test_sqlite_close_releases_connection():
    ds = SqliteDataSource().load([{"id": 1, "name": "A"}])
    ds.close()
    # Using a closed connection raises — the resource really was released.
    with pytest.raises(sqlite3.ProgrammingError):
        ds.conn.execute("SELECT 1")


def test_sqlite_close_is_idempotent():
    ds = SqliteDataSource()
    ds.close()
    ds.close()  # no error on a second close


def test_sqlite_with_block_closes_on_exit():
    ds = SqliteDataSource().load([{"id": 1, "name": "A"}])
    with ds:
        assert ds.count == 1
    with pytest.raises(sqlite3.ProgrammingError):
        ds.conn.execute("SELECT 1")


def test_sqlite_with_block_closes_even_on_exception():
    ds = SqliteDataSource()
    with pytest.raises(ValueError):
        with ds:
            raise ValueError("boom")
    with pytest.raises(sqlite3.ProgrammingError):
        ds.conn.execute("SELECT 1")


def test_memory_context_manager_is_noop_close():
    with MemoryDataSource() as ds:
        ds.load([{"id": 1, "name": "A"}])
        assert ds.count == 1
    # No resources to release; data remains accessible after the block.
    assert ds.count == 1
    ds.close()  # still a no-op, no error
