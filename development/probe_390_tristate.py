"""Does a tristate Checkbox's indeterminate state reach a bound Signal?"""
import os
import bootstack as bs

print("provenance:", os.path.dirname(bs.__file__))
app = bs.App(title="tri")

print("== tristate checkbox, no signal ==")
c = bs.Checkbox("Agree", tristate=True, parent=app)
app.tk.update()
print("start           value=%r checked=%r" % (c.value, c.checked))
c.value = True
print("value=True      value=%r" % (c.value,))
c.value = None
print("value=None      value=%r  (indeterminate)" % (c.value,))

print()
print("== tristate checkbox bound to a Signal ==")
sig = bs.Signal(False)
c2 = bs.Checkbox("Agree", tristate=True, signal=sig, parent=app)
app.tk.update()
seen = []
sig.subscribe(lambda v: seen.append(v))
print("realized=%s var=%s" % (sig._var is not None, type(sig._var).__name__ if sig._var else None))
c2.value = True
app.tk.update()
print("value=True      widget=%-6r signal=%r" % (c2.value, sig()))
c2.value = None
app.tk.update()
print("value=None      widget=%-6r signal=%r   <-- the two surfaces" % (c2.value, sig()))
print("subscriber saw:", seen)

print()
print("== can the signal drive it back to indeterminate? ==")
try:
    sig.set(None)
    print("sig.set(None) -> widget=%r" % (c2.value,))
except Exception as e:
    print("sig.set(None) RAISES %s: %s" % (type(e).__name__, str(e)[:70]))

print()
print("== what a nullable signal does here ==")
try:
    c3 = bs.Checkbox("Agree", tristate=True, signal=bs.Signal(False, nullable=True), parent=app)
    print("built OK, value=%r" % (c3.value,))
except Exception as e:
    print("RAISES %s: %s" % (type(e).__name__, str(e)[:70]))

app.tk.destroy()
