"""Master–detail (tree) — a hierarchy drives a detail view (a file explorer).

``tree_nav`` projects a flat adjacency-list source (each row names its parent) as
a hierarchy; ``@shell.detail`` renders the selected node, received as a record
dict. A folders → file-details browser is the archetypal tree screen. A tree opens
with nothing selected, so a placeholder shows until a node is picked.
"""
import bootstack as bs
from bootstack.data import MemoryDataSource

files = MemoryDataSource().load([
    {"id": "src", "name": "src", "parent_id": None, "icon": "folder", "kind": "Folder", "size": ""},
    {"id": "app", "name": "app.py", "parent_id": "src", "icon": "filetype-py", "kind": "Python source", "size": "4.2 KB"},
    {"id": "utils", "name": "utils.py", "parent_id": "src", "icon": "filetype-py", "kind": "Python source", "size": "1.8 KB"},
    {"id": "docs", "name": "docs", "parent_id": None, "icon": "folder", "kind": "Folder", "size": ""},
    {"id": "readme", "name": "README.md", "parent_id": "docs", "icon": "filetype-md", "kind": "Markdown", "size": "920 B"},
    {"id": "license", "name": "LICENSE", "parent_id": None, "icon": "file-earmark", "kind": "Text", "size": "1.1 KB"},
])

with bs.AppShell(title="Files", size=(900, 580)) as shell:
    shell.commandbar.add_label("Project", font="heading-md")
    shell.commandbar.add_spacer()
    shell.commandbar.add_button(icon="circle-half", on_click=bs.toggle_theme)

    shell.tree_nav(
        source=files,
        parent_field="parent_id",
        label_field="name",
        placeholder="Select a file",
    )

    @shell.detail
    def show(node):
        with bs.VStack(fill="both", expand=True, anchor_items="w", gap=12, padding=20):
            bs.Label(node["text"], font="heading-lg")
            bs.Label(node.get("kind", ""), font="caption")
            if node.get("size"):
                bs.Label(f"Size: {node['size']}")

shell.run()
