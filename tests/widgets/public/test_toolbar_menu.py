"""Tests for Toolbar.add_menu — menus as toolbar items.

Structural only — asserts the toolbar builds a menu model + in-window dropdown
triggers and wires item commands. Visual appearance is verified by hand. One
module-scoped App (creating several Apps in one process crashes Tk).
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.gui


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


def _toplevel_menu(app):
    """Build a toolbar menu and return its themed (Win/Linux) backend.

    Skips on the macOS native backend, which has no Toplevel to dismiss —
    the system menu already closes on window interaction.
    """
    import bootstack as bs
    from bootstack.widgets._impl.composites.contextmenu import _ToplevelContextMenu

    tb = bs.Toolbar(parent=app)
    with tb.add_menu("File") as file:
        file.add_action("Quit", on_click=lambda: None)
    menu = tb._internal._menu_triggers["File"].context_menu._impl
    if not isinstance(menu, _ToplevelContextMenu):
        pytest.skip("native menu backend dismisses on its own")
    return tb, menu


class _Evt:
    def __init__(self, widget):
        self.widget = widget


def test_menu_dismisses_on_owning_window_move(app):
    """Dragging the title bar moves the window but fires no click, so the
    dropdown must dismiss on the window's own `<Configure>`/`<Unmap>` — else it
    floats at its old screen position ("hangs in the air"). Regression test."""
    _tb, menu = _toplevel_menu(app)
    root = app._tk_root

    # Post-show state: the dismiss bindings are installed on the window root,
    # and the popup is on screen.
    menu._click_binding_root = root
    menu._toplevel.winfo_viewable = lambda: True  # pretend it's mapped

    hidden = []
    menu.hide = lambda: hidden.append(True)

    # A child relayout (event.widget is a descendant) must NOT dismiss it.
    menu._on_window_change(_Evt(_tb._internal))
    assert hidden == []

    # The window itself moving/resizing/minimizing DOES dismiss it.
    menu._on_window_change(_Evt(root))
    assert hidden == [True]


def test_window_dismiss_bindings_torn_down_on_hide(shown_app):
    """The `<Configure>`/`<Unmap>` dismiss bindings are removed when the menu
    hides, so a closed menu leaves no live handlers on the window root."""
    app = shown_app
    _tb, menu = _toplevel_menu(app)
    root = app._tk_root

    # Simulate installed window bindings (as bind_click would do post-show).
    menu._click_binding_root = root
    hid = root.bind("<Configure>", menu._on_window_change, add="+")
    menu._window_handler_ids = [("<Configure>", hid)]

    menu.hide()
    assert menu._window_handler_ids == []
    assert menu._click_binding_root is None
