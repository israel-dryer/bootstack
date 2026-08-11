# Review brief — #437 / #438, round 4

Hand this to a **fresh session**. Per `REVIEW-PROTOCOL.md`, the session that
wrote this code cannot review it, and this brief exists so intent travels in a
file rather than in a conversation.

## What to review

Branch **`fix/formdialog-select-value-428`**. Round 3 reviewed `eab58129`. This
round reviews **the round-3 fix step and everything taken after it**:

```
git diff eab58129..HEAD
```

Four commits, and knowing which is which matters because they were written under
different conditions:

| commit | what |
|---|---|
| `79431bb2` | the round-3 fix step — R1 through R4, written before the review handed off |
| `3d021cc0` | R5 + R6, the `docs/widgets/dialog.rst` refusal example |
| `70a039ce` | R7, `Form.result` cleared on a refused press |
| `38b22900` | CHANGELOG + `REVIEW.md` record |

Not the whole branch. The #428 half has been through two rounds and #437/#438
through three; re-reviewing them invites relitigating settled code.

## What to read

- **The diff.**
- **`REVIEW.md`'s round-3 FINDINGS** — the `R1` through `R7` sections. That is
  what this diff answers, so you need them to judge whether each was closed.
- `REVIEW-PROTOCOL.md` for the format and the severity split.
- `PLAN.md`, with the warning that its `SUPERSEDED` blocks are decisions of
  record rather than argument you are meant to agree with.

## What NOT to read

- **`REVIEW.md`'s `## Round 3 fix step` section**, including its
  `### Round 3 carry-forward` subsection, until you have formed your own view of
  the diff. It is the fixer's rationale — the input the protocol excludes,
  because it produces "yes, that seems right" instead of scrutiny. Read it
  afterward to check nothing was missed, or to tell a decision from an oversight.
- **The commit messages.** Same reason, and they are unusually detailed this
  round.
- **`REVIEW.md`'s round-1 and round-2 sections.** They describe the `closes`
  takeover and the `show()` reset, both deleted, and will send you looking for
  code that is gone.
- Any prior chat transcript.

## Shape of the diff

| file | what it is |
|---|---|
| `src/bootstack/dialogs/_impl/dialog.py` | R1 — `press_default` stands down when the key already reached a button |
| `src/bootstack/dialogs/_impl/formdialog.py` | R3 — `_accept_press` exempts the cancel role from form validation |
| `src/bootstack/widgets/_impl/composites/form.py` | R7 — `result = None` on the refusal path, plus the attribute docstring |
| `src/bootstack/widgets/form.py` | R7 — the public `Form.result` docstring |
| `docs/widgets/dialog.rst` | R5 + R6 — the refusal example |
| `tests/widgets/public/test_dialog_press_contract.py` | R4 rewrite + the R7 test |
| `tests/widgets/public/test_formdialog_result_value.py` | R3 coverage with a `required` item |
| `development/probe_437_round3.py`, `probe_437_dialog_focus.py` | the round-3 measurements |
| `CHANGELOG.md`, `REVIEW.md` | the record |

## Settled — do not re-litigate

Each of these was measured or decided deliberately. Finding a mistake in one is
a finding; disagreeing with the choice is not.

- **`Form.result` means "the most recent press that COMPLETED".** A refused
  press clears it. The rejected alternative was "the last thing that succeeded",
  and the cost is accepted knowingly: a refusal also erases an earlier accepted
  press, so a late reader sees `None`. Recording the declined press's own token
  was rejected outright as the shape #437 removed from `Dialog`. The maintainer
  raised and settled this.
- **R5's explanatory `.. note::` was dropped rather than shipped.** Documenting
  the nested-modal grab release in the teaching layer papers over a defect and
  goes stale when it is fixed. It is **#440** instead.
- **The keypad bullet is folded into #437**, not filed separately.
- **`default_button.focus_set()` is a no-op** — measured, and **#439**. Not
  fixed here. It means the Enter double dispatch R1 fixed needed a *click* to
  put focus on a button first.

## Where to push hardest

Honest soft spots, in the order I would attack them.

**R7's clear is the only behavior change in this diff that a user could be
relying on today.** It is new-in-this-release behavior, so nothing shipped can
depend on it — but check that reasoning rather than taking it, and check whether
any framework consumer reads `Form.result` after a press it may have refused.

**R1's `press_default` decides by bindtag string.** It reads
`"TButton" in bindtags(event.widget)`. Ask what else carries that tag, and what
happens for a footer button whose bindtags were customized. A widget class check
would be a different trade; the comment explains why the Tcl call is used rather
than the widget object, and that part is measured.

**R3 exempts `role == "cancel"` from validation but still falls through to the
capture.** Convince yourself that keeps F3 closed — a `role='cancel',
result='ok'` button must take a fresh snapshot, not report a previous run's.

**The R4 test rewrite is the one that failed to see a real bug last round.** It
now asserts focus as a precondition, sends the key to the focused widget, and
counts invocations. Check it counts the right thing and that the precondition
cannot pass vacuously — and note that #439 means focus there is *forced* by the
test, since a real dialog does not establish it.

**The R7 test's control was run** (with the clear stashed it fails with
`a refused press left {'k': 'accepted'} readable`, other 10 in the file passing).
The R4 and R3 tests' controls are claimed in `79431bb2` but were not re-run in
this session. Re-run any you doubt — that is what caught two vacuous tests in
the #417 review.

## Verification already run

Full `py -3.12 tests/run_gui.py` at `70a039ce`, **exit 0**: widgets+CLI **1005
passed / 13 skipped** (52 deselected), data **123 / 6**. Baseline at `eab58129`
was 1001 / 13, re-measured by stashing rather than recalled. The +4 is exactly
the 4 net tests added across the round.

Clean `-W` docs build at `3d021cc0`, exit 0. The docs example was checked
against the real API (`DialogButton.default`, `TextField.value`, `bs.toast`).

⚠ A `-n` nitpicky build was **not** run. The example carries no cross-reference
roles, so nothing new can dangle, but the page was edited — if you want the
guarantee, run it.
