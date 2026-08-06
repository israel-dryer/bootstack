# Code review — `fix/datatable-double-click-417`

**Reviewed commit:** `69f92b05` (6 commits, `main...69f92b05`)
**Date:** 2026-08-06
**Reviewer:** concurrent agent, read-only — see *Method* below.
**Verdict:** solid branch, ship-ready. One release-line decision needs the
maintainer; everything else is minor.

---

## Method (why you can trust this without re-running it)

The review ran **while another agent was working in the same tree** on
`fix/datatable-click-focus-421`. Nothing was checked out, stashed, committed, or
put in a worktree. Every line reviewed came from committed blobs
(`git show 69f92b05:<path>`) and `git diff main...69f92b05` — never from the
working copy, which at the time carried that agent's uncommitted edits to
**the same two files** (`tableview.py`, `test_datatable.py`).

⚠ **This is the trap to remember for the next concurrent review.** Both branches
pointed at the *identical* commit `69f92b05` — `fix/datatable-click-focus-421`
was a fresh branch off 417's tip with its work still uncommitted. So `Read`ing
`tableview.py` would have silently reviewed **421's work-in-progress** while
reporting on 417. Check `git rev-parse` on both branches before assuming a
branch name tells you which code you are looking at.

**Branch topology, verified not assumed:** 417 is **3 commits behind `main`**,
all of them `docs(claude):` handoff commits (`5e3ace3a`, `30e88bcf`, `fbc0b235`).
417 touches **no `CLAUDE.md`** — confirmed with
`git diff --stat main...69f92b05 -- CLAUDE.md` (empty). So the
**handoff-revert trap does not apply here**. Run that diff anyway before merging;
it is what caught the near-miss on PR #410.

**The suite was NOT run.** Two reasons, both real: (1) when the review started
the tree held 421's uncommitted edits, so any run would have measured *that*
code, not 417's; (2) these tests call `focus_set`/`focus_force` and depend on a
mapped window, so a second Tk process stealing focus is a concrete way to break a
concurrent GUI run. **Someone must still run `py -3.12 tests/run_gui.py` once 421
is parked** — this review is static.

---

## What was verified (not assumed)

- **The `iid not in self._row_map` guard is exact.** Group parents are written
  only to `_group_parents` (`tableview.py:3382`); data rows only to `_row_map`
  (`:3395`, `:3356`). The guard therefore identifies "group header or unknown
  item" precisely, and it makes `_on_row_double_click` and `_on_row_context`
  match `_on_row_click_event`, which already carried this exact test. Genuinely
  consistent, not merely similar-looking.
- **No binding accumulation from the unconditional `<Double-1>`.** `_build_tree`
  is called exactly once (`:475`), and the bind is a plain `bind` with no
  `add=`, so it cannot stack — including alongside the `add="+"` chevron binds.
- **The deferred chevron refresh is safe after teardown.** Scheduling on
  `self._root()` matches the rule already recorded in `CLAUDE.md` (the root
  outlives the widget, so the pending callback is not deleted mid-flight). The
  callback also survives a *destroyed* widget: `_group_by_key` and
  `_group_parents` are plain Python attributes, and every `self._tree.item()`
  call sits inside `try/except Exception`. Nothing reaches the background-error
  channel.
- **The one synchronous call site is correctly left synchronous.**
  `_refresh_group_chevrons()` at `:2193` runs from the theme-repaint path, where
  there is no open-state race to defer around.
- **A suspected conflict was chased down and is a non-issue.**
  `_update_selection_markers` writes `image=` over every *top-level* item —
  which in grouped mode would be the group headers, clobbering the chevrons
  #419 just fixed. But `_selection_markers_active()` returns `False` whenever
  `_group_by_key` is set (`:2239`). No collision. Recorded here so nobody
  re-derives it.

---

## Findings

### 1. Needs a maintainer decision — a `### Changed` section on the patch line

The `[Unreleased]` block targets **0.2.2**, and `CLAUDE.md` states the patch line
is **bug fixes only**. Both listed consequences are bug-adjacent (the second
press of a double-click no longer double-acts), so **patch is defensible and is
the reviewer's lean** — but 0.2.0 set the precedent of taking a whole minor for a
single behavior change (#381), and this is the same class of judgment.

**Decide it explicitly and record the reason**, rather than letting the `Changed`
heading ride through by default. That is the only item here that should block a
tag.

### 2. `on_row_click` fires twice per double-click — newly reachable

`<ButtonRelease-1>` has no `<Double-…>` counterpart, so **both** releases
dispatch `_on_row_click_event`. A double-click therefore produces **two
`<<RowClick>>` events plus one `<<RowDoubleClick>>`**.

This is **not a regression** — it was equally true before the branch, and on
`allow_edit=True` tables all along. What changed is *reachability*: until now
`on_row_double_click` never fired on read-only tables, which is the common case,
so nobody combined the two handlers. The obvious thing a user writes next is
"single click selects, double click opens" — and the click handler will run
twice.

**Action:** a line in the events docs, or a third bullet in the `Changed` entry.
No test covers the interaction.

### 3. `_double_click` test helper hardcodes `time=100/120`

Times are **non-monotonic across calls** on the shared root. It is fine today
because each call in the file targets a distinct position or widget, but two
calls at the same coordinates on the same tree would send time *backwards*, and
Tk's click-count detection would drop the double-click. That is an
order-dependent failure, in a suite `CLAUDE.md` already documents as
order-fragile — and it would fail as a confusing "the fix is broken" signal.

**Action:** a module-level counter so synthesized times always increase. Two
lines.

### 4. Coverage gap on the worst symptom of #420

The CHANGELOG's user-visible harm for #420 is a **spurious modal New Record
dialog** on `allow_edit=True`. Only `development/probe_021_allow_edit_group_header.py`
exercises it — there is **no test**. It routes through the same guard, so the
risk is low, but it is the symptom a user actually sees.

### 5. Minor — macOS right-click paths uncovered

`_right_click` synthesizes `<Button-3>`, which `bind_right_click` binds on
**every** platform (`_runtime/utility.py:425`), so the test is portable and will
pass on the macOS box. But the aqua-only `<Button-2>` and `<Control-Button-1>`
bindings get **no coverage** of the new group-header guard. Cheap to
parametrize.

### 6. Trivial — issue citation drift in the history

`638b24e3` is titled `(#417)` for the fix the CHANGELOG cites as **#420**. This
was knowingly re-cited later in `36ae3720`, so the **shipped notes are correct**;
only the commit history reads oddly. No action needed — noted so it is not
"discovered" again.

---

## Positive notes worth keeping

- The tests are **better than the repo average** and match the standards in
  `CLAUDE.md` that are usually honored in the breach: real preconditions
  (`bbox() != ''` before clicking, `identify_row()` hit-test assertions), real
  **controls** (the leaf-row click that proves an empty result means "guarded",
  not "the test cannot click"), and docstrings that state plainly where a test is
  weak — `test_row_double_click_bound_regardless_of_editing` documents its own
  vacuity risk instead of overselling.
- The tests live in `tests/widgets/public/`, which **is** in `testpaths` — they
  will actually run, unlike the 12 files stranded directly under
  `tests/widgets/`.
- The probes were **committed to `development/`** rather than left in a session
  scratchpad. That is the #407 lesson applied.
