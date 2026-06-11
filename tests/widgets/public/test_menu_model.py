"""Tests for the platform-neutral menu model (no GUI required)."""
from __future__ import annotations

import pytest

from bootstack._runtime.shortcuts import get_shortcuts
from bootstack.widgets._impl.composites.menu import MenuGroup, MenuItem, MenuModel


@pytest.fixture(autouse=True)
def _reset_shortcuts():
    """Clear the process-wide Shortcuts singleton around each test."""
    svc = get_shortcuts()
    svc._shortcuts.clear()
    svc._bound_windows.clear()
    svc._bindings.clear()
    yield
    svc._shortcuts.clear()
    svc._bound_windows.clear()
    svc._bindings.clear()


# ----- imperative building -----

def test_add_menu_returns_group_and_registers_it():
    model = MenuModel()
    group = model.add_menu("File")
    assert isinstance(group, MenuGroup)
    assert list(model) == [group]
    assert len(model) == 1


def test_builders_produce_typed_items():
    model = MenuModel()
    file = model.add_menu("File")
    a = file.add_action("Open", shortcut="Mod+O", on_click=lambda: None)
    file.add_separator()
    c = file.add_check("Word wrap", checked=True)
    r = file.add_radio("Light", value="light", group="theme")

    assert [i.type for i in file.items] == ["action", "separator", "check", "radio"]
    assert a.text == "Open"
    assert c.checked is True
    assert r.value == "light" and r.group == "theme"


def test_radio_value_and_group_default_to_text_and_group_key():
    model = MenuModel()
    view = model.add_menu("View", key="view")
    r = view.add_radio("Light")
    assert r.value == "Light"      # value defaults to text
    assert r.group == "view"       # group defaults to the owning group's key


def test_group_is_context_manager():
    model = MenuModel()
    with model.add_menu("Edit") as edit:
        edit.add_action("Undo")
        edit.add_action("Redo")
    assert len(model.groups[0]) == 2


def test_item_keys_autoderived_from_position():
    model = MenuModel()
    file = model.add_menu("File", key="file")
    i0 = file.add_action("Open")
    i1 = file.add_action("Save")
    assert i0.key == "file.0"
    assert i1.key == "file.1"


# ----- declarative loading -----

def test_load_matches_imperative():
    fn = lambda: None
    model = MenuModel()
    model.load([
        {"text": "File", "items": [
            {"text": "Open", "shortcut": "Mod+O", "on_click": fn},
            {"type": "separator"},
            {"text": "Quit", "shortcut": "Mod+Q", "on_click": fn},
        ]},
        {"text": "Edit", "items": [
            {"text": "Undo", "shortcut": "Mod+Z", "on_click": fn},
        ]},
    ])
    assert [g.text for g in model] == ["File", "Edit"]
    assert [i.type for i in model.groups[0].items] == ["action", "separator", "action"]
    assert model.groups[0].items[0].text == "Open"


def test_load_clears_previous_contents():
    model = MenuModel()
    model.add_menu("Stale")
    model.load([{"text": "File", "items": []}])
    assert [g.text for g in model] == ["File"]


def test_load_rejects_nested_items():
    model = MenuModel()
    with pytest.raises(ValueError, match="single layer"):
        model.load([
            {"text": "File", "items": [
                {"text": "Recent", "items": [{"text": "a.txt"}]},
            ]},
        ])


def test_load_rejects_unknown_item_field():
    model = MenuModel()
    with pytest.raises(ValueError, match="Unknown menu item field"):
        model.load([{"text": "File", "items": [{"text": "Open", "colour": "red"}]}])


def test_load_rejects_unknown_item_type():
    model = MenuModel()
    with pytest.raises(ValueError, match="Unknown menu item type"):
        model.load([{"text": "File", "items": [{"type": "slider", "text": "x"}]}])


# ----- iteration -----

def test_iter_items_walks_all_groups_in_order():
    model = MenuModel()
    f = model.add_menu("File"); f.add_action("Open"); f.add_action("Quit")
    e = model.add_menu("Edit"); e.add_action("Undo")
    assert [i.text for i in model.iter_items()] == ["Open", "Quit", "Undo"]


# ----- shortcut display resolution -----

def test_shortcut_display_resolved_for_pattern():
    item = MenuItem(type="action", text="Open", shortcut="Mod+O")
    # On Win/Linux this is "Ctrl+O"; on Mac "⌘O". Either way it's non-empty
    # and contains the key letter.
    assert item.shortcut_display
    assert "O" in item.shortcut_display


def test_no_shortcut_means_no_display():
    item = MenuItem(type="action", text="Open")
    assert item.shortcut_display is None


# ----- shortcut binding -----

def test_bind_registers_pattern_shortcuts():
    svc = get_shortcuts()
    model = MenuModel()
    f = model.add_menu("File")
    f.add_action("Open", shortcut="Mod+O", on_click=lambda: None)
    f.add_action("Save", shortcut="Mod+S", on_click=lambda: None)

    model.bind_shortcuts()
    patterns = {s.pattern for s in svc.all().values()}
    assert patterns == {"Mod+O", "Mod+S"}


def test_bind_skips_items_without_on_click():
    svc = get_shortcuts()
    model = MenuModel()
    f = model.add_menu("File")
    f.add_action("Open", shortcut="Mod+O")  # no on_click
    model.bind_shortcuts()
    assert svc.all() == {}


def test_bind_skips_registered_keys():
    svc = get_shortcuts()
    svc.register("save", "Mod+S", lambda: None)
    before = dict(svc.all())

    model = MenuModel()
    f = model.add_menu("File")
    # shortcut is an already-registered key → display only, no re-register
    f.add_action("Save", shortcut="save", on_click=lambda: None)
    model.bind_shortcuts()

    assert svc.all() == before  # nothing added


def test_bind_skips_literal_shortcuts():
    svc = get_shortcuts()
    model = MenuModel()
    f = model.add_menu("File")
    f.add_action("Help", shortcut="press any key", on_click=lambda: None)
    model.bind_shortcuts()
    assert svc.all() == {}


def test_rebind_is_idempotent():
    svc = get_shortcuts()
    model = MenuModel()
    f = model.add_menu("File")
    f.add_action("Open", shortcut="Mod+O", on_click=lambda: None)

    model.bind_shortcuts()
    model.bind_shortcuts()  # should release then re-register, not duplicate
    assert len(svc.all()) == 1


def test_unbind_releases_registered_shortcuts():
    svc = get_shortcuts()
    model = MenuModel()
    f = model.add_menu("File")
    f.add_action("Open", shortcut="Mod+O", on_click=lambda: None)
    model.bind_shortcuts()
    assert len(svc.all()) == 1

    model.unbind_shortcuts()
    assert svc.all() == {}


def test_clear_releases_shortcuts():
    svc = get_shortcuts()
    model = MenuModel()
    f = model.add_menu("File")
    f.add_action("Open", shortcut="Mod+O", on_click=lambda: None)
    model.bind_shortcuts()
    model.clear()
    assert svc.all() == {}
    assert list(model) == []