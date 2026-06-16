"""Tests for the public ``detach`` / ``attach`` widget API and its events.

A widget placed in a layout can be pulled out (`detach`) and put back
(`attach`) without being destroyed. Inside a `Row`/`Column` it rides the flex
engine (`detach`/`attach` re-plan the flow); a 2-D `Grid` cell and an absolute
`place` placement are supported too. `attach` round-trips the original position
and accepts layout overrides; `on_attach` / `on_detach` fire as the widget
enters and leaves the layout — and re-planning the flow when a sibling is
added/removed must NOT churn map/unmap on the other children.

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
    """Return the labels of `widgets` in current flow order under `container`.

    The flex frame's managed list is the live attached-sibling order — exactly
    what `detach`/`attach` manipulate — so it is the meaningful "what's shown,
    in what order" for a Row/Column.
    """
    by_tk = {w._internal: name for name, w in widgets.items()}
    managed = container._internal._managed
    return [by_tk[w] for w, _ in managed if w in by_tk]


# ---------------------------------------------------------------------------
# is_attached
# ---------------------------------------------------------------------------

def test_is_attached_reflects_placement(app, pump):
    col = bs.Column(parent=app)
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
# flex (Row / Column) — order round-trips
# ---------------------------------------------------------------------------

def test_flex_detach_attach_restores_order(app, pump):
    col = bs.Column(parent=app)
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


def test_flex_attach_index_moves(app, pump):
    col = bs.Column(parent=app)
    a = bs.Button("A", parent=col)
    b = bs.Button("B", parent=col)
    c = bs.Button("C", parent=col)
    widgets = {"A": a, "B": b, "C": c}
    pump()

    a.detach()
    a.attach(index=2)
    pump()
    assert _order(col, widgets) == ["B", "C", "A"]


def test_flex_index_at_construction(app, pump):
    col = bs.Column(parent=app)
    a = bs.Button("A", parent=col)
    b = bs.Button("B", parent=col)
    # Insert C at the front via the public index= knob.
    c = bs.Button("C", parent=col, index=0)
    widgets = {"A": a, "B": b, "C": c}
    pump()
    assert _order(col, widgets) == ["C", "A", "B"]


def test_attach_on_attached_widget_moves(app, pump):
    col = bs.Column(parent=app)
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


def test_flex_works_in_a_row(app, pump):
    row = bs.Row(parent=app)
    a = bs.Button("A", parent=row)
    b = bs.Button("B", parent=row)
    widgets = {"A": a, "B": b}
    pump()
    assert _order(row, widgets) == ["A", "B"]
    a.detach()
    a.attach()
    pump()
    assert _order(row, widgets) == ["A", "B"]


# ---------------------------------------------------------------------------
# flex — overrides + idempotency
# ---------------------------------------------------------------------------

def test_attach_applies_layout_override(app, pump):
    col = bs.Column(parent=app)
    btn = bs.Button("X", parent=col)
    pump()
    btn.detach()
    btn.attach(align_self="stretch")
    pump()
    # stretch on a Column's cross (horizontal) axis spans the cell east-west.
    sticky = btn._internal.grid_info()["sticky"]
    assert "e" in sticky and "w" in sticky


def test_detach_is_idempotent(app, pump):
    col = bs.Column(parent=app)
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


def test_legacy_child_kwarg_rejected(app):
    # Hard break: a stale pack kwarg must raise, not silently collapse.
    col = bs.Column(parent=app)
    with pytest.raises(bs.errors.BootstackError):
        bs.Button("X", parent=col, fill="x")


# ---------------------------------------------------------------------------
# grid (2-D)
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
# place — absolute overlay inside a flex container
# ---------------------------------------------------------------------------

def test_place_detach_attach_restores_coords(app, pump):
    col = bs.Column(parent=app)
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
    col = bs.Column(parent=app)
    btn = bs.Button("X", parent=col, attached=False)
    pump()
    assert btn.is_attached is False


def test_attached_false_attaches_in_natural_slot(app, pump):
    col = bs.Column(parent=app)
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
    col = bs.Column(parent=app)
    p = bs.Button("P", parent=col, x=10, y=20, attached=False)
    pump()
    assert p.is_attached is False
    p.attach()
    pump()
    assert p._internal.winfo_manager() == "place"


def test_attached_false_fires_no_spurious_events(app, pump):
    col = bs.Column(parent=app)
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
    col = bs.Column(parent=app)
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
    col = bs.Column(parent=app)
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


# ---------------------------------------------------------------------------
# regression — re-planning the flow must not churn map/unmap on siblings
# ---------------------------------------------------------------------------

def test_relayout_fires_no_spurious_sibling_events(app, pump):
    """Adding/removing a child re-plans the whole flow, but the engine must
    reposition surviving siblings IN PLACE (grid_configure, not forget+regrid)
    so they see no <Unmap>/<Map> — i.e. no spurious on_detach/on_attach.

    Regression for the bug where the blanket grid_forget in `_relayout` fired
    a detach+attach on every existing child whenever one child changed.
    """
    col = bs.Column(parent=app)
    a = bs.Button("A", parent=col)
    bs.Button("B", parent=col)
    pump()

    events: list[str] = []
    a.on_attach(lambda e: events.append("attach"))
    a.on_detach(lambda e: events.append("detach"))
    pump()
    events.clear()

    # Add a new sibling — A must not see any map/unmap churn.
    c = bs.Button("C", parent=col)
    pump()
    assert events == [], "adding a sibling churned events on an existing child"

    # Remove a sibling — likewise.
    c.detach()
    pump()
    assert events == [], "removing a sibling churned events on an existing child"

    # Sanity: A's OWN detach/attach still fires exactly one event each.
    a.detach()
    pump()
    a.attach()
    pump()
    assert events == ["detach", "attach"]
