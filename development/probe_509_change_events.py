"""Probe #509 - measure ChangeEvent behavior across the field family.

Each arm drives one widget the way a user would (focus moves, key events,
button clicks) and records every ChangeEvent it emits. ASCII output only.

Run: py -3.12 development/probe_509_change_events.py
"""
from __future__ import annotations

import tkinter as tk

import bootstack as bs
from bootstack.widgets._impl.composites import pathentry as _pathentry_mod

RESULTS: list[str] = []


def report(name: str, text: str) -> None:
    RESULTS.append(f"{name}: {text}")
    print(f"  {text}")


def pump(app, n: int = 3) -> None:
    for _ in range(n):
        app._internal.update()


with bs.App(title="probe 509", size=(600, 700), padding=8, horizontal_items="stretch") as app:
    # A neutral widget to move focus to.
    parking = bs.TextField(label="parking")

    ta = bs.TextArea(label="Text Area")
    ta_events: list = []
    ta.on_change(ta_events.append)

    sb = bs.SelectButton(options=["Small", "Medium", "Large"])
    sb_events: list = []
    sb.on_change(sb_events.append)

    pf = bs.PathField(label="Path Field")
    pf_events: list = []
    pf_inputs: list = []
    pf.on_change(pf_events.append)
    pf.on_input(pf_inputs.append)

    sl = bs.Slider(value=50, min_value=0, max_value=100, step=10)
    sl_events: list = []
    sl_commits: list = []
    sl.on_change(sl_events.append)
    sl.on_commit(sl_commits.append)

    # Control arm: the SAME sweep with no step at all, to separate "the guard
    # suppresses redundant events" from "the guard reduces event volume".
    sl_free = bs.Slider(value=50, min_value=0, max_value=100)
    slf_events: list = []
    sl_free.on_change(slf_events.append)

    ce_events: list = []
    ce = bs.CodeEditor(language="python", value='print("Hello, World!")', height=5)
    ce.on_change(ce_events.append)

root = app._internal
root.deiconify()
root.update_idletasks()
root.update()
root.focus_force()
pump(app, 5)
print(f"[setup] root mapped={root.winfo_ismapped()} geom={root.winfo_geometry()} "
      f"slider_canvas mapped={sl._internal._canvas.winfo_ismapped()} "
      f"w={sl._internal._canvas.winfo_width()} reqw={sl._internal._canvas.winfo_reqwidth()}")

print("\n=== ARM 1: TextArea ===")
ta_text = ta._internal._core.text
parking._entry_widget().focus_force()
pump(app)
ta_text.focus_force()
pump(app)
ta_text.insert("end", "hello")
pump(app)
parking._entry_widget().focus_force()   # blur -> commit
pump(app)
n_after_edit = len(ta_events)
first = ta_events[0] if ta_events else None
report("textarea.edit", f"events after typing+blur = {n_after_edit}, "
                        f"value={getattr(first, 'value', None)!r} "
                        f"prev_value={getattr(first, 'prev_value', 'MISSING')!r}")

ta_text.focus_force()
pump(app)
parking._entry_widget().focus_force()   # blur again, NOTHING changed
pump(app)
report("textarea.noop_blur", f"events after a no-edit focus round trip = "
                             f"{len(ta_events) - n_after_edit} (expected 0)")

print("\n=== ARM 2: SelectButton ===")
sb.value = "Medium"
pump(app)
sb.value = "Large"
pump(app)
report("selectbutton", f"events={len(sb_events)}; "
                       + "; ".join(f"value={getattr(e,'value',None)!r} "
                                   f"prev_value={getattr(e,'prev_value','MISSING')!r} "
                                   f"text={getattr(e,'text','MISSING')!r}"
                                   for e in sb_events))

print("\n=== ARM 3: PathField via the dialog button ===")
_pathentry_mod._MODE_TO_DIALOG["open"] = lambda **kw: r"C:\tmp\chosen.txt"
pf._internal.dialog_button.invoke()
pump(app, 6)
report("pathfield.dialog", f"value={pf.value!r} change_events={len(pf_events)} "
                           f"input_events={len(pf_inputs)} (expected >=1 change)")

# Control: the same widget DOES emit change when typed into and blurred.
pf_entry = pf._entry_widget()
pf_entry.focus_force()
pump(app)
pf_entry.insert("end", "X")
pump(app)
parking._entry_widget().focus_force()
pump(app)
report("pathfield.typed_control", f"change_events after typing+blur = {len(pf_events)} "
                                  f"(control: proves the handler is wired)")

print("\n=== ARM 4: Slider with step=10 ===")
canvas = sl._internal._canvas
pump(app, 4)
w = canvas.winfo_width()
canvas.event_generate("<Button-1>", x=5, y=canvas.winfo_height() // 2)
pump(app)
sl_events.clear()
# Sweep across the whole track one pixel at a time.
for x in range(5, max(6, w - 5)):
    canvas.event_generate("<B1-Motion>", x=x, y=canvas.winfo_height() // 2)
canvas.event_generate("<ButtonRelease-1>", x=w - 5, y=canvas.winfo_height() // 2)
pump(app, 3)
values = [e.value for e in sl_events]
distinct = len({round(v, 6) for v in values})
redundant = sum(1 for e in sl_events if e.value == e.prev_value)
report("slider.step10", f"canvas_width={w} events={len(values)} distinct_values={distinct} "
                        f"events_where_value==prev_value={redundant} "
                        f"commit_events={len(sl_commits)}")


def sweep(widget) -> tuple[int, int, int]:
    """Drag across the whole track one pixel at a time; return (events, distinct, redundant)."""
    cv = widget._internal._canvas
    ymid = cv.winfo_height() // 2
    width = cv.winfo_width()
    cv.event_generate("<Button-1>", x=5, y=ymid)
    pump(app)
    sink = slf_events
    sink.clear()
    for px in range(5, max(6, width - 5)):
        cv.event_generate("<B1-Motion>", x=px, y=ymid)
    cv.event_generate("<ButtonRelease-1>", x=width - 5, y=ymid)
    pump(app, 3)
    return (len(sink),
            len({round(e.value, 6) for e in sink}),
            sum(1 for e in sink if e.value == e.prev_value))


n_free, d_free, r_free = sweep(sl_free)
report("slider.no_step", f"events={n_free} distinct_values={d_free} "
                         f"events_where_value==prev_value={r_free} "
                         f"(a guard would suppress only the redundant ones)")

print("\n=== ARM 5: CodeEditor ===")
report("codeeditor.construction", f"events fired before any user edit = {len(ce_events)}")
n0 = len(ce_events)
ce_text = ce._text_widget()
ce_text.focus_force()
pump(app)
for ch in "abc":
    ce_text.event_generate("<KeyPress>", keysym=ch)
    pump(app)
report("codeeditor.keystrokes", f"events after 3 keystrokes = {len(ce_events) - n0}")
n1 = len(ce_events)
parking._entry_widget().focus_force()
pump(app)
report("codeeditor.blur", f"events on blur = {len(ce_events) - n1}")
last = ce_events[-1] if ce_events else None
report("codeeditor.payload", f"prev_value={getattr(last, 'prev_value', 'MISSING')!r}")

print("\n=== ARM 6: Calendar surface ===")
report("calendar", f"has on_change={hasattr(bs.Calendar, 'on_change')} "
                   f"has on_select={hasattr(bs.Calendar, 'on_select')}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
for line in RESULTS:
    print(line)

root.destroy()