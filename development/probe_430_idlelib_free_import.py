"""Does the ported WidgetRedirector work, and is the import free of idlelib?

Written to run unchanged on Windows, macOS, and Linux. Only arm 1 depends on
the machine: it can be *proved* only where `idlelib` is absent, so everywhere
else it reports SKIP and the run continues. Arms 2-4 test the port's behavior,
which has nothing to do with whether idlelib happens to be installed — gating
them behind arm 1 left them runnable only on the one box that cannot finish the
GUI suite (#432), which is the opposite of what a probe is for.

  1. `import bootstack` succeeds at all, which is the bug being fixed.
  2. The redirector intercepts BOTH a Python-side call and one made through the
     Tcl command directly. The second is what a keystroke looks like, and it is
     the entire reason this class exists rather than a <Key> binding.
  3. close() puts the widget back, so a real CodeEditor can be built and torn
     down without leaving the Text broken.

Arm 2 carries its own control: an unregistered operation must pass through
untouched, or "it was intercepted" would prove nothing.

Run: py -3.12 development/probe_430_idlelib_free_import.py    (Windows)
     python development/probe_430_idlelib_free_import.py      (macOS, Linux)
"""
import platform
import tkinter as tk

import bootstack as bs
print(f"  0. platform                   : {platform.system()}, Tk {tk.TkVersion}")
print(f"  1. import bootstack           : OK, version {bs.__version__}")
print(f"     idlelib importable?        : ", end="")
try:
    import idlelib  # noqa: F401
    print("YES — arm 1 SKIPPED, only a box without idlelib can prove it")
except ImportError:
    print("no (so the port is what made arm 1 pass)")

from bootstack.widgets._impl.composites.textarea.redirector import (
    WidgetRedirector,
)

# The App is created first and owns the root: a CodeEditor needs one, and a
# second Tk root would be a different interpreter entirely.
with bs.App(title="port check", size=(500, 400)) as app:
    editor = bs.CodeEditor(language="python")

root = app.tk
root.update()

text = tk.Text(root)
text.pack()
root.update()

seen = []
redirector = WidgetRedirector(text)
original_insert = redirector.register(
    "insert", lambda *args: (seen.append(args), original_insert(*args))[1]
)

# --- arm 2a: a call written in Python ---------------------------------------
text.insert("end", "from python\n")
python_side = len(seen)

# --- arm 2b: a call through the Tcl command, which is what a keystroke does --
text.tk.call(text._w, "insert", "end", "from tcl\n")
tcl_side = len(seen) - python_side

# --- arm 2 control: an operation nobody registered must pass through ---------
text.tk.call(text._w, "mark", "set", "insert", "1.0")
after_control = len(seen)

content = text.get("1.0", "end-1c")
print(f"  2. intercepted a Python call  : {python_side == 1} ({python_side})")
print(f"     intercepted a Tcl call     : {tcl_side == 1} ({tcl_side})")
print(f"     control, unregistered op   : {after_control == 2} "
      f"(untouched, still {after_control})")
print(f"     text actually reached widget: {content.splitlines()!r}")

# --- arm 3: close() restores the widget -------------------------------------
redirector.close()
before = len(seen)
text.insert("end", "after close\n")
print(f"  3. close() stops interception : {len(seen) == before}")
print(f"     widget still usable        : "
      f"{text.get('1.0', 'end-1c').splitlines()[-1]!r}")

text.destroy()

# --- arm 4: the real thing, built and destroyed -----------------------------
editor_ok = "n/a"
try:
    # A CodeEditor builds a FilterChain, which is the only caller of the port
    # in the framework — so this exercises register/dispatch through the real
    # code path rather than a hand-built one.
    editor.value = "def hello():\n    return 1\n"
    editor.insert("# appended\n")
    root.update()
    round_trip = editor.value.strip().splitlines()
    editor_ok = f"OK, round-tripped {round_trip!r}"
except Exception as exc:  # noqa: BLE001 - reporting, not handling
    editor_ok = f"FAILED {type(exc).__name__}: {exc}"
print(f"  4. a real CodeEditor          : {editor_ok}")

root.destroy()
