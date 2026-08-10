# Review/Fix Loop Protocol

## Core rule

**A session that has written code never reviews code.**

Start a new session immediately before every review. That is the only session
boundary needed.

```
implement ──┐
            │ NEW SESSION
review → fix ┐
             │ NEW SESSION
review → fix ┐
             │ NEW SESSION
review → (clean) ✓
```

Intent travels between sessions in files, not in session memory. Written
artifacts transfer intent; session memory transfers self-justification.

## Artifacts

### PLAN.md — written by the implementing session

**Write it UP FRONT, before implementation begins.** The whole protocol depends
on this file existing; a plan reconstructed afterward is a justification, which
is the thing the session boundary exists to keep out.

- What the feature is supposed to do
- Key invariants and assumptions
- Why the code is structured the way it is

### REVIEW.md — written by each review step

For each finding:
- `file:line`
- Root cause (not just symptom)
- Suggested minimal change
- Severity: **blocking** / **should-fix** / **nit**

The fix step appends to each finding what it actually changed, so the next
reviewer sees intent, findings, and resolutions.

## Review step

Runs at the start of a fresh session.

**Reads:** PLAN.md, REVIEW.md (prior rounds), and the diff.

**Scope the diff.** Round 1 reviews the branch. Every later round reviews only
the fix diff (`git diff <pre-fix-sha>`), not the whole branch — re-reviewing
everything invites relitigating settled code and generates noise.

**Do not read the implementer's or fixer's reasoning about why their approach
was sound.** Requirements and findings are fine; rationale is what produces
"yes, that seems right" instead of scrutiny.

Triage every finding by severity. There is always *something* to find — without
a severity split there is no stopping rule.

## Fix step

Continues in the same session as the review, after REVIEW.md is written.

1. **Load PLAN.md before making any edits.** The review read the diff, not the
   intent behind it. This is the step that prevents regressions.
2. **Fix blockers only** unless told otherwise. Re-rank severity as an explicit
   step before touching code — an agent fixing its own findings will not
   otherwise drop anything.
3. **State the root cause before editing.** Symptom-patching moves bugs rather
   than removing them.
4. **Minimal diff.** Fix only the listed findings. No refactoring of adjacent
   code, no renaming, no opportunistic cleanup. Most new bugs come from
   "while I'm here" changes, not from the fix itself.
5. **Add a regression test per fix.** Tests are what make the loop converge
   mechanically instead of depending on a reviewer noticing.
6. **Record resolutions in REVIEW.md.**

## Convergence check

If fix diffs are not shrinking each round, the branch was too large or the spec
too underdetermined. Split the work smaller rather than prompting harder.
