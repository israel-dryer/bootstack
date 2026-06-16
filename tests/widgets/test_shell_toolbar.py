"""Tests for add_toolbar() on AppShell (the chrome stack mounts above the body).

Structural only. One module-scoped AppShell (creating several Tk roots in one
process crashes Tk).
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.gui


@pytest.fixture(scope="module")
def shell():
    import bootstack as bs

    shell = bs.AppShell(title="test", size=(700, 400))
    shell._internal.withdraw()
    try:
        yield shell
    finally:
        try:
            shell._internal.destroy()
        except Exception:
            pass


def test_add_toolbar_mounts_in_shell_stack_above_body(shell):
    tb = shell.add_toolbar()
    shell._internal.update_idletasks()
    stack = shell._internal.toolbar_stack
    # The toolbar landed in the shell's stack region, which sits above the body.
    assert tb._internal.winfo_parent().startswith(str(stack))
    assert stack.winfo_y() <= shell._internal._body.winfo_y()


def test_menu_on_shell_toolbar(shell):
    tb = shell.add_toolbar()
    with tb.add_menu("File") as file:
        file.add_action("Quit", on_click=lambda: None)
    assert [g.text for g in tb._internal.menu_model] == ["File"]


def test_shell_has_no_titlebar_accessor(shell):
    # The #162 titlebar band is retired — undecorated title bars are built with
    # add_toolbar(show_window_controls=True), so there is no shell.titlebar.
    assert not hasattr(shell, "titlebar")
