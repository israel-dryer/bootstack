"""Could the literal string 'None' serve as a universal empty sentinel?

Three things must hold. Measured in PLAIN tkinter/ttk, so nothing bootstack
does can be blamed for the outcome.
"""
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("300x200+50+50")
root.update()

# Tk errors inside a trace or a widget's own variable read never reach Python.
bg = []
root.tk.createcommand("bgerror", lambda msg: bg.append(msg))

print("Tk patchlevel:", root.tk.call("info", "patchlevel"))
print()

print("== 1. does the END USER see it? StringVar -> ttk.Entry ==")
sv = tk.StringVar(value="hello")
e = ttk.Entry(root, textvariable=sv)
e.pack()
root.update()
sv.set(None)
root.update()
print("   var raw   : %r" % root.tk.call("set", str(sv)))
print("   entry text: %r   <- what is on screen" % e.get())

print()
print("== 2. does the WIDGET tolerate it? DoubleVar -> ttk.Scale ==")
dv = tk.DoubleVar(value=0.5)
s = ttk.Scale(root, variable=dv, from_=0, to=1)
s.pack()
root.update()
bg.clear()
try:
    dv.set(None)
    root.update()
    print("   set(None)  : no Python exception")
except Exception as ex:
    print("   set(None)  : %s: %s" % (type(ex).__name__, ex))
print("   var raw    : %r" % root.tk.call("set", str(dv)))
try:
    print("   scale.get(): %r" % s.get())
except Exception as ex:
    print("   scale.get(): RAISES %s: %s" % (type(ex).__name__, str(ex)[:60]))
try:
    print("   dv.get()   : %r" % dv.get())
except Exception as ex:
    print("   dv.get()   : RAISES %s: %s" % (type(ex).__name__, str(ex)[:60]))
print("   background errors Python never saw: %d" % len(bg))
for m in bg[:3]:
    print("      %s" % str(m)[:80])

print()
print("== 3. does it collide with real data? user types the four characters ==")
sv2 = tk.StringVar(value="")
e2 = ttk.Entry(root, textvariable=sv2)
e2.pack()
root.update()
e2.insert(0, "None")          # a user typing a perfectly ordinary word
root.update()
print("   entry text: %r" % e2.get())
print("   var raw   : %r" % root.tk.call("set", str(sv2)))
print("   a parse-on-read rule would hand the app None for this typed text")

print()
print("== 4. BooleanVar refuses before any sentinel can be written ==")
bv = tk.BooleanVar(value=False)
try:
    bv.set(None)
    print("   set(None): stored %r" % root.tk.call("set", str(bv)))
except Exception as ex:
    print("   set(None): RAISES %s: %s" % (type(ex).__name__, ex))

root.tk.deletecommand("bgerror")
root.destroy()
