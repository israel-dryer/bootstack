"""Smoke tests for the themed (Windows/Linux) menu-bar renderer.

Structural only — asserts the strip builds the right triggers and items from a
model. Visual appearance is verified by hand. One module-scoped App (creating
several Apps in one process crashes Tk).
"""
from __future__ import annotations

import pytest

from bootstack.widgets._impl.composites.menu import MenuModel
from bootstack.widgets._impl.composites.menu.render_themed import ThemedMenuBar

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


def test_strip_builds_one_trigger_per_group(app):
    bar = ThemedMenuBar(app._tk_root, _sample_model())
    try:
        assert len(bar._triggers) == 2
        assert [t.configure_style_options("text") or t.cget("text") for t in bar._triggers]
    finally:
        bar.destroy()


def test_trigger_items_match_model(app):
    model = _sample_model()
    bar = ThemedMenuBar(app._tk_root, model)
    try:
        file_trigger, edit_trigger = bar._triggers
        # File: Open, separator, Quit
        assert len(file_trigger.keys()) == 3
        # Edit: Undo, Word wrap, Light, Dark
        assert len(edit_trigger.keys()) == 4
    finally:
        bar.destroy()


def test_radio_items_in_same_group_share_a_variable(app):
    model = MenuModel()
    with model.add_menu("View") as view:
        view.add_radio("Light", value="light", group="theme")
        view.add_radio("Dark", value="dark", group="theme")
    bar = ThemedMenuBar(app._tk_root, model)
    try:
        assert "theme" in bar._radio_vars
        assert len(bar._radio_vars) == 1
    finally:
        bar.destroy()


def test_rebuild_after_model_change(app):
    model = MenuModel()
    model.add_menu("File")
    bar = ThemedMenuBar(app._tk_root, model)
    try:
        assert len(bar._triggers) == 1
        model.add_menu("Edit")
        bar.rebuild()
        assert len(bar._triggers) == 2
    finally:
        bar.destroy()


def test_empty_model_builds_no_triggers(app):
    bar = ThemedMenuBar(app._tk_root, MenuModel())
    try:
        assert bar._triggers == []
    finally:
        bar.destroy()