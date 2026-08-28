# bootstack — Claude Handoff

## Project overview

bootstack is a batteries-included Python desktop UI framework. It is **not**
advertised as a Tkinter wrapper — the goal is to abstract Tkinter away entirely
so that Tkinter's warts, naming conventions, and legacy API are invisible to the
user. Widget names, arguments, methods, and events are designed for modern Python
and ease of use, not compatibility with the raw tk/ttk surface.

**Design philosophy:** Opinionated and configurable within a reasonable range.
Go from nothing to something fast. The user should never need to `import tkinter`.

**Working directory:** `D:\Development\bootstack` (Windows box) — see Environment.
**Branch strategy:** `feat/*` / `fix/*` branches off `main`. PRs go → `main`.

### Where things live — READ THIS BEFORE ADDING TO THIS FILE

This file keeps **only what is OPEN plus the standing rules.** Everything else
has a home:

| File | Holds |
|---|---|
| `docs/_dev/handoff-archive.md` | **Every shipped initiative** with its root causes, decisions and gotchas. Indexed by issue/PR number — **read the entry before you touch an area it covers**, don't re-derive it |
| `docs/_dev/docs-authoring-patterns.md` | Docs IA, the API Reference & Guide page recipes, autosummary templates, the widget documentation pattern, screenshot patterns |
| `docs/_dev/widget-review-and-docs-standards.md` | The widget review + docs checklist |
| `REVIEW-PROTOCOL.md` (repo root) | **The standing workflow for iterative development.** Read it before any implementation or review work |
| `PLAN.md` / `REVIEW.md` (repo root) | Live working files **for the branch in hand only** |

⚠ **THIS FILE HAS BEEN SPLIT TWICE — 2026-07-30 and 2026-08-20 — AND THE SECOND
SPLIT WAS FORCED.** It had reached **~60,000 tokens**, over budget, because every
release from `0.2.2` to `0.3.2` accreted here instead of being archived when it
shipped. **Archive an entry THE DAY ITS RELEASE SHIPS.** If you are adding more
than a few lines about work that is finished, you are writing in the wrong file.

⚠ **A handoff artifact only survives if it is IN THE REPO.** The first split sat
untracked and nearly vanished; #379's `leakfix.patch` was saved to a per-session
temp `scratchpad/` and is genuinely gone.

### The review protocol, in one paragraph

**A session that has written code never reviews code** — start a fresh session
before every review, because written artifacts transfer intent while session
memory transfers self-justification. **If you are implementing, write `PLAN.md`
UP FRONT, before you write code**; a plan reconstructed afterwards is a
justification, which is what the session boundary exists to keep out. **Close
each round with its `docs(review):` record** — writing the record is the last
step of a fix step, not an optional one. **Hand `REVIEW.md` to the next
reviewer**, or the round re-litigates settled decisions. **On merge, archive
`PLAN.md`/`REVIEW.md` into `development/` and create `PLAN.md` fresh** — finding a
stale one describing shipped work is worse than finding none.

**Stopping rules** (`REVIEW-PROTOCOL.md`, four mechanical gates — a rule needing
judgment gets reasoned around exactly when it should bind):

1. **A round is triggered by a non-empty `git diff <range> -- src/`, and nothing
   else.** Test-, probe- and docs-only commits are self-checked. ⚠ **Gate 1 has a
   known GAP: `.github/` is none of those three**, so a CI workflow reads as
   no-round. Unresolved — raise it rather than deciding silently.
2. **Test code is reviewed on ONE axis — what defect can it let through.** Only
   **vacuity** (passes while the behavior is broken) and **false alarm** (fails
   while it is fine) are actionable. Diagnostics, wording, symmetry and probe
   ergonomics are **notes in the record, never fixes**.
3. **The round cap goes in `PLAN.md` up front** — 2 for a patch, 3 for a minor —
   and survivors are filed as issues.
4. **Probes are instruments, not reviewed code.** A flake gets **one** fix attempt
   with a mechanism-reproducing control, then quarantine. Exception: a probe whose
   *conclusion* is cited as settled must be shown capable of finding something.

**And know when to stop.** `0.3.1` ran four rounds yielding 6/5/4/5 findings but
only 3/5/1/2 real ones — round 2 existed only because round 1's fix was
incomplete, and round 4 reviewed a **test-only** diff. **When a round returns
mostly re-reports and out-of-scope pre-existing bugs, the branch is done and the
rest are issues.** ⚠ **But a re-report is not automatically noise** — ask *what
changed: the evidence, or the cost of acting?* `0.3.1` round 3 re-raised a finding
whose evidence was unchanged but whose price had dropped to one argument, and it
was rightly taken.

---

## Environment — THREE MACHINES. Check which one you are on first.

**Windows box** (`D:\Development\bootstack`) — the primary. The checked-in
`.venv` is **STALE** (points at a `Python314\python.exe` that fails with *"Access
is denied"*). **Use `py -3.12` for BOTH tests and docs** — pytest is installed
**only** on 3.12 (9.0.3). ⚠ `py -3.13 tests/run_gui.py` fails every leg with *"No
module named pytest"* **while still printing a plausible-looking harness
summary**. `py -3.13` (3.13.7, Tk 8.6) is fine for running demo scripts, which is
all it is good for. `bootstack.__version__` reports a stale `0.1.0a9` from old
install metadata — harmless, ignore it.

**WSL box** (`/home/iddryer/bootstack`, Ubuntu 22.04.5) — **the ONLY box that can
run the Linux leg.** Set up 2026-08-14; an earlier session's environment had been
lost, so **verify before assuming**.

- **`python` does not exist and `python3` is 3.10.12, below the 3.12 floor.** Use
  **`/home/iddryer/.virtualenvs/bootstack/bin/python`** — 3.13.11, Tk 8.6.12,
  editable install, pytest 9.1.1. ⚠ Confirm provenance: it must print
  `/home/iddryer/bootstack/src/bootstack`.
- ⚠ **NO passwordless sudo, and `openbox` is NOT installed.** `xfwm4`, `xvfb-run`
  and `xprop` are. CI uses `openbox`; local arms use `xfwm4`.
- ⚠ **Run the Linux suite WITH a window manager**, or you reproduce #447 and think
  you found a product bug. Poll `_NET_SUPPORTING_WM_CHECK`; never `sleep`.
- ⚠ **`gh` is not installed for Linux — use the WINDOWS binary**,
  `"/mnt/c/Program Files/GitHub CLI/gh.exe"`. It cannot read WSL paths, so pass
  bodies via **`--body-file -`** on stdin, never a `/home/...` path.
- **git can push** (`credential.helper` → the Windows credential manager). ⚠ The
  repo is public, so **a successful fetch is not evidence that push works.**
- **Screen capture is not measurable under WSLg** — Weston places windows at
  coordinates no screen covers, so `test_capture` fails with `X get_image failed`.
  Run it under Xvfb.

**macOS box** (`/Users/israeldryer/PycharmProjects/bootstack`) — here **`.venv`
WORKS**: `.venv/bin/python` = Python 3.14.0, Tk 8.6, editable install, macOS
26.5.2. `python tests/run_gui.py` runs the full GUI suite in ~2 min with a real
display. `python3.13` exists system-wide but does **NOT** have bootstack installed.

⚠ **Still NO Tk 9 on any of the three boxes.** All are 8.6, so the Tk 9 scroll/DPI
contract is unexercised and **#376/#378 remain unverifiable.**

**Running tests:** `python tests/run_gui.py` (one root per process, #150).
**Docs:** clean-build always — incremental builds MASK warnings.
`rm -rf docs/_build && sphinx-build -b html docs docs/_build/html -W --keep-going`.

⚠ **`tests/widgets/*.py` NEVER RUNS.** `testpaths` is `tests/cli`,
`tests/widgets/public`, `tests/data`; **12 files / 25 tests** directly under
`tests/widgets/` are collected by nothing. All 25 pass run individually. Same
class: `tests/test_public_surface.py` (166 tests, green, never run by
`run_gui.py`). Both folded into #380 — **and CI now runs them**, which is where
the branch's `+166`/`+25` deltas come from.

⚠ **Never pipe a build/test command to `tail`** — you capture `tail`'s exit 0 and
miss real failures. **This bites in PowerShell too**: `pytest ... | Select-String`
leaves `$LASTEXITCODE` from the *pipeline*. Redirect to a file, capture
`$LASTEXITCODE` on the next statement, then grep the file.

---

## Current state

**Released: `0.3.2` on PyPI, tag `v0.3.2` (2026-08-13)** — *Read-only select
fields*, one fix (#453). Prior: `0.3.1` (2026-08-12), `0.3.0` (2026-08-11),
`0.2.3`, `0.2.2`, `0.2.1`, `0.2.0`. **Full detail for every one of these is in
`docs/_dev/handoff-archive.md`** — do not re-derive it here.

⚠ **`v0.3.2` and `main` DIFFER BY DESIGN**, as `v0.3.1` did: the CHANGELOG was
reworded *after* the tag and the GitHub Release body edited to match with
`gh release edit --notes-file`. **THE TAG WAS NOT MOVED** — never move a tag a
release has already run on.

### ★ START HERE (2026-08-28) — **#444 IS IN FLIGHT ON PR #485, CI GREEN, AWAITING MERGE. `0.4.0` HAS THREE ISSUES LEFT: #444, #460, #467.**

#### ⭐ #444 — IN FLIGHT. **PR #485 open against `main`, all 5 CI jobs green, NOT merged.** Branch `fix/modal-window-grab-444`, head **`85c77bde`**.

**A modal `bs.Window` took the grab and nothing ever handed it back.** `grep -rn "grab_release\|grab_current" src/bootstack/_runtime/toplevel.py` returned nothing, which is the whole defect in one command. Tk drops a grab when its holder is destroyed but does **not** restore the grab that holder displaced, so a modal opened from inside another modal left the outer one on screen, still blocking its caller, holding nothing — the user clicked straight past it into the main window. **Pre-existing, identical in `0.2.3` and `0.3.0`, NOT a regression from #440**, which fixed the same defect scoped to the dialog classes.

⚠ **The helpers were MOVED, not copied.** #440's `capture_grab`/`restore_grab`/`_log_grab_failure` now live in `_runtime/grab.py`; `dialogs/_impl/dialog.py` imports the two names, so `datedialog.py:19` and #440's eight test call sites keep resolving **through `dialog.py`** with no alias and no re-export. **The move was forced by direction** — `dialogs` imports `Toplevel` from `_runtime`, so `_runtime` reaching back would be a cycle. **Do not write a second pair.**

⚠ **Restore is bound on `<Destroy>`, not paired around `block_until_closed()`, and that was MEASURED before it was chosen.** A modal window does not have to block, so a blocking-only pairing leaves `show()`-then-`destroy()` unfixed. The risk was that Tk's own grab release might land after our handler; `development/probe_444_grab_restore_ordering.py` shows the restore wins the race, on **win32 and X11**. **Do not re-propose option A.**

⚠⚠ **ROUND 1's BLOCKING FINDING IS THE ONE TO CARRY: A GUARD ON ONE HALF OF A PAIR IS NOT A GUARD.** `show()` captured the token **unconditionally** while `_bind_grab_restore` guarded itself against re-entry. On a second `show()` the window already holds the grab, so it captured **itself** and discarded the opener's token — **#444's symptom reintroduced by #444's fix**, on three ordinary public spellings (`show()` twice; `show()` then `block_until_closed()`, which shows it again itself; `show()` then `show(anchor_to=…)`, which is what that parameter is *for*). Measured `restored 2 / lost 3` before, `5 / 0` after. **Both halves now share one gate, `_grab_restore_bound`.** ⚠ **The gate is the BIND flag, not "have we captured before"** — if the first `grab_set()` fails, nothing was bound and a later `show()` **should** capture again.

⚠⚠ **ROUND 2's DURABLE FINDING: THE TESTS DROVE A STAND-IN FOR THE SCENARIO THE CHANGELOG NAMES, AND NOBODY HAD CHECKED THE REAL ONE.** The entry headlines *"an 'Advanced…' button on a dialog"*; the tests use a raw `tkinter.Toplevel` as the opener. **Dialog and window take their grabs through different code paths** (`dialog.py:478` directly, `Toplevel.show()` through the new helpers) **and nothing exercised them against each other.** `development/probe_444_review_round2.py` drives the real pairing: `*** LOST ***` at `main`, `OK` after — with a no-nesting **control OK on both arms**, so a LOST row is the defect and not the instrument. **Three-deep nesting unwinds correctly at every depth; depth had never been measured.** The reverse direction (a dialog inside a modal window) is OK on both arms, which is correct — that is #440's path. **Re-run the probe rather than re-deriving any of it.**

**Two rounds under a cap of 2, each in a fresh session.** Round 1: five findings, all originating outside the author's risk list, one blocking; 1-4 fixed, 5 left under gate 2. Round 2: **nothing blocking**, three structural notes, no fixes. Plan and both records archived **in the branch, before the PR opened** — `development/plan-444-modal-window-grab.md` and `development/review-444-modal-window-grab.md`.

⚠ **CROSS-PLATFORM: Windows and Linux MEASURED, macOS NOT.** The no-platform-branch design (read the kind back from Tk rather than assuming) is measured on X11 with a **REAL global grab**, not the stub — an isolated Xvfb display makes that safe, which no live desktop does. Kind reads back faithfully and a displaced global grab survives the round trip as `global`. **macOS is the whole remaining gap** and folds into #452's trip; the arms and commands are in the archived review. ⚠ **`tk busy` is already a measured silent no-op on Aqua (#429), so the worry is concrete** — but only ONE of the two outcomes is this branch's problem, and the archived review says which.

⚠⚠ **`git mv` STAGES THE RENAME OF THE *INDEXED* BLOB, SO EDITS MADE BEFORE IT STAY UNSTAGED — AND THIS PROJECT RUNS THAT EXACT OPERATION ON EVERY BRANCH.** Archiving `PLAN.md`/`REVIEW.md` with `git mv` after editing them produced `RM` in `git status`, and a plain `git commit` then shipped the rename at **100% similarity** with a message describing a record the commit did not contain. Caught only by reading `git show --stat`. **`git add` the moved file after the `git mv`, and check the rename similarity is NOT 100% when you meant to change the content.**


**✅ #461 + #459 MERGED (PR #475, merge commit `c8ebfb7c`, 2026-08-26).** #461 (`SelectButton`'s `signal=` bound the option's LABEL, not its value) and #459 (`TimeField` emitted a change while seeding from a signal). Branch deleted local + remote, head **`e3593cd1`**. Plan and round 1 record archived at `development/plan-461-selectbutton-signal-value.md` and `development/review-461-selectbutton-signal-value.md`. Cap was 3, spent 1.

**✅ #476 MERGED (PR #478, merge commit `5cf398f8`, 2026-08-26).** Every `SelectButton` fired `on_change` **twice** per selection. Branch deleted local + remote, head **`5e72f9b4`**. Plan and round 1 record archived at `development/plan-476-selectbutton-double-change.md` and `development/review-476-selectbutton-double-change.md`. Cap was 2, spent 1 — round 1 found **no blockers in production code**, one should-fix in a test, and filed **#479**.

⚠ **#476 WAS FOUND BY ASKING A QUESTION, NOT BY A SWEEP, AND THE QUESTION IS REUSABLE:** *is this internal member reachable from public API at all?* `OptionMenu._textsignal` is not — #461 deleted the wrapper property that read it and #472 made `bs.SelectButton(textsignal=…)` raise — and chasing that turned up two live `<<Change>>` subscriptions where the code assumed one. **`_bind_change_event` returned its handle for the caller to store; `__init__` stored it, `_delegate_textsignal` discarded it, and the cancel-guard saw `None` both times.** Fixed by having it store the handle itself.

⚠ **DO NOT "FIX" IT AT THE DISCARDING CALL SITE.** `self._bind_id = self._bind_change_event()` at `optionmenu.py:368` works and leaves the identical trap for the next caller — there has already been one. **`_bind_change_event` stores its own handle now; a caller that discards the return is harmless.**

⚠⚠ **ROUND 1'S DURABLE FINDING: A TEST CAN GO RED ON THE BROKEN BUILD AND STILL NOT TEST WHAT IT IS NAMED FOR — because pytest stops at the first assertion.** `test_rebinding_the_textsignal_replaces_the_subscription` closed on `len(menu._textsignal._subscribers) == 1`, the count on the **NEW** signal, which reads **1 on both arms**. It failed pre-fix only on its *first* assertion, so **the control never reached the line the whole test exists for.** What `:368` leaked is the orphan on the **REPLACED** signal — **50 across 50 rebinds before the fix, 0 after** — and that is what it asserts now. **When a control goes red, check WHICH assertion produced it.**

⚠ **#479 CAME OUT OF ROUND 1. ON `0.5.0` (maintainer, 2026-08-26), UNFIXED:** `OptionMenu` never cancels its `<<Change>>` subscription on destroy, so a destroyed widget keeps emitting — `event_generate` on a dead window raises `TclError: bad window path name` **inside the Tk trace**, invisible to whoever wrote the signal, and the subscription **pins the destroyed widget in memory** (measured with a weakref after `gc.collect()`). **Pre-existing, and #476 halved it** (two leaked subscriptions per widget before, one after). **Not reachable from public API** — #472 rejects `textsignal=` at the wrapper and `SelectButton` hands out no property that reads the internal's. ⚠ **The fix has an exemplar in the repo: `ValueSignalMixin._bind_value_signal` (`field_mixin.py:305-310`) holds its id and releases it on destroy**, measured clean (`subs 1 -> 0`, widget collected). ⚠ **It is NOT #469** — that is a *queued* `when="tail"` event reaching a *different* widget; this is a *live subscription* firing new emissions at a dead one. Re-run `development/probe_476_review_round1.py` rather than re-deriving any of it; it prints which arm it is on by reading the source.

#### ⭐ #477 — COLLAPSE THE `_impl` LAYER BEFORE 1.0. **Maintainer's framing, filed 2026-08-26, unmilestoned.**

**The `_impl` widgets were the ORIGINAL implementation, written to stand alone; the public layer came later and wraps them.** Much of what `_impl` still carries — its own variables, signals and event plumbing — serves a standalone consumer that no longer exists, and the wrapper translates across a boundary that need not be there. **Before 1.0, collapse what no longer earns a separate existence**, because after 1.0 the surface freezes and every gap becomes permanent.

**Scoping, measured 2026-08-26 (STATIC import-name AST pass — needs a construction cross-check before acting):**

| | |
|---|---|
| classes defined under `_impl/` | **174** |
| imported by name somewhere in `src/` | 125 |
| **never imported by name anywhere** | **49** — its own question |
| imported in 2+ places (shared, cannot collapse) | 83 |
| **imported by exactly one public wrapper and nothing else** | **24** |

**All 24 are LEAVES** — the subclass check returns zero, so collapsing any one is local. Two tiers: **14 with a generic or no base** (`Frame`/`GridFrame`/`Label`/none) are cheap; **10 with a behavioral base** (`OptionMenu`→`MenuButton`, the three `Field` entries, `TimeEntry`→`SelectBox`, `Switch`→`CheckButton`, two raw ttk) mean the wrapper absorbs real inherited behavior.

⚠ **THE `_impl` SIGNAL MACHINERY IS NOT UNIFORMLY DEAD — A MECHANICAL SWEEP BREAKS THREE THINGS.** `localization_mixin.py:185-195` **replaces** `_textsignal` with a derived formatted signal (you can `map()` a Signal, not a `StringVar`); `Form.field_textsignal(key)` and `Field.textsignal` are live consumers; and eight-plus wrappers forward `textsignal=` legitimately, because for them the variable **is** the text so no space mismatch can arise. **`OptionMenu` is the counter-example, not the rule** — it inherited a text-variable mixin into a widget whose variable is a value KEY. That mismatch is #461; the leftover bridge is #476.

⚠ **INVISIBLE TO THE #463 AUDIT, AND THAT IS THE POINT.** All five of its modes take a **constructor keyword** as their unit, so machinery no keyword reaches is outside every one of them. #463 reported "nothing new" over exactly this ground.

#### ✅ #390 SHIPPED (PR #480, merge commit `e6f67961`, 2026-08-27) — **`0.4.0`'s biggest item is in.**

**A `Signal` can hold an empty value when it declares one: `bs.Signal(v, allow_empty=True)`, `Signal.clear()`, `Signal.allows_empty`, and `dtype=` for a signal that starts empty.** Branch deleted local + remote, head **`cfa29a75`**. Plan and all three review records archived at `development/plan-390-signal-empty.md` and `development/review-390-signal-empty.md`. **Cap was 3, spent 3** — round 1 reviewed a design that was replaced mid-branch, so only rounds 2 and 3 saw shipped code.

⚠ **THE BRANCH NAME WAS A LIE AND SO IS THE 2026-08-26 COMMENT ON #390 — both say `nullable=`.** The shipped spelling is **`allow_empty=`**, re-scoped 2026-08-27: the concept is *empty*, not *null*, because `clear()` already ships on nine field widgets meaning one verb with a type-dependent spelling. **Read the archived plan, not the issue comment.**

⚠⚠ **THE EMPTY IS DECIDED BY THE BINDING, NOT THE TYPE, AND THERE ARE THREE ANSWERS — NOT TWO.** `None` normally; `''` where the signal **is** the widget's own variable (a variable holds only strings); and **`set()` for a `set`-typed signal, realized or not**, because an empty set is a real member of the type. **The two-answer version was written into `signals.rst` AND the CHANGELOG and was wrong in both.** Round 3 caught the docs; the CHANGELOG copy survived to `a13b64f3` because the completeness claim was scoped to `signals.rst` without saying so. **Write the command, not the conclusion.**

⚠ **`bool`, `int` and `float` REFUSE at the binding — `issubclass`, never identity.** Their variables have no empty member, and the failure they would otherwise produce is invisible: no error at the write, then a `TclError` at an arbitrary later `.get()` inside a Tk trace. **The identity spelling shipped first and was wrong four times over** — an `IntEnum` is an `int` to `isinstance`, so it walked past the guard into an `IntVar` and reported `sig() == 0` while `allows_empty` said `True`. **`grep -n "_type is \|_type in (" src/bootstack/signals/signal.py` bounds it**; the one survivor is `from_variable`'s recovery chain, left on purpose.

⚠⚠ **ROUND 3'S DURABLE FINDING, AND IT IS ROUND 2'S ONE TURN OUT: A PARAMETRIZE OVER WIDGETS IS BREADTH ALONG ONE AXIS ONLY.** `test_the_value_space_fields_all_report_a_clear` covered all five value-space fields and **seeded every one with a value**, so the bind-time door went untested — and that is where the defect was. `_bind_value_signal` read a `None` from the signal as *"nothing to give"* and seeded the signal **from the widget**, destroying a declared empty at construction. **Invisible on four of the five, whose own default is `None`; `NumberField` defaults to `0` and reported it.** **When a feature has two doors into the same code — a seed and a later write — a test that uses only one is half a test.**

⚠ **A `map()` TRANSFORM NEEDS A GUARD ONLY WHEN ITS SOURCE ALLOWS EMPTY**, and it must return the empty of the type it derives, never `None` (`map()` does not propagate `allow_empty` — decision 4, unchanged). ⚠ **The branch first guarded the example whose source is an ORDINARY signal, where the guard is dead code, and wrote two paragraphs defending it** — reversed in `cfa29a75`. **Do not re-guard it.** The live example is in `signals.rst`'s emptiness section.

⚠ **THE PROMOTION TRAP IS DISCHARGED — AND THE LAST WORD ON IT WAS WRONG TWICE, SO READ THIS ONE.** The #458 and #461 CHANGELOG tails now say *"declare it `allow_empty=True` and the clear reaches it"*. **They are accurate and they STAY**: `allow_empty=True` ships in the same release, so they document the opt-in, not a removed limitation. The real trap was the earlier `nullable=` wording and it is swept — `grep -n nullable CHANGELOG.md` is empty. **Do not delete those sentences at promotion.**

**Filed out of it and OPEN: #481** (`Signal(None)` bare still builds a signal that can never hold a value — on `0.5.0`; ⚠ **its title still says `nullable=True`**, a parameter that never shipped), **#482** (a field's `value` lags a programmatic signal write until the next commit — pre-existing, reproduces with an ordinary signal), and **#484** (every framework-created signal is `allow_empty=False`, so `clear()` on one raises advice naming a constructor the caller never wrote — **six reachable widgets**; ⚠ **the original `Signal.from_variable()` framing was wrong and that route is NOT publicly reachable**, since `RadioGroup`/`ToggleGroup`/`Tabs` expose no public `.signal`).

⚠⚠ **#483 IS DOCUMENTATION, NOT A CODE FIX (maintainer, 2026-08-27), and the construction it names is CORRECT.** Measured in plain `tkinter`: the toolkit's checkbutton has **no tristate or indeterminate option at all**, and its indeterminate paint is a widget state fully orthogonal to the bound variable — settable while the variable reads `1`. **So the third state was never a variable concept to lose**, and bootstack already surfaces more than the toolkit does, because `checkbox.value` returns `None`. ⚠ **`bs.Checkbox(tristate=True, signal=bs.Signal(False))` shows unchecked, reports `False` and its signal reads `False` — all three agree. DO NOT RE-FILE IT.** The residue is the runtime `cb.value = None`, where the widget paints indeterminate and the signal still says `False`; only a Python-side rebinding of boolean controls closes that, which is #477's territory.

**Three things from #472 outlive it. Read the archived review before touching the seam, the docs scripts, or #466:**

- ⚠⚠ **A GUARD'S BLAST RADIUS WAS MEASURED OVER `src/` AND `tests/` AND NEVER OVER `docs/` — and `docs/` is where it bit.** Two shipped scripts passed keywords that had never existed (`bs.DataTable(enable_search=…)`, the INTERNAL key for `searchable`; `bs.DataTable(paginated=…)`, nothing at all) and the guard turned both from silent no-ops into hard `TypeError`s. **Nothing caught them: the suite does not run `docs/examples/`, Sphinx `literalinclude` does not execute what it includes, and CI runs neither.** ⏭ **THE DURABLE FIX BELONGS ON #466 AND IS NOT BUILT: an AST check that every `bs.<Widget>(kw=…)` in `docs/**/*.py` names a real parameter or a layout key.** It would have caught both before the branch existed.
- ⚠ **A VACUOUS TEST INSIDE A SUITE THAT COVERS THE BEHAVIOR ELSEWHERE IS A DIFFERENT FINDING FROM A COVERAGE HOLE — and the review got this wrong first.** `test_declared_forwarders_still_forward[Chart]` passes without testing anything wherever `matplotlib` is absent (every CI leg — `ci.yml` installs `-e .` only), because `bs.Chart(bogus=1)` raises *"requires matplotlib"* before `__init__` reaches the split. The record first concluded the exemption was therefore unguarded on CI. **It is not** — `test_declared_forwarders_are_exactly_the_five` never constructs a widget and catches it regardless. **Review the test's siblings before pricing its vacuity.**
- ⚠ **`probe_wrapper_parameter_delta.py --arm leftovers` IS THE WRONG INSTRUMENT FOR THIS AREA NOW, and would report a working fix as a tool bug** — it compares the STATIC source verdict against construction, so a wrapper that rejects while still *looking* like a dropper reads as a DISAGREE under a banner saying a disagreement is a probe defect. **Use `development/probe_383_unknown_kwarg_policy.py`**, which classifies by construction only.

⚠ **#472 IS NEW AND IS NOT #383.** Gap 3 (unknown keyword **names**) was split out of #383 on 2026-08-25 and **moved to `0.4.0`**; **#383 keeps gaps 1 and 2 (bad *values*) and stays on `0.5.0`** with #369/#408/#416. **The batching rule did not argue for holding it**, and the measurement that overturned it is on #472: the rule minimizes the number of releases that force a migration, and `0.4.0` already forces one (#465's rule-type guard raises; #461 breaks working code), so it is two either way. **Do not re-propose deferring it.**

**#465 merged 2026-08-25 (PR #471), preceded by #449's harness fix (PR #470).** Their plan and review are archived at `development/plan-465-select-validation-surface.md` and `development/review-465-select-validation-surface.md`.

**Three things from #465 outlive the branch. Read the archived review before touching the field family or the harness:**

- **`Select` declares `_VALIDATION_KIND = None`, deliberately.** A `Select`'s value kind belongs to its **options**, not to the widget: `SelectBox._validation_value` decodes the label back to the option's value, so a `range` rule over numeric or `date` option values **works** and must keep working. ⚠ Declaring the mixin's `'text'` default there rejects it at attach time and **breaks running apps at construction** — that was round 1's blocking finding, and the plan's contrary measurement was taken on a `Select` whose text equals its value, which cannot reach the decode.
- ⚠ **A `when="tail"` event can OUTLIVE its widget and be delivered to a DIFFERENT one.** Proven by payload match, not inference. Filed as **#469**, unfixed in the product; `tests/conftest.py::_reset_scene` now pumps `root.update()` before destroying, which is what closed #449. **See the Tk traps section.**
- ⚠ **A RATE IS NOT EVIDENCE for a timing-dependent flake, because non-fixes silence it too.** Instrumenting the #449 leg made it pass; so did `update_idletasks()`, which does not drain the queue at all. **Assert the invariant.** Full account in the archived review's addendum.

#### ✅ #472 — mode 3 is FIXED and reviewed (PR #473). Kept only for what outlives it.

**Shipped exactly as decided: default-strict at the seam, declarative class-flag opt-out.** `_split_layout_kwargs` is an instance method that raises on whatever survives the split, naming the widget and every leftover key; the five deliberate forwarders (Chart, MenuButton, Picture, StatusBar, Toolbar) opt out with `_forwards_kwargs = True`. **Measured by construction, not read from source: `dropped=40 rejected=10` before, `dropped=0 rejected=50` after**, with the probe's control run at the base commit so the zero is a measurement. **The whole analysis is in the archived plan and review — do not re-derive it.**

- ⚠ **`App` and `Window` ARE NOT a third shape, which was the easy misread.** They forward their catch-all deliberately (`app.py:172`, `window.py:179`) and never call `_split_layout_kwargs`, because a top-level window is never placed in a layout — **so the seam guard does not touch them, and it did not.** They still reject, through the toolkit: `bs.App(bogus=1)` raises `TypeError` naming **`Tk.__init__`**, `bs.Window(bogus=1)` raises `TclError`. **That message shape is #383's OTHER gap (raw toolkit errors), still open on `0.5.0`.**
- ⚠ **The four crafted `textsignal` messages were the trap, and they are the thing most likely to be re-broken by a later "simplification".** `Select`, `DateField`, `NumberField` and `TimeField` ran the split **before** their bespoke `raise`, so a strict split would have fired the generic error first and silently retired all four — including #458's public explanation of a deliberate behaviour change. **Each check now sits ABOVE its split and each is pinned by a test asserting the specific text.** `grep -n "in kwargs" src/bootstack/widgets/*.py` returns exactly those four in constructor scope; **there is no fifth.**
- **The duplicated guards in `boolean_controls.py` and `radio_variants.py` are now DEAD CODE** — the seam raises first. Left in place deliberately (round 1 nit, no action); **do not read them as the live guard.**


**⏭ THE MEASUREMENT PASS IS DONE AND FILED NOTHING NEW.** Every real finding lands on an issue that already existed. **The pass's product is the MEASUREMENT those issues were missing** — read `development/wrapper-parameter-audit-463.md` before touching any of them, and do not re-derive it. The instrument is `development/probe_wrapper_parameter_delta.py` (arms `scan`, `control`, `leftovers`, `roundtrip`); **re-run it rather than reading the wrappers again.**

| mode | what | measured | verdict |
|---|---|---|---|
| 1 | never forwarded | **0** | clean |
| 2 | wrong destination | 100 renamed destinations | **1 defect — #461.** The other 99 are `_impl` spelling |
| 3 | swallowed as a layout key | **40 of 52 wrappers** | **THE finding.** Was #383 gap 3, split out as **#472** and ✅ **FIXED (PR #473)**. ⚠ **This row is now HISTORICAL — so is `--arm leftovers`, which reports the fix as a tool bug** |
| 4 | accepted then ignored | not statically decidable | 1 weak candidate (`Carousel.index`) |
| 5 | the type lies | **8** | **= #460's population exactly**, `TextArea` cleared |

⚠⚠ **THE FIVE MODES ALL TAKE A CONSTRUCTOR KEYWORD AS THEIR UNIT, SO A MISSING METHOD OR PROPERTY IS INVISIBLE TO EVERY ONE OF THEM — "FILED NOTHING NEW" IS BOUNDED BY THAT, AND IT IS NOT A CLEAN BILL OF HEALTH.** #465 is the proof: `Select` forwards every parameter it declares — **clean under all five modes** — while hiding six public members its internal has fully wired. It was filed by an external user three days after this pass reported nothing new. **There is a MODE 6, capability gap: what can the internal do that the wrapper gives no way to reach?**

⚠ **A one-hop scan exists — `development/probe_wrapper_capability_gap.py` (arms `scan`, `control`) — and its OWN CONTROL PROVES IT CANNOT SEE #465.** The capability sits two hops down (`_internal._entry._valid_signal`) behind underscore names, while the scan diffs one hop over public names. It finds the neighbourhood (`on_valid`/`on_invalid` show up on `Select`) and misses the members the user asked for. `--arm control` asserts that miss on purpose, so a quiet row cannot be read as coverage.

⚠ **AND ITS SILENCE MEANS NOTHING, WHICH IS THE POINT.** It reports **1267 one-hop candidate rows (75 "strong")**, and a further **1815 two-hop members across 155 sub-widget objects are enumerated but UNEXAMINED** — **zero classified**, with three hops and beyond not enumerated at all. **75 strong is a sample from an unbounded region, not a population**, and the ~29 wrappers it names are not evidence that the other 28 are clean. **Do not quote the 75 as findings.**

⚠ **WHAT WOULD MAKE SILENCE MEANINGFUL IS A CENSUS WITH A VERDICT ON EVERY ROW, NOT A BIGGER FINDER** — the design #466 already chose for mode 2: pin every row to a committed snapshot with a reason column and assert the snapshot MATCHES, so a new row fails once at the commit that introduces it. **#466 needs amending on this: a parameter-level snapshot cannot see members.**

⚠ **BUT A CENSUS IS NOT WHAT DECIDES A SINGLE WIDGET, AND REACHING FOR ONE IS THE TRAP THIS ALREADY FELL INTO.** `docs/_dev/widget-review-and-docs-standards.md` Part 1 step 1 **already** covers this — *"Unexposed capability / API gaps — internal features the public layer never surfaces, or surfaces inconsistently"* — as a **per-widget human read**. Parameters mechanize; capabilities do not, because the wrapper deliberately **renames, reshapes and hides** (the internal's `on_valid`/`off_valid`/`on_validated` callback pair becomes `valid`/`error` Signals **plus** `on_valid`/`on_invalid`, with `on_validated` dropped — none of it derivable from the internal's surface). ⚠ **"The internal has it" IS NOT THE STANDARD; applying it mechanically would re-Tkinterize the public layer.** **Walk one widget at a time against the existing checklist.** The field family is where the defects concentrate — #453, #455, #458, #460, #461, #465, #415 and #416 are all field-family.

- ⚠ **MODE 2 CAME OUT ESSENTIALLY CLEAN, AND THAT IS A NEGATIVE RESULT WORTH SOMETHING ONLY BECAUSE THE CONTROLS PASS** — the same scan finds #461 on `main` and finds #458 at the pre-fix commit. **The wrapper layer's forwarding is in better shape than the recent defect run suggested; the exposure is strictness (mode 3), not mis-wiring.**
- **What got 100 mode-2 rows down to 1 was DIVERGENCE**, not the rename itself: a public name that lands on a *different* internal key in some other wrapper. `max_value -> maxvalue` is ordinary; `signal -> textsignal` when nine siblings say `signal` is #461. **Reuse that ranking, don't re-invent one.**
- ⚠ **#383 GAP 3 IS NO LONGER BLOCKED.** Its open question was *"the shared split seam needs the wrappers that legitimately forward `**kwargs` counted first."* Counted: **40 drop, 5 reject, 5 forward, 2 never split.** And **the fix already ships** — `_BooleanControlBase.__init__` has the six-line guard covering five public widgets. Gap 3 needs no design, only placement.
- ⚠ **`Select`, `DateField`, `NumberField` and `TimeField` LOOK strict and are NOT.** They carry an `if "textsignal" in kwargs: raise` guard, which rejects **one known name** and says nothing about the rest. **A specific-key guard is not a leftover guard** — the audit's own static pass credited all four with rejecting until construction disproved it.
- ⚠ **NOT COVERED, AND NOT CLEAN: 84 params across `AppShell` (31), `Workbench` (34), `ThemeToggle`, `Notification`, `Snackbar`.** They build no internal in their own `__init__`. `App`, `Window` and `Splash` were in that list until the probe learned the alias hop.
- ⚠ **THE SURFACE FIGURE MOVED AND BOTH NUMBERS ARE RIGHT.** The audit plan (`development/plan-463-wrapper-audit.md`) says **77 classes / 890 params / 62 catch-alls**; the scan reports **65 / 810 / 52**. The plan counted every class in the wrapper modules; the scan counts only what a public `__all__` exports, skipping 17. **Different populations, not a discrepancy** — say which you mean.

**⏭ THE PASS IS OVER; WHAT IS LEFT IS FOUR MAINTAINER DECISIONS, none of which a session should make alone:**

1. ✅ **Mode 3: shared seam or per-wrapper? — DECIDED (maintainer, 2026-08-21): DEFAULT-STRICT AT THE SEAM, with a DECLARATIVE class-flag opt-out** for the five wrappers that forward leftovers on purpose (Chart, MenuButton, Picture, StatusBar, Toolbar). **`PLAN.md` §1 carries the shape, the code sketch and the reason.** ⚠ **The reason is not the edit count** — under opt-in the next wrapper anyone writes silently joins the 40; under default-strict a new wrapper is strict for free. **Do not re-propose per-wrapper opt-in.** Lands on **#383 / `0.5.0`** — the fix raises, which is that milestone's rule.
2. ✅ **#460's fix vs its milestone — DECIDED (maintainer, 2026-08-21): it STAYS ON `0.4.0`.** Dropping `| None` from eight annotations does retype what a public property returns, which is `0.5.0`'s membership rule verbatim — **but the released line is `0.3.2`, and deferring a typing fix two minors to honor a rule about batching migrations costs more than it saves.** `0.4.0` is a minor already (forced by #461), so the retype rides a minor either way. **Ship it with the other fixes. Do not re-propose the move.**
3. ✅ **#463's disposition — DECIDED (maintainer, 2026-08-21): CLOSED as completed**, with the table as its artifact. The durable guard was filed FRESH as **#466** rather than re-scoping #463, because #463's title, body, controls table and explicit *"ships no production code"* boundary all describe a finished measurement pass. **Do not re-open #463 to hold guard work.**
4. ✅ **The `_impl` naming inconsistency — DECIDED (maintainer, 2026-08-21): NOT AN ISSUE, it is internal.** (`readonly`/`read_only`, `maxvalue`/`maximum`, `items`/`options`/`values`, `override_redirect`/`overrideredirect`.) **Verified reachable-from-public before closing it, not assumed:** `Form`'s `editor_options` builds the PUBLIC wrapper and the bag carries that widget's public options (`_impl/composites/form.py:650`); `readonly` at `textfield.py:127` is the ttk STATE string, not a bootstack parameter; `MenuButton.menu_options`, `ButtonGroup.add`, `RadioGroup.add` and `Toolbar.add_widget` all route through `merge_kwargs` against public options. ⚠ **The one real leak path is `Picture` and `Chart`**, which do `internal_kwargs.update(kwargs)` (`picture.py:96`, `chart.py:158`) — so THEIR internals' vocabulary is reachable public surface. **None of the four names appear on those two internals** (grepped), so it does not touch this decision — but it is why `PLAN.md` §4 asks whether the five forwarders deserve a better error instead of an opt-out. **That is a #383 question, not a naming one.**

**The durable guard is the half that does not decay. It is now FILED AS #466 and still NOT BUILT.** A parameter-level `test_public_surface.py`-shaped test written **to the five modes**. ⚠ **Read #466 rather than re-deriving its shape** — it carries three things this file will not repeat: that it must not inherit the existing file's blind spot (that one gates the top-level *name set* and never asserts a submodule is unreachable as `bs.*`, which is how the `bs.events.X` drift survived two months); that the **84 unanalysed params are a hole, not coverage**; and the mode-2 design below.

⚠ **#466 AS FILED IS PARAMETER-LEVEL AND THEREFORE CANNOT SEE A MISSING METHOD OR PROPERTY — IT NEEDS AMENDING, and #465 is the proof it would have missed.** See the mode-6 block above for the measurement (1267 one-hop rows, 1815 two-hop members unexamined, zero classified) and for why the answer is a **census with a verdict per row**, not another finder. ⚠ **And do not let that census block a single-widget fix** — capabilities are a per-widget read against `docs/_dev/widget-review-and-docs-standards.md`, not a mechanizable diff.

⚠ **MODE 2 IS NOT A PLAIN ASSERTION AND MUST NOT BE BUILT AS ONE.** It is the only undecidable mode — #463's run flagged **100 rows to find 1 defect**, and **three of that pass's five tool defects were FALSE ALARMS pointing at working code**. A hard-failing mode 2 is a false-alarm generator, which is an actionable defect under gate 2. #466's shape: pin every wrapper-param-to-internal-key crossing to a **committed snapshot** with a per-row classification and a **reason column**, and assert the snapshot MATCHES. A new crossing fails once, at the commit that introduces it; existing rows never re-litigate. It answers *"did the forwarding change unnoticed?"* instead of *"is this forwarding correct?"* — **and #458 and #461 would both have failed such a snapshot.**

⚠ **THE PASS SHIPPED NO PRODUCTION CODE, as planned.** `git diff main...HEAD -- src/` was empty for its whole life. **Fixes are scoped separately, by the maintainer.**

⚠ **FIVE TOOL DEFECTS WERE FOUND WHILE RUNNING IT, AND FOUR WERE CAUGHT BY RUNNING SOMETHING RATHER THAN READING IT** — three of those were **false alarms pointing at working code** (`TimeField(read_only=True)` was reported as writing a key nothing accepts; it works). **A static wrapper audit that is not cross-checked against construction ships false findings.** That is why the probe has an arm that constructs all 52 wrappers and compares the outcome to the static verdict (51 agree, 0 disagree). **Keep that habit for the guard.**

⚠ **AND THE `main~` TRAP, WHICH COST THE FIRST CONTROL RUN A FALSE FAILURE:** the #458 before/after arm was pointed at `main~`, which is **two `docs(claude):` commits AFTER the merge** — the defect was long gone. **The commit that bounds a control has to be the one the defect actually lived in**, here `1f9a62d1^`, the fix's parent. It is pinned with a comment saying why.

✅ **PLACEMENT DECIDED (maintainer, 2026-08-20): [#463](https://github.com/israel-dryer/bootstack/issues/463) on its own UNNUMBERED milestone `Wrapper and internal parity`.**

⚠ **The reason it is unnumbered is specific and should survive: the findings will span compatibility categories.** Some fixes will RAISE where the framework accepts today (`0.5.0`-shaped), some add no surface (patch-line-shaped), some add public API (minor-shaped). **Until the table exists nobody knows the mix or the size**, so a release number would promise unmeasured scope. Findings get milestoned individually, by compatibility, once they are real.

⚠ **NOT folded into `0.5.0 — Strictness and value types`, and that is settled on `0.5.0`'s OWN terms** — its membership rule is *"a change belongs here if it RAISES where the framework currently accepts, or RETYPES what a public property returns"*, and the audit as a whole does not meet it. **Do not re-propose the merge.**

**Nothing was moved onto it.** #383 stays on `0.5.0` (its fix raises, so it meets that rule already); #460 and #461 stay on `0.4.0`, which they gate. ⏭ **#455 is the obvious candidate and was deliberately left alone** — unmilestoned, latent, and literally mode 4 (`Field.enable()/disable()/readonly()` write the ttk readonly state without re-deriving). **Moving it is a scope call, so it is a proposal, not a decision.**

#### STATE OF THE WORLD

| | |
|---|---|
| `main` | tip is this `docs(claude):` commit, whose parent chain runs through the **PR #480 merge (`e6f67961`, #390, 2026-08-27)**, the **PR #478 merge (`5cf398f8`, #476)**, the **PR #475 merge (`c8ebfb7c`, #461+#459)**, the **PR #473 merge (`935cf2c1`, #472)** and the **PR #471 merge (`62728770`, #465)**. ⚠ **A row cannot name its own SHA — verify with `git rev-parse origin/main` rather than trusting any SHA written here** |
| branches | **ONE — `fix/modal-window-grab-444`, local and remote, head `85c77bde`, PR #485 OPEN and CI green. Verified with `git branch -a` 2026-08-28.** Deleted on merge: `fix/signal-nullable-390` (head **`cfa29a75`**), `fix/selectbutton-double-change-476` (**`5e72f9b4`**), `fix/unknown-kwarg-strictness-383` (**`bb8ef8ff`**), `fix/selectbutton-signal-value-461` (**`e3593cd1`**), `fix/select-validation-surface-465` (**`ff718b4d`**), `fix/scene-reset-event-queue-449` (**`ed174211`**), `audit/wrapper-parameter-delta` (**`41828ba2`**), `fix/select-signal-value-458` (**`51d09f6e`**). ⚠ **NON-ANCESTOR ≠ UNMERGED** — check recorded head SHAs against `origin/main`, not branch names |
| root of `main` | **NO `PLAN.md` and NO `REVIEW.md` — CORRECT, not a gap.** #390's are at `development/plan-390-signal-empty.md` and `development/review-390-signal-empty.md`. ✅ **#444 BROKE THE STREAK: PR #485 archived both into `development/` IN THE BRANCH, BEFORE the PR was opened**, so nothing lands in `main`'s root at merge. ⚠⚠ **The two branches before it — PR #478 and PR #480 — both merged them into `main`'s ROOT and archived AFTER, each caught only because the next session looked. Archive before you open the PR** |
| released | `0.3.2`. **`## [Unreleased]` carries #444, #456, #458, #459, #461, #465, #472 and #476**, under **`### Added`** and **`### Changed`** as well as `### Fixed`, and is what `0.4.0` will promote. ⚠ #444's bullet is on the BRANCH, not on `main` — it arrives with the PR #485 merge. ⚠ The `Changed` section is #472 **and #461**: both RAISE where the framework used to accept, so an app can fail to start after the upgrade |
| next release | **`0.4.0 — Signal binding on fields`** — #458, #459, #461, #465, #472, #476 and **#390** done; **#444 fixed and awaiting the PR #485 merge; #460 and #467 open.** ⚠ **#444 ARRIVED 2026-08-27 from the patch line** by maintainer decision, in the same pass that closed `0.3.x — Patch line` and cut `0.4.x`. **Verified 2026-08-28 with `gh issue list --milestone <title> --state all`: 10 issues, 7 CLOSED, 3 OPEN (#444 #460 #467).** That command is the authority for *issues*; the milestone API endpoint counts PRs too, and reads `open=4` because PR #485 carries the milestone |
| CI | `ci.yml` green on `main`, 5 jobs. **No macOS leg** (#452) |
| suite, `main` | **1628 passed / 22 skipped, 33 legs, exit 0** — measured 2026-08-27 on `main` after the PR #480 merge, Windows box, `py -3.12`, **`matplotlib` and `pandas` BOTH PRESENT.** Reconciles as `1579 + 49` (#390's one new test file), bounded with `git diff e8caece4..HEAD --stat -- tests/`. ⚠ **#444's branch measures `1638 / 22`** — `1628 + 10`, its one new test file — so expect that figure after the PR #485 merge |
| open milestones | **11** — verified against `gh` 2026-08-28. ⚠⚠ **THE COUNT IS UNCHANGED BUT THE COMPOSITION IS NOT: `0.3.x — Patch line` is CLOSED and `0.4.x — Patch line` was cut in its place** (2026-08-27), which is the rolling line's own rule — a line that turns over gets a NEW milestone, never a rename. **Do not read the unchanged 11 as an unchanged list** |

⚠ **A HANDOFF COMMIT THAT IS NOT PUSHED DOES NOT EXIST.** Found 2026-08-26: the two `docs(claude):` commits describing #461's flight had **never left the local box**, so `main` and `origin/main` had silently diverged and `git pull --ff-only` refused. They rebased cleanly (CLAUDE.md-only, and #475's branch had an empty CLAUDE.md diff), but **the next session would have read a `main` that knew nothing about the branch in hand.** ⏭ **`git push` after every `docs(claude):` commit, and check `git rev-parse main origin/main` agree before trusting this file.**

#### ✅ #458 — MERGED (PR #462, merge commit `41c8bad1`). Kept for its traps.

`Select` mapped its public `signal=` onto the internal **`textsignal=`**, installing the `Signal`'s Tk variable as the entry's textvariable — so writes landed in the display text, bypassing the value-to-label map and the commit path. **One wiring line, two symptoms**, and the reported one was the milder: decoupled options displayed the raw value (reported), while a signal write moved the display but **not** the selection, leaving `.value`/`.selection` stale with **no `<<Change>>`** — on plain `list[str]` options too, and it did not self-heal. Fixed by binding through `ValueSignalMixin`.

⚠ **`signal=` IS NOW VALUE-SPACE — a deliberate, maintainer-approved behavior change.** Both directions moved: `sel.value = '2'` used to write the label `'Two'` into the signal and now writes `'2'`. **Do not re-litigate it.**

⚠ **`.signal` MEANS TWO DIFFERENT THINGS ACROSS THE PUBLIC API, and #458 widened the split rather than causing it.** Text-space: `TextField`, `PasswordField`, `PathField`, `SpinnerField`, `TextArea`, `CodeEditor`, **`SelectButton`**. Value-space: `NumberField`, `DateField`, `TimeField`, `Select`. **That is the real content of #460 and #461 taken together, and it is a family decision nobody has made.** ⚠ The CHANGELOG was corrected pre-merge for claiming the fix *"matches the other fields that take a `signal=`"* — **it does not match `SelectButton`**, which is the nearest sibling and still binds the label. **A closed list cannot over-claim the way an open one did.**

⚠ **THE MINOR WAS FORCED BY #461, NOT BY THE ADDITION.** #458 adds public surface (`Select` gains a `signal` property), and the standing rule says an addition needs a minor — but **#461 BREAKS WORKING CODE**, which is the stronger reason: seeding a `SelectButton` signal with an option's **label** works today and is the only spelling that does. That is #381's shape. **Do not re-read this as "#458 was only an addition".**

⚠ **ONE RESIDUAL, STILL UNDECIDED:** the #458 CHANGELOG bullet does not mention that `Select` gained a public `signal` property. **Announcing it is a maintainer call, not a defect.**

**Two review records, archived to `development/plan-458-select-signal.md` and `development/review-458-select-signal.md`** — round 1 (four findings, none in production code) plus an **off-protocol verification pass** that should not have opened (it reviewed a test-only commit, which gate 1 exists to keep out) and whose two re-reports cost a round of attention because **the reviewer was not handed `REVIEW.md`**. Cap was 2, spent 1.

⚠ **ITS ONE REAL FINDING IS THE ONE TO CARRY: a test can drive the right path and still assert nothing that can fail.** Round 1's own fix added a signal write to the read-only test but no assertion sensitive to the entry state — `read_only` reads the stored **setting** (#453 decoupled it from the entry on purpose) and the shown text is correct either way, so **both assertions passed while the field was silently editable**. Closed by asserting `entry_widget.instate(["readonly"])`, with a control that breaks the applier and watches the three older assertions still clear.

#### Two OPEN issues from that work — filed, not fixed

- **#461 — `SelectButton` has #458's defect, unfixed.** Identical `signal -> textsignal` wiring at `selectbutton.py:85`. Seeding with the **label** works; seeding with the **value** — what `value=` takes and what the docstring promises — gives `text='2' value='2' selection=None`, and `sel.value = "3"` writes the *label* back. ⚠ **Narrower than #458**: plain `list[str]` options are unaffected and `<<Change>>` does fire. **On `0.4.0`, and it is why that milestone is a MINOR.**
- **#460 — eight widgets annotate `.signal` as `Signal | None` and can never return `None`.** The wrappers forward with `getattr(self._internal, 'signal', None)` but the internal **lazily creates on first access**, so the default is dead code and the `| None` is **unreachable, not merely unobserved**. ⚠ **Do not "fix" `TextArea`, `CodeEditor`, or the `ValueSignalMixin` trio** — they genuinely return `None`. `Slider` is the honest exemplar.

#### ✅ #465 — the EXTERNAL report. MERGED 2026-08-25 (PR #471), on `0.4.0`. Kept for its traps.

**`Select` accepts `add_validation_rule()` but has NO `.error` or `.valid`.** Filed 2026-08-20 by `bLynnb2762` against `0.3.2`, labeled `bug` — **the only open issue that is not this project's own backlog**, and it sat unread while the audit merged the same day.

**Cause, measured 2026-08-21 — do not re-derive it:** `Select` **did not** inherit `FieldAddonMixin`. It hand-copied `add_validation_rule` and `validate` from that mixin, plus `_flex_vertical_default` for #394 — **but not `valid`/`error`**, which the other seven field widgets inherit. **Fixed by inheriting it**; the MRO is now `Select -> ValueSignalMixin -> FieldAddonMixin -> PublicWidgetBase`, and `_flex_vertical_default` comes from the mixin rather than a local copy.

⚠⚠ **AN EARLIER VERSION OF THIS ENTRY SAID "`Select` OPTS OUT DELIBERATELY — DO NOT MAKE IT INHERIT THE MIXIN." THAT WAS WRONG AND IT IS THE OPPOSITE OF THE FIX.** It was an inference nobody had checked, and it was repeated as fact three times before anyone looked. **Inheriting the mixin IS the fix.** What the evidence actually says, measured 2026-08-21:

- **No reason is recorded anywhere.** The comment at `select.py:88` explains `_flex_vertical_default` and merely *states* the non-inheritance in passing. It justifies nothing.
- **The class declaration traces to `a41b539e`, the flat-surface migration** — a refactor, not a decision. #357 (`884b8027`, 2026-07-20) then hand-restored `add_validation_rule` **alone**, a month after the mixin already carried `valid`/`error` and the kind gate. **Incomplete at birth, not drifted.**
- **The family is uniform 7/7 without it** — every other field widget exposes `valid`, `error`, `insert_addon`, `update_addon`, `remove_addon`, `addons`. A real opt-out would show variation somewhere; one widget missing the whole block is the signature of a lost mixin.
- ⚠ **The "addons don't suit a dropdown" theory is DISPROVED BY CONSTRUCTION** — `Select` **already uses addons**: its internal reports `addons=['dropdown', 'probe']` after a test insert, so **the dropdown arrow IS an addon.** Load-bearing, not merely compatible.

⚠ **THERE WAS A SECOND, INDEPENDENT CAUSE, and the mixin does not fix it — remember this shape, it recurs.** `on_valid`/`on_invalid` come from the **event map**, not the mixin: `_SELECT_EVENTS` carried only `change` while `ValidationMixin` on the entry part had been emitting `<<Valid>>`/`<<Invalid>>` all along **with nothing listening.** Fixed by adding `valid`/`invalid`/`validate` to `_SELECT_EVENTS`. ⚠ **A missing public event name looks exactly like a widget that does not emit** — check the map before concluding the emit is absent.

⚠⚠ **THE KIND GATE DID *NOT* SHIP, AND THE PARAGRAPH THAT USED TO STAND HERE ARGUING THAT IT SHOULD WAS WRONG. `Select` DECLARES `_VALIDATION_KIND = None` AND GATES NOTHING.** The old text said a `range` rule on a `Select` "can never pass today", so rejecting it broke nobody. **That measurement was taken on a `Select` whose option text EQUALS its value**, which cannot reach `SelectBox._validation_value`'s label-to-value decode and can therefore only ever hand a rule a `str`. Give the options distinct labels and the rule receives the option's **real Python object**, so `range` over `int` or `date` option values **works on the released line** — measured on both arms in `development/probe_465_select_range_kind.py`. Shipping the gate would have raised `BootstackError` **at construction** in running apps. ⚠ **A `Select`'s value kind belongs to its OPTIONS, not to the widget**, which is why `None` is the honest answer and why `field_mixin.py` skips the gate on `None`. **Do not re-propose attach-time rejection** — and note the reporter never asked for `range` at all.

**`development/plan-465-select-validation-surface.md` and `development/review-465-select-validation-surface.md` carry the whole analysis, both review rounds, the test list and the boundary of each claim. Read them rather than re-deriving.** ⚠ **The plan's "the gate ships too" section is SUPERSEDED by round 1** — `Select` gates nothing now.

⚠ **The fix ADDS PUBLIC SURFACE, so it needs a MINOR**, which is why it landed on `0.4.0` rather than the patch line: that milestone is a minor already (forced by #461), and this file's own rule is **to ask what else is ready when a minor is being cut anyway rather than parking a fix out of habit.** The milestone was **asked for and given**, not assigned unasked.

#### ⏭ BRIEF FOR THE macOS BOX — #452, the runner hang

**The job:** CI covers ubuntu and windows and **not macOS**, because the leg ran **90 minutes for a 90-second suite** and was removed rather than left hanging. aqua is a platform this project publishes for and is now the only one with zero automated coverage, so the value of #380 is capped until this closes.

**Known already, so it is not re-derived:** setup and the Tk-version report both **succeeded**, then "Run the suite" never returned — so it is not a provisioning failure. **Every job now sets `timeout-minutes`**, so a retry costs 15 minutes. ⚠ That guard has since proven itself twice: PR #462's ubuntu-3.12 leg hung inside `sudo apt-get update` on an unreachable mirror and was killed at 15 minutes instead of burning to GitHub's 6-hour default. **A cancelled leg whose log stops inside `apt-get` is a runner outage, not a defect — re-run it.**

**⏭ STEP 1, AND IT DECIDES HOW EVERYTHING ELSE READS: does a bare `tkinter.Tk()` even complete on the runner?** Not the suite — one root, one `update()`, one `destroy()`, with a timeout. A hang there means aqua needs something a headless runner does not give it (a window server session) and the answer is a different runner configuration. A pass means the hang is ours, and the next step is bisecting which leg blocks.

⚠ **This is debug-by-push and there is no way around it.** Make each push answer one question, and **write the question into the workflow step name** so the log reads as an experiment rather than a rerun.

⚠ **The local macOS box is NOT a substitute and will mislead you.** It has a window server, a logged-in session and Tk 8.6; the runner has none of the first two. **The whole #447 lesson transfers: a display without the thing that manages windows behaves differently from one with it, and the difference is invisible until measured.** If the local box passes, that is not evidence about the runner.

⚠ **#431 is waiting on a macOS answer too and is cheap to fold in** — its fix skips on aqua, and nobody has *observed* that branch being taken on a real Aqua build.

#### Open flakes and known-unstable tests

| # | what | status |
|---|---|---|
| **#447** | dialog focus/Enter cluster, Windows, ~4/50 | **OPEN.** The CI reproduction was a **missing window manager** and is fixed; **the Windows flake is NOT explained by that** and must not be closed on it |
| ~~#449~~ | `test_select_change_event_value_space` saw a stray `None` ahead of its value | ✅ **FIXED 2026-08-25 (PR #470), test-only.** The harness leaked it: `_reset_scene` destroyed a test's widgets without pumping, so a `when="tail"` event queued by one test was still in the queue while the next built its widgets. **Caught by payload match, not inference** — the stray was byte-for-byte the `ChangeEvent` emitted two tests earlier, arriving at a different `Select`. ⚠ **The product half is NOT fixed: #469.** ⚠ **The route (handle reuse?) is UNPROVEN** — a 300-round probe never forced it |
| flake C | `test_enter_on_a_disabled_button_still_reaches_the_default` | Folded into #447's family; 1 in 37, **UNEXPLAINED**, does not reproduce in a quiet process (0/40) |

⚠ **`probe_446_disabled_button_enter.py` COUNTS A BARRIER TIMEOUT AS A REPRODUCTION** — a run where the dialog never comes up yields `calls == []`, byte-identical to the flake, and the probe's READING text then points at the guard when the truth is that Enter was never pressed. **Fix that before working #447.**

⚠ **#447's rate went 4/50 -> 2/50 across #407, which SETTLES NOTHING** — inside noise at that sample size.

### Milestones

**THE RULE: numbered milestones are RELEASES; unnumbered milestones hold work NOT
YET ASSIGNED to a release.** Membership in a numbered one is decided by
compatibility *and* readiness, and the title names what actually ships. Nothing
gets a number until its order is real. **Subject lives on LABELS** (`tk9`,
`test-infra`, `hot-reload`, `new-widget`) so milestones stay about *when*.

⚠ **CLOSE A MILESTONE WHEN ITS RELEASE SHIPS.** All shipped ones are closed, which
makes **the open list exactly the live work and a direct cross-check on this
table.** They agreed 1:1 when last verified. **If they ever disagree, trust `gh`
and fix the table.**

| Order | Milestone | Open |
|---|---|---|
| 1 | **`0.4.0 — Signal binding on fields`** — ~~#458~~ (2026-08-20), ~~#465~~ (2026-08-25, PR #471), ~~#472~~ (2026-08-25, PR #473), ~~#459~~ and ~~#461~~ (2026-08-26, PR #475), ~~#476~~ (2026-08-26, PR #478), ~~#390~~ (2026-08-27, PR #480), **#444** (fixed, PR #485 OPEN and green), **#460, #467**. Cut 2026-08-19; the next release out the door. ⚠ **#390 ARRIVED 2026-08-25 from `0.6.0`** — #458/#461 turned its staleness into a regression, so the release that introduces it answers it. **It shipped as `allow_empty=`, NOT the `nullable=` its branch name and the 2026-08-26 issue comment both say.** ⚠ **#444 ARRIVED 2026-08-27 from the patch line** — it adds no public surface, so it needed no minor; it rides this one because the minor is being cut anyway, which is this file's own standing rule. ⚠ **The endpoint counts PRs as work items** — PRs #462, #471, #473, #475, #478, #480 and #485 all carry this milestone. **Verified 2026-08-28 with `gh issue list --milestone <title> --state all`: 10 issues, 7 CLOSED (#390 #458 #459 #461 #465 #472 #476), 3 OPEN (#444 #460 #467).** That command is the authority for *issues* | 3 |
| 2 | **`0.5.0 — Strictness and value types`** — #383, #369, #408, #416, **#445**, **#479**, **#481**. ⚠ **#383 KEEPS ONLY ITS GAPS 1 AND 2 (bad *values*)** — gap 3 (unknown *names*) was split out as #472 and moved to `0.4.0` on 2026-08-25. ⚠ **#445 ARRIVED FROM THE PATCH LINE 2026-08-27** and does meet the rule — `attach()`'s grid branch filters legacy layout kwargs with no rejection at all, so fixing it RAISES where the framework accepts. ⚠ **#481 came out of #390** (`Signal(None)` bare builds a signal that can never hold a value); **its title still says `nullable=True`, a parameter that never shipped.** ⚠ **#479 ARRIVED 2026-08-26 BY MAINTAINER DECISION AND DOES NOT MEET THIS MILESTONE'S MEMBERSHIP RULE — that is deliberate, do not "correct" it.** The rule is *raises where the framework accepts, or retypes what a public property returns*; releasing a subscription on destroy does neither. **Placement is the maintainer's call, not the rule's.** | 7 |
| 3 | **`0.6.0 — Form, signals, and composite authoring`** — #389, #412, #415. ⚠ **#390 LEFT for `0.4.0` on 2026-08-25** — and it **gates #389 shipping whole**, so #389's readiness now moves with a different release | 3 |
| 4 | **`0.7.0 — Guided flows`** — #311, #312 | 2 |
| 5 | **`0.8.0 — Power-user interactions`** — #315, #316 | 2 |
| 6 | **`0.9.0 — Structured editing`** — #192, #314 | 2 |
| — | **`Tcl/Tk 9 support`** (unnumbered, blocked on hardware) — #376, #378 | 2 |
| — | **`Hot reload (provisional)`** (unnumbered, outside the freeze) — #322, #328 | 2 |
| — | **`Additions awaiting a minor`** (unnumbered, rides any minor) — #208, #317, #352 | 3 |
| — | **`Wrapper and internal parity`** (unnumbered — its findings will span compatibility categories, so no release can be promised until they exist) — **#466**, the durable parameter-level guard. Cut 2026-08-20. ⏭ **#466 NEEDS A THIRD AMENDMENT, from #472's review: an AST check that every `bs.<Widget>(kw=…)` in `docs/**/*.py` names a real parameter or a layout key.** Two shipped scripts had passed keywords that never existed and **nothing caught them** — the suite does not run `docs/examples/`, `literalinclude` does not execute what it includes, and CI runs neither. **~~#463~~ CLOSED 2026-08-21**: the measurement pass ran the same day it was cut (PR #464) and filed NOTHING NEW — its findings landed on #383/#460/#461, and the table at `development/wrapper-parameter-audit-463.md` is its artifact. ⚠ **#477 (the `_impl` collapse pass) is ADJACENT BUT NOT ON THIS MILESTONE, deliberately** — this one holds parity *defects* between a wrapper and its internal; #477 asks whether the internal should exist at all, and is a PRE-1.0 goal. **Do not fold them.** | 1 |
| — | **`0.4.x — Patch line`** (rolling, **FIXES ONLY**) — #207, #422, #447. Cut 2026-08-27. It is rolling, so it does **NOT** close when a patch ships. ⚠⚠ **`0.3.x — Patch line` IS CLOSED AND THIS ONE REPLACED IT** — that is the rule working, not drift: a rolling line that turns over gets a NEW milestone, never a rename, because renaming would relabel `0.3.x`'s 3 closed issues as `0.4.x`. ⚠ **The turnover MOVED TWO ISSUES OFF THE PATCH LINE ENTIRELY: #444 to `0.4.0`** (adds no surface, but the minor was being cut anyway) **and #445 to `0.5.0`** (its fix raises). ⚠ **#449's fix shipped inside `0.4.0`, not a patch** — it was test-only and merged while `0.4.0` was open, so PR #470 was left unmilestoned rather than misreporting where it landed | 3 |

**Ordering reasons, so they are not re-litigated:** **breaks batched, not
dribbled** (#383/#369/#408/#416 in ONE minor = one migration for users instead of
four); then near-ready API, then new widgets. ⚠ **Numbers past `0.4.0` are ordering
hints, not commitments.** Retitling is cheap; that is the point of the rule.

⚠ **THE MILESTONES HAVE BEEN RENUMBERED THREE TIMES — read this table, never a
number quoted in older prose or in the archive.** The 2026-08-19 renumbering
inserted `0.4.0 — Signal binding on fields` and shifted everything above it one
step. A pre-2026-08-19 mention of `0.4.0 — Strictness` means `0.5.0`, and
`0.5.0`/`0.6.0`/`0.7.0`/`0.8.0` mean `0.6.0`/`0.7.0`/`0.8.0`/`0.9.0`.

⚠ **THE PATCH LINE IS BUG FIXES ONLY.** The project committed to SemVer at
`0.1.0`, so **adding public surface is a MINOR even when nothing breaks** —
someone upgrading `0.2.1 → 0.2.2` should be able to assume no new API arrived.
⚠ **BUT THE RULE IS ONE-DIRECTIONAL.** An addition **requires** a minor; a minor
does **not** require additions, and is free to carry as many plain bug fixes as it
likes (`0.3.0` carried two additions and **six fixes**). **So when a minor is being
cut anyway, ask what else is ready rather than parking fixes out of habit.** The
mirror-image question scoped `0.3.1`: **for a fix, ask whether it needs a minor at
all** — if it adds no public surface it can ship as a patch.

⚠ **A trap already paid for: the patch-line milestone had been renamed away from
"Fixes and small additions" while its description still said "fixes and small
additions", so the rename changed nothing. Fix the description, not just the
title.**

⚠ **A rolling line that turns over gets a NEW milestone, never a rename** —
`0.2.x` holds 15 CLOSED issues, so renaming it would have relabelled shipped work
as `0.3.x`. Check with
`gh api repos/:owner/:repo/milestones --jq '.[]|"\(.title) open=\(.open_issues) closed=\(.closed_issues)"'`.

⚠ **BUT THAT COMMAND COUNTS PULL REQUESTS AS ISSUES — do not reconcile it against
an issue list without allowing for them.** Measured 2026-08-20: `0.4.0` reported
`open=3 closed=2` while `gh issue list --milestone ... --state all` returned
**four** issues, exactly one of them closed. The second "closed issue" was **PR
#462**, which carried the milestone. **The milestone endpoint is a work-item
count, not an issue count**, and a session comparing the two would conclude an
issue had gone missing. `gh issue list --milestone <title> --state all` is the
authority for *issues*; use the API figure only for the open/closed shape.

**ELEVEN UNMILESTONED OPEN ISSUES — #431, #436, #452, #455, #468, #469, #474, #477, #482, #483, #484.** ⚠ **#477 is the `_impl` collapse pass, filed 2026-08-26 — see the ★ section; it is a PRE-1.0 goal, not a backlog nicety.** ⚠ **#468 and #469 both came out of #465's review**; #469 is the `when="tail"` hazard. ⚠ **#479 came out of #476's review and went to `0.5.0`** — it is no longer on this list. ⚠ **#482, #483 and #484 came out of #390's work.** #482 is a field's `value` lagging a programmatic signal write. **#483 is DOCUMENTATION, not a code fix (maintainer, 2026-08-27) — see the ★ section; do not re-open it as a defect.** #484 is every framework-created signal being `allow_empty=False`, so `clear()` on one gives advice the caller cannot follow. Verified 2026-08-27. Verify rather than counting by hand:
`gh issue list --state open --json number,milestone --jq '[.[]|select(.milestone==null)]'`

- **#431 is OPEN ON PURPOSE AND WAITING ON A DECISION, not on work.** Its fix
  landed with #434's, but on aqua it **SKIPS** — macOS has no NumLock modifier for
  `Mod1` to carry. The test cannot be made meaningful there and now says so out
  loud. **That resolves the failure; whether it resolves the issue is a scope
  call.** ⚠ And it is **UNVERIFIED on a real Aqua build** — fold into the #452 trip.
- **#436** — adopt `versionadded` across the public API, because the docs site
  serves ONE version and a reader cannot tell which release an API needs. Carries
  one undecided question: retroactive to `0.2.x`, or forward-only?
- **#455** — `Field.enable()/disable()/readonly()` write the ttk readonly state
  without re-deriving, plus `Field.readonly(False)` disabling the field instead of
  clearing read-only. **Latent: zero callers** anywhere. Unmilestoned because it
  gates nothing.
⚠ **"DO NOT ASSIGN A MILESTONE UNASKED" IS NARROWER THAN IT READS.** It guards
against making SCOPE calls for the maintainer. **It was never about a blocker,
whose placement is a fact rather than a choice** — an issue that gates a release
has already had its milestone decided by the thing it blocks. **The test: would
shipping the milestone without this issue be a decision, or a defect?** A defect
means it belongs on the milestone; a decision means ask.

⚠ **A bullet in this file is not proof an issue is open** — #222, #234 and #379 all
sat here as open work after being closed.
`gh issue view <n> --json state --jq .state`.

### Suite counts

⚠ **STOP RE-RECORDING THESE FROM MEMORY. This file has been wrong about them
SEVEN times, in both directions.** **Prefer a number you just measured over one
written here, and fix this section when they disagree.**

**AUTHORITATIVE — measured 2026-08-27 on `main` after the PR #480 merge**,
Windows box, `py -3.12 tests/run_gui.py`, **exit 0, 33 legs**, **`matplotlib` and
`pandas` BOTH PRESENT**:

| | measured |
|---|---|
| summed, 33 legs | **1628 passed / 22 skipped** |

⚠ **Reconciled by BOUNDING THE MOVEMENT, not by looking plausible:** `1579 + 49`, the 49 being
#390's one new test file. `git diff main...HEAD --stat -- tests/` returned that file and nothing
else, and the file's own collection was checked at each of its three review records — **40 at
round 2, 43 after the two subclass fixes, 49 at round 3** — so the total reconciles from two
directions rather than one.

**Superseded, kept for the reconciliation it anchors:** `1573 + 6`,
the 6 being #476's one new test file.
`git diff e8caece4..HEAD --stat -- tests/` says how much the count was ALLOWED to
move and confirms nothing else changed — one command, and it is the check that
catches what a self-consistent-but-wrong total does not. Here it returned exactly
one file, which is the whole check.

Prior steps, each bounded the same way: `1552 → 1573` was `+21` for #461/#459's two
files (15 + 6); `1500 → 1552` was `+24` for #465 and `+28` for #472.

**Superseded, kept for the environmental note it anchors — measured 2026-08-20 on
`main` at `41c8bad1`**, same box, same deps:

| | measured |
|---|---|
| summed, 33 legs | **1500 passed / 22 skipped** |
| shared leg | **1106 / 13** against **1119** selected |
| data leg | **123 / 6** (`pandas` present) |

The shared leg reconciles against its own collection line: `collected 1194 / 75
deselected / 1119 selected`, and `1106 passed + 13 runtime skips = 1119`.

⚠ **THIS SUPERSEDES `1458 / 21`, AND THE DIFFERENCE IS ENTIRELY ENVIRONMENTAL —
it is the first of this file's eight count discrepancies that was NOT an error.**
Against the 2026-08-19 figure (same box, both deps ABSENT):

```
1458 + 44 (test_chart.py now collects) - 2 (data leg 125/4 -> 123/6) = 1500 passed
  21 -  1 (its collection-time skip is gone) + 2 (pandas)            =   22 skipped
```

**`test_chart.py` is 44 tests behind a module-level `pytest.importorskip("matplotlib")`** — it *was* the `1 skipped` in the old collection line and now contributes all 44. **Check `py -3.12 -c "import matplotlib"` and `import pandas` before re-flagging either total**; both are legitimate on this box depending on what is installed.

⚠ **It reconciled because the COLLECTION LINE was read, not because the total
looked plausible.** The old line said `collected 1150 ... / 1 skipped / 1075
selected`; the new one says `collected 1194 ... / 1119 selected` with no
collection-time skip at all. **That vanished `1 skipped` is the whole tell** — a
session comparing only the summed totals would have seen +42 and had nothing to
attribute it to.

⚠ **A first pass summed `22` skipped by matching the `1 skipped` INSIDE the
collection line — sum the per-leg summary lines only.**

**The three checks, in order of what they actually prove:**

1. **The ceiling.** `passed + skipped` cannot exceed the selected count.
   `pytest <paths> -m "not isolated" --collect-only -q | tail -2`.
2. ⚠ **But `passed + skipped` CAN LEGITIMATELY EXCEED it by the collection-time
   skips** — a module-level skip is reported in the summary while never being one
   of the selected items. **Read the collection line before concluding a total is
   impossible.**
3. ⚠ **Self-consistency proves the run summed correctly, NOT that it selected the
   right population.** A wrong ceiling reconciles just as neatly as a right one —
   that is how the seventh error got through. **Bound the movement instead:**
   `git diff --stat <baseline>..HEAD -- tests/` says how much the count is
   ALLOWED to have changed, and it is one command.

⚠ **Platform figures are NOT comparable.** Linux at `5921dc41` read `1427 / 22`;
that is a different platform with different gating. **Do not close a gap by
picking whichever number makes the arithmetic work.**

⚠ **The data leg reads `125 / 4` when `pandas` is ABSENT and `123 / 6` when it is
installed** — two tests run only when it is missing. Documented environmental
pair, not a discrepancy. `py -3.12 -c "import pandas"` settles it.

**Record the DATE and the COMMIT beside any count, or don't record it.** Sum the
legs yourself — `run_gui.py` prints no aggregate.

---

## Backlog — what to pick up

✅ **#390 SHIPPED 2026-08-27 (PR #480). It is no longer backlog** — the entry in the ★ START
HERE section carries what outlives it, and the whole design, every measurement and every rejected
alternative are archived at `development/plan-390-signal-empty.md`. **Do not re-derive any of it.**

⚠ **Two of its standing rejections still bind.** **DO NOT re-propose per-type empties**
(`empty(int) = 0`, `empty(bool) = False`) — still rejected, and **the shipped design is NOT that**:
`''` is a real member of `str`, not a repurposed in-band value, and `Signal(int).set('')` still
raises. And **`RadioGroup`/`ToggleGroup` came in for free — #369 no longer needs to hold them.**

⚠⚠ **AN EARLIER VERSION OF THIS SECTION CALLED THE BOOLEAN REFUSAL "A GAP, NOT A PRINCIPLE" AND
POINTED AT #483 AS ITS FIX. THAT WAS OVERTURNED 2026-08-27 BY MEASUREMENT IN PLAIN `tkinter`:**
the toolkit's checkbutton has **no tristate option at all**, and its indeterminate paint is a widget
state orthogonal to the variable — settable while the variable reads `1`. **So the third state was
never a variable concept to lose, and #483 is DOCUMENTATION rather than a code fix** (maintainer).
⚠ `Switch` and `ToggleButton` reject `tristate=` outright, so this was ever about **ONE** widget.

**#389 — `Form.reset()` / `Form.clear()`.** Design settled, sketch on the issue.
**They are DIFFERENT verbs** — reset = construction-time originals, clear = `None`.
Both justified: `reset()` is **not user-implementable** (after an edit, `get()` no
longer knows the original); `clear()` is the data-entry case. Slider clears to
`min_value`. Needs an `__init__` snapshot because `set()` destroys `_data`; both
must clear validation state.

### Strictness batch (`0.5.0`) — four issues, ONE migration

- **#383** — presentation kwargs still degrading silently (`density`,
  `Tabs.orient`, `Slider.orient`, `Gauge.variant`) **plus** args that raise but
  leak a raw `TclError`/`AttributeError` (`Button.icon_position`, `Label.justify`,
  `Scrollbar.variant`, `Expander.icon_position`, `ProgressBar.mode`). **Sweep BY
  ARGUMENT NAME, not by widget.** Folds in `Slider.value = None` leaking a raw
  `TypeError` (reachable via `form.set({'slider_key': None})`) and `show_grid=True`
  silently accepted on `Row`.
  - ⚠ **#383'S THIRD GAP IS GONE FROM THIS ISSUE — it was split out as #472 and
    SHIPPED on `0.4.0` (PR #473).** That gap was about unknown **names**; the two
    left here are about bad **values**, which is why they stay batched with
    #369/#408/#416. ⚠ **Do not re-scope #383 to include it, and do not read the
    audit's mode-3 row as open work.**
  - ⚠ **BUT ONE HALF OF GAP 2 IS NOW SHARPER, NOT SOLVED.** #472 made unknown
    *names* raise a clean `TypeError` naming the widget — and in doing so it left
    `App`, `AppShell`, `Workbench` and `Window` as the visible exceptions:
    measured, they raise `TypeError` naming **`Tk.__init__`** or a bare
    `TclError`, never the widget. **That is exactly this issue's "args that raise
    but leak a raw `TclError`/`AttributeError`" complaint, now with a shipped
    counter-example to compare against.**
- **#369** — the selection family disagrees on off-list values (`SelectButton`
  raises both ways; `RadioGroup` accepts at construction, raises on assignment;
  `ToggleGroup` accepts both; and where accepted, `value` says `'MX'` while
  `selection` says `None`). **Wants ONE family decision, not four patches.**
- **#416** — `PathField` as a `Form` editor. ⚠ **`open_multiple` is FULLY DECIDED
  (maintainer, 2026-08-05) and the decision lives in a COMMENT on the issue, not
  the body, which still presents it as open.** The contract: **`open_multiple` →
  `tuple[Path, ...]`, empty `()`; every other mode → `Path | None`, empty `None`.**
  Two costs accepted deliberately: the return type depends on a construction
  argument, and **`()` rather than `None` when empty is a deliberate exception to
  the framework's `None`-when-empty convention** — the type stays stable so callers
  iterate without a guard.
- **#415** — filed with #416 from discussion #413. ⚠ **Measured finding worth not
  re-deriving: 10 of the 12 public field-family widgets are `Form` editors — the
  two that are not are `PathField` and `TimeField`** — and an unknown `editor=`
  name **silently builds a `TextField`** (`_impl/composites/form.py:774`).
  `DateField` being an editor while `TimeField` is not is what makes this drift
  rather than a design boundary.

### Before 1.0 — #477, the `_impl` collapse pass

**Maintainer's framing, and it reframes a lot of the recent defect run:** the `_impl` widgets are the ORIGINAL implementation and the public layer wraps them, so many internals are fossils carrying translations nothing needs. **Full scoping, the two-tier split and the three things a mechanical sweep would break are in the ★ START HERE section — read that, not this line.** 24 of 125 imported `_impl` classes are 1:1 with a single wrapper, all leaves. ⚠ **The 49 classes imported by name NOWHERE are a separate question and are not part of the 24.**

### Other open items

- **#412** — small and well-scoped: publish an existing internal front door so
  composite authors get a documented bare-name path *while keeping the typo
  guard*. Until it lands, `docs/reference/events.rst` stays **deliberately silent
  on custom events** — that silence is the one real cost of how #409 shipped.
  ⚠ Also folds in narrowing `resolve_event()`'s error, which is **process-wide,
  not per-widget**: `all_known` unions `GLOBAL_EVENT_MAP` with **every**
  `_CLASS_EVENT_MAPS` entry, so a `Button` typo is reported alongside
  `cursor_move`/`export`. **Don't write docs claiming the error lists what *that*
  widget knows.**
- **#376** — DataTable cell padding ignored on Tcl/Tk 9. **Unverifiable on all
  three boxes** (all Tk 8.6). Same blocker family as #378.
- **#207** — ContextMenu outside-dismiss vs a `'break'` target — **DEFERRED** (no
  API implication, low/self-inflicted impact, Win/Linux only). Agreed proportional
  fix if revisited: a module-level open-menu registry + dismiss-all from
  `DataTable._on_header_click`, **NOT** the risky grab.
- **#208** — DataTable: persist selection by record id across search/sort/page.
- **#192** — color-swatch `Select` control (decision-gated; lock shape/naming with
  the maintainer first). New widget or Select variant?
- **#328** — the E2E multi-file `@reloadable` reload test is the one OPEN piece,
  **DEFERRED** (the maintainer will write it). On PROVISIONAL `bootstack.dev`.
- **#445** — `attach()` drops legacy layout kwargs on a grid cell while rejecting
  them on a flex child. Pre-existing, filed out of `0.3.1` round 3. ⚠ **NO LONGER
  ON THE PATCH LINE — moved to `0.5.0` on 2026-08-27**, because the fix RAISES
  where the framework accepts, which is that milestone's rule. ⚠ **Its sibling
  #444 is FIXED and on PR #485** — see the ★ START HERE section; do not read this
  pair as two open patch-line items any more.
- **#432** — **DID NOT REPRODUCE** across two Linux runs; #407 appears to have
  removed it. It was the stated blocker on the whole CI workstream, so **closing
  or re-scoping it is a maintainer call that is now cheap to make.**
- **Gallery opt-in keyboard-focus ring** (future) + deferred Gallery perf (debounce
  `<Configure>`, bounded thumbnail-PhotoImage LRU, cache `_fit_caption`). Scope to
  keyboard focus, **NOT hover**.
- **`add_spacer()` → public `Spacer`** — deferred, entangled with
  `feat/unified-toolbars` (the internal `Toolbar` is pack-based).
- **Code-review follow-ups #4–#10** — cleanup/altitude items in
  `docs/_dev/widget-api-audit.md` (SelectButton stale value after `options=`;
  screenshot Win64 HWND hardening; group/window/date duplication; Calendar
  batch-redraw).
- **Docs site fleshout — substantially DONE.** Remaining is opportunistic: a review
  pass on `installation`/`quickstart` and enrichment of any still-thin page.

### API/cleanup backlog (memory-tracked)

- `project_capabilities_relevance` — `_core/capabilities` may be redundant now the
  public layer abstracts Tk; still imported by data/i18n/mixins.
- `project_event_naming_revisit` — past-tense event names pending rename:
  `SideNav.on_pane_toggled`/`on_display_mode_changed`,
  `ListView.on_selection_changed`, `Calendar.on_date_selected`.
- `project_editfilter_public_api` — `EditFilter` DEMOTED (Tk-coupled raw text
  indices/tags); investigate a de-Tkinter-ed CodeEditor extension API before any
  re-promotion. `NOTE(editfilter-public-api)` in
  `widgets/_impl/composites/textarea/filter.py`.
- `project_window_api_hardening` — `bs.Window` leaks uncurated `**kwargs` to the
  internal Toplevel, and `size`/`topmost` are construction-only. Own branch.
  ⚠ **Two thirds of this entry are now WRONG and it was never corrected — read the
  measurement, not the old wording.** *"Never releases the modal grab"* was #444 and
  is **FIXED** (PR #485). *"Has no live properties"* is false: `title` and `result`
  are both live get/set (`window.py:291-306`). **What is left is the `**kwargs`
  passthrough and the two construction-only settings.** ⚠ No memory file backs this
  entry — `project_window_api_hardening.md` is not in the store, so this bullet is
  the only record.
- `project_enum_option_typing` — promote recurring enumerated `str` kwargs to named
  `Literal` aliases in `widgets/types.py`. The ALIAS docstring carries the value
  list once; widget docstrings describe meaning only. Own branch.
- `project_show_indicator_removal` — **KEEP.** `show_indicator=False` +
  `on_icon`/`off_icon` is exactly what makes an icon-driven custom checkbox. #144
  closed won't-do. **Do NOT re-propose removal.**
- Lower-priority: bare index/landing pages; localization/windowing `tasks/` how-tos;
  screenshots pending (Tooltip/Toast, 7 Dialog pages); AppShell deferred
  improvements (`nav_pane_width=` not wired to `SideNav(pane_width=)`, hardcoded nav
  density/font, group active-child highlight + indentation, footer non-page
  widgets).

---

## Release flow

`py -3.12 -m bumpversion bump patch` → push `main` + the `v*` tag → `release.yml`
(PyPI + GitHub Release) → `docs.yml` deploys. `release.yml` fires on `v*` tags
only. There is **no `development` branch**.

⚠ **Use `py -3.12 -m bumpversion`, NOT the `.venv` shim** (stale, dies with
"Access is denied"). ⚠ **The import name is `bumpversion`, not
`bump_my_version`** — probing the wrong one reports "no module" on an interpreter
that has it. ⚠ **IT DISAPPEARS — check before every release.** Recorded installed
twice and gone twice.

**Order of operations, and the trap:** ⚠ `bump-my-version bump patch
--allow-dirty` commits **ONLY `pyproject.toml`** — it will NOT sweep the CHANGELOG
rename in, which ships a release whose notes still say `## [Unreleased]` and
breaks `release.yml`'s section extraction. **Promote `## [Unreleased]` to the
version in its OWN commit BEFORE running `bump-my-version`.**

⚠ **`docs.yml` is CHAINED to `release.yml` SUCCEEDING**, not to the tag or the
push — it triggers on `workflow_run` of "Release" `completed` and is gated on
`conclusion == 'success'`. **Any release that does not go through a green
`release.yml` run leaves the docs site stale, silently** (the run shows as
`completed/skipped`, which reads like a no-op). Kick it with
**`gh workflow run docs.yml --ref main`**.

⚠ **POST-RELEASE: `gh issue close --comment "..."` SILENTLY DROPS THE COMMENT when
the issue is already closed** — and a PR body containing `Closes #N` closes it at
merge, which is the normal case. `gh` warns only about the close. Post with
**`gh issue comment N --body ...`** and **verify it landed** with
`gh issue view N --json comments`.

### Post-release verification — every step VERIFIED, never assumed

- **PyPI** — prove with a real `pip download --no-deps bootstack==X.Y.Z`. ⚠ **The
  `/pypi/bootstack/json` summary endpoint is CDN-cached and has lagged behind a
  successful upload** — use `/pypi/bootstack/<version>/json` or a real download,
  and never read a stale summary as a failed upload and re-upload.
- **The fix, INSIDE the published wheel** — checking the artifact, not the source
  tree, is what proves a packaging-shaped bug is fixed.
- ⚠ **`import bootstack` with `idlelib` BLOCKED, every release.** That is #430's
  defect. Block the module with a `meta_path` finder, **assert the block works as a
  control**, then import. ⚠ **Grep is NOT enough and gives a FALSE POSITIVE** —
  seven `idlelib` mentions survive in the wheel and all are docstring
  attributions. **Do not re-prove #430 with grep, in either direction.**
- **Provenance asserted**, so the test cannot silently import the editable tree.
- **`NOTICE` at `dist-info/licenses/`** — it reaches users via setuptools'
  automatic license-file globbing, **NOT `MANIFEST.in`** (which names only
  `LICENSE`).
- **GitHub Release live with both assets; `bootstack.org` returning 200.**

### CHANGELOG convention

A fix commit writes `## [Unreleased]`; the promotion commit renames it AND adds
the `[X]:` link definition.

⚠ **An entry earns its place by being REACHABLE.** A CHANGELOG is read by someone
asking "was I affected?", so an entry for an unreachable defect is a false
positive. `0.2.1` deliberately omitted #397/#401 and `0.2.0` omitted #387 on those
grounds; #380, #407, #433 and #434 shipped with no entry because CI and test
harness are not reachable by any user. **Do not "fix" those absences.** Check
`__all__` and the public event registry before writing the bullet — **and say so in
the commit message, since that is where the omitted work stays documented.**

⚠ **A CHANGELOG claim about PRIOR behavior must be checked against the OLD code,
not against the fix.** The #456 bullet said a misspelled value *"previously turned
both menus off silently"*; it did the **opposite**. The sentence was written from
the fix's point of view and read as authoritative. `git show main:<file>` settles
it in one command.

⚠ **Read the entry as its AUDIENCE reads it before promoting the section.**
Verifying the *extraction* is not reviewing the *notes*. **This project has
reworded two CHANGELOGs AFTER tagging** (`0.3.1`, `0.3.2`), each forcing a
`gh release edit` on a published body.

⚠ **Read the whole `## [Unreleased]` section before promoting it.** `0.2.0`'s had
accreted across five fixes and nobody had read it end to end: **three entries were
filed under `Changed` but were plain bug fixes**, handing a reader scanning for
upgrade risk three false positives before the one that mattered.

⚠ **Verify the extraction against the REAL file before tagging, not a
simulation.** The **title** comes from the descriptive suffix after
`## [X.Y.Z] —`, so a section promoted without one ships a release titled bare
`X.Y.Z`. Confirm the body starts at `### Fixed` and no bottom link definitions
leaked in:
`py -3.12 -c "import sys; sys.path.insert(0,'.github/scripts'); from release_notes import extract; print(extract('X.Y.Z', open('CHANGELOG.md',encoding='utf-8').read())[0])"`

⚠ **Write CHANGELOG entries ONE PARAGRAPH PER LINE — do not hard-wrap.**
`release_notes.py` lifts the section verbatim into the **GitHub Release body**,
which renders a soft line break as a visible one. Unwrapped renders identically in
the repo file view and in Sphinx. **Older sections are left wrapped — do not
reformat shipped history.** Same rule for PR bodies, issue bodies, and review
comments.

### ⚠ FALLBACK: publishing BY HAND when Actions is down

Used for `0.2.2` during a major Actions outage; it worked cleanly and will be
needed again. ⚠ **Under an outage the run state itself is unreliable** (`gh run
cancel` said "already completed" while `gh run view` said `queued`) — **check
PyPI, not the run**, to decide whether anything was published.

1. `git worktree add <scratchpad>/rel-X.Y.Z vX.Y.Z` — build from a **pristine
   checkout of the tag**, never the working tree (this repo has ~60 untracked
   files in `development/`).
2. `py -3.12 -m pip install --upgrade build twine`
3. `py -3.12 -m build`, then **`py -3.12 -m twine check dist/*`**
4. `py -3.12 -m twine upload --config-file D:/Development/bootstack/.pypirc --non-interactive dist/*`
5. `gh release create vX.Y.Z dist/* --title "<from release_notes.py>" --notes-file RELEASE_NOTES.md --generate-notes`
6. `gh workflow run docs.yml --ref main` — **a manual publish SKIPS THE DOCS
   DEPLOY**, silently.
7. `git worktree remove <path> --force`

⚠ **`twine.exe` is NOT on PATH** — always `py -3.12 -m twine`. ⚠ **The token lives
at `D:\Development\bootstack\.pypirc`** (repo root, **not** `~/.pypirc`, which does
not exist), gitignored and untracked. Because it is not in the home directory,
**twine needs `--config-file` explicitly.** ⚠ **`release.yml` publishes via OIDC
trusted publishing, so there is NO token in CI** — the local `.pypirc` is the only
credential path for a manual publish, and CI's path cannot be reproduced locally.

---

## Working agreements

**Hold commits until the user tests; per-commit approval.** Never commit feature
work to `main` — create a dedicated `feat/*`/`fix/*` branch first. A fix pushed to
a branch AFTER its PR merged is **stranded** — verify it landed in `main`.

**Standing principles** (apply in every review):

- **Live properties only for legitimate runtime needs** — e.g. `surface` is
  **build-time, not live**.
- **Prefer Tk native/virtual-event bindings**; don't undo a convention without
  reason.
- **Describe the clean public surface in docs — no implementation/toolkit detail.**
- **Adversarially verify reviewer and agent claims** — agents over-flag. The
  2026-06-22 trust audit disproved 2 of the "bugs" it was handed; the Topic-guide
  review agents over-flagged 10 of 12 pages. ⚠ **But it cuts both ways: a clean
  review is not proof.** The #417 review called the tests "better than the repo
  average" and **two of them were broken** — one vacuous, one flaky — both found
  afterwards by the control the committing session should have run.
- **Pause and ask when a fix outgrows its issue** — #355 burned hours heading
  toward a `Select` value-model rewrite before the maintainer pointed at the
  ~15-line fix.
- **Test PUBLIC paths, not internal side-hacks.**
- **The framework absorbs the problem, not the developer.** A fix that hands the
  application author a new problem, or makes the end-user outcome worse than the
  bug, is not a fix.

### ⚠ Branch and worktree hygiene

- **DO NOT TOUCH A BRANCH WHILE A REVIEW RUNS.** The review reads files on disk,
  not only `git diff`, so it reviews a moving target. If follow-up cannot wait, use
  a **`git worktree`** or another branch.
- ⚠ **A worktree runs against `main`'s source unless you set `PYTHONPATH`** — the
  editable install points at `D:\Development\bootstack\src`.
- ⚠ **`PYTHONPATH` ALONE IS HALF THE FIX.** Setting it while passing **test paths
  relative to the primary checkout** runs the NEW tests against the OLD source
  (measured: 9–10 failures on every one of eight runs, where the honest answer was
  1 in 8). **Pass the worktree's ABSOLUTE test paths too**, and prove which tree
  you loaded:
  `PYTHONPATH=$W/src py -3.12 -c "import bootstack,os;print(os.path.dirname(bootstack.__file__))"`.
  **The failure mode is friendly here only by luck** — skew that breaks quietly
  reads as a real result.
- ⚠ **CHECK `git rev-parse` ON BOTH BRANCHES BEFORE READING ANY FILE.** Two
  branches were once at the *identical* commit, so a branch name did not tell you
  which code you were looking at. Review committed blobs (`git show <sha>:<path>`).
- ⚠ **RUN `git diff main...HEAD -- CLAUDE.md` BEFORE MERGING ANY BRANCH.** It must
  be empty. A branch once folded a 252-line CLAUDE.md rewrite into a fix commit,
  descending from a pre-cluster handoff — merging it would have silently reverted
  three `docs(claude):` commits. **Handoff state lives on `main` only.**
- ⚠ **NON-ANCESTOR ≠ UNMERGED.** Squash-merged branches are not ancestors of
  `main`, and a handoff once nearly read that as live work. Verify with two
  commands: `git merge-base --is-ancestor origin/<branch> origin/main`, then
  `gh pr list --head <branch> --state all --json number,state,mergedAt` — **a
  MERGED PR is what makes a non-ancestor safe to delete. Record the head SHAs
  before deleting.** ⚠ Once a remote branch is gone the ancestry check fails with
  *"Not a valid object name"* rather than reporting non-ancestry — **check the
  recorded head SHA against `origin/main` instead.**
- **Merge commits, not squashes, when the one-commit-per-issue granularity is the
  deliverable** — the standing call for #410/#423/#424/#442/#448.
- ⚠⚠ **`git mv` STAGES THE *INDEXED* BLOB, SO EDITS MADE BEFORE IT STAY UNSTAGED —
  and archiving `PLAN.md`/`REVIEW.md` runs that exact operation on EVERY branch.**
  Editing the record and then `git mv`-ing it shows `RM` in `git status`; a plain
  `git commit` then ships the rename at **100% similarity** with a message
  describing content the commit does not contain. It happened on #444 and was
  caught only by reading `git show --stat`. **`git add` the moved file after the
  `git mv`, and treat a 100% rename similarity as a failure whenever you meant to
  change the content.**

### Techniques that have repeatedly beaten static reading

- **Run an empirical probe instead of reading tangled code.** Decisive on the
  icon-DPI pipeline, the boolean-control ttk state rules, the menu window-move
  dismiss, and the #394 field alignment. **Rebuild the probe rather than reading**
  if one of these areas comes up again.
- **Tests must fail for the RIGHT reason.** A pre-fix `AttributeError` proves
  nothing — it only shows the new method doesn't exist yet. Stub the collaborator
  so the failure is *behavioral*. Tests that only assert "construction doesn't
  raise" are what let #358 ship twice.
- **Run the BASELINE before the fix**, so a before/after transition is *observed*
  rather than assumed. ⚠ **On a branch, "baseline" means CHECK OUT `main`** — a
  #417 probe read zero on both arms until it turned out to be running against
  `main` the whole time. **Print the branch, or `git checkout` it deliberately.**
- **A control experiment separates causation from correlation.** For #392 it was
  not enough that cancelling `sub_a` silenced `sub_b`; stripping the orphaned
  binding by hand and watching `sub_b` come back is what proved the cause.
- ⚠ **A control that does not reach the path under test is indistinguishable from
  a fix that works.** Round 4's first control left the test passing because the
  give-up path was never reached; **forcing the condition itself** is what
  exercised it.
- ⚠ **A probe that finds nothing must be proven able to find something.** A
  completeness scan reported **zero hits** because `ast.parse` choked on a UTF-8
  BOM and a bare `except Exception: continue` swallowed it, silently skipping every
  file. Reading `utf-8-sig` and re-running against the pre-fix commit as a control
  reproduced the two known handlers, which is the only thing that made the post-fix
  zero mean anything. **Always run the control.**
- ⚠ **A PROBE MUST BE RUNNABLE ON EVERY BOX IT IS MEANT TO INFORM.** #430's probe
  called `sys.exit(1)` the moment `idlelib` imported, so on Windows and macOS it
  printed arm 1 and stopped — even though arms 2–4 did not depend on `idlelib` at
  all. It was runnable only on the one box that could not finish the suite. **SKIP
  and continue.** This is a recurring failure mode, not a one-off.
- ⚠ **A GREEN SUITE IS NOT EVIDENCE OF STABILITY, and this project keeps learning
  it the expensive way.** `0.3.1` reported exit 0 across all legs and had **two**
  flakes at 1-in-8 and 1-in-12. **At those rates a single green run is the EXPECTED
  outcome of a broken branch.** Two habits follow: **never re-run to disprove a
  flake** — build a control that *creates* the condition and reports a rate — and
  **run the narrow combination as well as the full leg**, since ordering in a
  shared leg masks what a subset exposes.
- ⚠ **VERIFY AT THE COMMIT YOU ARE SHIPPING, not at the last one you happened to
  measure.** `0.3.0` round 4 verified one commit before a rewrite of the very tests
  it was verifying, and a flake entered `main`'s queue unseen.
- ⚠ **Re-run a recorded MEASUREMENT after any commit that changes what it
  measures.** A stale measurement block is worse than a stale table, because it
  reads as proof. Cause, three times over: a commit recording a decision by
  **APPENDING** without sweeping what it contradicted.
- ⚠ **STATE THE BOUNDARY WHEN YOU CLAIM COMPLETENESS — the scope word is where
  these go wrong.** *"No other `grab_set` exists in the package"* meant `dialogs/`,
  and the other call site was #444, found two rounds later. *"Not yet filed"* was
  true of the session and not of the tracker, and nearly produced a duplicate of a
  4-day-old issue. **A completeness claim whose scope was never written down reads
  as global and is checked as local. Write the COMMAND you ran, not the
  conclusion:** `grep -rn "grab_set" src/bootstack/` is the claim.
- ⚠ **To prove a fix does not over-reject, ENUMERATE THE PRODUCERS, don't reason
  about the consumer.** A guard's safety is a property of **who fills the
  collection**, not of who reads it. Grepping all four `self._tree.insert` sites
  settled in one command what arguing from the handler could not.
- **Before fixing a silent no-op, find what is LEANING on it.** `Form.set()` applied
  `None` to every absent field and only worked because the write was discarded —
  repairing the sentinel alone would have turned every partial `form.set()` into a
  destructive overwrite. **A no-op that has shipped for a while is load-bearing
  somewhere.**
- **When a piece of state becomes DERIVED, every existing writer becomes a silent
  no-op — and the writers outside the file are invisible.**
  `grep -rn 'state="readonly"' src/` found all seven. ⚠ **And a fix to a property is
  not a fix to the setting** — round 1 fixed the setter and MISSED THE CONSTRUCTOR
  doing the identical write. **Enumerate the ways a value can arrive (constructor,
  setter, `configure`) and pin each.**
- **Bisect order-dependent failures; do not theorize.** A scripted prefix-bisect
  found the culprit file in 6 runs; a geometry probe turned "state pollution" into
  "reqheight 1242 > window 828, so the geometry manager unmapped it".
- **Measure the surface before scoping a sweep.** An AST pass over public `__init__`
  signatures plus a construct-with-a-bogus-value probe turned "audit the siblings"
  into a table (215 kwargs, 17/24 silently accepting).
- **A platform-specific backend is often constructible off-platform.**
  `_NativeContextMenu` (macOS) is a `tk.Menu` wrapper and instantiates fine on
  Windows — which caught a `TclError`-on-separator bug. **Ask "can I build the other
  platform's object directly?" before accepting "unverifiable from this box".**
- **Prefer re-entering an existing routine over re-emitting an event by hand.** The
  #388 fix calls the entry's own `_check_if_changed()` rather than building a
  `ChangeEvent`, getting the bookkeeping for free.
- **A docstring outlives its code, and the expensive half is not the obvious one.**
  ⚠ **The toolkit leak looks wrong to any reader; the stale behavior looks
  authoritative.** Check both when a fix changes what an option means, and verify in
  the BUILT html:
  `grep -rlE "cget|instate|5-tuple|textvariable" docs/_build/html --include=*.html`.
- ⚠ **A warning meant for whoever EDITS a line belongs in a `#` comment, not a
  docstring** — the docstring is for whoever reads the docs.

### Measurement traps

- **Pair any alignment/geometry assertion with a precondition** proving the setup
  really took effect, or it can pass vacuously. **Measure within one process** —
  `winfo_rooty()` is NOT comparable across two runs.
- ⚠ **Compare captures only within ONE `bs.App` INSTANCE.** The FIRST app in a
  process renders its content white; every later one in the same process falls back
  to default grey, so two captures from different instances differ in ~99% of
  pixels for reasons unrelated to what is being measured — **and a noise control
  built from two same-population shots agreed to 14 px, so it looked sound.** That
  produced a confident WRONG conclusion.
- ⚠ **Build the noise floor across the SAME kind of change you are measuring.** A
  floor built from two static back-to-back shots was far too tight for a comparison
  that restacks a window; it was measuring text antialiasing.
- ⚠ **Measure DEPTH, not call count**, to separate re-entrancy from "it ran twice".
- ⚠ **A SYNTHESIZED CLICK CANNOT TEST A POINTER-ROUTED GUARD.** `tk busy` intercepts
  by putting a window over the target, so it only catches what the window system
  routed by pointer position; `event_generate` aimed at a widget delivers straight
  to that widget's bindings. **Some questions need a human and the probe should say
  so** rather than pretending otherwise.
- ⚠ **A 1-in-N flake cannot be verified against by re-running.** Build the control
  that **CREATES** the condition and reports a rate. `probe_437_focus_flake.py` is
  the pattern: arm 1 is the mechanism, arm 2 the quiet-process control.

### Tk and tkinter traps

- ⚠ **`event_generate` on a virtual event is DROPPED while the window is unmapped —
  use `shown_app`, not `app`.** The `app` fixture's root is **withdrawn**. A
  `bs.Button` still dispatches `<<Click>>` there, but a composite like `bs.Slider`
  receives **nothing** — not even a raw Tcl binding bypassing Python, which is what
  proves it is Tk dropping the event. **Pre-existing** — confirm with `git stash`
  before blaming your own diff.
- ⚠ **`shown_app` is NOT enough — a widget packed into the shared root may still be
  UNMAPPED**, because `pack()`ing a raw frame competes with the App's own geometry
  management and **once earlier tests have filled the root the frame is not mapped
  at all**. The tell is a test that **passes alone and fails in the suite**. Worse,
  it fails as a *false negative about the thing under test*. **Build a real event
  target in its own `Toplevel`** (`geometry`, `deiconify`, `update`, `focus_force`)
  and **assert `winfo_ismapped()` as a precondition**.
- ⚠ **Tk's `focus_set()` is a SILENT no-op when the widget or any ancestor is
  unmapped** — `TkSetFocusWin` walks the ancestry and returns without setting
  anything. The miss surfaces one line later as an inexplicable focus assertion.
  ⚠ **Under X11 it is the WINDOW MANAGER, not the server, that assigns focus to a
  newly mapped top-level.** `focus_lastfor()` returning the **empty string** is not
  "focus is on the wrong widget" — it is "nothing in this toplevel ever held focus",
  which is what a missing WM produces.
- **Assert focus via `focus_lastfor()`, not `focus_get()`** — the latter reports
  nothing unless the window is active.
- ⚠ **`dlg.show()` runs a modal wait loop that a close scheduled with `after` does
  NOT break.** Drive it by invoking a real footer button, and **poll for the modal
  grab rather than firing on a fixed delay** — `show()` pumps the event loop while
  building and positioning, so a timer can land on a half-built dialog. ⚠ **The
  grab is the barrier because it is the last thing `show()` does before it waits** —
  but ⚠ **the grab is set BEFORE the geometry manager maps the footer's children at
  idle**, so a grab-only barrier is not enough when the widget under test is a
  child. **Scope the barrier to the subtree you actually need.**
- ⚠⚠ **TK DROPS A GRAB WHEN ITS HOLDER IS DESTROYED BUT NEVER RESTORES THE ONE THAT
  HOLDER DISPLACED.** Whatever takes a modal grab has to hand back what it found, or
  the window underneath is left on screen, still blocking its caller, holding
  nothing — modal in appearance only. That is #440 (dialogs) and #444 (windows), the
  same defect twice. **`_runtime/grab.py` is the ONE home for the pairing; import
  `capture_grab`/`restore_grab` from it and do not write a second pair.** ⚠ **Capture
  BEFORE taking the grab** — once another window grabs, the previous holder's
  `grab_status()` reads `None`, so a kind read afterwards is always wrong, which is
  why the pairing is one function rather than two steps. ⚠ **The invariant is holder
  AND KIND, never identity alone**: a global grab restored as local silently narrows
  modality, and that passed every test before #440. ⚠ **`grab_current()` resolves a
  path through `_nametowidget`, which raises `KeyError`** — not `TclError` — for a
  window Tcl created on its own (a posted `ttk::combobox` popdown is one).
- ⚠ **Do not synthesize keys in the shared-root suite.** Drive the routine the key
  is bound to (`ttk::treeview::ToggleFocus`). The key-to-routine mapping is the
  toolkit's binding table, not ours.
- **Tk REJECTS `event_generate("<Double-1>")`** — `Double` is a binding pattern, not
  an event type. Two presses is the only way. ⚠ **And synthesized events default to
  `time=0` while Tk decides `Double` off the event clock**, so supply an explicit
  `time=`.
- ⚠ **`winfo_ismapped()` on a destroyed widget RAISES `TclError: bad window path
  name` — it does not return 0.**
- ⚠ **AN EVENT SENT WITH `when="tail"` CAN OUTLIVE ITS WIDGET AND BE DELIVERED TO A
  DIFFERENT ONE.** It is queued against the emitting **window**, not the Python object,
  so destroying the widget before the loop turns leaves it in the queue with nothing
  valid to receive it. **Proven by payload match, not inference** (#449): the stray
  `ChangeEvent` that failed `test_select_change_event_value_space` was byte-for-byte the
  one emitted two tests earlier — `(value=None, prev_value='Small', text='')` — arriving
  at a **different** `Select`. ⚠ **Tk path names are never reused** (the per-parent
  counter only climbs), so it is not happening by name, and **the actual route is
  UNPROVEN** — a 300-round probe built to force window-handle reuse produced zero, with
  its control arm proving it can detect a delivery. **You do not need the route: remove
  the precondition.** `tests/conftest.py::_reset_scene` now pumps `root.update()` before
  destroying. **The product half is UNFIXED — #469**, and ~20 composites emit this way.
- ⚠ **A LIVE SIGNAL SUBSCRIPTION OUTLIVING ITS WIDGET IS A DIFFERENT BUG FROM #469, AND IT IS #479.** #469 is a *queued* event delivered to a *different* widget; #479 is a subscription that is never cancelled, so a **destroyed** widget keeps emitting: `event_generate` on a dead window raises `TclError: bad window path name` **inside the Tk trace**, where the caller cannot see it, and the subscription **pins the destroyed widget in memory** (measured with a weakref after `gc.collect()`). `OptionMenu` is the instance found; **`ValueSignalMixin._bind_value_signal` (`field_mixin.py:305-310`) is the pattern that gets it right** — hold the id, release it in `on_destroy`. ⚠ **Check for this whenever `_impl` code subscribes to a signal it does not own.**
- ⚠ **`update_idletasks()` DOES NOT SERVICE QUEUED WINDOW EVENTS — only `update()` does.**
  Measured directly in `development/probe_449_queued_event_after_destroy.py`. This
  matters because `update_idletasks()` **silences** the #449 flake while fixing nothing,
  purely by shifting timing — as did instrumenting the leg, twice. ⚠⚠ **A RATE IS NOT
  EVIDENCE FOR A TIMING-DEPENDENT FLAKE: 0/5 was reached by a fix AND by a shim.** Assert
  the invariant instead — `test_harness_event_queue.py` queues a probe event on the root,
  calls `_reset_scene`, and asserts it arrived; it FAILS on the shim and on the old
  conftest, which is the only instrument that told them apart.
- ⚠ **Some failures are INVISIBLE TO PYTHON — read the background-error channel.** A
  binding or `after` script referencing a deleted Tcl command raises nothing Python
  can see; the suite stays green and the symptom is "handlers mysteriously stopped
  running". Install a collector (`root.tk.createcommand('bgerror', collector)`, and
  `deletecommand` it in a `finally`). **When a bug has no public observable, this
  channel IS the observable.**
- ⚠ **Defer widget cleanup on the ROOT, never on the widget.**
  `widget.after_idle(cb)` registers `cb` as a command owned by that widget, so
  destroying it deletes `cb` while the timer is pending and Tcl fires an orphan. Use
  `widget._root().after_idle(...)`. Guard against both `TclError` **and
  `AttributeError`** — `destroy()` sets `_tclCommands` to `None`.
- ⚠ **Tkinter binding names are recycled — never let a deferred cleanup hold one.**
  `Misc._register` names a command from `id()` of a throwaway bound method, so
  releasing it frees the address for immediate reuse: **498/499** consecutive
  cycles returned the *identical* name. Anything postponing a `deletecommand` can
  delete a *different, live* binding. **Make the name unique first.**
- ⚠ **When a symptom is allocator- or timing-dependent, assert the INVARIANT, not
  the symptom.** Behavioral tests passed on a broken build (1 of 3 caught it); a
  structural test (50 cancel/rebind cycles → 50 distinct ids) fails every time.
  **Worth breaking "test public paths" for; say why in the test.**
- ⚠ **`instate(['!disabled'])` is a QUESTION returning True when the widget is
  ENABLED.** `not instate(['!disabled'])` therefore selects the **disabled** one — a
  double negative that silently inverts a guard. Write `not instate(['disabled'])`.
- ⚠ **A test that schedules a hang guard must cancel it in a `finally`.** A leaked
  10s `after` on the shared root fired during a later test and destroyed an
  unrelated `Toplevel` — **and the test passed either way**, which is what made it
  invisible.
- ⚠ **Spying on an instance attribute is USELESS if the bound method was already
  captured.** `self.on_destroy(self._cleanup_x)` captures at construction. **Patch
  the CLASS attribute before constructing**, or assert on the observable side
  effect.
- ⚠ **Never `warnings.warn` from inside a Tk dispatch or a teardown path — use
  `debug_log`.** `_runtime/utility.py` has `debug_log(message)` beside
  `debug_log_exception`; both honor `BOOTSTACK_DEBUG` and **never raise**. A
  `warnings.warn` measurably escapes `Subscription.cancel()` under `-W error`. **A
  diagnostic that can fail the program it is diagnosing is not one.**
- ⚠ **Probe output must be ASCII** — a check mark raises `UnicodeEncodeError` on the
  Windows box's cp1252 console.

### ⚠ Line endings — this has bitten repeatedly, including with the warning in context

Files in this repo are **CRLF** (`core.autocrlf=true`, `.gitattributes` declares
`eol: crlf`). **`git diff` CANNOT SEE a flip to LF** — Git normalizes on read, so a
whole-file flip still shows the true small diffstat.

- **The ONLY signals** are the *"LF will be replaced by CRLF"* **warning on
  stderr**, which no test run and no docs build surfaces, and **`file <path>`**,
  which reports the working-tree truth.
- **A bulk `pathlib` rewrite, a `sed -i`, and Python `read_text`/`write_text` all
  flip CRLF→LF.** A `sed -i` with a `$`-anchored pattern **silently matches
  nothing** on CRLF files.
- **Prefer the Edit tool. If scripting, write BYTES** (strip `\r`, then re-add).
- ⚠ **A manual edit once left a stray `u` byte before a BOM (`75 ef bb bf`) and the
  WHOLE PACKAGE became unimportable** — `SyntaxError: invalid non-printable
  character U+FEFF`, every affected test file erroring at collection. **Verify
  `import bootstack` at the COMMITTED state**, not just in the working tree, when
  anything has hand-edited a source file.

---

## Gotchas

### Layout and wrappers

- **Self-placement via `**kwargs`** — `fill`, `expand`, `anchor`, `row`, `column`
  etc. are NOT explicit params. Route through `self._split_layout_kwargs(kwargs)`.
  ⚠ **SINCE #472 THAT SEAM IS DEFAULT-STRICT: whatever survives the split RAISES
  `TypeError` naming the widget.** It is an INSTANCE method now, not a
  `@staticmethod` — call it `self._split_layout_kwargs(...)`. **A new wrapper is
  strict for free and needs no guard of its own.** Only a wrapper that hands
  leftovers to its internal on purpose opts out, with the class flag
  `_forwards_kwargs = True` (Chart, MenuButton, Picture, StatusBar, Toolbar).
  ⚠ **A sixth opt-out FAILS `test_declared_forwarders_are_exactly_the_five` on
  purpose** — the flag is declarative precisely so the exemption list can be
  enumerated. ⚠ **And if a wrapper needs a crafted error for a specific key, put
  that check ABOVE its split**, or the generic error fires first and retires it.
- **`**kwargs` not `**extra_kw`** — catch-all must be named `**kwargs` throughout.
- **User options MERGE OVER framework kwargs; structural keys RAISE** (#363). A
  widget that builds another widget for you — `Form`'s `editor_options`,
  `MenuButton`'s `menu_options`, the `**kwargs` passthrough on `ButtonGroup.add` /
  `RadioGroup.add` / `Toolbar.add_widget` — must route through **`merge_kwargs`**
  (`widgets/_core/kwargs.py`): the caller's options win, and a short `reserved` map
  raises `BootstackError` naming the API called and what to use instead. Splatting a
  user dict alongside explicit kwargs raises `TypeError: got multiple values for
  keyword argument` from an internal class the caller never wrote.
  ⚠ **Legacy exception:** `MenuButton.__init__`'s `_RESERVED_INTERNAL_KEYS` still
  **SILENTLY SKIPS** collisions (so `bs.MenuButton("X", command=fn)` quietly does
  nothing). **Do NOT copy the silent-skip pattern into new code.**
- **`margin_x=` / `margin_y=`** — axis-specific external spacing. Never
  `padx=`/`pady=`.

### Widgets and API

- **Public namespace is CURATED (PR #104)** — top-level `bootstack` (`bs.*`) holds
  ONLY what you compose a UI from: every widget, `App`/`AppShell`/`Window`,
  `Signal`, the dialog VERBS, and `set_theme`/`toggle_theme`. Everything else comes
  from its submodule — `from bootstack.data import SqliteDataSource, col`;
  `bootstack.style`, `.i18n`, `.validation`, `.events`, `.streams`, `.scheduling`,
  `.shortcuts`, `.store`, `.errors`, `.types`; dialog CLASSES from
  `bootstack.dialogs`. `MessageCatalog`/`IntlFormatter`/`get_current_app`/`Image`
  are INTERNAL. **Do NOT write `bs.Theme`/`bs.col`/`bs.FormDialog`** — they no
  longer exist at top level. Guard: `tests/test_public_surface.py`.
- ⚠ **Write the submodule import, NOT `bs.events.ChangeEvent`** — `events` is absent
  from `bootstack.__all__` and `bs.events` resolves only because widget code imports
  the submodule transitively. ⚠ **`tests/test_public_surface.py` does NOT guard
  this** — it gates the top-level *name set*, never that a submodule is unreachable
  as a `bs.*` attribute, which is why the drift went uncaught for two months.
- ⚠ **`emit()` and `on()` take the same names but NOT always the same target.**
  `emit()` consults the `_event_target()` seam **only for `<<Virtual>>` sequences**;
  the native-mapped names (`click`/`focus`/`blur`/`submit`) fire on `_internal`, so
  `field.emit("submit")` on a retargeting composite reaches nothing bound through
  `on()` — silently. Generating a real sequence at the inner entry *drives* the
  widget instead of notifying about it.
- **Dialogs live in `bootstack.dialogs`** — impl under `bootstack/dialogs/_impl/`.
  `bootstack.widgets.dialogs` is GONE. ⚠ **`bootstack.dialogs.FormDialog` is a
  public WRAPPER**, not the impl; reach the impl through `._internal`.
- **`bs.App` / `bs.AppShell` config is FLAT kwargs.** There is **NO public
  `settings=` / `AppSettings` / `app.settings`** (clean break, no shim — passing
  `settings=` raises `TypeError`). Read/write as symmetric `app.*` properties;
  locale-derived values are flat read-only props. Config-change events:
  `app.on_theme_change(fn)`, `app.on_locale_change(fn)`. Persistence:
  `bs.App.from_store(store)` + `store.update(theme=...)`.
- **`bs.Signal()` is safe at module level** — the backing Tk var is created lazily.
- **`textsignal=`** for text-bearing widgets; **`signal=`** for non-text. Never
  expose `textvariable=`/`variable=` publicly.
- **`TTKWrapperBase.__init__` overwrites `self._accent`** — store accent before
  `super().__init__()`, re-assign after.
- **`<<BsThemeChanged>>`** fires after full rebuild (use this). `<<ThemeChanged>>`
  fires before.
- ⚠ **Canvas/imperatively-painted widgets — NEVER bind ttk `<<ThemeChanged>>` on the
  root/toplevel.** It re-fires **~1400× per rebuild** (once per style reconfigure);
  root-bound × instances = thousands of redraws. Re-resolve via the **STD
  `Publisher`** (fires once, after rebuild) and **gate the redraw on visibility**.
  `Frame` subclasses: `self._enable_theme_repaint(self._redraw)`.
- **`bs.DataTable`** (renamed from `bs.Table`) works with any `DataSourceProtocol`
  source; identity reads route through
  `_record_id`/`_public_record`/`_internal_fields`. No built-in border; `density=`
  and a footer separator supported.
- **`RadioGroup.set()` validates against keys**, not values. **`bs.Form` uses
  `col_count=`**, not `columns=`. **`ToggleGroup(padding=N)`** is safe now.
- ⚠ **`value=` ignored when `signal=` also passed** on boolean widgets — seed the
  Signal directly.
- ⚠ **`disabled` on Label** is not appropriate — Label is display-only.
  **`color=`/`background_color=`** removed; use `accent=`/`surface=`.

### Boolean controls

- **Switch** has no `on_icon`/`off_icon`/`icon_only`/`show_indicator`/`tristate`/
  `density`. **ToggleButton** has no `tristate`/`show_indicator`. **Checkbox** is
  the only widget supporting `tristate`. **Density**: Checkbox and Switch do NOT
  support `density=`; ToggleButton does.
- **Sphinx signatures** — give each subclass its own `__init__` to avoid inheriting
  unsupported params; `:inherited-members: PublicWidgetBase`.

### Layout widgets

- **`height=`/`width=` on stacks** — setting one collapses the other axis. Add
  `fill=` + `expand=True` for the unconstrained axis.
- **`show_border=True` needs padding** — the border is inside the frame edge.
- **`Grid columns=N` shorthand** — `columns=3` ≡ `[1,1,1]`. `0` == `'auto'`.
- **`variant=` removed from stacks** — use `bs.Card` for card-variant layout.

### Dialogs

- **7 doc pages**; `dialogs.rst` is toctree-only. `ColorDropperDialog` is internal.
- **`content_builder`** fills a PUBLIC content `Column` set as the active parent —
  write the body parent-free (`def build(): bs.Label(...)`). `Dialog(padding=, gap=)`
  configures it. bootstack's own verb/Form dialogs render raw and opt out with
  `_raw_content=True`.
- **`Frame.configure(surface=...)`** does NOT work at runtime — use
  `configure_style_options(surface=...)`.
- **`Dialog.__init__`** is fully keyword-only; `parent=` not `master=`;
  `min_size=`/`max_size=`. **`ButtonRole`**: `"primary"`, `"secondary"`, `"danger"`,
  `"cancel"`.
- ⚠ **`Dialog._toplevel` is never reset** — after a modal `show()` it is a DESTROYED
  widget. Resolve the result target from `master`, and poll `winfo_ismapped()` in
  modal tests.
- ⚠ **Enter handling asks the bindtag AND the keysym, both internal.** The test is
  **`keysym != "KP_Enter"`, NOT `== "Return"`, deliberately** — an unknown keysym
  then reads as consumed, because standing down wrongly costs a dead key while
  firing wrongly costs #441 itself. Pinned by its own test so it is not "simplified"
  into the equality form. **Measured:** a button answers `<Key-Return>` **and**
  `<Key-KP_Enter>`; a text widget answers only `Return`. ⚠ **Windows can reach this
  path by NEITHER route** (synthesis yields keysym `??`; the physical key folds into
  `Return`) — only X11 can run it end to end.
- ⚠ **A DISABLED button swallowing Enter** was a real defect: a stand-down guard
  must not assume a button that received the key acted on it.
- ⚠ **`event_add` mapping real keys to a virtual `<<Submit>>` WORKS but does NOT
  solve dispatch.** Measured: on a tag carrying **both**, the **PHYSICAL binding
  wins and the virtual one does not run at all**; the mapping is
  **per-INTERPRETER**, not per-widget; and **it does NOT change the bindtag walk**.
  Adopt it for clarity if wanted, but **do not scope #441 around it.**

### Sliders / fields

- ⚠ **THE FIELD FAMILY DISAGREES ABOUT WHETHER A PROGRAMMATIC SET IS A CHANGE, and
  nobody has decided which is right.** Measured 2026-08-26 with the event queue
  drained (so the `when="tail"` emitters are not undercounted): `w.value = x` in code
  emits **one** `<<Change>>` on `Select`, `TimeField` and `SelectButton`, and **zero**
  on `NumberField` and `DateField`. Plausibly deliberate — change meaning *user
  commit* — but it is not uniform and it is not written down anywhere.
  ✅ **MAINTAINER DISPOSITION (2026-08-26): KEEP IN MIND, DO NOT FIX, DO NOT FILE.**
  Unsure which behavior is correct, so nothing is being changed on it now. **Do not
  "harmonize" the family as a drive-by**, and do not re-propose filing it — raise it
  only if a real defect lands on top of it. Found out of #476, recorded in that
  branch's `PLAN.md` as out of scope.
- **Slider/RangeSlider spacing** — `gap=` does not visually separate tracks; use
  `margin_y=10`. Track heights: plain ≈ 24px, ticks ≈ 45px, badge+ticks ≈ 65px.
- **`anchor_items="baseline"`** is invalid — use `"s"`.
- **`select.py` / `calendar.py` shadow stdlib** — use `selectfield.py` and
  `calendarwidget.py`.
- **The property is `read_only`, not `readonly`** — a public widget is a plain
  Python object, so a bogus attribute sticks **silently** and the field keeps
  working. That produced a vacuous probe once.

### Style rebuild / MenuButton / misc

- **`configure_style_options` alone doesn't rebuild** — it only updates the stored
  dict. Call `rebuild_style()` immediately after.
- **`emit` wraps `event_generate`** — for internal widgets use `event_generate` with
  `data=` natively.
- **MenuButton item types**: public API uses `'command'`, `'check'`, `'radio'`,
  `'separator'`; internal ContextMenu uses `'checkbutton'`/`'radiobutton'`.
  Translate at the wrapper boundary via `_ITEM_TYPE_MAP`.
- **`show_menu()` respects disabled state** — guard with
  `instate(("!disabled", "!readonly"))`. **`disabled` property** — use
  `instate(("disabled",))`, not string comparison on `cget`.
- **American English** — all docstrings and user-facing text.
- **`font="heading-md"`** not `"heading-md[bold]"` — headings are already bold.
- **`&` in `bs.Label` text** — Tkinter strips it. Use `"and"`.
- **`Expander` is internal** — use `bs.Accordion`.
- **Run examples after editing** — always `python docs/examples/<widget>.py` before
  committing.
- **`Shortcuts` service** — public surface is `bootstack.shortcuts`: the `Shortcuts`
  class, the `Shortcut` dataclass, `get_shortcuts()`. `format_shortcut(spec)` is
  INTERNAL.

### Screenshots

Full patterns are in `docs/_dev/docs-authoring-patterns.md`. The traps:

- **Stacks centre children** — wrap button rows in a row container with `fill="x"`.
- **No `size=` by default**; use `minsize=(720, 1)` for input/field/slider rows.
  Full-app widgets (PageStack, SideNav, AppShell) need `size=(W, H)`.
- **Popdown menus** — the runner sets `topmost=True` at t=800ms and grabs at
  t=950ms; call `show_menu()` at t=850ms. The menu Toplevel is captured via a
  **screen** grab, so size the window to contain it.
- **Dialog hero** — open non-modally at t=200ms, lift at t=850ms, shoot at t=950ms;
  `app._capture_target = <toplevel>`.
- **The runner crops 2px per edge** to remove the Windows border artifact.

---

## Architecture (settled)

**Public API** is a composition layer over internal widgets. Public widgets are
plain Python objects (**NOT** `tk.Widget` subclasses) holding `self._internal`.

Constructor order: resolve parent → split layout kwargs → construct internal →
attach to parent. `.tk` returns the underlying ttk widget — escape hatch, the
user's responsibility.

### Context-manager parenting

```python
with bs.App(title="Demo", padding=16, gap=8) as app:
    with bs.Row(gap=4):
        bs.Label("Hello")
        bs.Button("OK", on_click=lambda: ...)
app.run()
```

`__enter__` pushes container, `__exit__` pops. App hides on enter, shows on exit.

### Events

```python
sub = widget.on_change(handler)                    # -> Subscription (cancellable)
widget.on_change().debounce(300).listen(handler)   # -> Stream (composable)
```

All `on_*()` shorthands use `@overload`: no-arg → `Stream`, with handler →
`Subscription`.

- **Data events** (`change`, `input`, `select`, validation) → the typed payload
  dataclass, **unpacked**: `on_change(lambda e: e.value)`. Payloads live in
  `bootstack.events`. **ListView item events are the exception** — a plain record
  `dict` (`e["field"]`).
- **Native events** (`click`, `hover`, `focus`, `blur`, `resize`, key, scroll) → a
  curated, Tk-free `Event`: `widget`, `x/y/x_root/y_root`, `width/height`, `delta`,
  modifier bools `ctrl/shift/alt/meta`, clean `key/char`, `time`.
- The generic `on(name, handler)` is typed `Callable[[Any], Any]` (string-keyed,
  can't infer the payload); precise types are on the `on_<event>()` shorthands.
- Transform happens in `adapt_handler()` (`widgets/_core/base.py`); emit sites build
  the dataclass. `on()` resolves through **one seam**,
  `PublicWidgetBase._event_target(sequence)` — the ten retargeting wrappers override
  only that. Regression coverage: `tests/widgets/public/test_event_target_seam.py`.

### Signals

```python
sig = bs.Signal(value)
bs.TextField(textsignal=sig)   # two-way binding
sig.subscribe(lambda v: ...)
```

### Layout

⚠ **`bs.HStack` / `bs.VStack` DO NOT EXIST** — the stacks are **`bs.Row`** and
**`bs.Column`**. Any `HStack`/`VStack` surviving elsewhere in the docs or the
archive is stale.

```python
bs.Column(padding=20, gap=12)
bs.Row(gap=8, vertical_items="center")
bs.Grid(columns=["auto", 1], gap=8)
```

Signatures — `Row`/`Column`: `parent`, `horizontal_items`, `vertical_items`,
`grow_items`, `weights`, `gap`, `padding`, `surface`, `show_border`, `width`,
`height`, `**kwargs`. `Grid` swaps `grow_items`/`weights` for `columns`, `rows`,
`auto_flow`.

⚠ **Container defaults are `horizontal_items=` / `vertical_items=` / `grow_items=` /
`weights=`.** `fill_items=`, `expand_items=`, `anchor_items=` and `sticky_items=`
are all GONE.

⚠ **`fill=`/`expand=`/`anchor=`/`sticky=`/`side=` on a layout child RAISE**, they
don't degrade. **THERE ARE TWO MESSAGES, and which one you get depends on how the
container PLACES the child — not on its class:**

- **flex child** (`Row`, `Column`, and `Card`/`GroupBox`/`Accordion` in their
  DEFAULT column mode) → advised `grow=` plus `horizontal=`/`vertical=`.
- **grid cell** (`Grid`, any page or pane, anything built with `layout="grid"`) →
  advised `horizontal=`/`vertical=` and weighting the row or column. ⚠ **It
  deliberately does NOT say `grow=`: a grid cell FILTERS that kwarg away silently**,
  so recommending it would replace advice that raises with advice that quietly does
  nothing.

⚠ **This was wrong twice, in both directions** — first advising
`align_self=`/`justify_self=`, which have never existed; then giving every container
the flex advice, including four that grid. `grep -n '_reject_legacy_child_kwargs'
src/` returns nine call sites; **the `kind` argument is required and positional
precisely so a caller who forgets gets a `TypeError` rather than the wrong message
reaching a user.** ⚠ **`attach()` is the one path still exempt** — its grid branch
filters with no rejection at all. Filed as **#445**.

### Source structure

```
src/bootstack/
├── _core/       infrastructure (capabilities, colorutils, mixins, publisher, images)
├── _runtime/    Tk patches (app, toplevel, menu, shortcuts, events)
├── assets/      locales, icons
├── data/        DataSource (Base, Memory, Sqlite, File)
├── dialogs/     dialog implementations
├── signals/     Signal, TraceOperation
├── style/       Theme (public), themes/, Style/Typography/Font (internal), builders
├── validation/  ValidationRule, ValidationResult
└── widgets/
    ├── _core/   public framework internals (base, container, context, events)
    ├── _impl/   internal implementation (primitives, composites, mixins)
    ├── app.py, button.py, ...  (~40 public wrapper files)
    └── types.py AccentToken, WidgetDensity, SurfaceToken, per-widget variants
```

### Key API reference

```python
import bootstack as bs

with bs.App(title="My App", size=(800,600), padding=16, gap=8) as app:
    sig = bs.Signal("World")
    bs.Label("Hello!", font="heading-lg")
    bs.Button("OK", accent="primary", on_click=lambda: ...)
app.run()

with bs.AppShell(title="My App", theme="bootstrap-light") as shell:
    shell.commandbar.add_button(icon="sun", command=bs.toggle_theme)
    with shell.menubar.add_menu("File") as file:
        file.add_action("Quit", shortcut="Mod+Q", on_click=shell.close)
    with shell.add_page("home", text="Home", icon="house"):
        bs.Label("Welcome!")
    shell.navigate("home")
shell.run()

# Tokens
accent  = "primary|secondary|info|success|warning|danger|default"
variant = "solid|outline|ghost|toggle"
surface = "content|card|chrome|overlay"
font    = "body|heading-lg|heading-md|caption|code|body+2[italic]"

# Dialogs
bs.alert("Done.")
bs.confirm("Delete?")                 # -> bool
bs.ask_string("Name:")                # -> str | None
bs.ask_integer("Age:", min_value=0)   # -> int | None
bs.ask_date("Pick date:")             # -> date | None
bs.ask_color()                        # -> ColorChoice | None
bs.ask_font()                         # -> Font | None
```

---

## Code standards

**Docstrings:** one-line summary + description + `Args:` (name: description, no
types). Single backtick `` `X` `` — never double. No RST roles. Valid values +
defaults per kwarg.

**Dataclasses — document fields with ATTRIBUTE DOCSTRINGS, never `Args:`.** A
one-line class summary, then a short docstring literal *directly under each field*.
Do NOT also list fields in an `Args:` block — that renders them twice.

⚠ **No colon on the FIRST LINE of an attribute docstring.** napoleon splits the
first line at the first `:` and jams the pre-colon text into a bogus `:type:` field,
**SILENTLY mangling the rendered type** (it only *warns* when the split also breaks
a backtick pair). A colon on line 2+ is fine. Use an em-dash or period to introduce
an enum list.

```python
@dataclass
class ChangeEvent:
    """Fires when a field's value is committed (on blur or Enter)."""

    value: Any = None
    """The committed, parsed value."""
    prev_value: Any = None
    """The value before this change."""
```

**`on_*()` shorthands:**

```python
@overload
def on_change(self) -> Stream: ...
@overload
def on_change(self, handler: Callable[[Event], Any]) -> Subscription: ...
def on_change(self, handler=None):
    return self.on("change", handler)
```

**No Tkinter in docs or docstrings** — no `tk.*` types or terms unless strictly
necessary; don't feature the escape hatch. LEFT BY DESIGN: `.tk`/`.var`
escape-hatch property docstrings, `signals/integration.py` (the Tk bridge).

---

## Open bugs

- `value=` silently ignored when `signal=`/`variable=` also passed (all boolean
  widgets)
- `Style._tk_widgets` grows forever — partially resolved; pages are never destroyed

---

## Recently shipped — pointers only

**Full detail — root causes, decisions, gotchas — is in
`docs/_dev/handoff-archive.md`, indexed by issue/PR number.**

| Release | Contents |
|---|---|
| **0.3.2** (2026-08-13) | *Read-only select fields*. **#453** — `read_only=True` on a `Select` was accepted and ignored: the arrow dimmed so the field *looked* locked while a click in its text area still opened the option list, and `select.read_only` answered `True` for every `Select` ever built. The ttk `readonly` state was doing double duty and is **derived, never storage** now; `TimeField` fixed with it |
| **0.3.1** (2026-08-12) | *Dialog keyboard and modality*. Four fixes, no new public surface. **#441** Enter in a multi-line field inserted its newline and the dialog closed on top of it · **#440** a nested modal released the grab entirely instead of handing it back · **#439** the default button's `focus_set()` ran while the window was hidden, where Tk silently ignores it · **#426** the layout migration error recommended kwargs renamed before release |
| **0.3.0** (2026-08-11) | *Screen capture and dialog results*. **A minor carrying two additions and SIX fixes.** **#427** `widget.capture(path)` · **#429** a click during `settle()` re-entered the handler; it now holds `tk busy` (the first fix, which stopped dispatching, was REVERSED because it photographed stale pixels on macOS) · **#428** `FormDialog.result` returned display text because it read after every editor was destroyed · **#437** a refused press still recorded its result · **#438** `DialogButton.closes` meant three things and is REMOVED. ⚠ **`tk busy` is a no-op on macOS** (a toolkit limitation, measured in plain tkinter) and real on Windows |
| **0.2.3** (2026-08-08) | *Import without IDLE*. **#430** — `import bootstack` raised `ModuleNotFoundError` on any Python without `idlelib` (Debian/Ubuntu package IDLE separately), taking down the **whole framework**. `idlelib` is stdlib so it could never be a declared dependency; `WidgetRedirector` is **ported** into `textarea/redirector.py`. ⚠ `NOTICE` carries a PSF attribution **scoped by measurement to `redirector.py` ALONE** — the other five IDLE-derived modules share 0–7% and implement IDLE's *designs*, which is an idea, not protected expression |
| **0.2.2** (2026-08-06) | *DataTable group headers and row events*. #417 · #418/#420 · #419 · #421. **Published MANUALLY during an Actions outage.** ⚠ Two behavior notes: a double-click delivers `on_row_click` **click, double, click** (the double lands BETWEEN the clicks, because `on_row_click` rides `<ButtonRelease-1>` while `<Double-1>` is a ButtonPress pattern), and a read-only table's second press no longer repeats the first press's action |
| **0.2.1** (2026-08-05) | *Event and shortcut correctness*. #403/#404, #406, #405, and the #392-review cluster (#396, #398, #399, #400). **#397 and #401 fixed but deliberately absent from the CHANGELOG**, being unreachable from public API |
| **0.2.0** (2026-07-30) | #332 · #379/#385 · #381 `InvalidChoiceError` on bad behavior-mode kwargs · #387 · #388 · #394/#395 · #392. **A minor, not a patch**, because #381 raises where it used to accept |
| **0.1.x** | 0.1.8 macOS sizing on Tk 9 · 0.1.7 Tk 9 scroll contract · 0.1.6 seven form/field fixes · 0.1.5 boolean state reads · 0.1.4 · 0.1.3 · 0.1.2 · 0.1.1 · **0.1.0 STABLE** — public compose API FROZEN under SemVer (`bootstack.dev` excluded) |

**Also shipped, unreleased or entry-free:** **#407** (harness scene reset —
`conftest._region()` returned the root on a decorated App, so the scene reset had
been **a no-op for content widgets for the entire life of the shared-root
harness**; shared leg **215s → 56s**) · **#380** (CI, PR #451) · **#456** (PR #457
— `DataTable(context_menus=)` never reached the widget, and `on_row_right_click` is
now decoupled from it) · **#409** (PR #414, docs).

Pre-0.1.0 initiatives are also in the archive: hot reload, builder-function
scaffolds, the docs-IA restructure, splash screen, icon-DPI sizing, the navigation
API reshape, the layout redesign, undecorated window chrome, the media widget
suite, the field-family reviews, field validation redesign, and the API Reference
restructure.

---

## Carryover (deferred)

- **Reference docs examples** — LARGELY DONE (PR #103). Remaining: opportunistic
  enrichment of any still-thin reference page.
- **Docs build is warning-free** (PR #106). ⚠ **Keep it that way: incremental Sphinx
  builds MASK warnings** — always clean-build to verify. ⚠ **A default `-W` build
  does NOT catch a dangling py xref — only `-n` does.**
- **Visual theme builder** (Phase 5, near-ship — emits `bs.Theme(...)` code). **Do
  NOT build yet.**
