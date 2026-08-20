# PLAN — wrapper/internal parameter audit (measurement pass)

**Issue:** [#463](https://github.com/israel-dryer/bootstack/issues/463) · **Milestone:** `Wrapper and internal parity` (unnumbered — see Placement)
**Branch:** not yet cut — suggested `audit/wrapper-parameter-delta`
**Base:** `main` @ `41c8bad1` (the #458 merge)
**Status:** ✅ **EXECUTED AND ARCHIVED 2026-08-20.** Ran on branch `audit/wrapper-parameter-delta`, merged as PR #464 (`51a44c1c`). Written 2026-08-20 by the session that merged #458, for the session that ran it.

⚠ **This is a HISTORICAL plan. The RESULT is `development/wrapper-parameter-audit-463.md`** — read that, not this, for what was found. Kept because its five failure modes, its oracle and its non-vacuity design are what the pass was built to, and the durable guard still has to be designed to the same taxonomy.

**Two of its predictions were right and cost real work:** the four window-family wrappers really were invisible to a tool that assumes one forwarding idiom (84 params recovered by an alias hop), and the controls really were free. **One instruction in it was wrong** — it says the #458 control runs at `main~`; `main~` is two docs commits after the merge, so the real pre-fix commit is `1f9a62d1^`.

**Release line:** none — this pass ships **no production code**. It produces a table and files issues. Whatever fixes come out of it get scoped, milestoned and planned separately, by the maintainer, after the table exists.

**Round cap: 0 for the measurement itself.** `git diff main...HEAD -- src/` must stay empty for the whole pass; if it does not, the pass has turned into a fix branch and needs its own plan and its own cap (gate 1, gate 3). ⚠ **The probe is an instrument, not reviewed code (gate 4)** — but this one is the exception gate 4 names: **its conclusion will be cited as settled, so it must be shown capable of finding something.** See `Non-vacuity` below.

---

## Why

**Maintainer, 2026-08-20:** *"the wrappers were not sufficiently designed or reviewed. In many cases the bugs derive from the wrapper, not the `_impl` widgets... at some point we need to do a more in-depth review of the wrapper vs original widget so that we can get these before they surface."*

This is the dominant recent defect pattern, and `CLAUDE.md` already records #458 as *"the THIRD 'the internal was right, the wrapper was the defect' IN A ROW."* The existing check — `git show main:<wrapper> | grep <kwarg>` — catches exactly one of the five ways it goes wrong.

## The five failure modes, with a real example each

| # | mode | example | caught by the existing grep? |
|---|---|---|---|
| 1 | **never forwarded** — the kwarg exists on the wrapper and never reaches the internal | #383 gap 3, #456 | ✅ yes |
| 2 | **wrong destination** — forwarded, to the wrong internal parameter | **#458**, **#461** | ❌ no |
| 3 | **swallowed as a layout key** — falls into `**kwargs`, `_split_layout_kwargs` eats it, nothing raises | #456 | ❌ no |
| 4 | **accepted then ignored** — reaches the internal and is overwritten by something recomputed | #453 | ❌ no |
| 5 | **the type lies** — the annotation describes a value the code cannot produce | #460 (eight widgets) | ❌ no |

⚠ **Mode 2 is the one that keeps landing and the one no tool currently sees.** `CLAUDE.md`: *"The existing check catches ABSENCE. It does not catch THE WRONG DESTINATION, which is what this was."*

## The surface — MEASURED, not estimated

Measured 2026-08-20 on `main` at `41c8bad1` with an `ast` pass over `src/bootstack/widgets/*.py`:

```
77 public wrapper classes · 890 named params · 62 with a **kwargs catch-all
```

**That is ~4x the #381 sweep (215 kwargs) and is why this cannot be a reading review.** It has to be mechanical, and the output has to be a ranked table rather than a verdict.

⚠ **THE SCAN ALREADY FOUND ITS OWN FIRST TRAP: `App` (28 params), `AppShell` (31), `Workbench` (34) and `Window` (21) have ZERO `internal_kwargs` references** — 114 params that forward through `APP_CONFIG_KWARGS` and other idioms instead. **A tool that assumes one forwarding idiom will report those four as clean.** Enumerate the idioms before trusting any "no findings" result on a wrapper.

## The oracle that makes this tractable

**The internal widget is the specification.** For most wrappers this is not code review — it is diffing two signatures and classifying the delta. Modes 1–3 and 5 are a pure AST pass; mode 4 needs the runtime construct-with-a-bogus-value probe already proven on #381.

Mode 2 is the only one needing a human, and it should be **short**: flag every case where wrapper param `X` forwards to internal key `Y` with `X != Y`. Every legitimate rename plus every #458 lands in that list. **#458 would have been in it.**

## Deliverable

**One committed probe and one table. No fixes.**

1. `development/probe_wrapper_parameter_delta.py` — the scan, runnable on any box, ASCII output only.
2. A table per wrapper: param, whether it reaches the internal, where it lands, and which mode (if any) it trips.
3. Findings filed as issues, ranked. **Do not fix them here** — `CLAUDE.md`'s rule is that a survivor is filed, not fixed, and this pass is all survivors by construction.

## Non-vacuity — REQUIRED before any "no findings" is believed

⚠ **A probe that finds nothing must be proven able to find something.** This project has already shipped a completeness scan that reported **zero hits** because `ast.parse` choked on a UTF-8 BOM and a bare `except Exception: continue` swallowed it, silently skipping every file.

**The control is free here, because four known-positive cases exist and three are still unfixed on `main`:**

| case | mode | state on `main` |
|---|---|---|
| **#461** `SelectButton` — `signal=` -> `textsignal=` | 2 | **OPEN** — must be found |
| **#460** eight widgets annotating `.signal` as `Signal \| None` | 5 | **OPEN** — must be found |
| **#383** gap 3 — `bs.TextField(bogus_xyz=1)` constructs silently | 1/3 | **OPEN** — must be found |
| **#458** `Select` — `signal=` -> `textsignal=` | 2 | **FIXED** — run the scan at `main~` and it must appear; at `main` it must not |

**The #458 arm is the strongest control available** — a real instance of the exact mode the tool exists to catch, with a known before and after. **Run it both ways.** Read files as `utf-8-sig` and let no bare `except` swallow a parse failure; count files parsed and assert it equals files found.

## Scope boundaries — write the command, not the conclusion

⚠ **`CLAUDE.md`: a completeness claim whose scope was never written down reads as global and is checked as local.** Two claims in this project's history went wrong exactly that way (*"no other `grab_set` in the package"* meant `dialogs/`; *"not yet filed"* meant this session, not the tracker).

State in the output, mechanically:

- **which directory** was scanned (`src/bootstack/widgets/*.py` is NOT all public wrappers — dialogs are under `src/bootstack/dialogs/`)
- **which classes** were skipped and why
- **which forwarding idioms** are understood, and therefore which wrappers the tool cannot speak about

## Out of scope, deliberately

- **Any fix.** Including obvious ones.
- **`_impl` widget defects.** The maintainer's framing is wrapper-vs-internal; an internal bug found on the way is filed, not chased.
- **The durable guard.** A one-time audit decays; a `test_public_surface.py`-style test at the *parameter* level is what prevents recurrence. **That is the more valuable half and it is a separate branch** — it needs the failure-mode taxonomy this pass produces in order to be designed to it. ⚠ Note the existing `tests/test_public_surface.py` has a known blind spot of exactly this kind (it gates the top-level name set but never asserts a submodule is unreachable as `bs.*`, which is why the `bs.events.X` drift went uncaught for two months). **Design the new guard to the modes, or it inherits the same shape.**

## Placement — ✅ DECIDED (maintainer, 2026-08-20)

**Issue [#463](https://github.com/israel-dryer/bootstack/issues/463), on its own UNNUMBERED milestone [`Wrapper and internal parity`](https://github.com/israel-dryer/bootstack/milestone/17).**

⚠ **It is unnumbered for a reason specific to this milestone, and the reason should survive: the findings will span compatibility categories.** Some fixes will RAISE where the framework currently accepts (`0.5.0`-shaped), some are pure bug fixes adding no surface (patch-line-shaped), and some will add public API (minor-shaped). **Until the table exists nobody knows the mix or the size**, so assigning a release would promise a scope that has not been measured. Findings get milestoned individually, by compatibility, once they are real.

⚠ **It was NOT folded into `0.5.0 — Strictness and value types`, and that is settled on `0.5.0`'s OWN terms.** That milestone's membership rule is explicit — *"a change belongs here if it RAISES where the framework currently accepts, or RETYPES what a public property returns"* — and the audit as a whole does not meet it. Only some of its future findings would. **Do not re-propose the merge.**

**Nothing was moved onto it, deliberately:**

- **#383 stays on `0.5.0`.** Its fix raises, so it meets that milestone's rule on its own terms — it is the closest relative of this work but it is correctly placed already.
- **#460 and #461 stay on `0.4.0`**, which they gate. Pulling them here would have changed what `0.4.0` ships.
- **#455 is the obvious candidate and was left alone.** It is unmilestoned, latent (zero callers in `src`, `tests` or `development`), and is literally mode 4 — `Field.enable()/disable()/readonly()` write the ttk readonly state without re-deriving. **Moving it is a scope call, so it is a proposal, not a decision.**
