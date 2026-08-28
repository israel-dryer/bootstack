# ★ HANDOFF — READ THIS FIRST (paused 2026-08-28)

**Branch `fix/modal-window-grab-444`, HEAD `fca6db6f`, off `main` at `a5f2c71d`.**

⚠⚠ **NOTHING BELOW IS COMMITTED. The round-1 fix lives in the WORKING TREE ONLY.** `git log` stops
at `fca6db6f`, which is the code round 1 found a blocker in — **the branch's last commit is the
BROKEN version.** Commits are held for the maintainer under the per-commit-approval agreement;
they were not withheld by accident.

⚠ **Run the FILTERED command, not bare `git status`** — `development/` carries ~70 pre-existing
untracked demo and verify scripts that have nothing to do with this branch, and a bare status buries
the six lines that matter in eighty:

```
git status --short -- src/ tests/ PLAN.md REVIEW.md development/probe_444_*
```

It should print exactly this:

```
 M PLAN.md                                        <- ONE line: the round count, 0 -> 1
 M src/bootstack/_runtime/grab.py
 M src/bootstack/_runtime/toplevel.py
 M tests/widgets/public/test_window_modal_grab.py
?? REVIEW.md
?? development/probe_444_grab_crossplatform.py    <- added 2026-08-28, see the ADDENDUM
?? development/probe_444_review_round1.py
```

**If that list differs, find out why before running anything.**

⚠ **`git status` ALSO shows two deletions that are NOT this branch's** and must not ride its
commit: `memory/feedback_demo_pattern.md` and `memory/feedback_no_v2_terminology.md`. They predate
the branch, they are the only two files in the repo's tracked `memory/` folder, and the "no v2" one
is already carried in the session memory store as `feedback_public_api_naming.md`. **Restore them or
decide them separately — do not stage them with #444.**

## What the 2026-08-28 session did — MEASUREMENT ONLY, no source touched

Prompted by the maintainer: *"when it comes to grab, you also have to take mac and linux into
account as well."* ⚠ **`git diff -- src/ tests/` is byte-for-byte what round 1's fix step left.**
That session added one probe and edited this file; it changed **no production code and wrote no
tests**.

- **Linux measured, first time on this branch.** Option B holds on X11, the grab tests pass 21/21,
  round 1's `reshow` probe reads 5/0, and the **full suite is exit 0, 1594 passed / 23 skipped**.
- **The no-platform-branch design is now MEASURED, not argued** — with a REAL global grab rather
  than the stub, which no box could safely do before an isolated display was used.
- **macOS is the whole remaining gap** and there is no route to it from this box.

**All of it is in the CROSS-PLATFORM ADDENDUM at the end of this file.** Read that before re-running
anything on another platform.

## State

| | |
|---|---|
| round 1 | **DONE** — 5 findings, all originating outside the author's risk list. Record below |
| fix step | **DONE** — findings 1-4 fixed, finding 5 deliberately not. Record below |
| round 2 | **NOT STARTED. Cap is 2, spent 1 — one round left** |
| suite | **exit 0, 33 legs, 1638 passed / 22 skipped**, measured on the final working tree |
| commit / PR | **neither.** No commit, no PR, nothing pushed |
| `CLAUDE.md` | **untouched on this branch, deliberately** — handoff state lives on `main` only. `git diff main...HEAD -- CLAUDE.md` is empty and must stay empty |
| platforms | **Windows + Linux measured; macOS NOT.** See the CROSS-PLATFORM ADDENDUM at the end of this file. Linux: 21 passed, option B holds, and a REAL global grab round-trips as `global` |
| suite, Linux | **exit 0, 33 legs, 1594 passed / 23 skipped** — WSL box under `xvfb-run` + `xfwm4`, 2026-08-28, against this working tree. ⚠ **Reconciles EXACTLY against the Windows figure and every difference is ENVIRONMENT** (absent `matplotlib`/`pandas`, Xvfb's missing display enumerator) — **none is platform behavior.** Table in the addendum |
| ⚠ standing directive | **"Let's not create a bunch of tests just to fill a testing gap. The goal is to fix things that are broken and not working."** (maintainer, 2026-08-28.) Gate 2 already said it — the two actionable test classes are vacuity and false alarm, and **coverage is not a defect.** This pass drifted past it once and was corrected; see *NOTE, NOT WORK* in the addendum |

## The next step, and it is not optional

⚠ **ROUND 2 NEEDS A FRESH SESSION. The session that wrote the fix cannot review it** — that is the
whole point of the boundary. **Hand the reviewer THIS FILE, not just the diff.** Round 1 was handed
`PLAN.md` and it paid for itself: the plan's out-of-scope list and its A/B measurement kept the
round off ground the author had already settled.

⚠ **The diff a round-2 reviewer wants is NOT `git diff main...HEAD -- src/`** — that range stops at
the broken commit. It is **`git diff main -- src/`** (working tree against `main`), or
`git diff -- src/` for the fix step alone.

⚠ **The 2026-08-28 pass does NOT consume the remaining round.** It ran probes and wrote no code, and
gate 1 says a round is triggered by a non-empty `git diff <range> -- src/` and nothing else. **Cap
is still 2, still spent 1.**

### Four things waiting on the maintainer, none of them a session's call

1. **Round 2** — one round left. A fresh session is the cleaner reviewer; the 2026-08-28 session
   wrote a probe and formed views on this branch, and although a probe is an instrument rather than
   reviewed code, it is no longer neutral about the area.
2. **The two untracked probes should ride the fix commit.** `development/` is tracked and all four
   plan-stage #444 probes are already in it — see the section on this in the addendum. One `git add`.
3. **The stray `memory/` deletions** — restore or decide, but keep them off the #444 commit.
4. **macOS.** The `ordering` arm is safe on that desktop and answers the design question in seconds;
   the global arms briefly grab the screen and need the env gate. Commands in the addendum.

⚠⚠ **ARCHIVE `PLAN.md` AND `REVIEW.md` INTO `development/` BEFORE OPENING THE PR, NOT AFTER.**
`CLAUDE.md` records that the last **two** branches — PR #478 and PR #480 — both merged them into
`main`'s root and archived afterwards, each caught only because the next session looked.

## Three residues, none of them mine to decide

⚠⚠ **1 AND 2 ARE NOW PARTLY CLOSED AND THE TEXT BELOW IS THE PRE-MEASUREMENT VERSION — read the
CROSS-PLATFORM ADDENDUM at the end of this file.** Measured on Linux 2026-08-28: option B holds on
X11, and a **real** global grab (not the stub) survives the round trip as `global`. **macOS is now
the whole of the gap**, and there is no route to that box from the Windows session.

1. **The global grab path is pinned only through a stub.** `bs.Window(modal="app")` restoring a real
   GLOBAL grab is untested **on Windows and macOS** — ✅ **it IS measured on Linux now, for real
   rather than through the stub; see the addendum** — because a real one would lock the machine running the
   suite out of every other application. #440 solved it the same way and for the same reason. The
   KIND is tested; what a global grab then *does* is not.
2. **The design decision was measured on Windows only — ✅ NOW ALSO ON LINUX, see the addendum.**
   `PLAN.md` chose option B — restore from a
   `<Destroy>` binding — over option A on a probe showing the restore wins its race with Tk's own
   grab release, run on this box. X11 differs, and this file already records that a global grab
   there can lose to another client. CI does run the new tests on ubuntu, so the OUTCOME gets
   cross-platform coverage; the RACE was never re-measured off Windows. ✅ **DONE 2026-08-28 on the
   WSL box** — option B holds on X11. ⚠ **The WSL run needs a window manager and `xfwm4` has NO
   `--daemon` flag**; a helper using it leaves the run with no display at all. Working helper and the
   control that proves it are in the addendum.
3. **Two smaller ones, recorded and latent.** `Toplevel.hide()` then a re-show is unmeasured — not
   publicly reachable, since `bs.Window` exposes no `hide()`, and the capture-once gate *should*
   make it correct, but "should" is the word. And `dialog.py:523` binds `<Destroy>` **without**
   `add="+"`, harmless today only because that toplevel is never modal.

## Re-run rather than re-deriving

```
py -3.12 development/probe_444_review_round1.py --arm reshow     # 5 restored / 0 lost after the fix
py -3.12 development/probe_444_review_round1.py --arm keyerror   # mechanism still reproduces; guard absorbs it
py -3.12 -m pytest tests/widgets/public/test_window_modal_grab.py tests/widgets/public/test_dialog_nested_modality.py -q
py -3.12 tests/run_gui.py
py -3.12 development/probe_444_grab_crossplatform.py ordering      # win32: OPTION B HOLDS
```

**Linux, from this Windows checkout** — the WSL clone is on a different commit, so point `PYTHONPATH`
at this tree and let the probe print its provenance rather than trusting the path. ⚠ **The helper is
required: `xfwm4` has NO `--daemon` flag**, and a run without a window manager reproduces #447 and
reads as a product bug. Helper source is in the addendum.

```
wsl -e bash -lc 'cd /mnt/d/Development/bootstack && BOOTSTACK_ALLOW_GLOBAL_GRAB=1   PYTHONPATH=/mnt/d/Development/bootstack/src   xvfb-run -a -s "-screen 0 1280x1024x24" /tmp/bs_wm.sh   /home/iddryer/.virtualenvs/bootstack/bin/python development/probe_444_grab_crossplatform.py'
```

Swap the trailing script for `tests/run_gui.py -q` for the full Linux suite (**1594 / 23, exit 0**),
or for `-m pytest <abs paths> -q` for the two grab files (**21 passed**).

**The control for the three new tests** — they must fail on the GRAB STATE, not on an import error:

```
cp src/bootstack/_runtime/{grab,toplevel}.py <somewhere-outside-the-repo>/   # keep the fix
git checkout fca6db6f -- src/bootstack/_runtime/grab.py src/bootstack/_runtime/toplevel.py
py -3.12 -m pytest tests/widgets/public/test_window_modal_grab.py -q        # expect 3 failed, 7 passed
cp <somewhere-outside-the-repo>/{grab,toplevel}.py src/bootstack/_runtime/  # put the fix back
```

⚠ **Revert the SOURCE only and keep the new tests in place** — that is what makes the failure
mean something. Reverting both leaves nothing to fail. And ⚠ **copy the fix somewhere OUTSIDE the
repo first**: it is uncommitted, so `git checkout` over it destroys it with no way back.

⚠ **Both probe arms carry their own controls and the record says what each control proves.** The
`keyerror` arm still shows `_nametowidget raises: KeyError 'popdown'` AFTER the fix — **that is
correct, not a regression.** The hazard did not go away; the guard absorbs it, and the arm exists to
keep the hazard visible.

---

# REVIEW — #444 round 1 (`fix/modal-window-grab-444`)

Reviewer session; a different session wrote the code. Range `git diff main...HEAD -- src/`,
branch head `fca6db6f`, off `main` at `a5f2c71d`. **Round cap 2, spent 1.**

`PLAN.md` was read before the diff, as asked. Its out-of-scope list, its A/B measurement and its
two cleared candidates are all taken as settled and are not re-litigated below.

## Where the findings came from

**Five findings, and all five originated OUTSIDE the author's risk list.** That list carried one
item — *the move touches shipped, tested code (#440)* — and it is **CLEARED**, checked three ways
rather than read: `dialog.capture_grab is canonical.capture_grab` and the same for `restore_grab`
(the branch's own test asserts it, and it passes); `datedialog.py:19` still imports both names
through `dialog.py` and resolves; and the eight call sites in `test_dialog_nested_modality.py`
plus the new file are **18 passed** together. The move is clean.

**Suite, measured on the branch head**, Windows box, `py -3.12 tests/run_gui.py`, `matplotlib`
and `pandas` both present: **exit 0, 33 legs, 1635 passed / 22 skipped.** Reconciles as
`1628 + 7` — `main`'s figure plus the new file's seven tests — and the movement is bounded by
`git diff main...HEAD --stat -- tests/`, which returns **one file, 198 insertions, and nothing
else**.

## 1. BLOCKING — a modal `bs.Window` restores the grab only if `show()` was called EXACTLY ONCE

`show()` stores the captured token **unconditionally** (`toplevel.py:234`), while
`_bind_grab_restore` guards itself against re-entry (`toplevel.py:257-259`). **The asymmetry is
the defect.** On a second `show()` the window already holds the grab, so `capture_grab(self)`
captures **itself** and the opener's token is discarded. On destroy the restore hands the grab
back to the window that is dying, and the opener gets nothing — **the exact #444 symptom this
branch exists to remove, silently reintroduced.**

Measured, `development/probe_444_review_round1.py --arm reshow`:

```
  block_until_closed() only  expected=('.!toplevel', 'local')   after=('.!toplevel', 'local')   RESTORED
  show() -> close()          expected=('.!toplevel3', 'local')  after=('.!toplevel3', 'local')  RESTORED
  show() -> show() -> close  expected=('.!toplevel5', 'local')  after=(None, None)              *** LOST ***
  show() -> block_until_cl.  expected=('.!toplevel7', 'local')  after=(None, None)              *** LOST ***
  show() -> show(anchor_to)  expected=('.!toplevel9', 'local')  after=(None, None)              *** LOST ***
```

**The two RESTORED rows are the control** — the probe can see a working restore, so a `LOST` row
is the fix not reaching that path rather than the probe failing to observe one. The captured
token itself was printed on the way through: after the first `show()` it is the opener
(`.!toplevel3`, `'local'`); after the second it is **the window itself**
(`bootstack._runtime.toplevel.Toplevel object .!toplevel4`).

⚠ **All three losing spellings are ordinary public API, not contrivances.**

- `win.show()` then `win.block_until_closed()` — and `block_until_closed()`'s own docstring says
  *"Show this window and block until it is destroyed"*, so it calls `show()` again itself. A
  caller who showed the window first, then decided to wait on it, reaches this.
- `win.show()` then `win.show(anchor_to=...)` — **re-anchoring is what the `anchor_to` parameter
  is for.** A window repositioned against a different widget on a second open is the parameter's
  own use case.
- Any plain double `show()`. `Window.show()` returns `self` for chaining and nothing marks it
  single-use.

**The single-show paths are correct and stay correct** — the fix works, its reach is one call
short. Not prescribing the edit, but the seam is `toplevel.py:234`: the capture needs the same
once-only treatment the binding already has, or to decline a token that names the window itself.

⚠ **The test file has NO `block_until_closed()` test at all** — the primary documented way to use
a modal window — and `test_a_modal_window_shown_without_blocking_also_hands_it_back` explicitly
names the blocking path as the one it is *not* covering. A test that showed the window and then
blocked on it would have caught this. Recorded as the reason it shipped, not as a separate
finding.

## 2. SHOULD-FIX (cheap) — `capture_grab` leaves `grab_current()` unwrapped, and it can raise `KeyError`

`grab.py:36` is `holder = widget.grab_current()`, outside any `try`. The `except (AttributeError,
tkinter.TclError)` two lines below guards only `grab_status()`. But tkinter's `grab_current()`
resolves the holder's path name through `_nametowidget`, which raises **`KeyError`** — a class in
neither except clause — for a window **Tcl** created without tkinter.

Measured, `--arm keyerror`:

```
  control (nothing posted): capture_grab -> None
  raw Tcl grab holder:      .!combobox.popdown
  _nametowidget raises:     KeyError 'popdown'
  capture_grab RAISED:      KeyError 'popdown'
```

A posted `ttk::combobox` popdown is such a window and it does hold the grab.

⚠ **BOUNDARY, stated because the mechanism and the route are different claims.** The *mechanism*
reproduces. **A live route to it inside `src/` was NOT found**, and the greps that bound that are
the claim, not the conclusion: `grep -rn "Combobox\|combobox" src/bootstack/ --include=*.py`
finds `widgets/_impl/primitives/combobox.py`, a real `ttk.Combobox` subclass with **zero
importers anywhere in `src/`**, and `selectbox.py:539-542` records that it builds its **own**
popdown rather than using the native one. So this is hardening, not a demonstrated defect.

**What makes it worth the one-line change anyway:** it is **newly reachable on this branch.**
Before it, `Toplevel.show()` never called `capture_grab` at all. And unlike `restore_grab` — which
runs on teardown and deliberately swallows — `capture_grab` runs on a **setup** path, so a raise
there escapes `Window.show()` into the application.

## 3. NOTE — the shared module still speaks only of dialogs

`grab.py`'s module docstring names both #440 and #444, but the function docstrings underneath it
did not move on: `restore_grab` is *"Hand the modal grab back to whatever held it before **this
dialog** took it"*, *"a **dialog** that has already closed must not raise on its way out"*, and
the string it actually emits is **`"could not restore the previous dialog's grab"`** —
`grab.py:91`. That line is now what a maintainer reads when a **window** grab fails to restore,
which is the one moment this code has an observable at all. Debug-only and internal, so a note.

## 4. NOTE — `show()` binds the restore only if `focus_set()` also succeeded

`toplevel.py:235-244` puts `grab_set()`/`grab_set_global()` **and** `focus_set()` in one `try`,
and hangs `_bind_grab_restore()` off its `else`. A `TclError` from `focus_set` after the grab
already succeeded would leave a grab taken with no restore bound. **I could not construct it** —
`focus_set` is a silent no-op on an unmapped widget rather than a raise — so this is structural,
not demonstrated. The observation is only that the binding is a consequence of **the grab**, not
of the focus, and the `else` couples it to both.

## 5. NOTE (gate 2: not actionable) — `_StubHolder` is duplicated

`test_window_modal_grab.py:154-168` is a verbatim second copy of
`test_dialog_nested_modality.py:332-346`. Gate 2 confines test findings to vacuity and false
alarm; this is neither, and the tests are neither. **Recorded, not to be fixed.**

## What was checked and came back clean

- **The two paths are disjoint, verified independently of `PLAN.md`.** `Dialog._create_toplevel`
  (`dialog.py:511-517`) passes `master`, `window_style` and `transient` and **never `modal=`**, so
  `Toplevel._modal` is falsy on the dialog path, `show()`'s grab block never runs, and there is no
  double restore. The dialog takes its own grab at `:478`.
- **No competing `<Destroy>` binding on the window path.** `grep -rn '<Destroy>' src/bootstack/_runtime/ src/bootstack/widgets/window.py`
  returns only `app.py:159` (a `bind_all` for `Publisher.unsubscribe`) and the new binding itself.
  The new one uses `add="+"`. ⚠ Note for later: `dialog.py:523` binds `<Destroy>` **without**
  `add="+"` — harmless today only because that toplevel is never modal.
- **The `event.widget is not self` guard is necessary and correct.** A child's bindtags include
  its toplevel's path, so a descendant's `<Destroy>` does reach this binding.
- **`bs.Window` is the only route to `modal=`.** `grep -rn "modal=" src/bootstack/` puts every
  other hit on the dialog classes, which pass it to `Dialog.show`, not to `Toplevel`. The blast
  radius of both findings is exactly `bs.Window`.
- **`PLAN.md`'s three boundary greps were re-run and match what it recorded** — `grab_set`,
  `capture_grab|restore_grab`, `grab_release` across `src/` and `tests/`.
- **No unused imports left in `dialog.py`** by the move; `Any` and `tkinter` are still used
  throughout it.
- **The CHANGELOG entry is accurate as written**, including *"the same defect fixed for dialogs in
  `0.3.1`"* (#440 shipped there). ⚠ Its claim *"A closing modal window now returns the grab to its
  previous holder"* is only true once finding 1 is closed — no separate edit needed, it follows
  the fix.

## Verdict

**Finding 1 blocks.** It is the branch's own defect on a public path the branch does not test, and
the fix for it is at one line. Findings 2–5 are the maintainer's call; 2 is a one-line hardening
with its reachability honestly unproven, and 3–5 are notes.

**One round left under the cap.**
---

# FIX STEP — round 1

Applied to `src/bootstack/_runtime/toplevel.py`, `src/bootstack/_runtime/grab.py` and
`tests/widgets/public/test_window_modal_grab.py`. **Findings 1-4 fixed; finding 5 deliberately not
touched.** `PLAN.md` is untouched — it is the author's record.

## 1 (BLOCKING) — FIXED. The capture is gated on the same flag as the binding

`_previous_grab` and `_grab_restore_bound` are initialized in `__init__` rather than reached with
`getattr`, and `show()` now captures only `if not self._grab_restore_bound`. **The two guards share
one gate**, which is what makes the asymmetry impossible to reintroduce: a second `show()` on a
window that already took its grab does not capture again, so the opener's token survives.

⚠ **The gate is the BIND flag, not "have we captured before", and the difference matters.** If the
first `show()` captures and then `grab_set()` FAILS (Tk refuses a grab on a window that is not
viewable), nothing was bound, so a later `show()` captures again — correctly, because the window
still does not hold the grab and the opener still does. Gating on "captured before" would have
frozen a token taken at a moment the grab never moved.

**Measured, `probe_444_review_round1.py --arm reshow`, same probe and same controls as the
finding:**

```
  before:  restored 2   lost 3
  after:   restored 5   lost 0
```

Three tests added, and they FAIL on the pre-fix source **on the grab state**, not on an import
error or a missing attribute — the control ran with `git checkout fca6db6f -- src/bootstack/_runtime/`
and the new tests in place:

```
  E  assert (None, None) == ('.!toplevel8', 'local')     <- shown twice
  E  assert (None, None) == ('.!toplevel10', 'local')    <- shown then blocked on
  E  KeyError: 'popdown'                                 <- finding 2, below
  3 failed, 7 passed
```

- `test_a_modal_window_shown_twice_still_hands_the_grab_back`
- `test_a_modal_window_blocked_on_after_being_shown_hands_the_grab_back` — **the blocking path,
  which nothing covered at all.** ⚠ It **POLLS FOR THE MODAL GRAB** rather than closing on a fixed
  delay (`_close_when_modal`), which is #446's lesson; a fixed delay here would fire on a
  half-built window. The poll job is cancelled in a `finally`, and `closer` is bound before the
  `try` so the `finally` cannot raise `NameError` over the real failure.
- `test_capture_grab_degrades_to_none_when_the_holder_cannot_be_named` — finding 2.

## 2 (SHOULD-FIX) — FIXED. `grab_current()` is wrapped, and `KeyError` is in the clause

`capture_grab` now wraps the lookup in `except (AttributeError, KeyError, tkinter.TclError)`,
returns `None`, and **logs** — a holder we cannot address reads the same as no holder, and this is
the setup path where a raise escapes into the application. The docstring says which of the two it
is and why the degradation is `None`.

The test drives it through a stub that raises `KeyError` from `grab_current`, so it is
deterministic and takes no real grab. **The stub's docstring names the real instrument**
(`--arm keyerror`) rather than asserting the hazard is real, and that arm still shows the mechanism
reproducing after the fix — `_nametowidget raises: KeyError 'popdown'`, `capture_grab -> None`. **The
hazard did not go away; the guard absorbs it.**

## 3 (NOTE) — FIXED. The shared module no longer speaks only of dialogs

`restore_grab`'s summary is now *"before the caller took it"*, the teardown paragraph says *window*
where it meant either, the issue reference reads *"#440 for dialogs, #444 for windows"*, and the
emitted string is **`"could not restore the previous grab holder"`**. The concrete #440 example is
kept as an example and a `bs.Window(modal=True)` one added beside it. **No test asserted the old
string** — checked before changing it.

## 4 (NOTE) — FIXED. `focus_set()` no longer stands between the grab and its restore

`grab_set()`/`grab_set_global()` keep the `try`/`else` that binds the restore; `focus_set()` moved
to its own guarded call after it. The restore is owed because the grab was **taken**, so it is now
bound off the grab alone. **Behavior-preserving on every path I could reach** — it only removes the
coupling, and the finding said plainly that the failure was structural rather than demonstrated.

## 5 (NOTE) — NOT FIXED, on purpose

`_StubHolder` stays duplicated. Gate 2 confines test findings to vacuity and false alarm, and this
is neither. **Deduplicating it would be exactly the "symmetry between helpers" the protocol names
as a note, never a fix.**

## Verification

- `tests/widgets/public/test_window_modal_grab.py` + `test_dialog_nested_modality.py`: **21 passed**
  (was 18; the three new tests).
- Both probe arms re-run against the fix and recorded above.
- **Full suite, measured on the FINAL tree** (re-run after the last edit, not carried over
  from an earlier one), Windows box, `py -3.12 tests/run_gui.py`, `matplotlib` and `pandas`
  both present: **exit 0, 33 legs, 1638 passed / 22 skipped.** Bounded rather than eyeballed:
  `1635 + 3`, the branch head's figure plus this fix step's three tests, and
  `git diff --stat` says the only test file touched is the one they went into.

⚠ **The CHANGELOG needs no edit.** Its claim *"A closing modal window now returns the grab to its
previous holder"* was true only for a single `show()` when finding 1 was open; it is true
unconditionally now. **Do not add a caveat about re-showing — there is nothing left to caveat.**

⚠ **NOT COMMITTED.** Per the working agreement, commits wait for the user.

⚠ **ROUND 2 NEEDS A FRESH SESSION.** This session has now written code, so it cannot review it.
Hand it this file, not just the diff.

---

# CROSS-PLATFORM ADDENDUM -- Linux measured 2026-08-28

Added by a session that wrote no product code, on the maintainer's prompt: *"when it comes to
grab, you also have to take mac and linux into account as well."* **Residues 1 and 2 above were
understated.** They read as notes; residue 2 said the design decision was "measured on Windows
only". It was -- and so was the entire grab contract this branch rests on.

## The assumption nobody had measured, on ANY platform

`grab.py` carries **no platform branch, deliberately**: `capture_grab` reads the grab KIND back
from Tk and `restore_grab` hands back whatever Tk reported. Its docstring states the assumption
outright -- *"Reading the kind back from Tk rather than assuming it keeps this correct on every
window system without a platform branch."*

**That is an assumption about Tk, and it was unmeasured everywhere**, because both #440 and #444
pin the global path through a recording stub: a real global grab locks the machine running the
suite out of every other application. Residue 1 says as much -- *"the KIND is tested; what a
global grab then does is not."*

**An isolated Xvfb display removes that objection.** The grab can be taken for real there, which
is a thing the Windows box cannot safely do at all.

## The instrument

`development/probe_444_grab_crossplatform.py` -- three arms, runnable on every box (it skips and
continues rather than exiting, so one unavailable arm never hides the others).

| arm | question | safety |
|---|---|---|
| `ordering` | does the `<Destroy>` restore win its race with Tk's own release? | local grabs only -- **safe anywhere, including a live desktop** |
| `kind` | does `grab_status()` read back `"global"` after `grab_set_global()`? | **takes a REAL global grab.** Gated on `BOOTSTACK_ALLOW_GLOBAL_GRAB=1` |
| `restore` | does a displaced GLOBAL grab survive the round trip through the shipped helpers? | same gate |

`kind` carries its own **control**: a local grab must read back `"local"` first. If that fails the
reading mechanism is broken and the global row means nothing.

## Results

**Windows** -- this box, `py -3.12`, `win32`, Tk **8.6.15**. `ordering` only. **The global arms
were NOT run**: a real global grab on a live desktop locks the user out of their own machine, and
no isolated display is available here.

```
ARM ordering   outer ('.!toplevel','local') -> inner -> after ('.!toplevel','local')
               VERDICT: OPTION B HOLDS
```

**Linux** -- WSL box, `x11`, Tk **8.6.12**, under `xvfb-run` **with `xfwm4` running**, against
THIS WORKING TREE (`PYTHONPATH=/mnt/d/Development/bootstack/src`; the probe prints its provenance,
`bootstack loaded from: /mnt/d/Development/bootstack/src/bootstack`, so it measured the FIX and not
the WSL clone, which sits on a different commit).

```
ARM ordering   after the dust ('.!toplevel','local')            VERDICT: OPTION B HOLDS
ARM kind       control local -> 'local';  global -> 'global'    VERDICT: KIND IS FAITHFUL
ARM restore    outer ('.!toplevel4','global') -> inner local
               -> after restore ('.!toplevel4','global')        VERDICT: GLOBAL SURVIVES
```

Also on Linux, same harness:

- `test_window_modal_grab.py` + `test_dialog_nested_modality.py` -- **21 passed**, matching Windows.
- `probe_444_review_round1.py --arm reshow` -- **restored 5 / lost 0**, so round 1's blocking
  finding is closed on X11 too, not only on the box it was found on.

## Full Linux suite -- exit 0, and the count reconciles EXACTLY

`tests/run_gui.py -q` on the WSL box, under `xvfb-run` with `xfwm4`, against this working tree:
**exit 0, 33 legs, 1594 passed / 23 skipped, zero failures and zero errors.**

⚠ **`CLAUDE.md` says platform figures are NOT comparable and warns against closing a gap by picking
whichever number makes the arithmetic work.** So this was reconciled by diffing the SKIP REASONS on
both boxes, not by arithmetic:

⚠ **The Windows `1638 / 22` was CARRIED from round 1's fix step, not re-measured on 2026-08-28** —
legitimate only because `git diff -- src/ tests/` has not moved since. What WAS re-measured that day
is what the reconciliation actually leans on: the Windows **shared leg** (`1244 / 13`) and the two
small legs that skip (`test_capture.py`, `test_pagestack.py`), each run with `-rs` so the reasons
could be diffed line by line against Linux.

| | passed | skipped |
|---|---|---|
| Windows total (`matplotlib` + `pandas` both present) | 1638 | 22 |
| `test_chart.py` -- matplotlib ABSENT on WSL, collects **0** | -44 | +1 |
| `test_unknown_kwarg_strictness.py:55` -- matplotlib absent | -1 | +1 |
| data leg -- pandas ABSENT (`123/6` -> `125/4`, the documented pair) | +2 | -2 |
| `test_capture.py:51` -- *"no display layout available: No enumerators available"* under Xvfb | -1 | +1 |
| **Linux predicted** | **1594** | **23** |
| **Linux measured** | **1594** | **23** |

⚠⚠ **EVERY difference is ENVIRONMENT -- absent dependencies and Xvfb's missing display enumerator --
and NONE is platform behavior.** The proof is the skip lists, not the total: the shared leg's **13
scroll-event skips are identical on both boxes**, same line numbers and same counts (`133/149/165/188/208`,
`79`x3, `60`x5), and Linux's only two extra shared-leg skips both read *"could not import
'matplotlib'"*. **Nothing in this branch's area gates by platform.**

⏭ **A macOS note falls out of this for free, and it argues for #452.** `test_pagestack.py:40/60/80`
skip with *"keep-mapped navigation is macOS-only"* on **both** Windows and Linux. **There are already
three tests in this suite that can only ever run on the box with no CI leg**, so they have never been
executed by automation at all. That is independent of #444 and belongs to #452, but it is one more
reason the macOS gap is not merely this branch's.

## What this closes, and what it does not

- ✅ **Residue 2 is CLOSED for Linux.** Option B was the risk `PLAN.md` refused to assume, and it
  holds on X11 as well as win32.
- ✅ **Residue 1 is CLOSED for Linux, and better than the stub could ever show.** A real global
  grab is taken, displaced, and restored as `global`. The kind is faithful on X11, so the
  no-platform-branch design is measured rather than argued -- on one more platform than before.
- ❌ **macOS is UNMEASURED, all three arms.** No CI leg (#452) and no route to that box from here
  (no SSH config). This is the real remaining gap.
- ❌ **The Windows global arms are UNMEASURED** and will stay that way on a live desktop. Windows
  CI could run them, but only by adding the env gate to a CI leg -- a scope call, not a defect.

## ⏭ macOS: run these two commands on that box

`ordering` is **safe to run on the real desktop right now** -- local grabs only, no isolated
display needed:

```
cd /Users/israeldryer/PycharmProjects/bootstack
.venv/bin/python development/probe_444_grab_crossplatform.py ordering
```

The global arms **will briefly grab the whole screen**. The probe takes the grab, reads
`grab_status()`, and releases in a `finally` with **no event-loop pump in between**, so the window
is as tight as it can be made -- but it is a real global grab on a real desktop and that is the
maintainer's call, not a session's:

```
BOOTSTACK_ALLOW_GLOBAL_GRAB=1 .venv/bin/python development/probe_444_grab_crossplatform.py kind restore
```

⚠ **The Aqua-specific worry is concrete, not generic.** This project has already measured one
toolkit feature that is a **silent no-op on macOS** -- `tk busy`, recorded in `CLAUDE.md` from
#429. If `grab_set_global()` is similarly weaker on Aqua, there are two different outcomes and
only one of them is this branch's problem:

- `grab_status()` reads back something other than `"global"` -> `capture_grab` records the wrong
  kind and `restore_grab` **narrows an app-modal window**. That IS this branch's problem, and the
  `kind` arm is what detects it.
- `grab_status()` says `"global"` while Aqua's global grab does less than X11's -> the round trip
  is faithful and the shortfall is Tk's, pre-existing, and not #444's to fix. **Say which one it
  is; do not report the second as a defect here.**

## ⚠⚠ THE ROUND-1 PROBE IS UNTRACKED, AND "Re-run rather than re-deriving" DEPENDS ON IT

**`development/` is NOT gitignored -- 160 files tracked, 102 of them probes.** Committing a probe is
this project's convention, not an exception. Every #444 probe from the PLAN stage is tracked, because
they rode `fca6db6f`:

```
TRACKED    probe_444_contextmenu_grab.py
TRACKED    probe_444_double_restore.py
TRACKED    probe_444_grab_restore_ordering.py
TRACKED    probe_444_verify.py
UNTRACKED  probe_444_review_round1.py          <- round 1's evidence
UNTRACKED  probe_444_grab_crossplatform.py     <- this pass's evidence
```

**`probe_444_review_round1.py` carries the measurement behind round 1's BLOCKING finding** -- the
`reshow` arm, `restored 2 / lost 3` before the fix and `5 / 0` after -- and the handoff block at the
top of this file instructs the next session to re-run it. **It exists only in the working tree.** A
`git clean -fd`, a fresh clone, or a worktree loses it, and the instruction then points at nothing.

This is the failure `CLAUDE.md` names in its own words: *"A handoff artifact only survives if it is
IN THE REPO ... #379's `leakfix.patch` was saved to a per-session temp `scratchpad/` and is genuinely
gone."* Milder here -- these sit in the repo DIRECTORY, just uncommitted -- but the instruction that
depends on them is already written.

⏭ **Both probes should ride the fix commit**, the same way the plan-stage four rode `fca6db6f`.
Nothing needs deciding; it is one `git add`.

## NOTE, NOT WORK -- `restore_grab`'s degrade branch is unexercised, and that is NOT a finding

⚠⚠ **AN EARLIER VERSION OF THIS SECTION FILED THIS AS A "CANDIDATE FOR ROUND 2" AND PROPOSED A TEST.
THAT WAS WRONG AND THE MAINTAINER OVERTURNED IT (2026-08-28):** *"let's not create a bunch of tests
just to fill a testing gap. the goal is to fix things that are broken and not working."*

**Gate 2 already said so and the pass drifted past it.** Test findings are actionable in exactly two
classes -- **vacuity** (passes while the behavior is broken) and **false alarm** (fails while it is
fine). **An uncovered branch is neither. Coverage is not a defect.**

The fact, recorded as a boundary on what this pass measured and nothing more:

```python
if kind == "global":
    try:
        holder.grab_set_global()
    except tkinter.TclError:
        _log_grab_failure("could not restore a global grab; falling back to local")
        holder.grab_set()          # <- no test reaches this line, on any platform
```

`_StubHolder.grab_set_global` never raises, in `test_window_modal_grab.py:193` or in the copy at
`test_dialog_nested_modality.py:345`, so `test_the_restored_grab_keeps_its_kind` pins that the
captured kind **selects** the matching call and nothing pins what happens when that call **loses**.

⚠ **There is NO evidence this branch is broken.** It was not observed failing, on either platform
measured; it is simply outside what was exercised. **Do not close this by writing a test.** It earns
work only if something is seen to actually misbehave -- and #440 has shipped this same helper since
`0.3.1` with no such report.

## ⚠ WSL gotcha, reproduced with a control -- `xfwm4` has NO `--daemon` flag

A helper that starts the window manager as `xfwm4 --daemon &` leaves the run with **no display at
all**: every `xprop` poll and a following `xdpyinfo` both report *"unable to open display :99"*.
Replacing it with a plain `xfwm4 &` and polling `_NET_SUPPORTING_WM_CHECK` works on the same
display number. **Reproduced twice each way with the working form as the control** -- so the fact
is solid even though **the mechanism is NOT explained**: an invalid flag making the whole display
unreachable is not obviously connected, and running `xfwm4 --daemon` in the foreground leaves the
display perfectly usable. **Recorded as an observation, not a cause.**

This matters beyond this branch: `CLAUDE.md` warns that running the Linux legs WITHOUT a window
manager reproduces #447 and reads as a product bug. A helper with this flag in it fails in exactly
that direction, and it announces nothing.

The working helper, for reuse:

```
xfwm4 >/tmp/bs_xfwm4.log 2>&1 &
for i in $(seq 1 2000); do
  xprop -root _NET_SUPPORTING_WM_CHECK 2>/dev/null | grep -q "window id" && break
done
exec "$@"
```

Invoked as `xvfb-run -a -s "-screen 0 1280x1024x24" /tmp/bs_wm.sh <command>`. The WM comes up
around poll 90-130.
