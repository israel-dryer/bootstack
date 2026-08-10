"""Probe: the reporter's literal flow, end to end, pre-fix (#428).

`probe_428_dialog_widget.py` proved the MECHANISM — read-after-teardown falling
back to the Tk variable's display text — by destroying the widgets by hand. This
runs the reporter's actual path instead: a real `FormDialog`, shown, with its OK
button pressed, and `dlg.result` read the way their code reads it.

⚠ The modal trap, again: `dlg.show()` runs its own wait loop and neither
`app.close()` nor a scheduled destroy breaks out of it. The way through is to
invoke the OK BUTTON's own command, so the dialog closes by its normal path and
`show()` returns like it does for a real user.

Reports the VALUE and its TYPE, because the reporter's complaint was that the
three paths do not agree on the kind of data they hand back.

Pre-fix this should print 'One' (str). Post-fix it must print 1 (int), matching
the two control arms in the same run.

Run:  py -3.12 development/probe_428_end_to_end.py
"""

from __future__ import annotations

import bootstack as bs
from bootstack.dialogs import FormDialog

OPTIONS = [("One", 1), ("Two", 2), ("Three", 3)]
PICK = "One"
EXPECTED = 1

out: list[str] = []


def report(label: str, got) -> None:
    ok = got == EXPECTED and type(got) is type(EXPECTED)
    out.append(f"  {label:<34} {got!r:<8} {type(got).__name__:<5} "
               f"{'OK' if ok else 'MISMATCH'}")


with bs.App(title="#428 end to end", size=(460, 240), padding=12) as app:

    # --- control 1: a plain Select ---------------------------------------
    plain = bs.Select(options=OPTIONS)
    plain.value = PICK
    app.tk.update_idletasks()
    report("bs.Select.value", plain.value)

    # --- control 2: the same field in a Form ------------------------------
    form = bs.Form(items=[bs.FieldItem(key="k", label="K", editor="select",
                                       editor_options={"options": OPTIONS})])
    app.tk.update_idletasks()
    form._internal._widgets["k"].value = PICK
    app.tk.update_idletasks()
    report("Form.get()['k']", form.get()["k"])

    # --- the reported path: a real dialog, really dismissed ---------------
    dlg = FormDialog(items=[bs.FieldItem(key="k", label="K", editor="select",
                                         editor_options={"options": OPTIONS})])

    def press_ok() -> None:
        impl = dlg._internal
        if impl.form is None:
            out.append("  dialog form never built")
            return
        impl.form._widgets["k"].value = PICK
        impl.form._internal_frame.update_idletasks() if hasattr(
            impl.form, "_internal_frame") else app.tk.update_idletasks()
        # Press OK through its own command, so the dialog closes normally.
        for button in impl._buttons:
            if button.role != "cancel":
                button.command()
                return
        out.append("  no non-cancel button found")

    app.tk.after(800, press_ok)
    dlg.show()

    report("FormDialog.result['k']",
           dlg.result["k"] if isinstance(dlg.result, dict) else dlg.result)

    app.tk.after(200, app.close)

app.run()

print(f"options {OPTIONS}, picked {PICK!r}, expecting {EXPECTED!r}\n")
print(f"  {'path':<34} {'value':<8} {'type':<5} verdict")
print("  " + "-" * 60)
print("\n".join(out))
