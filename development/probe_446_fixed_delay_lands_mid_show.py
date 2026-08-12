"""Flake A of #446: a fixed-delay timer can land INSIDE `Dialog.show()`.

The failure is `TclError: bad window path name` raised by `deiconify()` at
`dialog.py:930`, reached from `show()` -> `_position_dialog()`. The dialog's own
toplevel is gone between being created and being positioned.

`show()` does this, in order:

    521  _create_toplevel()     <- the toplevel exists from here
    522  _build_footer()
    523  _build_content()       <- runs the caller's content_builder
    534  _position_dialog()     <- deiconify() lives in here
    549  grab_set()             <- the modal grab goes up LAST

Building and positioning pump the event loop, so anything queued with `after`
can run between 521 and 534. `test_dialog_nested_modality.py::_outer` drives on
`after(300, drive)` -- a FIXED DELAY -- and `drive` destroys the toplevel. When
that 300ms lands before line 534, `show()` carries on and deiconifies a window
that no longer exists.

The other two dialog files do not have this bug because they poll for the modal
GRAB, which only goes up at 549, i.e. after positioning is finished. That is the
difference, and it is why only this file carries flake A.

At 1 in 12 the flake cannot be studied by re-running, so no arm here waits for
it. Arm 1 CREATES the condition by making the build slow enough that a fixed
delay is guaranteed to land inside it; arm 2 is the quiet-process control that
shows why the suite looks clean; arm 3 is the same forced condition with the
grab barrier in place.

Run:  py -3.12 development/probe_446_fixed_delay_lands_mid_show.py

Output is ASCII only (this box's console is cp1252).
"""
from __future__ import annotations

import time
import tkinter
import traceback

import bootstack as bs
from bootstack.dialogs import Dialog, DialogButton

RUNS = 10
DELAY_MS = 300
SLOW_BUILD_MS = 600


def _slow_content(root, millis: int):
    """A content_builder that keeps the event loop TURNING while it builds.

    Pumping is the point: a build that merely blocked would starve the timer
    rather than racing it, and the race is what is being reproduced. Real
    content does the same thing -- the geometry manager and any nested widget
    construction both turn the loop.
    """

    def build():
        bs.Label("slow body")
        deadline = time.monotonic() + millis / 1000.0
        while time.monotonic() < deadline:
            root.update()

    return build


def _run_once(root, *, slow: bool, barrier: str) -> str | None:
    """Open a dialog, drive it, return the error text if `show()` raised.

    `barrier` selects how the driver decides the dialog is ready:
      'delay' -- fixed `after(DELAY_MS)`, what the flaky test does today
      'grab'  -- poll until the dialog holds the modal grab, the fix
    """
    dialog = Dialog(
        title="outer",
        content_builder=(
            _slow_content(root, SLOW_BUILD_MS) if slow else (lambda: bs.Label("body"))
        ),
        buttons=[DialogButton(text="OK", role="primary", result="ok")],
        parent=root,
    )
    pending: list[str] = []

    def drive():
        top = dialog.toplevel
        if top is not None and top.winfo_exists():
            top.destroy()

    def poll(attempt=0):
        top = dialog.toplevel
        ready = (
            top is not None
            and top.winfo_exists()
            and top.grab_current() is top
        )
        if ready:
            drive()
        elif attempt < 200:
            pending.append(root.after(50, lambda: poll(attempt + 1)))

    guard = root.after(8000, drive)
    pending.append(guard)
    try:
        if barrier == "delay":
            pending.append(root.after(DELAY_MS, drive))
        else:
            pending.append(root.after(50, poll))
        try:
            dialog.show()
        except tkinter.TclError as exc:
            return f"{type(exc).__name__}: {exc}"
        return None
    finally:
        for job in pending:
            try:
                root.after_cancel(job)
            except tkinter.TclError:
                pass
        top = dialog.toplevel
        if top is not None and top.winfo_exists():
            top.destroy()


def _arm(root, label, *, slow: bool, barrier: str, expect: str) -> tuple[int, int]:
    print(f"\n--- {label}")
    failures = 0
    first = None
    for _ in range(RUNS):
        err = _run_once(root, slow=slow, barrier=barrier)
        if err is not None:
            failures += 1
            if first is None:
                first = err
    print(f"    failures: {failures}/{RUNS}   (expected: {expect})")
    if first is not None:
        print(f"    first error: {first}")
    return failures, RUNS


def main() -> int:
    app = bs.App(title="probe 446 flake A")
    root = app._tk_root
    root.geometry("360x200+200+200")
    root.update()

    print("Flake A -- a fixed-delay driver racing Dialog.show()")
    print(f"delay={DELAY_MS}ms  forced build={SLOW_BUILD_MS}ms  runs per arm={RUNS}")

    a_fail, _ = _arm(
        root,
        "ARM 1  MECHANISM: fixed delay + a build slow enough to still be running",
        slow=True, barrier="delay", expect="10/10 -- this IS the flake",
    )
    b_fail, _ = _arm(
        root,
        "ARM 2  CONTROL: fixed delay, ordinary content (a quiet process)",
        slow=False, barrier="delay", expect="0/10 -- why the suite looks green",
    )
    c_fail, _ = _arm(
        root,
        "ARM 3  FIX: poll for the modal grab, same forced-slow build",
        slow=True, barrier="grab", expect="0/10",
    )

    print("\n" + "=" * 72)
    print("READING")
    print("=" * 72)
    print(
        "Arm 1 vs arm 2 is the whole finding: the SAME driver code is a"
        "\nreliable crash or a clean pass depending only on how long the build"
        "\ntakes. That is what a 1-in-12 rate on a loaded shared root looks"
        "\nlike, and it is why re-running the suite says nothing."
    )
    print(
        "\nArm 3 holds the build slow and the crash still goes to zero, because"
        "\nthe modal grab is set AFTER positioning -- so a driver waiting on it"
        "\ncannot act on a half-built dialog no matter how slow the build is."
    )
    ok = a_fail == RUNS and b_fail == 0 and c_fail == 0
    print(f"\nRESULT: {'as expected' if ok else 'NOT the expected pattern - read the arms'}")
    root.destroy()
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except tkinter.TclError as exc:
        print(f"SKIP: no usable display ({exc})")
        raise SystemExit(0)
