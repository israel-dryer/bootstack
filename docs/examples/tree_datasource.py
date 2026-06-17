"""Tree — data-source backing (flat adjacency list projected as a hierarchy).

A data-source-backed tree stores flat records that each point at their parent
via a `parent_field` (an adjacency list). The tree loads one branch at a time —
a node's children are queried only when it is expanded — so even a very large
hierarchy shows instantly. Any data source works; this demo uses an in-memory
source and a SQLite source side by side.

Run with:
    python docs/examples/tree_datasource.py
"""

import bootstack as bs

from bootstack.data import MemoryDataSource, SqliteDataSource
# A flat org chart: every row carries its own id and its parent's id.
# parent_id is None for the roots.
ORG = [
    {"id": 1, "parent_id": None, "name": "Engineering", "kind": "team"},
    {"id": 2, "parent_id": 1, "name": "Platform", "kind": "team"},
    {"id": 3, "parent_id": 1, "name": "Product", "kind": "team"},
    {"id": 4, "parent_id": 2, "name": "Ada Lovelace", "kind": "person"},
    {"id": 5, "parent_id": 2, "name": "Alan Turing", "kind": "person"},
    {"id": 6, "parent_id": 3, "name": "Grace Hopper", "kind": "person"},
    {"id": 7, "parent_id": None, "name": "Design", "kind": "team"},
    {"id": 8, "parent_id": 7, "name": "Don Norman", "kind": "person"},
]

ICONS = {"team": "people-fill", "person": "person-fill"}


with bs.App(title="Tree — data source", padding=20, gap=16, minsize=(760, 520)) as app:
    with bs.Grid(columns=2, gap=20, grow=True, horizontal="stretch"):

        # In-memory source, simple field mapping. Folders (teams) get a chevron;
        # leaf people do not — decided by a batched has-children check per expand.
        with bs.Column(gap=6):
            bs.Label("MemoryDataSource", font="heading-sm")
            mem = MemoryDataSource()
            mem.load([dict(r) for r in ORG])
            bs.Tree(
                data_source=mem,
                parent_field="parent_id",
                label_field="name",
                order="name",
                grow=True, horizontal="stretch",
            )

        # SQLite source with a node_builder for computed labels + icons.
        with bs.Column(gap=6):
            bs.Label("SqliteDataSource + node_builder", font="heading-sm")
            db = SqliteDataSource()
            db.load([dict(r) for r in ORG])
            tree = bs.Tree(
                data_source=db,
                parent_field="parent_id",
                node_builder=lambda r: {
                    "label": r["name"],
                    "icon": ICONS.get(r["kind"], "dot"),
                },
                order="name",
                accent="primary",
                grow=True, horizontal="stretch",
            )
            tree.on_activate(lambda n: print("activated:", n.data.get("name")))

app.run()
