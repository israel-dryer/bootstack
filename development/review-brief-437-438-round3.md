# Review brief — #428 / #437 / #438, round 3

Hand this to a **fresh session**. Per `REVIEW-PROTOCOL.md`, the session that
wrote this code cannot review it, and this brief exists so intent travels in a
file rather than in a conversation.

## What to review

Branch **`fix/formdialog-select-value-428`**. Round 2 reviewed `065ef56a`. This
round reviews **only the fix diff**:

```
git diff 065ef56a..HEAD
```

Not the whole branch. The #428 half has been through two rounds and the
#437/#438 half through one; re-reviewing them invites relitigating settled code.

## What to read

- **The diff.**
- **`PLAN.md`** — with the warning below.
- **`REVIEW.md`'s round-2 FINDINGS** (the `# Round 2 — #437 / #438` section, F1
  through F8). That is what this diff is answering, so you need it to judge
  whether each finding was actually closed.
- `REVIEW-PROTOCOL.md` for the format and the severity split.

## What NOT to read

- **`REVIEW.md`'s `## Round 2 fix step` section** until you have formed your own
  view of the diff. It is the fixer's rationale — the input the protocol
  excludes, because it produces "yes, that seems right" instead of scrutiny.
  Read it afterward to check nothing was missed, or when you need to know
  whether something was a decision or an oversight.
- **The commit messages.** Same reason.
- **`REVIEW.md`'s round-1 section.** It describes the `closes` takeover and the
  `show()` reset, both deleted. It will send you looking for code that is gone.
- Any prior chat transcript.

⚠ **`PLAN.md` is a mixed document.** Its three original sections (#428, #437,
#438) predate implementation and are legitimate plan input. The blocks marked
**SUPERSEDED** were added after the fact and are decisions of record — what was
decided, by whom, and what measurement backed it — not argument you are meant to
agree with. If a superseded block's reasoning does not survive your reading of
the diff, that is a finding.

## Shape of the diff

| file | what it is |
|---|---|
| `src/bootstack/widgets/_impl/composites/form.py` | F1 — `_make_button_command` honors a `False` return |
| `src/bootstack/dialogs/_impl/formdialog.py` | F3 — `_button_returns_data` checks the token before the role; F8 — bad mapping wrapped in `ValueError`; F2 — docstring only |
| `src/bootstack/dialogs/_impl/dialog.py` | F4 — dead binding's replacement: `<KP_Enter>` bound alongside `<Return>`; `DialogButton.command` docstring widened to `Form` |
| `src/bootstack/dialogs/_impl/query.py` | F4 — dead `_submit_from_key` deleted |
| `src/bootstack/dialogs/_impl/datedialog.py` | F6 — docstring stating why no `grab_release()` |
| `src/bootstack/dialogs/__init__.py` | F2 — public `FormDialog(buttons=...)` docstring |
| `docs/widgets/dialog.rst` | F7 — **Refusing a press** subsection |
| `tests/widgets/public/test_dialog_press_contract.py` | **new** — F5 coverage, 8 tests |
| `tests/widgets/public/test_formdialog_result_value.py` | +2 tests (F3, F8) |
| `development/probe_437_review2_fixes.py` | the three cross-platform measurements |
| `development/probe_437_review2_controls.py` | the eight controls |
| `CHANGELOG.md` | F2 correction, plus the keypad entry |

## ⚠ Where the risk actually is — read this first

**1. `<KP_Enter>` is scope beyond the findings, and it is the thing to judge
first.** F4 asked only that the unreachable `<Return>` binding in `query.py` be
deleted. Deleting it alone would have removed the *intent* to support the keypad
key while leaving the key unsupported — measured, `Dialog` bound only
`<Return>`, so the keypad Enter did nothing in any dialog in the framework. So
the fix step deleted the dead code **and** bound `<KP_Enter>` on the toplevel
beside `<Return>`.

That is a user-visible behavior change on every dialog, made by the fix step
rather than asked for by the review. Questions worth putting to it: does it
belong on this branch at all, or is it a separate issue? It is a fix rather than
new API surface, so it can ride a minor — but that is a call, not a given. And
`for key in (...)` replacing a single `bind` is a structural change to a
much-used function.

**2. The new test file had two VACUOUS tests on its first draft**, caught only
by running the controls. Both asserted the result without asserting the press
had closed the dialog, and both routines write the result *before* returning —
so a version refusing every press left the value standing and the harness's
ten-second `force_close` tore the window down. The tell was `1 passed in
10.78s`. Both are fixed. **Worth checking whether the same shape survives
anywhere else in that file** — this is the third appearance of this exact trap
in this repo (#417's chevron test, #437's action-button test).

**3. `_drive` is now duplicated** between `test_dialog_press_contract.py` and
`test_formdialog_result_value.py`, with the second reaching one level deeper
(`dialog._internal._dialog` vs `dialog._dialog`). Known, not factored out. Your
call whether the duplication or the coupling is the worse cost.

**4. F2 was closed with documentation, not code.** If you think an action button
written as `DialogButton(text="Delete", role="danger", command=fn)` — no
`result=` — should work without the caller having to know about the token
convention, say so. The reasoning against is under *Settled* below, but the
conclusion is a judgment call and reversing it is a legitimate finding.

## Settled — do NOT re-litigate

- **F2: the inference stands; a result token is what makes a button an action.**
  This is the option round 2's own reviewer preferred ("the second is smaller and
  does not re-open the `submits` question"). Reclassifying "has a command, no
  result" as an action would change what such a button *returns* —
  `FormDialog(buttons=[DialogButton("Apply", command=fn)])` hands back the
  entered data today, and #437's plan lists that arm under "keeps today's
  behavior exactly". Point 4 above is still open to you; what is settled is that
  the change cannot be made *without* accepting that consequence.
- **F3 was fixed by reordering the predicate, NOT by re-adding the `show()`
  reset.** #438 removed that reset after measuring all four combinations of it
  and the veto. F3 is a path that measurement did not cover, which makes the
  measurement narrow rather than wrong — and with the token checked before the
  role, every data-token write is paired with a capture in the same press again,
  which is the invariant the reset defended. **Do not propose restoring it.**
- **F6 was closed with a docstring, not a code change.** Tk releases a grab held
  by a window when that window is destroyed (measured, below), so the range path
  needs no `grab_release()`. `_confirm` keeps its own because it destroys the
  window itself.
- **The `submits` field stays dropped**, and `closes` stays removed. Both were
  maintainer decisions in earlier rounds.

## Measured — do NOT re-derive

Arms 1–3 are in `development/probe_437_review2_fixes.py`; run it if you want to
see them rather than take them.

- **Tk releases a grab on destroy.** `grab_current()` is `None` after the
  grabbing toplevel is destroyed. This is what makes F6 cosmetic.
- **`query.py`'s frame-level `<Return>` binding was dead.** Focus lands on a
  `TEntry` whose bindtags are `[the entry, 'TEntry', the toplevel, 'all']` — the
  composite frame is not among them, and Tk does not bubble child → parent. So
  deleting it removed no behavior.
- ⚠ **`<KP_Enter>` CANNOT be synthesized on Windows Tk 8.6.15.**
  `event_generate("<KP_Enter>")` yields keysym `'??'`, keycode `0`: a `<Key>`
  catch-all sees it, `<KP_Enter>` does not, and `keycode=13` makes it arrive as
  `Return`. **Do not ask for a behavioral test of that key on this box** — the
  first draft was exactly that and it failed after the harness timeout. It is
  asserted structurally, with `<Return>` carrying the behavior. A Linux run
  could drive it for real.
- **All eight new tests observed failing** against reverted or deliberately
  broken source — `py -3.12 development/probe_437_review2_controls.py`, which
  asserts each revert matched before running (the CRLF trap from round 2).
- **Suite, measured 2026-08-10 on this working tree:** `py -3.12
  tests/run_gui.py` exit 0, all legs — **957 passed / 14 skipped** (shared root,
  52 deselected), **125 / 4** (data). The branch head collected 947; this adds
  exactly 10.
- **Docs:** clean `-W --keep-going` build, **exit 0, zero warnings**. A `-n`
  build reports 89, all pre-existing in autogenerated stubs and none on
  `docs/widgets/dialog.rst`.
- **Line endings uniform.** Every touched file is CRLF throughout — checked,
  because the round-2 controls were defeated by a CRLF/LF mismatch.

## Harness traps, already paid for

- `dlg.show()` runs a modal wait loop that neither `app.close()` nor a scheduled
  destroy escapes — it hangs. Drive the buttons instead.
- Press the real footer *widget*, not the spec's `command`. Invoking the command
  skips `Dialog`'s wrapper, where the veto, the result stamp and the close live.
- ⚠ **A test that takes ~10s is a vacuity signal, not a slow test.** That is
  `_drive`'s `force_close` backstop firing, which means the action never closed
  the dialog and the assertion passed on stale state.
- Two of `query._on_submit`'s three refusal branches open a `MessageBox`, which
  stacks a second modal inside the first and stalls the run. A date query with
  nothing entered is the one refusal reachable without it.
- Probe output must be ASCII — this box's console is cp1252.

## Deliverable

Append a **Round 3** section to **`REVIEW.md`** at the repo root: for each
finding, `file:line`, root cause (not just symptom), the suggested minimal
change, and a severity of **blocking** / **should-fix** / **nit**. Triage
everything — there is always something to find, and without the severity split
there is no stopping rule.

Per `REVIEW-PROTOCOL.md`'s convergence check: round 1 found 5, round 2 found 8.
If this round does not find materially fewer, the branch has grown too large and
the right answer is to split it rather than keep looping.
