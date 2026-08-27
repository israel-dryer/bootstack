"""#483 baseline -- a tristate Checkbox bound to a Signal, measured on main.

Rescued 2026-08-27 from a dead session's temp worktree, where it was the only
copy. Round 1 of #390 used it to establish that tristate + signal= misreports
BEFORE this branch existed, which is what makes #483 pre-existing rather than
something the allow_empty work introduced.
"""
import os
import bootstack as bs
print("provenance:", os.path.dirname(bs.__file__))
app = bs.App(title="trib")
print("tristate, no signal            value=%r" % bs.Checkbox("A", tristate=True, parent=app).value)
print("tristate, value=None           value=%r" % bs.Checkbox("A", tristate=True, value=None, parent=app).value)
for seed in (False, True):
    s = bs.Signal(seed)
    c = bs.Checkbox("A", tristate=True, signal=s, parent=app)
    app.tk.update()
    print("tristate, signal=Signal(%-5r) value=%r" % (seed, c.value))
s = bs.Signal(False)
c = bs.Checkbox("A", tristate=True, value=None, signal=s, parent=app)
app.tk.update()
print("tristate, value=None + signal  value=%r  (value= ignored when signal= passed)" % (c.value,))
app.tk.destroy()
