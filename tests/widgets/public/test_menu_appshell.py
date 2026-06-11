"""Smoke tests for the AppShell `.menu` facade (Windows/Linux themed path).

Structural only; visual appearance is verified by hand. One module-scoped AppShell.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.gui


@pytest.fixture(scope="module")
def shell():
    import bootstack as bs

    shell = bs.AppShell(window_style=None)
    shell._internal.withdraw()
    try:
        yield shell
    finally:
        try:
            shell._internal.destroy()
        except Exception:
            pass


def test_appshell_menu_renders_themed_strip(shell):
    menu = shell.menu
    try:
        with menu.add_menu("File") as file:
            file.add_action("Open", on_click=lambda: None)
            file.add_action("Quit", on_click=lambda: None)
        menu.refresh()
        assert menu._renderer is not None
        assert len(menu._renderer._triggers) == 1
    finally:
        menu.clear()
        menu.refresh()


def test_strip_packs_above_the_toolbar(shell):
    """The menu strip is packed before the toolbar (i.e. visually above it)."""
    menu = shell.menu
    try:
        with menu.add_menu("Edit") as edit:
            edit.add_action("Undo", on_click=lambda: None)
        menu.refresh()
        strip = menu._renderer
        toolbar = shell._internal._toolbar
        # Both pack into the same content root; the strip comes first.
        parent = shell._menu_pack_parent()
        kids = parent.pack_slaves()
        assert strip in kids and toolbar in kids
        assert kids.index(strip) < kids.index(toolbar)
    finally:
        menu.clear()
        menu.refresh()


def test_menu_root_is_the_tk_root(shell):
    # AppShell's internal is itself a Tk root, so the native menubar attaches there.
    assert shell._menu_root() is shell._internal