"""Tests for the public ``detach`` / ``attach`` widget API and its events.

A widget placed in a layout can be pulled out (`detach`) and put back
(`attach`) without being destroyed, across all three geometry managers
(pack / grid / place). `attach` round-trips the original position and accepts
layout overrides; `on_attach` / `on_detach` fire as the widget enters and
leaves the layout.

All GUI work shares ONE module-scoped `App` — creating a second `App` in the
same process crashes the ttk style engine.
"""
from __future__ import annotations

import pytest

import bootstack as bs
from bootstack.errors import ParentResolutionError

pytestmark = pytest.mark.gui


@pytest.fixture(scope="module")
def app():
    """A single shown App shared by every test in this module."""
    a = bs.App()
    a._tk_root.deiconify()
    a._tk_root.update_idletasks()
    a._tk_root.update()
    try:
        yield a
    finally:
        try:
            a._tk_root.destroy()
        except Exception:
            pass


@pytest.fixture
def pump(app):
    """Flush pending Tk events so map/unmap and geometry settle."""
    def _pump():
        app._tk_root.update_idletasks()
        app._tk_root.update()
    return _pump


def _order(container, widgets):
    """Return the labels of `widgets` in current pack order under `container`."""
    by_tk = {w._internal: name for name, w in widgets.items()}
    return [by_tk[s] for s in container._internal.pack_slaves() if s in by_tk]


# ---------------------------------------------------------------------------
# is_attached
# ---------------------------------------------------------------------------

def test_is_attached_reflects_placement(app, pump):
    col = bs.VStack(parent=app)
    btn = bs.Button("X", parent=col)
    pump()
    assert btn.is_attached is True
    btn.detach()
    pump()
    assert btn.is_attached is False
    btn.attach()
    pump()
    assert btn.is_attached is True


def test_detach_without_placement_is_noop(app):
    # The App has no stored placement (it is a root, never placed in a parent).
    # detach() must be a safe no-op rather than raising.
    assert not hasattr(app, "_placement")
    app.detach()  # no error
    assert not hasattr(app, "_placement")


# ---------------------------------------------------------------------------
# pack — order round-trips
# ---------------------------------------------------------------------------

def test_pack_detach_attach_restores_order(app, pump):
    col = bs.VStack(parent=app)
    a = bs.Button("A", parent=col)
    b = bs.Button("B", parent=col)
    c = bs.Button("C", parent=col)
    widgets = {"A": a, "B": b, "C": c}
    pump()
    assert _order(col, widgets) == ["A", "B", "C"]

    b.detach()
    pump()
    assert _order(col, widgets) == ["A", "C"]

    b.attach()
    pump()
    assert _order(col, widgets) == ["A", "B", "C"]


def test_pack_attach_index_moves(app, pump):
    col = bs.VStack(parent=app)
    a = bs.Button("A", parent=col)
    b = bs.Button("B", parent=col)
    c = bs.Button("C", parent=col)
    widgets = {"A": a, "B": b, "C": c}
    pump()

    a.detach()
    a.attach(index=2)
    pump()
    assert _order(col, widgets) == ["B", "C", "A"]


def test_pack_attach_before_after(app, pump):
    col = bs.VStack(parent=app)
    a = bs.Button("A", parent=col)
    b = bs.Button("B", parent=col)
    c = bs.Button("C", parent=col)
    widgets = {"A": a, "B": b, "C": c}
    pump()

    c.detach()
    c.attach(before=a)
    pump()
    assert _order(col, widgets) == ["C", "A", "B"]

    c.detach()
    c.attach(after=a)
    pump()
    assert _order(col, widgets) == ["A", "C", "B"]


def test_pack_index_at_construction(app, pump):
    col = bs.VStack(parent=app)
    a = bs.Button("A", parent=col)
    b = bs.Button("B", parent=col)
    # Insert C at the front via the public index= knob.
    c = bs.Button("C", parent=col, index=0)
    widgets = {"A": a, "B": b, "C": c}
    pump()
    assert _order(col, widgets) == ["C", "A", "B"]


def test_attach_on_attached_widget_moves(app, pump):
    col = bs.VStack(parent=app)
    a = bs.Button("A", parent=col)
    b = bs.Button("B", parent=col)
    c = bs.Button("C", parent=col)
    widgets = {"A": a, "B": b, "C": c}
    pump()

    # Move without an explicit detach first.
    a.attach(index=2)
    pump()
    assert a.is_attached is True
    assert _order(col, widgets) == ["B", "C", "A"]


# ---------------------------------------------------------------------------
# pack — overrides + idempotency
# ---------------------------------------------------------------------------

def test_attach_applies_layout_override(app, pump):
    col = bs.VStack(parent=app)
    btn = bs.Button("X", parent=col)
    pump()
    btn.detach()
    btn.attach(fill="x", expand=True)
    pump()
    info = btn._internal.pack_info()
    assert info["fill"] == "x"
    assert bool(int(info["expand"])) is True


def test_detach_is_idempotent(app, pump):
    col = bs.VStack(parent=app)
    btn = bs.Button("X", parent=col)
    pump()
    btn.detach()
    btn.detach()  # no error, still detached
    pump()
    assert btn.is_attached is False
    btn.attach()
    pump()
    assert btn.is_attached is True


def test_attach_without_placement_raises(app):
    # The App is a container that was never placed in a parent layout.
    with pytest.raises(ParentResolutionError):
        app.attach()


# ---------------------------------------------------------------------------
# grid
# ---------------------------------------------------------------------------

def test_grid_detach_attach_restores_cell(app, pump):
    grid = bs.Grid(parent=app, columns=2)
    ga = bs.Button("GA", parent=grid, row=0, column=0)
    gb = bs.Button("GB", parent=grid, row=0, column=1)
    pump()
    assert gb.is_attached is True

    gb.detach()
    pump()
    assert gb.is_attached is False

    gb.attach()
    pump()
    info = gb._internal.grid_info()
    assert int(info["row"]) == 0
    assert int(info["column"]) == 1


def test_grid_attach_override(app, pump):
    grid = bs.Grid(parent=app, columns=2)
    gb = bs.Button("GB", parent=grid, row=0, column=0)
    pump()
    gb.detach()
    gb.attach(sticky="ew")
    pump()
    assert gb._internal.grid_info()["sticky"] == "ew"


# ---------------------------------------------------------------------------
# place
# ---------------------------------------------------------------------------

def test_place_detach_attach_restores_coords(app, pump):
    col = bs.VStack(parent=app)
    p = bs.Button("P", parent=col, x=30, y=40)
    pump()
    assert p._internal.winfo_manager() == "place"

    p.detach()
    pump()
    assert p.is_attached is False

    p.attach()
    pump()
    info = p._internal.place_info()
    assert int(info["x"]) == 30
    assert int(info["y"]) == 40


# ---------------------------------------------------------------------------
# attached=False — start hidden
# ---------------------------------------------------------------------------

def test_attached_false_starts_detached(app, pump):
    col = bs.VStack(parent=app)
    btn = bs.Button("X", parent=col, attached=False)
    pump()
    assert btn.is_attached is False


def test_attached_false_attaches_in_natural_slot(app, pump):
    col = bs.VStack(parent=app)
    a = bs.Button("A", parent=col)
    b = bs.Button("B", parent=col, attached=False)
    c = bs.Button("C", parent=col)
    widgets = {"A": a, "B": b, "C": c}
    pump()
    assert _order(col, widgets) == ["A", "C"]

    b.attach()
    pump()
    assert _order(col, widgets) == ["A", "B", "C"]


def test_attached_false_grid_restores_cell(app, pump):
    grid = bs.Grid(parent=app, columns=2)
    gb = bs.Button("GB", parent=grid, row=0, column=1, attached=False)
    pump()
    assert gb.is_attached is False
    gb.attach()
    pump()
    info = gb._internal.grid_info()
    assert int(info["row"]) == 0 and int(info["column"]) == 1


def test_attached_false_place_restores(app, pump):
    col = bs.VStack(parent=app)
    p = bs.Button("P", parent=col, x=10, y=20, attached=False)
    pump()
    assert p.is_attached is False
    p.attach()
    pump()
    assert p._internal.winfo_manager() == "place"


def test_attached_false_fires_no_spurious_events(app, pump):
    col = bs.VStack(parent=app)
    btn = bs.Button("X", parent=col, attached=False)
    events: list[str] = []
    btn.on_attach(lambda e: events.append("attach"))
    btn.on_detach(lambda e: events.append("detach"))
    pump()
    assert events == []  # nothing fires while it sits detached
    btn.attach()
    pump()
    assert events == ["attach"]


# ---------------------------------------------------------------------------
# events
# ---------------------------------------------------------------------------

def test_on_attach_on_detach_fire(app, pump):
    col = bs.VStack(parent=app)
    btn = bs.Button("X", parent=col)
    pump()

    events: list[str] = []
    btn.on_attach(lambda e: events.append("attach"))
    btn.on_detach(lambda e: events.append("detach"))

    btn.detach()
    pump()
    btn.attach()
    pump()

    assert events == ["detach", "attach"]


def test_on_detach_returns_subscription(app, pump):
    col = bs.VStack(parent=app)
    btn = bs.Button("X", parent=col)
    pump()

    events: list[str] = []
    sub = btn.on_detach(lambda e: events.append("detach"))

    btn.detach()
    pump()
    assert events == ["detach"]

    sub.cancel()
    btn.attach()
    pump()
    btn.detach()
    pump()
    assert events == ["detach"], "cancelled subscription must not fire again"
