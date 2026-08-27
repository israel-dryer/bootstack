"""#390 -- could a nullable text signal ride OBJECT MODE, keeping None in Python
while the var carries '' as a display shadow?

Object mode makes __call__ return _last (signal.py:188), which is what would let
None round-trip.  The question is whether the WIDGET->SIGNAL direction survives:
the trace at signal.py:170 only writes _last back when NOT in object mode.
"""
import os
import bootstack as bs

print("provenance:", os.path.dirname(bs.__file__))
print()

with bs.App(title="probe") as app:
    print("-- control: normal native-mode str signal on a TextField --")
    a = bs.Signal("seed")
    ta = bs.TextField(textsignal=a)
    seen_a = []
    a.subscribe(seen_a.append)
    a._var.set("typed by the user")          # what a keystroke does
    print(f"   object_mode={a._object_mode}  call={a()!r}  saw={seen_a!r}")

    print()
    print("-- arm: same binding, forced into object mode --")
    b = bs.Signal("seed")
    tb = bs.TextField(textsignal=b)
    b._object_mode = True                    # the hypothetical nullable-text design
    seen_b = []
    b.subscribe(seen_b.append)
    b._var.set("typed by the user")          # the identical keystroke
    print(f"   object_mode={b._object_mode}  call={b()!r}  saw={seen_b!r}")
    print(f"   widget shows={tb.value!r}")
