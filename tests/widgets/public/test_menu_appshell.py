"""Smoke tests for the AppShell `.menubar` facade (Windows/Linux themed path).

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
    menu = shell.menubar
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


def test_strip_packs_before_the_command_bar(shell):
    """The menu strip is packed before the command bar in the chrome row
    (left of it when fused, above it when stacked)."""
    menu = shell.menubar
    commandbar = shell.commandbar  # lazily builds the command bar into the chrome
    try:
        with menu.add_menu("Edit") as edit:
            edit.add_action("Undo", on_click=lambda: None)
        menu.refresh()
        strip = menu._renderer
        toolbar = commandbar._internal
        # Both pack into the same chrome row; the strip comes first.
        parent = shell._menu_strip_parent()
        kids = parent.pack_slaves()
        assert strip in kids and toolbar in kids
        assert kids.index(strip) < kids.index(toolbar)
    finally:
        menu.clear()
        menu.refresh()


def test_menu_root_is_the_tk_root(shell):
    # AppShell's internal is itself a Tk root, so the native menubar attaches there.
    assert shell._menu_root() is shell._internal