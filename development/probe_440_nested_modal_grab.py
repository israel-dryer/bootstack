"""Probe for #440 - a nested modal drops the outer dialog's grab permanently.

A modal `Dialog` takes the grab with `grab_set()`. A second modal opened from
inside it takes the grab over, and destroying the inner one RELEASES the grab
outright instead of handing it back. The outer dialog is left on screen, still
blocking its caller inside `show()`, while the user can click straight back
into the main window and drive the app underneath it - modal in appearance
only.

Measured here as the issue describes it: `grab_current()` before the nested
dialog, and again after it has closed.

Arm 2 is the control, and it is what makes arm 1 mean anything: the SAME outer
dialog, measured across a stretch where no nested modal is opened. If the grab
were being lost for some unrelated reason - teardown, focus, the probe's own
driving - arm 2 would lose it too. It does not.

Arm 3 covers the depth the fix must not stop at: two levels of nesting, where
a naive "remember one previous grab" fix in the wrong place would still leak.

Run:  py -3.13 development/probe_440_nested_modal_grab.py
"""

from __future__ import annotations

import sys

import bootstack as bs
from bootstack.dialogs._impl.dialog import Dialog, DialogButton

failures: list[str] = []
results: dict[str, dict] = {}


def _open_nested(parent_top, depth: int) -> None:
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
        _open_nested(top, depth - 1)
        if top.winfo_exists():
            top.destroy()

    parent_top.after(300, drive)
    inner.show()


def arm(root, label: str, *, nest_depth: int):
    """Open an outer modal dialog; measure the grab across a nested stretch."""
    outer = Dialog(
        title="outer",
        content_builder=lambda: bs.Label("outer"),
        buttons=[DialogButton(text="OK", role="primary", result="ok")],
        parent=root,
    )
    state: dict = {}

    def drive():
        top = outer.toplevel
        if top is None or not top.winfo_exists():
            state["error"] = "outer dialog never came up"
            return

        state["before"] = str(top.grab_current())
        state["outer"] = str(top)

        if nest_depth:
            _open_nested(top, nest_depth)
        else:
            # The control: the same elapsed time and event pumping, no nesting.
            top.update()

        state["after"] = str(top.grab_current())
        state["still_modal"] = (top.grab_current() is top)
        top.destroy()

    root.after(400, drive)
    outer.show()

    results[label] = state
    print(f"ARM {label}")
    print(f"    outer dialog            {state.get('outer')}")
    print(f"    grab before             {state.get('before')}")
    print(f"    grab after              {state.get('after')}")
    print(f"    outer still modal       {state.get('still_modal')}")
    print()
    return bool(state.get("still_modal"))


if __name__ == "__main__":
    app = bs.App(title="probe_440")
    root = app._tk_root
    root.geometry("380x260+120+120")
    root.deiconify()
    root.update()

    control = arm(root, "2 CONTROL: no nested modal", nest_depth=0)
    one = arm(root, "1 one nested modal", nest_depth=1)
    two = arm(root, "3 two levels of nesting", nest_depth=2)

    print("=" * 66)
    if not control:
        failures.append(
            "CONTROL FAILED: the outer dialog lost its grab with no nested "
            "modal at all, so arms 1 and 3 prove nothing about nesting"
        )
    if not one:
        failures.append("one nested modal left the outer dialog non-modal (#440)")
    if not two:
        failures.append("two levels of nesting left the outer dialog non-modal")

    if failures:
        print(f"REPRODUCED / FAIL ({len(failures)})")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print("PASS - the outer dialog keeps its grab across nested modals,")
    print("       and the control shows the measurement can tell the difference.")
