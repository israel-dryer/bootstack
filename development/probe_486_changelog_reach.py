"""Which doors write into a TextArea while the placeholder is showing?

The #486 CHANGELOG bullet may need a sentence about a behavior change on the
RELEASED line: a write arriving while the placeholder is up used to leave the
text on screen while `value` still reported "". This asks how many ways in
there are, so the sentence is scoped to the ones the fix actually closes.

⚠ The textarea package is byte-identical between v0.3.2 and main
(`git diff v0.3.2..main -- src/bootstack/widgets/_impl/composites/textarea/`
is empty), so measuring on main IS measuring the released line.

Doors, each with the placeholder on screen:
  signal   sig.set(...)   -- the one the proposed sentence names
  insert   ta.insert(...) -- public method, NO signal involved
  append   ta.append(...) -- public method, NO signal involved
  setter   ta.value = ... -- the public setter, expected clean on both arms

Run on the branch, then on a worktree at main with PYTHONPATH set. ASCII out.
"""

import bootstack as bs

PLACEHOLDER = "Type something here"


def pump(app, n=6):
    for _ in range(n):
        app.tk.update()
        app.tk.update_idletasks()


def screen(ta):
    return ta._internal._core.text.get("1.0", "end-1c")


def report(door, ta, extra=""):
    shown = screen(ta)
    value = ta.value
    flag = ta._internal._showing_placeholder
    agree = (shown == value)
    print("  %-8s placeholder=%-5s screen=%-22r value=%-22r %s%s"
          % (door, flag, shown, value,
             "OK" if agree else "*** value LIES ***", extra))


app = bs.App(title="p486changelog", size=(600, 420))
app.__enter__()

sig = bs.Signal("hello")
ta_sig = bs.TextArea(placeholder=PLACEHOLDER, textsignal=sig)
ta_ins = bs.TextArea(placeholder=PLACEHOLDER)
ta_app = bs.TextArea(placeholder=PLACEHOLDER)
ta_set = bs.TextArea(placeholder=PLACEHOLDER)

app.__exit__(None, None, None)
app.tk.deiconify()
pump(app)

print("=" * 78)
print("SOURCE:", bs.__file__)
print("=" * 78)

# The signal widget suppresses its placeholder at construction, so bring it up
# the way a user does: empty the field and leave it.
ta_sig.value = ""
pump(app)
ta_sig._internal._core.text.event_generate("<FocusOut>")
pump(app)
assert ta_sig._internal._showing_placeholder, "precondition: placeholder not showing"
for w in (ta_ins, ta_app, ta_set):
    assert w._internal._showing_placeholder, "precondition: placeholder not showing"

print("all four start with the placeholder on screen")
print("-" * 78)

sig.set("written by code")
pump(app)
report("signal", ta_sig, "  sig=%r" % (sig(),))

ta_ins.insert("written by code")
pump(app)
report("insert", ta_ins)

ta_app.append("written by code")
pump(app)
report("append", ta_app)

ta_set.value = "written by code"
pump(app)
report("setter", ta_set)


# How stuck is the stuck state? `_on_core_change` and `_on_focus_out` both open
# with `if not self._showing_placeholder:`, so if the flag survives a code write
# the widget goes quiet as well as lying.
print("-" * 78)
print("after the signal write, does the widget still report edits?")
inputs, changes = [], []
ta_sig.on_input(lambda e: inputs.append(e.text))
ta_sig.on_change(lambda e: changes.append(e.value))
ta_sig._internal._core.text.insert("end", "!")
pump(app)
ta_sig._internal._core.text.event_generate("<FocusOut>")
pump(app)
print("  placeholder=%-5s value=%-24r on_input=%-3d on_change=%-3d %s"
      % (ta_sig._internal._showing_placeholder, ta_sig.value,
         len(inputs), len(changes),
         "OK" if (inputs and changes) else "*** EVENTS SUPPRESSED ***"))

print("=" * 78)
app.tk.destroy()
