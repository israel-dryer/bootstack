"""GUI tests for the public DataTable widget.

Two concerns are covered:

1. **Data-source decoupling** — the DataTable must work with any source that
   implements the data-source protocol, not just ``SqliteDataSource``. A
   ``MemoryDataSource`` should render, round-trip ``select_rows`` (the bug that
   motivated the decoupling), and hide the source's internal bookkeeping fields
   from displayed/returned records.

2. **Appearance params** — ``density`` is forwarded to the underlying themed
   treeview style.
"""
from __future__ import annotations

import pytest

import bootstack as bs


ROWS = [
    {"id": 10, "name": "Ada", "role": "eng"},
    {"id": 20, "name": "Boole", "role": "math"},
    {"id": 30, "name": "Church", "role": "math"},
]


@pytest.fixture(scope="module")
def shown_app():
    """A single shown App so child widgets get mapped and styles build."""
    app = bs.App()
    app.__enter__()
    root = app._tk_root
    root.deiconify()
    root.update_idletasks()
    try:
        yield app
    finally:
        try:
            app.__exit__(None, None, None)
        except Exception:
            pass
        try:
            root.destroy()
        except Exception:
            pass


def _pump(app) -> None:
    root = app._tk_root
    root.update_idletasks()
    root.update()


def _rowheight(table) -> int:
    """Resolved ttk rowheight for a table's treeview body style."""
    from bootstack.style.style import get_style

    tree = table._internal._tree
    return int(get_style().configure(tree.cget("style"), "rowheight"))


# --------------------------------------------------------------------------- decoupling


@pytest.mark.gui
def test_memory_source_renders(shown_app):
    src = bs.MemoryDataSource()
    src.load([dict(r) for r in ROWS])
    table = bs.DataTable(data_source=src, columns=["name", "role"], page_size=10)
    _pump(shown_app)

    rows = table.to_rows("page")
    assert [r["name"] for r in rows] == ["Ada", "Boole", "Church"]
    assert [r["id"] for r in rows] == [10, 20, 30]


@pytest.mark.gui
def test_memory_source_select_rows_roundtrip(shown_app):
    """The bug the decoupling fixed: select_rows silently did nothing for a
    non-Sqlite source because identity was read from a Sqlite-only column."""
    src = bs.MemoryDataSource()
    src.load([dict(r) for r in ROWS])
    table = bs.DataTable(
        data_source=src, columns=["name", "role"], selection_mode="multi", page_size=10
    )
    _pump(shown_app)

    table.select_rows([10, 30])
    _pump(shown_app)

    selected_ids = sorted(r["id"] for r in table.selected_rows)
    assert selected_ids == [10, 30]


@pytest.mark.gui
def test_memory_source_hides_internal_selected_field(shown_app):
    """The source's internal `selected` flag must not leak into public records."""
    src = bs.MemoryDataSource()
    src.load([dict(r) for r in ROWS])
    table = bs.DataTable(
        data_source=src, columns=["name", "role"], selection_mode="multi", page_size=10
    )
    _pump(shown_app)

    table.select_rows([10])
    _pump(shown_app)

    for r in table.to_rows("all"):
        assert "selected" not in r
    for r in table.selected_rows:
        assert "selected" not in r


@pytest.mark.gui
def test_sqlite_source_default_still_works(shown_app):
    """Sanity: the default (auto-created Sqlite) path is unchanged."""
    table = bs.DataTable(rows=[dict(r) for r in ROWS], columns=["name", "role"],
                     selection_mode="multi", page_size=10)
    _pump(shown_app)

    table.select_rows([20])
    _pump(shown_app)

    assert [r["id"] for r in table.selected_rows] == [20]
    for r in table.to_rows("all"):
        assert "_bs_row_id" not in r and "_bs_selected" not in r


# --------------------------------------------------------------------------- appearance


@pytest.mark.gui
def test_density_compact_is_shorter_than_default(shown_app):
    default_table = bs.DataTable(rows=[dict(r) for r in ROWS], columns=["name"], density="default")
    compact_table = bs.DataTable(rows=[dict(r) for r in ROWS], columns=["name"], density="compact")
    _pump(shown_app)

    assert _rowheight(compact_table) < _rowheight(default_table)
