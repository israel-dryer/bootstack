"""Probe: what widget does each path build for `editor='select'`? (#428)

`probe_428_select_value_paths.py` established that the READ paths are identical:
`bs.Form.get()` calls `_internal.get()`, the internal `Form.get()` is literally
`return self.data`, and `FormDialog` reads that same `.data`. All three end in
`_collect_data()`. So the divergence the reporter sees cannot come from how the
result is read, and chasing that is a dead end.

That leaves what each path BUILDS. This drives a real `FormDialog` — scheduling
the inspection on the root so it runs inside the dialog's own wait loop — and
compares the editor widget it creates against the one a public `bs.Form` creates
from the identical `FieldItem`.

It reports the widget class, the options as the widget holds them, and what
`.value` returns after selecting by TEXT the way a person would, rather than by
value the way `set()` does. Selecting by text is the part the earlier probe did
not exercise and is how the reporter hit this.

Run:  py -3.12 development/probe_428_dialog_widget.py
"""

from __future__ import annotations

import bootstack as bs
from bootstack.dialogs import FormDialog

OPTIONS = [("One", 1), ("Two", 2), ("Three", 3)]
ITEM = dict(key="k", label="K", editor="select",
            editor_options={"options": OPTIONS})

lines: list[str] = []


def describe(label: str, form_impl) -> None:
    """Report the built widget and what it returns, without assuming a shape."""
    widget = form_impl._widgets.get("k")
    lines.append(f"\n  {label}")
    lines.append(f"    widget class     : {type(widget).__name__}")
    for attr in ("options", "value", "selection", "text"):
        try:
            lines.append(f"    .{attr:<15}: {getattr(widget, attr)!r}")
        except Exception as exc:  # noqa: BLE001 - reporting, not asserting
            lines.append(f"    .{attr:<15}: <raised {type(exc).__name__}>")
    # Select by TEXT, the way a person picking from the dropdown does.
    try:
        widget.value = "One"
    except Exception as exc:  # noqa: BLE001
        lines.append(f"    set value='One'  : <raised {type(exc).__name__}: {exc}>")
    lines.append(f"    after picking 'One' by text:")
    lines.append(f"      widget.value       : {getattr(widget, 'value', '<none>')!r}")
    lines.append(f"      form.get()['k']    : {form_impl.get().get('k')!r}")
    lines.append(f"      form.data['k']     : {form_impl.data.get('k')!r}")


with bs.App(title="#428 widget probe", size=(560, 300), padding=12) as app:

    public_form = bs.Form(items=[bs.FieldItem(**ITEM)])
    app.tk.update_idletasks()
    describe("public bs.Form  -> internal Form", public_form._internal)

    # ⚠ Do NOT call dlg.show() here. It runs its own modal wait loop, and a
    # close scheduled with `after` does not break out of it — the first version
    # of this probe hung until it was killed. `_build_form_content` is the step
    # that creates `dlg.form`, so calling it directly against a real parent
    # reaches the same widget with no window to dismiss.
    dlg = FormDialog(items=[bs.FieldItem(**ITEM)])
    host = bs.Column()
    app.tk.update_idletasks()
    try:
        dlg._build_form_content(host._internal)
        app.tk.update_idletasks()
        describe("FormDialog      -> internal Form", dlg.form)
    except Exception as exc:  # noqa: BLE001 - report, never raise
        lines.append(f"\n  FormDialog build RAISED {type(exc).__name__}: {exc}")

    app.tk.after(300, app.close)

app.run()

print(f"options passed: {OPTIONS}")
print("\n".join(lines))
print(f"\nFormDialog.result: {dlg.result!r}")
