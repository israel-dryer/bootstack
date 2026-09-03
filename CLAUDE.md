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
| `RELEASE.md` (repo root) | **The complete release runbook** — cutting, publishing, verifying, and the manual fallback. Follow it rather than reconstructing the steps here |

⚠ **THIS FILE HAS BEEN SPLIT TWICE — 2026-07-30 and 2026-08-20 — AND THE SECOND
SPLIT WAS FORCED.** It had reached **~60,000 tokens**, over budget, because every
release from `0.2.2` to `0.3.2` accreted here instead of being archived when it
shipped. **Archive an entry THE DAY ITS RELEASE SHIPS.** If you are adding more
than a few lines about work that is finished, you are writing in the wrong file.

⚠ **A handoff artifact only survives if it is IN THE REPO.** The first split sat
untracked and nearly vanished; #379's `leakfix.patch` was saved to a per-session
temp `scratchpad/` and is genuinely gone.

### Reviewing changes

⚠ **The `PLAN.md`/`REVIEW.md` session-boundary sequence is RETIRED (maintainer, 2026-08-30), and `REVIEW-PROTOCOL.md` was DELETED with it (2026-09-02).** A plan is written for the **maintainer** to implement; a review runs in the **same session** as the work, since what is reviewed is their diff, not mine. Do not ask where `PLAN.md` is. What survives is below.

**A round is triggered by a non-empty `git diff <range> -- src/`, and nothing else.** Test-, probe- and docs-only commits are self-checked. ⚠ **Known GAP: `.github/` is none of those three**, so a CI workflow reads as no-round. Unresolved — raise it rather than deciding silently.

**Test code is reviewed on ONE axis — what defect can it let through.** Only **vacuity** (passes while the behavior is broken) and **false alarm** (fails while it is fine) are actionable. Diagnostics, wording, symmetry and probe ergonomics are **notes, never fixes**.

**Probes are instruments, not reviewed code.** A flake gets **one** fix attempt with a mechanism-reproducing control, then quarantine. Exception: a probe whose *conclusion* is cited as settled must be shown capable of finding something.

**And know when to stop.** `0.3.1` ran four rounds yielding 6/5/4/5 findings but only 3/5/1/2 real ones — round 2 existed only because round 1's fix was incomplete, and round 4 reviewed a **test-only** diff. **When a round returns mostly re-reports and out-of-scope pre-existing bugs, the branch is done and the rest are issues.** ⚠ **But a re-report is not automatically noise** — ask *what changed: the evidence, or the cost of acting?* `0.3.1` round 3 re-raised a finding whose evidence was unchanged but whose price had dropped to one argument, and it was rightly taken.

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

**Released: `0.4.1` on PyPI, tag `v0.4.1` (2026-08-30)** — *Signal writes and
clearing*, five entries (#481, #482, #484, #490, #491). Prior: `0.4.0`
(2026-08-29), `0.3.2` (2026-08-13), `0.3.1`, `0.3.0`, `0.2.3`, `0.2.2`, `0.2.1`,
`0.2.0`. **Full detail for every one of these is in
`docs/_dev/handoff-archive.md`** — do not re-derive it here.

✅ **`0.4.1` verified 11/11 by `development/verify_release.py 0.4.1`** — PyPI by
real download, the fix inside the wheel, the `idlelib`-blocked import with its
control, provenance, `NOTICE` placement, both release assets, and the chained
`docs.yml` run. ⚠ **Read its exit code without a pipe.**

⚠ **`v0.3.2` and `main` DIFFER BY DESIGN**, as `v0.3.1` did: the CHANGELOG was
reworded *after* the tag and the GitHub Release body edited to match with
`gh release edit --notes-file`. **THE TAG WAS NOT MOVED** — never move a tag a
release has already run on.

### ★ START HERE (2026-08-30) — **`0.4.1` SHIPPED. `## [Unreleased]` IS EMPTY. NOTHING IN FLIGHT.**

**`0.4.1 — Signal writes and clearing` released to PyPI, tag `v0.4.1`, 2026-08-30.**
Five entries, all on `0.4.x — Patch line`: #481, #482, #484, #490, #491. **The
milestone stays OPEN** — a rolling line does not close when a patch ships. **Read
the #482, #490 and #484 subsections below before touching the field-signal seam
again; between them they settle a question that has been re-opened three times.**

#### ⭐ #482 — `value` FOLLOWS A PROGRAMMATIC SIGNAL WRITE, AND `<<Change>>` MOVED WITH IT

**The fix:** `TextEntryPart._value` was re-derived only in `commit()`, at
FocusOut/Return — right for typing, wrong for a write the application made, where
there is no editing session to commit and no blur coming. It now re-derives when a
text change arrives while the widget does **not** hold keyboard focus. **Population
is FOUR widgets** (`TextField`, `PasswordField`, `PathField`, `SpinnerField`), not
the six the issue named.

⚠ **The path runs INSIDE the bound variable's own write trace, where Tcl suppresses
every other trace on that variable.** So it calls `_reparse()` — the extracted parse
half — and NOT `commit()`: a display-normalizing `textsignal.set()` there moves the
signal while the entry never repaints, and it never heals. **Do not "simplify"
`_reparse()` back into `commit()`.** That was round 1's blocker.

⚠⚠ **`<<Change>>` CHANGED, IN BOTH DIRECTIONS, AND THE MAINTAINER DECIDED TO SHIP IT
(2026-08-29). DO NOT RE-LITIGATE.** `_prev_changed_value` is snapshotted from
`_value` on FocusIn and compared on blur, so a `_value` that now follows the write
leaves nothing for the blur to find. Measured on all four widgets against `main`,
with controls:

| the user does, after a programmatic signal write | before | now |
|---|---|---|
| focuses and leaves, no edit | `<<Change>>` `('hello' → 'world')` | **nothing** |
| types the pre-write text back, leaves | nothing | **`<<Change>>` `('world' → 'hello')`** |

**One rule produces both rows: `<<Change>>` means the committed value differs from
what it was at focus-in.** The event that vanished was the application's own write
surfacing a cycle late, attributed to a user focus, and arriving only if the user
happened to touch the field. **Blast radius is the signal-write path ONLY** —
`field.value = x` and `Form.set()`, which writes through it, already set `_value`
and are untouched, as is every user edit. Pinned by
`test_the_deferred_change_on_a_later_focus_cycle_moves_with_value` and
`test_typing_the_pre_write_text_back_is_now_a_change`.

⚠ **The standing 2026-08-26 do-not-fix is UNCHANGED for the moment of the write** —
a programmatic set still emits no `<<Change>>` at all. The clean way to observe one
is to subscribe to the signal.

**Residual, stated and accepted:** a programmatic write while the field HAS focus
still lags. Indistinguishable from typing at this seam, identical on `main`, heals
on the next blur.

#### ⭐ #490 — `TextArea`/`CodeEditor` NOW HONOR `Signal.clear()`

`_on_signal_change` opened with `if new_value is not None`, and **the empty for a
signal no widget realizes as its own variable IS `None`** — so these two dropped
exactly the value a clear produces, while the entry-backed four never reached it
because their empty is a `str`. The tell that it was a defect and not a refusal:
binding the same signal to a `TextArea` **and** a `TextField` made the clear work,
because the second widget decided which empty the signal produced.

⚠ **Two things the one-line fix left behind, both measured, neither filed:** the new
`str(new_value or "")` blanks the widget for **any** falsy value, not just the empty
one (unreachable today — the type gate makes `set(0)` raise and `Signal(123)` refuse
to bind — so it is latent, not a bug); and **`_bind_signal` still carries the same
`if v is not None` guard** for the INITIAL apply, so the setter and the constructor
now disagree about what `None` means. Harmless today (an empty signal bound to a
widget with `value=` seeds from the widget, identically before and after).

⚠ **After a clear, the signal ends up `''` rather than `None`** — the widget writes
its now-empty text back — **but only when the document actually changed**; clear a
second time and it stays `None`. Both are falsy, which is the check #390's CHANGELOG
tells callers to use. **Deliberately left out of the CHANGELOG entry as noise for a
"was I affected?" reader.**

#### ⭐ #491 — `TextArea.insert()`/`append()` WROTE ALONGSIDE THE PLACEHOLDER. **SHIPPED in `0.4.1` (PR #505).**

Both reached `_internal._core.insert(...)` directly, so `_showing_placeholder` stayed
`True`: text landed on top of the placeholder, `value` kept returning `''`, and
`<<Input>>`/`<<Changed>>` stayed gated **for the field's whole life**, not one cycle.

⚠⚠ **`_hide_placeholder()` DELETES THE WHOLE DOCUMENT** — `_core.text.delete("1.0",
END)`. It is written for the one state where a placeholder IS showing, and **every
pre-existing caller guards it** (`_on_focus_in_placeholder`, the `value` setter).
Calling it unguarded turns `append()` into *replace everything*: measured,
`append("line2")` onto `"line1"` gave `'line2'` on all three non-placeholder arms.
**The fix is `if self._internal._showing_placeholder:`, not the call.**

⚠ **`CodeEditor` is genuinely unaffected** — a separate `PublicWidgetBase` subclass
with its own `insert`/`append`, and neither it nor its composite mentions
`placeholder`. Verified, not assumed.

**Pinned by `tests/widgets/public/test_textarea_insert_placeholder.py`, and no single
wrong implementation passes it:** against `main` the first four fail, against the
unguarded fix the last three do.

#### ⭐ #484 — A WIDGET-MADE SIGNAL CAN BE CLEARED. **SHIPPED in `0.4.1` (PR #506).**

`create_signal()` built every signal the framework makes for a widget with
`allow_empty=False`, so `.signal.clear()` raised and named a `Signal()` call the
caller never wrote. It now declares empty where the type has an empty member —
`isinstance(default_value, (str, set))`, mirroring `Signal._empty_value()`'s own
rule. **That is the whole fix**, and it reaches the four entry-backed text fields.

⚠⚠ **DO NOT "simplify" it to an unconditional `allow_empty=True`.** #390's floor
refuses to bind an empty-capable signal to a `Slider` or `Checkbox`, so a blanket
default makes **every slider and checkbox fail on construction**. Pinned by
`test_both_refusing_widgets_still_construct_and_expose_a_readable_signal`.

⚠ **THE PLAN'S MECHANISM SECTION WAS WRONG AND THE ARCHIVED COPY STILL SAYS SO:**
it claims both lazy paths funnel through `create_signal()`, so gating it "reaches
all six widgets." It reaches **five**. `Slider` is a canvas `tk.Frame` composite,
not a `SignalMixin`/ttk widget — it builds its own `Signal` eagerly at
`slider/slider.py:127,134`, and `RangeSlider` at `rangeslider.py:129,135,141,147`.
Change 1 hid this because a bare `Signal(0.0)` and the gated one are identical for
a float.

⚠ **An ownership flag was built, measured, and DELIBERATELY DROPPED.** A private
`Signal._widget_owned` set in `create_signal()`, branched on in `set()`'s `None`
guard, gave `Slider`/`Checkbox` their own sentence — but it taught `Signal` a
notion of provenance it otherwise has no use for, and it needed six slider call
sites to reach. **The shipped message is ONE sentence for both owners**, carrying
both ways out. Pinned by `test_one_sentence_serves_both_owners`, which fails if a
branch is reintroduced. **Do not re-propose the flag.**

⚠ **`field.value` reads `None` after a clear while the signal reads `''` — this is
PRE-EXISTING, not #484's doing.** Measured against `main`: the shipped
`TextField.clear()` already produced exactly that state. #484's correcting comment
calls it "already filed" but names no issue, and none was found.

**`0.4.0 — Signal binding on fields` released to PyPI, tag `v0.4.0`, 2026-08-29.**
13 issues: #390, #444, #449, #456, #458, #459, #460, #461, #465, #467, #472, #476,
#486, plus the unmilestoned chore PRs #492/#493/#494. Milestone closed.

**Its detail is in `docs/_dev/handoff-archive.md`** under the 2026-08-29 split, and
each branch's `PLAN.md`/`REVIEW.md` is at `development/plan-<issue>-<slug>.md` and
`development/review-<issue>-<slug>.md`. **Read those before re-deriving anything.**

✅ **Release verified 11/11 by `development/verify_release.py 0.4.0`** — reusable,
takes the version as an argument. Its control run against `0.3.2` fails exactly one
check (the #467 fix in the wheel), which is what shows it discriminates. ⚠ **Read
its exit code without a pipe** — the first control run was piped to `tail` and
reported `EXIT=0` over three failures.

#### ⚠ WHAT #467's TWO ROUNDS LEFT BEHIND

**Round 2's finding is the durable one: all three of its findings were regressions
introduced by ROUND 1's OWN FIX STEP**, measured against the branch's pre-fix commit
rather than against `main`. A fix step is code, and the next round must scope its
diff to the fix, not the branch.

⚠ **A demo found round 1's second blocker after a green suite AND a written review
had both missed it** — a field holding `6` reporting *"must exceed 5"*, because the
predicate had crashed rather than judged. **Drive the thing by hand before calling a
round clean.** Same lesson #486 paid for.

⚠ **`_uncheckable_message` runs INSIDE the `except` block that absorbs the func's
exception, so anything it raises escapes the guard.** That is why its body is
wrapped. Do not flatten it.

⚠⚠ **NOTHING IS OPEN FROM THOSE ROUNDS ANY MORE. ALL THREE SURVIVORS WERE CLOSED
`not planned` — #497, #499 AND #500 — verified against `gh` 2026-08-29.** This file
listed them as open work for days after they were not. **#500's closing reason is the
one to carry forward**, verbatim: it guards against an author passing a non-callable
`func` or a bound of the wrong type, *"their own broken code, which the framework
cannot sensibly rescue."* **#467 itself was real — a field silently stopped validating
and the user saw a dead form — this residue is not.** That also retires the #495
residue #500 was carrying. **Do not re-file any of the three.**

⚠⚠ **#479 WAS CLOSED TWICE BY PROSE, THE SECOND TIME BY THE COMMIT DOCUMENTING THE
FIRST.** `0e31f7ad`'s body quotes PR #489's phrase *"which closes #479's shape"* —
and GitHub's parser re-triggered on the quotation, 61 seconds after the reopen.
**The trap is not limited to PR bodies: a commit message on the default branch
closes issues the same way, and QUOTING the bad phrase re-arms it.** Write the
keyword and the number apart. Reopened 2026-08-29.
#### ⭐ #477 — COLLAPSE THE `_impl` LAYER BEFORE 1.0. **Maintainer's framing, filed 2026-08-26, unmilestoned.**

⏭ **THE `_windowingsystem` DUPLICATION BELONGS HERE — measured 2026-08-29, not yet filed on the issue.** Two private twins with the same body (`_runtime/wheel.py:38`, `widgets/toast.py:25`) plus **18 raw `tk.call("tk", "windowingsystem")` sites**; **8 of the 18 cache the result as `self.winsys` at construction**, so consolidating changes *when* the probe runs, not just where. ⚠ **Their fallbacks DISAGREE and one is load-bearing**: wheel returns `""` on failure (nothing equals it, so it degrades to the generic path — correct), toast returns `"win32"` (**asserts Windows**, and that drives `_resolve_corner`'s platform default). **Deliberately left out of PRs #492/#493/#494.**

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

#### STATE OF THE WORLD

| | |
|---|---|
| `main` | **at the `v0.4.1` tag** — the `Release 0.4.1` bump commit, on top of the `docs(changelog):` promotion. ⚠ **A row cannot name its own SHA — verify with `git rev-parse origin/main`** |
| branches | **NONE, local or remote, beyond `main`** — #484's merged as PR #506 and #491's as PR #505. Verify with `git branch -a` before trusting this |
| root of `main` | **no `PLAN.md`, no `REVIEW.md`, and the sequence that produced them is RETIRED** (maintainer, 2026-08-30). A plan I write is for the **maintainer** to implement; a review runs in the **same session** as the work, since what is reviewed is their diff, not mine. **`REVIEW-PROTOCOL.md` was DELETED and "Reviewing changes" rewritten to match, 2026-09-02** — the contradiction is gone. Do not ask where `PLAN.md` is, and do not read its absence as the rule slipping |
| released | **`0.4.1`** on PyPI, tag `v0.4.1`. **`## [Unreleased]` is EMPTY** — the next fix opens it |
| next release | **nothing scheduled and nothing queued.** `0.4.x — Patch line` is the largest open milestone at 6, and stays open |
| CI | `ci.yml` green, 5 jobs. **No macOS leg** (#452) |
| suite, `main` | **Windows `1756 / 22`, 33 legs, exit 0**, measured 2026-08-30 at `02593bd2`, the commit `v0.4.1` was cut from, `py -3.12`, both deps present. ⚠ **macOS is `1699 / 33` at the #467 merge and is now SEVEN merges stale.** The two are NOT comparable |
| open milestones | **10** — `0.4.0` closed on release; `0.4.x` did NOT. Verified against `gh` 2026-08-30 |
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
| — | ~~`0.4.0 — Signal binding on fields`~~ — **SHIPPED 2026-08-29, milestone CLOSED.** 13 issues. Detail in the archive |  |
| 1 | **`0.5.0 — Strictness and value types`** — #383, #369, #408, #416, #445, #479. ⚠ **#481 left for `0.4.x` on 2026-08-29 AND SHIPPED IN `0.4.1` — that is an exception to this milestone's rule, not a breach of it.** It raises where the framework accepted, which is the membership rule (and is why **#445** sits here), but **its break is unreachable by working code**: every call site it now rejects had built a signal that could never hold a value, so every later `set()` already raised. The batching rationale — one migration instead of four — buys a user nothing when there is no migration. **Do not read this as the rule slipping, and do not move #445 on the strength of it.** ⚠ **#383 keeps only gaps 1 and 2 (bad *values*)**; gap 3 (unknown *names*) shipped as #472. ⚠⚠ **#500 IS CLOSED, `not planned` (maintainer, 2026-08-29) — do NOT re-file it.** Its reason, verbatim: it guards against an author passing a non-callable `func` or a bound of the wrong type, *"their own broken code, which the framework cannot sensibly rescue."* **#467 itself was real — a field silently stopped validating — this residue is not.** That disposition also retires the #495 residue #500 was carrying. ⚠ **#479 does NOT meet this milestone's membership rule — that is deliberate, do not "correct" it**; placement is the maintainer's call, not the rule's | 6 |
| 2 | **`0.6.0 — Form, signals, and composite authoring`** — #389, #412, #415 | 3 |
| 3 | **`0.7.0 — Guided flows`** — #311, #312 | 2 |
| 4 | **`0.8.0 — Power-user interactions`** — #315, #316 | 2 |
| 5 | **`0.9.0 — Structured editing`** — #192, #314 | 2 |
| — | **`Tcl/Tk 9 support`** (unnumbered, blocked on hardware) — #376, #378 | 2 |
| — | **`Hot reload (provisional)`** (unnumbered, outside the freeze) — #322, #328 | 2 |
| — | **`Additions awaiting a minor`** (unnumbered, rides any minor) — #208, #317, #352 | 3 |
| — | **`Wrapper and internal parity`** (unnumbered — findings will span compatibility categories, so no release can be promised until they exist) — **#466**, the durable parameter-level guard. ⚠ **#466 needs THREE amendments, all recorded on the issue**: it is parameter-level so it cannot see a missing method or property; the 84 unanalysed params are a hole, not coverage; and it needs an AST check that every `bs.<Widget>(kw=…)` in `docs/**/*.py` names a real parameter. ⚠ **#477 is adjacent but NOT on this milestone, deliberately** — this holds parity *defects*; #477 asks whether the internal should exist. Do not fold them | 1 |
| — | **`0.4.x — Patch line`** (rolling, **FIXES ONLY**) — #207, #422, #447, #468, #469, #488. Verified against `gh` 2026-08-30. Cut 2026-08-27; **it did NOT close when `0.4.1` shipped, and must not** — renaming a turned-over line would relabel shipped work. ⚠ **Its five closed issues — #481, #482, #484, #490, #491 — ARE `0.4.1`.** ⚠ **Sweep a turning-over line with `--state all`** — the 2026-08-27 turnover missed #449 and #456 because both were already closed, and neither could ever have shipped as a patch | 6 |

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

**FIVE UNMILESTONED OPEN ISSUES — #431, #436, #452, #474, #477.** ⚠⚠ **THIS LIST SAID FOURTEEN UNTIL 2026-08-29 AND NINE OF THOSE WERE WRONG — run the command below, do not edit the count.** #482, #490, #483 and #455 all CLOSED, and **#468, #469, #484, #488 and #491 were all moved onto `0.4.x — Patch line`** without this file being swept. ⚠ **The list moved TWICE during the 2026-08-29 sweep itself** — #468/#469 were unmilestoned when the sweep started and milestoned by the time it finished, so a number in this paragraph is a snapshot, not a fact. ⚠ **#483 CLOSED `not planned` 2026-08-29** — it was already recorded here as documentation rather than a defect, and the toolkit measurement behind that is below; **do not re-open it in either direction.** ⚠ **#488 is the one to read before touching `TextArea` teardown: `_MultilineCore._on_destroy` guards on `event.widget is not self` and the only `<Destroy>` it receives names the inner `Text`, so the ENTIRE teardown block has never run** — including the wheel `unbind_class` sweep, so every `TextArea` and `CodeEditor` ever built leaves bindings on a shared bindtag. **#486 released only the signal hooks, #490 only the clear, and #491 only the placeholder on `insert`/`append`. Do not read any of the three as the fix.** ⚠ **#477 is the `_impl` collapse pass, filed 2026-08-26 — see the ★ section; it is a PRE-1.0 goal, not a backlog nicety.** ⚠ **#468 and #469 both came out of #465's review**; #469 is the `when="tail"` hazard. **Still exactly these five, re-verified against `gh` 2026-08-30 after `0.4.1`.** Verify rather than counting by hand:
`gh issue list --state open --json number,milestone --jq '[.[]|select(.milestone==null)]'`

- **#431 is OPEN ON PURPOSE AND WAITING ON A DECISION, not on work.** Its fix
  landed with #434's, but on aqua it **SKIPS** — macOS has no NumLock modifier for
  `Mod1` to carry. The test cannot be made meaningful there and now says so out
  loud. **That resolves the failure; whether it resolves the issue is a scope
  call.** ⚠ And it is **UNVERIFIED on a real Aqua build** — fold into the #452 trip.
- **#436** — adopt `versionadded` across the public API, because the docs site
  serves ONE version and a reader cannot tell which release an API needs. Carries
  one undecided question: retroactive to `0.2.x`, or forward-only?
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

⚠⚠ **TWO FIGURES, ONE PER BOX. They are NOT comparable and neither is the
other's baseline** — platform gating differs. Say which box you mean.

| box | measured | when |
|---|---|---|
| **macOS** | **`1699 passed / 33 skipped`**, 33 legs, exit 0 | 2026-08-29 at the #467 merge, `.venv/bin/python` 3.14.0, matplotlib present, **pandas ABSENT** |
| **Windows** | **`1756 / 22`**, 33 legs, exit 0 | 2026-08-30 at `02593bd2`, the commit `v0.4.1` was cut from, `py -3.12`, both deps present |

⚠ **`pandas` is ABSENT on the macOS box**, so its data leg runs the two tests that
exist only when pandas is missing (`125 / 4` absent vs `123 / 6` present — a
documented environmental pair, not a discrepancy). `matplotlib` matters more:
`test_chart.py` is **44 tests** behind a module-level `importorskip`. Check both
before re-flagging a total.

⚠ **`tests/widgets/*.py` NEVER RUNS** — `testpaths` is `tests/cli`,
`tests/widgets/public`, `tests/data`; 12 files / 25 tests under `tests/widgets/`
are collected by nothing. Same class: `tests/test_public_surface.py` (166 tests)
and **`tests/signals/test_signal.py` (22 tests)**, neither run by `run_gui.py`.
All pass run directly. Folded into **#380**; CI runs the first two.

**The three checks, in order of what they actually prove:**

1. **The ceiling.** `passed + skipped` cannot exceed the selected count:
   `pytest <paths> -m "not isolated" --collect-only -q | tail -2`.
2. ⚠ **But it CAN legitimately exceed it by the collection-time skips** — a
   module-level skip is reported in the summary while never being selected.
   **Read the collection line before concluding a total is impossible.**
3. ⚠ **Self-consistency proves the run summed correctly, NOT that it selected the
   right population.** A wrong ceiling reconciles just as neatly — that is how the
   seventh error got through. **Bound the movement instead:**
   `git diff --stat <baseline>..HEAD -- tests/` says how much the count is ALLOWED
   to have changed, and it is one command. It is the check that catches what a
   self-consistent-but-wrong total does not.

**Record the DATE and the COMMIT beside any count, or don't record it.** Sum the
legs yourself — `run_gui.py` prints no aggregate. ⚠ **A first pass once summed the
skips by matching the `1 skipped` INSIDE a collection line — sum the per-leg
summary lines only.**

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
  #444 SHIPPED on `0.4.0` (PR #485, 2026-08-28)** — do not read this pair as two
  open patch-line items any more.
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

- ~~`project_capabilities_relevance`~~ — **SETTLED AND SHIPPED 2026-08-29 (PR #494).
  The memory file is stale; update or delete it.** It was right: the package was
  redundant. **Measured before acting — 66 of 91 methods were pure pass-throughs**
  and ~12 more only re-derived a default `tkinter` already had. `_core/capabilities/`
  no longer exists; `signals.py` and `localization.py` moved up to `_core/` (the
  first renamed `signal_binding.py`), and 13 survivors folded into
  `_core/mixins/widget.py`. **See the ★ section.**
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
  is **FIXED AND MERGED** (PR #485, 2026-08-28). *"Has no live properties"* is false: `title` and `result`
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

⏭ **THE FULL PROCEDURE LIVES IN `RELEASE.md` (repo root) — follow it, do not reconstruct it here.** It carries the eight steps, the automation's actual behavior, the manual-publish fallback for an Actions outage, and every trap this project has paid for. **Do not copy any of it back into this file**; two copies drift and the wrong one gets followed.

**What you need at the moment you write a FIX**, rather than at release time:

- A fix commit writes under `## [Unreleased]`; the promotion commit renames the heading and adds the `[X.Y.Z]:` link definition.
- ⚠ **An entry earns its place by being REACHABLE from public API.** A CHANGELOG is read by someone asking "was I affected?", so an entry for an unreachable defect is a false positive. `0.2.1` deliberately omitted #397/#401 and `0.2.0` omitted #387 on those grounds; #380, #407, #433 and #434 shipped with no entry because CI and test harness are not reachable by any user. **Do not "fix" those absences.** Check `__all__` and the public event registry before writing the bullet — **and say so in the commit message, since that is where the omitted work stays documented.**
- ⚠ **A CHANGELOG claim about PRIOR behavior must be checked against the OLD code, not against the fix.** The #456 bullet said a misspelled value *"previously turned both menus off silently"*; it did the **opposite**. `git show main:<file>` settles it in one command.
- ⚠ **Write entries ONE PARAGRAPH PER LINE — do not hard-wrap.** The section is lifted verbatim into the GitHub Release body, which renders a soft line break as a visible one. **Older sections are left wrapped — do not reformat shipped history.** Same rule for PR bodies, issue bodies, and review comments.
- ⚠ **Adding public surface is a MINOR even when nothing breaks** — the project committed to SemVer at `0.1.0`, so someone upgrading `0.2.1 → 0.2.2` should be able to assume no new API arrived. **BUT THE RULE IS ONE-DIRECTIONAL:** an addition *requires* a minor; a minor does *not* require additions and is free to carry as many plain fixes as it likes (`0.3.0` carried two additions and **six fixes**). **So when a minor is being cut anyway, ask what else is ready rather than parking fixes out of habit** — and for a fix, ask whether it needs a minor at all.

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

⚠ **Verified 2026-08-29: NO branches exist, local or remote, beyond `main`.** The
three stale refs this file listed for weeks are all deleted; do not re-add them
from memory.

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
  root-bound × instances = thousands of redraws. **Define `_bs_apply_theme(self)`**
  and `Style.apply_theme_walk` calls it once, resolving visibility at apply time.
  ⚠⚠ **THE STD `Publisher` AND `_enable_theme_repaint` ARE BOTH GONE** — the
  publisher was deleted 2026-08-28 (PR #492) and `_enable_theme_repaint` well
  before it. **`docs/_dev/theme-repaint-architecture.md` is the live account; read
  it rather than this bullet if you are touching a painter.**
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
├── _core/       infrastructure (signal_binding, localization, mixins, images, capture)
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
| **0.4.1** (2026-08-30) | *Signal writes and clearing*. **Five entries, all patch-line** — #481 (`bs.Signal(None)` now raises at construction, `map()` included — the one `### Changed` entry) · #482 (a field's `value` follows a programmatic signal write) · #484 (the signal a text field makes for you can be cleared) · #490 (`TextArea`/`CodeEditor` honor `Signal.clear()`) · #491 (`insert()`/`append()` drop the placeholder first). ⚠ **No `### Added` section — that is the test that let it be a patch.** Verified 11/11 |
| **0.4.0** (2026-08-29) | *Signal binding on fields*. **13 issues** — #390 (`Signal(…, allow_empty=True)`) · #444 (a modal `Window` never handed the grab back) · #456 · #458 / #461 (a `Select`/`SelectButton` signal bound the LABEL, not the value) · #459 · #460 · #465 (a rule on a `Select` had nowhere to report) · #467 (a `custom` rule's raise escaped into the event loop) · #472 (an unknown keyword now RAISES) · #476 · #486 (`TextArea`/`CodeEditor` bound `textsignal=` one way only). ⚠ **Two entries break running code: #472 and #461** — but only #461 breaks code that WORKED; #472 only turns a silent no-op into a message |
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
