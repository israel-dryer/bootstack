"""#484 -- how far does the forced allow_empty=False reach? ASCII only."""
import bootstack as bs

def try_clear(sig):
    try:
        sig.clear()
        return "OK -> %r" % (sig(),)
    except Exception as e:
        return "%s: %s" % (type(e).__name__, str(e)[:60])

with bs.App(title="p") as app:
    print("=== a widget's OWN signal, when the user supplied none ===")
    for label, w in [
        ("RadioGroup",  bs.RadioGroup(options=["a", "b"])),
        ("ToggleGroup", bs.ToggleGroup(options=["a", "b"])),
        ("Tabs",        bs.Tabs()),
    ]:
        sig = getattr(w, "signal", None)
        if sig is None:
            print("  %-12s no public .signal" % label); continue
        print("  %-12s allows_empty=%-5s clear() -> %s" % (label, sig.allows_empty, try_clear(sig)))

    print("\n=== the SAME widget, with a user-supplied allow_empty signal ===")
    s = bs.Signal("a", allow_empty=True)
    g = bs.RadioGroup(options=["a", "b"], signal=s)
    print("  RadioGroup   allows_empty=%-5s clear() -> %s   widget.value=%r"
          % (s.allows_empty, try_clear(s), g.value))

    print("\n=== the workaround on a widget-owned signal ===")
    g2 = bs.RadioGroup(options=["a", "b"])
    g2.value = "a"
    s2 = g2.signal
    try:
        s2.set("")
        print("  set('') -> signal=%r widget.value=%r" % (s2(), g2.value))
    except Exception as e:
        print("  set('') raised", type(e).__name__, e)
app.destroy()
