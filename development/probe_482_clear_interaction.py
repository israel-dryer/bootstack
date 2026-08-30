import os, bootstack as bs
print("PROVENANCE", os.path.dirname(bs.__file__))
app = bs.App(); root = app.tk.winfo_toplevel()
root.geometry("400x300+60+60"); root.deiconify(); root.update()
for name, kw in [("TextField","textsignal"),("SpinnerField","textsignal"),
                 ("TextArea","textsignal"),("CodeEditor","textsignal")]:
    try:
        sig = bs.Signal("seed", allow_empty=True)
        w = getattr(bs, name)(parent=app, **{kw: sig})
        root.update(); root.focus_force(); root.update()
        sig.clear(); root.update()
        print("  %-12s after clear: signal=%r value=%r" % (name, sig(), w.value))
    except Exception as exc:
        print("  %-12s EXC %s: %s" % (name, type(exc).__name__, exc))
root.destroy()
