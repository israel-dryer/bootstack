"""#390 -- classify every public widget that takes a signal, at the SHIPPED commit.

Three groups the plan predicted: pure-Python bindings accept, StringVar-backed
bindings accept (the widening), BooleanVar/DoubleVar-backed bindings refuse.
Measured by construction, not read from source.
"""
import os
from datetime import date, time
import bootstack as bs
from bootstack.errors import BootstackError

print("provenance:", os.path.dirname(bs.__file__))
print()

OPTS = [("One", "1"), ("Two", "2")]
CASES = [
    ("Button",        "textsignal", "hi",   lambda s, p: bs.Button("Go", textsignal=s, parent=p)),
    ("Checkbox",      "signal",     False,  lambda s, p: bs.Checkbox("A", signal=s, parent=p)),
    ("CodeEditor",    "textsignal", "hi",   lambda s, p: bs.CodeEditor(textsignal=s, parent=p)),
    ("DateField",     "signal",     date(2024, 5, 5), lambda s, p: bs.DateField(signal=s, parent=p)),
    ("Label",         "textsignal", "hi",   lambda s, p: bs.Label(textsignal=s, parent=p)),
    ("MenuButton",    "textsignal", "hi",   lambda s, p: bs.MenuButton(textsignal=s, parent=p)),
    ("NumberField",   "signal",     5,      lambda s, p: bs.NumberField(signal=s, parent=p)),
    ("PasswordField", "textsignal", "hi",   lambda s, p: bs.PasswordField(textsignal=s, parent=p)),
    ("PathField",     "textsignal", "hi",   lambda s, p: bs.PathField(textsignal=s, parent=p)),
    ("ProgressBar",   "signal",     0.0,    lambda s, p: bs.ProgressBar(signal=s, parent=p)),
    ("Radio",         "signal",     "a",    lambda s, p: bs.Radio("A", value="a", signal=s, parent=p)),
    ("RadioGroup",    "signal",     "a",    lambda s, p: bs.RadioGroup(options=[("a", "A")], signal=s, parent=p)),
    ("Select",        "signal",     "1",    lambda s, p: bs.Select(options=OPTS, signal=s, parent=p)),
    ("SelectButton",  "signal",     "1",    lambda s, p: bs.SelectButton(options=OPTS, signal=s, parent=p)),
    ("RadioToggleButton", "signal", "a", lambda s, p: bs.RadioToggleButton("A", value="a", signal=s, parent=p)),
    ("SpinnerField",  "textsignal", "hi",   lambda s, p: bs.SpinnerField(textsignal=s, parent=p)),
    ("SpinnerField/f","textsignal", 1.0,    lambda s, p: bs.SpinnerField(textsignal=s, parent=p)),
    ("Chart",         "signal",     "hi",   lambda s, p: bs.Chart(signal=s, render=lambda *a: None, parent=p)),
    ("Slider",        "signal",     0.0,    lambda s, p: bs.Slider(signal=s, parent=p)),
    ("Switch",        "signal",     False,  lambda s, p: bs.Switch("A", signal=s, parent=p)),
    ("TextArea",      "textsignal", "hi",   lambda s, p: bs.TextArea(textsignal=s, parent=p)),
    ("TextField",     "textsignal", "hi",   lambda s, p: bs.TextField(textsignal=s, parent=p)),
    ("TimeField",     "signal",     time(9, 30), lambda s, p: bs.TimeField(signal=s, parent=p)),
    ("ToggleButton",  "signal",     False,  lambda s, p: bs.ToggleButton("A", signal=s, parent=p)),
    ("ToggleGroup",   "signal",     "a",    lambda s, p: bs.ToggleGroup(options=[("a", "A")], signal=s, parent=p)),
]

groups = {"accept, pure Python": [], "accept, StringVar": [], "REFUSE": [], "other": []}

with bs.App(title="probe") as app:
    print(f"{'widget':16} {'kw':11} {'binds?':8} {'var':11} empty")
    print("-" * 62)
    for name, kw, seed, build in CASES:
        sig = bs.Signal(seed, allow_empty=True)
        try:
            build(sig, app)
        except BootstackError as exc:
            groups["REFUSE"].append(name)
            print(f"{name:16} {kw:11} {'REFUSE':8} {'-':11} {str(exc)[60:78]}...")
            continue
        except Exception as exc:
            groups["other"].append(name)
            print(f"{name:16} {kw:11} {'?':8} {'-':11} {type(exc).__name__}")
            continue
        realized = sig._var is not None
        var = type(sig._var).__name__ if realized else "-"
        try:
            sig.clear()
            empty = repr(sig())
        except Exception as exc:
            empty = f"{type(exc).__name__}"
        groups["accept, StringVar" if realized else "accept, pure Python"].append(name)
        print(f"{name:16} {kw:11} {'accept':8} {var:11} {empty}")

print()
for k, v in groups.items():
    if v:
        print(f"{k:22} {len(v):2}  {', '.join(v)}")
