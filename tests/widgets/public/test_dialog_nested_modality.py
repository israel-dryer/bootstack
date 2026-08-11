"""A dialog stays modal after a nested modal closes.

A modal `Dialog` takes the grab with `grab_set()`. Tk releases a grab when the
window holding it is destroyed, but it does NOT restore the grab that window
displaced — so a second modal opened from inside the first took the grab over
and then dropped it entirely. The outer dialog was left on screen and still
blocking its caller inside `show()`, while the user could click straight back
into the main window and drive the app underneath it (issue #440).

That is reachable from ordinary code: a dialog button command that calls
`bs.alert(...)`, which is exactly what `docs/widgets/dialog.rst` taught for
refusing a press until it was changed to `bs.toast(...)`. `QueryDialog._on_submit`
is a second instance inside the framework itself.

⚠ The control matters here. "The grab is gone" is also what a dialog closing
normally looks like, so a test that only asserts the outer dialog is modal
after nesting can pass for the wrong reason if the driving never nested
anything. `test_a_dialog_keeps_its_grab_when_nothing_nests` is the same
measurement over a stretch with no nested modal.
"""
from __future__ import annotations

import tkinter

import pytest

import bootstack as bs
from bootstack.dialogs import Dialog, DialogButton

pytestmark = pytest.mark.gui


def _outer(app, body):
    """A modal dialog that runs `body(top)` once it is up, then closes."""
    dialog = Dialog(
        title="outer",
        content_builder=lambda: bs.Label("outer"),
        buttons=[DialogButton(text="OK", role="primary", result="ok")],
        parent=app._tk_root,
    )
    state: dict = {}

    def drive():
        top = dialog.toplevel
        if top is None or not top.winfo_exists():
            state["error"] = "the outer dialog never came up"
            return
        try:
            state["before"] = top.grab_current()
            state["kind_before"] = top.grab_status()
            body(top)
            state["after"] = top.grab_current()
            state["kind_after"] = top.grab_status()
            state["still_modal"] = top.grab_current() is top
            state["outer"] = top
        finally:
            if top.winfo_exists():
                top.destroy()

    guard = app._tk_root.after(10000, lambda: (
        dialog.toplevel.destroy()
        if dialog.toplevel is not None and dialog.toplevel.winfo_exists()
        else None
    ))
    try:
        app._tk_root.after(300, drive)
        dialog.show()
    finally:
        # The root outlives this test; a timer left queued fires during a later
        # one and would destroy an unrelated Toplevel.
        app._tk_root.after_cancel(guard)

    assert "error" not in state, state["error"]
    return state


def _nest(parent_top, depth: int) -> None:
    """Open `depth` modal dialogs inside one another, closing from the inside."""
    if depth == 0:
        return
    inner = Dialog(
        title=f"inner {depth}",
        content_builder=lambda: bs.Label("inner"),
        buttons=[DialogButton(text="Close", role="primary", result=None)],
        parent=parent_top,
    )

    def drive():
        top = inner.toplevel
        if top is None or not top.winfo_exists():
            return
        _nest(top, depth - 1)
        if top.winfo_exists():
            top.destroy()

    parent_top.after(200, drive)
    inner.show()


def test_a_dialog_keeps_its_grab_when_nothing_nests(app):
    """The CONTROL. Without it, the tests below can pass vacuously."""
    state = _outer(app, lambda top: top.update())

    assert state["before"] is state["outer"], "precondition: the outer dialog was modal"
    assert state["still_modal"], "the outer dialog lost its grab with nothing nested"


def test_a_nested_modal_hands_the_grab_back(app):
    """#440, at one level of nesting."""
    state = _outer(app, lambda top: _nest(top, 1))

    assert state["before"] is state["outer"], "precondition: the outer dialog was modal"
    assert state["still_modal"], (
        f"the outer dialog is no longer modal after a nested dialog closed: "
        f"grab is {state['after']}"
    )


def test_two_levels_of_nesting_hand_the_grab_back(app):
    """Restoring only one level deep would leave this leaking."""
    state = _outer(app, lambda top: _nest(top, 2))

    assert state["still_modal"], (
        f"the outer dialog is no longer modal after two nested dialogs closed: "
        f"grab is {state['after']}"
    )


def test_the_restored_grab_is_the_same_KIND_it_was(app):
    """Handing back WHO held the grab is not enough - the kind must survive.

    Every other test here asserts identity (`grab_current() is top`), which a
    downgraded grab passes: the right window holds it, just more weakly. That
    gap is why a global grab could be restored as a local one unnoticed.
    """
    state = _outer(app, lambda top: _nest(top, 1))

    assert state["kind_before"] is not None, "precondition: the outer dialog was modal"
    assert state["kind_after"] == state["kind_before"], (
        f"the grab came back as {state['kind_after']!r} but was "
        f"{state['kind_before']!r} before the nested dialog"
    )


def test_alert_from_a_dialog_button_hands_the_grab_back(app):
    """The path actually reported: a nested modal opened by a public verb.

    `bs.alert()` blocks, so the alert is dismissed by destroying whichever
    window holds the grab once it is up — that is the alert itself, since it
    just took the grab from the outer dialog.
    """
    root = app._tk_root

    def body(top):
        def dismiss(attempt=0):
            holder = root.grab_current()
            if holder is not None and holder is not top:
                holder.destroy()
                return
            if attempt < 100:
                root.after(50, lambda: dismiss(attempt + 1))

        root.after(50, dismiss)
        bs.alert("nested", parent=top)

    state = _outer(app, body)

    assert state["still_modal"], (
        f"bs.alert() from inside a dialog left it non-modal: grab is "
        f"{state['after']}"
    )


def test_no_grab_is_left_behind_once_every_dialog_has_closed(app):
    """The outermost case: `restore_grab(None)` must not re-grab anything."""
    _outer(app, lambda top: _nest(top, 1))

    assert app._tk_root.grab_current() is None, (
        f"a grab outlived every dialog: {app._tk_root.grab_current()} — the "
        f"main window is now blocked with nothing on screen"
    )


# --------------------------------------------------------------------------
# The GLOBAL grab, which cannot be driven for real in a test suite.
#
# `bs.Window(modal="app")` takes a global grab (`_runtime/toplevel.py`), and a
# real one confines the mouse and keyboard at the WINDOW SYSTEM level: a test
# that failed between taking it and releasing it would lock the machine running
# the suite out of every other application. So these drive `restore_grab`
# directly with a stub holder that records which call it received.
#
# This deliberately breaks the "test public paths" rule. The reason is above,
# and the logic being pinned is entirely ours — that the captured kind selects
# the matching restore call. What a global grab then MEANS is Tk's, and differs
# by window system; asserting on that would be testing the toolkit.
# --------------------------------------------------------------------------


class _StubHolder:
    """Records which grab call `restore_grab` made, without taking one."""

    def __init__(self, exists: bool = True, fail_global: bool = False):
        self.calls: list[str] = []
        self._exists = exists
        self._fail_global = fail_global

    def winfo_exists(self) -> bool:
        return self._exists

    def grab_set(self) -> None:
        self.calls.append("local")

    def grab_set_global(self) -> None:
        if self._fail_global:
            raise tkinter.TclError("grab failed: window not viewable")
        self.calls.append("global")


def test_a_global_grab_is_restored_as_a_global_grab():
    """The defect: `grab_set()` unconditionally narrowed an app-modal window."""
    from bootstack.dialogs._impl.dialog import restore_grab

    holder = _StubHolder()
    restore_grab((holder, "global"))

    assert holder.calls == ["global"], (
        f"a global grab was restored as {holder.calls} — an app-modal window "
        f"would come back blocking only this application"
    )


def test_a_local_grab_is_still_restored_as_a_local_grab():
    """Control: the common path must not have been widened to global."""
    from bootstack.dialogs._impl.dialog import restore_grab

    holder = _StubHolder()
    restore_grab((holder, "local"))

    assert holder.calls == ["local"]


def test_a_failed_global_restore_degrades_to_local_rather_than_to_nothing():
    """`grab set -global` can fail where a local grab cannot (X11, viewability).

    Falling back leaves the outer dialog modal within the application. Failing
    to no grab at all would be the #440 symptom this module exists to prevent.

    ⚠ What this does and does not prove, measured both ways: it FAILS if the
    fallback is removed (a failed global restore then records nothing), so it
    guards the fallback. It does NOT distinguish this fix from the code before
    it — the old version always called `grab_set()`, so it lands on the same
    `["local"]` for the wrong reason. The test above is the one that pins the
    actual change.
    """
    from bootstack.dialogs._impl.dialog import restore_grab

    holder = _StubHolder(fail_global=True)
    restore_grab((holder, "global"))

    assert holder.calls == ["local"], (
        f"a failed global restore left {holder.calls} — the outer dialog is on "
        f"screen holding no grab, which is exactly issue #440"
    )


def test_a_destroyed_holder_is_not_re_grabbed():
    """The holder can be destroyed while the inner dialog is up."""
    from bootstack.dialogs._impl.dialog import restore_grab

    holder = _StubHolder(exists=False)
    restore_grab((holder, "global"))

    assert holder.calls == []


def test_capture_grab_reports_the_kind_and_none_when_nothing_holds_it(app):
    """`capture_grab` must read the kind, and read it from the right window."""
    from bootstack.dialogs._impl.dialog import capture_grab
    import tkinter as tk

    root = app._tk_root
    assert capture_grab(root) is None, "precondition: no grab is held"

    holder = tk.Toplevel(root)
    holder.geometry("120x60+400+300")
    holder.update()
    try:
        holder.grab_set()
        captured = capture_grab(root)
        assert captured is not None, "capture_grab missed a held grab"
        assert captured[0] is holder
        assert captured[1] == "local"
    finally:
        holder.grab_release()
        holder.destroy()
