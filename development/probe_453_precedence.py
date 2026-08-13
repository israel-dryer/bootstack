"""Probe: what wins when read_only is paired with each other flag?  (#453)

Prints state, asserts nothing. The point is the PRECEDENCE, which pre-fix
disagreed between construction and runtime because the ttk `readonly` entry
state was the only storage and whichever writer ran last won.

MEASURED PRE-FIX:

    read_only=True, allow_custom=True   typeable=True  popup=True  .read_only=False
    read_only=True, searchable=True     typeable=True  popup=True  .read_only=False
    read_only=True, disabled=True       typeable=False popup=False .read_only=False
    allow_custom=True .read_only=True   typeable=False popup=True  .read_only=True
                      .read_only=False  typeable=True  popup=True  .read_only=False

So construction let allow_custom_values discard read_only outright, while at
runtime read_only won over typing but never over the popup. The last row only
restored correctly BY LUCK -- state="normal" happened to be right because
custom values were on; the same code on a plain Select granted typing instead.

POST-FIX the ladder is `disabled > read_only > allow_custom_values|searchable`,
and read_only SUPPRESSES the typing modes rather than overwriting them, so
clearing it restores whichever was asked for.

ASCII output only.
"""
import bootstack as bs

OPTS = ["Alpha", "Beta", "Gamma"]


def report(name, sel):
    e = sel._entry_widget()
    inner = sel._internal
    inner._popup_open = False
    try:
        inner._show_selection_options()
        opened = bool(inner._popup_open)
        if opened:
            try:
                inner._close_popup(inner._popup_frame.winfo_toplevel(), inner._popup_state)
            except Exception:
                inner._popup_open = False
    except Exception as exc:
        opened = "RAISED %s" % type(exc).__name__
    print("%-38s typeable=%-5s popup=%-5s .read_only=%-5s _allow_custom=%s" % (
        name,
        not e.instate(["readonly"]) and not e.instate(["disabled"]),
        opened,
        sel.read_only,
        inner._allow_custom_values,
    ))


with bs.App(title="probe") as app:
    a = bs.Select(OPTS, read_only=True, allow_custom_values=True)
    b = bs.Select(OPTS, read_only=True, searchable=True)
    c = bs.Select(OPTS, read_only=True, disabled=True)
    d = bs.Select(OPTS, allow_custom_values=True)

app.tk.update_idletasks()
app.tk.update()

print("-- construction-time pairings --")
report("read_only=True, allow_custom=True", a)
report("read_only=True, searchable=True", b)
report("read_only=True, disabled=True", c)

print()
print("-- runtime: set read_only on a custom-values Select --")
report("allow_custom=True (before)", d)
d.read_only = True
report("  .read_only = True (after)", d)
d.read_only = False
report("  .read_only = False (back)", d)

app.tk.destroy()
