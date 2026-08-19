"""`context_menus` must not decide whether `on_row_right_click` fires.

#456 wired the `context_menus` argument through to the widget for the first
time, which made `tableview.py`'s right-click gate reachable. That gate sat
above the `<<RowRightClick>>` emit, so turning a menu off also turned the
documented public event off -- `'none'` and, less obviously, `'headers'`.

`context_menus` chooses which menus the table offers. It does not choose
whether a right-click is reported: "no built-in row menu, I'll handle the
gesture myself" has to stay available. Same rule #417 established for
`on_row_double_click`, which is bound regardless of `allow_edit`.

These drive a real `<Button-3>` rather than reading the gate, because the gate
is what moved -- asserting on it would restate the implementation instead of
pinning the behavior.
"""
from __future__ import annotations

import pytest

import bootstack as bs


ROWS = [
    {"id": 1, "name": "Ada", "role": "eng"},
    {"id": 2, "name": "Alan", "role": "math"},
]

CONTEXT_MENU_VALUES = ["all", "headers", "rows", "none"]


def _right_click_row(tree, iid) -> None:
    """Synthesize a right-click on a row, with the usual mapping precondition.

    `<Button-3>` is bound on every windowing system by `bind_right_click`; the
    aqua-only `<Button-2>` and `<Control-Button-1>` are additive, so driving
    Button-3 exercises the same handler everywhere.
    """
    box = tree.bbox(iid)
    # An unmapped tree returns '' here, which would make the assertions below
    # pass or fail vacuously -- the failure #405 and #437 both paid for.
    assert box != "", "row has no bbox — the tree is unmapped, so this test cannot click"
    x, y = box[0] + box[2] // 2, box[1] + box[3] // 2
    assert tree.identify_row(y) == iid, "hit test missed the target row"
    tree.event_generate("<Button-3>", x=x, y=y)


@pytest.fixture
def shown_menus(monkeypatch):
    """Record menus instead of displaying them, and return the record.

    A synthesized right-click opens a real `ContextMenu`, which takes a grab and
    blocks the event loop forever in an automated run -- the trap CLAUDE.md
    records for probes ("stub the row menu; it blocks the loop"). Patching the
    CLASS before any table is built is what makes it stick: the menus are
    created lazily inside the handler, so there is no instance to patch first.

    It also sharpens the assertion. `_row_menu is not None` only says a menu was
    BUILT; this says one was SHOWN, which is what a user would see.
    """
    from bootstack.widgets._impl.composites.contextmenu import ContextMenu

    shown = []
    monkeypatch.setattr(ContextMenu, "show", lambda self, **kwargs: shown.append(self))
    return shown


def _table(context_menus):
    table = bs.DataTable(columns=["name", "role"], rows=list(ROWS), context_menus=context_menus)
    seen = []
    table.on_row_right_click(lambda e: seen.append(e))
    return table, seen


@pytest.mark.gui
@pytest.mark.parametrize("value", CONTEXT_MENU_VALUES)
def test_row_right_click_fires_for_every_context_menus_value(shown_app, shown_menus, value):
    table, seen = _table(value)
    tree = table._internal._tree
    shown_app._tk_root.update_idletasks()
    shown_app._tk_root.update()

    _right_click_row(tree, tree.get_children()[0])
    shown_app._tk_root.update()

    assert len(seen) == 1, f"context_menus={value!r} suppressed on_row_right_click"
    assert seen[0].record["name"] == "Ada"
    assert seen[0].id == 1


@pytest.mark.gui
@pytest.mark.parametrize("value", CONTEXT_MENU_VALUES)
def test_the_row_menu_still_obeys_context_menus(shown_app, shown_menus, value):
    """The other half: decoupling the event must not un-gate the menu.

    Without this, a fix that simply deleted the gate would pass the test above
    while making `context_menus` inert again -- which is the #456 defect coming
    back in the other direction.
    """
    table, _seen = _table(value)
    tree = table._internal._tree
    shown_app._tk_root.update_idletasks()
    shown_app._tk_root.update()

    _right_click_row(tree, tree.get_children()[0])
    shown_app._tk_root.update()

    expected = 1 if value in ("all", "rows") else 0
    assert len(shown_menus) == expected, (
        f"context_menus={value!r} should {'show' if expected else 'not show'} the row menu"
    )