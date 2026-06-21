"""Workbench — the two-tier workspace host.

Each `add_workspace` returns a `Workspace` sidebar host authored with the same
front doors as a single-tier `AppShell`. The filled `solid` selection is the
standalone nav's alone — under a rail a workspace's `page_nav` always uses the
wash. One App per process: ONE module-scoped `Workbench`.
"""

from __future__ import annotations

import pytest

import bootstack as bs

pytestmark = pytest.mark.isolated


@pytest.fixture(scope="module")
def wb():
    w = bs.Workbench(title="WB", size=(960, 600), nav_accent="primary")
    w.__enter__()
    try:
        yield w
    finally:
        try:
            w._internal.destroy()
        except Exception:
            pass


def test_workspaces_and_navigate(wb):
    with wb.add_workspace("docs", text="Docs", icon="folder") as ws:
        with ws.page_nav() as nav:
            with nav.add_page("recent", text="Recent", icon="clock", padding=20):
                bs.Label("Recent")
            with nav.add_page("shared", text="Shared", icon="people", padding=20):
                bs.Label("Shared")
    settings = wb.add_workspace("settings", text="Settings", icon="gear", pin_to_footer=True)
    with settings.page_nav() as nav:
        with nav.add_page("general", text="General", icon="sliders", padding=20):
            bs.Label("General")

    wb.navigate("docs", "recent")
    wb._internal.update_idletasks()
    assert wb.current_workspace == "docs"
    assert wb.current == "recent"
    # The settings workspace is pinned to the rail footer.
    assert wb._internal.model.workspace("settings").is_footer is True


def test_under_rail_page_nav_is_ghost(wb):
    # A workspace nav sits under the rail (nav-quiet) and always uses the wash —
    # the solid variant is the standalone AppShell page nav's alone.
    nav = wb._internal._workspaces["docs"]._provider._nav
    assert nav._variant == "nav-quiet"
    assert nav._selection == "ghost"