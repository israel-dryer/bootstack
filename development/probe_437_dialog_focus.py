"""Where does focus actually sit when a real `Dialog` comes up?

`Dialog._create_standard_buttons` calls `default_button.focus_set()`, and
`DialogButton.default` is documented as "focused, triggered by Enter". This
probe checks the first half of that claim, with NOTHING forced — no
`focus_force`, no `focus_set` of its own — because that is the difference
between measuring the framework and measuring the probe.

It exists because `probe_437_round3.py` did force focus (`_invoke_arm` calls
`top.focus_force()` then `button.focus_set()`), and so could not have noticed
that a real dialog never gets there. That mattered: it made the Enter
double-dispatch look reachable from any open dialog, when in fact it needs a
button to hold focus first — which a CLICK provides, since ttk's own `Press`
binding does `focus $w` unconditionally.

Arm 2 is the control. It asks the same questions after focusing the button by
hand, so a reader can see the measurement is capable of reporting "the button
has focus" and simply does not, unprompted.

ASCII output only: this box's console is cp1252 and a check mark raises
UnicodeEncodeError.

Run: py -3.12 development/probe_437_dialog_focus.py
"""
from __future__ import annotations

import bootstack as bs
from bootstack.dialogs import Dialog, DialogButton


def _drive(dialog, root, action, budget_ms=8000):
    """Show `dialog`, run `action(top)` once the modal grab is really up.

    `show()` runs its own wait loop that a scheduled close does not break, so
    every arm leaves by destroying the toplevel from inside the action. The
    poll waits on `grab_current()` rather than a fixed delay: `show()` builds
    and positions the window - both of which pump the event loop on Windows -
    before `grab_set()`, which makes the grab the only sound barrier.
    """
    def poll(attempt=0):
        top = dialog.toplevel
        if top is None or not top.winfo_exists() or top.grab_current() is not top:
            if attempt < 100:
                root.after(50, lambda: poll(attempt + 1))
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
    """Map spec text -> footer widget.

    `_create_standard_buttons` builds one button per spec in reverse order,
    which is what makes the pairing positional.
    """
    widgets = list(dialog._footer.winfo_children())
    specs = list(reversed(dialog._buttons))
    assert len(widgets) == len(specs), "precondition: one footer button per spec"
    return {spec.text: widget for spec, widget in zip(specs, widgets)}


def arm(root, label, focus_the_button, expected):
    dialog = Dialog(
        title="probe",
        content_builder=lambda: bs.Label("body"),
        buttons=[
            DialogButton(text="Cancel", role="cancel", result=None),
            DialogButton(text="OK", role="primary", result="ok", default=True),
        ],
        parent=root,
    )
    state = {}

    def action(top):
        ok = _footer_pairs(dialog)["OK"]
        if focus_the_button:
            ok.focus_set()
            root.update()
        state["the default button is"] = str(ok)
        state["focus_lastfor() reports"] = str(top.focus_lastfor())
        state["tcl [focus] reports"] = str(top.tk.call("focus"))
        state["focus is on the button"] = top.focus_lastfor() is ok

    _drive(dialog, root, action)

    print(f"ARM {label}")
    for key, value in state.items():
        print(f"    {key:32} {value}")
    print(f"    {'expected':32} {expected}")
    print()


if __name__ == "__main__":
    # One `bs.App` for both arms. A second one in the same process raises
    # `TclError: named font body does not already exist` - the same
    # one-app-per-process constraint the GUI suite works under (#150).
    _app = bs.App(title="probe")
    _root = _app._tk_root
    _root.deiconify()
    _root.update()

    arm(_root, "as Dialog leaves it (nothing forced)", False,
        "focus_set() at dialog.py:544 should have focused the button. "
        "MEASURED: the toplevel -> the call is a no-op")
    arm(_root, "control: focus the button by hand", True,
        "focus is on the button = True, which is what a CLICK produces")
