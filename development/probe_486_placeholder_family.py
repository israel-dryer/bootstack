"""#486 finding 1: is the placeholder reaching a bound signal EXPECTED?

The multiline write-back is new, so "does the placeholder land in the signal"
cannot be answered against main -- main writes nothing back at all, so it
scores clean by being inertly stale. The question this probe asks instead is
what the FAMILY does: TextField's two-way binding has shipped for releases and
is the exemplar #486 is being made to match.

Arm 1  TextField  placeholder + textsignal  -- the shipped exemplar
Arm 2  TextArea   placeholder + textsignal  -- this branch's new write-back
Arm 3  TextArea   no placeholder            -- control, bounds the finding

Same driver for all three: real focus moves, public API only.
"""

import bootstack as bs

PLACEHOLDER = "Type something here"


def pump(app, n=6):
    for _ in range(n):
        app.tk.update()
        app.tk.update_idletasks()


def run(factory, label):
    """focus -> type -> clear -> blur. Returns (on_clear, on_blur, widget.value)."""
    app = bs.App(title="probe486family", size=(500, 300))
    app.__enter__()
    sig = bs.Signal("hello")
    w = factory(sig)
    park = bs.TextField()
    app.__exit__(None, None, None)
    app.tk.deiconify()
    pump(app)

    w.focus()
    pump(app)
    w.value = "typed by user"
    pump(app)
    typed = sig()

    w.value = ""
    pump(app)
    on_clear = sig()

    park.focus()           # a REAL focus move, so <FocusOut> is not synthesized
    pump(app)
    on_blur = sig()
    value = w.value

    app.tk.destroy()
    return typed, on_clear, on_blur, value


print("=" * 78)
print("SOURCE:", bs.__file__)
print("=" * 78)

specs = [
    ("TextField  placeholder + signal",
     lambda sig: bs.TextField(placeholder=PLACEHOLDER, textsignal=sig)),
    ("TextArea   placeholder + signal",
     lambda sig: bs.TextArea(placeholder=PLACEHOLDER, textsignal=sig)),
    ("TextArea   CONTROL no placeholder",
     lambda sig: bs.TextArea(textsignal=sig)),
]

rows = [(label, ) + run(factory, label) for label, factory in specs]

print()
print("%-34s %-16s %-24s %-14s %s" % ("arm", "on type", "on blur sig()", "widget.value", "verdict"))
print("-" * 112)
for label, typed, on_clear, on_blur, value in rows:
    live = typed == "typed by user"
    polluted = PLACEHOLDER in str(on_blur)
    if not live:
        verdict = "no write-back -- cannot pollute, and cannot be a control"
    elif polluted:
        verdict = "*** PLACEHOLDER IN SIGNAL ***"
    else:
        verdict = "clean"
    print("%-34s %-16r %-24r %-14r %s" % (label, typed, on_blur, value, verdict))

print()
print("READING: the verdict asks ONE question -- did the placeholder STRING reach")
print("the signal. The 'on type' column is what makes an arm admissible: it proves")
print("the write-back is live, so a clean arm is a widget that COULD have polluted")
print("and did not, rather than one scoring clean by writing nothing at all. That")
print("is the error the round 1 probe made against main.")
print()
print("NOT A FINDING: TextField reports value=None after a setter-clear while its")
print("signal reports ''. That reproduces with no signal bound and on a widget this")
print("branch does not touch, so it is pre-existing and unrelated. It is why this")
print("probe does not compare sig() against widget.value across families -- the two")
print("spell empty differently, and that comparison would flag a working widget.")
