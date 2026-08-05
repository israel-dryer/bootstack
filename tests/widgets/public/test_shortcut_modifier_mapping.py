"""`Command`/`Option` in a shortcut pattern, off macOS (#405).

#403 closed one call site — the AppShell sidebar toggle — but the same trap was
still reachable through the public `Shortcuts` API, because the shared modifier
map guarded only `mod` and `alt`. `command` and `option` were mapped to the
toolkit words `Command` and `Option` on every platform, while the display map
had always rendered them as `Ctrl` and `Alt`.

Off macOS the toolkit resolves those two words to its generic Mod1 and Mod2
slots, and Windows reports NumLock as Mod1. So `Shortcut(pattern="Command+S")`
produced a menu accelerator reading *Ctrl+S* beside a binding that fired on a
bare `s` for anyone with NumLock on — and the display/binding mismatch is what
kept it quiet, since nothing on screen suggested the shortcut was listening for
anything else.

Measured rather than assumed: bound on its own, `<Command-s>` fires for a plain
`s` carrying Mod1, and `<Option-k>` for a plain `k` carrying Mod2. That is what
`test_the_toolkit_words_really_do_catch_bare_keys` pins, so the mapping tests
below cannot quietly become assertions about nothing.
"""
from __future__ import annotations

import tkinter

import pytest

from bootstack.shortcuts import Shortcut
from bootstack._runtime.shortcuts import IS_MAC

# Tk's generic modifier bits. Windows reports NumLock as Mod1.
_MOD1 = 8
_MOD2 = 16


def _shortcut(pattern: str) -> Shortcut:
    return Shortcut(key="probe", pattern=pattern, command=lambda: None)


@pytest.mark.parametrize(
    "pattern",
    [
        "Command+S",
        "Option+K",
        "Mod+S",
        "Alt+K",
        "Ctrl+S",
        "Shift+Command+P",
        "Command+Option+I",
    ],
)
def test_binding_and_display_name_the_same_modifiers(pattern):
    """The invariant, and the one that holds on both platforms.

    A shortcut whose binding disagrees with its own menu label is the defect;
    which physical key each maps to is platform detail, but that they agree is
    not.
    """
    shortcut = _shortcut(pattern)
    binding, display = shortcut.binding, shortcut.display

    if IS_MAC:
        # Mac renders modifiers as symbols, so compare against those.
        assert ("Command" in binding) == ("⌘" in display)
        assert ("Option" in binding) == ("⌥" in display)
        assert ("Control" in binding) == ("⌃" in display)
    else:
        assert ("Control" in binding) == ("Ctrl" in display)
        assert ("Alt" in binding) == ("Alt" in display)
        # The toolkit words must not survive into a binding off macOS at all.
        assert "Command" not in binding
        assert "Option" not in binding


@pytest.mark.skipif(IS_MAC, reason="the mismatch is an off-macOS defect")
@pytest.mark.parametrize(
    "pattern,expected",
    [
        ("Command+S", "<Control-s>"),
        ("Option+K", "<Alt-k>"),
        ("Shift+Command+P", "<Shift-Control-p>"),
        ("Command+Option+I", "<Control-Alt-i>"),
    ],
)
def test_command_and_option_bind_the_keys_their_labels_promise(pattern, expected):
    assert _shortcut(pattern).binding == expected


@pytest.mark.skipif(IS_MAC, reason="Command/Option are the real modifiers there")
@pytest.mark.parametrize("word,key,state", [("Command", "s", _MOD1), ("Option", "k", _MOD2)])
def test_the_toolkit_words_really_do_catch_bare_keys(shown_app, word, key, state):
    """Why the mapping above matters, established directly.

    Without this, every assertion above is just string comparison and would keep
    passing even if the toolkit stopped resolving these words to Mod1/Mod2.

    Bound on its own — binding both `<Command-s>` and `<Mod1-s>` to one widget
    lets the toolkit match only the more specific of the two, which reads as
    though the trap were absent.

    Runs in its own mapped `Toplevel` rather than in the shared root. A frame
    packed straight into the App root is not reliably mapped once earlier tests
    have filled it, and the toolkit drops synthesized key events at an unmapped
    window — which failed here as "the trap is gone" rather than as a setup
    problem. The `winfo_ismapped` precondition below is what keeps that from
    being silent a second time.
    """
    window = tkinter.Toplevel(shown_app._tk_root)
    window.geometry("200x100+100+100")
    window.deiconify()
    window.update()
    window.focus_force()
    window.update()

    fired: list = []
    try:
        assert window.winfo_ismapped(), "precondition: the window must be mapped"
        window.bind(f"<{word}-{key}>", lambda e: fired.append(word))

        window.event_generate(f"<KeyPress-{key}>", state=state)
        window.update()
        assert fired == [word], f"<{word}-{key}> no longer catches a bare {key}"

        fired.clear()
        window.event_generate(f"<KeyPress-{key}>", state=0)
        window.update()
        assert fired == [], "control: an unmodified key must not match"
    finally:
        window.destroy()
