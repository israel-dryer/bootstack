"""GUI tests for the public ListView widget — data-bag fidelity.

ListView is in-memory (its default source is a ``MemoryDataSource``), so a record
carries *every* user field — including ones the item template never displays and
arbitrary live objects — and hands them back from ``selection``.
"""
from __future__ import annotations

import pytest

import bootstack as bs


def _pump(app) -> None:
    root = app._tk_root
    root.update_idletasks()
    root.update()


@pytest.mark.gui
def test_undisplayed_fields_survive(shown_app):
    payload = object()
    lv = bs.ListView(
        items=[
            {"id": 1, "title": "Alice", "tags": ["vip"], "handle": payload},
            {"id": 2, "title": "Bob", "tags": ["beta"], "handle": payload},
        ],
        selection_mode="multi",
    )
    _pump(shown_app)

    lv.select_all()
    _pump(shown_app)

    selected = {r["id"]: r for r in lv.selection}
    assert selected[1]["tags"] == ["vip"]
    # In-memory: an arbitrary live object rides along by reference.
    assert selected[1]["handle"] is payload
    assert selected[2]["title"] == "Bob"


@pytest.mark.gui
def test_selection_shape_by_mode(shown_app):
    """`.selection` is polymorphic by mode — a record dict (single) vs a list."""
    single = bs.ListView(
        items=[{"id": 1, "title": "Alice", "tags": ["vip"]}, {"id": 2, "title": "Bob"}],
        selection_mode="single",
    )
    multi = bs.ListView(items=[{"id": 1, "title": "Alice"}], selection_mode="multi")
    _pump(shown_app)

    assert single.selection is None       # singular accessor → None, not []
    assert multi.selection == []          # list accessor → empty list

    single.select_items([1])
    _pump(shown_app)
    sel = single.selection
    assert isinstance(sel, dict) and sel["id"] == 1
    # The bag carries undisplayed fields through the singular accessor too.
    assert sel["tags"] == ["vip"]

    # Single mode replaces, never accumulates.
    single.select_items([2])
    _pump(shown_app)
    assert single.selection["id"] == 2

    multi.select_all()
    _pump(shown_app)
    sel = multi.selection
    assert isinstance(sel, list) and sel[0]["id"] == 1


@pytest.mark.gui
def test_select_and_deselect_items_by_id(shown_app):
    """`select_items`/`deselect_items` drive a multi selection by record id."""
    lv = bs.ListView(
        items=[{"id": i, "title": str(i)} for i in (1, 2, 3)],
        selection_mode="multi",
    )
    _pump(shown_app)

    lv.select_items([1, 3])
    _pump(shown_app)
    assert sorted(r["id"] for r in lv.selection) == [1, 3]

    lv.deselect_items([1])
    _pump(shown_app)
    assert [r["id"] for r in lv.selection] == [3]


@pytest.mark.gui
def test_single_mode_replace_fires_one_event(shown_app):
    """Single-mode selection fires exactly one change event per selection.

    Replacing a selection internally does `deselect_all()` + `select()` — two
    source mutations — but they are silenced as a unit and the widget emits a
    single `<<SelectionChange>>`, so a replace must not double-fire.
    """
    lv = bs.ListView(
        items=[{"id": 1, "title": "A"}, {"id": 2, "title": "B"}],
        selection_mode="single",
    )
    _pump(shown_app)

    fires = []
    lv.on_select(lambda e: fires.append(e))
    _pump(shown_app)

    lv.select_items([1])
    _pump(shown_app)
    assert len(fires) == 1 and lv.selection["id"] == 1

    lv.select_items([2])          # replace the existing selection
    _pump(shown_app)
    assert len(fires) == 2 and lv.selection["id"] == 2   # one more, not two
