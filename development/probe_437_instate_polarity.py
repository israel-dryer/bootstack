"""What does `instate(['!disabled'])` return for each button state?

The guard has to stand down when a button HAS already handled the key, which is
the enabled case. So the question is which way `instate(['!disabled'])` reads.

Run: py -3.13 development/probe_437_instate_polarity.py
"""

import bootstack as bs

app = bs.App(title="probe", size=(320, 120))

with bs.Column(parent=app):
    btn = bs.Button("OK")

w = btn.tk

print("state            instate(['!disabled'])   not instate(['!disabled'])")
for label, setup in (("enabled", lambda: w.state(["!disabled"])),
                     ("disabled", lambda: w.state(["disabled"]))):
    setup()
    v = bool(w.instate(["!disabled"]))
    print("%-16s %-24s %s" % (label, v, not v))

print()
print("The guard must RETURN (stand down) only when the button already invoked,")
print("i.e. when it is ENABLED. That is instate(['!disabled']) == True.")
print("`not instate(['!disabled'])` is True for the DISABLED button instead --")
print("the opposite of the intent.")

app.tk.destroy()
