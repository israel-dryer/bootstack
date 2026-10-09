"""A child destroyed out of a `Row`/`Column` gives up its place (#537).

Tk's `destroy()` does not route through `remove_child`, and the append fast path
never re-plans, so a destroyed child kept its track: children built after it
were gridded below the dead ones, the first of them with a leading gap, and the
frame held every dead widget. Track and padding are read from `grid_info()`,
which is what the frame wrote, so no assertion depends on the root being mapped.
"""
from __future__ import annotations

import pytest

import bootstack as bs

pytestmark = pytest.mark.gui


def _pump(app):
    app._tk_root.update_idletasks()
    app._tk_root.update()


def _track(widget):
    return int(widget._internal.grid_info()["row"])


def _pady(widget):
    return widget._internal.grid_info()["pady"]


def test_children_rebuilt_after_a_destroy_start_at_the_top(app, monkeypatch):
    col = bs.Column(gap=6)
    with col:
        old = [bs.Label(f"old {i}") for i in range(3)]
    _pump(app)
    frame = col._internal
    # Precondition: a plain stack, so the new children take the fast path.
    assert frame._can_append_in_place()

    relayouts = []
    real = frame._relayout
    monkeypatch.setattr(frame, "_relayout", lambda: (relayouts.append(1), real()))

    # Destroy and rebuild in one go, the way an app refreshes a list.
    for w in old:
        w.destroy()
    with col:
        new = [bs.Label(f"new {i}") for i in range(3)]
    _pump(app)

    assert [_track(w) for w in new] == [0, 1, 2]
    assert _pady(new[0]) == 0, "the first rebuilt child kept a leading gap"
    assert [w for w, _ in frame._managed] == [w._internal for w in new]
    assert len(relayouts) <= 1, "the rebuild re-planned once per child"


def test_destroying_a_middle_child_closes_the_gap_without_remapping(shown_app):
    # Mapped: <Map>/<Unmap> fire only while the root is.
    col = bs.Column(gap=6)
    with col:
        a, b, c = bs.Label("a"), bs.Label("b"), bs.Label("c")
    _pump(shown_app)
    events = []
    for w in (a, c):
        w.on_attach(lambda e: events.append("attach"))
        w.on_detach(lambda e: events.append("detach"))
    _pump(shown_app)
    events.clear()

    b.destroy()
    with col:
        d = bs.Label("d")
    _pump(shown_app)

    assert [_track(w) for w in (a, c, d)] == [0, 1, 2]
    assert events == [], "closing up behind a destroyed child remapped a sibling"


def test_destroying_the_first_child_closes_up_without_another_add(app):
    col = bs.Column(gap=6)
    with col:
        a, b = bs.Label("a"), bs.Label("b")
    _pump(app)
    assert _pady(b) == (6, 0)  # precondition: b carries the gap to drop

    a.destroy()
    _pump(app)

    assert _track(b) == 0
    assert _pady(b) == 0, "the new first child kept its leading gap"


def test_an_index_after_a_sibling_is_destroyed_counts_live_siblings(app):
    col = bs.Column()
    with col:
        a, b, c, d = (bs.Label(t) for t in "abcd")
    _pump(app)

    def order():
        return [w for w, _ in col._internal._managed]

    # No pump in between: the idle close-up would hide a stale index.
    a.destroy()
    b.detach()
    b.attach()
    assert order() == [b._internal, c._internal, d._internal]

    b.destroy()
    x = bs.Label("x", parent=col, index=1)
    assert order() == [c._internal, x._internal, d._internal]
