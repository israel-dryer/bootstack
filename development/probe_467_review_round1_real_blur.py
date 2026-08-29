"""Review probe #467: drive a REAL <FocusOut> through the debounced after() path.

Prints which arm it is on by reading the source of validation_rules.py.
Arms:
  1. custom func that raises, real blur   -> expect valid False (branch), stale True (main)
  2. CONTROL: func returning False, real blur -> proves the trigger fired at all
  3. CONTROL: func returning True, real blur  -> proves valid can still be True
"""
import pathlib
import time
import bootstack as bs

src = pathlib.Path(bs.__file__).parent / "validation" / "validation_rules.py"
ARM = "BRANCH (guard present)" if "custom validation rule raised" in src.read_text() else "MAIN (no guard)"
print(f"ARM: {ARM}")

bgerrors = []

def run(label, func):
    app = bs.App(title="probe", size=(320, 120))
    with app:
        field = bs.TextField(value="6")
        field.add_validation_rule("custom", func=func, message="must exceed 5", trigger="blur")
        other = bs.TextField(value="x")
    tkroot = field.tk.winfo_toplevel()
    tkroot.tk.createcommand("bgerror", lambda m: bgerrors.append(m))
    tkroot.deiconify(); tkroot.update()
    entry = field._internal._entry
    entry.focus_force(); tkroot.update()
    # a REAL focus change: move focus to the other field
    other._internal._entry.focus_force()
    tkroot.update()
    entry.event_generate("<FocusOut>")
    tkroot.update()
    # let the 50ms debounce fire
    end = time.time() + 1.0
    while time.time() < end:
        tkroot.update()
    print(f"  {label}: valid={field.valid()!r} error={field.error()!r}")
    tkroot.destroy()

try:
    run("arm1 raising func      ", lambda v: v > 5)
except Exception as e:
    print("  arm1 EXCEPTION out of the loop:", type(e).__name__, e)
try:
    run("arm2 control False func", lambda v: False)
except Exception as e:
    print("  arm2 EXCEPTION:", type(e).__name__, e)
try:
    run("arm3 control True func ", lambda v: True)
except Exception as e:
    print("  arm3 EXCEPTION:", type(e).__name__, e)

print("bgerror messages:", len(bgerrors))
for m in bgerrors[:3]:
    print("   ", str(m)[:120])
