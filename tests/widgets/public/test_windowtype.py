"""Cross-platform `windowtype` mapping on the internal Toplevel (#308).

`windowtype` is a single switch that resolves to the right native window on
each platform: `-type` on X11, a `MacWindowStyle` on Aqua, and on Windows the
chromeless types resolve to override-redirect while `'utility'` resolves to a
tool window. These assert the Windows mapping (the platform this runs on) and
the cross-platform back-compat for the existing chromeless callers.
"""
from __future__ import annotations

import pytest

from bootstack._runtime.toplevel import Toplevel


def _winsys(app) -> str:
    return app._tk_root.tk.call("tk", "windowingsystem")


@pytest.mark.parametrize("windowtype", ["splash", "tooltip", "dock"])
def test_chromeless_types_override_redirect_on_win32(app, windowtype):
    """splash/tooltip/dock resolve to override-redirect (no chrome) on Windows."""
    top = Toplevel(windowtype=windowtype)
    try:
        if _winsys(app) == "win32":
            assert bool(top.overrideredirect()) is True
            assert top.attributes("-toolwindow") == 0
    finally:
        top.destroy()


def test_utility_type_is_toolwindow_not_chromeless_on_win32(app):
    """'utility' is a minimal-chrome tool window, never override-redirect."""
    top = Toplevel(windowtype="utility")
    try:
        if _winsys(app) == "win32":
            assert top.attributes("-toolwindow") == 1
            assert bool(top.overrideredirect()) is False
    finally:
        top.destroy()


def test_plain_window_unchanged(app):
    """No windowtype leaves the window fully decorated."""
    top = Toplevel()
    try:
        assert bool(top.overrideredirect()) is False
        if _winsys(app) == "win32":
            assert top.attributes("-toolwindow") == 0
    finally:
        top.destroy()


def test_explicit_overrideredirect_still_honored(app):
    """The existing toast/tooltip path (windowtype + explicit override) is unchanged."""
    top = Toplevel(windowtype="tooltip", overrideredirect=True)
    try:
        if _winsys(app) == "win32":
            assert bool(top.overrideredirect()) is True
    finally:
        top.destroy()