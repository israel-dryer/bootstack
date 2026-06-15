"""Hero screenshot for the Displaying Data how-to.

The same set of records shown three ways — a ListView, a DataTable, and a Tree
grouped by department — side by side. Regenerate with::

    py -3.12 docs/scripts/take_screenshots.py displaying-data
"""
import bootstack as bs

PEOPLE = [
    {"id": 1, "name": "Ada Lovelace", "dept": "Engineering"},
    {"id": 2, "name": "Alan Turing", "dept": "Engineering"},
    {"id": 3, "name": "Grace Hopper", "dept": "Research"},
    {"id": 4, "name": "Katherine Johnson", "dept": "Research"},
]


def _tree_nodes():
    depts: dict[str, dict] = {}
    for p in PEOPLE:
        depts.setdefault(p["dept"], {"label": p["dept"], "icon": "folder", "children": []})
        depts[p["dept"]]["children"].append({"label": p["name"], "icon": "person"})
    return list(depts.values())


def collections():
    with bs.App(title="Displaying data", size=(720, 490), padding=16, gap=20) as app:
        with bs.HStack(fill="x", height=200, gap=16):
            with bs.VStack(fill="both", expand=True, gap=6):
                bs.Label("ListView", font="caption", accent="secondary")
                bs.ListView(
                    items=[{"id": p["id"], "title": p["name"], "text": p["dept"]} for p in PEOPLE],
                    selection_mode="single",
                    density="compact",
                    fill="both", expand=True,
                )
            with bs.VStack(fill="both", expand=True, gap=6):
                bs.Label("Tree", font="caption", accent="secondary")
                tree = bs.Tree(nodes=_tree_nodes(), density="compact", fill="both", expand=True)
                tree.expand_all()
        with bs.VStack(fill="x", gap=6):
            bs.Label("DataTable", font="caption", accent="secondary")
            bs.DataTable(
                columns=[
                    {"key": "name", "text": "Name", "width": 200},
                    {"key": "dept", "text": "Department", "width": 160},
                ],
                rows=PEOPLE,
                density="compact",
                page_size=4,
                searchable=False,
                fill="x",
            )
    app.run()


SCENES = {
    "collections": collections,
}
