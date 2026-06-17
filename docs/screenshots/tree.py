import bootstack as bs

# Folders use open/closed icon variants — open when expanded, closed otherwise.
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
        "expanded": True,
        "children": [
            {"label": "index.rst", "icon": "file-earmark-text"},
            {"label": "tree.rst", "icon": "file-earmark-text"},
        ],
    },
    {"label": "README.md", "icon": "file-earmark-text"},
]

OUTLINE = [
    {"label": f"Chapter {i}", "icon": "bookmark", "expanded": True, "children": [
        {"label": f"Section {i}.{j}", "icon": "file-text"} for j in range(1, 4)
    ]}
    for i in range(1, 4)
]


def hero():
    with bs.App(title="Tree", size=(400, 360), padding=20) as app:
        bs.Tree(nodes=PROJECT, show_scrollbar=False, grow=True, horizontal="stretch")
    app.run()


def selection():
    with bs.App(title="Tree — Selection", size=(400, 360), padding=20) as app:
        tree = bs.Tree(
            nodes=PROJECT,
            selection_mode="multi",
            show_selection_controls=True,
            accent="primary",
            show_scrollbar=False,
            grow=True, horizontal="stretch",
        )
    # Select a folder so the tri-state cascade marks its children + the parent.
    for node in tree._internal._roots:
        if node.label == "docs":
            tree.select(node)
    app.run()


def density():
    with bs.App(title="Tree — Density", size=(400, 360), padding=20) as app:
        bs.Tree(
            nodes=OUTLINE,
            striped=True,
            density="compact",
            accent="success",
            show_scrollbar=False,
            grow=True, horizontal="stretch",
        )
    app.run()


SCENES = {
    "hero":      hero,
    "selection": selection,
    "density":   density,
}

if __name__ == "__main__":
    hero()
