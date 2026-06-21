"""Toolbar.add_sidebar_toggle() — the AppShell sidebar hamburger (#201).

`add_sidebar_toggle()` builds a button that collapses/expands the AppShell
sidebar. It defaults to `collapse='compact'` (shrink to the icon rail where the
sidebar can show icons, else hide) with a panel glyph, and `collapse='hidden'`
fully hides with a hamburger. It is AppShell-only — not a Workbench/App.

Structural tests need no Tk; functional tests share one module-scoped AppShell.
"""

from __future__ import annotations

import inspect

import pytest

import bootstack as bs

pytestmark = pytest.mark.isolated
from bootstack.errors import BootstackError
from bootstack.widgets.sidebar_toggle import SidebarToggle


# ----- Structural (no Tk root) -----

def test_toolbar_exposes_add_sidebar_toggle():
    assert hasattr(bs.Toolbar, "add_sidebar_toggle")
    # Not exported at the top level — it is shell-bound, not standalone.
    assert not hasattr(bs, "SidebarToggle")


def test_signature_defaults():
    p = inspect.signature(SidebarToggle.__init__).parameters
    for k in ("collapse", "icon", "expand_icon", "collapse_icon"):
        assert k in p
    assert p["collapse"].default == "compact"
    assert p["icon"].default is None  # resolved by mode


# ----- Functional (one module-scoped AppShell) -----

@pytest.fixture(scope="module")
def shell():
    s = bs.AppShell(title="SidebarToggle", size=(800, 540))
    s.__enter__()
    with s.page_nav() as nav:
        with nav.add_page("home", text="Home", icon="house"):
            bs.Label("Home")
        with nav.add_page("docs", text="Docs", icon="file-text"):
            bs.Label("Docs")
    s.navigate("home")
    s._internal.update_idletasks()
    try:
        yield s
    finally:
        try:
            s._internal.destroy()
        except Exception:
            pass


def test_default_compact_panel_glyph(shell):
    btn = shell.add_toolbar().add_sidebar_toggle()
    assert isinstance(btn, SidebarToggle)
    assert btn.icon == "layout-sidebar"


def test_hidden_variant_hamburger_glyph(shell):
    btn = shell.add_toolbar().add_sidebar_toggle(collapse="hidden")
    assert btn.icon == "list"


def test_compact_toggles_icon_rail(shell):
    btn = shell.add_toolbar().add_sidebar_toggle()
    shell.sidebar_mode = "expanded"
    shell._internal.update_idletasks()
    btn._toggle()
    assert shell.sidebar_mode == "compact"
    btn._toggle()
    assert shell.sidebar_mode == "expanded"


def test_hidden_toggles_visibility(shell):
    btn = shell.add_toolbar().add_sidebar_toggle(collapse="hidden")
    shell.sidebar_mode = "expanded"
    shell._internal.update_idletasks()
    btn._toggle()
    assert shell.sidebar_mode == "hidden"
    btn._toggle()
    assert shell.sidebar_mode == "expanded"


def test_stateful_icons_reflect_state(shell):
    btn = shell.add_toolbar().add_sidebar_toggle(
        expand_icon="chevron-right", collapse_icon="chevron-left"
    )
    shell.sidebar_mode = "expanded"
    btn._sync_icon()
    assert btn.icon == "chevron-left"   # expanded -> the collapse affordance
    shell.sidebar_mode = "compact"
    btn._sync_icon()
    assert btn.icon == "chevron-right"  # collapsed -> the expand affordance
    shell.sidebar_mode = "expanded"


def test_rejects_non_appshell_host(shell):
    bar = shell.add_toolbar()
    bar._host = None
    with pytest.raises(BootstackError):
        bar.add_sidebar_toggle()
    bar._host = object()
    with pytest.raises(BootstackError):
        bar.add_sidebar_toggle()
