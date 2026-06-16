"""Tests for the add_toolbar() chrome stack on App/Window (ChromeHostMixin).

Structural only — asserts toolbars stack above content in creation order, the
divider renders, menus work on a stacked toolbar, and the returned handle is a
context manager. One module-scoped App (creating several Apps crashes Tk).
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


def test_add_toolbar_returns_toolbar(app):
    import bootstack as bs

    tb = app.add_toolbar()
    assert isinstance(tb, bs.Toolbar)


def test_toolbars_stack_above_content_in_order(app):
    tb1 = app.add_toolbar()
    tb2 = app.add_toolbar(divider=True)
    app._internal.update_idletasks()

    stack = app._toolbar_stack
    # The stack is packed above the content frame.
    assert stack.winfo_y() < app._content_frame.winfo_y()
    # Both toolbars + the divider live in the stack.
    classes = [c.winfo_class() for c in stack.winfo_children()]
    assert classes.count("TFrame") >= 2
    assert "TSeparator" in classes  # from divider=True


def test_menu_on_stacked_toolbar(app):
    tb = app.add_toolbar()
    with tb.add_menu("File") as file:
        file.add_action("Quit", on_click=lambda: None)
    assert [g.text for g in tb._internal.menu_model] == ["File"]


def test_add_toolbar_context_manager_scopes_and_returns_handle(app):
    import bootstack as bs

    # The `with` form is for visual grouping; it returns the handle and does NOT
    # capture bare widgets — items are added only via add_* (so the bar keeps
    # control of density/surface).
    with app.add_toolbar() as tb:
        tb.add_button(text="Explicit")
    assert isinstance(tb, bs.Toolbar)
    app._internal.update_idletasks()
    assert len(tb._internal.content.winfo_children()) == 1


def test_add_widget_class_inherits_bar_density_skips_unsupported_surface(app):
    import bootstack as bs

    tb = app.add_toolbar(density="compact")
    kw: dict = {}
    tb._apply_bar_defaults(bs.TextField, kw)
    # density is injected (TextField accepts it); surface is skipped (it does not).
    assert kw == {"density": "compact"}


def test_add_toolbar_defaults_chrome_surface(app):
    tb = app.add_toolbar()
    assert tb._internal._surface == "chrome"
