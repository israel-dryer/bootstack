# Review brief — round 4, the #446 flake fixes

Written by the implementing session for the reviewing one. Per
`REVIEW-PROTOCOL.md` this carries **scope and triage state only**. It
deliberately does not argue that the fix is correct — that is the reasoning the
session boundary exists to keep out.

## Scope — the fix diff, NOT the branch

```
git diff 7ef64236..48dba181
```

Two test files and four probes. **`src/` is untouched in this diff**, and that
is worth verifying rather than taking on trust (`git diff 7ef64236..48dba181 --
src/` must be empty) — if it is not, the premise that both flakes were test
defects is wrong and the whole finding changes.

Rounds 1–3 reviewed the production code for #426/#439/#440/#441 and are closed.
**Do not re-review them.** Round 3's record ends by noting that re-reviewing
settled code is what made it re-file three already-decided findings.

## Already decided — do not re-file

| item | state |
|---|---|
| #444 — modal `bs.Window` never restores the grab | **filed**, out of #440's scope, pre-existing |
| #445 — `attach()` drops legacy kwargs on a grid cell | **filed**, pre-existing |
| round 1 F4 — unguarded `grab_current()` | **deferred** twice, unchanged |
| `CLAUDE.md` quoting the wrong #426 message | **fixed on `main`**, never on this branch |
| a CHANGELOG entry for #446 | **deliberately omitted** — test infrastructure, no public API reaches it |
| #441 keysym polarity (`!= "KP_Enter"`, not `== "Return"`) | **settled in round 3**, pinned by its own test |

`git diff main...HEAD -- CLAUDE.md` must stay empty. Check it.

## The open question this round exists for

**A third flake, unexplained.**
`test_dialog_press_contract.py::test_enter_on_a_disabled_button_still_reaches_the_default`
failed once in 37 post-fix runs with `calls == []` — Enter reached neither the
disabled Apply button nor the default OK button.

What is known:

- It did **not** appear in 12 runs of the pre-fix branch, and appeared **once**
  in 37 runs after. That is far too little to attribute either way. Whether the
  timing change in this diff exposed it is **unknown**, and saying so is the
  honest state.
- `development/probe_446_disabled_button_enter.py` reproduces **0/40** in a
  quiet process, so like the other two it needs cross-test state.
- 25 further runs with the guard instrumented did not catch it again.

Reading the guard does not explain it: `_key_was_consumed` sees `TButton` in the
bindtags and returns `not instate(["disabled"])`, which is `False` for a
disabled button, so the toplevel binding should invoke the default every time.
That leaves two candidate steps, and the probe is already instrumented to
separate them — **did the toplevel binding run at all**, or **did it run and
`invoke()` do nothing**.

⚠ **Do not attempt to settle this by re-running.** At this rate a clean batch is
the expected outcome either way; that is the trap that produced #446 in the
first place, and it is now recorded in `CLAUDE.md`'s Techniques section.

## How to reproduce and measure

The five-file combination, which is what exposes all three (each file passes
alone):

```
py -3.12 -m pytest tests/widgets/public/test_dialog_enter_key.py \
  tests/widgets/public/test_dialog_nested_modality.py \
  tests/widgets/public/test_dialog_initial_focus.py \
  tests/widgets/public/test_layout_migration_error.py \
  tests/widgets/public/test_dialog_press_contract.py -q -p no:cacheprovider
```

Probes, each of which prints its own arms and expected pattern:

| probe | what it measures |
|---|---|
| `probe_446_fixed_delay_lands_mid_show.py` | flake A's mechanism, forced |
| `probe_446_barrier_scope.py` | flake B's mechanism, forced |
| `probe_446_leaked_after_jobs.py` | the hypothesis that was **refuted** — no test-scheduled timer survives a test |
| `probe_446_disabled_button_enter.py` | the third flake, instrumented; returns 0/40 quiet |

## Numbers measured at `48dba181`, for comparison rather than trust

- Five-file reproduction: **4/12 failing before, 0/37 after** (the third flake
  is the one failure inside that 37).
- Full `py -3.12 tests/run_gui.py`: **exit 0, all 20 legs, 1250 passed / 22
  skipped**.
- Shared leg **1055 passed / 13 skipped**, against a measured selected-count
  ceiling of **1068**. `1055 + 13 = 1068` exactly.

⚠ **Two recorded numbers did not survive re-measurement, so re-measure rather
than comparing against anything written down.** Round 3 recorded the shared leg
as 1011/14 against a 1024 ceiling; the same commit collects **1068** today, and
this diff adds no tests (61 in the five-file run both before and after). And the
data leg reads **123 / 6**, not the 125 / 4 in `CLAUDE.md` — that difference is
**environmental**, tracking whether `pandas` is installed, because two of those
tests skip when it is.

## What a vacuity check on this diff looks like

Both barriers were widened, and a barrier that waits for the thing the assertion
is about can silently swallow its own test. The check that was run, if it is
worth repeating: restore the pre-#439 focus behavior by replacing
`Dialog._focus_when_mapped` with an immediate `focus_set()`, and confirm the
focus tests still fail. **A barrier change that leaves them passing is the
failure mode to look for**, in this diff and in any future one.
