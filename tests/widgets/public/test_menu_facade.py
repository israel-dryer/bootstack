"""Smoke tests for the window `menu` facade (Windows/Linux themed path).

Structural only; visual appearance is verified by hand. One module-scoped App.
"""
from __future__ import annotations

import pytest

from bootstack._runtime.shortcuts import get_shortcuts

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


@pytest.fixture(autouse=True)
def _reset_shortcuts():
    svc = get_shortcuts()
    svc._shortcuts.clear()
    svc._bound_windows.clear()
    svc._bindings.clear()
    yield
    svc._shortcuts.clear()
    svc._bound_windows.clear()
    svc._bindings.clear()


def test_menu_is_lazy_singleton(app):
    assert app.menubar is app.menubar  # same object each access


def test_add_menu_renders_themed_strip(app):
    menu = app.menubar
    try:
        with menu.add_menu("File") as file:
            file.add_action("Open", on_click=lambda: None)
            file.add_action("Quit", on_click=lambda: None)
        menu.refresh()
        assert menu._renderer is not None
        assert len(menu._renderer._triggers) == 1
        assert len(menu._renderer._triggers[0].keys()) == 2
    finally:
        menu.clear()
        menu.refresh()


def test_pattern_shortcuts_bound_to_window(app):
    menu = app.menubar
    try:
        with menu.add_menu("File") as file:
            file.add_action("Save", shortcut="Mod+S", on_click=lambda: None)
        menu.refresh()
        patterns = {s.pattern for s in get_shortcuts().all().values()}
        assert "Mod+S" in patterns
    finally:
        menu.clear()
        menu.refresh()


def test_load_declarative_then_render(app):
    menu = app.menubar
    try:
        menu.load([
            {"text": "File", "items": [{"text": "Open", "on_click": lambda: None}]},
            {"text": "Edit", "items": [{"text": "Undo", "on_click": lambda: None}]},
        ])
        menu.refresh()
        assert len(menu._renderer._triggers) == 2
    finally:
        menu.clear()
        menu.refresh()


def test_clear_tears_down_strip(app):
    menu = app.menubar
    with menu.add_menu("File") as file:
        file.add_action("Open", on_click=lambda: None)
    menu.refresh()
    assert menu._renderer is not None

    menu.clear()
    menu.refresh()
    assert menu._renderer is None


def test_idle_debounce_flush_via_update(app):
    """Building inside a block and flushing idle tasks renders once."""
    menu = app.menubar
    try:
        with menu.add_menu("View") as view:
            view.add_action("Zoom in", on_click=lambda: None)
        app._tk_root.update_idletasks()  # fire the coalesced after_idle rebuild
        assert menu._renderer is not None
        assert len(menu._renderer._triggers) == 1
    finally:
        menu.clear()
        menu.refresh()