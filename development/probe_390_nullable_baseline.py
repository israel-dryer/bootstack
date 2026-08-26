"""Baseline for #390 — what a Signal does around None today, measured on this box.

Run on `main` (or the branch before any src change). ASCII only.
"""
from datetime import date
import tkinter as tk

import bootstack as bs


def show(label, fn):
    try:
        print(f"{label:<42} {fn()!r}")
    except Exception as e:
        print(f"{label:<42} RAISES {type(e).__name__}: {e}")


app = bs.App(title="p390")
app.__enter__()

print("--- the guard ---")
show("Signal(date).set(None)", lambda: bs.Signal(date(2024, 5, 5)).set(None))
show("Signal(0).set(None)", lambda: bs.Signal(0).set(None))
show("Signal('').set(None)", lambda: bs.Signal("").set(None))
show("Signal(None) constructs, type is", lambda: bs.Signal(None).type)

print()
print("--- realization: which bindings touch .var ---")
rows = [
    ("NumberField(signal=)", lambda s: bs.NumberField(signal=s, parent=app), bs.Signal(1)),
    ("DateField(signal=)", lambda s: bs.DateField(signal=s, parent=app), bs.Signal(date(2024, 5, 5))),
    ("Checkbox(signal=)", lambda s: bs.Checkbox("x", signal=s, parent=app), bs.Signal(False)),
    ("TextField(textsignal=)", lambda s: bs.TextField(textsignal=s, parent=app), bs.Signal("hi")),
]
for label, build, sig in rows:
    build(sig)
    app.tk.update()
    print(f"{label:<42} realized={sig._var is not None}  object_mode={sig._object_mode}")

print()
print("--- the stale-signal regression (value-space field cleared) ---")
sig = bs.Signal(date(2024, 5, 5))
fld = bs.DateField(signal=sig, parent=app)
app.tk.update()
seen = []
sig.subscribe(lambda v: seen.append(v))
fld.value = None
app.tk.update()
print(f"{'DateField cleared -> field/signal':<42} field={fld.value!r} signal={sig()!r} subscribers_saw={seen}")

print()
print("--- what a raw StringVar does with None (the corruption path) ---")
v = tk.StringVar(master=app.tk, value="hi")
v.set(None)
print(f"{'StringVar.set(None) -> contents':<42} {v.get()!r}")
show("IntVar.set(None)", lambda: tk.IntVar(master=app.tk, value=1).set(None))

print()
print("--- map() over a None-producing transform ---")
s = bs.Signal(date(2024, 5, 5))
guarded = s.map(lambda d: d.strftime("%B %d, %Y") if d else "")
print(f"{'guarded map, derived type':<42} {guarded.type.__name__} value={guarded()!r}")
show("unguarded map over None seed", lambda: bs.Signal(None).map(lambda d: d.strftime("%b")))
