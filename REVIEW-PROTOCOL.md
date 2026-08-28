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

### Archiving both — BEFORE the PR is opened, not after the merge

Move `PLAN.md` and `REVIEW.md` into `development/` as
`plan-<issue>-<slug>.md` and `review-<issue>-<slug>.md`, **in the branch, in a
commit that precedes the PR.** They are the branch's record; `main`'s root
carries neither.

⚠ **Three branches in a row got the timing wrong.** PR #478 and PR #480 both
merged them into `main`'s root and archived afterwards, each caught only because
the next session happened to look; #444 was the first to archive first.
**Archiving after the merge means `main` briefly ships a root `PLAN.md`
describing work that is already done, which is worse than finding none.**

⚠ **`git mv` stages the rename of the *indexed* blob.** If you edited the record
before moving it — and the round's own record is written just before the archive,
so you did — the edits stay UNSTAGED and `git status` reads `RM`. A plain
`git commit` then ships the rename at **100% similarity** with a message
describing content the commit does not contain. **`git add` the moved file after
the `git mv`, and read `git show --stat`: a 100% rename is a failure whenever you
meant to change the content.**

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

## Stopping rules

The loop above terminates only if something bounds it. Severity triage is not
enough on its own — there is always another finding, and a review that reviews
its own previous round's output never runs out of work. These four gates are
mechanical on purpose; a rule that needs judgment gets reasoned around at
exactly the moment it is supposed to bind.

### 1. A round is triggered by a PRODUCTION diff, not by a commit

Before opening a round, run:

```
git diff <pre-fix-sha>..HEAD -- src/
```

**Empty means there is no round.** A commit that changes only tests, probes, or
documentation is self-checked by the session that wrote it and goes no further.

This is the gate the 0.3.1 dialog branch was missing. Round 4 there reviewed a
test-only commit, produced five findings about test diagnostics, and would have
produced a round 5 reviewing the fixes to those — while the four issues the
branch existed for had been fixed and verified since round 3.

### 2. Test code is reviewed on ONE axis: what defect can it let through?

Only two classes of finding about a test are actionable:

- **Vacuity** — the test can pass while the behavior it names is broken.
- **False alarm** — the test can fail while the behavior is fine (a flake).

Everything else about test code — diagnostic quality, error-message wording,
symmetry between helpers, probe ergonomics — is a **note in the record, never a
fix**. Write it down and move on.

A test's whole value is the production defect it catches, so that is the only
axis it earns review time on. Reviewing a test as code means reviewing the
instrument instead of the thing being measured, and an instrument can always be
made nicer — which is precisely why it does not terminate.

### 3. Declare a round cap in PLAN.md, before implementation

**2 rounds for a patch branch, 3 for a minor.** When the cap is reached,
surviving findings are filed as issues, not fixed on the branch.

Set it before there are any findings. A cap chosen afterward is chosen by the
session that wants one more round.

### 4. Probes are instruments; a flake gets ONE attempt

Probes under `development/` are committed as a record of what was measured.
They are **not reviewed code** and do not get findings filed against them.

⚠ The exception that still matters: if a probe's *conclusion* is cited as
settled — especially a refutation, where the probe reports finding nothing —
then the record must show the probe was capable of finding something. That is a
claim about evidence, not about code quality, and it belongs in the review
record rather than in a fix commit.

A flake gets **one** fix attempt, and it must come with a control that
reproduces the mechanism rather than a re-run that happens to come back clean.
If that attempt does not settle it, the test is quarantined and the flake is
filed as an issue. A second round of harness surgery on the same flake is the
loop this section exists to stop.
