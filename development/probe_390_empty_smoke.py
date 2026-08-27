"""#390 -- smoke the allow_empty design across the three census groups."""
import os
from datetime import date
import bootstack as bs

print("provenance:", os.path.dirname(bs.__file__))
print()

with bs.App(title="probe") as app:
    print("-- group 1: pure-Python value-space bindings --")
    s = bs.Signal(date(2024, 5, 5), allow_empty=True)
    f = bs.DateField(signal=s)
    seen = []
    s.subscribe(seen.append)
    f.value = None
    print(f"   DateField cleared    field={f.value!r} sig={s()!r} saw={seen!r} realized={s._var is not None}")
    s2 = bs.Signal(date(2024, 5, 5), allow_empty=True)
    f2 = bs.DateField(signal=s2)
    s2.clear()
    print(f"   signal.clear()       field={f2.value!r} sig={s2()!r}")

    print()
    print("-- group 2: realized StringVar bindings (the widening) --")
    t = bs.Signal("hello", allow_empty=True)
    tf = bs.TextField(textsignal=t)
    tseen = []
    t.subscribe(tseen.append)
    t.clear()
    raw = app.tk.getvar(str(t._var))
    print(f"   TextField clear()    field={tf.value!r} sig={t()!r} raw_var={raw!r} saw={tseen!r}")
    t.set(None)
    print(f"   set(None) normalizes sig={t()!r}")

    r = bs.Signal("a", allow_empty=True)
    rg = bs.RadioGroup(options=[("a", "Apple"), ("b", "Banana")], signal=r)
    r.clear()
    print(f"   RadioGroup clear()   value={rg.value!r}")

    lsig = bs.Signal(None, allow_empty=True, dtype=str)
    lb = bs.Label(textsignal=lsig)
    print(f"   Label seeded empty   text={lb.text!r} raw_var={app.tk.getvar(str(lsig._var))!r}")

    print()
    print("-- group 3: the floor -- no empty member --")
    for label, seed, build in (
        ("Checkbox", False, lambda s: bs.Checkbox("Agree", signal=s)),
        ("Slider", 0.0, lambda s: bs.Slider(signal=s)),
    ):
        try:
            build(bs.Signal(seed, allow_empty=True))
            print(f"   {label:10} NO RAISE  <- wrong")
        except Exception as exc:
            print(f"   {label:10} {type(exc).__name__}: {str(exc)[:90]}...")

    print()
    print("-- clear() requires the declaration, whatever the type --")
    for label, seed in (("Signal('x')", "x"), ("Signal(date)", date(2024, 5, 5))):
        try:
            bs.Signal(seed).clear()
            print(f"   {label:14} NO RAISE  <- wrong")
        except TypeError as exc:
            print(f"   {label:14} TypeError: {exc}")

    print()
    print("-- the binding decides the empty, not the type (both str) --")
    a = bs.Signal("hello", allow_empty=True)
    bs.TextField(textsignal=a)
    a.clear()
    b_ = bs.Signal("1", allow_empty=True)
    sel = bs.Select(options=[("One", "1"), ("Two", "2")], signal=b_)
    b_.clear()
    print(f"   TextField signal  realized={a._var is not None}  clear -> {a()!r}")
    print(f"   Select signal     realized={b_._var is not None}  clear -> {b_()!r}  widget={sel.value!r}")
