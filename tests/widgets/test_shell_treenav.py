"""Smoke test for the hierarchical tree_nav provider + @detail (step 5c).

Verifies: an inline node hierarchy mounts, a tree opens with nothing selected
(no auto-select), selecting a node renders the detail with the node normalized
to a record dict, and TreeNavProvider does not support compaction. One App/process.
"""

from __future__ import annotations

import bootstack as bs
from bootstack.widgets._impl.composites.shell import Shell, TreeNavProvider


def test_tree_nav_master_detail():
    shell = Shell(title="TreeNav")
    try:
        shell.tree_nav(nodes=[
            {"label": "Datasets", "icon": "folder", "expanded": True, "children": [
                {"label": "run_001.csv", "icon": "filetype-csv", "data": {"rows": 1024}},
                {"label": "run_002.csv", "icon": "filetype-csv", "data": {"rows": 2048}},
            ]},
            {"label": "README.md", "icon": "filetype-md"},
        ])

        seen: list[dict] = []

        @shell.detail
        def render(record):
            seen.append(record)
            bs.Label(record["text"])

        # A tree opens with nothing selected -> no auto-render.
        assert seen == []
        assert shell.current_page is None
        assert isinstance(shell.provider, TreeNavProvider)
        assert shell.provider.supports_compact is False

        # Select a leaf node -> detail renders with the normalized record dict.
        tree = shell.provider.tree
        leaf = tree.selection  # None yet
        assert leaf is None
        # Find a node to select via the public tree handle.
        datasets = tree.find(lambda n: n.label == "run_002.csv")
        assert datasets is not None
        tree.select(datasets)
        shell.update()
        assert seen, "selecting a node should render its detail"
        rec = seen[-1]
        assert rec["text"] == "run_002.csv"
        assert rec["rows"] == 2048           # node.data bag flattened into the record
        assert "id" in rec
        assert shell.content.winfo_children()
    finally:
        shell.destroy()
