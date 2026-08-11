"""Run the Dialog page's refusal example verbatim, and check both of its arms.

The docs teach reading a Signal after `show()` returns. This drives the real
dialog: one refused press (empty field, dialog stays open, no result), then a
typed value and an accepted press, then the post-`show()` read.

Run: py -3.13 development/probe_437_doc_example_runs.py
"""

import bootstack as bs
from bootstack.dialogs import Dialog, DialogButton

app = bs.App(title="probe", size=(320, 120))

refusals = []

# --- the example, as the page prints it -------------------------------------
name = bs.Signal("")


def build():
    bs.Label("Project name")
    bs.TextField(textsignal=name)


def save(dlg):
    if not name():
        refusals.append("refused")
        return False        # refused: the dialog stays open


dlg = Dialog(
    title="New project",
    content_builder=build,
    buttons=[
        DialogButton("Save", role="primary", result="save", command=save, default=True),
        DialogButton("Cancel", role="cancel"),
    ],
)
# ----------------------------------------------------------------------------

state = {"open_after_refusal": None}


def find_save_button(top):
    stack = list(top.winfo_children())
    while stack:
        w = stack.pop()
        if w.winfo_class() == "TButton":
            try:
                if str(w.cget("text")) == "Save":
                    return w
            except Exception:
                pass
        stack.extend(w.winfo_children())
    return None


def drive():
    top = dlg._toplevel
    btn = find_save_button(top)
    print("found the Save button:", btn is not None)

    # Arm 1: press with the field empty. The command refuses.
    btn.invoke()
    state["open_after_refusal"] = bool(top.winfo_exists() and top.winfo_ismapped())
    print("after the refused press: dialog open=%s  result=%r"
          % (state["open_after_refusal"], dlg.result))

    # Arm 2: type a name, press again. This one is accepted and closes.
    name.set("Apollo")
    btn.invoke()


guard = app.tk.after(5000, lambda: dlg._toplevel.destroy())
try:
    app.tk.after(400, drive)
    dlg.show()
finally:
    app.tk.after_cancel(guard)

print("after show(): result=%r  signal=%r" % (dlg.result, name()))

ok = (
    refusals == ["refused"]
    and state["open_after_refusal"] is True
    and dlg.result == "save"
    and name() == "Apollo"
)
print("PASS" if ok else "FAIL")

app.tk.destroy()
