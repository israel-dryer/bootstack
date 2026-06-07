"""Tree — full feature demo.

Demonstrates declarative nodes, icons (including open/closed folder variants),
expand/collapse, multi-select with tri-state cascade controls, striped/compact
density, lazy loading, and a per-node context menu.

Run with:
    python docs/examples/tree.py
"""

import bootstack as bs

# A declarative file tree. Folders use open/closed icon variants.
PROJECT = [
    {
        "label": "src",
        "open_icon": "folder2-open",
        "closed_icon": "folder-fill",
        "expanded": True,
        "children": [
            {
                "label": "bootstack",
                "open_icon": "folder2-open",
                "closed_icon": "folder-fill",
                "expanded": True,
                "children": [
                    {"label": "app.py", "icon": "file-earmark-code"},
                    {"label": "button.py", "icon": "file-earmark-code"},
                    {"label": "tree.py", "icon": "file-earmark-code"},
                ],
            },
            {"label": "__init__.py", "icon": "file-earmark-code"},
        ],
    },
    {
        "label": "docs",
        "open_icon": "folder2-open",
        "closed_icon": "folder-fill",
        "children": [
            {"label": "index.rst", "icon": "file-earmark-text"},
            {"label": "tree.rst", "icon": "file-earmark-text"},
        ],
    },
    {"label": "README.md", "icon": "file-earmark-text"},
]

# An outline — every undisplayed attribute rides along in node.data.
OUTLINE = [
    {"label": f"Chapter {i}", "icon": "bookmark", "expanded": True, "page": i * 10,
     "children": [
         {"label": f"Section {i}.{j}", "icon": "file-text", "page": i * 10 + j}
         for j in range(1, 4)
     ]}
    for i in range(1, 4)
]


def load_users(node):
    """Lazy loader — children fetched on first expand."""
    return [
        {"label": f"User {i}", "icon": "person-fill", "user_id": 100 + i}
        for i in range(1, 6)
    ]


with bs.App(title="Tree Demo", padding=20, gap=16, minsize=(900, 640)) as app:
    with bs.Grid(columns=2, gap=20, fill="both", expand=True, sticky_items="nsew"):

        # Column 1: file tree with open/closed folder icons
        with bs.VStack(gap=6):
            bs.Label("Icons + Nesting", font="heading-sm")
            bs.Tree(nodes=PROJECT, fill="both", expand=True)

        # Column 2: multi-select with tri-state cascade controls
        with bs.VStack(gap=6):
            bs.Label("Multi-Select + Cascade", font="heading-sm")
            bs.Tree(
                nodes=PROJECT,
                selection_mode="multi",
                show_selection_controls=True,
                accent="primary",
                fill="both", expand=True,
            )

        # Column 3: striped + compact density (data rides in node.data)
        with bs.VStack(gap=6):
            bs.Label("Striped + Compact", font="heading-sm")
            outline = bs.Tree(
                nodes=OUTLINE, striped=True, density="compact",
                accent="success", fill="both", expand=True,
            )
            outline.on_activate(lambda n: print("page", n.data.get("page")))

        # Column 4: lazy loading + context menu
        with bs.VStack(gap=6):
            bs.Label("Lazy Loading + Menu", font="heading-sm")
            lazy = bs.Tree(fill="both", expand=True)
            lazy.add("Team", icon="people-fill", loader=load_users)
            lazy.add("Guests", icon="people", loader=load_users)

            def build_menu(node, menu):
                menu.add_item("Reveal", icon="eye", on_click=lambda: lazy.reveal(node))
                menu.add_item("Remove", icon="trash", on_click=lambda: lazy.remove(node))

            lazy.set_context_menu(build_menu)

app.run()
