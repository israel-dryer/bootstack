"""The AppShell sidebar-toggle shortcut — modifier key required (#403).

The shortcut is Ctrl-B (Cmd-B on macOS). It must NOT fire on a bare `b` typed
into a field: Tk resolves the `Command` modifier word to `Mod1` on Windows and
X11, and Windows reports `Mod1` for NumLock, so a `<Command-b>` binding left
unguarded off macOS matched every unmodified `b` on a machine with NumLock on.

The NumLock bit is supplied explicitly (`state=8`) rather than being taken from
the host, so the test reproduces the reported failure on any machine.
"""

from __future__ import annotations

import pytest

import bootstack as bs

pytestmark = pytest.mark.isolated

# Tk's Mod1 bit — set by NumLock on Windows, by Alt on X11.
_MOD1 = 8


@pytest.fixture(scope="module")
def shell():
    s = bs.AppShell(title="Shortcuts", size=(800, 540))
    s.__enter__()
    with s.page_nav() as nav:
        with nav.add_page("entry", text="Data Entry", icon="clipboard2-data"):
            field = bs.TextField(label="Text Field")
    s.navigate("entry")
    s._internal.update()
    s._entry_widget = field.tk
    try:
        yield s
    finally:
        try:
            s._internal.destroy()
        except Exception:
            pass


@pytest.fixture()
def expanded(shell):
    """Start each test from an expanded sidebar."""
    shell.sidebar_mode = "expanded"
    shell._internal.update()
    return shell


def test_modifier_shortcut_toggles_the_sidebar(expanded):
    # Precondition: the shortcut is wired at all, so a "did not toggle"
    # assertion below cannot pass vacuously on a shell that binds nothing.
    entry = expanded._entry_widget
    entry.focus_force()
    entry.event_generate("<Control-KeyPress-b>")
    expanded._internal.update()
    assert expanded.sidebar_mode != "expanded"


def test_bare_b_does_not_toggle_the_sidebar(expanded):
    # A plain "b" — no modifier, but carrying the NumLock bit that Windows
    # reports as Mod1. Typing must reach the field and leave the sidebar alone.
    entry = expanded._entry_widget
    entry.focus_force()
    entry.event_generate("<KeyPress-b>", state=_MOD1)
    expanded._internal.update()
    assert expanded.sidebar_mode == "expanded"


def test_bare_b_without_numlock_does_not_toggle_the_sidebar(expanded):
    entry = expanded._entry_widget
    entry.focus_force()
    entry.event_generate("<KeyPress-b>")
    expanded._internal.update()
    assert expanded.sidebar_mode == "expanded"