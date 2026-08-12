"""Positive control for the #447 arm-3 measurement: is a window manager RUNNING?

Arm 3 of the #447 investigation (Xvfb WITH a window manager) is only evidence if
the window manager was actually there. An `openbox &` that dies on startup is
indistinguishable, from the test output alone, from a window manager that ran and
changed nothing -- which is exactly the trap `REVIEW-PROTOCOL.md` and the #447
handoff warn about ("a control that does not reach the code path under test is
indistinguishable from a fix that works").

This probe reports, for the CURRENT $DISPLAY:

  * whether an EWMH-compliant window manager owns the root window
    (`_NET_SUPPORTING_WM_CHECK` -> `_NET_WM_NAME`), and
  * a Tk-level consequence of one: whether a mapped Toplevel gets REPARENTED
    into a frame. A window manager reparents; a bare X server does not.

The reparent check is the load-bearing half. It needs no external tool, it is
what Tk itself sees, and it is true of every window manager rather than only the
EWMH-advertising ones.

Run it under each arm -- it is designed to report a DIFFERENT answer under each,
which is what makes it a control rather than a smoke test:

    python probe_447_wm_present.py                                  # WSLg
    xvfb-run -a python probe_447_wm_present.py                       # no WM
    xvfb-run -a sh -c 'xfwm4 --daemon & sleep 2; python probe_447_wm_present.py'

Output is ASCII-only: this has to be readable on the Windows box too.
"""
from __future__ import annotations

import os
import subprocess
import tkinter as tk


def ewmh_wm_name() -> str:
    """Return the EWMH window-manager name, or a reason it could not be read."""
    try:
        root_props = subprocess.run(
            ["xprop", "-root", "_NET_SUPPORTING_WM_CHECK"],
            capture_output=True, text=True, timeout=10,
        )
    except FileNotFoundError:
        return "<xprop not installed>"
    except subprocess.TimeoutExpired:
        return "<xprop timed out>"

    out = root_props.stdout.strip()
    if "window id" not in out:
        return "<none: no _NET_SUPPORTING_WM_CHECK on the root window>"

    win = out.rsplit("#", 1)[-1].strip()
    named = subprocess.run(
        ["xprop", "-id", win, "_NET_WM_NAME"],
        capture_output=True, text=True, timeout=10,
    ).stdout.strip()
    return named or "<check window present but unnamed>"


def toplevel_is_reparented() -> tuple[bool, str]:
    """Map a Toplevel and report whether something reparented it into a frame.

    A window manager wraps a top-level window in a decoration frame, so the
    window's X parent stops being the root window. Without a window manager the
    parent stays the root. Tk exposes this as ``wm frame`` (the outermost frame
    id) differing from ``winfo id`` (the window's own id).
    """
    root = tk.Tk()
    root.geometry("200x120+50+50")
    top = tk.Toplevel(root)
    top.geometry("200x120+80+80")
    top.deiconify()
    # NOT wait_visibility(): with no window manager on the display, nothing ever
    # delivers the VisibilityNotify it blocks on, so the probe would hang on the
    # exact arm it exists to measure. Pump the queue a bounded number of times
    # instead -- reparenting, when it happens at all, happens on the map.
    for _ in range(20):
        top.update()

    own_id = top.winfo_id()
    frame_id = int(root.tk.call("wm", "frame", top._w), 0)
    root.destroy()
    return frame_id != own_id, f"winfo id={own_id:#x} wm frame={frame_id:#x}"


def main() -> int:
    print("display     :", os.environ.get("DISPLAY", "<unset>"), flush=True)
    print("ewmh wm     :", ewmh_wm_name(), flush=True)

    reparented, detail = toplevel_is_reparented()
    print("reparented  :", "YES" if reparented else "NO", "(" + detail + ")", flush=True)
    print()
    print("VERDICT     :", "A window manager IS managing this display."
          if reparented else "NO window manager is managing this display.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
