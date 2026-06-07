"""GUI tests for the public Tree widget.

Covers the node-handle identity model, declarative + imperative building,
mutation, expand/collapse, lazy loading, single/multi selection with the
tri-state cascade, events, and the per-node context menu.

The suite uses a single shown ``bs.App`` for the whole module — the test
runner crashes if multiple Apps are created in one process.
"""
from __future__ import annotations

import pytest

import bootstack as bs
from bootstack.widgets.tree import TreeNode


PROJECT = [
    {
        "label": "src",
        "icon": "folder-fill",
        "expanded": True,
        "children": [
            {"label": "app.py", "icon": "file-earmark-code"},
            {"label": "tree.py", "icon": "file-earmark-code", "badge": "new"},
        ],
    },
    {"label": "README.md", "icon": "file-earmark-text", "status": "draft"},
]


@pytest.fixture(scope="module")
def shown_app():
    """A single shown App so child widgets get mapped and styles build."""
    app = bs.App()
    app.__enter__()
    root = app._tk_root
    root.deiconify()
    root.update_idletasks()
    try:
        yield app
    finally:
        try:
            app.__exit__(None, None, None)
        except Exception:
            pass
        try:
            root.destroy()
        except Exception:
            pass


def _pump(app) -> None:
    root = app._tk_root
    root.update_idletasks()
    root.update()


def _roots(tree) -> list[TreeNode]:
    return tree._internal._roots


# --------------------------------------------------------------------------- building


@pytest.mark.gui
def test_declarative_nodes_build_hierarchy(shown_app):
    tree = bs.Tree(nodes=PROJECT)
    _pump(shown_app)

    roots = _roots(tree)
    assert [n.label for n in roots] == ["src", "README.md"]
    src = roots[0]
    assert [c.label for c in src.children] == ["app.py", "tree.py"]
    assert src.expanded is True
    # `badge` is no longer a display param — it folds into the data bag (nothing
    # is lost), and there's no `badge` attribute on the node.
    assert src.children[1].data["badge"] == "new"
    assert not hasattr(src.children[1], "badge")


@pytest.mark.gui
def test_unrecognized_keys_fold_into_data(shown_app):
    tree = bs.Tree(nodes=PROJECT)
    _pump(shown_app)

    readme = _roots(tree)[1]
    assert readme.data["status"] == "draft"
    # A recognized display key never leaks into the bag.
    assert "label" not in readme.data


@pytest.mark.gui
def test_add_returns_handle_and_nests(shown_app):
    tree = bs.Tree()
    src = tree.add("src", icon="folder-fill")
    child = tree.add("app.py", parent=src)
    via_node = src.add("button.py")
    _pump(shown_app)

    assert isinstance(src, TreeNode)
    assert child.parent is src
    assert via_node.parent is src
    assert [c.label for c in src.children] == ["app.py", "button.py"]
    assert src.depth == 0 and child.depth == 1


@pytest.mark.gui
def test_node_identity_not_value_equality(shown_app):
    tree = bs.Tree()
    a = tree.add("dup")
    b = tree.add("dup")
    assert a is not b
    assert a != b


@pytest.mark.gui
def test_insert_move_remove_clear(shown_app):
    tree = bs.Tree()
    src = tree.add("src")
    a = tree.add("a.py", parent=src)
    b = tree.add("b.py", parent=src)
    first = tree.insert(0, "first.py", parent=src)
    _pump(shown_app)
    assert [c.label for c in src.children] == ["first.py", "a.py", "b.py"]

    tree.move(a, parent=None)
    _pump(shown_app)
    assert a.parent is None
    assert a in _roots(tree)
    assert a not in src.children

    tree.remove(b)
    _pump(shown_app)
    assert b not in src.children

    tree.clear()
    _pump(shown_app)
    assert _roots(tree) == []


@pytest.mark.gui
def test_move_into_own_descendant_raises(shown_app):
    """Moving a node into its own subtree would create a cycle (infinite
    re-flatten); it must be rejected, not hang."""
    tree = bs.Tree()
    a = tree.add("a")
    b = tree.add("b", parent=a)
    c = tree.add("c", parent=b)
    _pump(shown_app)

    with pytest.raises(ValueError):
        tree.move(a, parent=c)        # a -> grandchild of a
    with pytest.raises(ValueError):
        tree.move(a, parent=a)        # a -> itself
    # The tree is unchanged.
    assert a.parent is None and c.parent is b


@pytest.mark.gui
def test_roots_walk_find_expose_handles(shown_app):
    """Declarative construction returns no handles; roots/walk/find recover
    them."""
    tree = bs.Tree(nodes=PROJECT)
    _pump(shown_app)

    assert [n.label for n in tree.roots] == ["src", "README.md"]
    assert {n.label for n in tree.walk()} == {
        "src", "app.py", "tree.py", "README.md"
    }
    found = tree.find(lambda n: n.label == "tree.py")
    assert found is not None and found.label == "tree.py"
    assert tree.find(lambda n: n.label == "missing") is None


@pytest.mark.gui
def test_toggle(shown_app):
    tree = bs.Tree(nodes=PROJECT)
    _pump(shown_app)
    src = tree.roots[0]
    assert src.expanded is True

    tree.toggle(src)
    _pump(shown_app)
    assert src.expanded is False

    tree.toggle(src)
    _pump(shown_app)
    assert src.expanded is True


@pytest.mark.gui
def test_prebuilt_node_subtree_attaches_recursively(shown_app):
    """A pre-built TreeNode passed as a spec must attach the WHOLE subtree to
    the tree, so deep descendants' convenience methods work (not just one
    level deep)."""
    root = TreeNode("root")
    child = TreeNode("child")
    grandchild = TreeNode("grandchild")
    child.children.append(grandchild)
    grandchild.parent = child
    root.children.append(child)
    child.parent = root

    tree = bs.Tree(nodes=[root])
    _pump(shown_app)

    internal = tree._internal
    assert root._tree is internal
    assert child._tree is internal
    assert grandchild._tree is internal
    # A deep descendant's convenience method routes to the tree (no RuntimeError).
    grandchild.expand()


@pytest.mark.gui
def test_destroy_is_clean(shown_app):
    """Destroy must not raise even with a context menu attached and relayout
    callbacks freshly scheduled."""
    tree = bs.Tree(nodes=PROJECT)
    tree.set_context_menu(lambda node, menu: menu.add_item("X", on_click=lambda: None))
    tree.destroy()
    _pump(shown_app)
    assert tree._ctx_sub is None


# --------------------------------------------------------------------------- expansion


@pytest.mark.gui
def test_expand_collapse(shown_app):
    tree = bs.Tree(nodes=PROJECT)
    _pump(shown_app)
    src = _roots(tree)[0]

    tree.collapse(src)
    _pump(shown_app)
    assert src.expanded is False

    tree.expand(src)
    _pump(shown_app)
    assert src.expanded is True


@pytest.mark.gui
def test_expand_all_collapse_all(shown_app):
    tree = bs.Tree(nodes=PROJECT)
    _pump(shown_app)

    tree.collapse_all()
    _pump(shown_app)
    assert all(not n.expanded for n in _roots(tree))

    tree.expand_all()
    _pump(shown_app)
    assert _roots(tree)[0].expanded is True


# --------------------------------------------------------------------------- lazy loading


@pytest.mark.gui
def test_lazy_loader_runs_once_on_expand(shown_app):
    calls = []

    def loader(node):
        calls.append(node)
        return [{"label": "child-1"}, {"label": "child-2"}]

    tree = bs.Tree()
    node = tree.add("lazy", loader=loader)
    _pump(shown_app)

    # Loader has not run yet, but the node reports itself as expandable.
    assert calls == []
    assert node.expandable is True
    assert node.is_leaf is False

    tree.expand(node)
    _pump(shown_app)
    assert len(calls) == 1
    assert [c.label for c in node.children] == ["child-1", "child-2"]

    # Re-expanding does not re-fetch.
    tree.collapse(node)
    tree.expand(node)
    _pump(shown_app)
    assert len(calls) == 1


@pytest.mark.gui
def test_reload_children_refetches(shown_app):
    counter = {"n": 0}

    def loader(node):
        counter["n"] += 1
        return [{"label": f"v{counter['n']}"}]

    tree = bs.Tree()
    node = tree.add("lazy", loader=loader)
    tree.expand(node)
    _pump(shown_app)
    assert [c.label for c in node.children] == ["v1"]

    tree.reload_children(node)
    _pump(shown_app)
    assert [c.label for c in node.children] == ["v2"]


@pytest.mark.gui
def test_expand_all_loads_deep_lazy(shown_app):
    """expand_all must keep loading/expanding until deep lazy levels appear,
    not stop after one pass."""
    def inner_loader(node):
        return [{"label": "leaf"}]

    def outer_loader(node):
        return [{"label": "mid", "loader": inner_loader}]

    tree = bs.Tree()
    tree.add("root", loader=outer_loader)
    _pump(shown_app)

    tree.expand_all()
    _pump(shown_app)

    labels = {n.label for n in tree.walk()}
    assert {"root", "mid", "leaf"} <= labels


# --------------------------------------------------------------------------- selection


@pytest.mark.gui
def test_single_selection_replaces(shown_app):
    tree = bs.Tree(nodes=PROJECT, selection_mode="single")
    _pump(shown_app)
    src, readme = _roots(tree)

    tree.select(src)
    _pump(shown_app)
    assert tree.selected_nodes == [src]

    tree.select(readme)
    _pump(shown_app)
    assert tree.selected_nodes == [readme]


@pytest.mark.gui
def test_multi_selection_accumulates_and_clears(shown_app):
    tree = bs.Tree(nodes=PROJECT, selection_mode="multi")
    _pump(shown_app)
    src = _roots(tree)[0]
    a, b = src.children

    tree.select(a)
    tree.select(b)
    _pump(shown_app)
    assert set(tree.selected_nodes) >= {a, b}

    tree.deselect(a)
    _pump(shown_app)
    assert a not in tree.selected_nodes

    tree.clear_selection()
    _pump(shown_app)
    assert tree.selected_nodes == []


@pytest.mark.gui
def test_multi_select_cascades_to_descendants(shown_app):
    tree = bs.Tree(nodes=PROJECT, selection_mode="multi")
    _pump(shown_app)
    src = _roots(tree)[0]

    tree.select(src)
    _pump(shown_app)
    selected = set(tree.selected_nodes)
    # Parent + all descendants selected by the cascade.
    assert src in selected
    for child in src.children:
        assert child in selected


# --------------------------------------------------------------------------- events


@pytest.mark.gui
def test_on_selection_changed_fires_with_event(shown_app):
    tree = bs.Tree(nodes=PROJECT, selection_mode="single")
    _pump(shown_app)
    received = []
    tree.on_selection_changed(lambda e: received.append(e))

    tree.select(_roots(tree)[1])
    _pump(shown_app)

    assert received
    assert received[-1].nodes == [_roots(tree)[1]]


@pytest.mark.gui
def test_reselecting_same_node_does_not_reemit(shown_app):
    """Single-mode: re-clicking the already-selected node must not re-fire
    on_selection_changed."""
    tree = bs.Tree(nodes=PROJECT, selection_mode="single")
    _pump(shown_app)
    node = _roots(tree)[1]
    received = []
    tree.on_selection_changed(lambda e: received.append(e))

    tree.select(node)
    _pump(shown_app)
    assert len(received) == 1

    tree.select(node)        # no change
    _pump(shown_app)
    assert len(received) == 1


@pytest.mark.gui
def test_on_expand_collapse_pass_node(shown_app):
    tree = bs.Tree(nodes=PROJECT)
    _pump(shown_app)
    src = _roots(tree)[0]
    expanded, collapsed = [], []
    tree.on_expand(lambda n: expanded.append(n))
    tree.on_collapse(lambda n: collapsed.append(n))

    tree.collapse(src)
    tree.expand(src)
    _pump(shown_app)

    assert src in collapsed
    assert src in expanded


# --------------------------------------------------------------------------- context menu


@pytest.mark.gui
def test_set_context_menu_builder_invoked_per_right_click(shown_app):
    tree = bs.Tree(nodes=PROJECT)
    _pump(shown_app)
    seen = []

    def build(node, menu):
        seen.append(node)
        menu.add_item("Remove", on_click=lambda: tree.remove(node))

    tree.set_context_menu(build)
    src = _roots(tree)[0]

    # Drive the right-click path directly (no real pointer in a headless test).
    tree._show_context_menu({"node": src, "x_root": 0, "y_root": 0})
    _pump(shown_app)

    assert seen == [src]

    # Detaching removes the subscription.
    tree.set_context_menu(None)
    assert tree._ctx_sub is None
