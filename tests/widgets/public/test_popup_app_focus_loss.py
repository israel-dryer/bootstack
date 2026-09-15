"""An open popup closes when another application takes the foreground (#516).

Each test opens a popup, starts a second process that takes the foreground, and
waits for the popup to close. Windows only: the switch is confirmed through
user32. If the environment will not hand the foreground over, the test skips —
that is the desktop session, not the product.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time

import pytest

import bootstack as bs

pytestmark = [
    pytest.mark.isolated,
    pytest.mark.skipif(sys.platform != "win32", reason="foreground detection uses user32"),
]

CHILD = (
    "import tkinter as t; r=t.Tk(); r.geometry('320x200+80+80');"
    "r.after(200, lambda:(r.lift(), r.attributes('-topmost', 1), r.focus_force()));"
    "r.after(15000, r.destroy); r.mainloop()"
)


def _foreground_pid() -> int:
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(user32.GetForegroundWindow(), ctypes.byref(pid))
    return pid.value


def _bring_to_foreground(root):
    # Windows refuses a foreground request from a process that did not receive
    # the last input; sharing the foreground thread's input state lifts that.
    import ctypes

    user32, kernel32 = ctypes.windll.user32, ctypes.windll.kernel32
    hwnd = int(root.wm_frame(), 16)
    fg_thread = user32.GetWindowThreadProcessId(user32.GetForegroundWindow(), None)
    me = kernel32.GetCurrentThreadId()
    attached = bool(fg_thread and fg_thread != me and user32.AttachThreadInput(me, fg_thread, True))
    try:
        user32.BringWindowToTop(hwnd)
        user32.SetForegroundWindow(hwnd)
    finally:
        if attached:
            user32.AttachThreadInput(me, fg_thread, False)


def _poll(root, condition, timeout=5.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        root.update()
        if condition():
            return True
        time.sleep(0.02)
    return False


def _take_focus(root):
    _bring_to_foreground(root)
    root.focus_force()
    if not _poll(root, lambda: _foreground_pid() == os.getpid() and root.focus_get() is not None):
        pytest.skip("the test process never held the foreground")


def _switch_away(root):
    child = subprocess.Popen([sys.executable, "-c", CHILD])
    if not _poll(root, lambda: _foreground_pid() == child.pid):
        child.kill()
        child.wait()
        pytest.skip("the second process never took the foreground")
    return child


def test_menu_closes_when_another_app_takes_the_foreground(shown_app):
    root = shown_app._tk_root
    menu = bs.MenuButton("Menu")
    menu.add_item("Open")
    menu.add_item("Save")
    _take_focus(root)
    child = None
    try:
        menu.show_menu()
        top = menu._internal._context_menu._impl._toplevel
        assert _poll(root, lambda: top.winfo_viewable() and root.focus_get() is not None)
        # Focus is inside the menu, so the switch reaches it as a focus-out.
        assert str(root.focus_get()).startswith(str(top))

        child = _switch_away(root)

        assert _poll(root, lambda: not top.winfo_viewable())
    finally:
        if child is not None:
            child.kill()
            child.wait()


def test_searchable_select_closes_when_another_app_takes_the_foreground(shown_app):
    root = shown_app._tk_root
    select = bs.Select(["Apple", "Banana", "Cherry"], value="Apple", searchable=True)
    internal = select._internal
    _take_focus(root)
    child = None
    try:
        internal._show_selection_options()
        assert _poll(root, lambda: internal._popup_open and root.focus_get() is not None)
        # Focus stays in the entry while the list is open, so the popup's own
        # focus-out never fires; only the entry's binding can close it.
        assert root.focus_get() is internal.entry_widget

        child = _switch_away(root)

        assert _poll(root, lambda: not internal._popup_open)
    finally:
        if child is not None:
            child.kill()
            child.wait()