"""#486 review round 1 — does the write-back push widget CHROME into the signal?

The finding: a `TextArea` built with BOTH `placeholder=` and `textsignal=` writes
the placeholder string into the caller's signal as soon as the user leaves an
empty field. The placeholder is inserted into the same Text the write-back reads,
one layer below the composite that knows it is chrome.

Run both arms. The probe prints which one it is on by reading the source, so a
mislabeled run cannot be read as a result.

    py -3.12 development/probe_486_review_round1.py                      # branch
    PYTHONPATH=<main-worktree>/src py -3.12 development/probe_486_review_round1.py

Expected:

    BRANCH   after blur : sig='Type something here'   *** POLLUTED ***
    MAIN     after blur : sig='hello'                 stale in every state

Arm 2 is the control that makes arm 1 mean something: the SAME sequence on a
TextArea with no placeholder must be clean on both arms, or the probe is
measuring the write-back rather than the placeholder.

⚠⚠ ARM 3 IS NOT OPTIONAL AND ARMS 1-2 MISLEAD WITHOUT IT. Arms 1 and 2 only ask
"is the placeholder string in the signal?", which is a POLLUTION detector, not a
correctness one — and by that question `main` scores clean while being wrong in
four states out of five, because a one-way binding never writes anything back at
all. Arm 3 scores every step against the invariant a two-way binding actually
claims, `sig() == widget.value`, and that is the arm that answers "did this fix it
or break it?": main 4/5 disagreements, branch 0/5 without a placeholder and 1/5
with one. Read arm 3 before quoting arms 1-2.
"""
import os

import bootstack as bs

_SRC = os.path.join(
    os.path.dirname(bs.__file__), "widgets", "_impl", "composites", "textarea", "core.py"
)
ARM = "BRANCH" if "_push_to_signal" in open(_SRC, encoding="utf-8").read() else "MAIN"


def pump(app, n=6):
    for _ in range(n):
        app.tk.update()
        app.tk.update_idletasks()


def run(placeholder):
    """Type, clear, blur, refocus. Returns the signal's value at each step."""
    app = bs.App(title="probe486", size=(500, 300))
    app.__enter__()
    sig = bs.Signal("hello")
    kw = {"textsignal": sig}
    if placeholder:
        kw["placeholder"] = "Type something here"
    ta = bs.TextArea(**kw)
    other = bs.TextField()
    app.__exit__(None, None, None)
    app.tk.deiconify()
    pump(app)

    ta.focus()
    pump(app)
    ta.value = ""          # select-all + delete, through the public setter
    pump(app)
    cleared = sig()

    other.focus()          # a REAL focus move, so <FocusOut> is not synthesized
    pump(app)
    blurred = sig()
    showing = ta._internal._showing_placeholder

    ta.focus()
    pump(app)
    refocused = sig()

    app.tk.destroy()
    return cleared, blurred, refocused, showing


print("=" * 72)
print("ARM:", ARM, "--", os.path.dirname(bs.__file__))
print("=" * 72)

print("\n[1] TextArea(placeholder=..., textsignal=...)   <- the finding")
cleared, blurred, refocused, showing = run(placeholder=True)
print("    after clear    : sig=%r" % (cleared,))
print("    after blur     : sig=%r   (placeholder showing=%s)" % (blurred, showing))
print("    after refocus  : sig=%r" % (refocused,))
print("    >>> *** POLLUTED ***" if blurred == "Type something here" else "    >>> clean")

print("\n[2] CONTROL: same sequence, no placeholder")
c2, b2, r2, s2 = run(placeholder=False)
print("    after clear    : sig=%r" % (c2,))
print("    after blur     : sig=%r" % (b2,))
print("    after refocus  : sig=%r" % (r2,))
print("    >>> control DIRTY -- probe is measuring the wrong thing"
      if b2 == "Type something here" else "    >>> control clean")


def score(placeholder):
    """Arm 3: agreement with the invariant, which is what decides fixed-vs-broke.

    A pollution check scores a one-way binding as clean, because it never writes
    anything back. `sig() == widget.value` does not.
    """
    app = bs.App(title="probe486", size=(500, 300))
    app.__enter__()
    sig = bs.Signal("hello")
    kw = {"textsignal": sig}
    if placeholder:
        kw["placeholder"] = "Type something here"
    ta = bs.TextArea(**kw)
    other = bs.TextField()
    app.__exit__(None, None, None)
    app.tk.deiconify()
    pump(app)

    rows = []

    def step(label):
        rows.append((label, sig(), ta.value))

    ta.focus(); pump(app); step("focused, untouched")
    ta.value = "typed by user"; pump(app); step("user types")
    ta.value = ""; pump(app); step("user clears")
    other.focus(); pump(app); step("blur while empty")
    ta.focus(); pump(app); step("refocus")
    app.tk.destroy()
    return rows


print("\n[3] AGREEMENT: does sig() match the widget's own public value?")
for placeholder in (False, True):
    print("    placeholder=%s" % placeholder)
    print("      %-20s %-24s %-16s %s" % ("step", "sig()", "widget.value", "agree?"))
    bad = 0
    for label, s, v in score(placeholder):
        ok = s == v
        bad += not ok
        print("      %-20s %-24r %-16r %s"
              % (label, s, v, "OK" if ok else "*** WRONG ***"))
    print("      --> %d of 5 steps disagree" % bad)
