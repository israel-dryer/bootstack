# REVIEW — #486 round 1

**Branch:** `fix/textarea-signal-binding-486` at `51631a07`
**Base:** `main` at `17765718`
**Round 1 of 3.** Gate 1 satisfied — `git diff main...HEAD -- src/` is four files,
49 insertions.
**Reviewer session wrote none of this code.** `PLAN.md` was read first; its design,
its two rejected alternatives and its measurements are not re-derived here.

**Verdict: THE FIX WORKS. ONE SHOULD-FIX DEFECT IN THE NEW CODE — NOT A
REGRESSION, NOT BLOCKING.** The write-back is correct for content and wrong for
chrome in exactly one state: a `TextArea` built with both `placeholder=` and
`textsignal=` writes the placeholder string into the caller's signal while the
placeholder is on screen. Everything else the round looked at came back clean, and
the cleared items are recorded below so round 2 does not pay for them again.

⚠⚠ **AN EARLIER VERSION OF THIS RECORD CALLED FINDING 1 BLOCKING AND SHOWED `main`
AS "CLEAN". BOTH WERE WRONG, AND THE SECOND CAUSED THE FIRST.** The first probe
only asked *"is the placeholder string in the signal?"* — a pollution detector, not
a correctness one — so `main` scored clean by being **inertly stale**: it never
wrote anything back at all, which is the defect #486 exists to fix. Scored against
the invariant a two-way binding actually claims, `sig() == widget.value`, the
numbers reverse. **Do not re-derive this; it is the round's main correction.**

---

## The fix works — scored against `sig() == widget.value`

Five steps: focus an untouched field, type, clear, blur while empty, refocus.

| step | `main` | branch, no placeholder | branch, placeholder |
|---|---|---|---|
| focused, untouched | OK | OK | OK |
| user types | **WRONG** | OK | OK |
| user clears | **WRONG** | OK | OK |
| blur while empty | **WRONG** | OK | **WRONG** |
| refocus | **WRONG** | OK | OK |
| **disagreements** | **4 of 5** | **0 of 5** | **1 of 5** |

`main` reads `'hello'` — the last value its own code wrote — in every state,
because the binding never travelled back. **Every state `main` gets right, the
branch also gets right.** The branch is a strict improvement, and Finding 1 is a
new defect in new code rather than a regression against anything that worked.

---

## Finding 1 — SHOULD FIX: the placeholder is written into the bound signal

`bs.TextArea(placeholder="…", textsignal=sig)`. The user clears the field and tabs
away. `sig()` becomes `"Type something here"` — the placeholder — while
`widget.value` reports `""`. Two public reads of the same widget disagree, and
whatever the application does with that signal (persist it, validate it, mirror it
into a `bs.Label`) receives UI chrome as if it were data.

**Measured, both arms, real focus move, public API only** —
`development/probe_486_review_round1.py`:

```
BRANCH   after clear : sig=''       after blur : sig='Type something here'   *** POLLUTED ***
MAIN     after clear : sig='hello'  after blur : sig='hello'                 stale in both
```

⚠ **Read that `MAIN` row as STALE, not as correct** — see the correction above. What
it shows is that the placeholder string could not previously reach a signal,
because nothing could. **The failure mode is new; the state it occurs in was
already wrong.**

⚠ **The control is what bounds the finding.** Arm 2 runs the identical sequence on
a `TextArea` with **no** placeholder and is clean on **both** arms (`''` throughout
on the branch, 0 of 5 disagreements). A POLLUTED row is therefore the placeholder
and not the write-back in general.

**Why it is still worth fixing here rather than filing:** the fix is local and the
guard already exists one layer up (below), it is reachable from two documented
constructor keywords of the same widget, and shipping a two-way binding that can
put UI chrome into an application's data model is a worse thing to explain than a
one-line guard is to write. **But it does not gate the merge on its own** — a
maintainer who wants #486's two directions now and this state later is choosing
between two defects, not between a defect and a regression.

**Cause — a layering mismatch, and the composite already contains the guard that
is missing.** `_show_placeholder` (`_impl/composites/textarea/textarea.py:239`)
inserts the placeholder into `core.text`. That insert rides the `WidgetRedirector`
like any keystroke, so `ChangeNotifier` fires `<<Change>>`, and the new
`_push_to_signal` — which lives on the **core** — reads `core.value` and pushes it.
`core.value` is the raw document, so it *is* the placeholder text. The composite's
own `<<Change>>` subscriber, `_on_core_change` (`:341`), opens with
`if not self._showing_placeholder:` for exactly this reason. The new subscriber was
added one layer below the layer that knows the difference.

**Reachability is ordinary, not contrived.** `placeholder=` and `textsignal=` are
both documented constructor keywords of the same widget; `placeholder=` appears in
four of `docs/widgets/textarea.rst`'s own examples. No shipped doc happens to
combine them, so the docs do not demonstrate the bug — that is luck, not coverage.
`CodeEditor` has no placeholder and is unaffected.

⚠ **ONE NOTE FOR WHOEVER FIXES IT, SO THE OBVIOUS ANSWER IS NOT WRONGLY REJECTED:
`_showing_placeholder` IS NOT THE SUSPEND FLAG THE PLAN FORBIDS.** The plan's ban is
on a flag *raised around a write and lowered immediately*, which a `when="tail"`
event outlives. `_showing_placeholder` is durable state that stays `True` for as
long as the placeholder is on screen, so it is still `True` when the tail delivery
arrives — measured: the pollution happens **with the flag set**. Consulting it is
sound; the echo guard's value comparison stays as it is.

The direction the fix must **not** grow into: the mirror-image bug
(`_on_signal_change` writes through `core.value`, which does not clear
`_showing_placeholder`, so a model write while the placeholder shows leaves the
widget displaying the text while `widget.value` says `""`) is **identical on both
arms** and is therefore pre-existing and out of scope. Measured, same probe run.

---

## Notes — recorded, not fixes

**N1. Two-way binding doubles the per-keystroke cost, and it scales with document
size.** `_push_to_signal` does a full `text.get("1.0","end-1c")`, a full string
compare, and a full `Signal.set` on every `<<Change>>`. Measured on a 480 KB /
6000-line `CodeEditor` with a signal bound: **1.99 ms per keystroke on `main`,
3.92 ms on the branch.** Still inside a frame budget at this size, linear beyond
it, and only paid when a signal is bound. This is inherent to the contract the
issue asks for — `TextField` pays the same shape on one line — so it is **not a
defect and not a fix**. Recorded with the number so a later `CodeEditor`
performance report is not re-derived from scratch.

**N2. `test_a_destroyed_widget_stops_receiving_and_raises_nothing` names an
observable that is not the one that fires.** Its docstring says the emit happens
inside a Tk trace where the background-error channel is the only observable. It is
not: the signal is unrealized, so `Signal.set` notifies Python subscribers
**synchronously**, and on `main` the control fails with a `TclError` propagating
straight out of `sig.set(...)` — verified by reading which line went red, per the
#476 lesson. So `assert not seen` is the assertion that **cannot** fail here, and
the load-bearing one is the implicit "`sig.set` did not raise". Not vacuous today
(it is red on `main` and green here for the right reason) and not a false alarm, so
under gate 2 it is a note. ⚠ **It would become vacuous the moment anyone wraps that
`sig.set` in a `try`.**

**N3. `test_alternating_writes_do_not_echo` asserts `fired <= 25`; the measured
value is exactly 20.** The slack is correct and deliberate — a feedback loop is
unbounded, not slightly over — and a tighter bound would buy nothing and could
flake. Recorded only so it is not "tightened" later.

---

## Checked and cleared — do not re-derive these in round 2

- **`off_change(bind_id)` does not wipe its siblings.** The obvious hazard was
  tkinter's historical `unbind(seq, funcid)`, which dropped **every** binding for
  the sequence — and `core.text` carries five other `<<Change>>` bindings
  (`_on_core_change`, `CodeEditor`'s typed-change emitter, the line-number sidebar,
  the search overlay, user callbacks). On the project's **3.12 floor**
  (`requires-python = ">=3.12"`), `Misc._unbind` removes only the named binding.
  Measured: after a rebind, an unrelated `<<Change>>` handler still fires.
- **The refusal is wider than the plan's `int` example and is still consistent.**
  `signal.type is not str` rejects **any** non-`str` type, `NoneType` included, so
  `bs.TextArea(textsignal=bs.Signal(None))` is accepted on `main` and refused here.
  That is inside the maintainer's decision, and **`TextField` refuses `Signal(None)`
  with the byte-identical message** — measured, all three widgets return
  `Expected NoneType, got str`. The consistency claim holds beyond the case the
  test pins.
- **Clearing a bound field does not raise.** `Signal.set('')` goes through
  `_reconcile`, where `''` is an ordinary `str`; `allow_empty` is not involved. So
  emptying a `TextArea` bound to a plain `bs.Signal("…")` is safe.
- **The destroy change has a blast radius of exactly one widget.** `core.bind()` is
  overridden to `self.text.bind()`, so the `<Destroy>` handler only ever receives
  the inner `Text`'s own destroy and `_unbind_signal()` runs once. The plan's
  decision to leave the rest of the block behind the dead guard (#488) is respected
  by the diff. ⚠ Minor: the code comment says "any Destroy in this subtree", which
  overstates it — there is only ever one.
- **Chrome-versus-content sweep is complete.** `grep -rn "text\.insert\|text\.delete"`
  over the textarea package returns the placeholder pair, search-and-replace, undo,
  smart-indent and the core's own setters. **The placeholder is the only one that
  writes something that is not the user's content**, so Finding 1 bounds the class.
- **CHANGELOG is accurate.** Its claim that "single-line fields have always refused
  the same thing with the same message" is verified against `main` for both `int`
  and `NoneType`. The upgrade warning about subscribers firing on user edits is the
  right half to headline.
- **Suite: 1680 passed / 22 skipped, 33 legs, exit 0**, `py -3.12 tests/run_gui.py`,
  Windows box. Matches the plan. Movement bounded rather than eyeballed:
  `git diff main...HEAD --stat -- tests/` returns exactly one new file, and
  `1661 + 19` is that file's collection.
- **Controls on the new tests were run**: 15 of 19 fail against `main`'s source, and
  the write-back failures are behavioral (the signal simply never changes), not
  `AttributeError`.
- **`git diff main...HEAD -- CLAUDE.md` is empty.**
- **The `invalid command name "…_delete_command"` / `"…<lambda>"` noise the probe
  prints at teardown is NOT this branch's.** It appears identically on both arms and
  comes from destroying the `App` directly out of a script; it is the deferred
  `deletecommand` family this project already documents. Not chased, not a finding.

---

## Process

⚠ **`PLAN.md` is still at the branch root and there is no `REVIEW.md` in
`development/` yet.** Both must be archived into `development/` **before the PR
opens** — three of the last five branches merged with a plan left in `main`'s root.
⚠ And **`git add` the moved file after the `git mv`**: `git mv` stages the rename
of the *indexed* blob, so edits made before it stay unstaged and the rename ships at
100% similarity with a message describing content the commit does not contain.

**Round 1 of 3 spent. No blocking findings. One should-fix defect in new code; a
fix plus its `docs(review):` record closes the round.**

---

## Round 1 fix — Finding 1 closed

**Fixed at the layer that knows the difference.** `_push_to_signal` lives on the
core, which holds the raw document; the placeholder is chrome the composite
*inserts into* that document to render it, so the core cannot tell content from
chrome on its own. The core now reads through a seam, `_signal_text_source`, and
the composite installs its own public `value` as the reader — so a bound signal
carries exactly what the widget reports through every other observable. Two
files, 16 insertions.

⚠ **The seam is installed BEFORE `bind_signal`, not after.** `bind_signal` seeds
the widget and that seeding fires `<<Change>>`, so a reader installed afterwards
leaves a window in which a push can run against the raw document.

**`CodeEditor` has no placeholder and installs no reader**, so it keeps the plain
`self.value` default and is untouched by this.

### Verified against the finding's own instrument

`development/probe_486_review_round1.py`, unchanged, both states:

| step | before the fix | after |
|---|---|---|
| blur while empty, placeholder | `sig='Type something here'` **WRONG** | `sig=''` OK |
| disagreements, placeholder=True | **1 of 5** | **0 of 5** |
| disagreements, placeholder=False | 0 of 5 | 0 of 5 |

### The finding was verified as a real defect before it was fixed, on evidence round 1 did not use

Round 1 argued from the family. Two stronger lines were measured first, because
"the placeholder is in the signal" is only a defect if the placeholder is not
content — and that had been asserted, not shown.

**1. The widget already contradicted itself.** With the placeholder showing,
four public observables of the same `TextArea` disagreed, and only one was new:

| observable | reported |
|---|---|
| `ta.value` | `''` |
| `on_change` | nothing fired |
| `on_input` | nothing fired |
| **the bound signal** | **`'Type something here'`** |

`_on_core_change` and `_on_focus_out` both open with
`if not self._showing_placeholder:`, and `value` returns `""` for the same
reason. The composite had already decided a placeholder is not content, in three
places. The write-back was added one layer below that decision. **This settles it
without appealing to any other widget.**

**2. The entry-backed family solved the identical problem on purpose and says so
in a comment.** `_parts/textentry_part.py:111` — *"uses textvariable detach so
the Signal is never set to the placeholder text"*; `_show_placeholder` does
`configure(textvariable='')` and `_hide_placeholder` reattaches. Load-bearing
machinery whose stated purpose is this exact hazard.

**3. Measured against that exemplar** —
`development/probe_486_placeholder_family.py`, real focus moves, public API only.
⚠ **Its `on type` column is what makes the comparison admissible**, and it is the
correction of round 1's own mistake in reverse: it proves each arm's write-back
is *live*, so a clean arm is a widget that COULD have polluted and did not,
rather than one scoring clean by writing nothing at all.

| arm | on type | on blur, `sig()` | verdict |
|---|---|---|---|
| `TextField` placeholder + signal | `'typed by user'` | `''` | clean |
| `TextArea` placeholder + signal, before | `'typed by user'` | `'Type something here'` | **PLACEHOLDER IN SIGNAL** |
| `TextArea` placeholder + signal, after | `'typed by user'` | `''` | clean |
| `TextArea` control, no placeholder | `'typed by user'` | `''` | clean |

**It also decided the shape of the fix.** The composite already suppresses the
placeholder at construction when a signal is bound (`textarea.py:190`), which
could have meant the intent was "a bound signal means no placeholder at all".
Measured: `TextField` shows the placeholder on blur *with* a signal bound
(`showing=True`). So the family shows the placeholder and keeps it out of the
signal — guard the write-back, do not hide the placeholder.

### Tests — three added, `TextArea` only, and one of them is the anti-vacuity control

- `test_the_placeholder_never_reaches_the_bound_signal` — the finding, with
  `_showing_placeholder is True` asserted as a **precondition**, without which it
  passes vacuously in exactly the state the defect needs.
- `test_every_observable_agrees_while_the_placeholder_shows` — pins the invariant
  the finding actually broke, across all four readers at once.
- ⚠ `test_a_placeholder_does_not_switch_the_write_back_off` — **the control that
  bounds the guard.** Suppressing the write-back entirely whenever `placeholder=`
  was passed satisfies the other two while reinstating the one-way binding #486
  exists to remove. It asserts an edit still travels on a widget that HAS a
  placeholder.

**All three fail against the pre-fix source, and the failing line was read in
each rather than the red taken at face value** (#476's lesson):

| test | assertion that went red |
|---|---|
| never reaches | `sig() == ""` — the precondition passed |
| observables agree | `pushes == []` — **`changes == []` and `inputs == []` passed first**, so the signal is demonstrably the only reader that disagreed |
| write-back not off | the final `sig() == ""` — `sig() == "typed by user"` passed first |

### Verification

- **Suite: 1684 passed / 22 skipped, 33 legs, exit 0**, `py -3.12 tests/run_gui.py`,
  Windows box. Reconciles from two directions: `main` is 1661,
  `git diff main...HEAD --stat -- tests/` returns exactly one new file, and that
  file collects 23. The four `failed|error` matches in the log are test
  **filenames**.
- **Line endings:** the appended tests were written LF into a CRLF file and were
  normalized back to CRLF (96 bare LF lines). ⚠ `git diff` cannot see this;
  `file` was what caught it.

### Not done, deliberately

- **The mirror-image bug stays out of scope**, as round 1 scoped it: a model write
  while the placeholder shows goes through `core.value`, which does not clear
  `_showing_placeholder`. **Identical on both arms — pre-existing.**
- **`TextField.value` reads `None` after a setter-clear while its signal reads
  `''`.** Found while building the family probe. Reproduces with **no signal
  bound**, on a widget this branch's diff does not touch. Pre-existing and
  unrelated; recorded here only so the next reader does not re-chase it. ⚠ It is
  also why the probe asks "did the placeholder STRING reach the signal" rather
  than comparing `sig()` against `widget.value` across families — the two
  families spell empty differently, and that comparison flags a working widget.
- **CHANGELOG is unchanged.** The polluted write-back never shipped, so there is
  nothing for a reader asking "was I affected?" to be told.

**Round 1 closed. Two rounds remain under the cap. Round 2 must be a fresh
session — this one wrote the fix.**

---

## ⚠⚠ ROUND 1 FIX, SECOND PASS — THE READER SEAM ALONE WAS A REGRESSION, AND A DEMO CAUGHT IT, NOT THE SUITE

**A reader without a writer silently reverts `sig.set(...)` from application
code.** Measured while smoke-testing a demo built for the maintainer to click
through — the suite was green, all 22 tests passed, and the branch was wrong.

`_on_signal_change` wrote the **core's raw document**, which does not clear
`_showing_placeholder`. So with the placeholder up: the write lands in the
document, `<<Change>>` fires, the new reader answers `""` because the flag is
still set, and the push sends that `""` **straight back over the caller's
value**. The signal ends at `''` and the text vanishes.

| after `sig.set("written by code")` with the placeholder showing | on screen | `.value` | `sig()` |
|---|---|---|---|
| committed branch head, before any of this | `'written by code'` | `''` | `'written by code'` |
| **reader seam only — the regression** | **`''`** | **`''`** | **`''` — WRITE LOST** |
| reader + writer seam, shipped | `'written by code'` | `'written by code'` | `'written by code'` |

**Fixed by making the seam symmetric.** `_signal_text_sink` is the write half;
the composite installs its own `value` setter, which clears the placeholder
before writing. Both halves are installed together, before `bind_signal`, and
`bind_signal`'s own seeding goes through the applier too. The rule is that the
two halves must **agree about what the widget's text is** — a reader that says
`""` and a writer that fills the raw document cannot both be right.

⚠ **THIS PULLS THE MIRROR-IMAGE BUG INTO SCOPE, AND THAT IS FORCED RATHER THAN
CHOSEN.** Round 1 scoped out "a model write while the placeholder shows leaves
the widget displaying text while `value` says `''`" as pre-existing. The writer
seam fixes it as a consequence, because routing through the composite's setter
*is* the fix for it. There is no version of this change that keeps the reader and
leaves that behavior alone — the alternative is data loss. **`TextArea` now
reports the same thing through screen, `value` and signal in this state.**

**New test, and it is the one the suite did not have:**
`test_a_code_write_while_the_placeholder_shows_is_not_reverted`. Controlled
against the reader-only arm — fails with `the widget reverted the caller's write:
''`, on the load-bearing assertion, precondition passing first.

⚠⚠ **THE LESSON, AND IT IS THE ROUND'S SECOND CORRECTION: EVERY TEST HERE DROVE
THE WIDGET AND THEN THE MODEL, NEVER THE MODEL WHILE THE WIDGET WAS IN THE STATE
THE FIX TOUCHED.** That is #390 round 3's finding in a new place — a feature with
two doors into the same code, tested through one. The placeholder tests all
reach the placeholder state by *editing*, so none of them ever wrote a signal
while it was up. **A demo built for a human to click through found it in one
run.** Clicking through the states is not a lesser instrument than the suite.

**Suite after the second pass: 1684 passed / 22 skipped, 33 legs, exit 0.** (Superseded below: 1687 after the edit-door tests.)
`1661 + 23`, one new test file, collection checked.

**Demo:** `development/demo_486_textarea_signal.py`, module-level `with bs.App(...)`,
readouts bound through `Signal.map` so they are real subscribers. Step 3 is the
regression above. It labels the TextField `value: None` readout as **#482**, so a
known pre-existing lag is not misread as this branch's.

---

## ⚠ CORRECTION TO THE FIX'S STATED PRINCIPLE — "the signal carries what `value` reports" IS NOT A FAMILY INVARIANT

Raised by the maintainer running the demo: *"textfield changes on blur, and text
changes on keypress"*, and *"textfield shows 'written by code', but not in
value"*. Measured with **real key events**, which no test in this file uses --
they all drive the programmatic setter, which is a different door.

| after | `TextField.value` | `TextField` signal | `TextArea.value` | `TextArea` signal |
|---|---|---|---|---|
| key `a` | `''` | `'a'` | `'a'` | `'a'` |
| key `b` | `''` | `'ab'` | `'ab'` | `'ab'` |
| key `c` | `''` | `'abc'` | `'abc'` | `'abc'` |
| blur | `'abc'` | `'abc'` | `'abc'` | `'abc'` |

**The two SIGNALS are identical — both push on every keystroke.** So the
write-back's granularity matches the family exactly, which is what #486 is about.
What differs is `.value`: `TextField` is **commit-scoped** (blur or Enter, the
field family's documented change model) while `TextArea.value` is the live
document. Pre-existing, by design, and `TextField` is not in this diff.

⚠⚠ **BUT IT INVALIDATES HOW THIS RECORD FRAMED THE FIX.** The round 1 fix section
above says a bound signal "must carry what `value` reports". That is true of
`TextArea` and **false of `TextField` while typing**, so it is not the family rule
and must not be quoted as one. **The invariant that actually justifies the fix is
narrower: a visible placeholder is not content.** That is what `field.py:285`
states, what the textvariable detach implements, and what `TextField` upholds in
every state — including the ones where its `value` and its signal disagree.

**The code is unaffected** — the composite's `value` is still the right reader for
`TextArea`, because for `TextArea` the two coincide. Only the justification was
overstated.

⚠ **The second observation is #482** — after a code write `TextField.value` reads
`None` until the next commit. Pre-existing, filed, reproduces with an ordinary
signal. The demo now labels both on screen, because a reviewer running it will hit
the same two questions.

⚠ **AND THE GAP THAT PRODUCED THE OVERSTATEMENT IS THE SAME ONE AS THE PASS-1
REGRESSION: EVERY TEST IN THIS FILE DRIVES `widget.value = ...`, NEVER A REAL
KEYSTROKE.** The programmatic setter and the keyboard are two doors into the
write-back and only one is tested. Nothing measured here is a defect — but round 2
should decide whether that is a coverage hole worth filing.

---

## Round 1 fix, third pass — the edit door is covered now

The gap named twice above is closed: every test in this file drove
`widget.value = ...`, so the other door into the write-back — an actual edit —
was untested, and both of this branch's own problems came through it.

**Two tests added.** `test_an_incremental_edit_reaches_the_signal` (both widgets)
asserts after **every character**, because a write-back that only fired on
whole-document replacement — all the setter tests can see — still passes a single
end-state assertion. `test_clearing_by_editing_then_blurring_keeps_the_placeholder_out`
reaches the finding's own scenario through an edit rather than the setter.

⚠⚠ **THEY DRIVE `text.insert` / `text.delete`, NOT SYNTHESIZED KEYS, AND THAT WAS
MEASURED BEFORE IT WAS CHOSEN.** A `<KeyPress-a>` generated in the shared-root
suite **does nothing**: the root is withdrawn, `focus_force` is a silent no-op on
an unmapped widget, the key never reaches the Text's class bindings, and the
document stays empty — `doc='' sig=''` against `doc='abc' sig='abc'` for the
insert arm, same test file, same fixture. **A keystroke-driven test here would
have been vacuous**, which is the standing repo rule against synthesizing keys in
the shared root, arrived at independently. `insert` rides the same
`WidgetRedirector` a keystroke does; the key-to-insert leg above it is the
toolkit's binding table, not ours.

**Controls, and the two kinds are different:**

- `test_clearing_by_editing_then_blurring_keeps_the_placeholder_out` **fails at
  the pre-fix source** on its load-bearing assertion — `the placeholder was
  written into the signal: 'Type something here'`, precondition passing first.
- The two incremental tests **pass** at the pre-fix source, because the committed
  head already has the write-back and only the placeholder guard is new. They are
  **regression guards, not fix-provers** — so they were run against **`main`** in
  a worktree with `PYTHONPATH` set and **provenance asserted**, where both fail on
  the **first** edit with `the signal did not follow edit 1: ''`. Behavioral, not
  an `AttributeError`. ⚠ Recording this because a control that passes on the arm
  you happened to try is indistinguishable from a vacuous test until you pick the
  arm that can disprove it.

**Suite: 1687 passed / 22 skipped, 33 legs, exit 0.** `1661 + 26`, one new test
file, collection checked, CRLF verified.

---

## ⏭ OPEN, DEFERRED BY THE MAINTAINER — the CHANGELOG says nothing about the released-line change

The forced scope expansion (the writer seam) changes behavior on the **released**
line, not only on unreleased work. On `0.3.2`, writing a bound signal while the
placeholder shows leaves the widget displaying the text while `value` returns
`""`; after this it returns the text. **Reachable from two documented constructor
keywords**, which is this project's own test for whether an entry is earned.

The `## [Unreleased]` bullet for #486 does not mention it. **Raised and
deliberately deferred (maintainer, 2026-08-28) — not overlooked, and not
decided.** The proposed sentence, if it is taken, appends to the existing bullet
rather than adding a second one, since it is the same issue and the same upgrade
decision:

> Writing to a bound signal while the placeholder is showing now updates the widget's `value` as well as what it displays; previously the text appeared on screen while `value` still reported an empty string.

⚠ **Do not re-derive this in round 2 and do not treat the silence as a decision.**
It is a promotion-time call at the latest, and `0.4.0` is the release that
promotes it.
