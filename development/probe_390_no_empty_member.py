"""#390 -- 'the BooleanVar/DoubleVar bindings still refuse': what does that mean?

StringVar has '' -- a legal str that every widget reads as empty.  Ask whether
BooleanVar and DoubleVar have any analogous member at all.
"""
import tkinter as tk

root = tk.Tk(); root.withdraw()
print("-- can the variable even STORE an empty? --")
for name, cls in (("StringVar", tk.StringVar), ("BooleanVar", tk.BooleanVar),
                  ("DoubleVar", tk.DoubleVar), ("IntVar", tk.IntVar)):
    for label, val in (("''", ""), ("None", None)):
        v = cls(master=root)
        try:
            v.set(val)
            raw = root.getvar(str(v))
            try:
                got = repr(v.get())
            except Exception as exc:
                got = f"get() RAISES {type(exc).__name__}: {exc}"
            print(f"   {name:11} set({label:4}) OK    raw tcl={raw!r:8}  {got}")
        except Exception as exc:
            print(f"   {name:11} set({label:4}) RAISES {type(exc).__name__}: {exc}")
root.destroy()

print()
print("-- and is there a natural empty MEMBER of the Python type? --")
print("   str    -> ''      a real value, distinct from every non-empty string")
print("   bool   -> {}      True/False only; False is 'off', not 'unset' (#358 tristate)"
      .format(sorted(map(repr, (True, False)))))
print("   float  -> none    0.0 is a position on the track, not an absent one")
