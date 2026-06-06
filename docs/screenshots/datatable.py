import bootstack as bs

COLUMNS = [
    {"text": "Name",     "key": "name",     "width": 150},
    {"text": "Role",     "key": "role",     "width": 150},
    {"text": "Dept",     "key": "dept",     "width": 110},
    {"text": "Location", "key": "location", "width": 100},
    {"text": "Salary",   "key": "salary",   "width": 100,
     "anchor": "e", "format": "${:,.0f}"},
]

_PEOPLE = [
    ("Ada Lovelace",      "Staff Engineer",     "Engineering", "London"),
    ("Alan Turing",       "Software Engineer",  "Engineering", "London"),
    ("Grace Hopper",      "Engineering Lead",   "Engineering", "New York"),
    ("Katherine Johnson", "Data Scientist",     "Engineering", "Remote"),
    ("Carol Williams",    "Product Designer",   "Design",      "Berlin"),
    ("David Kim",         "Product Designer",   "Design",      "Tokyo"),
    ("Eva Martinez",      "Account Executive",  "Sales",       "New York"),
    ("Frank Wong",        "Sales Manager",      "Sales",       "Remote"),
    ("Grace Lee",         "Support Specialist", "Support",     "London"),
    ("Henry Ford",        "Support Specialist", "Support",     "Berlin"),
    ("Iris Chen",         "Content Strategist", "Marketing",   "Tokyo"),
    ("Jack Brown",        "Account Executive",  "Sales",       "New York"),
    ("Karen Davis",       "Software Engineer",  "Engineering", "Berlin"),
    ("Leo Nakamura",      "QA Engineer",        "Engineering", "Tokyo"),
    ("Mia Rossi",         "UX Researcher",      "Design",      "Milan"),
    ("Noah Schmidt",      "Visual Designer",    "Design",      "Berlin"),
    ("Olivia Park",       "Account Executive",  "Sales",       "Seoul"),
    ("Paul Andersson",    "Sales Engineer",     "Sales",       "Stockholm"),
    ("Quinn Murphy",      "Support Lead",       "Support",     "Dublin"),
    ("Rosa Gomez",        "Support Specialist", "Support",     "Madrid"),
    ("Sam Okafor",        "Growth Marketer",    "Marketing",   "Lagos"),
    ("Tara Singh",        "Content Strategist", "Marketing",   "Mumbai"),
    ("Umar Farouk",       "Platform Engineer",  "Engineering", "Cairo"),
    ("Vera Novak",        "Data Engineer",      "Engineering", "Prague"),
    ("Will Carter",       "Product Designer",   "Design",      "Austin"),
    ("Xenia Petrova",     "Brand Designer",     "Design",      "Lisbon"),
    ("Yara Haddad",       "Account Manager",    "Sales",       "Dubai"),
    ("Zane Mitchell",     "Sales Manager",      "Sales",       "Sydney"),
    ("Amara Diallo",      "Support Specialist", "Support",     "Paris"),
    ("Bruno Costa",       "SEO Specialist",     "Marketing",   "São Paulo"),
]

ROWS = [
    {"name": n, "role": r, "dept": d, "location": loc, "salary": 70_000 + i * 5_500}
    for i, (n, r, d, loc) in enumerate(_PEOPLE)
]

SIZE = (820, 440)


def _table(**kwargs):
    opts = dict(columns=COLUMNS, rows=ROWS, striped=True, fill="both", expand=True)
    opts.update(kwargs)
    return bs.DataTable(**opts)


def hero():
    with bs.App(title="Table", size=SIZE, padding=12) as app:
        t = _table(
            selection_mode="multi",
            show_selection_controls=True,
            allow_add=True, allow_edit=True, allow_delete=True,
            allow_export=True, allow_group=True,
        )
    t._internal.set_sorting("name", True)   # show a sorted column in the hero
    t.select_rows([4, 5])                    # two checked rows to show the controls
    app.run()


def selection():
    with bs.App(title="Table — Selection", size=SIZE, padding=12) as app:
        t = _table(selection_mode="multi", show_selection_controls=True)
    t.select_rows([1, 2, 4])
    app.run()


def search():
    with bs.App(title="Table — Search", size=SIZE, padding=12) as app:
        t = _table(searchable=True)
    t.set_search("Engineering")
    app.run()


def column_filter():
    with bs.App(title="Table — Filter", size=SIZE, padding=12) as app:
        t = _table(allow_filter=True)
    iv = t._internal
    iv._column_filters["dept"] = ["Engineering"]
    iv._apply_where()
    app.run()


def sort():
    with bs.App(title="Table — Sort", size=SIZE, padding=12) as app:
        t = _table()
    t._internal.set_sorting("salary", False)   # descending
    app.run()


def group():
    with bs.App(title="Table — Group", size=SIZE, padding=12) as app:
        t = _table(allow_group=True)
    t._internal.set_grouping("dept")
    app.run()


# Popup scenes pin a fixed-size table to the top-left of the window and add room
# only where an anchored menu needs it (extra width on the right for the export
# popdown), so the menu is captured without bloating the image.
TABLE_BOX = (820, 360)
POPUP_WINDOW = (980, 396)   # width: right room for popdowns; height: hugs the table


def export():
    with bs.App(title="Table — Export", size=POPUP_WINDOW, padding=16) as app:
        with bs.VStack(width=TABLE_BOX[0], height=TABLE_BOX[1], anchor="nw"):
            t = _table(selection_mode="multi", allow_export=True,
                       fill="both", expand=True)
    t.select_rows([1, 2])   # menu labels read "selection (2)"
    app.tk.after(850, t._internal._export_btn.show_menu)
    app.run()


def row_menu():
    # Tall window: the row menu (sort/filter/hide/move/delete) is long, so it
    # needs vertical room to drop fully below the clicked row.
    with bs.App(title="Table — Row menu", size=(820, 600), padding=16) as app:
        t = _table(selection_mode="multi", allow_filter=True, allow_delete=True,
                   fill="both", expand=True)
    iv = t._internal

    def open_menu():
        iids = iv._tree.get_children("")
        if not iids:
            return
        iid = iids[1]                             # row 2 — leaves room for the menu
        iv._tree.selection_set(iid)
        iv._row_menu_col = 1                      # the Role column
        bbox = iv._tree.bbox(iid, "#2")
        if bbox:
            x = iv._tree.winfo_rootx() + bbox[0] + 60
            y = iv._tree.winfo_rooty() + bbox[1] + 15
        else:
            x = iv._tree.winfo_rootx() + 140
            y = iv._tree.winfo_rooty() + 150
        iv._ensure_row_menu()
        iv._row_menu.show(position=(x, y))

    app.tk.after(850, open_menu)
    app.run()


def header_menu():
    # Tall window: the header menu (align/move/hide/group/reset/clear-sort) is
    # long, so it needs room to drop fully below the column header.
    with bs.App(title="Table — Header menu", size=(820, 600), padding=16) as app:
        t = _table(allow_filter=True, allow_group=True, fill="both", expand=True)
    iv = t._internal

    def open_menu():
        idx = 1                                   # the Role column header
        iv._header_menu_col = iv._display_columns[idx]
        iv._ensure_header_menu()
        col_id = f"#{idx + 1}"
        items = iv._tree.get_children("")
        bbox = iv._tree.bbox(items[0], col_id) if items else None
        if bbox:
            x = iv._tree.winfo_rootx() + bbox[0]
            y = iv._tree.winfo_rooty() + bbox[1] + 2
        else:
            x = iv._tree.winfo_rootx() + 150
            y = iv._tree.winfo_rooty() + 30
        iv._header_menu.show(position=(x, y))

    app.tk.after(850, open_menu)
    app.run()


def edit_record():
    with bs.App(title="Table — Edit record", size=(820, 600), padding=16) as app:
        t = _table(allow_edit=True, allow_delete=True, fill="both", expand=True)
    iv = t._internal

    def open_edit():
        # Open the actual built-in editor (modal — runs in wait_window's loop).
        record_id = t.to_rows(scope="page")[0]["id"]
        iv.edit_row(record_id)

    def lift_dialog():
        # Keep the dialog above the table, but DON'T set app._capture_target —
        # let the runner grab the whole app region so the shot shows the table
        # with the dialog centered over it.
        d = iv._active_form_dialog
        if d and d._dialog and d._dialog.toplevel:
            top = d._dialog.toplevel
            top.attributes("-topmost", True)
            top.lift()

    app.tk.after(200, open_edit)
    app.tk.after(850, lift_dialog)
    app.run()


def column_chooser():
    # Tall window: the chooser dialog drops down from the top-right button and can
    # be up to ~380px tall, so it needs vertical room below the toolbar.
    with bs.App(title="Table — Columns", size=(820, 475), padding=16) as app:
        t = _table(show_column_chooser=True, fill="both", expand=True)
    iv = t._internal

    def open_chooser():
        iv._show_column_chooser_dialog()   # modal — runs in wait_window's loop

    def lift_dialog():
        d = iv._active_chooser_dialog
        if d and d._dialog and d._dialog.toplevel:
            top = d._dialog.toplevel
            top.attributes("-topmost", True)
            top.lift()

    app.tk.after(200, open_chooser)
    app.tk.after(850, lift_dialog)
    app.run()


def density():
    # Compact density fits more rows in the same height — render at the standard
    # size so the difference from the default scenes is apparent.
    with bs.App(title="Table — Compact", size=SIZE, padding=12) as app:
        _table(density="compact")
    app.run()


SCENES = {
    "hero":      hero,
    "selection": selection,
    "search":    search,
    "filter":    column_filter,
    "sort":      sort,
    "group":     group,
    "export":    export,
    "density":        density,
    "row-menu":       row_menu,
    "header-menu":    header_menu,
    "edit":           edit_record,
    "column-chooser": column_chooser,
}


if __name__ == "__main__":
    group()   # run this file directly to preview the row menu