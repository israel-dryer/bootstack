"""GUI tests for the public ListView widget — data-bag fidelity.

ListView is in-memory (its default source is a ``MemoryDataSource``), so a record
carries *every* user field — including ones the item template never displays and
arbitrary live objects — and hands them back from ``get_selected()``.
"""
from __future__ import annotations

import pytest

import bootstack as bs


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

    selected = {r["id"]: r for r in lv.get_selected()}
    assert selected[1]["tags"] == ["vip"]
    # In-memory: an arbitrary live object rides along by reference.
    assert selected[1]["handle"] is payload
    assert selected[2]["title"] == "Bob"
