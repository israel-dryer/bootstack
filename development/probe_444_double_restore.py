"""Does Dialog's own capture/restore now double up with Toplevel's? ASCII only."""
import tkinter as tk
import bootstack as bs
from bootstack._runtime import grab as grabmod

calls = []
_real = grabmod.restore_grab
def spy(prev):
    calls.append(prev)
    return _real(prev)
# Patch the names where they are BOUND, not where they are defined -- a
# `from x import y` copies the reference, so patching the source module is a
# no-op and reports 0 calls exactly the way a real absence would.
import bootstack._runtime.toplevel as topmod
import bootstack.dialogs._impl.dialog as dlgmod
topmod.restore_grab = spy
dlgmod.restore_grab = spy

with bs.App(title="a") as app:
    pass
root = app.tk
outer = tk.Toplevel(root); outer.geometry("200x100+90+90"); outer.update()
outer.grab_set()

def who():
    g = root.grab_current()
    return (str(g), g.grab_status()) if g is not None else (None, None)

print("  before:", who())
w = bs.Window(title="w", modal=True, parent=outer)
w.show(); root.update(); w.close(); root.update()
print("  after :", who())
print("  restore_grab called %d time(s)" % len(calls))
print("  tokens:", [(str(t[0]) if t else None) for t in calls])
outer.destroy(); app.destroy()

print()
print("  CONTROL -- the spy must be able to see a call at all:")
calls.clear()
topmod.restore_grab(None)
print("    direct call seen:", len(calls) == 1)
