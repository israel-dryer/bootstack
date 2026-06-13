"""Headless unit tests for `NavModel` — the shell's navigation state.

No Tk / App required; this is pure state-machine coverage.
"""

from __future__ import annotations

import pytest

from bootstack.widgets._core.navmodel import NavChange, NavModel, WorkspaceState


# ----- Workspaces & activation -----

def test_add_workspace_returns_state():
    m = NavModel()
    ws = m.add_workspace("home", text="Home", icon="house")
    assert isinstance(ws, WorkspaceState)
    assert ws.key == "home"
    assert ws.text == "Home"
    assert ws.icon == "house"
    assert ws.provider == "pages"
    assert m.has_workspace("home")
    assert m.workspace("home") is ws


def test_first_non_footer_workspace_becomes_active():
    m = NavModel()
    assert m.active_workspace is None
    m.add_workspace("a")
    assert m.active_workspace == "a"
    # a second workspace does not steal active
    m.add_workspace("b")
    assert m.active_workspace == "a"


def test_footer_workspace_does_not_auto_activate():
    m = NavModel()
    m.add_workspace("settings", is_footer=True)
    assert m.active_workspace is None
    m.add_workspace("home")
    assert m.active_workspace == "home"


def test_duplicate_and_empty_workspace_keys_raise():
    m = NavModel()
    m.add_workspace("a")
    with pytest.raises(ValueError):
        m.add_workspace("a")
    with pytest.raises(ValueError):
        m.add_workspace("")


def test_workspace_unknown_key_raises():
    m = NavModel()
    with pytest.raises(KeyError):
        m.workspace("nope")


# ----- Rail visibility (the degenerate-case unification) -----

def test_rail_hidden_until_more_than_one_workspace():
    m = NavModel()
    assert m.rail_visible is False
    m.add_workspace("a")
    assert m.rail_visible is False          # single-tier: no rail
    m.add_workspace("b")
    assert m.rail_visible is True           # two-tier: rail appears


def test_footer_workspace_counts_toward_rail():
    m = NavModel()
    m.add_workspace("home")
    m.add_workspace("settings", is_footer=True)
    assert m.rail_visible is True


# ----- Workspace selection -----

def test_select_workspace_sets_active_and_notifies():
    m = NavModel()
    m.add_workspace("a")
    m.add_workspace("b")
    seen: list[NavChange] = []
    m.subscribe(seen.append)
    m.select_workspace("b")
    assert m.active_workspace == "b"
    assert seen[-1].facet == "workspace"
    assert seen[-1].workspace == "b"


def test_select_workspace_same_is_noop():
    m = NavModel()
    m.add_workspace("a")
    seen: list[NavChange] = []
    m.subscribe(seen.append)
    m.select_workspace("a")                 # already active
    assert seen == []


def test_select_unknown_workspace_raises():
    m = NavModel()
    with pytest.raises(KeyError):
        m.select_workspace("nope")


# ----- Page selection & per-workspace memory -----

def test_select_page_defaults_to_active_workspace():
    m = NavModel()
    m.add_workspace("a")
    m.select_page("p1")
    assert m.active_page() == "p1"
    assert m.active_page("a") == "p1"


def test_per_workspace_page_memory_survives_switching():
    m = NavModel()
    m.add_workspace("a")
    m.add_workspace("b")
    m.select_page("a1")                     # on active 'a'
    m.select_workspace("b")
    m.select_page("b1")
    assert m.active_page("a") == "a1"       # remembered independently
    assert m.active_page("b") == "b1"
    m.select_workspace("a")
    assert m.active_page() == "a1"          # switching back restores memory


def test_select_page_explicit_workspace():
    m = NavModel()
    m.add_workspace("a")
    m.add_workspace("b")
    m.select_page("b1", workspace="b")      # set non-active workspace's page
    assert m.active_workspace == "a"        # active unchanged
    assert m.active_page("b") == "b1"


def test_select_page_without_active_workspace_raises():
    m = NavModel()
    with pytest.raises(ValueError):
        m.select_page("p1")


def test_select_page_unknown_workspace_raises():
    m = NavModel()
    m.add_workspace("a")
    with pytest.raises(KeyError):
        m.select_page("p1", workspace="nope")


def test_active_page_none_when_unset():
    m = NavModel()
    m.add_workspace("a")
    assert m.active_page() is None


# ----- The VS Code rail gesture -----

def test_activate_rail_different_workspace_switches_and_shows():
    m = NavModel()
    m.add_workspace("a")
    m.add_workspace("b")
    m.hide_sidebar()
    m.activate_rail("b")
    assert m.active_workspace == "b"
    assert m.sidebar_visible is True


def test_activate_rail_active_workspace_hides_when_visible():
    m = NavModel()
    m.add_workspace("a")
    m.add_workspace("b")
    assert m.sidebar_visible is True
    m.activate_rail("a")                    # clicking the active icon
    assert m.sidebar_visible is False
    assert m.active_workspace == "a"


def test_activate_rail_active_workspace_shows_when_hidden():
    m = NavModel()
    m.add_workspace("a")
    m.hide_sidebar()
    m.activate_rail("a")
    assert m.sidebar_visible is True


def test_activate_rail_unknown_raises():
    m = NavModel()
    m.add_workspace("a")
    with pytest.raises(KeyError):
        m.activate_rail("nope")


# ----- Sidebar axis: hidden -> compact -> expanded -----

def test_default_sidebar_mode_expanded():
    assert NavModel().sidebar_mode == "expanded"


def test_set_sidebar_mode_validates():
    m = NavModel()
    with pytest.raises(ValueError):
        m.set_sidebar_mode("bogus")  # type: ignore[arg-type]


def test_set_sidebar_mode_notifies_once_and_dedupes():
    m = NavModel()
    seen: list[NavChange] = []
    m.subscribe(seen.append)
    m.set_sidebar_mode("compact")
    m.set_sidebar_mode("compact")           # no-op
    assert len(seen) == 1
    assert seen[0].facet == "sidebar"
    assert seen[0].sidebar_mode == "compact"


def test_hide_then_show_restores_prior_mode():
    m = NavModel()
    m.set_sidebar_mode("compact")
    m.hide_sidebar()
    assert m.sidebar_mode == "hidden"
    m.show_sidebar()
    assert m.sidebar_mode == "compact"      # not the default 'expanded'


def test_toggle_sidebar_round_trip():
    m = NavModel()                          # expanded
    m.toggle_sidebar()
    assert m.sidebar_mode == "hidden"
    m.toggle_sidebar()
    assert m.sidebar_mode == "expanded"


def test_show_sidebar_when_visible_is_noop():
    m = NavModel()
    seen: list[NavChange] = []
    m.subscribe(seen.append)
    m.show_sidebar()                        # already expanded
    assert seen == []


def test_initial_hidden_restores_to_expanded():
    m = NavModel(sidebar_mode="hidden")
    assert m.sidebar_mode == "hidden"
    m.show_sidebar()
    assert m.sidebar_mode == "expanded"


# ----- Dock -----

def test_toggle_dock():
    m = NavModel()
    assert m.dock_visible is False
    seen: list[NavChange] = []
    m.subscribe(seen.append)
    m.toggle_dock()
    assert m.dock_visible is True
    assert seen[-1].facet == "dock"
    assert seen[-1].dock_visible is True
    m.toggle_dock()
    assert m.dock_visible is False


# ----- Subscription mechanics -----

def test_unsubscribe_stops_notifications():
    m = NavModel()
    m.add_workspace("a")
    m.add_workspace("b")
    seen: list[NavChange] = []
    handle = m.subscribe(seen.append)
    m.select_workspace("b")
    handle.cancel()
    m.select_workspace("a")
    assert [c.workspace for c in seen] == ["b"]


def test_unsubscribe_during_dispatch_is_safe():
    m = NavModel()
    m.add_workspace("a")
    m.add_workspace("b")
    calls: list[str] = []

    def once(change: NavChange) -> None:
        calls.append("once")
        handle.cancel()

    handle = m.subscribe(once)
    m.subscribe(lambda c: calls.append("other"))
    m.select_workspace("b")                 # both fire; 'once' removes itself
    m.select_workspace("a")                 # only 'other' fires
    assert calls == ["once", "other", "other"]


def test_subscribe_returns_cancellable_handle():
    m = NavModel()
    m.add_workspace("a")
    m.add_workspace("b")
    seen: list[NavChange] = []
    handle = m.subscribe(seen.append)
    assert handle.cancelled is False
    handle.cancel()
    assert handle.cancelled is True
    m.select_workspace("b")
    assert seen == []


def test_subscribe_handle_works_as_context_manager():
    m = NavModel()
    m.add_workspace("a")
    m.add_workspace("b")
    seen: list[NavChange] = []
    with m.subscribe(seen.append):
        m.select_workspace("b")
    m.select_workspace("a")                 # after context exit: unsubscribed
    assert [c.workspace for c in seen] == ["b"]


def test_add_workspace_emits_structure_change():
    m = NavModel()
    seen: list[NavChange] = []
    m.subscribe(seen.append)
    m.add_workspace("a")
    assert seen[-1].facet == "structure"
    assert seen[-1].workspace == "a"
