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
            body(top)
            state["after"] = top.grab_current()
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
