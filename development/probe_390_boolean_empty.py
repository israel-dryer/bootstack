"""#390 -- does a BOOLEAN empty make sense, or is it genuinely not supported?

The framework already ships a third boolean state: Checkbox(tristate=True)
reports indeterminate as .value is None.  So the question is not whether bool
needs an empty -- it is whether the SIGNAL binding can carry the one that
already exists.

Arm 1  which boolean widgets even have a third state?
Arm 2  where does a tristate Checkbox actually keep 'indeterminate'?
Arm 3  what does a tristate Checkbox + signal do today?
"""
import os
import tkinter as tk
from tkinter import ttk
import bootstack as bs

print("provenance:", os.path.dirname(bs.__file__))
print()

with bs.App(title="probe") as app:
    print("-- arm 1: which boolean widgets accept tristate= ? --")
    for name, build in (
        ("Checkbox", lambda: bs.Checkbox("A", tristate=True)),
        ("Switch", lambda: bs.Switch("A", tristate=True)),
        ("ToggleButton", lambda: bs.ToggleButton("A", tristate=True)),
    ):
        try:
            w = build()
            print(f"   {name:14} accepted    value={w.value!r}")
        except Exception as exc:
            print(f"   {name:14} {type(exc).__name__}: {str(exc)[:70]}")

    print()
    print("-- arm 2: where is 'indeterminate' stored? --")
    cb = bs.Checkbox("A", tristate=True)
    inner = cb._internal
    var = inner.cget("variable")
    for want in (True, None, False):
        cb.value = want
        raw = app.tk.getvar(var) if var else "-"
        alt = inner.instate(["alternate"])
        print(f"   set {str(want):5} -> value={cb.value!r:5} var={raw!r:7} ttk 'alternate' state={alt}")

    print()
    print("   ttk Checkbutton options containing 'tri':",
          [o for o in ttk.Checkbutton(app.tk).keys() if "tri" in o])

    print()
    print("-- arm 3: tristate Checkbox + signal, today --")
    sig = bs.Signal(False)
    box = bs.Checkbox("A", tristate=True, signal=sig)
    seen = []
    sig.subscribe(seen.append)
    for want in (True, None):
        box.value = want
        print(f"   set {str(want):5} -> widget={box.value!r:5} signal={sig()!r:5} subscriber_saw={seen!r}")
