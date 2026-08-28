"""#444 -- the grab contract on THIS window system. Runnable on Windows, X11 and Aqua.

capture_grab/restore_grab carry no platform branch: they read the grab KIND back
from Tk and hand back whatever Tk reported. That is only correct if Tk reports
the kind faithfully on every window system. The suite cannot check it -- a real
global grab would lock the machine running it out of every other application, so
#440 and #444 both pin the global path through a recording stub. This probe
takes the REAL grab, which is safe on an isolated display.

Arms:
  ordering  -- does a <Destroy> restore win its race with Tk's own release?
               Local grabs only. SAFE ANYWHERE.
  kind      -- does grab_status() read back "global" after grab_set_global()?
               TAKES A REAL GLOBAL GRAB. Gated on BOOTSTACK_ALLOW_GLOBAL_GRAB=1.
  restore   -- does a displaced GLOBAL grab come back as global, through the
               shipped capture_grab/restore_grab? Same gate.

ASCII only. Skips and continues rather than exiting, so one unavailable arm
never hides the others.
"""
import os
import sys
import tkinter as tk

GLOBAL_OK = os.environ.get("BOOTSTACK_ALLOW_GLOBAL_GRAB") == "1"
GATE = ("SKIPPED -- set BOOTSTACK_ALLOW_GLOBAL_GRAB=1 to run. A real global grab "
        "locks this display away from every other application, so run it under "
        "Xvfb or on a box you can afford to freeze.")


def status(w):
    try:
        return w.grab_status()
    except Exception:
        return None


def who(root):
    g = root.grab_current()
    return (str(g) if g is not None else None), (status(g) if g is not None else None)


def banner(root):
    print("platform:", sys.platform)
    print("windowingsystem:", root.tk.call("tk", "windowingsystem"))
    print("tk patchlevel:", root.tk.call("info", "patchlevel"))
    print()


def arm_ordering(root):
    print("=== ARM ordering -- does the destroy-time restore survive? ===")
    outer = tk.Toplevel(root); outer.geometry("200x100+100+100"); outer.update()
    outer.grab_set()
    print("  outer holds:      ", who(root))

    inner = tk.Toplevel(root); inner.geometry("180x80+140+140"); inner.update()
    previous = root.grab_current()
    prev_kind = status(previous) if previous is not None else None
    inner.grab_set()
    print("  inner holds:      ", who(root))

    def _on_destroy(event):
        if event.widget is not inner:
            return
        if previous is not None and previous.winfo_exists():
            previous.grab_set()

    inner.bind("<Destroy>", _on_destroy, add="+")
    inner.destroy()
    root.update()

    final = who(root)
    expected = (str(outer), prev_kind)
    print("  after the dust:   ", final)
    print("  VERDICT:", "OPTION B HOLDS" if final == expected
          else "OPTION B LOSES -- expected %s" % (expected,))
    outer.destroy()
    root.update()
    print()


def arm_kind(root):
    print("=== ARM kind -- does grab_status() read back what was taken? ===")
    if not GLOBAL_OK:
        print(" ", GATE)
        print()
        return
    w = tk.Toplevel(root); w.geometry("200x100+100+100"); w.update()

    # CONTROL: a local grab must read back "local". If this fails, the reading
    # mechanism is broken and the global result below means nothing.
    w.grab_set()
    local_kind = status(w)
    print("  control, local grab -> grab_status():", local_kind)
    w.grab_release()

    try:
        w.grab_set_global()
    except Exception as e:
        print("  grab_set_global RAISED:", type(e).__name__, e)
        w.destroy(); root.update(); print()
        return
    try:
        global_kind = status(w)
        print("  global grab -> grab_status():      ", global_kind)
    finally:
        try:
            w.grab_release()
        except Exception:
            pass

    if local_kind != "local":
        print("  VERDICT: CONTROL FAILED -- a local grab did not read back 'local'")
    elif global_kind == "global":
        print("  VERDICT: KIND IS FAITHFUL -- capture_grab records the real kind here")
    else:
        print("  VERDICT: KIND IS LOST -- grab_status() said %r after grab_set_global()."
              % (global_kind,))
        print("           capture_grab would record %r, and restore_grab would hand an"
              % (global_kind,))
        print("           app-modal window back a NARROWER grab than it had.")
    w.destroy(); root.update()
    print()


def arm_restore(root):
    print("=== ARM restore -- a displaced GLOBAL grab, through the shipped helpers ===")
    if not GLOBAL_OK:
        print(" ", GATE)
        print()
        return
    try:
        from bootstack._runtime.grab import capture_grab, restore_grab
    except Exception as e:
        print("  SKIPPED -- cannot import bootstack._runtime.grab:", type(e).__name__, e)
        print()
        return
    import bootstack
    print("  bootstack loaded from:", os.path.dirname(bootstack.__file__))

    outer = tk.Toplevel(root); outer.geometry("200x100+100+100"); outer.update()
    try:
        outer.grab_set_global()
    except Exception as e:
        print("  outer grab_set_global RAISED:", type(e).__name__, e)
        outer.destroy(); root.update(); print()
        return
    print("  outer holds:      ", who(root))

    inner = tk.Toplevel(root); inner.geometry("180x80+140+140"); inner.update()
    token = capture_grab(inner)
    print("  captured token:   ", (str(token[0]), token[1]) if token else None)
    inner.grab_set()
    print("  inner holds:      ", who(root))

    restore_grab(token)
    root.update()
    final = who(root)
    print("  after restore:    ", final)
    if final == (str(outer), "global"):
        print("  VERDICT: GLOBAL SURVIVES THE ROUND TRIP")
    else:
        print("  VERDICT: NARROWED OR LOST -- expected %s" % ((str(outer), "global"),))
    try:
        outer.grab_release()
    except Exception:
        pass
    inner.destroy(); outer.destroy(); root.update()
    print()


def main():
    arms = sys.argv[1:] or ["ordering", "kind", "restore"]
    root = tk.Tk(); root.withdraw()
    banner(root)
    table = {"ordering": arm_ordering, "kind": arm_kind, "restore": arm_restore}
    for name in arms:
        fn = table.get(name)
        if fn is None:
            print("unknown arm:", name)
            continue
        try:
            fn(root)
        except Exception as e:
            print("  ARM %s RAISED: %s: %s" % (name, type(e).__name__, e))
            print()
    root.destroy()


main()
