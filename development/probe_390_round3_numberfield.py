"""Round 3 -- why does an empty-seeded signal bound to a NumberField read 0?"""
import datetime as _dt
import bootstack as bs
from bootstack.signals.signal import Signal

print("=== control: unbound NumberField / DateField / TimeField defaults ===")
with bs.App(title="ctl") as app:
    print("  NumberField()  value =", repr(bs.NumberField().value))
    print("  DateField()    value =", repr(bs.DateField().value))
    print("  TimeField()    value =", repr(bs.TimeField().value))
    print("  Select()       value =", repr(bs.Select(options=["a", "b"]).value))
app.destroy()

print("\n=== an empty-seeded signal bound to each of the five ===")
specs = [
    ("NumberField", lambda s: bs.NumberField(signal=s), int),
    ("DateField", lambda s: bs.DateField(signal=s), _dt.date),
    ("TimeField", lambda s: bs.TimeField(signal=s), _dt.time),
    ("Select", lambda s: bs.Select(options=["a", "b"], signal=s), str),
    ("SelectButton", lambda s: bs.SelectButton(options=["a", "b"], signal=s), str),
]
with bs.App(title="x") as app:
    for label, build, dt in specs:
        sig = Signal(None, allow_empty=True, dtype=dt)
        w = build(sig)
        print("  %-13s widget.value=%-8r signal=%-8r  %s" % (
            label, w.value, sig(),
            "OK" if sig() is None else "SIGNAL CLOBBERED"))
app.destroy()

print("\n=== is it pre-existing? the same widget with an ORDINARY signal ===")
with bs.App(title="y") as app:
    s0 = Signal(0)
    nf = bs.NumberField(signal=s0)
    print("  NumberField(signal=Signal(0))   value=%r signal=%r" % (nf.value, s0()))
    s7 = Signal(7)
    nf7 = bs.NumberField(signal=s7)
    print("  NumberField(signal=Signal(7))   value=%r signal=%r" % (nf7.value, s7()))
app.destroy()

print("\n=== clearing AFTER the binding (the path #390 was moved for) ===")
with bs.App(title="z") as app:
    s = Signal(5, allow_empty=True, dtype=int)
    nf = bs.NumberField(signal=s)
    print("  seeded 5      value=%r signal=%r" % (nf.value, s()))
    s.clear()
    print("  after clear() value=%r signal=%r" % (nf.value, s()))
    nf.value = None
    print("  widget->None  value=%r signal=%r" % (nf.value, s()))
app.destroy()
