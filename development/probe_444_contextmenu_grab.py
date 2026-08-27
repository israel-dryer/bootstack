"""Sibling check: does ContextMenu.show()'s grab_release drop an outer grab?

contextmenu.py:1423 releases outright rather than handing back. That is the
canonical tk_popup idiom, so this measures rather than assumes. ASCII only.
"""
import tkinter as tk
from tkinter import TclError

root = tk.Tk(); root.withdraw()

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
print("  outer holds:                ", who())

# Reproduce the show() shape without posting a real menu (tk_popup blocks on a
# real grab), so this isolates the grab_release half exactly as shipped.
menu = tk.Menu(root, tearoff=0)
menu.add_command(label="x")
try:
    menu.grab_release()
except TclError:
    pass
print("  after menu.grab_release():  ", who())

released = root.grab_current() is None
print()
print("  VERDICT:", "SIBLING DEFECT -- the outer grab was dropped" if released
      else "NOT A DEFECT -- grab_release on the menu left the outer grab alone")
outer.destroy(); root.destroy()
