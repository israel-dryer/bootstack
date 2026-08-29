"""Does the FRAMEWORK itself call the 'manual' trigger from inside a Tk dispatch?

form.validate() -> entry.validate(..., trigger='manual') (form.py:351), and
FormDialog's button handler calls form.validate() (formdialog.py:552). So the
issue's premise -- "the manual path is fine, the caller catches it" -- has at
least one framework-internal caller with no author call site.
"""
import pathlib
import bootstack as bs

src = pathlib.Path(bs.__file__).parent / "validation" / "validation_rules.py"
print("ARM:", "BRANCH" if "custom validation rule raised" in src.read_text() else "MAIN")

app = bs.App(title="p", size=(300, 200))
with app:
    form = bs.Form(items=[{"key": "n", "label": "N", "editor": "text"}])
form.field("n").add_validation_rule("custom", func=lambda v: v > 5, message="must exceed 5")
try:
    print("  form.validate() ->", form.validate())
except Exception as e:
    print("  form.validate() RAISED:", type(e).__name__, e)
print("  form.valid ->", form.valid())
app.tk.destroy() if hasattr(app, "tk") else None
