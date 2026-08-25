# REVIEW — round 1 of 2 · `fix/select-validation-surface-465`

---

## ★ PICK UP HERE (written 2026-08-21, updated 2026-08-25)

**⏭ THE WORK IN HAND IS ROUND 2. Everything below round 2 is settled and
committed — read it, do not redo it.**

**Round 1 is CLOSED. Its fix is COMMITTED as `3116cabb`.** The branch is
`fadedf9d` (the implementer) + `3116cabb` (round 1's fix) + this record.
Nothing is held in the working tree any more.

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

### ⏭ ROUND 2 — what is left

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
