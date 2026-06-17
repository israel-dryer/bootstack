"""Tests for Toolbar.add_menu — menus as toolbar items.

Structural only — asserts the toolbar builds a menu model + in-window dropdown
triggers and wires item commands. Visual appearance is verified by hand. One
module-scoped App (creating several Apps in one process crashes Tk).
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.gui


@pytest.fixture(scope="module")
def app():
    import bootstack as bs

    app = bs.App()
    app._tk_root.withdraw()
    try:
        yield app
    finally:
        try:
            app._tk_root.destroy()
        except Exception:
            pass


def test_add_menu_builds_model_and_trigger(app):
    import bootstack as bs

    fired: list[str] = []
    tb = bs.Toolbar(parent=app)
    with tb.add_menu("File") as file:
        file.add_action("New", shortcut="Mod+N", on_click=lambda: fired.append("new"))
        file.add_divider()
        file.add_action("Quit", shortcut="Mod+Q", on_click=lambda: fired.append("quit"))

    model = tb._internal.menu_model
    assert [g.text for g in model] == ["File"]
    assert [(i.type, i.text) for i in model.groups[0].items] == [
        ("action", "New"),
        ("separator", None),
        ("action", "Quit"),
    ]
    # An in-window dropdown trigger was rendered for the menu.
    assert "File" in tb._internal._menu_triggers

    # The dropdown received the items (here: 3, incl. the separator).
    trigger = tb._internal._menu_triggers["File"]
    assert len(trigger.context_menu._items) == 3

    # Item commands are wired through to the menu model.
    model.groups[0].items[0].on_click()
    assert fired == ["new"]


def test_add_menu_returns_context_manager_group(app):
    import bootstack as bs

    tb = bs.Toolbar(parent=app)
    group = tb.add_menu("View")
    # Returned object is the MenuGroup builder (usable without `with`).
    group.add_check("Status Bar", checked=True)
    group.add_radio("Light", group="theme")
    group.add_radio("Dark", group="theme")
    assert [i.type for i in group.items] == ["check", "radio", "radio"]


def test_multiple_menus_share_one_model(app):
    import bootstack as bs

    tb = bs.Toolbar(parent=app)
    tb.add_menu("File")
    tb.add_menu("Edit")
    assert [g.text for g in tb._internal.menu_model] == ["File", "Edit"]
    assert set(tb._internal._menu_triggers) == {"File", "Edit"}


def test_no_menu_model_without_add_menu(app):
    import bootstack as bs

    tb = bs.Toolbar(parent=app)
    tb.add_button(text="Save", icon="floppy")
    assert tb._internal.menu_model is None
