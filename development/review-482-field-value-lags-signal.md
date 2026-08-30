# REVIEW — #482 round 1

Branch `fix/field-value-lags-signal-482`, diff `main...HEAD` (36 lines of `src/`,
13 tests). Round cap 2, this is round 1.

Measured on the macOS box, `.venv/bin/python` 3.14.0, against a `main` worktree
arm with `PYTHONPATH` set and provenance printed. Probes:
`development/probe_482_commit_in_trace.py`.

---

## 1 — BLOCKING. An in-trace `commit()` cannot repaint the entry, so the signal and the display diverge permanently

`textentry_part.py:190` / `spinnerentry_part.py:174` — `_commit_if_not_editing`
calls the whole of `commit()`, including its display-normalizing
`textsignal.set(new_text)`.

**Root cause.** That call now runs inside the variable's own write trace. Tcl
suppresses every other trace on a variable while one of its traces is executing,
so the nested `set()` moves the signal and the entry's own textvariable trace
never runs — the widget keeps the old text. Measured in plain `tkinter`: a
nested `set` from inside a write trace fires no trace at all. `commit()`'s
cancel/resubscribe dance is therefore also inert on this path.

Worse, it does not heal. Because the signal has already been advanced to the
formatted text, the real commit at blur finds `new_text == self.textsignal()`
and skips the display update, so the entry shows the raw text for the rest of
its life.

`TextField(textsignal=sig, value_format="#,##0.00")`, then `sig.set("1234.5")`:

| | main | branch |
|---|---|---|
| after the write | sig `'1234.5'` · display `'1234.5'` · value `1.0` | sig **`'1,234.50'`** · display `'1234.5'` · value `1234.5` |
| after a later blur | sig `'1,234.50'` · display `'1,234.50'` · value `1234.5` | sig `'1,234.50'` · display **`'1234.5'`** · value `1234.5` |

Three consequences, all new: the widget displays text neither the caller nor the
signal holds; the caller's own `Signal` is silently rewritten by a write they
made; and an application subscriber on that signal is handed `'7.00'` where it
used to receive the `'7'` it set.

`value_format` is not required to reach it — `commit()` also `.strip()`s.
`sig.set("  padded  ")` on a plain `TextField` leaves sig `'padded'` and display
`'  padded  '`.

**Minimal change.** Re-derive the value; do not normalize the display. Split
`commit()`'s parse half into `_reparse()` and call that from
`_commit_if_not_editing`. Normalizing stays where it was — at blur/Return,
outside any trace — which is also where the family's committed-value contract
puts it: a programmatic write has no editing session to normalize the end of.

**RESOLVED** — `_reparse()` extracted in both parts; `_commit_if_not_editing`
calls it behind the placeholder guard. Both arms of the table above now match
`main` except for `value`, which is the fix. Regression test:
`test_a_formatted_write_leaves_the_display_and_the_signal_alone`.

## 2 — BLOCKING (same fix). The change reaches a fifth widget by inheritance, and PLAN's population does not

`NumberEntryPart` subclasses `TextEntryPart`, so it inherits `_handle_change`
and the new helper. PLAN scopes the fix to four widgets on the grounds that
`NumberField` already followed; the code does not respect that scope, and
`NumberEntryPart.commit()` applies bounds and re-normalizes.

`NumberField(value=5, min_value=0, max_value=10, value_format="#,##0.00")`:

| | main | branch |
|---|---|---|
| `f.value = 7` | `7.0` | `7` — return type changed |
| `f.value = 99` | value `99.0`, display `'99.00'` | value **`10`**, display `'99.00'` |

The second row is the same divergence as finding 1 in a widget the branch
claims not to touch: `.value` reports the clamp while the widget shows the
unclamped number.

**Minimal change.** Finding 1's fix makes this inert — `_reparse()` does not
reach `NumberEntryPart`'s bounds override, so `NumberField` returns to `main`'s
behavior exactly.

**RESOLVED** — verified byte-identical to `main` on both rows.

## 3 — NOTE. Re-entrancy: no recursion, no leak, subscription stays live

The attack that motivated the round comes back clean, for a reason worth
recording. `commit()` cannot re-enter `_handle_change` — not because of its
cancel/resubscribe, but because Tcl has already suppressed the trace (finding
1). 50 successive programmatic writes leave `_on_input_fid` live and the
subscriber count where it started. An application subscriber on the same signal
is called once per write, not twice.

## 4 — NOTE. Per-keystroke cost is 1.5 us

2000 signal writes with the field focused: 13.5 us/write on `main`, 16.6 us at
round 0, 14.8 us after the fix. `focus_get()` alone is 1.1 us. The existing
`<FocusIn>`/`<FocusOut>` bindings could carry a boolean for free, but 1.3 us on
a keystroke is not worth the diff.

## 5 — NOTE. `except (TclError, KeyError): return` is right, and unreachable

`destroy()` cancels `_on_input_fid` before the widget goes, so `_handle_change`
does not run for a destroyed entry; a write to a signal whose field's toplevel
was destroyed raises nothing on either arm. Kept as written — skipping the
commit is the correct answer during teardown, and `KeyError` out of
`_nametowidget` is a real shape (see `grab_current`).

## 6 — NOTE (gate 2, diagnostics only).

`test_typing_is_still_uncommitted_until_blur` rests on `focus_force()` taking
effect. Where it does not — an unmapped widget, or X11 with no window manager —
`focus_get()` is not the entry, the write commits, and the test fails while the
product is fine. A precondition assert would label that as setup rather than
product; gate 2 makes it a note, not a fix.

## 7 — NOTE. No third part needs the helper

`grep -rn "def _handle_change\|def commit" src/bootstack/` returns three
`commit`s and two `_handle_change`s: `textentry_part`, `spinnerentry_part`, and
`numberentry_part`, which inherits both from the first. The duplication is the
two copies already flagged for #477.

---

# REVIEW — #482 round 2

Diff `81146adb..HEAD` (`src/` + `tests/`, +93/−46 across three files) — round 1's
own fix step plus the two commits after it. `81146adb` is settled code and was not
re-reviewed; the two questions the round was handed are answered against it anyway,
because both were assigned explicitly.

Measured on the Windows box, `py -3.12`, one process per arm: HEAD, `main`
(`99990cc4`) and `81146adb`, the latter two in worktrees with `PYTHONPATH` set,
absolute paths into each worktree, and provenance printed on every run. Probes:
`development/probe_482_round2_events_and_clear.py` (new),
`development/probe_482_commit_in_trace.py` (round 1's, re-run on all three arms).

Full suite at HEAD, Windows, `py -3.12`, 2026-08-29: **33 legs, 1726 passed / 22
skipped, exit 0.** Recorded rather than leaned on — the merge gate is a fresh run at
whatever commit ships.

---

## 8 — BLOCKING. The CHANGELOG's "no event changes" is false as written

`CHANGELOG.md:15` ends *"...and no event changes: a programmatic write emits exactly
what it did before."*

**Root cause.** The claim was checked at the moment of the write, which is the only
moment `test_a_programmatic_write_still_emits_exactly_what_it_did_before` reaches.
One focus/blur cycle later the branch emits something different from `main`, in both
directions (finding 9). A reader deciding whether the upgrade touches them is being
told the opposite of what happens to a handler on a field their code writes through a
bound `Signal`.

The entry also never names `Signal.clear()`, which `0.4.0` shipped four weeks ago and
which this branch changes (finding 10).

**Minimal change.** Replace the clause with what was measured, and name `clear()`.

**RESOLVED** — clause replaced. The entry now says the write itself still emits what
it always did, and that the change event which used to arrive on the *next* focus/blur
cycle moves with `value`: gone where the user changes nothing, emitted where the user
types the field back to the text it held before the write. `clear()` is named as a
write `value` follows, and `field.value` is named as the path that is unaffected.

Three regression tests, one per claim the reworded entry now makes:
`test_the_deferred_change_on_a_later_focus_cycle_moves_with_value`,
`test_typing_the_pre_write_text_back_is_now_a_change`, and
`test_value_follows_a_clear_of_the_bound_signal`.

**Control, because a precondition can hide what a test really checks.** All three
fail against a `main` worktree — but the first two fail on their *precondition*
(`field.value == "world"`), which only re-proves the fix moved `value` and says
nothing about whether they can see the event difference. Re-run with that
precondition stubbed out, they fail on the event assertion itself, with exactly the
values the probe measured: `assert [('hello', 'world')] == []` and
`assert [] == [('world', 'hello')]`. The event assertions discriminate on their own.

They drive the cycle with a synthesized `<FocusIn>`/`<FocusOut>` pair rather than
`focus_force()`, deliberately: `focus_force()` is a silent no-op where the window
manager does not grant focus, and there the snapshot would stay at its construction
value and both tests would fail while the product is fine. That is round 1's finding
6 as a false alarm rather than a note, so it is designed out.

## 9 — SHOULD-FIX, but no minimal code change exists. `<<Change>>` moves on the focus/blur cycle after a programmatic signal write

`textentry_part.py:149` (`_store_prev_value`) and `:202` (`_check_if_changed`),
reached because `_commit_if_not_editing` (`:179`) advances `_value` before the next
FocusIn. Same two seams in `spinnerentry_part.py` (`:140`, `:185`).

**Root cause.** `_prev_changed_value` is snapshotted **from `_value`** on FocusIn and
compared against `_value` on blur. `_value` now already carries the programmatic
write, so the snapshot is no longer stale — and the deferred `<<Change>>` that
staleness produced is gone with it.

Measured, `TextField` unless noted, `[(prev_value, value)]` collected per arm:

| arm | main | 81146adb | HEAD |
|---|---|---|---|
| write, then focus/blur with no edit | `[('hello','world')]` | `[]` | `[]` |
| write, then type the old text back, blur | `[]` | `[('world','hello')]` | `[('world','hello')]` |
| *control* — focus/blur, no write | `[]` | `[]` | `[]` |
| *control* — typed edit, no write | `[('hello','typed')]` | same | same |
| *control* — `field.value = x`, then cycle | `[]` | `[]` | `[]` |

The two controls that must not move do not move, so the difference is the write and
not the cycle. All four widgets agree: `PasswordField` and `PathField` match
`TextField` row for row, `SpinnerField` matches on row 1.

**Blast radius is the signal-write path only.** `field.value = x` already set `_value`
on both arms, so the snapshot was never stale there. `Form.set()` writes through
`widget.value` (`form.py:916`), so it rides that unaffected path.

**It originates at `81146adb`, not at round 1's fix.** HEAD and `81146adb` agree on
every row above — round 1's fix changed how `_value` is *derived*, not *when* it
moves. Round 1 did not see it because the event test it inherited stops at the moment
of the write (finding 11).

**No minimal change restores `main`.** Keeping the deferred `<<Change>>` means keeping
`_prev_changed_value` pinned to the last user-committed value, which is exactly the
staleness #482 exists to remove. And the new behavior is the more coherent of the two
in both directions: `<<Change>>` now compares against the value the field actually
holds, so it stops announcing a change the application made itself as though the user
had made it, and starts announcing one the user really made. PLAN's *"event behaviour
must be byte-identical before and after"* is therefore not met. **Which of the two
wins is a maintainer call**, and it sits directly on the seam carrying the standing
2026-08-26 *keep in mind, do not fix, do not file* disposition.

**Not fixed on the branch** — the cap is reached. Recorded here, pinned by a test so
it cannot drift unnoticed, and written into the CHANGELOG (finding 8).

## 10 — SHOULD-FIX (documentation only). `value` follows `Signal.clear()` too

`bs.Signal("hello", allow_empty=True)` bound to a `TextField`, then `sig.clear()`:

| | main | HEAD |
|---|---|---|
| after the clear | `value` `'hello'` | `value` `None` |
| after a later focus/blur | `<<Change>>` `('hello', None)` | none |

**Root cause.** A `clear()` reaches `_handle_change` down the same path as a `set()`
— `Signal.clear` is `set(None)`, and a realized text signal takes that as `''` — so
`_reparse`'s empty branch sets `_value = None`.

The value half is the fix working, and is what `0.4.0` shipped `clear()` for: the
field and the signal now agree instead of the field holding the value the user was
told had been cleared. The event half is finding 9 again. No code change is wanted;
the gap is that the CHANGELOG says only *"a write your code made"* and never names
`clear()`.

**RESOLVED** — named in the CHANGELOG under finding 8.

## 11 — NOTE (gate 2, vacuity). The event test is narrower than its name

`tests/widgets/public/test_field_value_follows_signal.py:69`,
`test_a_programmatic_write_still_emits_exactly_what_it_did_before`, counts `<<Input>>`
and `<<Change>>` across three writes and stops. The branch *does* change `<<Change>>`
for a programmatic write — one focus/blur cycle later — and this test passes anyway.
The behavior its name claims is broken while it is green, so this is vacuity rather
than wording, and it is why round 1 saw nothing here.

The test comes from `81146adb` and is outside this round's diff, so it is left exactly
as written. The fix step adds a test covering the moment it does not reach, which is
what removes the vacuity.

## 12 — NIT. The placeholder guard round 1 added is unreachable

`textentry_part.py:181-182`. `grep -rn "_commit_if_not_editing" src/bootstack/`
returns two definitions and two call sites, both inside `_handle_change` — and
`_handle_change` has already run `_hide_placeholder()`, or returned, before it calls
down. So `_showing_placeholder` is always False there. Instrumented by patching the
class attribute and recording the flag on entry, across a write onto a placeholdered
field, a clear back to empty, and a re-write: `[False, False, False]`.

`commit()`'s own guard at `:350` is the live one. `SpinnerEntryPart` has no
placeholder support at all, so its absence there is correct rather than asymmetric.
Harmless either way. Not fixed.

## 13 — NOTE. Round 1's two findings verified resolved, each against a control

Both re-measured rather than taken on the record's word.

**Finding 1.** `probe_482_commit_in_trace.py` on all three arms: HEAD's signal and
display are byte-identical to `main` on every arm — `sig='1234.5' display='1234.5'`
where round 0 left `sig='1,234.50' display='1234.5'`, the unstripped `'  padded  '`
preserved in both, arm B healing to `'1,234.50'` at blur. Only `value` differs, which
is the fix. Arm D reproduces the mechanism in plain `tkinter` — a nested `set` inside
a write trace fires no trace while the variable still moves
(`hits=[('t2','y'),('t1','y')] final='z'`) — so the root cause round 1 recorded is
instrumented, not inferred.

**Finding 2.** `NumberField(value=5, min_value=0, max_value=10,
value_format="#,##0.00")`, then `f.value = 99`: `81146adb` gives `value=10` (`int`)
with display `'99.00'` — the divergence finding 2 named — while HEAD gives
`value=99.0` (`float`), display `'99.00'`, identical to `main`, both clamping to `10`
at blur. The pre-fix arm is the control that makes the HEAD reading mean anything.

## 14 — NOTE. Extracting `_reparse()` is behavior-preserving for `commit()`

`_reparse` maps `main`'s inline parse block one-to-one: the empty branch assigns and
returns True, so `commit()` falls through to formatting exactly as it did; a
`ValueError` returns False, so `commit()` returns exactly as it did. The only other
callers of `commit()` are `SpinnerEntryPart.step()` and `NumberEntryPart.commit()`,
and both go through that same door.

---

## Round 2 fix step — what was re-ranked and what was touched

Re-ranked before editing, as the protocol asks. Finding 8 stays **blocking**: it is a
user-facing statement contradicted by measurement, on an entry no tag has run on yet,
and the fix is one paragraph. Everything else drops or holds below it — finding 9 has
no minimal change that does not undo #482, finding 10 is finding 9 plus documentation,
and 11/12/13/14 are notes and a nit.

**Touched:** `CHANGELOG.md` (finding 8) and
`tests/widgets/public/test_field_value_follows_signal.py` (three tests). **No `src/`
change** — which means the next round's gate 1 diff is empty and there is no round 3.

Full suite re-run at the fixed tree, Windows, `py -3.12`: **33 legs, 1729 passed / 22
skipped, exit 0** — the three new tests and nothing else.

## Survivors — filed, not fixed

**Finding 9** is the one that leaves the branch. It needs a maintainer decision rather
than a patch: `<<Change>>` on the focus/blur cycle following a programmatic signal
write is gone, and one appears where the user types the pre-write text back. Both
follow from `_prev_changed_value` being snapshotted from `_value`, so preserving
`main`'s behavior means preserving the staleness #482 removes. It is documented in the
CHANGELOG and pinned by tests, so whichever way the decision goes, it is visible
rather than silent.

Findings 11 and 12 are notes and stay in this record.
