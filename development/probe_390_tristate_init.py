"""Tristate is a STARTING state. Does it survive being bound to a signal?"""
import os
import bootstack as bs

print("provenance:", os.path.dirname(bs.__file__))
app = bs.App(title="tri2")

print("== no signal ==")
print("tristate, no value            value=%r" % bs.Checkbox("A", tristate=True, parent=app).value)
print("tristate, value=True          value=%r" % bs.Checkbox("A", tristate=True, value=True, parent=app).value)

print()
print("== with a signal (the seed branch runs only when signal is None) ==")
for seed in (False, True):
    s = bs.Signal(seed)
    c = bs.Checkbox("A", tristate=True, signal=s, parent=app)
    app.tk.update()
    print("tristate, signal=Signal(%-5r)  value=%r signal=%r" % (seed, c.value, s()))

print()
print("== can a CLICK return it to indeterminate? ==")
c = bs.Checkbox("A", tristate=True, parent=app)
app.tk.update()
print("start                         value=%r" % (c.value,))
for i in range(3):
    c._internal.invoke()
    app.tk.update()
    print("after click %d                 value=%r" % (i + 1, c.value))

app.tk.destroy()
