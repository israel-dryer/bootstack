"""An undecorated AppShell gets the built-in title bar, like App and Window (#565)."""
from __future__ import annotations

import sys

import pytest

pytestmark = [
    pytest.mark.gui,
    pytest.mark.isolated,
    pytest.mark.skipif(sys.platform == "darwin", reason="overrideredirect disabled on macOS"),
]


def test_undecorated_appshell_gets_default_titlebar():
    import bootstack as bs

    shell = bs.AppShell(title="My App", undecorated=True)
    try:
        assert bool(shell.tk.overrideredirect())
        assert not getattr(shell, "_chrome_toolbars", None)
        shell._ensure_default_titlebar()  # the first thing run() does
        bars = [tb for tb, _ in getattr(shell, "_chrome_toolbars", None) or []]
        assert [tb._internal.show_window_controls for tb in bars] == [True]
    finally:
        shell.tk.destroy()
