"""Would `event add <<Submit>> <Return> <KP_Enter>` help the dialog Enter guard?

The dialog binds two real sequences on its toplevel and then has to work out,
inside the handler, whether a button already answered the key. Tk can map real
events onto a virtual name (`event add`, `Misc.event_add` in Tkinter), which
would collapse the two bindings into one and give the intent a name. The
question is whether it changes DISPATCH -- because if a virtual binding
supersedes the class binding, or fires in a different order, that would bear on
the guard, and if it does not, this is a naming improvement only.

Four things, each measured rather than assumed:

  1. does a `<<Submit>>` binding fire when the real key is pressed?
  2. does it also cover KP_Enter, i.e. one name for both keys?
  3. ORDER: with a widget binding, a class binding and a toplevel binding all
     live, in what order do they run, and does the virtual one displace the
     physical one on the same tag?
  4. SCOPE: is the mapping per-widget or per-interpreter?

Run: py -3.13 development/probe_439_virtual_event_for_submit.py
"""

import tkinter as tk
from tkinter import ttk

import bootstack as bs

app = bs.App(title="probe", size=(320, 120))
root = app.tk

order = []

with bs.Column(parent=app):
    btn = bs.Button("OK")

w = btn.tk
top = w.winfo_toplevel()

# ⚠ Tk DROPS a generated key event while the window is unmapped, and a bare
# `bs.App` that has not been run is withdrawn -- which silently turns every arm
# below into a no-op. Map it first and assert it, so this cannot be silent.
top.deiconify()
top.update()
assert top.winfo_ismapped(), "precondition: the window is mapped"
assert w.winfo_ismapped(), "precondition: the button is mapped"

# --- 1 & 2: does the virtual name fire, and for both keys? -------------------
root.event_add("<<Submit>>", "<Return>", "<KP_Enter>")

hits = []
w.bind("<<Submit>>", lambda e: hits.append(e.keysym))
w.focus_set()
w.event_generate("<Return>", when="now")
w.event_generate("<KP_Enter>", when="now", keycode=13)
print("1/2  <<Submit>> fired for: %r" % (hits,))
print("     (KP_Enter cannot be synthesized faithfully on this box -- see")
print("      test_the_keypad_enter_key_is_bound_alongside_enter; treat the")
print("      second entry as inconclusive, not as proof.)")

# --- 3: order, and does the virtual binding displace the physical one? -------
order.clear()
w.unbind("<<Submit>>")

w.bind("<<Submit>>", lambda e: order.append("widget:<<Submit>>"))
w.bind("<Return>", lambda e: order.append("widget:<Return>"))
top.bind("<<Submit>>", lambda e: order.append("toplevel:<<Submit>>"))
top.bind("<Return>", lambda e: order.append("toplevel:<Return>"))
root.tk.call("bind", "TButton", "<Return>",
             root.register(lambda: order.append("class:<Return>")))

w.event_generate("<Return>", when="now")
print()
print("3    dispatch order: %s" % (order,))
same_tag = [o for o in order if o.startswith("widget:")]
print("     on the WIDGET tag, both bound, fired: %s" % (same_tag,))
if len(same_tag) == 2:
    print("     -> both run; the virtual name is additive")
elif same_tag == ["widget:<Return>"]:
    print("     -> the PHYSICAL binding wins on a tag that has both;")
    print("        the virtual one does not run at all")
elif same_tag == ["widget:<<Submit>>"]:
    print("     -> the VIRTUAL binding wins on a tag that has both")
else:
    print("     -> neither ran; inconclusive")

# --- 4: scope of the mapping -------------------------------------------------
print()
print("4    event_info on the root:  %s" % (root.tk.call("event", "info", "<<Submit>>"),))
print("     event_info via a WIDGET: %s" % (w.tk.call("event", "info", "<<Submit>>"),))
print("     -> the mapping is per-INTERPRETER, not per-widget"
      if str(root.tk.call("event", "info", "<<Submit>>")) ==
         str(w.tk.call("event", "info", "<<Submit>>"))
      else "     -> per-widget")

print()
if not order:
    print("INCONCLUSIVE: nothing dispatched, so arms 1-3 measured nothing.")
else:
    print("CONCLUSION: `event add` renames and unifies the TRIGGER.")
    print("Whether it changes the bindtag walk is answered by arm 3 above --")
    print("read that, do not assume it.")

root.event_delete("<<Submit>>")
app.tk.destroy()
