# Review brief — #428, round 1

Hand this to a **fresh session**. Per `REVIEW-PROTOCOL.md`, the session that
wrote this code cannot review it, and this brief exists so intent travels in a
file rather than in a conversation.

## What to review

Branch **`fix/formdialog-select-value-428`**, head **`9a55742f`**, rebased onto
`origin/main` (`f9685cb0`) so `main` is a genuine ancestor.

Round 1, so the scope is the whole branch:

```
git diff origin/main...HEAD
```

Three dots, not two — it diffs from the merge base and shows only this branch's
work.

## What to read

- **`PLAN.md`** (at the repo root, committed on this branch) — the intent, the
  measured root cause, the invariants, and what was explicitly ruled out.
- **The diff.**
- `REVIEW-PROTOCOL.md` for the format and the severity split.

## What NOT to read

- **The commit messages on this branch.** They are long and carry the
  implementer's reasoning about why the approach is sound. That is exactly the
  input the protocol excludes: it produces "yes, that seems right" instead of
  scrutiny. `git diff` gives you the code without them; resist `git log`.
- Any prior chat transcript.

`PLAN.md` is a deliberate exception — the protocol lists it as a review input,
because it states requirements and invariants you need in order to judge whether
the diff meets them.

## Shape of the diff

| file | what it is |
|---|---|
| `src/bootstack/dialogs/_impl/formdialog.py` | **the fix** — ~20 lines, the only production change |
| `tests/widgets/public/test_formdialog_result_value.py` | 5 regression tests |
| `CHANGELOG.md` | one entry, re-creating `## [Unreleased]` |
| `PLAN.md` | intent, written before implementation |
| `development/probe_428_*.py` | three probes; groundwork, not shipped code |

The production surface is small. Weight the review accordingly — the probes are
scratch artifacts kept for the record, not code to hold to shipping standards.

## Deliverable

**`REVIEW.md`** at the repo root, per the protocol: for each finding, `file:line`,
root cause (not just symptom), the suggested minimal change, and a severity of
**blocking** / **should-fix** / **nit**. Triage everything — there is always
something to find, and without the severity split there is no stopping rule.

Then, in the same session, the fix step: load `PLAN.md` before editing, fix
blockers only unless told otherwise, state the root cause before each edit, keep
the diff minimal, add a regression test per fix, and record resolutions back
into `REVIEW.md`.

## Worth knowing before you start

Verified on this branch, so a re-check is only warranted if you doubt it:

- Full suite green at `9a55742f` — `py -3.12 tests/run_gui.py`, exit 0, shared
  leg **937 passed / 14 skipped**, data leg **125 / 4**. `main` alone is
  **932 / 14**, so the delta is exactly the 5 new tests.
- Three of the five tests fail against unfixed source with the reported symptom
  (`assert 'One' == 1`) rather than an import or attribute error; the other two
  pass on both sides by design and are controls.

⚠ **Two harness traps in this area, both already paid for:**

- `dlg.show()` runs a modal wait loop that neither `app.close()` nor a scheduled
  destroy escapes — it hangs. Drive the buttons instead.
- A **cancel** button keeps `closes = True`, so the framework closes it; only
  non-cancel buttons are switched to `closes = False` and destroy the toplevel
  themselves. Calling `command()` on cancel returns early WITHOUT closing, which
  leaves `show()` blocked and lets a later assertion read a previous dialog's
  data.
