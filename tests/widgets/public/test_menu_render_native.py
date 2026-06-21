"""Structural tests for the native (macOS) menu-bar renderer.

`tk.Menu` is cross-platform, so the cascade *structure* is verified here on any
OS; the native *appearance* (global menu bar) is verified by hand on macOS.
One module-scoped App.
"""
from __future__ import annotations

import pytest

from bootstack.widgets._impl.composites.menu import MenuModel
from bootstack.widgets._impl.composites.menu.render_native import NativeMenuBar

pytestmark = pytest.mark.gui


def _sample_model() -> MenuModel:
    model = MenuModel()
    with model.add_menu("File") as file:
        file.add_action("Open", icon="folder2-open", shortcut="Mod+O", on_click=lambda: None)
        file.add_divider()
        file.add_action("Quit", shortcut="Mod+Q", on_click=lambda: None)
    with model.add_menu("Edit") as edit:
        edit.add_action("Undo", on_click=lambda: None)
        edit.add_check("Word wrap", checked=True)
        edit.add_radio("Light", value="light", group="theme")
        edit.add_radio("Dark", value="dark", group="theme")
    return model


def _menubar_widget(root):
    name = root["menu"]
    return root.nametowidget(name)


def test_assigns_menubar_with_one_cascade_per_group(app):
    root = app._tk_root
    bar = NativeMenuBar(root, _sample_model())
    try:
        menubar = _menubar_widget(root)
        assert menubar.index("end") == 1  # two cascades: File, Edit
        assert menubar.type(0) == "cascade"
        assert menubar.entrycget(0, "label") == "File"
        assert menubar.entrycget(1, "label") == "Edit"
    finally:
        bar.destroy()


def test_file_submenu_entry_types_and_accelerator(app):
    root = app._tk_root
    bar = NativeMenuBar(root, _sample_model())
    try:
        menubar = _menubar_widget(root)
        file_menu = root.nametowidget(menubar.entrycget(0, "menu"))
        # Open (command), separator, Quit (command)
        assert [file_menu.type(i) for i in range(file_menu.index("end") + 1)] == [
            "command", "separator", "command",
        ]
        assert file_menu.entrycget(0, "label") == "Open"
        # Accelerator is display text (no icon — icons are dropped on macOS).
        acc = file_menu.entrycget(0, "accelerator")
        assert acc and "O" in acc
    finally:
        bar.destroy()


def test_edit_submenu_has_check_and_radios(app):
    root = app._tk_root
    bar = NativeMenuBar(root, _sample_model())
    try:
        menubar = _menubar_widget(root)
        edit_menu = root.nametowidget(menubar.entrycget(1, "menu"))
        types = [edit_menu.type(i) for i in range(edit_menu.index("end") + 1)]
        assert types == ["command", "checkbutton", "radiobutton", "radiobutton"]
    finally:
        bar.destroy()


def test_rebuild_reflects_model_changes(app):
    root = app._tk_root
    model = MenuModel()
    model.add_menu("File")
    bar = NativeMenuBar(root, model)
    try:
        assert _menubar_widget(root).index("end") == 0  # one cascade
        model.add_menu("Edit")
        bar.rebuild()
        assert _menubar_widget(root).index("end") == 1  # two cascades
    finally:
        bar.destroy()


def test_destroy_detaches_menubar(app):
    root = app._tk_root
    bar = NativeMenuBar(root, _sample_model())
    bar.destroy()
    assert root["menu"] in ("", None)