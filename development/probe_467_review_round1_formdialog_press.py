"""Is #467 reachable with the DEFAULT trigger, through a FormDialog submit?

`custom` defaults to trigger='manual', which is why the issue's own repro does
not fire. But `_accept_press` (formdialog.py:526) calls `self.form.validate()`,
and `Form.validate` passes trigger='manual' -- under which EVERY rule runs. So a
default-trigger custom rule does evaluate on a submit press, inside a Tk button
handler with no author call site to catch anything.

Drives `_accept_press` directly rather than pressing a real button: the press is
what we are asking about, not the modal loop.
"""
import pathlib
import bootstack as bs
from bootstack.dialogs import FormDialog

src = pathlib.Path(bs.__file__).parent / "validation" / "validation_rules.py"
print("ARM:", "BRANCH" if "custom validation rule raised" in src.read_text() else "MAIN")

app = bs.App(title="p", size=(320, 200))
dlg = FormDialog(title="Details", items=[{"key": "n", "label": "N", "editor": "text"}])
impl = dlg._internal

# The form is built by show(); build it directly into a plain frame so the press
# can be driven without entering the modal wait loop.
import tkinter
host = tkinter.Frame(app.tk.winfo_toplevel())
impl._build_form_content(host)
form = impl.form

form.field("n").add_validation_rule(
    "custom", func=lambda v: v > 5, message="must exceed 5"      # DEFAULT trigger
)
from bootstack.dialogs import DialogButton
btn = DialogButton(text="OK", role="primary", result="ok")
print("  pressing:", btn.role, btn.text)
try:
    accepted = impl._accept_press(btn)
    print("  _accept_press ->", accepted)
except Exception as exc:
    print("  _accept_press RAISED:", type(exc).__name__, exc)
print("  form.valid ->", form.valid())
