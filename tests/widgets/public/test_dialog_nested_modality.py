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

⚠ The `state["before"] is state["outer"]` preconditions below are now
GUARANTEED by `_outer`'s barrier, which waits for that grab before it measures
anything (see its docstring, and issue #446). They are kept because they state
what the measurement rests on, but they can no longer fail — the barrier
timing out is what reports a dialog that never became modal, and it does so by
name rather than as a confusing assertion one line later.
"""
from __future__ import annotations

import tkinter

import pytest

import bootstack as bs
from bootstack.dialogs import Dialog, DialogButton

pytestmark = pytest.mark.gui

# Where `_nest` reports a barrier it never cleared.
#
# ⚠ Module-level because `_nest` is reached through `_outer`'s `body`, which the
# tests pass as a bare `lambda top: ...` — there is no return path from inside
# it back to the test. `_outer` clears this on entry and copies it into the
# state it returns, so a nested dialog that never became modal fails the test
# that nested it instead of silently measuring nothing.
_NEST_PROBLEMS: list[str] = []


def _outer(app, body):
    """A modal dialog that runs `body(top)` once it is up, then closes.

    ⚠ POLLS FOR THE MODAL GRAB. It must not drive on a fixed delay, and that
    cost a flaky test (issue #446, 1 failure in 12 runs of the shared leg).

    `show()` creates the toplevel, then builds the footer and the content, then
    positions the window, and only then calls `grab_set()`. Building and
    positioning both pump the event loop, so a timer scheduled with a fixed
    delay can fire while `show()` is still partway through — and this driver
    DESTROYS the toplevel. `show()` then carried on into `_position_dialog` and
    deiconified a window that no longer existed:

        dialog.py:930: in _position_dialog
            self._toplevel.deiconify()
        E   TclError: bad window path name ".!toplevel7"

    The grab is the barrier because it is the LAST thing `show()` does before
    it waits, so a driver holding for it cannot act on a half-built dialog.
    Same hazard and same remedy as `_drive` in `test_dialog_press_contract.py`;
    this helper was the one that had not adopted it.

    Reproduced deterministically in `development/probe_446_fixed_delay_lands_mid_show.py`
    by forcing the build to outlast the delay: **10/10 with the fixed delay,
    0/10 with this barrier**, against 0/10 for the fixed delay in a quiet
    process — which is exactly why a green suite run did not show it.
    """
    root = app._tk_root
    dialog = Dialog(
        title="outer",
        content_builder=lambda: bs.Label("outer"),
        buttons=[DialogButton(text="OK", role="primary", result="ok")],
        parent=root,
    )
    state: dict = {}
    pending: list[str] = []
    _NEST_PROBLEMS.clear()

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

    def run(attempt=0):
        top = dialog.toplevel
        if top is None or not top.winfo_exists() or top.grab_current() is not top:
            # ⚠ 150 attempts = 7550ms, deliberately BELOW `force_close`'s 10s.
            # At 200 the budget ran to 10050ms, so `force_close` always won the
            # race: it destroyed the toplevel, `show()` returned, the `finally`
            # below cancelled the remaining retries, and this branch never got
            # to run. `state` was then empty with no `"error"` key, so the
            # assert at the bottom PASSED and every test reading `state` died
            # with a bare `KeyError` instead.
            if attempt < 150:
                pending.append(root.after(50, lambda: run(attempt + 1)))
            else:
                state["error"] = "the outer dialog never took the modal grab"
            return
        drive()

    def force_close():
        top = dialog.toplevel
        if top is not None and top.winfo_exists():
            # Reaching here at all means the measurement never completed —
            # either the grab never arrived, or `body` was still running. Both
            # invalidate the result, so say so rather than closing quietly.
            state.setdefault(
                "error",
                "the outer dialog was still up after 10s - the barrier never "
                "cleared, or the body driving it never finished",
            )
            top.destroy()

    pending.append(root.after(50, run))
    pending.append(root.after(10000, force_close))
    try:
        dialog.show()
    finally:
        # The root outlives this test; a timer left queued fires during a later
        # one and would destroy an unrelated Toplevel.
        for job in pending:
            root.after_cancel(job)

    state["nest_problems"] = list(_NEST_PROBLEMS)

    assert "error" not in state, state["error"]
    assert not state["nest_problems"], (
        f"a nested dialog never became modal, so nothing was nested and this "
        f"measurement proves nothing: {state['nest_problems']}"
    )
    return state


def _nest(parent_top, depth: int) -> None:
    """Open `depth` modal dialogs inside one another, closing from the inside.

    Polls for the inner dialog's own grab, for the reason in `_outer` — a fixed
    delay here races `inner.show()` in exactly the same way.

    ⚠ Schedules on the ROOT, not on `parent_top`. An `after` job is a command
    owned by the widget it is scheduled on, so a job left pending on a dialog
    that is then destroyed fires as an orphan with nothing Python can see.

    ⚠ Reports a barrier it never cleared into `_NEST_PROBLEMS`, which `_outer`
    asserts on. Giving up quietly here means nothing was ever nested, so the
    outer grab was never displaced and every test that nests passes measuring
    nothing — the exact vacuity the control test at the top of this module
    exists to catch, arriving by a different route.
    """
    if depth == 0:
        return
    root = parent_top.nametowidget(".")
    inner = Dialog(
        title=f"inner {depth}",
        content_builder=lambda: bs.Label("inner"),
        buttons=[DialogButton(text="Close", role="primary", result=None)],
        parent=parent_top,
    )
    pending: list[str] = []

    def drive():
        top = inner.toplevel
        if top is None or not top.winfo_exists():
            return
        _nest(top, depth - 1)
        if top.winfo_exists():
            top.destroy()

    def run(attempt=0):
        top = inner.toplevel
        if top is None or not top.winfo_exists() or top.grab_current() is not top:
            # ⚠ 120 attempts = 6050ms, below `force_close`'s 8s for the reason
            # given in `_outer.run` — a budget that outlasts the fallback can
            # never report anything.
            if attempt < 120:
                pending.append(root.after(50, lambda: run(attempt + 1)))
            else:
                _NEST_PROBLEMS.append(
                    f"the inner dialog at depth {depth} never took the modal grab"
                )
            return
        drive()

    def force_close():
        top = inner.toplevel
        if top is not None and top.winfo_exists():
            _NEST_PROBLEMS.append(
                f"the inner dialog at depth {depth} was still up after 8s"
            )
            top.destroy()

    pending.append(root.after(50, run))
    pending.append(root.after(8000, force_close))
    try:
        inner.show()
    finally:
        for job in pending:
            root.after_cancel(job)


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
        # ⚠ This is the one driver here that destroys a window it LOOKS UP
        # rather than one it was handed, so a job of its left queued would
        # destroy whatever holds the grab in a LATER test. Every handle is
        # cancelled in the `finally` for that reason, not for tidiness.
        pending: list[str] = []

        def dismiss(attempt=0):
            holder = root.grab_current()
            if holder is not None and holder is not top:
                holder.destroy()
                return
            if attempt < 100:
                pending.append(root.after(50, lambda: dismiss(attempt + 1)))

        pending.append(root.after(50, dismiss))
        try:
            bs.alert("nested", parent=top)
        finally:
            for job in pending:
                root.after_cancel(job)

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
