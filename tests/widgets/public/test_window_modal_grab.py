"""A modal `bs.Window` hands its grab back to whoever held it (#444).

`Toplevel.show()` took a modal grab and nothing ever handed it back. Tk drops a
grab when its holder is destroyed but does NOT restore the grab that holder
displaced, so a modal window opened from inside another modal left the outer one
on screen — still blocking the code that opened it, and holding no grab at all.
The user could click straight past it into the main window.

This is #440's defect on the path #440 did not cover: that fix was scoped to the
dialog classes, and `_runtime/toplevel.py` is the only other place in the tree
that takes a grab.

⚠ The invariant is the holder AND the kind, never identity alone. A global grab
restored as a local one silently narrows the window's modality, and that is what
passed every test before #440.
"""
from __future__ import annotations

import tkinter

import pytest

import bootstack as bs


def _grab(root) -> tuple[str | None, str | None]:
    """Who holds the grab, and how — the pair every assertion here uses."""
    holder = root.grab_current()
    if holder is None:
        return (None, None)
    try:
        return (str(holder), holder.grab_status())
    except (AttributeError, tkinter.TclError):
        return (str(holder), None)


def _opener(root):
    """A mapped window holding a local grab, standing in for an outer modal."""
    top = tkinter.Toplevel(root)
    top.geometry("240x120+80+80")
    top.update()
    top.grab_set()
    return top


def test_a_modal_window_hands_the_grab_back_to_its_opener(app):
    """The headline case, and the issue's own reproduction.

    Measured before the fix: `after inner closed` read `None` and
    `outer still holds grab` read `False`.
    """
    root = app.tk
    outer = _opener(root)
    try:
        assert _grab(root) == (str(outer), "local"), "precondition: outer holds the grab"

        inner = bs.Window(title="inner", modal=True, parent=outer)
        inner.show()
        root.update()
        assert root.grab_current() is not outer, "precondition: the inner window took it"

        inner.close()
        root.update()

        assert _grab(root) == (str(outer), "local"), (
            "the modal window did not hand the grab back — its opener is still on "
            "screen blocking its caller, with nothing grabbed"
        )
    finally:
        outer.destroy()
        root.update()


def test_a_modal_window_shown_without_blocking_also_hands_it_back(app):
    """The path a `block_until_closed()`-only fix would have missed.

    A modal window does not have to block: `show()` and a later `close()` is an
    ordinary sequence. The restore is bound on destroy rather than paired around
    the blocking call precisely so this path is covered too — chosen only after
    measuring that a destroy-time restore wins its race with Tk's own grab
    release (`development/probe_444_grab_restore_ordering.py`).
    """
    root = app.tk
    outer = _opener(root)
    try:
        win = bs.Window(title="non-blocking", modal=True, parent=outer)
        win.show()
        root.update()
        win.close()
        root.update()

        assert _grab(root) == (str(outer), "local")
    finally:
        outer.destroy()
        root.update()


def _close_when_modal(root, win, tries=200):
    """Close `win` once it actually holds the grab, never on a fixed delay.

    ⚠ #446's lesson, and it cost a flake once already: `show()` pumps the event
    loop while it builds and positions, so a timer scheduled with a fixed delay
    can fire on a half-built window. Poll for the barrier instead — here the
    modal grab, which is the last thing `show()` takes.
    """
    state = {"job": None, "timed_out": False}

    def poll(remaining=tries):
        holder = root.grab_current()
        if holder is not None and str(holder) == str(win._tk_toplevel):
            win.close()
            return
        if remaining <= 0:
            state["timed_out"] = True
            win.close()
            return
        state["job"] = root.after(5, poll, remaining - 1)

    state["job"] = root.after(5, poll)
    return state


def test_the_outermost_modal_window_restores_nothing(app):
    """Nothing held the grab, so nothing may be re-grabbed on the way out.

    `restore_grab(None)` is the outermost case. Getting this wrong leaves the
    main window blocked with nothing on screen, which is worse than the defect.
    """
    root = app.tk
    assert root.grab_current() is None, "precondition: nothing holds a grab"

    win = bs.Window(title="only", modal=True)
    win.show()
    root.update()
    win.close()
    root.update()

    assert root.grab_current() is None, (
        f"a grab outlived the only modal window: {root.grab_current()}"
    )


def test_a_non_modal_window_never_touches_the_grab(app):
    """The guard runs only for a modal window.

    A non-modal `bs.Window` takes no grab, so it has nothing to hand back and
    must not disturb one it never displaced.
    """
    root = app.tk
    outer = _opener(root)
    try:
        win = bs.Window(title="plain", parent=outer)
        win.show()
        root.update()
        assert _grab(root) == (str(outer), "local"), "a non-modal window took a grab"

        win.close()
        root.update()
        assert _grab(root) == (str(outer), "local")
    finally:
        outer.destroy()
        root.update()


# --------------------------------------------------------------------------
# The GLOBAL grab, which cannot be driven for real in a test suite.
#
# `bs.Window(modal="app")` takes a global grab, and a real one confines the
# mouse and keyboard at the WINDOW SYSTEM level: a test that failed between
# taking it and releasing it would lock the machine running the suite out of
# every other application. So this drives `restore_grab` directly against a stub
# that records which call it received — the same shape #440's tests use, and for
# the same reason.
#
# What is pinned here is ours: that the captured KIND selects the matching
# restore call. What a global grab then means is Tk's, and differs by window
# system; asserting on that would be testing the toolkit.
# --------------------------------------------------------------------------


class _StubHolder:
    """Records which grab call `restore_grab` made, without taking one."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def winfo_exists(self) -> bool:
        return True

    def grab_set(self) -> None:
        self.calls.append("local")

    def grab_set_global(self) -> None:
        self.calls.append("global")


@pytest.mark.parametrize("kind, expected", [("global", "global"), ("local", "local")])
def test_the_restored_grab_keeps_its_kind(kind, expected):
    """A global grab must come back global — restoring it local narrows modality.

    This is the half that identity-only assertions miss, and the reason the
    helper reads the kind back from Tk rather than assuming one.
    """
    from bootstack._runtime.grab import restore_grab

    holder = _StubHolder()
    restore_grab((holder, kind))

    assert holder.calls == [expected]


def test_the_helpers_have_one_home_and_the_dialog_path_still_reaches_them():
    """`_runtime/grab.py` is canonical; `dialog.py` imports rather than redefines.

    The move was forced by direction — `dialogs` imports `Toplevel` from
    `_runtime`, so `_runtime` reaching back would be a cycle. Two copies of a
    teardown-path helper is how they drift, so this pins that there is one.
    """
    from bootstack._runtime import grab as canonical
    from bootstack.dialogs._impl import dialog

    assert dialog.capture_grab is canonical.capture_grab
    assert dialog.restore_grab is canonical.restore_grab
def test_a_modal_window_shown_twice_still_hands_the_grab_back(app):
    """`show()` is re-callable, and the second call must not eat the token.

    `show(anchor_to=...)` re-anchors a window that is already open, so a second
    `show()` is ordinary use — and at that point the window itself holds the
    grab. Capturing again there recorded the window as its own previous holder
    and discarded the opener's, which is #444's symptom reintroduced by #444's
    fix. Measured before the fix: `after=(None, None)`.
    """
    root = app.tk
    outer = _opener(root)
    try:
        win = bs.Window(title="reshown", modal=True, parent=outer)
        win.show()
        root.update()
        win.show()
        root.update()
        win.close()
        root.update()

        assert _grab(root) == (str(outer), "local"), (
            "a second show() discarded the opener's grab token"
        )
    finally:
        outer.destroy()
        root.update()


def test_a_modal_window_blocked_on_after_being_shown_hands_the_grab_back(app):
    """The blocking path, which nothing covered — and it calls `show()` twice.

    `block_until_closed()` shows the window itself, so showing it first and then
    blocking on it drives `show()` a second time. This is the spelling a caller
    reaches for when the window is put up and only later waited on, and it is
    where the re-show defect was found.
    """
    root = app.tk
    closer = {"job": None, "timed_out": False}
    outer = _opener(root)
    try:
        win = bs.Window(title="blocked", modal=True, parent=outer)
        win.show()
        root.update()

        closer = _close_when_modal(root, win)
        win.block_until_closed()
        root.update()
        assert not closer["timed_out"], "the window never became modal"

        assert _grab(root) == (str(outer), "local")
    finally:
        if closer["job"] is not None:
            try:
                root.after_cancel(closer["job"])
            except tkinter.TclError:
                pass
        outer.destroy()
        root.update()


class _UnnameableHolder:
    """A widget whose grab holder cannot be resolved to a Python object.

    tkinter resolves the holder's path name through `_nametowidget`, which
    raises `KeyError` — not `TclError` — for a window the toolkit created on its
    own. A posted `ttk::combobox` popdown is a real one:
    `development/probe_444_review_round1.py --arm keyerror` shows
    `.!combobox.popdown` holding the grab and the lookup raising.
    """

    def grab_current(self):
        raise KeyError("popdown")


def test_capture_grab_degrades_to_none_when_the_holder_cannot_be_named():
    """A holder we cannot address reads as no holder, and must not raise.

    This runs on the SETUP path — `Toplevel.show()` — where a raise escapes into
    the application, unlike `restore_grab`, which swallows on teardown.
    """
    from bootstack._runtime.grab import capture_grab

    assert capture_grab(_UnnameableHolder()) is None
