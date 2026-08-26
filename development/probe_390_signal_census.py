"""Every public widget accepting signal=/textsignal=: does it REALIZE the signal?

Realized  -> the Signal IS the widget's Tk variable; None corrupts or raises.
Unrealized-> the binding syncs in pure Python; None is free.
"""
import inspect
import os

import bootstack as bs

print("provenance:", os.path.dirname(bs.__file__))

rows = []
for name in sorted(bs.__all__):
    obj = getattr(bs, name)
    if not inspect.isclass(obj):
        continue
    try:
        params = inspect.signature(obj.__init__).parameters
    except (ValueError, TypeError):
        continue
    kws = [k for k in ("signal", "textsignal") if k in params]
    if kws:
        rows.append((name, kws))

print("public widgets taking a signal: %d" % len(rows))
print()
print("%-16s %-12s %-10s %s" % ("widget", "keyword", "realizes?", "var type"))
print("-" * 60)

app = bs.App(title="census")
EXTRA = {
    "Select": {"options": [("One", "1")]},
    "SelectButton": {"options": [("One", "1")]},
    "RadioGroup": {"options": [("a", "a")]},
    "ToggleGroup": {"options": [("a", "a")]},
    "Checkbox": {"label": "x"},
    "Switch": {"label": "x"},
    "ToggleButton": {"text": "x"},
}
SEED = {"signal": "a", "textsignal": "a"}
NUMERIC = {"Slider", "RangeSlider", "ProgressBar", "Gauge", "NumberField", "SpinnerField"}
BOOL = {"Checkbox", "Switch", "ToggleButton"}

for name, kws in rows:
    cls = getattr(bs, name)
    for kw in kws:
        seed = 0.0 if name in NUMERIC else (False if name in BOOL else "a")
        sig = bs.Signal(seed)
        kwargs = dict(EXTRA.get(name, {}))
        kwargs[kw] = sig
        kwargs["parent"] = app
        try:
            cls(**kwargs)
            app.tk.update()
            realized = sig._var is not None
            vt = type(sig._var).__name__ if realized else "-"
            print("%-16s %-12s %-10s %s" % (name, kw, "YES" if realized else "no", vt))
        except Exception as e:
            print("%-16s %-12s %-10s %s: %s" % (name, kw, "?", type(e).__name__, str(e)[:34]))

app.tk.destroy()
