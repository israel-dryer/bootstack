"""#484 -- widget-owned signals: who made them, and can the caller clear them?"""
import bootstack as bs

def probe(label, w):
    sig = getattr(w, "signal", None)
    if sig is None:
        print("  %-14s .signal is None" % label); return
    # how was it made? from_variable signals are realized at birth with no _allow_empty path
    made = "from_variable" if sig._var is not None and sig._object_mode is False and \
           getattr(sig, "_master", "x") is not None and sig._var.__class__.__name__ and \
           sig._bridge_fid is not None and sig._var is getattr(w.tk, "_bs_probe", sig._var) else "?"
    try:
        sig.clear()
        out = "clear() OK -> %r" % (sig(),)
    except Exception as e:
        out = "clear() %s: %s" % (type(e).__name__, str(e)[:52])
    print("  %-14s allows_empty=%-5s realized=%-5s %s" % (label, sig.allows_empty, sig._var is not None, out))

with bs.App(title="p") as app:
    print("=== widget-owned signal (the caller passed none) ===")
    probe("TextField", bs.TextField())
    probe("PasswordField", bs.PasswordField())
    probe("PathField", bs.PathField())
    probe("SpinnerField", bs.SpinnerField())
    probe("TextArea", bs.TextArea())
    probe("Slider", bs.Slider())
    probe("Checkbox", bs.Checkbox("x"))
    probe("NumberField", bs.NumberField())
    probe("Select", bs.Select(options=["a", "b"]))

    print("\n=== caller-supplied, declared able to be empty ===")
    s = bs.Signal("x", allow_empty=True)
    tf = bs.TextField(textsignal=s)
    try:
        s.clear(); print("  TextField      clear() OK -> %r  entry=%r" % (s(), tf.tk.get()))
    except Exception as e:
        print("  TextField      clear()", type(e).__name__, e)
app.destroy()
