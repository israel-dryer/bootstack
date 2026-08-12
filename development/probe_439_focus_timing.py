"""Probe for #439 - WHEN can the default button actually take focus?

`Dialog` calls `default_button.focus_set()` from `_build_footer`
(dialog.py:544) while the toplevel is still WITHDRAWN (`_create_toplevel`,
dialog.py:402), and the footer buttons are STILL not mapped once `deiconify()`
has returned (measured below). `TkSetFocusWin` walks a widget's ancestry and
returns without setting anything if any window on that path is unmapped,
reporting nothing - so the call is a silent no-op.

This probe picks between candidate fixes by measurement rather than by
reasoning about Tk's focus rules, which are not obvious here: it is genuinely
unclear whether `focus_set()` on an unmapped widget is DISCARDED or merely
DEFERRED until the widget maps. Those two possibilities imply completely
different fixes, and only one of them is cheap.

Three arms, each on its own dialog:

  A  control - the framework untouched, nothing forced. This is #439.
  B  focus_set() once positioning is done, while the button is still unmapped.
     Passes iff Tk DEFERS the request to map time.
  C  focus_set() from the button's own <Map> binding - the precise
     precondition, and the only arm that cannot depend on that question.

⚠ Each arm measures a dialog it did NOT force focus on beforehand. An earlier
draft of this probe called `focus_set()` mid-measurement and then reported the
state it had itself created - the same defect that hid #439 inside
`probe_437_round3.py`. Arm A is what keeps the other two honest: if A ever
reports the button focused, the arms below prove nothing.

Run:  py -3.13 development/probe_439_focus_timing.py
"""

from __future__ import annotations

import sys

import bootstack as bs
from bootstack.dialogs._impl.dialog import Dialog, DialogButton

DEFAULT_TEXT = "OK"

results: dict[str, dict] = {}


def _find_default(dialog):
    """The default button, by text. Footer buttons are created in reverse."""
    footer = getattr(dialog, "_footer", None)
    if footer is None or not footer.winfo_exists():
        return None
    for child in footer.winfo_children():
        try:
            if child.cget("text") == DEFAULT_TEXT:
                return child
        except Exception:
            continue
    return None


def run_arm(app, name: str, strategy: str) -> None:
    """Open one dialog under `strategy`, then measure once it is really up."""
    root = app._tk_root
    dialog = Dialog(
        parent=root,
        title=f"probe {name}",
        buttons=[
            DialogButton(text=DEFAULT_TEXT, role="primary", default=True),
            DialogButton(text="Cancel", role="cancel"),
        ],
    )

    original_position = Dialog._position_dialog
    observed: dict = {"strategy": strategy}

    def instrumented(self, *a, **kw):
        result = original_position(self, *a, **kw)
        btn = _find_default(self)
        observed["mapped_after_deiconify"] = (
            btn.winfo_ismapped() if btn is not None else None
        )
        if strategy == "after_position" and btn is not None:
            # Arm B: ask now, while still unmapped. Deferred or discarded?
            btn.focus_set()
        elif strategy == "on_map" and btn is not None:
            # Arm C: wait for the precondition Tk actually requires.
            def on_map(event=None, w=btn):
                try:
                    w.unbind("<Map>", bind_id)
                except Exception:
                    pass
                if w.winfo_exists():
                    w.focus_set()

            bind_id = btn.bind("<Map>", on_map, add="+")
        return result

    Dialog._position_dialog = instrumented
    try:
        def measure_then_close():
            top = dialog.toplevel
            if top is None or not top.winfo_exists():
                observed["error"] = "toplevel gone before measurement"
                return
            btn = _find_default(dialog)
            observed["mapped_at_measure"] = (
                btn.winfo_ismapped() if btn is not None else None
            )
            # ⚠ str() is load-bearing: tk.call returns a Tcl_Obj, which never
            # compares equal to a widget path string even when the two print
            # identically. Without it every arm reads FOCUSED=False.
            observed["tcl_focus"] = str(top.tk.call("focus") or "(none)")
            observed["focus_lastfor"] = str(top.focus_lastfor())
            observed["button_path"] = str(btn) if btn is not None else "(not found)"
            observed["focused"] = (
                btn is not None and observed["tcl_focus"] == str(btn)
            )
            top.destroy()

        # Well clear of the geometry manager's idle pass, so "not yet mapped"
        # cannot be mistaken for "never focused".
        root.after(500, measure_then_close)
        dialog.show()
    finally:
        Dialog._position_dialog = original_position

    results[name] = observed


with bs.App(title="probe_439", size=(360, 220)) as app:
    run_arm(app, "A control (framework as-is)", "none")
    run_arm(app, "B focus_set after positioning", "after_position")
    run_arm(app, "C focus_set from <Map>", "on_map")

print("MEASURED - does the default button end up focused?\n")
for name, obs in results.items():
    print(f"  {name}")
    print(f"      button mapped after deiconify() : {obs.get('mapped_after_deiconify')}")
    print(f"      button mapped at measurement    : {obs.get('mapped_at_measure')}")
    print(f"      the default button is           : {obs.get('button_path')}")
    print(f"      tcl [focus] reports             : {obs.get('tcl_focus')}")
    print(f"      focus_lastfor() reports         : {obs.get('focus_lastfor')}")
    print(f"      FOCUSED                         : {obs.get('focused')}")
    print()

control = results["A control (framework as-is)"].get("focused")
after_position = results["B focus_set after positioning"].get("focused")
on_map = results["C focus_set from <Map>"].get("focused")

print("=" * 70)
if control:
    print("CONTROL IS DEAD: the framework already focuses the button, so arms")
    print("B and C prove nothing and #439 does not reproduce here.")
    sys.exit(1)

print("Arm A reproduces #439: the default button is NOT focused.\n")
print(f"  B  focus_set() while unmapped, after positioning : {after_position}")
print(f"  C  focus_set() from the button's <Map>           : {on_map}")
print()
if on_map and not after_position:
    print("=> Tk DISCARDS a focus request for an unmapped widget; it does not")
    print("   defer it. The fix must wait for <Map>. Arm C is the fix.")
elif after_position and on_map:
    print("=> Both work on this box, so Tk DEFERS the request. Prefer C anyway:")
    print("   it states the precondition instead of relying on that deferral,")
    print("   which is not guaranteed across platforms.")
elif after_position and not on_map:
    print("=> Unexpected: the simple fix works and the <Map> one does not.")
    print("   Investigate before choosing - <Map> may not fire for this widget.")
else:
    print("=> NEITHER candidate works. Do not guess; measure a third approach")
    print("   before writing a fix.")
sys.exit(0)
