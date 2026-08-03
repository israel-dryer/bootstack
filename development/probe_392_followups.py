"""Baseline/after probe for the #392 follow-up cluster (#396, #398, #401).

Run with `py -3.12 development/probe_392_followups.py`. Each check prints
PASS/FAIL against the FIXED behavior, so the whole block reads FAIL before the
fix and PASS after it.
"""
import tkinter

import bootstack as bs
from bootstack.events import ChangeEvent

results = []


def check(name, actual, expected):
    ok = actual == expected
    results.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: got {actual!r}, want {expected!r}")


def probe_396(app):
    """emit() must reach a handler registered via the matching on_*()."""
    print("#396 — emit()/on() target the same widget")
    field = bs.TextField(parent=app)
    seen = []
    field.on_change(lambda e: seen.append(e.value))
    app.tk.update()

    field.emit("change", data=ChangeEvent(value="typed"))
    app.tk.update()
    check("TextField emit->on_change", seen, ["typed"])

    # A non-retargeted event on the same widget must keep working.
    sel = bs.Select(options=["a", "b"], parent=app)
    seen_sel = []
    sel.on_change(lambda e: seen_sel.append(getattr(e, "value", None)))
    app.tk.update()
    sel.emit("change", data=ChangeEvent(value="b"))
    app.tk.update()
    check("Select emit->on_change", seen_sel, ["b"])

    # Stream path must retarget identically.
    field2 = bs.TextField(parent=app)
    seen2 = []
    field2.on("change").listen(lambda e: seen2.append(e.value))
    app.tk.update()
    field2.emit("change", data=ChangeEvent(value="streamed"))
    app.tk.update()
    check("TextField emit->Stream", seen2, ["streamed"])


def probe_398(app):
    """unbind of the <Visibility> alpha binding must actually remove it."""
    print("#398 — on_visibility_alpha unbinds itself")
    from bootstack._runtime.base_window import on_visibility_alpha

    w = tkinter.Toplevel(app.tk)
    fired = []
    w.alpha = 0.9
    w.alpha_bind = w.bind("<Visibility>", lambda e: fired.append(1), "+")
    app.tk.update()

    on_visibility_alpha(type("E", (), {"widget": w})())
    still_bound = bool(w.bind("<Visibility>"))
    check("binding removed after first use", still_bound, False)
    w.destroy()


def probe_401(app):
    """A non-interactive field must not suppress later <<Increment>> handlers."""
    print("#401 — NumberEntryPart 'break' no longer aborts the dispatch")
    nf = bs.NumberField(value=1, disabled=True, parent=app)
    part = nf._internal._entry
    later = []
    part.bind("<<Increment>>", lambda e: later.append(1), add="+")
    app.tk.update()

    part.event_generate("<<Increment>>")
    app.tk.update()
    check("later handler still runs", later, [1])


with bs.App(title="probe") as app:
    pass
app.tk.update()
app.tk.deiconify()
app.tk.update()

for probe in (probe_396, probe_398, probe_401):
    try:
        probe(app)
    except Exception as exc:  # noqa: BLE001
        results.append(False)
        print(f"  [ERROR] {probe.__name__}: {type(exc).__name__}: {exc}")
    print()

print(f"{sum(results)}/{len(results)} checks pass")
app.tk.destroy()