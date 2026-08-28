"""#444 -- the issue's own reproduction, run against the fix. ASCII only."""
import tkinter as tk
import bootstack as bs

with bs.App(title="app") as app:
    pass
root = app.tk

def who():
    g = root.grab_current()
    if g is None:
        return (None, None)
    try:
        return (str(g), g.grab_status())
    except Exception:
        return (str(g), "?")

outer = tk.Toplevel(root); outer.geometry("240x120+80+80"); outer.update()
outer.grab_set()
print("  outer holds grab:      ", who())

inner = bs.Window(title="inner", modal=True, parent=outer)
inner.show()
root.update()
print("  inner holds grab:      ", who())

inner.close()
root.update()
print("  after inner closed:    ", who())
print("  outer still holds grab:", root.grab_current() is outer)

outer.destroy()
app.destroy()
