"""Probe for #439 - the default button must actually end up focused.

`Dialog._create_standard_buttons` focused the default button from
`_build_footer`, which runs while `_create_toplevel` still has the toplevel
WITHDRAWN. `focus_set()` is a silent no-op there, so the call never took and
`focus_lastfor()` kept naming the toplevel. The fix waits for the button's own
`<Map>` (`Dialog._focus_when_mapped`).

⚠ THE BARRIER IS THE WHOLE DIFFICULTY, and it is why the older
`development/probe_437_dialog_focus.py` still reports "focus is on the button
False" against FIXED code. That probe waits on the modal grab, and the grab is
set BEFORE the geometry manager maps the footer's children at idle - so it
measures while the button is still unmapped and `<Map>` has not fired yet. The
grab is not a sound barrier for a focus question; being mapped is. Do not read
that probe's output as this fix failing.

Arms:

  A  pre-fix control - `_focus_when_mapped` patched back to a bare
     `focus_set()`, which is the shipped-in-0.3.0 behavior. Must NOT focus.
  B  the fix. Must focus.
  C  QueryDialog - the entry must keep focus, not lose it to the default
     button. `_build_content` re-focuses the entry via `after_idle`
     specifically to win this race, and #439 changes who it is racing.

A and B differ only in that patch, so B cannot pass for an unrelated reason.

Run:  py -3.13 development/probe_439_default_button_focus.py
"""

from __future__ import annotations

import sys

import bootstack as bs
from bootstack.dialogs._impl.dialog import Dialog, DialogButton

failures: list[str] = []


def _drive_until_mapped(dialog, root, action, budget_ms=8000):
    """Show `dialog`; run `action(top)` once the footer is really mapped.

    Waits on the grab AND on every footer child being mapped. The grab alone
    is not enough - see the module docstring.
    """
    def footer_is_up(dlg) -> bool:
        footer = getattr(dlg, "_footer", None)
        if footer is None or not footer.winfo_exists():
            return False
        children = footer.winfo_children()
        return bool(children) and all(c.winfo_ismapped() for c in children)

    def poll(attempt=0):
        top = dialog.toplevel
        ready = (
            top is not None and top.winfo_exists()
            and top.grab_current() is top
            and footer_is_up(dialog)
        )
        if not ready:
            if attempt < 150:
                root.after(50, lambda: poll(attempt + 1))
            else:
                failures.append("barrier never satisfied - dialog never came up")
            return
        try:
            action(top)
        finally:
            if dialog.toplevel is not None and dialog.toplevel.winfo_exists():
                dialog.toplevel.destroy()

    def bail():
        top = dialog.toplevel
        if top is not None and top.winfo_exists():
            top.destroy()

    root.after(50, poll)
    root.after(budget_ms, bail)
    dialog.show()


def _footer_pairs(dialog):
    """Map spec text -> footer widget (built one per spec, in reverse)."""
    widgets = list(dialog._footer.winfo_children())
    specs = list(reversed(dialog._buttons))
    assert len(widgets) == len(specs), "precondition: one footer button per spec"
    return {spec.text: widget for spec, widget in zip(specs, widgets)}


def dialog_arm(root, label, *, prefix_behavior: bool, expect_focused: bool):
    dialog = Dialog(
        title="probe",
        content_builder=lambda: bs.Label("body"),
        buttons=[
            DialogButton(text="Cancel", role="cancel", result=None),
            DialogButton(text="OK", role="primary", result="ok", default=True),
        ],
        parent=root,
    )
    state: dict = {}

    # ⚠ Take the staticmethod OBJECT out of __dict__. Reading it as
    # `Dialog._focus_when_mapped` yields the plain function, and assigning that
    # back makes it an instance method - so the restore silently changes the
    # signature and the next arm dies with "takes 1 positional argument".
    original = Dialog.__dict__["_focus_when_mapped"]
    if prefix_behavior:
        # The 0.3.0 behavior, restored exactly: focus at build time.
        Dialog._focus_when_mapped = staticmethod(lambda w: w.focus_set())

    def action(top):
        ok = _footer_pairs(dialog)["OK"]
        state["default button"] = str(ok)
        state["button mapped"] = ok.winfo_ismapped()
        state["focus_lastfor()"] = str(top.focus_lastfor())
        state["tcl [focus]"] = str(top.tk.call("focus"))
        state["focused"] = top.focus_lastfor() is ok

    try:
        _drive_until_mapped(dialog, root, action)
    finally:
        Dialog._focus_when_mapped = original

    print(f"ARM {label}")
    for key, value in state.items():
        print(f"    {key:22} {value}")
    got = state.get("focused")
    ok = (got is expect_focused)
    print(f"    {'expected':22} focused={expect_focused}")
    print(f"    {'RESULT':22} {'ok' if ok else 'FAIL'}\n")
    if not ok:
        failures.append(f"{label}: expected focused={expect_focused}, got {got}")


def query_arm(root, label, *, prefix_behavior: bool):
    """The entry must keep focus - the default button must not steal it.

    Run against BOTH behaviors. If the entry lacks focus pre-fix too, then
    `ask_string()` was already broken (a second instance of #439) rather than
    regressed by this branch - and those are different bugs with different
    fixes, so the control decides it rather than an assumption.
    """
    from bootstack.dialogs._impl.query import QueryDialog

    original = Dialog.__dict__["_focus_when_mapped"]
    if prefix_behavior:
        Dialog._focus_when_mapped = staticmethod(lambda w: w.focus_set())

    q = QueryDialog("Name:", master=root)
    dialog = q._dialog
    state: dict = {}

    def action(top):
        entry = q._entry_widget
        target = getattr(entry, "entry_widget", entry)
        holder = str(top.tk.call("focus"))
        state["entry widget"] = str(target)
        state["tcl [focus]"] = holder
        state["entry has focus"] = holder == str(target)

    try:
        _drive_until_mapped(dialog, root, action)
    finally:
        Dialog._focus_when_mapped = original

    print(f"ARM {label}")
    for key, value in state.items():
        print(f"    {key:22} {value}")
    print(f"    {'entry has focus':22} {state.get('entry has focus')}")
    return bool(state.get("entry has focus"))


if __name__ == "__main__":
    # One `bs.App` per process (#150): a second raises
    # `TclError: named font body does not already exist`.
    _app = bs.App(title="probe")
    _root = _app._tk_root
    _root.deiconify()
    _root.update()

    dialog_arm(_root, "A pre-fix control (bare focus_set at build time)",
               prefix_behavior=True, expect_focused=False)
    dialog_arm(_root, "B the fix (_focus_when_mapped)",
               prefix_behavior=False, expect_focused=True)
    before = query_arm(_root, "C1 QueryDialog, pre-fix behavior",
                       prefix_behavior=True)
    print()
    after = query_arm(_root, "C2 QueryDialog, with the fix",
                      prefix_behavior=False)
    print()

    print("QueryDialog verdict")
    print(f"    entry focused pre-fix : {before}")
    print(f"    entry focused post-fix: {after}")
    if before and not after:
        failures.append(
            "REGRESSION: the entry held focus before this branch and does not "
            "now - the default button steals it, so ask_string() stops "
            "accepting typing. The fix must yield to content focus."
        )
    elif not before and not after:
        print("    -> the entry never had focus; ask_string() is a SECOND")
        print("       instance of #439, not something this branch broke.")
    elif after:
        print("    -> the entry keeps focus. No regression.")
    print()

    print("=" * 66)
    if failures:
        print(f"FAIL ({len(failures)})")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print("PASS - the default button is focused, and QueryDialog's entry still wins")
