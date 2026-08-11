"""Round-3 review measurements for #437 / #438 — the Enter-key double invoke.

Each arm runs in ITS OWN PROCESS: the first `bs.App` in a process registers the
named fonts, and a second one in the same process dies with
`TclError: named font body does not already exist`. Run with no argument to
drive every arm as a subprocess; run with an arm name to execute just that one.

    py -3.12 development/probe_437_round3.py
    py -3.12 development/probe_437_round3.py control

Arms
----
control      the `TButton` class binding alone (toplevel bindings stripped)
             -> 1 invoke.  Without this the "2" below means nothing.
shipped      class binding + the toplevel binding this branch adds, command
             returns False (refuses) -> 2 invokes for one key press.
accepting    same, command returns None -> 1 invoke; the destroy aborts the
             rest of the dispatch, which is why the defect was invisible
             before #437 made a press survivable.
crossfire    focus a NON-default button whose command refuses, press Enter once
             -> the refusing command runs AND the default button is invoked,
             closing the dialog with the other button's result.
classbind    what `bind_class('TButton')` actually carries — the premise behind
             "the keypad key did nothing at all in a dialog".
cancel_trap  #438: a `role='cancel', result='ok'` button on an invalid form is
             refused, and so is Escape, because Escape is bound to that button.
grab         the docs' refusal pattern: `bs.alert()` inside the command leaves
             `grab_current()` None, so the dialog stops being modal.

Output is ASCII only — this box's console is cp1252.
"""
from __future__ import annotations

import subprocess
import sys

import bootstack as bs
from bootstack.dialogs import Dialog, DialogButton

ARMS = ["control", "shipped", "accepting", "crossfire", "classbind",
        "cancel_trap", "grab"]


def _report(name, state, expected):
    print("ARM %s" % name)
    for key, value in state.items():
        print("    %-24s %s" % (key, value))
    print("    %-24s %s" % ("expected", expected))
    print("")


def _drive(dialog, root, action, budget_ms=8000):
    """Show `dialog` and run `action()` once its modal grab is really up.

    `show()` runs a wait loop that no scheduled close escapes, and it pumps the
    event loop while building and positioning — so poll for `grab_set()`, which
    is the last thing it does before waiting, rather than firing on a timer.
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


def _invoke_arm(strip_toplevel_binding, refuse):
    calls = []
    app = bs.App(title="probe")
    root = app._tk_root
    root.deiconify()
    root.update()

    def command(_dlg):
        calls.append(1)
        return False if refuse else None

    dialog = Dialog(
        title="probe",
        content_builder=lambda: bs.Label("body"),
        buttons=[DialogButton(text="OK", role="primary", result="ok",
                              default=True, command=command)],
        parent=root,
    )
    state = {}

    def action(top):
        button = _footer_pairs(dialog)["OK"]
        top.focus_force()
        button.focus_set()
        root.update()
        state["focus_is_the_button"] = top.focus_get() is button
        state["bindtags"] = [str(t) for t in button.bindtags()]
        if strip_toplevel_binding:
            top.unbind("<Return>")
            top.unbind("<KP_Enter>")
        state["toplevel_return_bound"] = bool(top.bind("<Return>"))
        button.event_generate("<Return>", when="now")
        root.update()
        state["invokes_for_one_press"] = len(calls)

    _drive(dialog, root, action)
    return state


def arm_control():
    _report("control (class binding only)", _invoke_arm(True, refuse=True),
            "invokes_for_one_press = 1")


def arm_shipped():
    _report("shipped (class + toplevel), command refuses",
            _invoke_arm(False, refuse=True),
            "invokes_for_one_press = 1; MEASURED 2 -> the defect")


def arm_accepting():
    _report("shipped (class + toplevel), command accepts",
            _invoke_arm(False, refuse=False),
            "invokes_for_one_press = 1 (the destroy aborts the dispatch)")


def arm_crossfire():
    log = []
    app = bs.App(title="probe")
    root = app._tk_root
    root.deiconify()
    root.update()

    def apply_refuses(_dlg):
        log.append("apply")
        return False

    def ok(_dlg):
        log.append("ok")

    dialog = Dialog(
        title="probe",
        content_builder=lambda: bs.Label("body"),
        buttons=[
            DialogButton(text="Apply", role="secondary", result="apply",
                         command=apply_refuses),
            DialogButton(text="OK", role="primary", result="ok",
                         default=True, command=ok),
        ],
        parent=root,
    )
    state = {}

    def action(top):
        apply_button = _footer_pairs(dialog)["Apply"]
        top.focus_force()
        apply_button.focus_set()
        root.update()
        state["focus_is_apply"] = top.focus_get() is apply_button
        apply_button.event_generate("<Return>", when="now")
        root.update()
        state["commands_run"] = list(log)
        state["still_open"] = bool(top.winfo_exists())
        state["dialog_result"] = dialog.result

    _drive(dialog, root, action)
    _report("crossfire (Enter on a refusing non-default button)", state,
            "commands_run = ['apply']; still_open = 1; result = None. "
            "MEASURED ['apply','ok'] / 0 / 'ok'")


def arm_classbind():
    app = bs.App(title="probe")
    root = app._tk_root
    root.update()
    state = {
        "TButton class bindings": sorted(str(s) for s in root.bind_class("TButton")),
        "KP_Enter bound at class level": bool(root.bind_class("TButton", "<KP_Enter>")),
    }
    root.destroy()
    _report("classbind (was the keypad key really unwired?)", state,
            "if <Key-KP_Enter> is listed, the key already pressed a FOCUSED button")


def arm_cancel_trap():
    from bootstack.dialogs import FormDialog

    app = bs.App(title="probe")
    root = app._tk_root
    root.deiconify()
    root.update()

    public = FormDialog(
        items=[bs.FieldItem(key="name", label="Name", editor="text", required=True)],
        buttons=[DialogButton(text="Close", role="cancel", result="ok"),
                 DialogButton(text="OK", role="primary", result="ok", default=True)],
        parent=root,
    )
    impl = public._internal
    state = {}

    def action(top):
        _footer_pairs(impl._dialog)["Close"].invoke()
        root.update()
        state["open_after_pressing_Close"] = bool(top.winfo_exists())
        if top.winfo_exists():
            top.event_generate("<Escape>", when="now")
            root.update()
            state["open_after_Escape"] = bool(top.winfo_exists())

    def poll(attempt=0):
        top = impl._dialog.toplevel
        if top is None or not top.winfo_exists() or top.grab_current() is not top:
            if attempt < 100:
                root.after(50, lambda: poll(attempt + 1))
            return
        try:
            action(top)
        finally:
            if top.winfo_exists():
                top.destroy()

    root.after(50, poll)
    root.after(8000, lambda: impl._dialog.toplevel is not None
               and impl._dialog.toplevel.winfo_exists()
               and impl._dialog.toplevel.destroy())
    public.show()
    _report("cancel_trap (role='cancel', result='ok', required field blank)", state,
            "both should be 0 (the dialog closes). MEASURED 1 / 1 -> no way out")


def arm_grab():
    app = bs.App(title="probe")
    root = app._tk_root
    root.deiconify()
    root.update()
    state = {}

    def save(dlg):
        state["grab_before_alert"] = str(dlg.toplevel.grab_current())
        bs.alert("A name is required.")
        state["grab_after_alert"] = str(dlg.toplevel.grab_current())
        return False

    dialog = Dialog(
        title="probe",
        content_builder=lambda: bs.Label("body"),
        buttons=[DialogButton(text="Save", role="primary", result="save",
                              command=save)],
        parent=root,
    )

    def action(top):
        # Close the nested alert from the outside; it is modal on top of us.
        root.after(300, lambda: [w.destroy() for w in root.winfo_children()
                                 if w is not top and w.winfo_class() == "Toplevel"])
        _footer_pairs(dialog)["Save"].invoke()
        root.update()

    _drive(dialog, root, action, budget_ms=12000)
    _report("grab (the docs' refusal pattern)", state,
            "grab_after_alert should still be the dialog. MEASURED None -> "
            "the dialog is no longer modal")


def main():
    if len(sys.argv) > 1:
        name = sys.argv[1]
        if name not in ARMS:
            print("unknown arm %r; pick one of %s" % (name, ", ".join(ARMS)))
            return 2
        globals()["arm_" + name]()
        return 0

    for name in ARMS:
        proc = subprocess.run([sys.executable, __file__, name],
                              capture_output=True, text=True)
        sys.stdout.write(proc.stdout)
        if proc.returncode != 0:
            print("ARM %s FAILED (exit %s)" % (name, proc.returncode))
            sys.stdout.write(proc.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
