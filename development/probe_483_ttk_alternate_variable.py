"""Is indeterminate-not-in-the-variable ttk's behavior or bootstack's?
Plain tkinter/ttk only -- no bootstack. ASCII only."""
import tkinter as tk
from tkinter import ttk

root = tk.Tk(); root.withdraw()
v = tk.BooleanVar(master=root, value=False)
cb = ttk.Checkbutton(root, text="x", variable=v, onvalue=True, offvalue=False)
cb.pack(); root.update()

def row(label):
    print("  %-22s var.get()=%-6r raw=%-5r alternate=%-5s selected=%s" % (
        label, v.get(), root.getvar(str(v)), cb.instate(["alternate"]), cb.instate(["selected"])))

row("start (off)")
cb.state(["alternate"])          # the ONLY way ttk expresses indeterminate
root.update()
row("state(['alternate'])")

v.set(True); root.update()
row("var True")
cb.state(["alternate"]); root.update()
row("alternate again")

print("\n  ttk option list has a tristate/indeterminate option?",
      any("tristate" in str(o) or "indeterminate" in str(o) for o in cb.configure()))
print("  ttk Checkbutton options:", sorted(cb.configure().keys()))
root.destroy()
