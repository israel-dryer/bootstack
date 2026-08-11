"""Does a Signal bound into dialog content survive the dialog's teardown?

The Dialog page teaches reading a value after `show()` returns. Everything the
builder created is destroyed by then, so the value has to live somewhere else.
This checks whether a Signal is that somewhere -- and pairs it with a control
showing the widget read that the docs used to teach.

Run: py -3.13 development/probe_437_signal_outlives_dialog.py
"""

import bootstack as bs

app = bs.App(title="probe", size=(320, 120))

name = bs.Signal("")
holder = {}

with bs.Column(parent=app):
    holder["field"] = bs.TextField(textsignal=name)

field = holder["field"]
field.value = "Apollo"

print("while alive: signal=%r  widget=%r" % (name(), field.value))

# Tear the content down the way a dialog does when it closes.
field.tk.destroy()

print("after destroy: signal=%r" % (name(),))

try:
    print("after destroy: widget=%r" % (field.value,))
except Exception as exc:
    print("after destroy: widget read raised %s: %s" % (type(exc).__name__, exc))

# Control: a TextField is backed by a Tk string variable, so reading it after
# destroy happens to keep working -- which is what makes the pattern look sound
# on the one widget the docs used. A Select is not, so the same read fails.
print()
sig = bs.Signal("b")
holder2 = {}
with bs.Column(parent=app):
    holder2["sel"] = bs.Select(options=[("A", "a"), ("B", "b")], signal=sig)

sel = holder2["sel"]
print("while alive: signal=%r  widget=%r" % (sig(), sel.value))

sel.tk.destroy()

print("after destroy: signal=%r" % (sig(),))
try:
    print("after destroy: widget=%r" % (sel.value,))
except Exception as exc:
    print("after destroy: widget read raised %s: %s" % (type(exc).__name__, exc))

app.tk.destroy()
