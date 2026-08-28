"""#444 round 2 -- the CROSS-PATH nesting the tests never drive.

`test_window_modal_grab.py` uses a raw `tkinter.Toplevel` as the opener. The
CHANGELOG's headline scenario is different: a modal `bs.Window` opened from a
DIALOG button ("an 'Advanced...' button on a dialog"). Dialog and window take
their grabs through two separate code paths -- `Dialog._show_modal` grabs
directly, `Toplevel.show()` grabs through the new capture/restore -- and nothing
exercises them against each other.

Arms (each skips and continues, so one failure never hides the others):

  dialog_window   modal Dialog -> modal bs.Window -> close. Does the DIALOG get
                  its grab back, holder AND kind?
  control         the same stretch with NOTHING nested. Proves the measurement
                  can report a dialog that is still modal, so a PASS on the arm
                  above is not the instrument being blind.
  window_dialog   modal bs.Window -> Dialog -> close. The reverse direction.
  three_deep      three nested modal bs.Windows, unwound one at a time.

Run:  py -3.12 development/probe_444_review_round2.py [arm ...]
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import bootstack as bs
from bootstack.dialogs import Dialog, DialogButton


def _pair(top):
    """(holder path, kind) -- the invariant, never identity alone."""
    holder = top.grab_current()
    if holder is None:
        return (None, None)
    try:
        return (str(holder), holder.grab_status())
    except Exception:
        return (str(holder), None)


def _poll_until(root, predicate, tries=200, interval=10):
    """Poll for a barrier rather than firing on a fixed delay (#446)."""
    for _ in range(tries):
        root.update()
        if predicate():
            return True
        root.after(interval)
    return False


def _drive_dialog(root, body, label):
    """Show a modal Dialog; run body(top) once it holds the grab; report."""
    dialog = Dialog(
        title="outer",
        content_builder=lambda: bs.Label("outer"),
        buttons=[DialogButton(text="OK", role="primary", result="ok")],
        parent=root,
    )
    state = {}
    pending = []

    def run(attempt=0):
        top = dialog.toplevel
        if top is None or not top.winfo_exists() or top.grab_current() is not top:
            if attempt < 150:
                pending.append(root.after(50, lambda: run(attempt + 1)))
            else:
                state["error"] = "the outer dialog never took the modal grab"
            return
        try:
            state["before"] = _pair(top)
            body(root, top, state)
            state["after"] = _pair(top)
            state["outer"] = str(top)
        finally:
            if top.winfo_exists():
                top.destroy()

    pending.append(root.after(50, run))
    try:
        dialog.show(modal=True)
    finally:
        for job in pending:
            try:
                root.after_cancel(job)
            except Exception:
                pass
    if "error" in state:
        print("  %-14s ERROR %s" % (label, state["error"]))
        return None
    print("  %-14s before=%-28s after=%-28s  %s" % (
        label, state["before"], state["after"],
        "OK" if state["after"] == state["before"] else "*** LOST ***",
    ))
    return state


def arm_dialog_window(root):
    print("ARM dialog_window -- modal Dialog nests a modal bs.Window")

    def body(root, top, state):
        win = bs.Window(title="inner", modal=True, parent=top)
        win.show()
        ok = _poll_until(root, lambda: top.grab_current() is win._tk_toplevel)
        state["inner_grabbed"] = ok
        print("  inner window took the grab: %s" % ok)
        win.close()
        root.update()

    _drive_dialog(root, body, "dialog_window")


def arm_control(root):
    print("ARM control -- the same stretch with NOTHING nested")

    def body(root, top, state):
        root.update()

    _drive_dialog(root, body, "control")


def arm_window_dialog(root):
    print("ARM window_dialog -- modal bs.Window nests a Dialog")
    win = bs.Window(title="outer-window", modal=True, parent=root)
    win.show()
    root.update()
    top = win._tk_toplevel
    before = _pair(top)
    print("  outer window holds: %s" % (before,))

    dialog = Dialog(
        title="nested",
        content_builder=lambda: bs.Label("nested"),
        buttons=[DialogButton(text="OK", role="primary", result="ok")],
        parent=top,
    )
    pending = []

    def close_it(attempt=0):
        dtop = dialog.toplevel
        if dtop is None or not dtop.winfo_exists() or dtop.grab_current() is not dtop:
            if attempt < 150:
                pending.append(root.after(50, lambda: close_it(attempt + 1)))
            return
        dtop.destroy()

    pending.append(root.after(50, close_it))
    try:
        dialog.show(modal=True)
    finally:
        for job in pending:
            try:
                root.after_cancel(job)
            except Exception:
                pass
    root.update()
    after = _pair(top)
    print("  %-14s before=%-28s after=%-28s  %s" % (
        "window_dialog", before, after,
        "OK" if after == before else "*** LOST ***",
    ))
    win.close()
    root.update()


def arm_three_deep(root):
    print("ARM three_deep -- three nested modal bs.Windows, unwound one at a time")
    wins = []
    expected = []
    parent = root
    for i in range(3):
        top_before = _pair(root)
        w = bs.Window(title="w%d" % i, modal=True, parent=parent)
        w.show()
        root.update()
        wins.append(w)
        expected.append(top_before)
        parent = w._tk_toplevel
    for i in reversed(range(3)):
        wins[i].close()
        root.update()
        got = _pair(root)
        print("  depth %d  expected=%-28s after=%-28s  %s" % (
            i, expected[i], got, "OK" if got == expected[i] else "*** LOST ***",
        ))


ARMS = {
    "dialog_window": arm_dialog_window,
    "control": arm_control,
    "window_dialog": arm_window_dialog,
    "three_deep": arm_three_deep,
}

if __name__ == "__main__":
    import bootstack
    print("bootstack loaded from: %s" % os.path.dirname(bootstack.__file__))
    wanted = sys.argv[1:] or list(ARMS)
    app = bs.App(title="probe444r2")
    root = app._tk_root
    root.geometry("360x200+60+60")
    root.update()
    for name in wanted:
        fn = ARMS.get(name)
        if fn is None:
            print("SKIP unknown arm %s" % name)
            continue
        try:
            fn(root)
        except Exception as exc:
            print("  ARM %s RAISED: %r" % (name, exc))
        print()
    root.destroy()
