"""Regression tests for dynamic rebuild bugs (one App per process).

Both bugs were surfaced by a UI that destroys and recreates child widgets on
every update (a live preview):

1. ``Grid`` auto-flow placed re-added children on top of one another because
   ``destroy()`` bypasses ``grid_forget()``, leaving stale occupied cells.
2. ``Schedule`` cancelled an owner's jobs whenever *any* descendant was
   destroyed, because ``<Destroy>`` propagates up to the owner's binding.
"""

from __future__ import annotations

import pytest

import bootstack as bs


@pytest.fixture(scope="module")
def app():
    a = bs.App()
    a._tk_root.withdraw()
    try:
        yield a
    finally:
        try:
            a._tk_root.destroy()
        except Exception:
            pass


def test_grid_autoflow_survives_destroy_recreate(app):
    grid = bs.Grid(rows=2, columns=1, parent=app)
    tiles: list = []

    def rebuild() -> None:
        for w in tiles:
            w.destroy()
        tiles.clear()
        tiles.append(bs.Label("a", parent=grid))
        tiles.append(bs.Label("b", parent=grid))

    rebuild()
    rebuild()  # the re-add that used to collide both children at row 0
    rebuild()

    rows = sorted(int(t._internal.grid_info()["row"]) for t in tiles)
    assert rows == [0, 1], f"auto-flow collided after rebuild: rows={rows}"
    grid.destroy()


def test_child_destroy_does_not_cancel_ancestor_schedule(app):
    job = app.schedule.delay(10_000, lambda: None)
    assert job in app.schedule._jobs

    child = bs.Label("x", parent=app)
    child.destroy()  # before the fix this wiped the app's scheduler

    assert job in app.schedule._jobs, "destroying a child cancelled an ancestor job"
    assert job._active
    job.cancel()


def test_owner_destroy_still_cancels_its_jobs(app):
    # The guard must not break the intended behavior: a widget's own jobs are
    # cancelled when that widget is destroyed.
    panel = bs.VStack(parent=app)
    job = panel.schedule.delay(10_000, lambda: None)
    assert job in panel.schedule._jobs
    panel.destroy()
    assert job._active is False
