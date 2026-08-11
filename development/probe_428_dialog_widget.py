"""Probe: what does FormDialog build for `editor='select'`? (#428)

`probe_428_select_value_paths.py` ruled out the read path: `bs.Form.get()`,
the internal `Form.get()` and `FormDialog`'s `.data` all end in
`_collect_data()`. So the difference has to be in what the dialog BUILDS.

Reaching the dialog's form needs two things the first attempt got wrong, both
recorded here so they are not hit again:

  - `bootstack.dialogs.FormDialog` is a public WRAPPER. The impl class — the one
    with `_build_form_content` and `form` — is at `._internal`.
  - `dlg.show()` runs a modal wait loop that a close scheduled with `after` does
    NOT break; it hangs. `_build_form_content(parent)` is what creates
    `.form`, so calling it against a real parent reaches the same widget with no
    window to dismiss.

Both halves are built in ONE app instance and compared side by side, because the
first app in a process is themed and later ones are not — a difference that has
already produced one confident wrong answer on this branch.

Run:  py -3.12 development/probe_428_dialog_widget.py
"""

from __future__ import annotations

import bootstack as bs
from bootstack.dialogs import FormDialog

OPTIONS = [("One", 1), ("Two", 2), ("Three", 3)]
lines: list[str] = []


def item():
    """A fresh FieldItem per form — the same object must not be shared."""
    return bs.FieldItem(key="k", label="K", editor="select",
                        editor_options={"options": OPTIONS})


def describe(label: str, form_impl) -> None:
    widget = form_impl._widgets.get("k")
    lines.append(f"\n  {label}")
    lines.append(f"    editor class      : {type(widget).__name__}")
    lines.append(f"    widget.options    : {getattr(widget, 'options', '<none>')!r}")

    stored = form_impl._items_by_key.get("k")
    lines.append(f"    item.dtype        : {getattr(stored, 'dtype', '<no item>')!r}")

    # Pick by TEXT, which is what choosing from the dropdown amounts to.
    try:
        widget.value = "One"
    except Exception as exc:  # noqa: BLE001 - report, never raise
        lines.append(f"    set value='One'   : <raised {type(exc).__name__}: {exc}>")
    lines.append(f"    widget.value      : {getattr(widget, 'value', '<none>')!r}")
    lines.append(f"    form.get()['k']   : {form_impl.get().get('k')!r}")
    lines.append(f"    form.data['k']    : {form_impl.data.get('k')!r}")

    # And by VALUE, the way form.set() does it.
    try:
        form_impl.set({"k": 2})
        lines.append(f"    after set(k=2)    : {form_impl.get().get('k')!r}")
    except Exception as exc:  # noqa: BLE001
        lines.append(f"    set(k=2)          : <raised {type(exc).__name__}: {exc}>")


with bs.App(title="#428", size=(560, 320), padding=12) as app:

    public_form = bs.Form(items=[item()])
    app.tk.update_idletasks()
    describe("bs.Form (works per the report)", public_form._internal)

    dlg = FormDialog(items=[item()])
    impl = dlg._internal
    lines.append(f"\n  impl class          : {type(impl).__name__}")
    host = bs.Column()
    app.tk.update_idletasks()
    try:
        impl._build_form_content(host._internal)
        app.tk.update_idletasks()
        describe("FormDialog (reported wrong)", impl.form)
    except Exception as exc:  # noqa: BLE001
        lines.append(f"  build RAISED {type(exc).__name__}: {exc}")

    # --- The decisive arm ---------------------------------------------
    # `FormDialog.show()` reads `form.data` AFTER its wait loop returns, i.e.
    # after the window is gone. `_read_value_from_widget` falls back to
    # `self._variables[key].get()` when `widget.value` raises - and that
    # variable holds the DISPLAY TEXT. Nothing above destroys anything, which
    # is why everything above agrees.
    #
    # This has to run in the SAME app: a second `bs.App` in one process dies
    # with `Layout bs[...].Default.TField not found`, because the first root
    # took the styles with it.
    lines.append("\n  === reading form.data AFTER the widgets are destroyed ===")
    try:
        lines.append(f"    before destroy    : {impl.form.data.get('k')!r}")
        has_var = "k" in impl.form._variables
        lines.append(f"    _variables has k  : {has_var}")
        if has_var:
            lines.append(f"    variable holds    : {impl.form._variables['k'].get()!r}")
        host._internal.destroy()
        app.tk.update_idletasks()
        try:
            after = impl.form.data.get("k")
            lines.append(f"    AFTER destroy     : {after!r}   <-- what show() reads")
        except Exception as exc:  # noqa: BLE001
            lines.append(f"    AFTER destroy     : RAISED {type(exc).__name__}: {exc}")
    except Exception as exc:  # noqa: BLE001
        lines.append(f"    destroy arm RAISED {type(exc).__name__}: {exc}")

    app.tk.after(300, app.close)

app.run()

print(f"options passed: {OPTIONS}")
print("\n".join(lines))
