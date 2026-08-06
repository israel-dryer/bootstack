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
from bootstack.data import MemoryDataSource


ROWS = [
    {"id": 10, "name": "Ada", "role": "eng"},
    {"id": 20, "name": "Boole", "role": "math"},
    {"id": 30, "name": "Church", "role": "math"},
]


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
    src = MemoryDataSource()
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
    src = MemoryDataSource()
    src.load([dict(r) for r in ROWS])
    table = bs.DataTable(
        data_source=src, columns=["name", "role"], selection_mode="multi", page_size=10
    )
    _pump(shown_app)

    table.select_rows([10, 30])
    _pump(shown_app)

    selected_ids = sorted(r["id"] for r in table.selection)
    assert selected_ids == [10, 30]


@pytest.mark.gui
def test_memory_source_hides_internal_selected_field(shown_app):
    """The source's internal `selected` flag must not leak into public records."""
    src = MemoryDataSource()
    src.load([dict(r) for r in ROWS])
    table = bs.DataTable(
        data_source=src, columns=["name", "role"], selection_mode="multi", page_size=10
    )
    _pump(shown_app)

    table.select_rows([10])
    _pump(shown_app)

    for r in table.to_rows("all"):
        assert "selected" not in r
    for r in table.selection:
        assert "selected" not in r


@pytest.mark.gui
def test_sqlite_source_default_still_works(shown_app):
    """Sanity: the default (auto-created Sqlite) path is unchanged."""
    table = bs.DataTable(rows=[dict(r) for r in ROWS], columns=["name", "role"],
                     selection_mode="multi", page_size=10)
    _pump(shown_app)

    table.select_rows([20])
    _pump(shown_app)

    assert [r["id"] for r in table.selection] == [20]
    for r in table.to_rows("all"):
        assert "_bs_row_id" not in r and "_bs_selected" not in r


# --------------------------------------------------------------------------- data bag


@pytest.mark.gui
def test_nonscalar_fields_survive_default_source(shown_app):
    """Undisplayed, non-scalar fields ride the data bag and come back intact,
    even on the default (Sqlite) source where columns are scalar-only."""
    table = bs.DataTable(
        rows=[
            {"id": 1, "name": "Ada", "tags": ["math", "eng"], "meta": {"era": 1840}},
            {"id": 2, "name": "Boole", "tags": ["logic"], "meta": {"era": 1850}},
        ],
        columns=["name"],  # tags/meta are not displayed
        page_size=10,
    )
    _pump(shown_app)

    rows = {r["id"]: r for r in table.to_rows("all")}
    assert rows[1]["tags"] == ["math", "eng"]
    assert rows[1]["meta"] == {"era": 1840}
    assert rows[2]["tags"] == ["logic"]
    # No bookkeeping columns leak.
    for r in table.to_rows("all"):
        assert "_bs_data" not in r and "_bs_row_id" not in r


# --------------------------------------------------------------------------- export formats


@pytest.mark.gui
def test_export_formats_drive_available_and_resolution(shown_app):
    table = bs.DataTable(
        rows=[dict(r) for r in ROWS], columns=["name", "role"],
        allow_export=True, export_formats=["csv", "json", "jsonl"],
    )
    _pump(shown_app)
    internal = table._internal

    assert internal._available_export_formats() == ["csv", "json", "jsonl"]
    # A format not in export_formats is rejected.
    import pytest as _pytest
    with _pytest.raises(ValueError):
        internal._resolve_format("out.xlsx", None)


@pytest.mark.gui
def test_export_file_writes_registry_formats(shown_app, tmp_path):
    from bootstack.data import read_records, FileSourceConfig

    table = bs.DataTable(
        rows=[dict(r) for r in ROWS], columns=["name", "role"],
        allow_export=True, export_formats=["csv", "json", "jsonl"],
    )
    _pump(shown_app)
    internal = table._internal

    # JSON (registry) export — projected to the displayed columns.
    p = tmp_path / "out.json"
    n = internal.export_file(str(p), scope="all")
    assert n == 3
    back = list(read_records(p))
    assert [r["name"] for r in back] == ["Ada", "Boole", "Church"]
    assert set(back[0].keys()) == {"name", "role"}  # only displayed columns

    # CSV (cooperative) still works.
    c = tmp_path / "out.csv"
    internal.export_file(str(c), scope="all")
    rows = list(read_records(c, FileSourceConfig(file_format="csv")))
    assert [r["name"] for r in rows] == ["Ada", "Boole", "Church"]


# --------------------------------------------------------------------------- appearance


@pytest.mark.gui
def test_density_compact_is_shorter_than_default(shown_app):
    default_table = bs.DataTable(rows=[dict(r) for r in ROWS], columns=["name"], density="default")
    compact_table = bs.DataTable(rows=[dict(r) for r in ROWS], columns=["name"], density="compact")
    _pump(shown_app)

    assert _rowheight(compact_table) < _rowheight(default_table)


# --------------------------------------------------------------------------- selection shape


@pytest.mark.gui
def test_selection_single_mode_is_a_record_dict(shown_app):
    """Single mode: `.selection` is the selected record dict (or None)."""
    table = bs.DataTable(rows=[dict(r) for r in ROWS], columns=["name", "role"],
                         selection_mode="single", page_size=10)
    _pump(shown_app)

    assert table.selection is None

    table.select_rows([20])
    _pump(shown_app)
    sel = table.selection
    assert isinstance(sel, dict)
    assert sel["id"] == 20 and sel["name"] == "Boole"


@pytest.mark.gui
def test_selection_multi_mode_is_a_list(shown_app):
    """Multi mode: `.selection` is always a list — empty when none selected."""
    table = bs.DataTable(rows=[dict(r) for r in ROWS], columns=["name", "role"],
                         selection_mode="multi", page_size=10)
    _pump(shown_app)

    assert table.selection == []

    table.select_rows([10, 30])
    _pump(shown_app)
    assert sorted(r["id"] for r in table.selection) == [10, 30]


# --------------------------------------------------------------------------- per-view isolation


@pytest.mark.gui
def test_two_tables_share_source_independent_search(shown_app):
    """Two DataTables on one MemoryDataSource must filter independently.

    Searching in table_a must not affect the rows visible in table_b, and
    the source's own where/order state must be unchanged after both tables
    have rendered.
    """
    src = MemoryDataSource()
    src.load([dict(r) for r in ROWS])

    table_a = bs.DataTable(
        data_source=src, columns=["name", "role"],
        searchable=True, page_size=10,
    )
    table_b = bs.DataTable(
        data_source=src, columns=["name", "role"],
        searchable=True, page_size=10,
    )
    _pump(shown_app)

    # Both tables start with all rows.
    assert len(table_a.to_rows("page")) == 3
    assert len(table_b.to_rows("page")) == 3

    # Apply a search to table_a only.
    table_a.set_search("Ada")
    _pump(shown_app)

    rows_a = table_a.to_rows("page")
    rows_b = table_b.to_rows("page")

    assert [r["name"] for r in rows_a] == ["Ada"], "table_a should be filtered"
    assert len(rows_b) == 3, "table_b must not be affected by table_a's search"

    # Source's own filter must be untouched.
    assert src._filter is None, "source where() must not be mutated"


@pytest.mark.gui
def test_two_tables_share_source_independent_sort(shown_app):
    """Sorting in one table must not change the sort order seen by the other."""
    src = MemoryDataSource()
    src.load([dict(r) for r in ROWS])

    table_a = bs.DataTable(data_source=src, columns=["name", "role"], page_size=10)
    table_b = bs.DataTable(data_source=src, columns=["name", "role"], page_size=10)
    _pump(shown_app)

    # Sort table_a descending by name.
    table_a.sort_by("name", ascending=False)
    _pump(shown_app)

    names_a = [r["name"] for r in table_a.to_rows("page")]
    names_b = [r["name"] for r in table_b.to_rows("page")]

    assert names_a == sorted(names_a, reverse=True), "table_a should be sorted desc"
    assert names_b == ["Ada", "Boole", "Church"], "table_b must keep insertion order"

    # Source's own sort must be untouched.
    assert src._sort == [], "source order() must not be mutated"


@pytest.mark.gui
def test_iter_rows_suspended_does_not_clobber_shared_source(shown_app):
    """A suspended iter_rows() generator must not hold this view's filter/sort
    on the shared source.

    The view (the table's search/sort) is applied to the shared source only
    around each read, never across a ``yield`` — otherwise pausing or abandoning
    iteration mid-stream leaves the source filtered for every other view until
    the generator is garbage-collected.
    """
    src = MemoryDataSource()
    src.load([dict(r) for r in ROWS])

    table = bs.DataTable(
        data_source=src, columns=["name", "role"],
        searchable=True, page_size=10,
    )
    _pump(shown_app)

    table.set_search("math")  # matches Boole + Church
    _pump(shown_app)

    it = table.iter_rows("all")
    first = next(it)  # advance once; the generator is now suspended
    assert first["role"] == "math"

    # While the generator is still alive (not closed), the shared source must
    # already be restored — the view CM must not span the yield.
    assert src._filter is None, "iter_rows left the source filtered while suspended"
    assert src._sort == [], "iter_rows left the source sorted while suspended"

    it.close()


# --------------------------------------------------------------------------- row events


def _double_click(tree, iid) -> None:
    """Synthesize a double-click on a row.

    Tk rejects ``event_generate("<Double-1>")`` outright ("Double, Triple, or
    Quadruple modifier not allowed") — ``Double`` is a binding pattern, not an
    event type, and the binding machinery derives it from consecutive presses
    close in time and position. So two presses is the only way to produce one.
    """
    box = tree.bbox(iid)
    # Precondition: an unmapped window returns '' from bbox(), which would make
    # every assertion below pass (or fail) vacuously.
    assert box != "", "row has no bbox — the tree is unmapped, so this test cannot click"
    x, y = box[0] + box[2] // 2, box[1] + box[3] // 2
    assert tree.identify_row(y) == iid, "hit test missed the target row"
    for t in (100, 120):
        tree.event_generate("<ButtonPress-1>", x=x, y=y, time=t)
        tree.event_generate("<ButtonRelease-1>", x=x, y=y, time=t + 5)


@pytest.mark.gui
def test_row_double_click_fires_without_editing(shown_app):
    """#417: on_row_double_click fired only when the table also had allow_edit=True.

    The `<Double-1>` binding was installed inside `if self._editing['updating']`,
    so on a default (read-only) table the public event had nothing behind it.
    """
    seen = []
    table = bs.DataTable(rows=[dict(r) for r in ROWS], columns=["name", "role"], page_size=10)
    table.on_row_double_click(lambda e: seen.append(e))
    _pump(shown_app)

    tree = table._internal._tree
    _double_click(tree, tree.get_children()[0])
    _pump(shown_app)

    assert len(seen) == 1, "double-click on a read-only table did not fire on_row_double_click"
    assert seen[0].record["name"] == "Ada"


@pytest.mark.gui
def test_row_double_click_bound_regardless_of_editing(shown_app):
    """A geometry-free canary for #417: the binding exists either way.

    Deliberately weaker than it looks, so don't rely on it alone — it proves a
    `<Double-*>` sequence is bound, not that it reaches `_on_row_double_click`.
    The handler is not recoverable from the bound script: bootstack names its Tcl
    commands with a serial (`bsregular31`) rather than tkinter's stock
    `id(...) + func.__name__`, so there is nothing to match on. The behavioral
    test above is what proves the wiring; this one is the cheap regression net.
    """
    read_only = bs.DataTable(rows=[dict(r) for r in ROWS], columns=["name"], page_size=10)
    editable = bs.DataTable(rows=[dict(r) for r in ROWS], columns=["name"], page_size=10, allow_edit=True)
    _pump(shown_app)

    for label, table in (("read-only", read_only), ("allow_edit=True", editable)):
        bound = [b for b in table._internal._tree.bind() if "Double" in b]
        assert bound, f"{label} table has no double-click binding"


@pytest.mark.gui
def test_row_double_click_ignores_group_header(shown_app):
    """A group header carries no record, so it must not emit a row event.

    Group parents are real tree items that `identify_row()` resolves, but
    `_render_grouped` never puts them in `_row_map` — so a handler guarding only
    on `if not iid` falls through to an empty record. `on_row_click` has always
    guarded on membership; `on_row_double_click` did not, and binding it
    unconditionally for #417 made that reachable on every grouped table.
    """
    seen = []
    table = bs.DataTable(rows=[dict(r) for r in ROWS], columns=["name", "role"], page_size=10)
    table.on_row_double_click(lambda e: seen.append(e))
    table.group_by("role")
    _pump(shown_app)

    tree = table._internal._tree
    header = tree.get_children("")[0]
    leaf = tree.get_children(header)[0]
    # Precondition: without a header that is genuinely absent from _row_map there
    # is nothing here to test, and the empty result below would be meaningless.
    assert header not in table._internal._row_map, "group header unexpectedly has a record"

    _double_click(tree, header)
    _pump(shown_app)
    assert seen == [], f"double-click on a group header emitted a row event: {seen!r}"

    # Control: the identical synthesis on a real row under that header must fire,
    # or the empty result above only shows the test cannot click.
    _double_click(tree, leaf)
    _pump(shown_app)
    assert len(seen) == 1, "control failed — double-click on a real row did not fire"
    assert seen[0].record["name"] == table._internal._row_map[leaf]["name"]
    assert seen[0].id is not None
