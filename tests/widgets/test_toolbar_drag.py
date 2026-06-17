"""Drag re-anchor math for un-maximizing an undecorated window (#165).

Dragging a maximized window restores it to its normal size *under the cursor*.
The grab offset is captured against the maximized width, so on restore the
window must be repositioned to the cursor's same relative spot. Pure logic —
`_on_drag_motion`'s zoomed branch is exercised against a stub toplevel, so no Tk
root is needed.
"""
from __future__ import annotations

from bootstack.widgets._impl.composites.toolbar import Toolbar


class _StubWindow:
    def __init__(self):
        self._state = "zoomed"
        self._w = 1920  # maximized width
        self._x = 0
        self._y = 0
        self.geometry_calls: list[str] = []

    def state(self, value=None):
        if value is None:
            return self._state
        self._state = value
        if value == "normal":
            self._w = 800  # restored width

    def winfo_width(self):
        return self._w

    def winfo_rootx(self):
        return self._x

    def winfo_rooty(self):
        return self._y

    def update_idletasks(self):
        pass

    def geometry(self, spec):
        self.geometry_calls.append(spec)


class _StubEvent:
    def __init__(self, x_root, y_root):
        self.x_root = x_root
        self.y_root = y_root


def _drag_motion(window, event):
    tb = type(
        "_TB",
        (),
        {
            "winfo_toplevel": lambda self: window,
            "_sync_maximize_icon": lambda self, name: None,
            "_drag_start_x": 0,
            "_drag_start_y": 0,
        },
    )()
    Toolbar._on_drag_motion(tb, event)
    return tb


def test_unmaximize_reanchors_window_under_cursor():
    # Cursor at the horizontal midpoint of the maximized window, on the title bar.
    win = _StubWindow()
    tb = _drag_motion(win, _StubEvent(x_root=960, y_root=10))
    # frac_x = 960/1920 = 0.5 -> over the 800px restored width that's 400px in;
    # new_x = 960 - 400 = 560. The 10px title-bar offset is preserved -> new_y = 0.
    assert win.geometry_calls == ["+560+0"]
    assert win.state() == "normal"
    # The drag origin re-anchors to the current cursor for subsequent motion.
    assert tb._drag_start_x == 960
    assert tb._drag_start_y == 10


def test_unmaximize_keeps_cursor_fraction_near_right_edge():
    # Cursor near the right edge stays near the right edge of the restored window.
    win = _StubWindow()
    _drag_motion(win, _StubEvent(x_root=1824, y_root=5))  # 95% across, on the bar
    # frac_x = 1824/1920 = 0.95 -> 0.95*800 = 760; new_x = 1824 - 760 = 1064.
    # 5px title-bar offset preserved -> new_y = 0.
    assert win.geometry_calls == ["+1064+0"]