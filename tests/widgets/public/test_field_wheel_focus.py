"""The mouse wheel steps a number field only while it has focus (#525).

Over an unfocused field the wheel belongs to the page: it must scroll an
enclosing ScrollView and leave the value alone. While focused, the wheel steps
the field and each widget keeps its own value/text split: a `NumberField` step
commits at once, a `SpinnerField` step moves the text and commits on blur.
"""
from __future__ import annotations

import sys
import time

import pytest

import bootstack as bs
from bootstack._runtime import wheel

pytestmark = pytest.mark.gui

FIELDS = {
    "NumberField": lambda: bs.NumberField(5),
    "SpinnerField": lambda: bs.SpinnerField(5, min_value=0, max_value=99),
}


def _pump(root, condition, timeout=3.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        root.update()
        if condition():
            return True
        time.sleep(0.02)
    return False


def _show(win, entry):
    win.show()
    assert _pump(entry, entry.winfo_ismapped), "precondition: the field is mapped"


def _bring_to_foreground(toplevel):
    # Windows refuses a foreground request from a process that did not receive
    # the last input; sharing the foreground thread's input state lifts that.
    if sys.platform != "win32":
        return
    import ctypes

    user32, kernel32 = ctypes.windll.user32, ctypes.windll.kernel32
    hwnd = int(toplevel.wm_frame(), 16)
    fg_thread = user32.GetWindowThreadProcessId(user32.GetForegroundWindow(), None)
    me = kernel32.GetCurrentThreadId()
    attached = bool(fg_thread and fg_thread != me and user32.AttachThreadInput(me, fg_thread, True))
    try:
        user32.BringWindowToTop(hwnd)
        user32.SetForegroundWindow(hwnd)
    finally:
        if attached:
            user32.AttachThreadInput(me, fg_thread, False)


def _focus(widget):
    _bring_to_foreground(widget.winfo_toplevel())
    widget.focus_force()
    if not _pump(widget, lambda: widget.focus_get() is widget):
        pytest.skip("keyboard focus could not be taken in this environment")


def _wheel(widget, notches):
    """Send `notches` wheel notches to `widget`; positive rolls away from the user."""
    for _ in range(abs(notches)):
        if wheel.uses_x11_buttons(widget):
            button = 4 if notches > 0 else 5
            widget.event_generate(f"<ButtonPress-{button}>", x=3, y=3, when="now")
            widget.event_generate(f"<ButtonRelease-{button}>", x=3, y=3, when="now")
        else:
            delta = 120 if notches > 0 else -120
            widget.event_generate("<MouseWheel>", delta=delta, x=3, y=3, when="now")
    widget.update()


@pytest.mark.parametrize("kind", FIELDS)
def test_wheel_over_an_unfocused_field_scrolls_the_page(shown_app, kind):
    win = bs.Window(title="wheel", size=(320, 200))
    try:
        with win:
            with bs.ScrollView(height=120) as sv:
                field = FIELDS[kind]()
                for i in range(40):
                    filler = bs.Label(f"row {i}")
        entry = field._entry_widget()
        _show(win, entry)
        root = shown_app._tk_root
        assert entry.focus_get() is not entry, "precondition: the field is not focused"

        _wheel(filler._internal, -3)
        assert sv.scroll_position[0] > 0.0, "precondition: the ScrollView scrolls on the wheel"
        sv.scroll_to_top()
        root.update()

        text = entry.get()
        _wheel(entry, -3)

        assert entry.get() == text, "the wheel stepped a field that has no focus"
        assert sv.scroll_position[0] > 0.0, "the field swallowed the wheel instead of scrolling"
    finally:
        win.close()


@pytest.mark.parametrize("kind", FIELDS)
def test_wheel_on_a_focused_field_keeps_the_value_text_split(shown_app, kind):
    win = bs.Window(title="wheel", size=(320, 200))
    try:
        with win:
            field = FIELDS[kind]()
            other = bs.TextField("elsewhere")
        entry = field._entry_widget()
        _show(win, entry)
        start = field.value
        changes = []
        field.on_change(lambda e: changes.append((e.prev_value, e.value)))

        _focus(entry)
        _wheel(entry, 2)

        if kind == "NumberField":
            assert changes == [(5, 6), (6, 7)], "each focused step commits once"
        else:
            assert entry.get() == "7", "the focused wheel moved the text"
            assert field.value == start and changes == [], "the value waits for blur"

        _focus(other._entry_widget())

        if kind == "NumberField":
            assert changes == [(5, 6), (6, 7)], "blur repeated a committed step"
        else:
            assert changes == [(start, "7")], "blur commits the stepped text once"
    finally:
        win.close()


def test_wheel_over_a_spinner_field_does_not_step_the_focused_field(shown_app):
    win = bs.Window(title="wheel", size=(320, 200))
    try:
        with win:
            focused = bs.NumberField(5)
            spinner = bs.SpinnerField(5, min_value=0, max_value=99)
        target = spinner._entry_widget()
        _show(win, target)
        _focus(focused._entry_widget())

        _wheel(target, 2)

        assert focused.value == 5, "the wheel over the spinner stepped the focused field"
    finally:
        win.close()