"""An open context menu closes on a click the clicked widget swallows (#207).

The themed menu closes on an outside click through a handler on the owning
window. A widget handler that returns `'break'` stops the click before the
window sees it, so these hosts must close open menus themselves: a DataTable row
click with selection controls, and a Tree row's selection control and
right-click.

The macOS menu is native and closes itself; the defect does not exist there.
"""
from __future__ import annotations

import time

import pytest

import bootstack as bs

pytestmark = [
    pytest.mark.gui,
    pytest.mark.skipif(
        __import__("sys").platform == "darwin",
        reason="the native macOS menu closes itself; show() blocks in tk_popup",
    ),
]


def _pump(root, condition, timeout=3.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        root.update()
        if condition():
            return True
        time.sleep(0.02)
    return False


def _is_open(menu) -> bool:
    # No public visibility property; read the themed backend's popup window.
    return bool(menu._internal._impl._toplevel.winfo_viewable())


def _dismiss_armed(menu) -> bool:
    # The outside-click handler binds 100 ms after show().
    return bool(menu._internal._impl._click_handler_ids)


def _clear_of(win) -> tuple[int, int]:
    """A screen point beside the window, so the click can never land inside the menu."""
    top = win._internal
    return top.winfo_rootx() + top.winfo_width() + 40, top.winfo_rooty() + 10


def test_datatable_row_click_with_selection_controls_closes_the_menu(shown_app):
    root = shown_app._tk_root
    win = bs.Window(title="207", size=(420, 320))
    try:
        with win:
            table = bs.DataTable(
                columns=["name"],
                rows=[{"id": i, "name": f"row {i}"} for i in range(4)],
                selection_mode="multi",
                show_selection_controls=True,
                context_menus="none",
                grow=True,
                horizontal="stretch",
            )
        menu = bs.ContextMenu(table)
        menu.add_item("Hello")
        tree = table._internal._tree
        win.show()
        assert _pump(root, tree.winfo_ismapped), "precondition: the table is mapped"

        iid = tree.get_children()[1]
        box = tree.bbox(iid)
        assert box != "", "precondition: the row has a bbox"
        x, y = box[0] + 20, box[1] + box[3] // 2
        assert tree.identify_row(y) == iid, "precondition: the click hits the row"

        menu.show(position=_clear_of(win))
        assert _pump(root, lambda: _dismiss_armed(menu)), "precondition: outside-click dismiss is armed"
        assert _is_open(menu), "precondition: the menu is open"

        tree.event_generate("<Button-1>", x=x, y=y)
        root.update()

        # The click took the toggle-select branch, which is the one that returns 'break'.
        assert iid in tree.selection(), "precondition: the click toggled the row"
        assert not _is_open(menu), "the menu stayed open after a swallowed row click"
    finally:
        win.close()


def test_tree_selection_control_click_closes_the_menu(shown_app):
    root = shown_app._tk_root
    win = bs.Window(title="207", size=(420, 320))
    try:
        with win:
            tree = bs.Tree(
                selection_mode="multi",
                show_selection_controls=True,
                select_on_click=False,
                grow=True,
                horizontal="stretch",
            )
            for label in ("alpha", "beta", "gamma"):
                tree.add(label)
        tree.set_context_menu(lambda node, m: m.add_item("Rename"))
        rows = tree._internal._rows
        win.show()
        assert _pump(root, lambda: rows and rows[1].winfo_ismapped()), "precondition: the rows are mapped"

        # Open the menu the way a user does: right-click a row.
        target = rows[0]
        x_root, y_root = _clear_of(win)
        target.event_generate("<Button-3>", x=5, y=5, rootx=x_root, rooty=y_root)
        menu = tree._ctx_menu
        assert menu is not None, "precondition: the right-click built the menu"
        assert _pump(root, lambda: _dismiss_armed(menu)), "precondition: outside-click dismiss is armed"
        assert _is_open(menu), "precondition: the menu is open"

        # One synthesized click per row: on Windows a repeat click on a Tree row
        # reaches none of its handlers.
        ctrl = rows[1]._select_ctrl
        assert tree.selection == [], "precondition: nothing selected"
        ctrl.event_generate("<Button-1>", x=3, y=3)
        root.update()

        assert len(tree.selection) == 1, "precondition: the control click selected the row"
        assert not _is_open(menu), "the menu stayed open after a selection-control click"
    finally:
        win.close()


def test_tree_row_right_click_closes_another_menu(shown_app):
    root = shown_app._tk_root
    win = bs.Window(title="207", size=(420, 320))
    try:
        with win:
            host = bs.Label("host")
            tree = bs.Tree(grow=True, horizontal="stretch")
            for label in ("alpha", "beta"):
                tree.add(label)
        other = bs.ContextMenu(host, trigger=None)
        other.add_item("Hello")
        tree.set_context_menu(lambda node, m: m.add_item("Rename"))
        rows = tree._internal._rows
        win.show()
        assert _pump(root, lambda: rows and rows[0].winfo_ismapped()), "precondition: the rows are mapped"

        other.show(position=_clear_of(win))
        assert _pump(root, lambda: _dismiss_armed(other)), "precondition: outside-click dismiss is armed"
        assert _is_open(other), "precondition: the other menu is open"

        row = rows[0]
        row.event_generate("<Button-3>", x=5, y=5, rootx=row.winfo_rootx() + 5, rooty=row.winfo_rooty() + 5)
        root.update()

        # The tree's own menu opening proves the right-click reached the row's handler,
        # and that the close ran before it rather than closing it too.
        assert tree._ctx_menu is not None and _is_open(tree._ctx_menu), "precondition: the tree's menu opened"
        assert not _is_open(other), "the other menu stayed open after a tree-row right-click"
    finally:
        win.close()
