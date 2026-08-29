"""Headless driver for the #467 demo: drive each panel and assert what it shows.

Two things a driver here gets wrong, both of which make a WORKING fix look broken:
  * the debounce is 50 ms of WALL TIME, so pumping update() in a tight loop never
    reaches it -- every wait below is wall-clock;
  * event_generate("<KeyRelease>") with no keysym is not delivered as a key, so
    the key trigger never runs. Pass keysym=.
"""
import importlib.util, sys, time

spec = importlib.util.spec_from_file_location("demo467", sys.argv[1])
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

real_stderr = sys.stderr
app, w = demo.build()
root = app.tk.winfo_toplevel()
root.deiconify()

def pump(seconds=0.35):
    end = time.time() + seconds
    while time.time() < end:
        root.update()

def entry(field):
    return field._internal._entry

def say(*a):
    print(*a); sys.stdout.flush()

def lines():
    return w["log"]().count("bootstack:")

def type_into(field, text, *, clear=True):
    e = entry(field)
    e.focus_force(); pump(0.15)
    if clear:
        e.delete(0, "end")
    for ch in text:
        e.insert("end", ch)
        e.event_generate("<KeyRelease>", keysym=ch if ch.isalnum() else "space")
        pump(0.11)
    e.event_generate("<FocusOut>")
    pump()

def report(field, label):
    say(f"   {label:12} valid={str(field.valid()):5} error={field.error()!r}")

pump(0.3)

say("panel 1  wrong type, `v > 5` on a TextField -- everything raises")
before = lines()
type_into(w["wrong"], "6")
report(w["wrong"], "'6'")
type_into(w["wrong"], "abcdef")
report(w["wrong"], "'abcdef'")
say(f"   console lines for 7 keystrokes across 2 values: {lines() - before}  (expect 1)")

say("panel 2  converts, `int(v) > 5` -- judges '6', raises on 'abc' and empty")
type_into(w["converts"], "6");   report(w["converts"], "'6'")
type_into(w["converts"], "abc"); report(w["converts"], "'abc'")
type_into(w["converts"], "");    report(w["converts"], "empty")

say("panel 3  guarded -- a verdict for every input, console silent")
before = lines()
for text, label in [("6", "'6'"), ("2", "'2'"), ("abc", "'abc'"), ("", "empty")]:
    type_into(w["guarded"], text); report(w["guarded"], label)
say(f"   console lines added by the guarded predicate: {lines() - before}  (expect 0)")

say("panel 4  right type, `v > 5` on a NumberField -- console silent")
before = lines()
for text, label in [("6", "6"), ("4", "4")]:
    type_into(w["right"], text); report(w["right"], label)
say(f"   console lines added by the NumberField: {lines() - before}  (expect 0)")

say("panel 5  manual -- expect False returned, not a raise")
try:
    say("   validate() ->", w["manual"].validate())
except Exception as exc:
    say("   validate() RAISED", type(exc).__name__, exc)

say("")
say(f"TOTAL console lines: {lines()}  (one per raising rule, never one per keystroke)")
sys.stderr = real_stderr
root.destroy()
