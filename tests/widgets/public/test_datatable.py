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

import types

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


_click_clock = 1000
"""Monotonic timestamp source for synthesized clicks.

Click-count detection compares each press against the previous one's time and
position, so two synthesized clicks at the same coordinates must never send time
backwards. Fixed literals did: every call started at the same value, which was
harmless only for as long as no two calls in the suite happened to share a
position. That is an order-dependent trap, and it would surface as a
double-click silently not registering — i.e. as a false "the fix is broken".
"""


def _next_click_time(step: int = 20) -> int:
    global _click_clock
    _click_clock += step
    return _click_clock


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
    first = _next_click_time()
    for t in (first, first + 20):
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
def test_group_header_double_click_opens_no_dialog(shown_app):
    """#420's user-visible harm: a spurious New Record dialog on an editable table.

    A group header fell through to an empty record, and `_open_form_dialog({})`
    takes the falsy branch and titles itself "New Record" — so double-clicking a
    header invited the user to create a row by clicking something that is not a
    row. The empty row event is the API-level symptom; this is the one a user
    actually sees, and only a probe covered it.

    The dialog is stubbed rather than opened: it is modal, and driven
    synthetically it blocks the loop forever. Recording the call is enough — what
    is under test is whether it is reached at all, and with what.
    """
    opened = []
    table = bs.DataTable(rows=[dict(r) for r in ROWS], columns=["name", "role"],
                         page_size=10, allow_edit=True)
    table.group_by("role")
    _pump(shown_app)

    impl = table._internal
    impl._open_form_dialog = lambda record=None, **kw: opened.append(record)

    tree = impl._tree
    header = tree.get_children("")[0]
    leaf = tree.get_children(header)[0]
    # Preconditions: the edit path must genuinely be live, and the header must
    # genuinely carry no record, or a clean result below means nothing.
    assert impl._editing['updating'], "editing is not enabled, so no dialog could open either way"
    assert header not in impl._row_map, "group header unexpectedly has a record"

    _double_click(tree, header)
    _pump(shown_app)
    assert opened == [], f"double-clicking a group header opened the edit dialog with {opened!r}"

    # Control: a real row must still open it, carrying that row's record — or the
    # empty result above only shows the dialog never opens at all.
    _double_click(tree, leaf)
    _pump(shown_app)
    assert len(opened) == 1, "control failed — double-clicking a real row did not open the dialog"
    assert opened[0], "control failed — the dialog opened with an empty record (the New Record path)"
    assert opened[0]["name"] == impl._row_map[leaf]["name"]


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


def _right_click(tree, iid) -> None:
    """Synthesize a right-click on a row, with the same hit-test preconditions."""
    box = tree.bbox(iid)
    assert box != "", "row has no bbox — the tree is unmapped, so this test cannot click"
    x, y = box[0] + box[2] // 2, box[1] + box[3] // 2
    assert tree.identify_row(y) == iid, "hit test missed the target row"
    tree.event_generate("<Button-3>", x=x, y=y, rootx=x + 200, rooty=y + 200)


@pytest.mark.gui
def test_row_right_click_ignores_group_header(shown_app):
    """#418: right-click on a group header emitted a row event with no record.

    Same defect as #417's, one handler over: `_on_row_context` tested only
    `if not iid` under a comment that claimed to exclude group headers. Unlike
    the double-click case this needed no unusual configuration — right-click is
    bound whenever context menus are on, which is the default — so it was live
    in 0.2.1 rather than newly exposed.

    Also asserts `_context_iid` is cleared. A header used to be recorded as the
    menu's target even though the menu never opened, leaving a later row-menu
    command pointed at a row that carries no record.
    """
    seen = []
    table = bs.DataTable(rows=[dict(r) for r in ROWS], columns=["name", "role"], page_size=10)
    table.on_row_right_click(lambda e: seen.append(e))
    table.group_by("role")
    _pump(shown_app)

    impl = table._internal
    # The row menu grabs the pointer and blocks the loop when driven
    # synthetically; it is not what is under test here.
    impl._ensure_row_menu = lambda *a, **kw: None
    impl._row_menu = types.SimpleNamespace(show=lambda *a, **kw: None)

    tree = impl._tree
    header = tree.get_children("")[0]
    leaf = tree.get_children(header)[0]
    assert header not in impl._row_map, "group header unexpectedly has a record"

    _right_click(tree, header)
    _pump(shown_app)
    assert seen == [], f"right-click on a group header emitted a row event: {seen!r}"
    assert impl._context_iid is None, "a group header was recorded as the row menu's target"

    # Control: the identical synthesis on a real row must fire, or the empty
    # result above only shows the test cannot click.
    _right_click(tree, leaf)
    _pump(shown_app)
    assert len(seen) == 1, "control failed — right-click on a real row did not fire"
    assert seen[0].record["name"] == impl._row_map[leaf]["name"]
    assert impl._context_iid == leaf


# --------------------------------------------------------------------------- click focus


def _single_click(tree, iid) -> None:
    """Synthesize one left click on a row, with the usual hit-test precondition."""
    box = tree.bbox(iid)
    assert box != "", "row has no bbox — the tree is unmapped, so this test cannot click"
    x, y = box[0] + box[2] // 2, box[1] + box[3] // 2
    assert tree.identify_row(y) == iid, "hit test missed the target row"
    tree.event_generate("<ButtonPress-1>", x=x, y=y)
    tree.event_generate("<ButtonRelease-1>", x=x, y=y)


def _park_focus(tree, app) -> None:
    """Move focus off the table so the next click is what puts it back."""
    tree._root().focus_set()
    tree.focus("")
    _pump(app)
    assert tree.focus_lastfor() is not tree, "precondition: focus did not leave the table"


@pytest.mark.gui
def test_click_takes_keyboard_focus(shown_app):
    """#421: clicking a group header left the keyboard aimed somewhere else.

    Both the group-header branch and the checkbox branch of the click handler
    answer the click and return `'break'`, which also suppresses the built-in
    handling that focuses the body and sets item focus. So the row a user had
    just clicked was not the row the arrow keys moved from.

    Asserts through `focus_lastfor()` rather than `focus_get()`: the latter
    reports nothing unless the window is the active one, which is not
    dependable in a shared-root suite and would make this pass or fail on
    whether some other window happened to be up.
    """
    table = bs.DataTable(rows=[dict(r) for r in ROWS], columns=["name", "role"], page_size=10)
    table.group_by("role")
    _pump(shown_app)

    tree = table._internal._tree
    header = tree.get_children("")[0]
    leaf = tree.get_children(header)[0]

    # Control: a plain data row has always taken focus. If this fails, the arm
    # below proves nothing about the fix — the test simply cannot click.
    _park_focus(tree, shown_app)
    _single_click(tree, leaf)
    _pump(shown_app)
    assert tree.focus_lastfor() is tree, "control failed — clicking a data row did not focus the table"
    assert tree.focus() == leaf, "control failed — clicking a data row did not set item focus"

    _park_focus(tree, shown_app)
    _single_click(tree, header)
    _pump(shown_app)
    assert tree.focus_lastfor() is tree, "clicking a group header did not focus the table"
    assert tree.focus() == header, "clicking a group header did not set item focus"


@pytest.mark.gui
def test_click_takes_keyboard_focus_in_checkbox_mode(shown_app):
    """#421, the wider half: with checkboxes no click focused the table at all.

    The checkbox branch returns `'break'` on every body click, so this affected
    ordinary data rows rather than only group headers, leaving Tab as the only
    way to start driving the table from the keyboard.
    """
    table = bs.DataTable(
        rows=[dict(r) for r in ROWS], columns=["name", "role"], page_size=10,
        selection_mode="multi", show_selection_controls=True,
    )
    _pump(shown_app)

    tree = table._internal._tree
    row = tree.get_children("")[0]
    # Precondition: without the checkbox branch actually being active this is
    # only a re-run of the plain data-row control above.
    assert table._internal._toggle_select_active(), "checkbox click handling is not active"

    _park_focus(tree, shown_app)
    _single_click(tree, row)
    _pump(shown_app)

    assert tree.focus_lastfor() is tree, "clicking a row in checkbox mode did not focus the table"
    assert tree.focus() == row, "clicking a row in checkbox mode did not set item focus"


def _find_separator(tree) -> tuple[int, int]:
    """Scan the heading strip for a point ttk reports as a column separator."""
    for y in (4, 8, 12):
        for x in range(2, int(tree.winfo_width()) - 2):
            if tree.identify_region(x, y) == "separator":
                return x, y
    raise AssertionError("no column separator found — the tree is too narrow or unmapped")


def _drag(tree, x: int, y: int, dx: int) -> None:
    tree.event_generate("<ButtonPress-1>", x=x, y=y)
    tree.event_generate("<B1-Motion>", x=x + dx, y=y)
    tree.event_generate("<ButtonRelease-1>", x=x + dx, y=y)


@pytest.mark.gui
def test_column_resize_survives_checkbox_mode(shown_app):
    """#421: the checkbox branch stopped clicks that were never its business.

    A press on a column separator reports no row, but the branch returned
    `'break'` regardless, swallowing the press that starts ttk's resize drag.
    Column resizing was dead on every table showing selection checkboxes.

    The plain table is the control: it shares the drag synthesis, so if it
    fails to resize the checkbox arm proves nothing about the fix.
    """
    plain = bs.DataTable(rows=[dict(r) for r in ROWS], columns=["name", "role"], page_size=10)
    checkbox = bs.DataTable(
        rows=[dict(r) for r in ROWS], columns=["name", "role"], page_size=10,
        selection_mode="multi", show_selection_controls=True,
    )
    _pump(shown_app)

    assert not plain._internal._toggle_select_active(), "the control table is in checkbox mode"
    assert checkbox._internal._toggle_select_active(), "checkbox click handling is not active"

    widths = {}
    for label, table in (("control", plain), ("checkbox", checkbox)):
        tree = table._internal._tree
        cols = ("#0", "#1", "#2")
        x, y = _find_separator(tree)
        before = {c: tree.column(c, "width") for c in cols}
        _drag(tree, x, y, 36)
        _pump(shown_app)
        after = {c: tree.column(c, "width") for c in cols}
        widths[label] = [c for c in cols if before[c] != after[c]]

    assert widths["control"], "control failed — dragging a separator resized nothing at all"
    assert widths["checkbox"], "dragging a separator in checkbox mode resized nothing"


# --------------------------------------------------------------------------- group chevrons


def _chevron_state(impl, iid) -> tuple[bool, bool]:
    """Return (group is open, chevron is drawn as open) for a group header."""
    opened = bool(int(impl._tree.item(iid, "open") or 0))
    image = impl._tree.item(iid, "image")
    if isinstance(image, (list, tuple)):
        image = image[0] if image else ""
    return opened, str(image) == str(impl._chevron_icon(True))


def _grouped_table(shown_app, *, opened: bool):
    """A grouped table plus its first group header, in `opened` state and in sync.

    The starting state is a parameter because it decides whether a test can see
    the defect at all: only the *expand* direction desyncs, so a test that ends
    up collapsing proves nothing. A double-click nets two toggles, so it has to
    start open to finish on an expand.

    Set directly rather than by synthesizing an action: the setup must not
    depend on the mechanism under test, and setting `open` fires no
    notification, so it cannot mask the defect either.
    """
    table = bs.DataTable(rows=[dict(r) for r in ROWS], columns=["name", "role"], page_size=10)
    table.group_by("role")
    _pump(shown_app)

    impl = table._internal
    header = impl._tree.get_children("")[0]
    impl._tree.focus_set()
    impl._tree.focus(header)
    impl._tree.selection_set(header)
    impl._tree.item(header, open=opened, image=impl._chevron_icon(opened))
    _pump(shown_app)

    # Precondition: the setup itself must be in sync, or a desync below proves
    # nothing about the action under test.
    assert _chevron_state(impl, header) == (opened, opened), "setup left the group out of sync"
    return table, impl, header


@pytest.mark.gui
@pytest.mark.parametrize("routine, keys", [
    ("ToggleFocus", "space / Return"),
    ("Keynav right", "Right"),
])
def test_group_chevron_tracks_keyboard_expand(shown_app, routine, keys):
    """#419: a keyboard-driven expand repainted the previous chevron.

    `_refresh_group_chevrons` is bound to the open/close notifications and read
    the item's state synchronously. The toolkit reports an expand *before* it
    records it (its collapse path sets the state first), so the handler saw the
    stale value and drew a collapsed chevron on an open group. Reachable in
    0.2.1 from the keyboard alone: the body takes focus from a click on a data
    row or from Tab, and arrow keys then step onto the header.

    Both routines are covered because the expand keys are not one path — space
    and Return route through the toggle, while Right calls the open routine
    directly, so a fix applied at the toggle alone would leave Right broken.

    Drives the routine each key is bound to rather than synthesizing the key.
    A synthesized key is silently dropped once earlier tests have filled the
    shared root and the table is no longer mapped, which showed up as this test
    failing about one run in five with its own control tripping — the failure
    mode this suite is known for. The key-to-routine mapping belongs to the
    toolkit's binding table, not to us; what this test owns is what happens once
    the notification arrives, and that is reproduced exactly.
    """
    _table, impl, header = _grouped_table(shown_app, opened=False)

    # Both routines act on whichever item holds focus.
    impl._tree.focus(header)
    _pump(shown_app)
    assert impl._tree.focus() == header, "precondition: the group header does not hold item focus"

    if routine == "ToggleFocus":
        impl._tree.tk.call("ttk::treeview::ToggleFocus", impl._tree)
    else:
        impl._tree.tk.call("ttk::treeview::Keynav", impl._tree, "right")
    _pump(shown_app)

    opened, chevron_open = _chevron_state(impl, header)
    assert opened, f"control failed — {routine} ({keys}) did not expand the group"
    assert chevron_open, f"group expanded via {routine} ({keys}) but its chevron is drawn collapsed"


@pytest.mark.gui
def test_group_chevron_tracks_double_click(shown_app):
    """#419, via the path #417 opened up on read-only tables.

    Binding `<Double-1>` unconditionally means the second press of a
    double-click resolves to the double-click handler instead of the click
    handler, so the click handler's `'break'` no longer suppresses the built-in
    expand — which routes through the same stale-state notification above.

    Starts open deliberately. A double-click nets two toggles, so from a
    collapsed start it finishes on a *collapse*, which was never broken — the
    test would pass against the unfixed code and prove nothing. Starting open
    means the second toggle is the expand that desyncs. The net open state is
    unchanged either way; the chevron is what breaks.
    """
    _table, impl, header = _grouped_table(shown_app, opened=True)

    _double_click(impl._tree, header)
    _pump(shown_app)

    opened, chevron_open = _chevron_state(impl, header)
    assert opened, "control failed — the double-click did not leave the group expanded"
    assert chevron_open, "group is expanded after a double-click but its chevron is drawn collapsed"


# --------------------------------------------------------------------------- context menus

# #456: `context_menus` was documented on the public widget and taught in
# `docs/widgets/datatable.rst`, but was not a parameter of `DataTable.__init__`.
# It fell into `**kwargs`, went to `_split_layout_kwargs` as though it were a
# layout option, and was discarded without error -- so every table kept the
# default `'all'` and `context_menus='none'` still showed both menus.
#
# The internal was never at fault (control in
# `development/probe_456_context_menus.py`), so these assert the wrapper
# forwards the value, through the two predicates the click path consults rather
# than the raw attribute.

CONTEXT_MENU_GATES = [
    ("all", True, True),
    ("headers", True, False),
    ("rows", False, True),
    ("none", False, False),
]


@pytest.mark.parametrize("value,header,row", CONTEXT_MENU_GATES, ids=[c[0] for c in CONTEXT_MENU_GATES])
def test_context_menus_reaches_the_header_and_row_gates(app, value, header, row):
    table = bs.DataTable(columns=["name"], rows=[{"name": "Ada"}], context_menus=value)
    impl = table._internal

    assert impl._header_context_enabled() is header
    assert impl._row_context_enabled() is row


def test_context_menus_defaults_to_all(app):
    """The compatibility invariant: an omitted argument must not change anything.

    Every DataTable ever constructed passes through this path, so a default that
    drifted would turn a fix into a silent behavior change for every caller.
    """
    table = bs.DataTable(columns=["name"], rows=[{"name": "Ada"}])
    impl = table._internal

    assert impl._context_menus == "all"
    assert impl._header_context_enabled() is True
    assert impl._row_context_enabled() is True


def test_context_menus_none_leaves_the_right_click_handler_unbound(app):
    """The strongest observable, and the closest to what the reporter sees.

    `'none'` is the one value that skips `bind_right_click` entirely
    (tableview.py:1160), so no handler exists to open a menu. `<Button-3>` is
    bound on every windowing system by that helper -- the extra aqua sequences
    are additive -- and it is the only right-click binding the tree carries, so
    reading it is unambiguous on all three platforms.
    """
    disabled = bs.DataTable(columns=["name"], rows=[{"name": "Ada"}], context_menus="none")
    enabled = bs.DataTable(columns=["name"], rows=[{"name": "Ada"}], context_menus="all")

    # Control first: the binding is observable at all through this route.
    assert enabled._internal._tree.bind("<Button-3>"), "control failed — no right-click binding to detect"
    assert not disabled._internal._tree.bind("<Button-3>")
