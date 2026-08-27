"""Can a Tk VARIABLE carry the indeterminate state? ttk vs classic, plain tkinter."""
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.withdraw()
print("Tk patchlevel:", root.tk.call("info", "patchlevel"))

print()
print("== ttk.Checkbutton: does it even have a tristate option? ==")
c = ttk.Checkbutton(root)
opts = sorted(c.keys())
print("tristate-ish options:", [o for o in opts if "tri" in o] or "NONE")

print()
print("== ttk: write a third value into the variable ==")
v = tk.StringVar(value="off")
c = ttk.Checkbutton(root, variable=v, onvalue="on", offvalue="off")
root.update()
for val in ("on", "off", "maybe", ""):
    v.set(val)
    root.update()
    print("  var=%-7r selected=%-5s alternate=%-5s"
          % (val, bool(c.instate(("selected",))), bool(c.instate(("alternate",)))))

print()
print("== ttk: set alternate by STATE, then write the var ==")
v.set("off"); root.update()
c.state(("alternate",))
root.update()
print("  after state(alternate)   alternate=%s var=%r" % (bool(c.instate(("alternate",))), v.get()))
v.set("off")
root.update()
print("  after var.set('off')     alternate=%s  <- a variable write clears it"
      % bool(c.instate(("alternate",))))

print()
print("== classic tk.Checkbutton: -tristatevalue ==")
c2 = tk.Checkbutton(root)
print("tristate-ish options:", [o for o in sorted(c2.keys()) if "tri" in o] or "NONE")
v2 = tk.StringVar(value="off")
c3 = tk.Checkbutton(root, variable=v2, onvalue="on", offvalue="off", tristatevalue="maybe")
root.update()
for val in ("on", "off", "maybe"):
    v2.set(val)
    root.update()
    print("  var=%-7r -> widget reports %r" % (val, c3.cget("tristatevalue") == val))

root.destroy()
