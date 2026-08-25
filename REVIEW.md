# REVIEW — rounds 1–2 of 2 · `fix/select-validation-surface-465`

---

## ★ PICK UP HERE (written 2026-08-21, updated 2026-08-25 after round 2)

**⏭ BOTH ROUNDS ARE CLOSED, THE CAP IS SPENT, AND F13 — THE ONE THING THAT
BLOCKED THE MERGE — IS NOW FIXED.** The branch is green: **1524 passed / 22
skipped / 0 failed, 33 legs, exit 0.** Nothing is outstanding for a reviewer.

**Read in this order:** the **ADDENDUM at the very bottom** (the #449 fix and the
trap it nearly shipped), then **round 2's F13** for how it was found.

**F13 in one line: the branch made #449 fail ~9 of every 10 shared-root leg runs**
(`main` = 0 of 6), and it took BOTH the production change and the test change —
neither alone reproduced. **FIXED, test-only**, by draining the event queue in
`_reset_scene`. ⚠ **The addendum's warning matters more than the fix does: two
different changes silenced this flake WITHOUT fixing it**, so a green leg is not
evidence here. The guard that separates them is
`test_harness_event_queue.py::test_scene_reset_delivers_events_queued_with_when_tail`.

**No production code was touched after `3116cabb`** — round 2's fix was one
CHANGELOG sentence (F9) plus a test, and the #449 fix is test-only.
`git diff origin/main...HEAD -- src/` is unchanged since round 1, so gate 1 opens
no round 3. Round 2's F10/F11/F12 are notes, not work.

**Round 1 is CLOSED. Its fix is COMMITTED as `3116cabb`.** The branch is
`fadedf9d` (the implementer) + `3116cabb` (round 1's fix) + its record. Round 2's
record and its fix are **HELD IN THE WORKING TREE, uncommitted.**

### ✅ The open decision was TAKEN, by the maintainer, 2026-08-25

**A `Select` keeps ACCEPTING a `range` rule.** `_VALIDATION_KIND = None`, the
gate is skipped, #465 lands on `0.4.0` as a pure addition that changes nothing
a `Select` already did. **Do not re-propose the rejection** — the four-row table
in "Filed rather than fixed" at the bottom of this file is why, and
`py -3.12 development/probe_465_what_range_does_on_select.py` re-measures it.

⚠ **One fact settles it faster than the table does, and it was found only after
round 1 closed: the reporter never asked for `range`.** #465 uses a `custom`
rule and its stated need is a `required` rule with a custom message; the word
`range` does not appear in the report. The whole gate question was a side effect
of the mechanism chosen to fix #465, not a user requirement.

### ✅ The two pre-existing bugs are FILED — do not re-file them

- **[#467](https://github.com/israel-dryer/bootstack/issues/467)** — a `custom`
  rule's exception escapes into the event loop on an automatic trigger. On
  **`0.4.0`**: it is a plain defect, not a strictness change (the framework
  already raises there, just badly), and the milestone is open.
- **[#468](https://github.com/israel-dryer/bootstack/issues/468)** — a `Select`
  with `allow_custom_values=True` hands rules the raw typed text. **Unmilestoned
  deliberately**: fixing it means deciding how a `Select` learns its value type,
  which is design work, not a patch.

⚠ **This file's "Filed rather than fixed" section below routes both to `0.5.0`.
That was WRONG and is superseded.** Neither raises where the framework accepts
nor retypes a public property, so neither meets `0.5.0`'s membership rule; they
were sorted there by association with #383. **Read the issues, not that section,
for their disposition.**

### ~~⏭ ROUND 2 — what is left~~ — DONE 2026-08-25. Kept for the brief it set.

⚠ **This section is the brief round 2 was handed, not open work.** Both numbered
reasons below were checked and answered — see round 2's Summary. Reason 2's
"widened blast radius" turned out to be **one** consumer, `field_mixin.py:248`,
measured rather than assumed.

**Review `git diff fadedf9d..HEAD -- src/`** — 22 production lines across
`select.py` (`_VALIDATION_KIND = None` plus a 9-line comment) and
`field_mixin.py` (the annotation widened to `str | None`, the gate skipped on
`None`, two docstring edits). Cap is 2, spent 1.

**Two reasons this round is worth spending on a diff that small**, so it is not
waved through:

1. **Nobody independent has read those 22 lines.** Round 1's fix step was
   written by the session that reviewed it, which is the exact boundary
   `REVIEW-PROTOCOL.md` exists to enforce.
2. **The fix widened its blast radius.** `field_mixin.py` is inherited by all
   eight field widgets, so a `Select`-only defect was closed with an edit to
   shared infrastructure. The controls already catch the over-broad version
   (setting the mixin default to `None` fails two tests), but that is round 1
   checking its own work.

⚠ **THE REVIEWER MUST BE A FRESH SESSION.** The session that took the decision
above spent a long conversation arguing for it — for keeping `range` accepted,
for `_VALIDATION_KIND = None`, against attach-time rejection. That is
self-justification in exactly the form the session boundary is meant to exclude,
and a round 2 from it would be worth less than it looks. **Hand a new session
this file and `PLAN.md` and nothing else.**

### After round 2

1. Archive `PLAN.md` and `REVIEW.md` into `development/`, and **create
   `PLAN.md` fresh** — a stale one describing shipped work is worse than none.
2. Close #465 with **`gh issue comment`**, not `gh issue close --comment` — a PR
   body's `Closes #N` closes it at merge and the comment is then dropped
   silently.
3. `#383` gap 3 is cut and ready behind this, plan parked at
   `development/plan-383-unknown-kwarg-strictness.md`, round cap 3.

### What is already verified — do not re-run to satisfy yourself

Full harness **1480 passed / 21 skipped, 33 legs, exit 0** (deps-absent box);
docs clean-built `-W`, **0 warnings**; both fix-direction controls fail the right
tests. Details in **Verification**, below.

⚠ **Round 2 re-measured all three on a box where `matplotlib` and `pandas` are
now PRESENT and got `1521 / 22` with `1 failed` (F13).** Both totals are right for
their box; the arithmetic reconciling them is in round 2's Verification. **The
`exit 0` above no longer holds on this box** — that is F13, not movement in the
code.

---

**Diff reviewed:** `git diff main...HEAD` (base `9a910235`, head `fadedf9d`)
**Production diff:** `src/bootstack/widgets/select.py` — non-empty, so gate 1 opens a round.
**Round cap:** 2 (from `PLAN.md`). **Spent after this round: 1.**
**Box:** Windows, `py -3.12`. Docs clean-built (`-W --keep-going`), **0 warnings**.

**Suites run before the fix step:** `tests/widgets/public` `1056 passed / 14 skipped`,
`tests/test_public_surface.py` `166 passed`, the two touched test files `45 passed`.

---

## Summary

The inheritance is right and the tests are not vacuous — both controls I ran
found something (F7). One finding is blocking on its own merits and takes two
user-facing statements down with it: **the branch's justification for shipping
the validation-kind gate was measured on a `Select` that cannot exhibit the
behavior in question**, and the gate breaks working code.

| | severity | file |
|---|---|---|
| F1 | **blocking** | `select.py:27` / `field_mixin.py:24,244` |
| F2 | **blocking** | `CHANGELOG.md:16` |
| F3 | **blocking** | `docs/reference/events.rst:140` |
| F4 | should-fix | `test_field_validation_typed.py:169` |
| F8 | should-fix | `CHANGELOG.md:16` |
| F5 | nit | `PLAN.md` |
| F6 | note (gate 2) | `test_select_valid_error.py` |
| F7 | note | controls |

---

## F1 — **blocking** — `_VALIDATION_KIND = "text"` misclassifies `Select`, and the `range` rejection breaks working code

`src/bootstack/widgets/select.py:27` · `src/bootstack/widgets/_core/field_mixin.py:24`, `:244`

### Root cause

A `Select`'s value kind is set by its **options**, not by the widget.
`SelectBox._validation_value` (`_impl/composites/selectbox.py:384`) maps the
displayed label back to the option's value before any rule sees it, so a rule on
a decoupled option list receives the option's real Python object — an `int`, a
`date` — and not text. Inheriting the mixin's default `_VALIDATION_KIND = "text"`
therefore asserts something about `Select` that is false, and the gate built on
that assertion rejects a rule that works.

### Failure scenario

```python
tier = bs.Select([("One", 1), ("Seven", 7), ("Twelve", 12)], value=7)
tier.add_validation_rule("range", min=5, max=10)     # BootstackError on the branch
```

On `main` this app starts and the rule is correct: `7` validates, `12` does not.
On the branch it raises `BootstackError` at attach — i.e. at construction — so a
working app fails on launch. Same for `date` option values.

### Measured, both arms

`development/probe_465_select_range_kind.py`, run against the branch and against
a worktree at `main` (`9a910235`) via `PYTHONPATH`, provenance printed by the
probe on both runs:

| options | handed to the rule | `main` | branch |
|---|---|---|---|
| `["1","7","12"]`, value `"7"` | `'7'` *(str)* | range fails | REJECTED |
| `[("Seven","7")]` | `'7'` *(str)* | range fails | REJECTED |
| `[("One",1),("Seven",7),…]`, value `7` | `7` *(int)* | **range passes** | REJECTED |
| same, value `12` | `12` *(int)* | **range fails, correctly** | REJECTED |
| `[{"text":"Seven","value":7}]` | `7` *(int)* | **range passes** | REJECTED |
| `[("Jan",d1),("Jun",d2),…]`, value `d2` | `date` | **range passes** | REJECTED |
| same, value `d3` | `date` | **range fails, correctly** | REJECTED |

### Why the plan's measurement missed it

`PLAN.md` states its boundary — `rule_applies_to_kind` over the full rule set,
"cross-checked against live construction on a real `Select`" — and the
cross-check is what went wrong, not the reasoning. The `Select` it constructed
had **text equal to value** (`Select value=7 … value handed to the rule: '7'`).
`_validation_value` decodes *only* when the two differ, so that widget cannot
reach the decode and can only ever hand a rule a `str`. "It can never pass" is
true of that one `Select` and false of the widget.

That takes the milestone argument with it. "The migration count is zero" is the
whole reason the gate was allowed to ride `0.4.0` instead of the `0.5.0`
strictness batch; the count is not zero.

### Also internally inconsistent

The branch hands a `custom` rule the `int` `7` while telling the caller the field
is text, and on a `Select` of dates the rejection's hint reads
*"'stringLength' bounds text length."*

### Suggested minimal change

Do not misdeclare the kind, and do not re-copy the method. Let the mixin's
existing attribute carry "not fixed by the widget":

- `field_mixin.py` — widen `_VALIDATION_KIND` to `str | None`; skip the gate when
  it is `None`.
- `select.py` — `_VALIDATION_KIND = None`, with the reason in a `#` comment.

Three lines of production code. `Select` keeps the mixin's `add_validation_rule`
(so the hand-copy divergence that caused #465 does not come back), the break
disappears, and #465 ships as the pure addition its milestone expects. Whether a
`Select` should reject `range` **at all** is a real strictness question — it just
belongs in `0.5.0` beside #383 and #369, which is where the batching rule wants
it. Filed as a follow-up rather than decided here.

---

## F2 — **blocking** — the CHANGELOG states a falsehood about prior behavior

`CHANGELOG.md:16`

> *"Such a rule could never pass — it receives the selected value as text and
> compares it against numbers, so it reported 'invalid' for every value, in range
> or not."*

Disproved by F1: it receives the option's value, which for a decoupled option
list is an `int` or a `date`, and the rule is correct. `CLAUDE.md` names this
exact class — *"A CHANGELOG claim about PRIOR behavior must be checked against
the OLD code, not against the fix"* — and `git show main:…` settles it.

Once F1 is fixed the branch introduces no behavior change at all, so the entire
*"One thing to check when you upgrade"* passage goes rather than being reworded.

---

## F3 — **blocking** — the events reference still says `Select` emits only `change`

`docs/reference/events.rst:140-143`

`Select` sits in the *Boolean and selection controls* table with `change` as its
only event. The branch adds `valid` / `invalid` / `validate` and the CHANGELOG
announces `on_valid`, `on_invalid` and `on_validate` by name. The events
reference is the page a reader consults to learn what a widget emits, so leaving
it stale re-creates the discoverability defect #465 was filed for, on the events
half of the same fix.

`tests/test_events_doc_coverage.py` does not catch this: it gates payload *class*
names against `docs/api-reference/events.rst`, and `ValidationEvent` was already
documented there for the field family. The widget-to-event tables are unguarded.

Minimal change: one row.

---

## F4 — should-fix — `compare` is unpinned in the applicable-rule set

`tests/widgets/public/test_field_validation_typed.py:169-178`

`PLAN.md` says *"Pin all seven — the whole point is that only one moved."* Five
were added (`required`, `stringLength`, `pattern`, `email`, `custom`) plus the
`range` case. `compare` is missing, so the evidence that exactly one rule moved
has a hole in it.

Not blocking: `rule_applies_to_kind` returns `True` for `compare` on every kind,
so it is structurally incapable of being the rule that moved. Left for the fix
step to pick up alongside F1's test churn if it is free; otherwise a note.

---

## F8 — should-fix — the bullet files an addition under `### Fixed`

`CHANGELOG.md:16`

`PLAN.md` asked for this explicitly: *"It is both `Fixed` (no way to read a
validation outcome) and `Added` (`valid`/`error`/addons/events) — say which is
which."* The whole entry sits under `### Fixed`. The bullet does name every new
member, so a reader who reads it learns what arrived; a reader **scanning section
headings** for "did new API land?" does not.

Not blocking, and deliberately not fixed: splitting it means adding an `### Added`
section to `## [Unreleased]` and deciding how much of the sentence moves with it,
which is a call about how the `0.4.0` notes read as a whole — and `0.2.0` is on
record for the mirror-image mistake (three plain bug fixes filed under `Changed`,
handing a reader three false positives). That is a promotion-time judgement for
whoever reads the section end to end before tagging, which `CLAUDE.md` requires
anyway.

---

## F5 — nit — `PLAN.md` records a base the branch was not cut from

`PLAN.md` says **Base:** `main @ cfae3713`. The branch's merge-base is
`9a910235`, two docs-only commits later. Harmless today, but a later session
reconstructing the diff range from the plan picks the wrong `<pre-fix-sha>`.

---

## F6 — note (gate 2, record only) — the exact-event-list assertion is safe here

`test_select_valid_error.py::test_select_emits_valid_and_invalid` asserts
`kinds == ["invalid", "valid"]`. That is #449's shape, and the instinct to flag
it is right — but it does not apply: `ValidationMixin.validate`
(`_impl/mixins/validation_mixin.py:124-134`) calls `event_generate` with the
default `when="now"`, so both events dispatch synchronously inside the
`validate()` call rather than being queued. 5/5 repeat runs clean. Recorded so
the next session does not re-derive it.

---

## F7 — note — both controls found something, so the tests are not vacuous

Run before writing this record, and reverted after:

- **Detach the signal** — `FieldAddonMixin.valid` returns a fresh `Signal(True)`:
  3 tests fail, including `test_select_signals_are_the_entry_s_own_objects` on
  identity. Covers the "fix" that reads `True` forever.
- **Un-wire the events** — drop the three new `_SELECT_EVENTS` entries: 3 tests
  fail with `UnknownEventError`. Covers the second, independent cause.

Both halves of the fix are load-bearing on the suite. This is what `PLAN.md`
asked for as its item 7 and it holds.

---

# FIX STEP

Ran after this record was written. `PLAN.md` re-read first. **Blockers only** —
F1, F2, F3 — re-ranked before editing; F4 came along free with F1's test churn.

## F1 — FIXED

**Root cause restated before editing:** the gate asks the *widget* for a value
kind that only the *options* know. `Select` has no fixed kind, so any single
answer it gives is wrong for some option list; declaring `"text"` is wrong for
every numeric or date one.

- `src/bootstack/widgets/_core/field_mixin.py` — `_VALIDATION_KIND` widened to
  `str | None`, documented as `None` when the widget does not fix the kind, and
  `add_validation_rule` skips the gate on `None`. Typed wrappers
  (`'number'`/`'date'`/`'time'`) and the text default are untouched, so the seven
  other field widgets gate exactly as before.
- `src/bootstack/widgets/select.py` — `_VALIDATION_KIND = None` with the reason in
  a `#` comment (a warning for whoever edits the line, not for whoever reads the
  docs).

`Select` still inherits `add_validation_rule` from the mixin —
`"add_validation_rule" not in vars(Select)` still holds, so the divergence that
caused #465 stays closed.

**Regression tests** — `test_select_valid_error.py`:

- `test_select_range_rule_works_on_numeric_option_values` — attaches `range 5..10`
  to `[("One",1),("Seven",7),("Twelve",12)]` and asserts `7` validates and `12`
  does not. Fails on the pre-fix branch at the `add_validation_rule` call, and
  would fail on a fix that let the rule attach but broke the decode.
- `test_select_range_rule_works_on_date_option_values` — the same for `date`
  values, the other type `_validation_value` can return.
- `test_select_does_not_gate_rules_by_value_kind` — pins `_VALIDATION_KIND is None`
  on `Select` *and* that the seven other field widgets still declare a kind, so
  the opt-out cannot be widened into a family-wide gate removal unnoticed.

## F2 — FIXED

`CHANGELOG.md` — the *"One thing to check when you upgrade"* passage removed
entirely. With F1 fixed the branch adds surface and changes no behavior, so there
is nothing for a reader asking *"was I affected?"* to check. The rest of the
bullet (the missing `valid`/`error`, the events, the addon API) is unchanged and
was verified accurate.

## F3 — FIXED

`docs/reference/events.rst` — `Select` given its own row for
`valid` / `invalid` / `validate` → `ValidationEvent`, worded so it is clear the
three belong to `Select` alone among the selection controls.

**No test.** The widget-to-event tables are prose, and a guard over them is the
#412-shaped work the events reference already has open; adding one here would be
the "while I'm here" change step 4 warns about.

## F4 — FIXED (free, alongside F1)

`test_field_validation_typed.py` — the `Select` + `range` **rejection** case is
gone (F1 makes it false) and `Select` + `compare` joins the applicable set, so all
seven rule types are now pinned for `Select` as `PLAN.md` asked.

## F5, F6, F7, F8 — NOT FIXED, recorded only

F8 is a promotion-time judgement about how the release notes read as a whole, not
a defect in this branch (see the finding). F5 is a stale SHA in the implementer's
own artifact. F6 and F7 are notes about tests, which gate 2 says are recorded and
not fixed.

## Verification

Windows box, `py -3.12`.

- **Control — revert the two production edits, keep the new tests.** Exactly the
  four new/changed cases fail, and they fail *behaviorally* (`BootstackError` at
  attach), not with an `AttributeError` that would only prove the code is absent:
  `test_select_range_rule_works_on_numeric_option_values`,
  `…_on_date_option_values`, `test_select_does_not_gate_rules_by_value_kind`, and
  `test_applicable_rule_attaches_cleanly[Select-range]`. 4 failed / 45 passed.
- **Control the other way — set the mixin default to `None` instead of scoping the
  opt-out to `Select`.** 2 failed: `test_select_does_not_gate_rules_by_value_kind`
  and `test_inapplicable_rule_rejected_at_attach[TextField-range]`. So the
  over-broad fix is caught too; the two range tests alone would have passed it.
- `development/probe_465_select_range_kind.py` on the fixed branch — **identical
  to `main`, row for row**: `int` and `date` rows pass in range and fail out of
  range, `str` rows fail as they always have. The break is gone and nothing else
  moved. The probe's closing note records all three states so the comparison is
  not re-derived.
- `tests/widgets/public` + `tests/test_public_surface.py` +
  `tests/test_events_doc_coverage.py` — **1227 passed / 14 skipped**, exit 0. The
  `+4` over the pre-fix `1223` is `+3` new tests and `test_field_validation_typed`
  netting `-1 +2`.
- Full harness `py -3.12 tests/run_gui.py` — **1480 passed / 21 skipped, 33 legs,
  exit 0**, summed from the per-leg summary lines. ⚠ **`matplotlib` and `pandas`
  are BOTH ABSENT on this box right now**, so this is the deps-absent population,
  not the `1500 / 22` recorded in `CLAUDE.md`. Checked with
  `py -3.12 -c "import matplotlib"` / `import pandas` rather than assumed.
  **The movement is bounded rather than reconciled from memory:** the branch plus
  this fix touch exactly two test files, and `--collect-only` on those paths reads
  **27 on `main` → 49 here, +22** — which is the whole difference from the
  deps-absent baseline. Nothing else moved.
- Docs clean-built `-W --keep-going`, three times across the fix (before it, after
  the code and CHANGELOG edits, and once more after the final `events.rst`
  wording) — **0 warnings, build succeeded** each time. The generated
  `bootstack.Select` page now carries `valid`, `error`, `addons`, `insert_addon`,
  `update_addon`, `remove_addon`, `on_valid`, `on_invalid`, `on_validate`.
- `git diff main...HEAD -- CLAUDE.md` is empty, and so is the fix's.

**Fix diff size:** 22 production lines (16 of them the comment recording why
`Select` opts out), 3 docs lines, 1 CHANGELOG line, 64 test lines. Round 2, if it
is opened, reviews `git diff fadedf9d..HEAD -- src/`.

**Nothing is committed.** Held for the maintainer to test, per the standing
working agreement.

## Filed rather than fixed

⚠ **Re-scoped after the fix, on the maintainer's question "what does `range`
accomplish on a `Select`?" — which is a better question than the one I filed.**
Measured in `development/probe_465_what_range_does_on_select.py`; do not
re-derive it. `range` on a `Select` has **exactly one job, and it is broken in
the mode where a bound matters most**:

| scenario | what `range` does |
|---|---|
| user picks from a **fixed** option list | **nothing curating the list would not.** Offering `12` and then rejecting it is worse for the user than not offering it |
| an **off-list** value arrives — a retired option, `form.set()` of a stored record | **the one real job.** A `Select` displays an off-list value rather than rejecting it, by design, and a bound catches an out-of-range one. Works today |
| `allow_custom_values=True`, user **types** a value | **BROKEN.** Typed `'6'` reports invalid inside `5..10`, identically to `'99'` and to `'banana'` |
| empty | passes, by the rule's documented contract |

So the branch's instinct — *`range` on a `Select` is not sound* — was **partly
right, for a reason `PLAN.md` never found**. It is just not right in a way that
rescues an attach-time rejection, because the rejection also kills the off-list
row, which works.

### The two issues this actually surfaces — both PRE-EXISTING, neither touched by #465

1. **`allow_custom_values=True` silently fails every ordered comparison.** The
   typed text never decodes to a value (it is not in `_value_by_text`), so
   `_validation_value` falls through to the entry's raw text and `str < int`
   raises `TypeError` — which the `range` branch swallows as *"invalid"*
   (`validation_rules.py:149-151`). Every typed value is out of range, whatever
   it is.
2. **A `custom` rule doing the same comparison leaks a raw `TypeError`** — there
   is no `except TypeError` on that branch (`validation_rules.py:155-158`), and
   `range`'s default trigger is `blur`, so this escapes a blur handler into the
   Tk event loop. Same family as #383's *"args that raise but leak a raw
   `TclError`/`AttributeError`"*.

⚠⚠ **THE NEXT SENTENCE WAS WRONG AND IS SUPERSEDED — kept so the error is
visible rather than quietly swept.** ~~Both raise or retype where the framework
currently accepts, so they belong with #383 and #369 on `0.5.0 — Strictness and
value types`.~~ **Neither does.** #467 is a crash the framework already has, so
fixing it breaks nobody; #468 makes a rule that misreports start reporting
correctly, and nobody has code depending on `'6'` being rejected inside `5..10`.
They were sorted onto `0.5.0` by association with #383, which is a milestone
rule applied by proximity rather than by reading it. **Filed 2026-08-25 as
[#467](https://github.com/israel-dryer/bootstack/issues/467) on `0.4.0` and
[#468](https://github.com/israel-dryer/bootstack/issues/468) unmilestoned; the
issues carry their own disposition and supersede this section.** The measurement
above stands unchanged — it was the sorting that was wrong, not the evidence.

### What this does NOT change

F1 still stands and the fix still holds. The off-list row works on `main` and
raised at construction on the branch — a break is a break even when the thing
broken is narrow. Reverting to the rejection would mean moving #465 off `0.4.0`,
which trades an external reporter's fix for a strictness change that is only
one-third right.

---

# ROUND 2 of 2 — fresh session, 2026-08-25

**Diff reviewed:** `git diff fadedf9d..HEAD -- src/` — **non-empty (22 lines
across 2 files), so gate 1 opens the round.**
**Round cap:** 2 (`PLAN.md`). **SPENT: 2. THE CAP IS NOW REACHED** — anything
surviving this round is filed, not fixed on the branch.
**Box:** Windows, `py -3.12`. ⚠ **`matplotlib 3.11.0` and `pandas 3.0.3` are BOTH
PRESENT on this box now.** They were ABSENT when round 1 measured, which is why
the harness total below is not round 1's — read Verification before treating the
difference as movement.

**The fix step's rationale was not read before reviewing** (`REVIEW-PROTOCOL.md`:
requirements and findings, not "why this was sound"). The ★ block's settled
decision and `PLAN.md` were read up front; the fix step's own argument was read
afterwards, to write the resolutions.

## Summary

**The 22 production lines are correct, minimal, and narrower in reach than the
round-1 handoff's own caution implies** — measured rather than taken on trust:
`_VALIDATION_KIND` has exactly **one** consumer in `src/`, `field_mixin.py:248`,
the line the diff edits. "Shared infrastructure inherited by all eight field
widgets" is, here, a class attribute read in a single `if`. Both of round 1's
controls reproduce independently and name the same tests.

⚠ **The blocking finding is not in those lines. The branch turns #449 from
unobserved on `main` into a ~9-in-10 failure of the shared-root CI leg**, and it
takes BOTH halves of the branch to do it — neither the production change nor the
test change reproduces it alone. That is F13, it is measured across five arms and
28 leg runs, and it is a merge blocker that this round is not allowed to fix.

| | severity | file |
|---|---|---|
| F13 | **blocking (merge)** — #449, not fixable under gate 4 | `test_select_options.py:274` |
| F9 | should-fix | `CHANGELOG.md:16` |
| F10 | nit | `field_mixin.py:212` |
| F11 | note (gate 2) | `test_field_validation_typed.py:180` |
| F12 | note — pre-existing, belongs on #468 | `selectbox.py:384` |

---

## F13 — **blocking (merge)** — the branch makes #449 fail ~9 leg runs in 10, and it needs both halves of the branch to do it

`tests/widgets/public/test_select_options.py:274`

### What was observed

The full harness came back **1 failed**, and the failure is
`test_select_change_event_value_space` asserting `[None, 's'] == ['s']` — the
extra leading `None`, which is **#449** exactly. `Select` is what this branch
touches, so "it is a known flake" is not good enough on its own, and `CLAUDE.md`
is explicit that a flake is never disproved *or* dismissed by re-running.

### Measured — five arms, 28 runs of the shared-root leg

`pytest tests/widgets/public tests/cli -m "not isolated"`, one leg per run,
arms interleaved so they see the same machine conditions. `main` = `origin/main`
in a worktree with `PYTHONPATH` set.

| arm | src | tests | failures |
|---|---|---|---|
| branch, primary checkout | branch | branch | **9 / 10** |
| branch, worktree | branch | branch | **3 / 4** |
| `main`, worktree | main | main | **0 / 6** |
| mixed A, worktree | **main** | **branch** | **0 / 4** |
| mixed B, worktree | **branch** | **main** | **0 / 4** |

**12 of 14 with both halves; 0 of 14 with either half alone.** The two mixed arms
are the load-bearing rows — they are what rules out "the new test rows shifted the
ordering" *and* "the production change did it", each on its own.

It does **not** reproduce in isolation on either arm: the two-file narrow
combination (`test_field_validation_typed.py + test_select_options.py`) is
**0/10 branch, 0/10 main**, and the three-test trio around the failure
(`…reassignment_reconciles`, `…selected_index`, `…change_event_value_space`) is
**0/15 branch, 0/15 main**. It needs the whole leg's accumulated widget churn.

### Root cause — this is #449, not a new defect

The `None` is not invented by the branch. `test_select_options_reassignment_reconciles`
(`test_select_options.py:251`) reassigns `options` and asserts `s.value is None`
— *"stale 's' cleared"* — which emits a `<<Change>>` carrying `None`
**asynchronously** (`when="tail"`; see `reference_async_change_event_suspend_guard`).
The scene reset then destroys that widget with the event still queued. Two tests
later the queued event dispatches, and if Tk has recycled the destroyed widget's
path name onto the new `Select`, it lands on *that* widget's handler and prepends
`None` to `seen`.

That is #449's remaining open hypothesis word for word — *"stale bindings
surviving destroy while Tk recycles path names"*, recorded in `CLAUDE.md` as
**UNTESTED**. The branch does not create the event; it shifts widget-name
allocation enough that the recycling aligns almost every time.

### Why blocking even though the defect is pre-existing

Merging as-is turns the shared-root leg red on roughly seven of every eight CI
runs, on both ubuntu and windows. A branch does not have to introduce a defect to
be unmergeable; it has to leave CI usable.

### Why this round does not fix it, and what the options actually cost

Gate 4 gives a flake **one** fix attempt, #449 has spent it, and the endpoint the
gate prescribes — quarantine plus a filed issue — is half-done already: the issue
exists. Choosing among the three real options is a scope call, and the cap is
reached:

1. **Quarantine `test_select_change_event_value_space`.** ⚠ **Not free, and the
   cost is easy to miss: that test is #458's own regression guard** — it is the
   test that pins a `Select`'s change event carrying the value and not the label.
   Skipping it drops the guard on a fix that shipped four days ago.
2. **Fix #449 now.** Out of scope by the cap, but see below — it just got much
   cheaper.
3. **Merge with a known-red leg.** Only defensible with a decision recorded
   somewhere it will be found again.

### ⏭ The one genuinely good thing here: this branch is a #449 reproducer

#449 has been a ~1-in-10 heisenbug with two hypotheses ruled out by measurement
and no way to make it happen on demand. **This branch makes it happen ~88% of the
time, and the arm table above says which combination is needed.** Whoever takes
#449 should start from this branch, not from `main` — the "control that CREATES
the condition and reports a rate" that `CLAUDE.md` keeps asking for already
exists, in the five arms above.

---

## F9 — should-fix — the replacement CHANGELOG sentence is a prior-behavior claim, and it is not true

`CHANGELOG.md:16`

> *"Nothing a `Select` already did changes — the rules you attach today run
> exactly as before, and this only gives their outcome somewhere to go."*

### Root cause

With `_VALIDATION_KIND = None` no rule is rejected on kind grounds, so no rule
that attached before stops attaching — that much holds. But the branch does not
only drop the gate it briefly added: it replaces `Select`'s hand-copied
`add_validation_rule` with the mixin's, and **the mixin's carries a second guard
the hand-copy never had** (`field_mixin.py:241`) — a `TypeError` when `rule_type`
is not a string. `Select` inherits that with everything else. So one thing a
`Select` already did *does* change, and it changes at attach time, which is
construction time, which is exactly where round 1's F1 objection lived.

### Measured, both arms

Run against the branch and against a worktree at `origin/main`, provenance
printed on both:

```
                                 branch                  main
add_validation_rule(<non-str>)   TypeError at attach     accepted silently
then validate()                  (never reached)         True, error '' — forever
```

On `main`, a caller who passed a rule *object* instead of the rule-type string
got a field that silently never validated — **#465's own defect one level down**.
On the branch that same call raises at construction.

### Why should-fix and not blocking

Nobody has working code to break: what changes was already broken, and broken in
a way its author could not observe. The change is an improvement and should ship.
What should not ship is a release note telling a reader who *was* affected that
they were not. Same sentence position and same class of error as round 1's
blocking F2, and `CLAUDE.md` carries the rule verbatim — *"A CHANGELOG claim
about PRIOR behavior must be checked against the OLD code, not against the fix"*.
The guard is reachable public API, so by the CHANGELOG's own membership rule it
earns a mention rather than an absolute denial.

### Suggested minimal change

Drop the absolute clause and name the one thing that moved. CHANGELOG text only —
no production code, and no re-opening of the settled gate decision.

---

## F10 — nit — the mixin docstring names `Select`, and it renders on all eight field pages

`src/bootstack/widgets/_core/field_mixin.py:212-214`

The added sentence — *"A `Select` is the exception — its value kind is whatever
its options carry, so it accepts every rule type"* — is accurate, and on
`Select`'s own page it is exactly what a reader wants. But it sits in a docstring
on the shared mixin, so autodoc renders it on the other seven too. Verified in the
built HTML rather than assumed:

```
grep -rl "is the exception" docs/_build/html --include=*.html
  -> bootstack.{DateField,NumberField,PasswordField,PathField,Select,
                SpinnerField,TextField,TimeField}.html
```

Seven of the eight audiences get a paragraph about a widget they are not reading
about. If it is ever touched, phrasing it by property rather than by name — *"a
field whose value kind is not fixed by the widget accepts every rule type"* —
reads correctly on all eight, and `docs/widgets/select.rst` already carries the
`Select` specifics. **Not fixed**: a nit, and the round-2 fix step is holding its
production diff at zero on purpose.

---

## F11 — note (gate 2, record only) — the `compare` row attaches with `other_field=None`

`tests/widgets/public/test_field_validation_typed.py:180`

`(lambda: bs.Select([("Five", "5")], value="5"), "compare", {"other_field": None})`
in `test_applicable_rule_attaches_cleanly`. The test's axis is *does attach
raise*, and it does not, so the row is correct today and not vacuous — control A
below shows the parametrization can fail. Recorded because a later change that
validates `other_field` **at attach** would turn this row into a false alarm
pointing at working code, and the next session should recognise it rather than
re-derive it.

Also recorded, and **not** a finding against this branch: the mixin's
`isinstance(rule_type, str)` guard (`field_mixin.py:241`) has **no test anywhere**
— `grep -rn "takes a rule-type string" tests/` returns nothing. A pre-existing
family-wide gap. F9's fix pins it on `Select`, because a CHANGELOG claim with no
test behind it is how #458's round 1 went wrong.

---

## F12 — note — `range` on a plain-string option list still silently always fails, and the branch now advertises "every rule type"

`_impl/composites/selectbox.py:384` · pre-existing, untouched by the branch

```
bs.Select(["10", "20", "30"])  +  add_validation_rule("range", min=5, max=25)
  -> invalid for every option, on main AND on the branch
```

Same swallowed-`TypeError` root as **#468**, but a *different path*, and #468's
body does not describe it: there the option-list lookup **misses**; here it
**succeeds** and the option's value genuinely is a `str`, so `'20' < 25` raises
`TypeError` and `validation_rules.py:149-151` catches it and reports "invalid".

Out of scope by the cap and by gate 1. Worth a comment on **#468** widening its
mechanism section rather than a new issue, because the fix is the same decision:
how does a `Select` learn its value type.

⚠ **The neighbouring worry does NOT hold, and it is measured rather than
assumed:** text rules on typed option values do not crash. `stringLength(min=5)`
on the `int` `7` reports invalid with *"Enter at least 5 characters."*, and
`pattern` stringifies the same way. So the docstring's *"accepts every rule
type"* does not invite a crash — only F12's silent misreport, which predates it.

---

## What I checked and found nothing on — recorded so this round's silence means something

- **Blast radius, measured not argued.** `grep -rn "_VALIDATION_KIND" src/` → five
  declarations (`field_mixin`, `datefield`, `numberfield`, `timefield`, `select`)
  and **one** read, `field_mixin.py:248`. The widened annotation reaches nothing
  else, and `rule_applies_to_kind`'s `kind: str` signature is never handed a `None`
  because the new guard short-circuits first.
- **The new guard is load-bearing, not decorative.** `rule_applies_to_kind(rt,
  None)` returns **False** for `TEXT_RULES` and for `range` — `None == "text"` and
  `None in ("number","date","time")` are both false — so deleting the
  `kind is not None and` would invert the intent and reject four rule types on a
  `Select`. Four rows of `test_applicable_rule_attaches_cleanly` catch that.
- **MRO shadowing from the inheritance.** `vars(FieldAddonMixin) &
  vars(PublicWidgetBase)` is **empty**, so inserting the mixin displaces nothing on
  `Select`; `Select` overrides exactly `text` and `_VALIDATION_KIND`.
  `_flex_vertical_default` still resolves to `"top"`, matching `TextField` — the
  attribute the implementer deleted from `select.py` now comes from the mixin, and
  `test_select_keeps_the_family_row_alignment_default` pins it.
- **`Form` does not change, and this was the most plausible unannounced behavior
  change.** `Form._validity_entry` (`form.py:308-320`) probes
  `internal._entry._valid_signal` — the *internal*, which a `Select` already had on
  `main`. The new public `valid` is not on that path, so form-level validity
  aggregation is untouched by #465.
- **`.valid`/`.error` cannot `AttributeError`.** `Field.__init__`
  (`_impl/composites/field.py:216-220`) assigns `self._entry` on every branch, so
  there is no `Select` configuration where the two properties have nothing to read.
- **"`Select` only" in `events.rst` is true.** `SelectButton`, `RadioGroup` and
  `ToggleGroup` all report `hasattr(w, "add_validation_rule") is False`.
- **The events row is well-formed** — three columns in a three-column
  `list-table`, and the clean `-W` build agrees.

## Verification

Windows box, `py -3.12`. Every number below was produced this session.

- **Round 1's control A, reproduced independently.** Rather than editing the two
  production lines back, a pytest plugin sets `bs.Select._VALIDATION_KIND = "text"`
  at `pytest_configure` — the `fadedf9d` state, source untouched. **4 failed / 45
  passed**, the same four the record names, failing *behaviorally*
  (`BootstackError: the 'range' rule does not apply to a text field (Select)`) and
  not with an `AttributeError`.
- **Round 1's control B, reproduced.** A plugin setting
  `FieldAddonMixin._VALIDATION_KIND = None` — the over-broad fix — gives **2 failed
  / 47 passed**: `test_select_does_not_gate_rules_by_value_kind` and
  `test_inapplicable_rule_rejected_at_attach[TextField-range]`. The opt-out cannot
  be widened to the family unnoticed.
- **`development/probe_465_select_range_kind.py` re-run against `origin/main`**
  through a worktree, `PYTHONPATH` set and the probe's provenance line printing the
  worktree — **row for row identical to the branch**: `int` and `date` rows True in
  range and False out of it, `str` rows False. Round 1's F1 evidence now stands on
  both arms as something observed here, not inherited.
- **Full harness `py -3.12 tests/run_gui.py`** — **1521 passed / 22 skipped / 1
  failed**, 33 legs, summed from the per-leg summary lines. The one failure is F13.
  ⚠ **This is the deps-PRESENT population and round 1's `1480 / 21` was
  deps-absent** — `matplotlib` and `pandas` were installed on this box in between,
  checked with `py -3.12 -c "import matplotlib"` / `import pandas` rather than
  inferred. It reconciles exactly against `CLAUDE.md`'s deps-present figure for
  `main`: `1500 + 22 (the branch's two test files) = 1522 = 1521 passed + 1 failed`.
- **Docs clean-built** — `rm -rf docs/_build && sphinx-build -b html docs
  docs/_build/html -W --keep-going` — **exit 0, "build succeeded", 0 warnings**.
  All nine new members render on `bootstack.Select.html`.
- ⚠ **`pytest tests/widgets/public …` as ONE process is not a green baseline on
  either arm, and a session that runs it will think this branch broke something.**
  It gives **2 failed / 4 errors** on the branch and **1 failed / 4 errors** on
  `main`; the four `test_appshell_shortcuts` errors are identical on both and the
  `test_app_config` failure moves between tests run to run. **Use
  `tests/run_gui.py`**, which splits the legs — the directory in one process is an
  artifact of the invocation, not of the code.
- **CRLF preserved** on all touched files (`file <path>`), and
  `git diff origin/main...HEAD -- CLAUDE.md` is **empty**.

# FIX STEP — round 2

Ran after the record above was written. `PLAN.md` re-read first. Severity
re-ranked before editing: **F13 is the only blocking finding and it is out of
this round's reach** (gate 4 — a flake gets one attempt and #449 has spent it;
the cap is reached, so the remaining choice is a scope call). **F9 is fixed.
F10, F11, F12 are recorded only.**

⚠ **The round-2 fix touches NO production code.** `git diff <this-fix> -- src/`
is empty, which by gate 1 means it opens no round 3 — the loop terminates here on
its own terms rather than on the cap alone.

## F13 — NOT FIXED. Escalated to the maintainer with its measurement.

Nothing was quarantined, nothing was re-run to make it go away. The five-arm
table in the finding is the deliverable. The three options and what each costs
are written out there; option 1 (quarantine) is the one gate 4 nominally
prescribes and it is **not free**, because the test in question is #458's own
regression guard.

## F9 — FIXED

**Root cause restated before editing:** the branch replaced `Select`'s
hand-copied `add_validation_rule` with the mixin's, and the mixin's carries an
`isinstance(rule_type, str)` guard the hand-copy never had. The sentence claimed
nothing a `Select` already did changes; that one thing does.

- `CHANGELOG.md` — the absolute clause is gone. The bullet now says the rules you
  attach today run exactly as before, then names the one behavior that moved:
  passing anything other than a rule-type string raises `TypeError` instead of
  being accepted and then silently ignored. One paragraph, unwrapped, per the
  CHANGELOG convention.
- `tests/widgets/public/test_select_valid_error.py` —
  `test_select_rejects_a_non_string_rule_type`, pinning both halves: the
  `TypeError` **and** that the working spelling still attaches, so an over-broad
  guard cannot pass it.

**Control, run once and recorded:** the new test against `origin/main`'s source
through the worktree fails with **`Failed: DID NOT RAISE <class 'TypeError'>`** —
behavioral, not an `AttributeError` that would only prove a member is absent.
Against the branch it passes.

⚠ **One phrase in the same bullet was considered and deliberately LEFT:**
*"emitted no `valid`/`invalid` events"*. Strictly the entry's `ValidationMixin`
did emit `<<Valid>>`/`<<Invalid>>` on `main` — there was simply no public event
name to subscribe to, which `test_select_valid_error.py`'s own docstring records.
From the reader's vantage the two are indistinguishable: no subscription was
possible, so no event arrived. Rewriting it would trade a true user-facing
sentence for an implementation detail. **Not a defect; do not "fix" it.**

## F10, F11, F12 — NOT FIXED, recorded only

F10 is a docstring-altitude nit and the fix step is holding its production diff at
zero deliberately. F11 and F12 are notes about tests and about pre-existing
behavior, which gate 2 and the cap say are recorded and not fixed. F12 belongs as
a comment on **#468**, not as a new issue.

## Verification of the fix

- `tests/widgets/public/test_select_valid_error.py` +
  `test_field_validation_typed.py` — **50 passed**, exit 0 (was 49; `+1` is the
  new test).
- Control above: the new test fails on `main`'s source for the right reason.
- Docs clean-built again after the CHANGELOG edit (`rm -rf docs/_build` +
  `-W --keep-going`) — **exit 0, "build succeeded", 0 warnings**, and the new
  sentence renders on `release-notes.html`.
- `git diff --stat` for the fix: **CHANGELOG.md 1 line, one test file 24 lines,
  `src/` untouched.**
- CRLF preserved on both edited files (`file <path>`).

**Nothing is committed.** Held for the maintainer, per the standing working
agreement.

## ⏭ What the next session needs, in order

1. **Decide F13.** It gates the merge and nothing else on the branch does. ⚠ **Do
   not re-measure it first** — the five-arm table is 28 leg runs and the arms that
   matter are the two mixed ones. If #449 is to be fixed rather than worked
   around, **this branch is the reproducer**; `main` is not.
2. Then the "After round 2" list at the top of this file — archive `PLAN.md` and
   `REVIEW.md` into `development/`, create `PLAN.md` fresh, close #465 with
   `gh issue comment`.
3. F12 as a comment on #468. F10 whenever `field_mixin.py` is next open.

---

# ADDENDUM — #449 FIXED (2026-08-25, maintainer-directed, after the cap)

**This is not a review round.** Round 2 closed at the cap; the maintainer asked
for F13 to be fixed so the branch can merge. **Test-only —
`git diff origin/main...HEAD -- src/` is still empty for the whole branch**, so
gate 1 opens nothing.

## Root cause — caught end to end, not inferred

An event generated with `when="tail"` is queued against the emitting **window**,
not against the Python widget object. `SelectBox.value` emits one on every
committed change (`selectbox.py:1213`); about twenty other composites do the
same. `tests/conftest.py::_reset_scene` destroyed a test's widgets **without ever
pumping the event loop**, so an event queued by the last statement of one test
was still in the queue while the next test built its widgets.

**The evidence is a payload match, not a plausible story.** Instrumenting a full
shared-root leg pinned the emit; a temporary diagnostic on the assertion pinned
the delivery:

```
EMIT      .!flexframe.!selectbox31.!frame.!textentrypart   'Small' -> None
             (test_select_options_reassignment_reconciles)
DELIVERED .!flexframe.!selectbox33.!frame.!textentrypart
             (test_select_change_event_value_space)
          seen=[(None, 'Small', ''), ('s', None, 'Small')]
```

`(value=None, prev_value='Small', text='')` is byte-for-byte the `ChangeEvent`
the earlier test emitted, arriving at a **different** `Select`'s handler two
tests later. Tk path names are never reused — the per-parent counter only climbs,
and `selectbox31` vs `selectbox33` proves it — so the delivery is not by name.

⚠ **The exact toolkit route is NOT pinned down, and the record should not
pretend otherwise.** Window-handle reuse is the obvious candidate and
`development/probe_449_queued_event_after_destroy.py --arm churn` was built to
force it — **300 rounds, 8 widgets each, zero handle reuse and zero stray
deliveries**, with its `control` arm proving it can detect a delivery at all. So
the route is unproven. It does not need to be: the fix removes the *precondition*
(an event outliving its widget), which is sufficient whatever the route.

## The fix

`tests/conftest.py::_reset_scene` now calls `root.update()` **before** the
destroy loop, so anything the test queued is delivered to its own widget while
that widget is still alive. Guarded with `except Exception` like the rest of the
function, since it runs during teardown.

## ⚠ THE TRAP THIS NEARLY SHIPPED — read before touching this again

**A rate is NOT sufficient evidence for this flake, because things that are not
fixes also silence it.** Two separate times a change made the leg go green for
the wrong reason:

1. **Instrumenting the leg silenced it.** The first instrument patched
   `tkinter.Misc.event_generate` globally (tens of thousands of calls per leg)
   and the leg passed — the instrument hid what it was measuring. The second one
   patched only the rare emit/subscribe calls and still passed twice.
2. **`update_idletasks()` silences it and is NOT a fix.** Measured over the
   shared-root leg, three arms interleaved, five rounds each:

   | `_reset_scene` pump | leg runs failing |
   |---|---|
   | none (the shipped state) | **4 / 5** |
   | `update_idletasks()` | 0 / 5 |
   | `update()` | 0 / 5 |

   `update_idletasks()` does **not** service queued window events —
   `probe_449_queued_event_after_destroy.py` measures it directly: after
   `update_idletasks()` the tail event is still undelivered, after `update()` it
   has arrived. It silences the flake by shifting timing, exactly as the
   instrumentation did.

**So the guard asserts the invariant, not the symptom** (`CLAUDE.md`'s own rule
for allocator- and timing-dependent bugs). `tests/widgets/public/test_harness_event_queue.py::
test_scene_reset_delivers_events_queued_with_when_tail` queues a probe event on
the **root** — which the reset never destroys, so a failure means the queue was
not drained rather than that a binding died with its widget — calls
`_reset_scene` directly, and asserts the event arrived. It carries a precondition
assert so it cannot pass vacuously if `when="tail"` ever became synchronous.

**Controls, run and recorded:**

| conftest under test | the new guard |
|---|---|
| no pump (the shipped state) | **FAILS** |
| `update_idletasks()` (the shim) | **FAILS** |
| `update()` (the fix) | passes |

It is the only instrument here that separates the fix from the shim; the rate
cannot.

## Verification

- **Full harness `py -3.12 tests/run_gui.py` — 1524 passed / 22 skipped / 0
  failed, 33 legs, "All GUI test legs passed", exit 0.** Reconciles exactly
  against round 2's figure: `1521 passed + 1 failed = 1522`, `+1` for round 2's
  F9 test and `+1` for the new guard = **1524**, with the former failure now
  passing.
- The shared-root leg ran **0 / 10** failures with the fix across the two rate
  measurements, against **4 / 5** for the shipped state in the same session.
- CRLF preserved on `tests/conftest.py`, the new test file and the probe.

## ⏭ What is NOT fixed — FILED AS [#469](https://github.com/israel-dryer/bootstack/issues/469)

**The same hazard exists in the product, and the harness fix does not touch it.**
Any composite that emits with `when="tail"` and is then destroyed before the loop
turns leaves an event queued against a dead window. In an application that is
reachable — a handler that commits a value and then tears its page down does
exactly this — though far rarer than in the harness, because a running app pumps
its loop continuously and the window is microseconds rather than a whole test.

**It is a separate issue from #449**, which is filed as a test flake and is now
genuinely closed by a test-only change. **Filed 2026-08-25 as
[#469](https://github.com/israel-dryer/bootstack/issues/469), `bug`, deliberately
UNMILESTONED** — it gates no release, so placing it is a scope call. Its two
candidate fixes are written out there: drop `when="tail"` (deliberate, and #354
leans on it) or carry the emitter's identity in the payload and drop mismatches
at dispatch, which is public-event-path work. **The issue also records that the
toolkit route is unproven**, so a later session does not read the handle-reuse
theory as settled.
