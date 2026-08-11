"""Why `test_enter_on_a_focused_button_does_not_also_press_the_default` is flaky.

Measured 2026-08-11 on the Windows box. The test passes alone (12/12) and
passed a clean shared-root leg (962 passed), but a `tests/run_gui.py` run at
`e0092336` failed it at its own precondition:

    assert top.focus_lastfor() is apply_widget, "precondition: Apply holds focus"
    E   assert <Toplevel .!toplevel7> is <Button .!toplevel7.!frame.!button2>

`focus_lastfor()` returned the TOPLEVEL, which is what Tk reports when no focus
has ever been set inside that window -- i.e. the `focus_set()` on the line above
did nothing at all.

The suspected mechanism is Tk's own: `TkSetFocusWin` walks from the widget up to
its toplevel, and if ANY window on that path is unmapped it returns without
setting anything. No error, no return value -- a silent no-op. So a footer
button whose parent frame has not been mapped yet cannot take focus, and the
window can still report `winfo_ismapped() == 1` at the toplevel while that is
true of a child.

Arms:

  1. control    -- force the mechanism: focus_set on a button inside a frame
                   that has not been mapped yet. Proves the silent no-op is
                   real on this Tk, and that `focus_lastfor` is how it shows.
  2. repeat     -- drive the real dialog N times through the same grab-poll the
                   test uses, and count how often the focus request fails to
                   take. Records the mapped/viewable state each time, so a
                   failure carries its own diagnosis.

Run: py -3.13 development/probe_437_focus_flake.py [iterations]
ASCII only -- this box's console is cp1252.
"""
from __future__ import annotations

import sys
import tkinter as tk

import bootstack as bs
from bootstack.dialogs import Dialog, DialogButton


def arm_1_control(root):
    """A button under an unmapped parent cannot take focus, and says nothing."""
    top = tk.Toplevel(root)
    top.geometry("200x100+100+100")

    frame = tk.Frame(top)
    button = tk.Button(frame, text="Apply")
    button.pack()
    # frame is deliberately NOT packed, so button is unmapped while top is not.
    top.update()

    before = top.focus_lastfor()
    button.focus_set()
    after = top.focus_lastfor()

    print("arm 1 (control) -- focus_set on a button under an unmapped parent")
    print(f"  top mapped      = {bool(top.winfo_ismapped())}")
    print(f"  button mapped   = {bool(button.winfo_ismapped())}")
    print(f"  lastfor before  = {before}")
    print(f"  lastfor after   = {after}")
    took = str(after) == str(button)
    print(f"  focus took      = {took}   <- expected False: the silent no-op")

    # And the same button once its parent IS mapped, so the arm cannot be read
    # as "focus_set never works here".
    frame.pack()
    top.update()
    button.focus_set()
    took_mapped = str(top.focus_lastfor()) == str(button)
    print(f"  after mapping the parent, focus took = {took_mapped}   <- expected True")

    top.destroy()
    return (not took) and took_mapped


def arm_2_repeat(app, iterations):
    """Drive the real dialog repeatedly; count focus requests that do not take."""
    root = app._tk_root
    results = []

    for i in range(iterations):
        calls = []
        dialog = Dialog(
            parent=root,
            title="Keypad",
            content_builder=lambda: bs.Label("body"),
            buttons=[
                DialogButton(text="Cancel", role="cancel", result=None),
                DialogButton(
                    text="Apply", role="secondary", result="apply",
                    command=lambda dlg: (calls.append("apply"), False)[1],
                ),
                DialogButton(
                    text="OK", role="primary", result="ok", default=True,
                    command=lambda dlg: calls.append("ok"),
                ),
            ],
        )

        record = {}
        pending = []

        def run(attempt=0, dialog=dialog, record=record, pending=pending):
            top = dialog.toplevel
            if top is None or not top.winfo_exists() or top.grab_current() is not top:
                if attempt < 200:
                    pending.append(root.after(50, lambda: run(attempt + 1)))
                return

            # Same positional pairing the test's `_footer_widget` uses.
            apply_widget = None
            specs = list(reversed(dialog._buttons))
            widgets = list(dialog._footer.winfo_children())
            if len(specs) == len(widgets):
                for spec, widget in zip(specs, widgets):
                    if spec.text == "Apply":
                        apply_widget = widget
            if apply_widget is None:
                record["error"] = "no Apply button found"
                top.destroy()
                return

            record["top_mapped"] = bool(top.winfo_ismapped())
            record["btn_mapped"] = bool(apply_widget.winfo_ismapped())
            record["btn_viewable"] = bool(apply_widget.winfo_viewable())
            record["parent_mapped"] = bool(apply_widget.master.winfo_ismapped())
            apply_widget.focus_set()
            record["took"] = top.focus_lastfor() is apply_widget
            top.destroy()

        pending.append(root.after(20, run))
        try:
            dialog.show()
        finally:
            for job in pending:
                try:
                    root.after_cancel(job)
                except tk.TclError:
                    pass
        results.append(record)

    failures = [r for r in results if not r.get("took")]
    print()
    print(f"arm 2 (repeat) -- {iterations} real dialogs through the grab poll")
    print(f"  focus requests that did NOT take: {len(failures)} / {len(results)}")
    for r in failures[:5]:
        print(f"    {r}")
    if not failures:
        print("    (none this run -- the flake did not reproduce here)")
        sample = results[0] if results else {}
        print(f"    sample of a passing iteration: {sample}")
    return failures


def arm_3_under_load(app, iterations):
    """Reproduce the unmapped-at-grab state on purpose, and show the barrier fixes it.

    Arm 2 cannot reproduce it in a quiet process and a full leg reproduces it
    once in five, which is too weak to verify a fix against. So this arm
    CREATES the condition rather than waiting for it: a pile of freshly packed
    widgets leaves the geometry manager with idle work outstanding, and the
    modal grab is reached while the footer's own buttons are still waiting
    their turn.

    Two readings per iteration, which is what makes it a control rather than a
    demonstration:

      at_grab   -- the old barrier: grab is up. Is the button mapped, and does
                   focus_set take?
      at_mapped -- the new barrier: grab is up AND the footer is mapped. Same
                   two questions.
    """
    root = app._tk_root
    at_grab_unmapped = 0
    at_grab_focus_missed = 0
    at_mapped_unmapped = 0
    at_mapped_focus_missed = 0

    for i in range(iterations):
        # Queue geometry work: packed but never updated, so the idle handler is
        # still outstanding when the dialog goes up.
        ballast = tk.Frame(root)
        ballast.pack()
        for n in range(300):
            tk.Label(ballast, text=f"ballast {n}").pack()

        dialog = Dialog(
            parent=root,
            title="Load",
            content_builder=lambda: bs.Label("body"),
            buttons=[
                DialogButton(text="Cancel", role="cancel", result=None),
                DialogButton(text="Apply", role="secondary", result="apply",
                             command=lambda dlg: False),
                DialogButton(text="OK", role="primary", result="ok", default=True),
            ],
        )

        record = {}
        pending = []

        def apply_button(dialog=dialog):
            specs = list(reversed(dialog._buttons))
            widgets = list(dialog._footer.winfo_children())
            if len(specs) != len(widgets):
                return None
            for spec, widget in zip(specs, widgets):
                if spec.text == "Apply":
                    return widget
            return None

        def run(attempt=0, dialog=dialog, record=record, pending=pending):
            top = dialog.toplevel
            if top is None or not top.winfo_exists() or top.grab_current() is not top:
                if attempt < 200:
                    pending.append(root.after(5, lambda: run(attempt + 1)))
                return

            btn = apply_button()
            if btn is None:
                top.destroy()
                return

            # Reading 1 -- the OLD barrier.
            record["at_grab_mapped"] = bool(btn.winfo_ismapped())
            btn.focus_set()
            record["at_grab_took"] = top.focus_lastfor() is btn

            # Reading 2 -- the NEW barrier: wait for the footer to be mapped.
            waited = 0
            while not all(w.winfo_ismapped() for w in dialog._footer.winfo_children()):
                root.update()
                waited += 1
                if waited > 500:
                    break
            record["waits"] = waited
            record["at_mapped_mapped"] = bool(btn.winfo_ismapped())
            btn.focus_set()
            record["at_mapped_took"] = top.focus_lastfor() is btn

            top.destroy()

        pending.append(root.after(1, run))
        try:
            dialog.show()
        finally:
            for job in pending:
                try:
                    root.after_cancel(job)
                except tk.TclError:
                    pass
        ballast.destroy()

        if not record.get("at_grab_mapped", True):
            at_grab_unmapped += 1
        if not record.get("at_grab_took", True):
            at_grab_focus_missed += 1
        if not record.get("at_mapped_mapped", True):
            at_mapped_unmapped += 1
        if not record.get("at_mapped_took", True):
            at_mapped_focus_missed += 1

    print()
    print(f"arm 3 (under load) -- {iterations} dialogs shown with geometry work queued")
    print("  at the OLD barrier (grab only):")
    print(f"    button unmapped   : {at_grab_unmapped} / {iterations}")
    print(f"    focus_set missed  : {at_grab_focus_missed} / {iterations}")
    print("  at the NEW barrier (grab AND the footer mapped):")
    print(f"    button unmapped   : {at_mapped_unmapped} / {iterations}")
    print(f"    focus_set missed  : {at_mapped_focus_missed} / {iterations}")
    return at_grab_focus_missed, at_mapped_focus_missed


if __name__ == "__main__":
    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 40

    with bs.App(title="probe 437 focus flake") as app:
        bs.Label("probe")

    root = app._tk_root
    root.withdraw()

    ok = arm_1_control(root)
    failures = arm_2_repeat(app, iterations)
    old_missed, new_missed = arm_3_under_load(app, max(10, iterations // 4))

    print()
    print("=" * 60)
    print(f"control proved the silent no-op:   {ok}")
    print(f"flake reproduced in arm 2 (quiet): {bool(failures)}")
    print(f"arm 3: old barrier missed focus    {old_missed} time(s)")
    print(f"arm 3: new barrier missed focus    {new_missed} time(s)")
