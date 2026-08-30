# Round 2 review — #482, branch `fix/field-value-lags-signal-482`

You are reviewing, not implementing. This is a fresh session on purpose: the
session that wrote this code does not review it.

**Read first:** `REVIEW-PROTOCOL.md`, then `PLAN.md` and `REVIEW.md` at the repo
root. Read `PLAN.md` for the requirements, invariants and the round cap — not
for whether the approach sounds right.

## Scope — this is the whole of it

```
git diff 81146adb..HEAD -- src/ tests/
```

Three files, +93/−46. Round 1 reviewed the branch; this round reviews only what
**round 1's own fix step** introduced, plus the two commits after it. Do not
re-review `81146adb` — that is settled code.

That scoping is the lesson this project paid for on #467: all three of that
branch's round-2 findings were regressions introduced by round 1's own fix,
because the round was measured against the branch's pre-fix commit rather than
against the fix. A fix step is code.

**Gate 1, already checked:** the `src/` diff is non-empty
(`textentry_part.py`, `spinnerentry_part.py`), so the round is real.

**Round cap is 2, and this is round 2.** Surviving findings are filed as issues,
not fixed on the branch. Set that expectation before you start looking.

## Gates that bind this round

**Gate 2 — test code.** `tests/widgets/public/test_field_value_follows_signal.py`
is in scope on exactly one axis: what defect can it let through? Only **vacuity**
(passes while the behavior is broken) and **false alarm** (fails while it is
fine) are actionable. Diagnostics, wording and symmetry are notes in the record,
never fixes.

**Gate 4 — probes.** The five `development/probe_482_*.py` files are instruments,
not reviewed code; no findings against them. One exception applies and it matters
here: several arms in `probe_482_focused_write_residual.py` drive a button with
synthesized `<ButtonPress-1>`/`<ButtonRelease-1>`, and **those arms returned
inconsistent results across runs**. Do not treat any conclusion resting on a
synthesized click as settled. The arms that write the signal directly were stable
across every run.

## Environment

Windows box, `D:\Development\bootstack`. Use **`py -3.12`** for everything — the
checked-in `.venv` is stale and pytest is installed only on 3.12. Full suite is
`py -3.12 tests/run_gui.py`. Never pipe a test or build command to `tail` or
`Select-String`; redirect to a file, read `$LASTEXITCODE` on the next statement,
then grep the file.

To compare against `main`, use a worktree with `PYTHONPATH=<worktree>/src` **and**
absolute paths into that worktree, and print provenance
(`os.path.dirname(bootstack.__file__)`) — `PYTHONPATH` alone runs new tests
against old source.

## Already true — do not report as findings

- The full suite has **not** been run at HEAD. The only figure on record,
  `1712 passed / 33 skipped`, is from `81146adb` on the macOS box — before the
  round-1 fix. Running it is a merge gate, not this round's job; say so if you
  lean on it.
- No PR is open, nothing is pushed, and no release follows this branch. Several
  patches will roll into one patch release later, so `## [Unreleased]` is correct
  as it stands.

## Settled — do not re-litigate

- A programmatic write while the field **has** keyboard focus still lags. It is
  stated in `PLAN.md` as a residual, measured as **not a regression** (identical
  on `main`), and it heals on the next blur.
- Event emission **at the moment of a write** is deliberately unchanged. Whether
  a programmatic set counts as a change is a standing maintainer do-not-fix
  across the whole field family.
- The population is four widgets (`TextField`, `PasswordField`, `PathField`,
  `SpinnerField`), not the six the issue names. `TextArea`, `CodeEditor` and the
  value-space fields already followed.

## Two questions this round should settle

Stated as questions, not conclusions — verify or refute against `main`.

1. **Does the fix change `<<Change>>` on a later focus/blur cycle?**
   `_store_prev_value` snapshots `_prev_changed_value` from `_value` on FocusIn,
   and `_check_if_changed` compares them on blur. Re-deriving `_value` earlier
   may remove a `<<Change>>` that previously fired after a programmatic write.
   The commit message for `81146adb` claims events do not move; that claim covers
   the moment of the write, and this is a different moment.

2. **Does `.value` now follow `Signal.clear()`?** A clear reaches
   `_handle_change` down the same path as a `set()`. If it does, is the CHANGELOG
   entry — which says only "a write your code made" — accurate as written?

## Output

Append round 2 to `REVIEW.md` in the existing format: `file:line`, root cause,
suggested minimal change, severity (**blocking** / **should-fix** / **nit**).
Then run the fix step — blockers only — and record resolutions inline, as round 1
did. If nothing is blocking, say so and stop: the branch is done, and any
survivors are filed as issues rather than fixed.
