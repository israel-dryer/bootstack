"""Round 1, part c: the deferred-type path and the bind-time seeding asymmetry."""
import os
from datetime import date

import bootstack as bs

print("provenance:", os.path.dirname(bs.__file__))
app = bs.App(title="p390c")

print("== bind-time seeding: nullable signal holding None + a field WITH a value ==")
sig = bs.Signal(None, nullable=True)
f = bs.DateField(value=date(2024, 5, 5), signal=sig, parent=app)
app.tk.update()
print("field=%r  signal=%r   (signal's None did NOT clear the field)" % (f.value, sig()))

print()
print("== deferred type locked by the first value pushed from the field ==")
sig2 = bs.Signal(None, nullable=True)
n = bs.NumberField(signal=sig2, parent=app)
app.tk.update()
n.value = 5
app.tk.update()
print("after value=5      signal_type=%s signal=%r" % (sig2.type, sig2()))
n.value = 5.5
app.tk.update()
print("after value=5.5    signal_type=%s signal=%r  field=%r" % (sig2.type, sig2(), n.value))

print()
print("== control: the same with an int-seeded NON-nullable signal (pre-existing) ==")
sig3 = bs.Signal(0)
n3 = bs.NumberField(signal=sig3, parent=app)
app.tk.update()
n3.value = 5.5
app.tk.update()
print("after value=5.5    signal_type=%s signal=%r  field=%r" % (sig3.type, sig3(), n3.value))

print()
print("== deferred type: signal -> field after the type locks ==")
sig4 = bs.Signal(None, nullable=True)
d4 = bs.DateField(signal=sig4, parent=app)
app.tk.update()
sig4.set(date(2025, 1, 1))
app.tk.update()
print("signal.set(date) -> field=%r type=%s" % (d4.value, sig4.type))

app.tk.destroy()
