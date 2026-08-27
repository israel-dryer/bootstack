"""Round 1, part b: signal -> field clear for all five, plus mis-binding messages."""
import os
from datetime import date, time

import bootstack as bs

print("provenance:", os.path.dirname(bs.__file__))
app = bs.App(title="p390b")

print("== signal.set(None) clears the field, all five ==")
cases = [
    ("NumberField", lambda s: bs.NumberField(signal=s, parent=app), 5),
    ("DateField", lambda s: bs.DateField(signal=s, parent=app), date(2024, 5, 5)),
    ("TimeField", lambda s: bs.TimeField(signal=s, parent=app), time(9, 30)),
    ("Select", lambda s: bs.Select(options=[("One", "1"), ("Two", "2")], signal=s, parent=app), "1"),
    ("SelectButton", lambda s: bs.SelectButton(options=[("One", "1"), ("Two", "2")], signal=s, parent=app), "1"),
]
for name, build, seed in cases:
    sig = bs.Signal(seed, nullable=True)
    w = build(sig)
    app.tk.update()
    before = w.value
    try:
        sig.set(None)
        app.tk.update()
        print("%-14s before=%-12r after=%-8r text=%r" % (name, before, w.value, getattr(w, "text", "<none>")))
    except Exception as e:
        print("%-14s RAISES %s: %s" % (name, type(e).__name__, e))

print()
print("== mis-binding a nullable signal ==")
mis = [
    ("Slider(signal=)", lambda s: bs.Slider(signal=s, parent=app)),
    ("Label(text=)", lambda s: bs.Label(text=s, parent=app)),
    ("Label(textsignal=)", lambda s: bs.Label(textsignal=s, parent=app)),
    ("RadioGroup(signal=)", lambda s: bs.RadioGroup(options=[("a", "a")], signal=s, parent=app)),
]
for name, build in mis:
    sig = bs.Signal(0.0, nullable=True)
    try:
        build(sig)
        app.tk.update()
        print("%-22s built OK (realized=%s)" % (name, sig._var is not None))
    except Exception as e:
        print("%-22s %s: %s" % (name, type(e).__name__, str(e)[:90]))

app.tk.destroy()
