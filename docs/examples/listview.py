"""ListView — full feature demo.

Demonstrates item field combinations, selection controls, row features
(chevron, remove, reorder), striped rows, and density variants.

Run with:
    python docs/examples/listview.py
"""

import bootstack as bs

TEAM = [
    {"id": 1, "title": "Alice Johnson",  "text": "Engineering lead",  "icon": "person-fill"},
    {"id": 2, "title": "Bob Smith",      "text": "Product manager",   "icon": "person-fill"},
    {"id": 3, "title": "Carol Williams", "text": "Design director",   "icon": "person-fill"},
    {"id": 4, "title": "David Brown",    "text": "Data scientist",    "icon": "person-fill"},
    {"id": 5, "title": "Eva Martinez",   "text": "DevOps engineer",   "icon": "person-fill"},
    {"id": 6, "title": "Frank Lee",      "text": "QA engineer",       "icon": "person-fill"},
    {"id": 7, "title": "Grace Kim",      "text": "Tech lead",         "icon": "person-fill"},
    {"id": 8, "title": "Henry Patel",    "text": "Backend engineer",  "icon": "person-fill"},
]

ALERTS = [
    {"id": 1, "title": "Build passed",     "text": "main · 3 min ago",   "icon": "check-circle-fill"},
    {"id": 2, "title": "PR review ready",  "text": "feat/auth · 12 min", "icon": "git-pull-request"},
    {"id": 3, "title": "Deployment done",  "text": "production · 1 hr",  "icon": "rocket-takeoff-fill"},
    {"id": 4, "title": "Test suite failed","text": "staging · 2 hr ago", "icon": "x-circle-fill"},
    {"id": 5, "title": "Coverage drop",    "text": "dev · 3 hr ago",     "icon": "exclamation-circle"},
    {"id": 6, "title": "Lint warnings",    "text": "feat/ui · 4 hr ago", "icon": "exclamation-triangle"},
]

SIMPLE = [
    {"id": i, "text": f"Option {i}"}
    for i in range(1, 27)
]

with bs.App(title="ListView Demo", padding=20, gap=16, minsize=(800, 700)) as app:
    with bs.Grid(columns=2, gap=20, fill="both", expand=True, sticky_items="nsew"):

        # Column 1: Item fields
        with bs.VStack(gap=6):
            bs.Label("Item Fields", font="heading-sm")
            bs.ListView(items=TEAM, fill="both", expand=True)

        # Column 2: Multi-selection with controls
        with bs.VStack(gap=6):
            bs.Label("Multi Selection", font="heading-sm")
            sel_list = bs.ListView(
                items=SIMPLE,
                selection_mode="multi",
                show_selection_controls=True,
                accent="primary",
                fill="both", expand=True,
            )

        # Column 3: Chevron + remove button
        with bs.VStack(gap=6):
            bs.Label("Chevron + Remove", font="heading-sm")
            bs.ListView(items=ALERTS, show_chevron=True, allow_remove=True, fill="both", expand=True)

        # Column 4: Compact + striped
        with bs.VStack(gap=6):
            bs.Label("Compact + Striped", font="heading-sm")
            bs.ListView(items=SIMPLE, striped=True, density="compact", fill="both", expand=True)

# Pre-select after window is shown so TTK renders the selected state correctly
for item_id in (1, 3, 5):
    sel_list.data_source.select(item_id)
sel_list.reload()

app.run()
