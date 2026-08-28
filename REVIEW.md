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
