"""A third flake: Enter on a DISABLED dialog button sometimes reaches nothing.

Surfaced while verifying #446's two known flakes, in a file the issue does not
mention: `test_dialog_press_contract.py::test_enter_on_a_disabled_button_still_
reaches_the_default` failed with `calls == []`. Neither the disabled Apply
button NOR the default OK button ran, so the key vanished between the two.

The guard cannot explain that by reading. `_key_was_consumed` sees `TButton` in
the bindtags and returns `not instate(["disabled"])`, which for a disabled
button is False -- not consumed -- so the toplevel binding should invoke the
default button every time.

So this measures the two candidate steps SEPARATELY, many times in one process,
instead of waiting for the combination to fail again:

  * did the toplevel binding run at all (was the key delivered past the
    button's own class binding)?
  * if it ran, what did the guard decide, and did `invoke()` do anything?

Run:  py -3.12 development/probe_446_disabled_button_enter.py

Output is ASCII only (this box's console is cp1252).
"""
from __future__ import annotations

import tkinter

import bootstack as bs
from bootstack.dialogs import Dialog, DialogButton
from bootstack.dialogs._impl import dialog as dialog_mod

RUNS = 40

# Exceptions raised INSIDE a Tk callback, which Python cannot otherwise see.
#
# ⚠ This is the candidate reading the guard cannot rule out. The toplevel's
# Return binding ends in `b.invoke()`; if anything in that callback raises,
# tkinter routes it to `report_callback_exception`, which PRINTS and returns.
# The binding then completes having done nothing, and the only trace left in
# the test is `calls == []` -- the exact symptom, with the cause on stderr
# where no assertion looks. A Tcl-level failure in a binding or `after` script
# is invisible in the same way and lands on `bgerror` instead. Both are
# collected here so a failing run names its own cause.
_TK_ERRORS: list[str] = []


def _install_error_collectors(root):
    """Capture both invisible failure channels. Returns an undo callable."""
    import traceback

    original = root.report_callback_exception

    def on_callback_exception(exc, val, tb):
        _TK_ERRORS.append(
            "callback: " + "".join(traceback.format_exception_only(exc, val)).strip()
        )

    def on_bgerror(*args):
        _TK_ERRORS.append(f"bgerror: {' '.join(str(a) for a in args)}")

    root.report_callback_exception = on_callback_exception
    root.tk.createcommand("bgerror", on_bgerror)

    def undo():
        root.report_callback_exception = original
        try:
            root.tk.deletecommand("bgerror")
        except tkinter.TclError:
            pass

    return undo


def _footer_widget(impl, text):
    specs = list(reversed(impl._buttons))
    widgets = list(impl._footer.winfo_children())
    if len(widgets) != len(specs):
        raise AssertionError("one footer button per spec")
    for spec, widget in zip(specs, widgets):
        if spec.text == text:
            return widget
    raise AssertionError(f"no footer button labelled {text!r}")


def _run_once(root, trace: dict) -> dict:
    calls: list[str] = []
    dialog = Dialog(
        title="disabled",
        content_builder=lambda: bs.Label("body"),
        buttons=[
            DialogButton(text="Cancel", role="cancel", result=None),
            DialogButton(text="Apply", role="secondary", result="apply",
                         command=lambda dlg: calls.append("apply")),
            DialogButton(text="OK", role="primary", result="ok", default=True,
                         command=lambda dlg: calls.append("ok")),
        ],
        parent=root,
    )
    seen: dict = {"calls": calls, "acted": False}
    pending: list[str] = []
    trace.clear()
    _TK_ERRORS.clear()

    def act(top):
        seen["acted"] = True
        apply_widget = _footer_widget(dialog, "Apply")
        apply_widget.state(["disabled"])
        seen["apply_disabled"] = bool(apply_widget.instate(["disabled"]))
        apply_widget.focus_set()
        seen["focus_took"] = top.focus_lastfor() is apply_widget
        seen["apply_mapped"] = bool(apply_widget.winfo_ismapped())
        ok_widget = _footer_widget(dialog, "OK")
        seen["ok_disabled"] = bool(ok_widget.instate(["disabled"]))
        seen["ok_exists"] = bool(ok_widget.winfo_exists())
        seen["binding"] = bool(top.bind("<Return>"))

        apply_widget.event_generate("<Return>", when="now")

        seen["trace"] = dict(trace)
        if top.winfo_exists():
            top.destroy()

    # ⚠ 120 attempts = 6050ms, BELOW `force_close`'s 8s. A budget that outlasts
    # its fallback can never report anything: the fallback destroys the dialog,
    # `show()` returns, the `finally` cancels the retries, and the give-up
    # branch never runs.
    def run(attempt=0):
        top = dialog.toplevel
        if top is None or not top.winfo_exists() or top.grab_current() is not top:
            if attempt < 120:
                pending.append(root.after(50, lambda: run(attempt + 1)))
            else:
                seen["barrier"] = "the dialog never took the modal grab"
            return
        footer = dialog._footer
        if not (footer.winfo_children()
                and all(w.winfo_ismapped() for w in footer.winfo_children())):
            if attempt < 120:
                pending.append(root.after(50, lambda: run(attempt + 1)))
            else:
                seen["barrier"] = "the footer buttons never mapped"
            return
        try:
            act(top)
        except Exception as exc:  # noqa: BLE001
            seen["error"] = f"{type(exc).__name__}: {exc}"
            if top.winfo_exists():
                top.destroy()

    def force_close():
        top = dialog.toplevel
        if top is not None and top.winfo_exists():
            seen.setdefault("barrier", "still up after 8s, the fallback closed it")
            top.destroy()

    pending.append(root.after(50, run))
    pending.append(root.after(8000, force_close))
    try:
        dialog.show()
    finally:
        for job in pending:
            try:
                root.after_cancel(job)
            except tkinter.TclError:
                pass
    if _TK_ERRORS:
        seen["tk_errors"] = list(_TK_ERRORS)
    return seen


def main() -> int:
    app = bs.App(title="probe 446 disabled enter")
    root = app._tk_root
    root.geometry("360x200+200+200")
    root.update()

    # Instrument the guard WITHOUT changing its answer, so the probe reports
    # what the shipped rule decided rather than what a copy of it would.
    trace: dict = {}
    real_guard = dialog_mod._key_was_consumed

    def traced(widget, keysym):
        answer = real_guard(widget, keysym)
        trace["guard_ran"] = True
        trace["guard_answer"] = answer
        trace["guard_widget"] = str(widget)
        trace["guard_keysym"] = keysym
        try:
            trace["guard_tags"] = [str(t) for t in widget.bindtags()]
        except Exception:  # noqa: BLE001
            trace["guard_tags"] = "<no bindtags - widget arrived as a string>"
        return answer

    dialog_mod._key_was_consumed = traced
    undo_collectors = _install_error_collectors(root)
    try:
        print("Enter on a DISABLED footer button, repeated in one process.")
        print(f"runs={RUNS}\n")
        bad = 0
        never_acted = 0
        for i in range(RUNS):
            seen = _run_once(root, trace)
            calls = seen.get("calls")
            # ⚠ A run that never pressed Enter is NOT a reproduction, and
            # counting it as one is how this probe used to lie. Its `seen` is
            # `{"calls": []}` -- byte-identical to the flake -- so a barrier
            # that never cleared read as "the key vanished between the two"
            # and sent the reader at the guard instead of at the harness.
            if not seen.get("acted"):
                never_acted += 1
                print(f"  run {i:2d}  NOT MEASURED  {seen.get('barrier', 'unknown')}")
                continue
            if calls != ["ok"]:
                bad += 1
                print(f"  run {i:2d}  FAIL calls={calls}")
                for key in sorted(seen):
                    if key not in ("calls", "acted"):
                        print(f"          {key}: {seen[key]}")
        measured = RUNS - never_acted
        print(f"\nfailures: {bad}/{measured} measured "
              f"({never_acted}/{RUNS} never pressed Enter and prove nothing)")
        print("\n" + "=" * 72)
        print("READING")
        print("=" * 72)
        print(
            "NOT MEASURED is not a failure. It means the dialog never came up,"
            "\nso Enter was never pressed and the run says nothing either way."
            "\nOnly the measured runs count.\n"
            "\nOn a MEASURED failure, read in this order:\n"
            "\n  tk_errors present -> the binding RAN and something in it raised."
            "\n    tkinter prints a callback exception and returns, so the press"
            "\n    completes having done nothing and the test sees only calls==[]."
            "\n    This is the candidate reading the guard cannot rule out."
            "\n  guard_ran False    -> the key never reached the toplevel binding,"
            "\n    a delivery problem rather than a guard one."
            "\n  guard_ran True and guard_answer True -> the guard called the press"
            "\n    consumed, which for a DISABLED button is the #441 round-4 defect"
            "\n    returning."
        )
        if bad == 0:
            print(
                "\nNo failure in this population. The condition is NOT reproduced"
                "\nby repetition alone, so it depends on state left by other"
                "\ntests -- widen the probe rather than trusting this zero."
            )
    finally:
        dialog_mod._key_was_consumed = real_guard
        undo_collectors()
        root.destroy()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except tkinter.TclError as exc:
        print(f"SKIP: no usable display ({exc})")
        raise SystemExit(0)
