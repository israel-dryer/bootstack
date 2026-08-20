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

### ★ START HERE (2026-08-20) — the wrapper audit RAN and MERGED (PR #464). Next: the maintainer's four decisions.

**⏭ THE MEASUREMENT PASS IS DONE AND FILED NOTHING NEW.** Every real finding lands on an issue that already existed. **The pass's product is the MEASUREMENT those issues were missing** — read `development/wrapper-parameter-audit-463.md` before touching any of them, and do not re-derive it. The instrument is `development/probe_wrapper_parameter_delta.py` (arms `scan`, `control`, `leftovers`, `roundtrip`); **re-run it rather than reading the wrappers again.**

| mode | what | measured | verdict |
|---|---|---|---|
| 1 | never forwarded | **0** | clean |
| 2 | wrong destination | 100 renamed destinations | **1 defect — #461.** The other 99 are `_impl` spelling |
| 3 | swallowed as a layout key | **40 of 52 wrappers** | **THE finding.** Posted on #383 as its gap 3 |
| 4 | accepted then ignored | not statically decidable | 1 weak candidate (`Carousel.index`) |
| 5 | the type lies | **8** | **= #460's population exactly**, `TextArea` cleared |

- ⚠ **MODE 2 CAME OUT ESSENTIALLY CLEAN, AND THAT IS A NEGATIVE RESULT WORTH SOMETHING ONLY BECAUSE THE CONTROLS PASS** — the same scan finds #461 on `main` and finds #458 at the pre-fix commit. **The wrapper layer's forwarding is in better shape than the recent defect run suggested; the exposure is strictness (mode 3), not mis-wiring.**
- **What got 100 mode-2 rows down to 1 was DIVERGENCE**, not the rename itself: a public name that lands on a *different* internal key in some other wrapper. `max_value -> maxvalue` is ordinary; `signal -> textsignal` when nine siblings say `signal` is #461. **Reuse that ranking, don't re-invent one.**
- ⚠ **#383 GAP 3 IS NO LONGER BLOCKED.** Its open question was *"the shared split seam needs the wrappers that legitimately forward `**kwargs` counted first."* Counted: **40 drop, 5 reject, 5 forward, 2 never split.** And **the fix already ships** — `_BooleanControlBase.__init__` has the six-line guard covering five public widgets. Gap 3 needs no design, only placement.
- ⚠ **`Select`, `DateField`, `NumberField` and `TimeField` LOOK strict and are NOT.** They carry an `if "textsignal" in kwargs: raise` guard, which rejects **one known name** and says nothing about the rest. **A specific-key guard is not a leftover guard** — the audit's own static pass credited all four with rejecting until construction disproved it.
- ⚠ **NOT COVERED, AND NOT CLEAN: 84 params across `AppShell` (31), `Workbench` (34), `ThemeToggle`, `Notification`, `Snackbar`.** They build no internal in their own `__init__`. `App`, `Window` and `Splash` were in that list until the probe learned the alias hop.
- ⚠ **THE SURFACE FIGURE MOVED AND BOTH NUMBERS ARE RIGHT.** `PLAN.md` says **77 classes / 890 params / 62 catch-alls**; the scan reports **65 / 810 / 52**. The plan counted every class in the wrapper modules; the scan counts only what a public `__all__` exports, skipping 17. **Different populations, not a discrepancy** — say which you mean.

**⏭ THE PASS IS OVER; WHAT IS LEFT IS FOUR MAINTAINER DECISIONS, none of which a session should make alone:**

1. **Mode 3: shared seam or per-wrapper?** A seam is one change, but **a blanket guard breaks the five wrappers that forward leftovers on purpose** (Chart, MenuButton, Picture, StatusBar, Toolbar). `App`/`Window` never split at all — a third shape.
2. ⚠ **#460's fix vs its milestone.** Dropping `| None` from eight annotations **RETYPES WHAT A PUBLIC PROPERTY RETURNS**, which is `0.5.0`'s membership rule verbatim. #460 sits on **`0.4.0`**, which it gates. **Settle this before `0.4.0` is cut.**
3. **#463's disposition** — close with the table as its artifact, or re-scope it into the durable guard (below). Both are on the issue as a comment.
4. **Whether the `_impl` naming inconsistency gets an issue at all** (`readonly`/`read_only`, `maxvalue`/`maximum`, `items`/`options`/`values`, `override_redirect`/`overrideredirect`). **No user can see it**; the plan scoped `_impl` out.

**The durable guard is the half that does not decay, and it is DELIBERATELY NOT BUILT.** A parameter-level `test_public_surface.py`-shaped test written **to these five modes**. It needed the taxonomy to exist first; it does now. ⚠ **It must not inherit the existing file's blind spot** (that one gates the top-level *name set* and never asserts a submodule is unreachable as `bs.*` — which is how the `bs.events.X` drift survived two months), **and it must treat those 84 unanalysed params as a hole, not as coverage.**

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
| `main` | **`51a44c1c`** — PR #464 merged 2026-08-20 (the wrapper audit). `PLAN.md` archived to `development/plan-463-wrapper-audit.md` and recreated as an explicit empty |
| branches | **NONE in flight.** `audit/wrapper-parameter-delta` merged and deleted local + remote (head **`41828ba2`**); `fix/select-signal-value-458` merged earlier (head **`51d09f6e`**). ⚠ **Both are squash/merge history now, so NON-ANCESTOR ≠ UNMERGED** — check the recorded head SHAs against `origin/main`, not the branch names |
| root of `main` | **`PLAN.md` PRESENT and DELIBERATELY EMPTY** — it says no implementation is planned and names the four decisions instead. **NO `REVIEW.md`** — correct, and **no round was owed**: gate 1 fires on a non-empty `git diff -- src/` and nothing else, and #464's was empty |
| released | `0.3.2`. **`## [Unreleased]` carries #456 and #458** and is what `0.4.0` will promote |
| next release | **`0.4.0 — Signal binding on fields`** — #458 done, **#459, #460, #461 still open.** The milestone cannot close yet |
| CI | `ci.yml` green on `main`, 5 jobs. **No macOS leg** (#452) |
| suite, `main` | **1500 passed / 22 skipped, 33 legs, exit 0** — measured 2026-08-20, Windows box, `py -3.12`. ⚠ **See the environmental note below before comparing this to anything older** |
| open milestones | **11** — verified against `gh` 2026-08-20, and they agree 1:1 with the table below. `Wrapper and internal parity` is the new one |

⚠ **A NEW ENVIRONMENTAL PAIR — AND IT IS BIGGER THAN THE PANDAS ONE THIS FILE ALREADY DOCUMENTS.** The Windows box now has **matplotlib** installed, so **`test_chart.py` (44 tests behind a module-level `pytest.importorskip("matplotlib")`) COLLECTS instead of being the collection-time skip.** `pandas` arrived too. Against the `1458 / 21` recorded on 2026-08-19:

```
1458 + 44 (test_chart) - 2 (data leg 125/4 -> 123/6) = 1500 passed
  21 -  1 (the collection-time skip is gone) + 2 (pandas)  =   22 skipped
```

Exact on both, and `git diff --stat <base>..HEAD -- tests/` confirms no test was added. **So a session measuring `1500 / 22` on this box is seeing the right number, and one measuring `1458 / 21` has neither dep installed.** Check with `py -3.12 -c "import matplotlib"` and `import pandas` before re-flagging either. ⚠ **This is the eighth count discrepancy this file has had to reconcile, and the first that was NOT an error** — it reconciled because the collection line was read, not because the total looked plausible.

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
| **#449** | `test_select_change_event_value_space` pins an exact event list against an async change, ~1 in 10 full runs | **OPEN.** Two candidate causes RULED OUT by measurement: it is **not** a `Select` emitting at construction, and **not** an event leaked by the reset destroying a widget. Remaining hypothesis — stale bindings surviving destroy while Tk recycles path names — is **UNTESTED** |
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
| 1 | **`0.4.0 — Signal binding on fields`** — ~~#458~~ (merged 2026-08-20), **#459, #460, #461**. Cut 2026-08-19; the next release out the door | 3 |
| 2 | **`0.5.0 — Strictness and value types`** — #383, #369, #408, #416 | 4 |
| 3 | **`0.6.0 — Form, signals, and composite authoring`** — #390, #389, #412, #415 | 4 |
| 4 | **`0.7.0 — Guided flows`** — #311, #312 | 2 |
| 5 | **`0.8.0 — Power-user interactions`** — #315, #316 | 2 |
| 6 | **`0.9.0 — Structured editing`** — #192, #314 | 2 |
| — | **`Tcl/Tk 9 support`** (unnumbered, blocked on hardware) — #376, #378 | 2 |
| — | **`Hot reload (provisional)`** (unnumbered, outside the freeze) — #322, #328 | 2 |
| — | **`Additions awaiting a minor`** (unnumbered, rides any minor) — #208, #317, #352 | 3 |
| — | **`Wrapper and internal parity`** (unnumbered — its findings will span compatibility categories, so no release can be promised until they exist) — **#463**. Cut 2026-08-20. ⚠ **The measurement pass RAN the same day (PR #464) and filed NOTHING NEW** — its findings landed on #383/#460/#461. What is left on #463 is a disposition call, not work | 1 |
| — | **`0.3.x — Patch line`** (rolling, **FIXES ONLY**) — #207, #422, #444, #445, #447, #449. Reads `open=6 closed=2`. It is rolling, so it does **NOT** close when a patch ships | 6 |

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

**FOUR UNMILESTONED OPEN ISSUES — #431, #436, #452, #455.** All four predate the
current work. Verify rather than counting by hand:
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

**AUTHORITATIVE — measured 2026-08-20 on `main` at `41c8bad1`**, Windows box,
`py -3.12 tests/run_gui.py`, **exit 0, 33 legs**, **`matplotlib` and `pandas`
BOTH PRESENT**:

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

**#390 is the exception to milestone order and can be taken at ANY time — it is a
DECISION, not work.** Should signals model emptiness at all? Cheapest item on the
board and the largest unblock, since it gates #389 shipping *whole*. **The analysis
is COMPLETE — it needs an answer, not more analysis**, and the maintainer is
actively evaluating (discussion #386), so do not re-derive it or ask the reporter
to weigh in.

`Signal.set(None)` raises unconditionally (`signal.py:248` — strictly monomorphic,
type inferred from the seed). **Four decisions, in order:**

1. *Do it at all?*
2. *Declared or automatic?* — recommend **declared** (`Signal(v, nullable=True)`).
   Automatic-by-mode cannot cover `int` and is not safe to lean on: `Signal(0)` is
   Python-authoritative only *while unrealized*, so the moment anything touches
   `.var`, `__call__` starts reading the IntVar and a stored `None` is lost.
3. *What happens to a non-nullable signal asked to go empty?* — recommend a public
   `Signal.nullable` so `ValueSignalMixin` skips rather than crashing
   `Form.clear()`.
4. *What does `map()` do over a nullable signal?* — it calls the transform
   unconditionally and infers the derived type from the first result, so a `None`
   source breaks the **documented** Date/Time pattern.

**No existing code is at risk either way** — `set(None)` raises today, so nothing
can currently receive it. ⚠ **KEY MEASURED FINDING: the dividing line is
attached-vs-not, not object-vs-native.** `NumberField(signal=)` /
`DateField(signal=)` are **unrealized** — `ValueSignalMixin` syncs in pure Python
and never touches `.var`, so for a number field's value signal **there is no IntVar
at all**. `Checkbox(signal=)` and `TextField(textsignal=)` **are** the widget's
`variable`/`textvariable` — there `None` either raises (`IntVar`) or **silently
corrupts**: `StringVar.set(None)` stores the literal `'None'`, the widget displays
it, and every subscriber gets the 4-character string. **That is why a blanket guard
relaxation must not ship.** ⚠ **Per-type "empty" values were CONSIDERED and
REJECTED** — `empty(int) = 0` contradicts the shipped `NumberField.clear()`
decision, `empty(bool) = False` collapses tristate (#358), `date` has only a
sentinel indistinguishable from data, and it makes emptiness type-dependent at
every call site.

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
  - ⚠ **#383 gained a THIRD gap, and it is now MEASURED — read the comment on the
    issue (2026-08-20) before re-deriving any of this.** The two gaps in its body
    are about bad **values**; this one is about unknown **names** —
    `bs.TextField(bogus_xyz=1)` constructs silently while the internal
    `TextEntry(None, bogus_xyz=1)` raises `TclError: unknown option "-bogus_xyz"`,
    so **the public layer is the less strict of the two** — both halves measured,
    not inferred. ⚠ **It does NOT reuse `validate_choice`**; the name never
    reaches a validator. **THE BLOCKER IS GONE:** of the 52 wrappers with a
    catch-all, **40 drop / 5 reject / 5 forward / 2 never split**, and the guard
    already ships in `_BooleanControlBase.__init__` at six lines. What is left is
    placement — and ⚠ **a blanket seam guard breaks the five that forward on
    purpose** (Chart, MenuButton, Picture, StatusBar, Toolbar), while `App` and
    `Window` never split at all.
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
- **#444 / #445** — both pre-existing, filed out of `0.3.1` round 3, on the patch
  line. #444: a modal `bs.Window` never restores the grab it took, so a dialog
  underneath it loses its modality (`_runtime/toplevel.py`). #445: `attach()` drops
  legacy layout kwargs on a grid cell while rejecting them on a flex child.
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
  internal Toplevel, has no live properties (`title`/`size`/`topmost` are
  construction-only), and never releases the modal grab. Own branch.
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
- ⚠ **Do not synthesize keys in the shared-root suite.** Drive the routine the key
  is bound to (`ttk::treeview::ToggleFocus`). The key-to-routine mapping is the
  toolkit's binding table, not ours.
- **Tk REJECTS `event_generate("<Double-1>")`** — `Double` is a binding pattern, not
  an event type. Two presses is the only way. ⚠ **And synthesized events default to
  `time=0` while Tk decides `Double` off the event clock**, so supply an explicit
  `time=`.
- ⚠ **`winfo_ismapped()` on a destroyed widget RAISES `TclError: bad window path
  name` — it does not return 0.**
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
