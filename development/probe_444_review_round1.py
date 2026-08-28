"""Round 1 review probe for #444 (fix/modal-window-grab-444).

Two findings, each with the control that makes its reading mean something.

  --arm reshow   Finding 1. A modal `bs.Window` restores the displaced grab only
                 when `show()` was called EXACTLY ONCE. `show()` stores the
                 captured token unconditionally, while `_bind_grab_restore`
                 guards itself against re-entry -- so a second `show()` finds the
                 window already holding the grab and captures ITSELF, discarding
                 the opener. CONTROL: the two single-show arms restore, so a
                 `*** LOST ***` row is not the probe failing to see a restore.

  --arm keyerror Finding 2. `capture_grab` leaves `widget.grab_current()`
                 unwrapped. tkinter resolves the holder name through
                 `_nametowidget`, which raises KeyError -- not TclError -- for a
                 window Tcl created without tkinter. A posted ttk combobox
                 popdown is exactly that. BOUNDARY: the mechanism reproduces;
                 no live route to it was found inside src/ (see the review).

Run:  py -3.12 development/probe_444_review_round1.py --arm reshow
      py -3.12 development/probe_444_review_round1.py --arm keyerror
"""
import sys
import tkinter
from tkinter import ttk


def _snap(root):
    """Holder AND kind -- the pair every #440/#444 assertion uses."""
    holder = root.grab_current()
    if holder is None:
        return (None, None)
    try:
        return (str(holder), holder.grab_status())
    except Exception:
        return (str(holder), None)


def _opener(root):
    """A mapped window holding a local grab, standing in for an outer modal."""
    top = tkinter.Toplevel(root)
    top.geometry("240x120+80+80")
    top.update()
    top.grab_set()
    return top


# --------------------------------------------------------------------- reshow

def arm_reshow():
    import bootstack as bs

    results = []

    def run(app, name, drive):
        root = app.tk
        outer = _opener(root)
        want = _snap(root)
        win = bs.Window(title=name.strip(), modal=True, parent=outer)
        drive(root, win)
        root.update()
        got = _snap(root)
        try:
            outer.destroy()
        except Exception:
            pass
        root.update()
        results.append((name, want, got, got == want))

    def d_block_only(root, win):
        root.after(250, win.close)
        win.block_until_closed()

    def d_show_close(root, win):
        win.show()
        root.update()
        win.close()

    def d_show_show_close(root, win):
        win.show()
        root.update()
        win.show()
        root.update()
        win.close()

    def d_show_block(root, win):
        win.show()
        root.update()
        root.after(250, win.close)
        win.block_until_closed()

    def d_show_anchor(root, win):
        win.show()
        root.update()
        win.show(anchor_to="cursor")
        root.update()
        win.close()

    app = bs.App(title="probe444")
    app.tk.geometry("400x200+400+400")
    app.tk.update()

    cases = [
        ("block_until_closed() only ", d_block_only),      # CONTROL: one show()
        ("show() -> close()         ", d_show_close),      # CONTROL: one show()
        ("show() -> show() -> close ", d_show_show_close),
        ("show() -> block_until_cl. ", d_show_block),
        ("show() -> show(anchor_to) ", d_show_anchor),
    ]
    for name, drive in cases:
        try:
            run(app, name, drive)
        except Exception as exc:
            results.append((name, "EXC", repr(exc), False))

    print()
    print("ARM reshow -- does the opener get its grab back?")
    print()
    for name, want, got, ok in results:
        verdict = "RESTORED" if ok else "*** LOST ***"
        print(f"  {name} expected={str(want):32} after={str(got):32} {verdict}")
    print()
    lost = [n for n, _, _, ok in results if not ok]
    kept = [n for n, _, _, ok in results if ok]
    print(f"  restored: {len(kept)}   lost: {len(lost)}")
    print("  READING: the two CONTROL rows restore, so a lost row is the fix")
    print("  not reaching that path -- not the probe failing to observe one.")
    app.tk.destroy()


# ------------------------------------------------------------------- keyerror

def arm_keyerror():
    from bootstack._runtime.grab import capture_grab

    root = tkinter.Tk()
    root.geometry("300x160+300+300")
    combo = ttk.Combobox(root, values=["a", "b", "c"])
    combo.pack(pady=20)
    root.update()

    print()
    print("ARM keyerror -- can a Tcl-created window hold the grab?")
    print()

    # CONTROL: nothing posted, nothing holds the grab, capture_grab returns None.
    print(f"  control (nothing posted): capture_grab -> {capture_grab(root)!r}")

    try:
        root.tk.call("ttk::combobox::Post", combo._w)
    except tkinter.TclError as exc:
        print(f"  could not post the popdown: {exc}")
    root.update()

    name = root.tk.call("grab", "current", root._w)
    print(f"  raw Tcl grab holder:      {name or '<none>'}")

    if name:
        try:
            root.nametowidget(name)
            print("  resolves through tkinter: yes -- NOT a route")
        except KeyError as exc:
            print(f"  _nametowidget raises:     KeyError {exc}")
        try:
            print(f"  capture_grab ->           {capture_grab(root)!r}")
        except Exception as exc:
            print(f"  capture_grab RAISED:      {type(exc).__name__} {exc}")
            print()
            print("  READING: grab_current() is unwrapped in capture_grab, and")
            print("  KeyError is not in the except clause guarding grab_status().")
            print("  This escapes Toplevel.show(), which is a SETUP path -- unlike")
            print("  restore_grab, which swallows on teardown.")
    else:
        print("  the popdown holds no grab -- not a route on this platform")

    try:
        root.tk.call("ttk::combobox::Unpost", combo._w)
    except Exception:
        pass
    root.destroy()


ARMS = {"reshow": arm_reshow, "keyerror": arm_keyerror}


def main():
    arm = "reshow"
    if "--arm" in sys.argv:
        arm = sys.argv[sys.argv.index("--arm") + 1]
    if arm not in ARMS:
        print(f"unknown arm {arm!r}; choose from {sorted(ARMS)}")
        raise SystemExit(2)
    ARMS[arm]()


main()
