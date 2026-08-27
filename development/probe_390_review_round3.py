"""#390 round 3 -- verify the round 2 surface by construction.

One arm per candidate. Each prints HOLDS (the concern is real) or REFUTED.
ASCII only. Run: py -3.12 development/probe_390_review_round3.py
"""
import datetime as _dt
import enum
import tkinter as tk
import bootstack as bs
from bootstack.signals.signal import Signal

def hdr(n, t):
    print("\n" + "=" * 70)
    print("ARM %s -- %s" % (n, t))
    print("=" * 70)

# ---------------------------------------------------------------- A
hdr("A", "a set-typed signal that STARTS empty reads None, but clear() gives set()")
sig = Signal(None, allow_empty=True, dtype=set)
seeded_empty = sig()
sig2 = Signal({"a"}, allow_empty=True, dtype=set)
sig2.clear()
cleared_empty = sig2()
print("  starts-empty  sig() =", repr(seeded_empty), " type =", sig.type.__name__)
print("  cleared       sig() =", repr(cleared_empty))
print("  VERDICT:", "HOLDS -- two spellings of the same empty" if seeded_empty != cleared_empty else "REFUTED")

# ---------------------------------------------------------------- B
hdr("B", "a str-typed signal that STARTS empty reads None before a binding")
s = Signal(None, allow_empty=True, dtype=str)
before = s()
print("  before bind sig() =", repr(before))
with bs.App(title="B") as app:
    f = bs.TextField(textsignal=s)
after = s()
print("  after bind  sig() =", repr(after), " entry shows", repr(f.tk.get()))
app.destroy()
print("  VERDICT:", "HOLDS -- realization changes the read" if before != after else "REFUTED")

# ---------------------------------------------------------------- C
hdr("C", "the use case #390 exists for -- an empty NumberField/DateField binding")
n = Signal(None, allow_empty=True, dtype=int)
d = Signal(None, allow_empty=True, dtype=_dt.date)
with bs.App(title="C") as app:
    nf = bs.NumberField(signal=n)
    df = bs.DateField(signal=d)
print("  NumberField value =", repr(nf.value), " signal =", repr(n()), " realized =", n._var is not None)
print("  DateField   value =", repr(df.value), " signal =", repr(d()), " realized =", d._var is not None)
n.set(5)
print("  after n.set(5): field =", repr(nf.value), " signal =", repr(n()))
n.clear()
print("  after n.clear(): field =", repr(nf.value), " signal =", repr(n()))
app.destroy()

# ---------------------------------------------------------------- D
hdr("D", "declared IntEnum dtype is refused at the binding (1040a62d)")
class Color(enum.IntEnum):
    RED = 1
c = Signal(None, allow_empty=True, dtype=Color)
try:
    with bs.App(title="D") as app:
        bs.Slider(signal=c)
    print("  BUILT -- sig() =", repr(c()))
    app.destroy()
    print("  VERDICT: HOLDS -- guard bypassed")
except Exception as e:
    try:
        app.destroy()
    except Exception:
        pass
    print("  raised %s: %s" % (type(e).__name__, str(e)[:90]))
    print("  VERDICT: REFUTED -- guard holds")

# ---------------------------------------------------------------- E
hdr("E", "doubt 5 -- a float seed refuses on a TEXT field where a str seed accepts")
for seed, label in ((1.0, "float seed"), ("1.0", "str seed")):
    sg = Signal(seed, allow_empty=True)
    try:
        with bs.App(title="E") as app:
            bs.SpinnerField(textsignal=sg)
        print("  %-11s ACCEPTED  var=%s" % (label, type(sg._var).__name__))
        app.destroy()
    except Exception as e:
        try:
            app.destroy()
        except Exception:
            pass
        print("  %-11s REFUSED   %s" % (label, type(e).__name__))

# ---------------------------------------------------------------- F
hdr("F", "doubt 6 -- from_variable forces allows_empty False")
root = tk.Tk(); root.withdraw()
v = tk.StringVar(master=root, value="x")
fv = Signal.from_variable(v)
print("  allows_empty =", fv.allows_empty)
try:
    fv.clear()
    print("  clear() OK -> ", repr(fv()))
    print("  VERDICT: REFUTED")
except Exception as e:
    print("  clear() raised %s: %s" % (type(e).__name__, str(e)[:80]))
    print("  VERDICT: HOLDS -- a widget-owned StringVar CAN hold '' but the signal refuses")
root.destroy()

# ---------------------------------------------------------------- G
hdr("G", "accept-parity: does the constructor accept what set() accepts, and vice versa")
cases = [
    ("int into float", float, 5),
    ("bool into int", int, True),
    ("str into str", str, "x"),
    ("float into int", int, 1.5),
]
for label, dt, val in cases:
    try:
        Signal(val, dtype=dt)
        ctor = "accept"
    except Exception as e:
        ctor = type(e).__name__
    base = {float: 0.0, int: 0, str: ""}[dt]
    sg = Signal(base)
    try:
        sg.set(val)
        st = "accept"
    except Exception as e:
        st = type(e).__name__
    flag = "" if ctor == st else "   <-- DRIFT"
    print("  %-16s ctor=%-10s set()=%-10s%s" % (label, ctor, st, flag))
