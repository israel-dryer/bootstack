"""Probe: what do the three Select paths actually return? (#428)

The report says `FormDialog` hands back the option's TEXT where a plain
`bs.Select` and a `Form` select hand back its VALUE. Reproduced here before
anything is changed, because the issue names two suspects and the fix depends
on which layer actually differs - and on whether `Form` and `FormDialog` really
disagree, or whether the difference is in how the result is READ.

Everything runs headless-ish in one app instance and prints what it measured
rather than asserting a Windows answer.

Arms:
  1. plain    - bs.Select(options=OPTIONS).value
  2. form     - bs.Form(...).get_field_value(key) and .get()
  3. dialog   - the same field built the way FormDialog builds it, read the way
                FormDialog reads it. The dialog itself is modal, so this drives
                the layer underneath rather than opening a window nobody can
                click.

Run:  py -3.12 development/probe_428_select_value_paths.py
"""

from __future__ import annotations

import bootstack as bs

OPTIONS = [("One", 1), ("Two", 2), ("Three", 3)]
PICK_TEXT = "One"
EXPECTED = 1

findings: list[str] = []


def show(label: str, got) -> None:
    verdict = "VALUE (ok)" if got == EXPECTED else (
        "TEXT  (bug)" if got == PICK_TEXT else "other (bug)"
    )
    findings.append(f"  {label:<46} {got!r:<12} {type(got).__name__:<6} {verdict}")


with bs.App(title="#428 probe", size=(520, 260), padding=12) as app:

    # --- arm 1: a plain Select -------------------------------------------
    plain = bs.Select(options=OPTIONS)
    plain.value = EXPECTED
    app.tk.update_idletasks()
    show("bs.Select.value", plain.value)
    show("bs.Select.selection", getattr(plain, "selection", "<no attr>"))

    # --- arm 2: the same option list inside a Form ------------------------
    form = bs.Form(items=[
        bs.FieldItem(key="k", label="K", editor="select",
                     editor_options={"options": OPTIONS}),
    ])
    app.tk.update_idletasks()
    form.set({"k": EXPECTED})
    app.tk.update_idletasks()
    show("Form.get_field_value('k')", form.get_field_value("k"))
    show("Form.get()['k']", form.get().get("k"))

    # --- arm 3: what FormDialog does with the same field ------------------
    # Reached without opening the modal dialog: build one, drive its form, and
    # read the result the way its own accessor does.
    from bootstack.dialogs import FormDialog

    dlg = FormDialog(items=[
        bs.FieldItem(key="k", label="K", editor="select",
                     editor_options={"options": OPTIONS}),
    ])
    inner = None
    for name in ("_form", "form", "_content_form"):
        inner = getattr(dlg, name, None)
        if inner is not None:
            findings.append(f"  (FormDialog's form found at .{name})")
            break
    if inner is None:
        findings.append("  (could not reach FormDialog's internal form - "
                        "inspect the class)")
    else:
        app.tk.update_idletasks()
        inner.set({"k": EXPECTED})
        app.tk.update_idletasks()
        show("FormDialog inner form.get_field_value('k')",
             inner.get_field_value("k"))
        show("FormDialog inner form.get()['k']", inner.get().get("k"))

    app.tk.after(200, app.close)

app.run()

print(f"options = {OPTIONS}")
print(f"picked  = {PICK_TEXT!r} -> expected {EXPECTED!r}\n")
print(f"  {'path':<46} {'returned':<12} {'type':<6} verdict")
print("  " + "-" * 74)
print("\n".join(findings))
