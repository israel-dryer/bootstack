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
    # Built through the context manager so the parent-context stack is left
    # balanced (`__enter__` without `__exit__` strands the shell on it).
    with bs.AppShell(title="Shortcuts", size=(800, 540)) as s:
        with s.page_nav() as nav:
            with nav.add_page("entry", text="Data Entry", icon="clipboard2-data"):
                field = bs.TextField(label="Text Field")
        s.navigate("entry")
    # The window must be MAPPED or focus_force lands on the root and the
    # synthesized keystrokes never reach the entry, which would make the
    # "typing still works" half of these tests pass vacuously. `run()` is what
    # normally reveals the shell, and the suite never calls it.
    s._internal.deiconify()
    s._internal.update()
    s._field = field
    s._entry_widget = field._internal.entry_widget
    try:
        yield s
    finally:
        try:
            s._internal.destroy()
        except Exception:
            pass


@pytest.fixture()
def expanded(shell):
    """Start each test from an expanded sidebar and an empty field."""
    shell.sidebar_mode = "expanded"
    shell._field.value = ""
    shell._entry_widget.focus_force()
    shell._internal.update()
    return shell


def test_modifier_shortcut_toggles_the_sidebar(expanded):
    # Precondition: the shortcut is wired at all, so a "did not toggle"
    # assertion below cannot pass vacuously on a shell that binds nothing.
    expanded._entry_widget.event_generate("<Control-KeyPress-b>")
    expanded._internal.update()
    assert expanded.sidebar_mode != "expanded"


def test_bare_b_does_not_toggle_the_sidebar(expanded):
    # A plain "b" — no modifier, but carrying the NumLock bit that Windows
    # reports as Mod1. Typing must reach the field and leave the sidebar alone.
    expanded._entry_widget.event_generate("<KeyPress-b>", state=_MOD1)
    expanded._internal.update()
    assert expanded.sidebar_mode == "expanded"
    assert expanded._field.text == "b"


def test_bare_b_without_numlock_does_not_toggle_the_sidebar(expanded):
    expanded._entry_widget.event_generate("<KeyPress-b>")
    expanded._internal.update()
    assert expanded.sidebar_mode == "expanded"
    assert expanded._field.text == "b"


def test_command_binding_exists_only_on_macos(shell):
    # The suite runs on Windows and Linux, where every test above exercises the
    # non-aqua branch only — so a typo in the guard would drop the macOS
    # shortcut with nothing failing. Assert the binding table directly.
    # `windowingsystem` is read from Tk rather than from the shell's cached
    # `winsys`, so the check does not lean on the same value the guard used.
    #
    # Match on the KEY, not on the literal sequence: off macOS Tk normalizes the
    # `Command` modifier word to `Mod1`, so the unguarded binding shows up as
    # `<Mod1-Key-b>` and a `"<Command-Key-b>" not in ...` assertion would pass
    # vacuously on the very platform this test runs on (measured, not assumed).
    b_bindings = {seq for seq in shell._internal.bind() if seq.endswith("-Key-b>")}
    assert "<Control-Key-b>" in b_bindings
    extra = b_bindings - {"<Control-Key-b>"}
    if shell._internal.tk.call("tk", "windowingsystem") == "aqua":
        assert len(extra) == 1, "Cmd-B must be bound on macOS"
    else:
        assert extra == set(), f"unguarded modifier binding off macOS: {extra}"
