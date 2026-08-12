"""Flake B of #446: the barrier waits for the FOOTER, the test measures the ENTRY.

`test_query_dialog_focuses_its_entry_not_the_default_button` fails about 1 run
in 8 with focus on the TOPLEVEL rather than the entry -- the #437 signature of
`focus_set()` no-opping against an unmapped widget.

`_drive` holds until the modal grab is up AND every FOOTER child is mapped.
That is the correct barrier for `test_dialog_press_contract.py`, where the
widget under test IS a footer button. Here the widget under test is
`QueryDialog`'s entry, which lives in the CONTENT area -- a different subtree
that the barrier says nothing about. Initial focus is deferred to the target's
own `<Map>` (`Dialog._focus_when_mapped`), so if the entry maps after the
footer, the test samples focus before it can possibly have landed.

This measures the ORDERING directly rather than waiting for the flake: for each
dialog it records whether the focus target was already mapped at the moment the
old barrier opened. Any nonzero count is the flake's precondition.

Run:  py -3.12 development/probe_446_barrier_scope.py

Output is ASCII only (this box's console is cp1252).
"""
from __future__ import annotations

import tkinter

import bootstack as bs

RUNS = 12


def _footer_up(dialog) -> bool:
    footer = getattr(dialog, "_footer", None)
    if footer is None or not footer.winfo_exists():
        return False
    children = footer.winfo_children()
    return bool(children) and all(w.winfo_ismapped() for w in children)


def _focus_target(dialog):
    """What `show()` resolved initial focus onto -- content beats the button."""
    return dialog._focus_target or dialog._default_button


def _run_once(root) -> dict:
    from bootstack.dialogs._impl.query import QueryDialog

    query = QueryDialog("Name:", master=root)
    dialog = query._dialog
    seen: dict = {}
    pending: list[str] = []

    def run(attempt=0):
        top = dialog.toplevel
        if top is None or not top.winfo_exists():
            if attempt < 200:
                pending.append(root.after(50, lambda: run(attempt + 1)))
            return
        # The OLD barrier: grab + footer mapped.
        if top.grab_current() is not top or not _footer_up(dialog):
            if attempt < 200:
                pending.append(root.after(50, lambda: run(attempt + 1)))
            return
        target = _focus_target(dialog)
        seen["target_mapped_at_old_barrier"] = bool(
            target is not None and target.winfo_ismapped()
        )
        seen["focus_at_old_barrier"] = str(top.focus_lastfor())
        seen["target"] = str(target)
        seen["top"] = str(top)
        # Now hold for what the NEW barrier adds, and re-read.
        for _ in range(200):
            if target is not None and target.winfo_ismapped():
                break
            root.update()
            root.after(10)
            root.update()
        seen["target_mapped_after_wait"] = bool(
            target is not None and target.winfo_ismapped()
        )
        seen["focus_after_wait"] = str(top.focus_lastfor())
        top.destroy()

    def force_close():
        top = dialog.toplevel
        if top is not None and top.winfo_exists():
            top.destroy()

    pending.append(root.after(50, run))
    pending.append(root.after(8000, force_close))
    try:
        query.show()
    finally:
        for job in pending:
            try:
                root.after_cancel(job)
            except tkinter.TclError:
                pass
    return seen


def main() -> int:
    app = bs.App(title="probe 446 flake B")
    root = app._tk_root
    root.geometry("360x200+200+200")
    root.update()

    print("Flake B -- is the focus target mapped when the OLD barrier opens?")
    print(f"runs={RUNS}\n")

    unmapped_at_barrier = 0
    focus_wrong_at_barrier = 0
    focus_wrong_after_wait = 0
    rows = []
    for i in range(RUNS):
        seen = _run_once(root)
        if not seen:
            rows.append(f"  run {i:2d}  <dialog never came up>")
            continue
        at = seen["target_mapped_at_old_barrier"]
        ok_at = seen["focus_at_old_barrier"] == seen["target"]
        ok_after = seen["focus_after_wait"] == seen["target"]
        unmapped_at_barrier += 0 if at else 1
        focus_wrong_at_barrier += 0 if ok_at else 1
        focus_wrong_after_wait += 0 if ok_after else 1
        rows.append(
            f"  run {i:2d}  target mapped at old barrier: {str(at):5s}"
            f"   focus correct then: {str(ok_at):5s}"
            f"   after waiting for the map: {str(ok_after):5s}"
        )
    for row in rows:
        print(row)

    print("\n" + "=" * 72)
    print("READING")
    print("=" * 72)
    print(f"target UNMAPPED when the old barrier opened : {unmapped_at_barrier}/{RUNS}")
    print(f"focus NOT on the target at the old barrier  : {focus_wrong_at_barrier}/{RUNS}")
    print(f"focus NOT on the target after the map wait  : {focus_wrong_after_wait}/{RUNS}")
    print(
        "\nThe first two columns track each other: the barrier opens, the entry"
        "\nis not mapped yet, and focus is therefore still on the toplevel. The"
        "\nthird column is what the widened barrier buys -- it must be 0, and if"
        "\nit is not, the failure is NOT a barrier problem and the fix is wrong."
    )
    root.destroy()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except tkinter.TclError as exc:
        print(f"SKIP: no usable display ({exc})")
        raise SystemExit(0)
