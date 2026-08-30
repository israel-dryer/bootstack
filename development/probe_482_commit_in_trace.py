"""#482 round 1 -- an in-trace commit() cannot repaint the entry.

`_commit_if_not_editing` runs inside the bound variable's own write trace. Tcl
suppresses every other trace on a variable while one of its traces is executing,
so the display-normalizing `textsignal.set()` inside `commit()` moves the signal
while the entry's own trace never runs. Arm D shows that in plain tkinter; arms
1/A/B/E show what it does to a field, and B shows it does not heal on blur.

Run it twice and diff, once per arm:

    .venv/bin/python development/probe_482_commit_in_trace.py
    PYTHONPATH=<main-worktree>/src .venv/bin/python development/probe_482_commit_in_trace.py

Needs a display (xvfb-run on the WSL box). Every arm is independent -- one that
raises reports and the rest still run.
"""
import os

import bootstack as bs

print("PROVENANCE", os.path.dirname(bs.__file__))

app = bs.App(title="probe482")
root = app.tk.winfo_toplevel()
root.geometry("400x300+50+50")
root.deiconify()
root.update()


def arm(label, fn):
    try:
        print("[%s] %s" % (label, fn()))
    except Exception as exc:
        print("[%s] EXC %s: %s" % (label, type(exc).__name__, exc))


def snap(field, sig):
    return "sig=%r display=%r value=%r" % (
        sig(), field._internal._entry.get(), field.value)


def a1():
    sig = bs.Signal("1")
    f = bs.TextField(parent=app, textsignal=sig, value_format="#,##0.00")
    root.update()
    sig.set("1234.5")
    root.update()
    return snap(f, sig)


def a2():
    # An unparseable programmatic write must not revert the display.
    sig = bs.Signal("1")
    f = bs.TextField(parent=app, textsignal=sig, value_format="#,##0.00")
    root.update()
    sig.set("abc")
    root.update()
    return snap(f, sig)


def a_strip():
    # No value_format needed -- commit() also strips.
    sig = bs.Signal("a")
    f = bs.TextField(parent=app, textsignal=sig)
    root.update()
    sig.set("  padded  ")
    root.update()
    return snap(f, sig)


def a_heal():
    sig = bs.Signal("1")
    f = bs.TextField(parent=app, textsignal=sig, value_format="#,##0.00")
    root.update()
    sig.set("1234.5")
    root.update()
    before = snap(f, sig)
    e = f._internal._entry
    e.focus_force()
    root.update()
    e.event_generate("<FocusOut>")
    root.update()
    return "after write: %s || after blur: %s" % (before, snap(f, sig))


def a_spinner():
    sig = bs.Signal("1")
    f = bs.SpinnerField(parent=app, textsignal=sig, value_format="#,##0.00",
                        min_value=0, max_value=100000)
    root.update()
    sig.set("1234.5")
    root.update()
    return snap(f, sig)


def a_tcl():
    # The mechanism, in plain tkinter: traces fire in reverse creation order,
    # and a nested set from inside a trace fires nothing at all.
    import tkinter as tk
    v = tk.StringVar(master=root, value="x")
    hits = []

    def t1(*_):
        hits.append(("t1", v.get()))
        if v.get() == "y":
            v.set("z")

    def t2(*_):
        hits.append(("t2", v.get()))

    v.trace_add("write", t1)
    v.trace_add("write", t2)
    v.set("y")
    return "hits=%s final=%r" % (hits, v.get())


def a_subscribers():
    # Re-entrancy: no recursion, no leak, and an application subscriber is
    # called once per write with the text it wrote.
    sig = bs.Signal("a")
    f = bs.TextField(parent=app, textsignal=sig, value_format="#,##0.00")
    root.update()
    seen = []
    sig.subscribe(seen.append)
    for i in range(50):
        sig.set(str(i))
        root.update()
    fid = f._internal._entry._on_input_fid
    return "subs=%d fid_live=%s app_calls=%d last=%r value=%r" % (
        len(sig._subscribers), fid is not None, len(seen), seen[-1], f.value)


def a_number():
    # NumberEntryPart subclasses TextEntryPart and inherits the helper, so the
    # fix must be inert here: NumberField already followed.
    f = bs.NumberField(parent=app, value=5, min_value=0, max_value=10,
                       value_format="#,##0.00")
    e = f._internal._entry
    root.update()
    out = []
    for v in (7, 99):
        f.value = v
        root.update()
        out.append("value=%s -> %r display=%r" % (v, f.value, e.get()))
    e.focus_force()
    root.update()
    e.event_generate("<FocusOut>")
    root.update()
    out.append("after blur: %r display=%r" % (f.value, e.get()))
    return " | ".join(out)


def a_cost():
    import time
    sig = bs.Signal("")
    f = bs.TextField(parent=app, textsignal=sig)
    root.update()
    e = f._internal._entry
    e.focus_force()
    root.update()
    n = 2000
    t0 = time.perf_counter()
    for i in range(n):
        sig.set("x" * (i % 40 + 1))
    t1 = time.perf_counter()
    t2 = time.perf_counter()
    for _ in range(n):
        e.focus_get()
    t3 = time.perf_counter()
    return "%.1f us/write; focus_get %.1f us/call" % (
        (t1 - t0) * 1e6 / n, (t3 - t2) * 1e6 / n)


arm("1  value_format write", a1)
arm("2  unparseable write", a2)
arm("A  strip, no value_format", a_strip)
arm("B  heal on blur?", a_heal)
arm("E  spinner value_format", a_spinner)
arm("D  nested set fires traces?", a_tcl)
arm("S  subscriber integrity", a_subscribers)
arm("N  NumberField inertness", a_number)
arm("C  per-write cost", a_cost)
print("DONE")
