"""Why `test_bare_b_does_not_toggle_the_sidebar` fails on Linux.

`tests/widgets/public/test_appshell_shortcuts.py` synthesizes a keypress with
`state=8` to stand in for "NumLock is on", and then asserts the character lands
in the field:

    _MOD1 = 8   # Tk's Mod1 bit -- set by NumLock on Windows, by Alt on X11.
    expanded._entry_widget.event_generate("<KeyPress-b>", state=_MOD1)
    assert expanded._field.text == "b"

The comment is the whole story. Bit 3 of the event state is `Mod1`, and what
`Mod1` is bound to is a property of the X server's modifier map, not of Tk:

  * on Windows Tk reports NumLock there, which is why the test was written this
    way, and NumLock does not suppress typing; but
  * on X11 `Mod1` is conventionally **Alt**, and an Entry does not insert a
    character while Alt is held -- that is the Alt+b accelerator, not text.

So an empty field on X11 is CORRECT toolkit behavior, and the assertion encodes
a Windows-only premise. This probe measures that rather than arguing it.

Three arms, one process, same widget:

    state=0   -- plain `b`, the control. Must insert.
    state=8   -- Mod1/Alt on X11. What the failing test sends.
    state=16  -- Mod2, which is what X11 actually uses for NumLock.

If the diagnosis is right, arm 1 and arm 3 insert and arm 2 does not, and the
X modifier map shows Alt on `mod1`. If arm 1 failed to insert, the probe would
be measuring a broken harness instead of the modifier, which is why it is here.

Output is ASCII-only: this has to be readable on the Windows box too.
"""
from __future__ import annotations

import subprocess
import sys
import tkinter as tk


def x_modifier_map() -> str:
    """Return what the X server binds mod1/mod2 to, or why it is unknown."""
    try:
        out = subprocess.run(["xmodmap", "-pm"], capture_output=True,
                             text=True, timeout=10).stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "<xmodmap unavailable>"
    keep = [ln.strip() for ln in out.splitlines()
            if ln.startswith(("mod1", "mod2"))]
    return " | ".join(keep) if keep else "<no mod1/mod2 rows>"


def typed_char(state: int) -> str:
    """Send `<KeyPress-b>` with `state` to a focused Entry; return its text."""
    root = tk.Tk()
    root.geometry("300x120+60+60")
    entry = tk.Entry(root)
    entry.pack()
    root.update()
    entry.focus_force()
    root.update()

    entry.event_generate("<KeyPress-b>", state=state)
    root.update()
    text = entry.get()
    root.destroy()
    return text


def main() -> int:
    print("platform    :", sys.platform, flush=True)
    print("modifier map:", x_modifier_map(), flush=True)
    print(flush=True)

    arms = [
        (0, "plain b (CONTROL -- must insert, or this probe measures nothing)"),
        (8, "Mod1: NumLock on Windows, Alt on X11 -- what the test sends"),
        (16, "Mod2: what X11 actually uses for NumLock"),
    ]
    results = {}
    for state, label in arms:
        text = typed_char(state)
        results[state] = text
        print(f"state={state:<3} -> field={text!r:<5}  {label}", flush=True)

    print(flush=True)
    if not results[0]:
        print("INVALID     : the control did not type. Measured nothing.", flush=True)
        return 1
    if results[8] == "" and results[16] == "b":
        print("VERDICT     : Mod1 suppresses typing on this display and Mod2 does "
              "not.\n              An empty field under state=8 is correct X11 "
              "behavior, so the\n              test's assertion is a "
              "Windows-only premise.", flush=True)
    else:
        print("VERDICT     : does NOT match the Mod1-is-Alt diagnosis. "
              "Investigate.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
