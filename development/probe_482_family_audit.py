"""After a programmatic signal write, does every reader of the widget agree?

#482 is one instance: `value` read a snapshot that only refreshed at a commit
point the signal path never reached. This asks the same question of every
signal-bindable widget and every reader it exposes -- `value`, `selection`, and
the validation pair -- plus `Form.get()`, which reads through `value`.

The write is made UNFOCUSED, which is the path #482 fixes. A row that disagrees
is a widget where some derived state does not follow a signal write.

    py -3.12 development/probe_482_family_audit.py
"""
import datetime as dt
import os

import bootstack as bs

print("PROVENANCE", os.path.dirname(bs.__file__))

app = bs.App(title="audit482")
root = app.tk.winfo_toplevel()
root.geometry("500x400+60+60")
root.deiconify()
root.update()

OPTS = [("Alpha", "a"), ("Beta", "b")]   # (text, value)

# name, kwarg, factory kwargs, seed, new value
CASES = [
    ("TextField",    "textsignal", {},                       "one",  "two"),
    ("PasswordField", "textsignal", {},                      "one",  "two"),
    ("PathField",    "textsignal", {},                       "one",  "two"),
    ("SpinnerField", "textsignal", {},                       "one",  "two"),
    ("TextArea",     "textsignal", {},                       "one",  "two"),
    ("CodeEditor",   "textsignal", {},                       "one",  "two"),
    ("NumberField",  "signal",     {},                       1,      2),
    ("DateField",    "signal",     {},                       dt.date(2020, 1, 1), dt.date(2021, 2, 3)),
    ("TimeField",    "signal",     {},                       dt.time(1, 0), dt.time(2, 30)),
    ("Select",       "signal",     {"options": OPTS},        "a",    "b"),
    ("SelectButton", "signal",     {"options": OPTS},        "a",    "b"),
    ("RadioGroup",   "signal",     {"options": OPTS},        "a",    "b"),
    ("Checkbox",     "signal",     {},                       False,  True),
    ("Switch",       "signal",     {},                       False,  True),
    ("ToggleButton", "signal",     {},                       False,  True),
    ("Slider",       "signal",     {"min_value": 0, "max_value": 10}, 1, 7),
]


def readers(w):
    """Every public reader this widget exposes that should track the signal."""
    out = {}
    for attr in ("value", "selection"):
        if hasattr(w, attr):
            try:
                out[attr] = getattr(w, attr)
            except Exception as exc:
                out[attr] = "EXC:%s" % type(exc).__name__
    return out


print("\n== A. readers after an unfocused programmatic signal write ==")
print("%-14s %-10s %s" % ("widget", "verdict", "readers (signal -> ...)"))
for name, kw, extra, seed, new in CASES:
    try:
        cls = getattr(bs, name)
        sig = bs.Signal(seed)
        w = cls(parent=app, **{kw: sig}, **extra)
        root.update()
        root.focus_force()
        root.update()
        sig.set(new)
        root.update()
        got = readers(w)
        # `selection` reports the option record, not the raw value; compare its value.
        bad = []
        if "value" in got and got["value"] != new:
            bad.append("value=%r" % (got["value"],))
        if bad:
            print("%-14s %-10s signal=%r  %s" % (name, "DISAGREES", sig(), "  ".join(bad)))
        else:
            print("%-14s %-10s signal=%r  %s" % (name, "agrees", sig(), got))
    except Exception as exc:
        print("%-14s %-10s %s: %s" % (name, "EXC", type(exc).__name__, exc))

print("\n== B. Form.get() after writing the editors' signals ==")
try:
    sigs = {"a": bs.Signal("one"), "b": bs.Signal(1)}
    form = bs.Form(parent=app, items=[
        {"key": "a", "label": "A", "editor": "textfield", "editor_options": {"textsignal": sigs["a"]}},
        {"key": "b", "label": "B", "editor": "numberfield", "editor_options": {"signal": sigs["b"]}},
    ])
    root.update()
    root.focus_force()
    root.update()
    sigs["a"].set("two")
    sigs["b"].set(2)
    root.update()
    data = form.get()
    ok = data.get("a") == "two" and data.get("b") == 2
    print("  form.get() -> %r  %s" % (data, "agrees" if ok else "DISAGREES"))
except Exception as exc:
    print("  EXC %s: %s" % (type(exc).__name__, exc))

print("\n== C. validation state after a failing signal write ==")
for name, kw, extra, seed, bad_value in [
    ("TextField", "textsignal", {}, "aaaa", "x"),
    ("NumberField", "signal", {}, 50, 1),
]:
    try:
        cls = getattr(bs, name)
        sig = bs.Signal(seed)
        w = cls(parent=app, **{kw: sig}, **extra)
        if name == "TextField":
            w.add_validation_rule("stringLength", min=3)
        else:
            w.add_validation_rule("range", min=10)
        root.update()
        root.focus_force()
        root.update()
        w.validate()
        before = w.valid()
        if before is not True:
            print("  %-12s SETUP BAD -- seed does not pass its own rule" % name)
            continue
        sig.set(bad_value)
        root.update()
        after_write = w.valid()
        w.validate()
        after_validate = w.valid()
        if after_validate is not False:
            print("  %-12s SETUP BAD -- the rule never fails, so the arm proves nothing" % name)
            continue
        print("  %-12s valid: seed=%s  after signal write=%s  after validate()=%s  %s" % (
            name, before, after_write, after_validate,
            "state follows" if after_write is False else "state STALE until validate()"))
    except Exception as exc:
        print("  %-12s EXC %s: %s" % (name, type(exc).__name__, exc))

print("\n== D. does the OTHER programmatic path update validation? ==")
for name, kw, extra, seed, bad_value in [
    ("TextField", "textsignal", {}, "aaaa", "x"),
    ("NumberField", "signal", {}, 50, 1),
]:
    try:
        cls = getattr(bs, name)
        sig = bs.Signal(seed)
        w = cls(parent=app, **{kw: sig}, **extra)
        w.add_validation_rule("stringLength", min=3) if name == "TextField" else w.add_validation_rule("range", min=10)
        root.update(); root.focus_force(); root.update()
        w.validate()
        w.value = bad_value          # the setter, not the signal
        root.update()
        print("  %-12s valid after `.value =` a failing value: %s   %s" % (
            name, w.valid(),
            "follows" if w.valid() is False else "STALE -- same as the signal path"))
    except Exception as exc:
        print("  %-12s EXC %s: %s" % (name, type(exc).__name__, exc))

root.destroy()
