# PLAN — none in flight

**Status:** ⏭ **NO IMPLEMENTATION IS PLANNED.** Written 2026-08-20, after PR #464 merged (`51a44c1c`).

This file exists so the next session finds an accurate empty rather than a stale plan describing shipped work. **The protocol's rule is that a stale `PLAN.md` is worse than none** — if you are about to write code, replace this file with a real plan *before* you start, including the round cap (2 for a patch, 3 for a minor).

---

## What just finished

The wrapper/internal parameter audit (#463). Its plan is archived at `development/plan-463-wrapper-audit.md`; **its result is `development/wrapper-parameter-audit-463.md`, which is the file to read.** The pass filed nothing new — every real finding landed on #383, #460 or #461 — so what it produced is measurement, not a backlog.

## Why there is no plan here

**The next step is four maintainer decisions, not work.** None of them should be made by a session alone:

1. **Mode 3 — where the strictness guard goes.** 40 of 52 wrappers silently accept an unrecognised keyword; 5 already reject it with a six-line guard that ships today (`_BooleanControlBase.__init__`). ⚠ **A blanket guard at the shared seam breaks the five wrappers that forward leftovers on purpose** (Chart, MenuButton, Picture, StatusBar, Toolbar), and `App`/`Window` never split at all. Seam-plus-opt-out vs per-wrapper is the call. Lands on **#383**, `0.5.0` — its fix raises, which is that milestone's rule.
2. ⚠ **#460's fix vs its milestone.** Dropping `| None` from eight annotations **retypes what a public property returns**, which is `0.5.0`'s membership rule verbatim — but **#460 sits on `0.4.0`, which it gates.** Settle before `0.4.0` is cut.
3. **#463's disposition** — close with the table as its artifact, or re-scope it into the durable guard below. Both options are on the issue.
4. **Whether the `_impl` naming inconsistency is worth an issue at all.** No user can see it and the audit's plan scoped `_impl` out.

## The one piece of real work that is already scoped

**A parameter-level guard test, written to the audit's five failure modes.** It is the half that does not decay, it needed the taxonomy to exist first, and it is a separate branch.

⚠ **Two things it must not inherit:**

- `tests/test_public_surface.py`'s blind spot — it gates the top-level *name set* and never asserts a submodule is unreachable as `bs.*`, which is how the `bs.events.X` drift survived two months.
- The audit probe's coverage hole. **84 params across `AppShell` (31), `Workbench` (34), `ThemeToggle`, `Notification` and `Snackbar` are UNANALYZED, not clean.** A guard built on the probe's reach silently inherits that.

⚠ **And one habit to carry, because it was paid for:** four of the audit's five tool defects were caught by *running* something rather than reading it, and three were false alarms pointing at working code. **A static wrapper check that is not cross-checked against real construction ships false findings.** The probe's `--arm leftovers` is the pattern — it constructs all 52 wrappers and compares the outcome against the static verdict.
