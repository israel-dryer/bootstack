"""Master–detail (tree) — a hierarchy drives a detail view (a file explorer).

``tree_nav`` builds the sidebar from a hierarchy and returns the `Tree` driving
it; ``@shell.detail`` renders the selected node, received as a record dict. A
folders → file-details browser is the archetypal tree screen. Here the hierarchy
is declared inline with ``nodes=`` (each node a ``{"label", "icon", "children",
...}`` spec; extra keys ride along as the node's data). For large or dynamic
hierarchies, pass ``source=`` instead — a flat adjacency-list data source where
each row names its parent.

A tree opens with nothing selected (showing the ``placeholder``); we open it
expanded with a file selected, like a real file explorer, by driving the
returned `Tree`.
"""
import bootstack as bs

tree_nodes = [
    {"label": "src", "icon": "folder", "children": [
        {"label": "app.py", "icon": "filetype-py", "kind": "Python source", "size": "4.2 KB"},
        {"label": "utils.py", "icon": "filetype-py", "kind": "Python source", "size": "1.8 KB"},
    ]},
    {"label": "tests", "icon": "folder", "children": [
        {"label": "test_app.py", "icon": "filetype-py", "kind": "Python source", "size": "2.0 KB"},
    ]},
    {"label": "docs", "icon": "folder", "children": [
        {"label": "README.md", "icon": "filetype-md", "kind": "Markdown", "size": "920 B"},
    ]},
    {"label": "LICENSE", "icon": "file-earmark", "kind": "Text", "size": "1.1 KB"},
]

with bs.AppShell(title="Files", size=(900, 580)) as shell:
    with shell.add_toolbar() as bar:
        with bar.add_menu("File") as file:
            file.add_action("New", shortcut="Mod+N", on_click=lambda: None)
            file.add_action("Open", shortcut="Mod+O", on_click=lambda: None)
            file.add_separator()
            file.add_action("Quit", shortcut="Mod+Q", on_click=shell.close)
        with bar.add_menu("View") as view:
            view.add_action("Refresh", shortcut="Mod+R", on_click=lambda: None)
        bar.add_spacer()
        bar.add_button(icon="search", on_click=lambda: None)
        bar.add_theme_toggle()

    tree = shell.tree_nav(nodes=tree_nodes, placeholder="Select a file")

    @shell.detail
    def show(node):
        with bs.Column(grow=True, horizontal="stretch", gap=12, padding=20):
            bs.Label(node["text"], font="heading-lg")
            bs.Label(node.get("kind", ""), font="caption")
            if node.get("size"):
                bs.Label(f"Size: {node['size']}")

    # Open expanded with a file selected, like a real file explorer.
    tree.expand_all()
    app = tree.find(lambda node: node.label == "app.py")
    if app is not None:
        tree.select(app)

shell.run()
