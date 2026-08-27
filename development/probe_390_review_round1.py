"""Round 1 review probe for #390 (nullable Signals).

Arms, all ASCII output:
  A  the two selection widgets named in the docs and in the error message -
     Select and SelectButton - against a nullable signal.
  B  Signal(None) WITHOUT nullable: what set(None) does. The plan claims this
     is "left exactly as it is". Run on both arms to check.
  C  map() over a nullable source, including the identity transform.
  D  does a value-space binding realize the signal (a nullable one raises).
"""
import os
import sys
from datetime import date

import bootstack as bs
from bootstack.errors import BootstackError

print("provenance:", os.path.dirname(bs.__file__))
print("python    :", sys.version.split()[0])
print()


def show(label, fn):
    try:
        print("%-46s %s" % (label, fn()))
    except Exception as e:
        print("%-46s RAISES %s: %s" % (label, type(e).__name__, e))


# ---------------------------------------------------------------- arm B first
# (no App needed - pure Signal)
print("== arm B: Signal(None) without nullable ==")
show("Signal(None).type", lambda: bs.Signal(None).type)
show("Signal(None).set(None)", lambda: (bs.Signal(None).set(None), "no raise")[1])
show("Signal(None).set(5)", lambda: (bs.Signal(None).set(5), "no raise")[1])
print()

print("== arm C: map() ==")
src = bs.Signal(date(2024, 5, 5), nullable=True)
guarded = src.map(lambda d: d.strftime("%Y-%m-%d") if d else "")
show("guarded derived type", lambda: guarded.type)
show("source.set(None) with guarded derived", lambda: (src.set(None), guarded())[1])

src2 = bs.Signal(None, nullable=True)
ident = src2.map(lambda v: v)
show("identity derived over empty source: type", lambda: ident.type)
show("identity derived .nullable", lambda: ident.nullable)
show("then source.set(date(...))", lambda: (src2.set(date(2024, 1, 1)), ident())[1])

src3 = bs.Signal(date(2024, 5, 5), nullable=True)
ident3 = src3.map(lambda v: v)
show("identity derived over seeded source: type", lambda: ident3.type)
show("then source.set(None)", lambda: (src3.set(None), ident3())[1])
print()

# ------------------------------------------------------------------ arms A, D
app = bs.App(title="probe390")

print("== arm A: the selection widgets ==")
for name, build, seed, other in [
    ("Select", lambda s: bs.Select(options=[("One", "1"), ("Two", "2")], signal=s, parent=app), "1", "2"),
    ("SelectButton", lambda s: bs.SelectButton(options=[("One", "1"), ("Two", "2")], signal=s, parent=app), "1", "2"),
]:
    sig = bs.Signal(seed, nullable=True)
    try:
        w = build(sig)
    except Exception as e:
        print("%-14s build RAISES %s: %s" % (name, type(e).__name__, e))
        continue
    app.tk.update()
    seen = []
    sig.subscribe(lambda v: seen.append(v))
    try:
        w.value = None
    except Exception as e:
        print("%-14s value=None RAISES %s: %s" % (name, type(e).__name__, e))
        continue
    app.tk.update()
    print("%-14s widget=%-6r signal=%-6r subscriber_saw=%r"
          % (name, w.value, sig(), seen))

    # the other direction
    sig2 = bs.Signal(other, nullable=True)
    w2 = build(sig2)
    app.tk.update()
    sig2.set(None)
    app.tk.update()
    print("%-14s signal.set(None) -> widget=%r" % (name, w2.value))

print()
print("== arm D: does a value-space binding realize? ==")
for name, build in [
    ("NumberField", lambda s: bs.NumberField(signal=s, parent=app)),
    ("DateField", lambda s: bs.DateField(signal=s, parent=app)),
    ("TimeField", lambda s: bs.TimeField(signal=s, parent=app)),
    ("Select", lambda s: bs.Select(options=[("One", "1")], signal=s, parent=app)),
    ("SelectButton", lambda s: bs.SelectButton(options=[("One", "1")], signal=s, parent=app)),
]:
    sig = bs.Signal(None, nullable=True)
    try:
        build(sig)
        app.tk.update()
        print("%-14s bound, realized=%s" % (name, sig._var is not None))
    except Exception as e:
        print("%-14s RAISES %s: %s" % (name, type(e).__name__, e))

app.tk.destroy()
