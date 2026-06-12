"""Smoke tests for the App/Window command bar (`.commandbar`) + `menu_layout`.

Structural only; visuals verified by hand. ONE module-scoped App (creating
several Apps in one process crashes Tk) — layout variants are exercised by
toggling `_menu_layout` and re-arranging.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.gui


@pytest.fixture(scope="module")
def app():
    import bootstack as bs

    app = bs.App(window_style=None)
    app._tk_root.withdraw()
    try:
        yield app
    finally:
        try:
            app._tk_root.destroy()
        except Exception:
            pass


def test_toolbar_is_lazy_singleton(app):
    assert app.commandbar is app.commandbar


def test_toolbar_lives_in_the_chrome_row(app):
    tb = app.commandbar
    tb.add_button(label="Theme", on_click=lambda: None)
    assert tb._internal in app._chrome.pack_slaves()


def test_default_layout_is_fused(app):
    assert app._menu_layout == "fused"


def test_chrome_surface_defaults_and_threads(app):
    # Default chrome surface, and it threads into the menu strip so its
    # menubar-item triggers paint that surface (not their hardcoded default).
    assert app._chrome_surface == "chrome"
    with app.menubar.add_menu("Help") as h:
        h.add_action("About", on_click=lambda: None)
    app.menubar.refresh()
    assert app.menubar._renderer._surface == "chrome"


def test_chrome_divider_present_by_default(app):
    app._ensure_chrome()
    assert app._chrome_divider_enabled is True
    assert hasattr(app, "_chrome_divider")


def test_fused_then_stacked_rearranges(app):
    # Ensure both menu and toolbar exist in the chrome row.
    with app.menubar.add_menu("File") as f:
        f.add_action("Quit", on_click=lambda: None)
    app.commandbar  # realize it
    app.menubar.refresh()
    strip = app.menubar._renderer
    tb_widget = app.commandbar._internal

    # Fused → one row: menu strip left, both present, strip before toolbar.
    app._menu_layout = "fused"
    app._arrange_chrome()
    kids = app._chrome.pack_slaves()
    assert strip in kids and tb_widget in kids
    assert kids.index(strip) < kids.index(tb_widget)
    assert strip.pack_info().get("side") == "left"

    # Stacked → two rows: both packed side=top.
    app._menu_layout = "stacked"
    app._arrange_chrome()
    assert strip.pack_info().get("side") == "top"
    assert tb_widget.pack_info().get("side") == "top"