"""Visual test for public ListView, Tree, and Table."""
from bootstack.widgets import (
    App, VStack, HStack, Label, Button, Separator, Tabs,
    ListView, Tree, Table,
)


PEOPLE = [
    {"id": i, "title": n, "text": r, "caption": d, "name": n, "role": r, "dept": d}
    for i, (n, r, d) in enumerate([
        ("Alice Chen",    "Engineer",  "Engineering"),
        ("Bob Smith",     "Designer",  "Design"),
        ("Carol White",   "Manager",   "Engineering"),
        ("David Lee",     "Engineer",  "Data"),
        ("Eva Brown",     "Analyst",   "Data"),
        ("Frank Kim",     "Designer",  "Design"),
        ("Grace Patel",   "Engineer",  "Engineering"),
        ("Henry Zhao",    "Manager",   "Product"),
        ("Irene Torres",  "Analyst",   "Data"),
        ("James Wilson",  "Engineer",  "Engineering"),
        ("Karen Adams",   "Designer",  "Design"),
        ("Leo Martinez",  "Engineer",  "Data"),
    ], start=1)
]


def main():
    with App(title="Data Display", minsize=(900, 620), padding=0, gap=0) as app:

        tabs = Tabs(fill="both", expand=True)

        # --- ListView tab ---
        with tabs.add("listview", label="ListView"):
            with VStack(padding=16, gap=10, fill="both", expand=True):
                Label("Virtual-scrolling list (multi-select, removable):",
                      font="heading-sm")

                lv = ListView(
                    items=PEOPLE,
                    selection_mode="multi",
                    show_selection_controls=True,
                    allow_remove=True,
                    striped=True,
                    fill="both",
                    expand=True,
                )

                lbl_sel = Label("Selected: []")

                def show_selection(_event=None):
                    selected = lv.get_selected()
                    lbl_sel.text = f"Selected: {[r['name'] for r in selected]}"

                lv.on_selection_changed(show_selection)

                with HStack(gap=8):
                    Button("Select All",    on_click=lv.select_all)
                    Button("Clear",         on_click=lv.clear_selection)
                    Button("Scroll Top",    on_click=lv.scroll_to_top)
                    Button("Scroll Bottom", on_click=lv.scroll_to_bottom)

        # --- Tree tab ---
        with tabs.add("tree", label="Tree"):
            with VStack(padding=16, gap=10, fill="both", expand=True):
                Label("Hierarchical tree with columns:", font="heading-sm")

                tv = Tree(
                    columns=["role", "dept"],
                    show="tree headings",
                    fill="both",
                    expand=True,
                )
                tv.heading("#0",    text="Name")
                tv.heading("role",  text="Role")
                tv.heading("dept",  text="Department")
                tv.column("#0",    width=200)
                tv.column("role",  width=120)
                tv.column("dept",  width=120)

                depts: dict[str, str] = {}
                for p in PEOPLE:
                    dept = p["dept"]
                    if dept not in depts:
                        iid = tv.insert("", "end", text=dept, open=True)
                        depts[dept] = iid
                    tv.insert(depts[dept], "end",
                              text=p["name"], values=(p["role"], p["dept"]))

                lbl_tv = Label("(click an item)")

                def on_tv_select(_event=None):
                    sel = tv.selection()
                    if sel:
                        it = tv.item(sel[0])
                        lbl_tv.text = f"Selected: {it['text']}"

                tv.on_select(on_tv_select)

                with HStack(gap=8):
                    Button("Expand All",
                           on_click=lambda: [tv.expand(i)
                                             for i in tv.get_children()])
                    Button("Collapse All",
                           on_click=lambda: [tv.collapse(i)
                                             for i in tv.get_children()])

        # --- Table tab ---
        with tabs.add("table", label="Table"):
            with VStack(padding=16, gap=10, fill="both", expand=True):
                Label("Sortable / filterable table:", font="heading-sm")

                tbl = Table(
                    columns=["name", "role", "dept"],
                    rows=PEOPLE,
                    selection_mode="multi",
                    searchable=True,
                    allow_filter=True,
                    striped=True,
                    fill="both",
                    expand=True,
                )

                lbl_tbl = Label("(click a row)")

                def on_tbl_click(event):
                    rec = event.data.get("record", {})
                    lbl_tbl.text = f"Clicked: {rec.get('name', '?')}"

                tbl.on_row_click(on_tbl_click)

    app.run()


if __name__ == "__main__":
    main()
