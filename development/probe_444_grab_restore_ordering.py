"""#444 -- does a <Destroy> restore win its race with Tk's own grab release?

Decides option B (restore on destroy, covers every path) vs option A (restore in
block_until_closed's finally, blocking path only). ASCII only.
"""
import tkinter as tk

def status(w):
    try:
        return w.grab_status()
    except Exception:
        return None

def who(root):
    g = root.grab_current()
    return (str(g) if g is not None else None), (status(g) if g is not None else None)

root = tk.Tk(); root.withdraw()

# --- outer window holds a LOCAL grab, standing in for a modal dialog ---------
outer = tk.Toplevel(root); outer.geometry("200x100+100+100"); outer.update()
outer.grab_set()
print("ARM 1 -- baseline")
print("  outer holds:", who(root))

# --- inner modal takes the grab, and restores from <Destroy> ----------------
inner = tk.Toplevel(root); inner.geometry("180x80+140+140"); inner.update()
previous = root.grab_current()
prev_kind = status(previous) if previous is not None else None
print("  captured before grabbing:", (str(previous) if previous else None), prev_kind)
inner.grab_set()
print("  inner holds:", who(root))

seen = []
def _on_destroy(event):
    if event.widget is not inner:
        return
    seen.append(("destroy fired", who(root)))
    try:
        if previous is not None and previous.winfo_exists():
            if prev_kind == "global":
                previous.grab_set_global()
            else:
                previous.grab_set()
        seen.append(("restore attempted", who(root)))
    except Exception as e:
        seen.append(("restore raised", type(e).__name__))

inner.bind("<Destroy>", _on_destroy, add="+")
inner.destroy()
root.update()

print()
print("ARM 2 -- what the <Destroy> handler saw")
for label, val in seen:
    print("  %-18s %s" % (label, val))

print()
print("ARM 3 -- the verdict, read after the dust settles")
final = who(root)
print("  grab_current / status now:", final)
expected = (str(outer), prev_kind)
if final == expected:
    print("  VERDICT: OPTION B HOLDS -- the destroy-time restore survives")
else:
    print("  VERDICT: OPTION B LOSES -- expected %s, got %s. Ship option A." % (expected, final))

root.destroy()
