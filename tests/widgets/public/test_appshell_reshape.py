"""The AppShell + Workbench navigation reshape — sidebar-host front doors.

`AppShell` is the single-tier sidebar host; `Workbench` is the two-tier workspace
host. A sidebar is declared with one of four front doors — `page_nav` /
`list_nav` / `tree_nav` / `custom_nav`; only `page_nav` is authored
(`add_page` / `add_header` / `add_divider`). Footer placement is `pin_to_footer=`,
and a page is itself a layout container (the `add_page` layout kwargs).

The structural tests need no Tk root. The functional tests share ONE module-scoped
`AppShell` (one App per process); `Workbench` is covered in `test_workbench.py`.
"""

from __future__ import annotations

import inspect

import pytest

import bootstack as bs
from bootstack.widgets.appshell import AppShell, PageNav, Workbench, Workspace
from bootstack.style.builders.sidenav import _selection_colors
from bootstack.style.style_builder_ttk import StyleBuilderTtk


# ----- Structural (no Tk root) -----

def test_class_surface_split():
    # AppShell is a sidebar host; it does NOT host workspaces.
    assert hasattr(AppShell, "page_nav")
    assert hasattr(AppShell, "list_nav")
    assert hasattr(AppShell, "tree_nav")
    assert hasattr(AppShell, "custom_nav")
    assert not hasattr(AppShell, "add_workspace")
    # Workbench hosts workspaces; it is NOT a sidebar host.
    assert hasattr(Workbench, "add_workspace")
    assert not hasattr(Workbench, "page_nav")
    assert not hasattr(Workbench, "list_nav")
    # A Workspace is a sidebar host (same front doors as AppShell).
    for name in ("page_nav", "list_nav", "tree_nav", "custom_nav"):
        assert hasattr(Workspace, name)


def test_no_legacy_footer_methods():
    # Footer placement is a flag, not a separate method.
    assert not hasattr(PageNav, "add_footer_page")
    assert not hasattr(Workbench, "add_footer_workspace")
    assert "pin_to_footer" in inspect.signature(PageNav.add_page).parameters
    assert "pin_to_footer" in inspect.signature(Workbench.add_workspace).parameters


def test_nav_variant_removed_from_constructor():
    # The selection variant moved to page_nav(variant=); it is no longer a kwarg.
    assert "nav_variant" not in inspect.signature(AppShell.__init__).parameters
    assert "nav_selection" not in inspect.signature(AppShell.__init__).parameters
    # variant lives on AppShell.page_nav, but NOT on the under-rail Workspace one.
    assert "variant" in inspect.signature(AppShell.page_nav).parameters
    assert "variant" not in inspect.signature(Workspace.page_nav).parameters


def test_add_page_has_layout_kwargs():
    params = inspect.signature(PageNav.add_page).parameters
    for k in ("layout", "padding", "gap", "horizontal_items", "columns", "rows"):
        assert k in params


# ----- Functional (one module-scoped AppShell) -----

@pytest.fixture(scope="module")
def shell():
    s = bs.AppShell(title="Reshape", size=(800, 540), nav_accent="primary")
    s.__enter__()
    try:
        yield s
    finally:
        try:
            s._internal.destroy()
        except Exception:
            pass


def test_page_nav_solid_and_footer(shell):
    with shell.page_nav(variant="solid") as nav:
        # A page is a column — layout kwargs configure it directly.
        with nav.add_page("home", text="Home", icon="house", padding=24, gap=12):
            bs.Label("Welcome")
        with nav.add_page("acct", text="Account", icon="person", pin_to_footer=True):
            bs.Label("Account")
    shell.navigate("home")
    shell._internal.update_idletasks()
    panel = shell.nav
    assert panel._variant == "nav-pill"      # standalone primary nav
    assert panel._selection == "solid"        # variant honored
    assert "acct" in panel._items             # footer item present
    assert shell.current == "home"


def test_builder_solid_vs_ghost_colors(shell):
    b = StyleBuilderTtk()
    opts = {"surface": "raised"}
    ghost_bg, _ = _selection_colors(b, "primary", {**opts, "selection_style": "ghost"})
    solid_bg, solid_fg = _selection_colors(b, "primary", {**opts, "selection_style": "solid"})
    assert solid_bg.lower() == b.color("primary").lower()   # filled accent
    assert solid_bg.lower() != ghost_bg.lower()             # ghost is a wash
    none_bg, _ = _selection_colors(b, None, {**opts, "selection_style": "solid"})
    assert none_bg.lower() != b.color("primary").lower()    # no accent -> neutral