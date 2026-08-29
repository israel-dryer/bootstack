"""Does a `Signal.clear()` reach the widget bound to it? A family census.

Round 2 of #486 found that clearing an `allow_empty` signal bound to a
`TextArea` leaves the widget showing its old text. This asks how wide that is,
and whether the multiline pair is the exception or the rule.

Arm `census`   -- clear a bound signal on every field widget that takes one and
                  read what is ON SCREEN, not `.value` (which lags a
                  programmatic signal write on the entry-backed family, #482).
Arm `realized` -- the sharp one. The empty a signal produces is decided by its
                  BINDING: `None` normally, `''` where the signal IS the
                  widget's own Tk variable. So bind ONE signal to a TextArea
                  alone, then to a TextArea AND a TextField, and clear it both
                  times. If the TextArea honors the clear only in the second
                  case, the guard is the defect and not a design.

ASCII output. One `bs.App` per process.
"""

import sys
from datetime import date, time

import bootstack as bs


def pump(app, n=6):
    for _ in range(n):
        app.tk.update()
        app.tk.update_idletasks()


def shown(widget):
    """What the widget actually displays, read from the toolkit widget."""
    inner = widget._internal
    core = getattr(inner, "core", None) or getattr(inner, "_core", None)
    if core is not None and hasattr(core, "text"):
        return core.text.get("1.0", "end-1c")
    entry = getattr(inner, "_entry", None)
    if entry is not None and hasattr(entry, "get"):
        return entry.get()
    return "<no reader>"


def arm_census():
    print("-" * 78)
    print("ARM census: clear a bound signal, read what is on screen")
    print("-" * 78)
    app = bs.App(title="p486clear", size=(600, 400))
    app.__enter__()

    cases = []

    def add(label, factory, seed, kw="signal"):
        sig = bs.Signal(seed, allow_empty=True)
        try:
            w = factory(**{kw: sig})
        except Exception as exc:
            cases.append((label, None, None, "REFUSED: %s" % exc))
            return
        cases.append((label, w, sig, None))

    add("TextField", bs.TextField, "hello", "textsignal")
    add("PasswordField", bs.PasswordField, "hello", "textsignal")
    add("PathField", bs.PathField, "hello", "textsignal")
    add("SpinnerField", bs.SpinnerField, "hello", "textsignal")
    add("TextArea", bs.TextArea, "hello", "textsignal")
    add("CodeEditor", bs.CodeEditor, "hello", "textsignal")
    add("NumberField", bs.NumberField, 7)
    add("DateField", bs.DateField, date(2026, 1, 15))
    add("TimeField", bs.TimeField, time(9, 30))

    app.__exit__(None, None, None)
    app.tk.deiconify()
    pump(app)

    print("  %-14s %-10s %-16s %-16s %-10s" % ("widget", "realized", "shown before",
                                               "shown after", "sig after"))
    for label, w, sig, err in cases:
        if err:
            print("  %-14s %s" % (label, err))
            continue
        before = shown(w)
        realized = "yes" if getattr(sig, "_var", None) is not None else "no"
        try:
            sig.clear()
        except Exception as exc:
            print("  %-14s clear() raised %s: %s" % (label, type(exc).__name__, exc))
            continue
        pump(app)
        after = shown(w)
        verdict = "OK" if after in ("", "<no reader>") else "*** IGNORED ***"
        print("  %-14s %-10s %-16r %-16r %-10r %s"
              % (label, realized, before, after, sig(), verdict))
    app.tk.destroy()


def arm_realized():
    print("-" * 78)
    print("ARM realized: the SAME signal, alone vs also bound to a TextField")
    print("-" * 78)
    app = bs.App(title="p486clear2", size=(600, 400))
    app.__enter__()

    lonely = bs.Signal("hello", allow_empty=True)
    ta_alone = bs.TextArea(textsignal=lonely)

    shared = bs.Signal("hello", allow_empty=True)
    ta_shared = bs.TextArea(textsignal=shared)
    tf_shared = bs.TextField(textsignal=shared)

    app.__exit__(None, None, None)
    app.tk.deiconify()
    pump(app)

    for label, sig, w in (("TextArea alone", lonely, ta_alone),
                          ("TextArea + TextField", shared, ta_shared)):
        realized = getattr(sig, "_var", None) is not None
        before = shown(w)
        sig.clear()
        pump(app)
        after = shown(w)
        print("  %-22s realized=%-5s empty=%-6r  shown %r -> %r  %s"
              % (label, realized, sig(), before, after,
                 "OK" if after == "" else "*** IGNORED ***"))
    print()
    print("  The TextArea code is identical in both rows. What differs is the")
    print("  EMPTY the signal produced, and `_on_signal_change` drops None.")
    app.tk.destroy()


def arm_widget_side():
    """The other direction: the WIDGET is cleared. Does the signal go empty?

    A signal that allows empty has a declared empty state. `Signal.clear()`
    enters it. The write-back calls `set()`, so what the widget pushes when it
    is emptied is an ordinary `''` -- a real member of `str` -- not the empty.
    """
    print("-" * 78)
    print("ARM widget_side: clear the WIDGET, ask whether the signal went empty")
    print("-" * 78)
    app = bs.App(title="p486clear3", size=(600, 400))
    app.__enter__()
    ta_sig = bs.Signal("hello", allow_empty=True)
    ta = bs.TextArea(textsignal=ta_sig)
    tf_sig = bs.Signal("hello", allow_empty=True)
    tf = bs.TextField(textsignal=tf_sig)
    app.__exit__(None, None, None)
    app.tk.deiconify()
    pump(app)

    for label, w, sig in (("TextArea", ta, ta_sig), ("TextField", tf, tf_sig)):
        w.clear()
        pump(app)
        print("  %-10s after widget.clear() : sig=%-6r falsy=%-5s shown=%r"
              % (label, sig(), not sig(), shown(w)))
    print()
    print("  Both are falsy, which is the check the CHANGELOG tells callers to")
    print("  use -- but only one of them is the signal's declared empty.")
    app.tk.destroy()


ARMS = {"census": arm_census, "realized": arm_realized,
        "widget_side": arm_widget_side}

if __name__ == "__main__":
    print("=" * 78)
    print("SOURCE:", bs.__file__)
    if len(sys.argv) > 1:
        for name in sys.argv[1:]:
            ARMS[name]()
        print("=" * 78)
    else:
        import subprocess
        for name in ARMS:
            subprocess.run([sys.executable, __file__, name])
