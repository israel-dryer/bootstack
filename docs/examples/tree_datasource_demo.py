"""Tree — data-source backing, lazy loading at scale (interactive demo).

Generates a ~5,000-node org chart as a FLAT adjacency list (every row carries
its own id and its parent's id), loads it into a SqliteDataSource, and projects
it as a hierarchy with `bs.Tree(data_source=...)`.

The whole tree is in the source, but only the children of nodes you actually
expand are ever queried — so the window appears instantly and the live counter
at the top shows how few nodes are materialized vs. how many exist. Expand a few
branches and watch "queries run" tick up one-per-expand while "nodes shown"
stays tiny relative to the 5,000 in the source.

Run with:
    python docs/examples/tree_datasource_demo.py
"""

import bootstack as bs

# --------------------------------------------------------------------------- data

DIVISIONS = ["Engineering", "Design", "Sales", "Marketing",
             "Finance", "Legal", "Support", "Operations"]
FIRST = ["Ada", "Alan", "Grace", "Linus", "Margaret", "Dennis",
         "Barbara", "Ken", "Katherine", "Edsger", "Donald", "Radia"]
LAST = ["Lovelace", "Turing", "Hopper", "Torvalds", "Hamilton", "Ritchie",
        "Liskov", "Thompson", "Johnson", "Dijkstra", "Knuth", "Perlman"]


def build_org():
    """Build a flat adjacency list: division -> department -> team -> person."""
    rows = []
    nid = 0

    def add(parent_id, name, kind):
        nonlocal nid
        nid += 1
        rows.append({"id": nid, "parent_id": parent_id, "name": name, "kind": kind})
        return nid

    for d, div in enumerate(DIVISIONS):
        div_id = add(None, div, "division")
        for dep in range(6):
            dep_id = add(div_id, f"{div} Dept {dep + 1}", "department")
            for team in range(8):
                team_id = add(dep_id, f"Team {chr(65 + team)}", "team")
                for p in range(12):
                    person = f"{FIRST[(d + p) % len(FIRST)]} {LAST[(team + p) % len(LAST)]}"
                    add(team_id, person, "person")
    return rows


ICONS = {
    "division": "building",
    "department": "diagram-3",
    "team": "people-fill",
    "person": "person",
}

ROWS = build_org()

# --------------------------------------------------------------------------- ui

with bs.App(title="Tree — lazy loading at scale", padding=16, gap=12,
            size=(560, 720)) as app:

    # A SqliteDataSource holds the whole flat dataset. Wrap _query so the demo
    # can show that one query runs per expand (the framework does not need this).
    src = bs.SqliteDataSource()
    src.load([dict(r) for r in ROWS])

    stats = {"queries": 0}
    _real_query = src._query

    def _counted_query(condition, sort_keys):
        stats["queries"] += 1
        return _real_query(condition, sort_keys)

    src._query = _counted_query

    status = bs.Signal("")
    bs.Label(textsignal=status, font="body")

    tree = bs.Tree(
        data_source=src,
        parent_field="parent_id",
        node_builder=lambda r: {"label": r["name"], "icon": ICONS.get(r["kind"], "dot")},
        order="name",
        accent="primary",
        fill="both", expand=True,
    )

    def refresh_status(*_):
        materialized = sum(1 for _ in tree.walk())
        status.set(
            f"source: {len(ROWS):,} records   ·   "
            f"queries run: {stats['queries']}   ·   "
            f"nodes materialized: {materialized}"
        )

    tree.on_expand(refresh_status)
    tree.on_collapse(refresh_status)
    tree.on_activate(lambda n: print("activated:", n.data.get("name")))

    refresh_status()  # initial: only the 8 divisions are loaded

app.run()
