"""Tests for the add_toolbar() chrome stack on App/Window (ChromeHostMixin).

Structural only — asserts toolbars stack above content in creation order, the
divider renders, menus work on a stacked toolbar, and the returned handle is a
context manager. One module-scoped App (creating several Apps crashes Tk).
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.gui


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


def test_macos_menu_aggregation_order_and_filter(app):
    # The macOS native bar aggregates bridged toolbars' menus in stack order,
    # excluding any toolbar with use_macos_menus=False. (On Windows the bridge is
    # inactive — the aggregation model is what would feed the native bar.)
    with app.add_toolbar() as bridged:
        with bridged.add_menu("AggFile") as f:
            f.add_action("X", on_click=lambda: None)
        with bridged.add_menu("AggEdit") as e:
            e.add_action("Y", on_click=lambda: None)
    with app.add_toolbar(use_macos_menus=False) as unbridged:
        with unbridged.add_menu("AggTools") as t:
            t.add_action("Z", on_click=lambda: None)

    groups = [g.text for g in app._aggregate_native_menu_model()]
    # bridged menus appear in order...
    assert groups.index("AggFile") < groups.index("AggEdit")
    # ...the opted-out toolbar's menu does not.
    assert "AggTools" not in groups


def test_bridge_inactive_on_non_macos(app):
    # On Windows/Linux menus render in-window — the bridge does not hide triggers.
    with app.add_toolbar() as tb:
        with tb.add_menu("InWindow") as m:
            m.add_action("X", on_click=lambda: None)
    assert not app._menus_are_native()
    assert "InWindow" in tb._internal._menu_triggers
