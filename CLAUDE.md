# bootstack — Claude Handoff

## Project overview

bootstack is a batteries-included Python desktop UI framework. It is **not** advertised as a Tkinter wrapper — the goal is to abstract Tkinter away entirely, so its warts, naming conventions and legacy API are invisible to the user. Widget names, arguments, methods and events are designed for modern Python, not for compatibility with the raw tk/ttk surface.

**Design philosophy:** opinionated, configurable within a reasonable range, nothing to something fast. The user should never need to `import tkinter`.

**Branch strategy:** `feat/*` / `fix/*` off `main`; PRs go to `main`.

### Where things live — read before adding to this file

This file holds **only what is OPEN plus the standing rules.**

| File | Holds |
|---|---|
| `docs/_dev/handoff-archive.md` | **Every shipped initiative** — root causes, decisions, gotchas — indexed by issue/PR number. **Read the entry before touching an area it covers** |
| `docs/_dev/theme-repaint-architecture.md` | The live account of theme repaint (the walk, container-show triggers, surfaces) |
| `docs/_dev/docs-authoring-patterns.md` | Docs IA, API Reference & Guide page recipes, autosummary templates, screenshot patterns |
| `docs/_dev/widget-review-and-docs-standards.md` | The widget review + docs checklist |
| `RELEASE.md` | **The complete release runbook.** Follow it; never reconstruct it here |

- **Archive an entry THE DAY ITS RELEASE SHIPS.** More than a few lines about finished work means you are writing in the wrong file. This file was force-split twice for ignoring that.
- **`development/` holds only what serves OPEN work** (maintainer, 2026-09-11) — plans (`plan-<issue>-<slug>.md`), probes, demos and handoff notes. Delete them when the work ships; git history keeps the rest. `verify_release.py` is the permanent exception.
- ⚠ **`src/` and `tests/` never cite `development/` files** — no "measured in `development/probe_…`". State the finding itself, or nothing.
- **A handoff artifact survives only if it is IN THE REPO** — never in a session scratchpad.

### Reviewing changes

The `PLAN.md`/`REVIEW.md` session-boundary sequence is **retired**. A plan is written for the **maintainer** to implement; a review runs in the **same session** as the work.

- **A round is triggered by a non-empty `git diff <range> -- src/`, and nothing else.** Test-, probe- and docs-only changes are self-checked. ⚠ Known gap: `.github/` is none of those, so a CI workflow reads as no-round — raise it rather than deciding silently.
- **Test code is reviewed on ONE axis — what defect can it let through.** Only **vacuity** (passes while broken) and **false alarm** (fails while fine) are actionable; wording, symmetry and diagnostics are notes.
- **Keep tests minimal** (maintainer, 2026-09-11): one test per defect plus the preconditions that stop it passing vacuously. Controls that prove a test discriminates are run once and cited in the commit, not kept in the suite.
- **Probes are instruments, not reviewed code.** A flake gets one fix attempt with a mechanism-reproducing control, then quarantine. A probe whose *conclusion* is cited as settled must be shown able to find something.
- **Know when to stop.** When a round returns mostly re-reports and out-of-scope pre-existing bugs, the branch is done and the rest are issues. But a re-report is not automatically noise — ask *what changed: the evidence, or the cost of acting?*

---

## Environment — three machines; check which one you are on

**Windows** (`D:\Development\bootstack`, primary). The checked-in `.venv` is **stale** ("Access is denied"). **Use `py -3.12` for tests and docs** — pytest is installed only there. ⚠ `py -3.13 tests/run_gui.py` fails every leg with "No module named pytest" while printing a plausible harness summary; 3.13 is for demo scripts only. `bootstack.__version__` reports a stale `0.1.0a9` — ignore it.
- ⚠ **A second Tk is reachable here, and it is not the one `py -3.12` runs.** `uv run --no-project --python 3.13 --python-preference only-managed --with-editable . --with pytest tests/run_gui.py -q` runs on python-build-standalone: **Tk 8.6.12**, against python.org's **8.6.15**. That is the build #520 crashed on. Green there 2026-09-16 at the #520 fix — `1758 / 24`, 34 legs — below the `py -3.12` count only because pandas and matplotlib are absent. `uv` is not installed; `pip install uv` into a throwaway venv.

**WSL** (`/home/iddryer/bootstack`, Ubuntu 22.04) — **the only box that runs the Linux leg.**
- Use **`/home/iddryer/.virtualenvs/bootstack/bin/python`** (3.13, Tk 8.6.12, editable). `python3` is 3.10, below the floor. Confirm it prints `/home/iddryer/bootstack/src/bootstack`.
- No passwordless sudo; `openbox` is not installed — `xfwm4`, `xvfb-run` and `xprop` are. CI uses `openbox`.
- ⚠ **Run the Linux suite WITH a window manager**, or you reproduce #447 and think it is a product bug. Poll `_NET_SUPPORTING_WM_CHECK`; never `sleep`.
- `gh` is the **Windows** binary, `"/mnt/c/Program Files/GitHub CLI/gh.exe"`; it cannot read WSL paths, so pass bodies via `--body-file -` on stdin.
- Screen capture is not measurable under WSLg — run `test_capture` under Xvfb.

**macOS** (`/Users/israeldryer/PycharmProjects/bootstack`) — `.venv/bin/python` works (3.14, Tk 8.6). `python tests/run_gui.py` runs the full suite in ~2 min. System `python3.13` has no bootstack.

⚠ **No Tk 9 on any box** — #376/#378 stay unverifiable.

**Tests:** `py -3.12 tests/run_gui.py` (one Tk root per process, #150). Sum the per-leg summary lines yourself; the runner prints no aggregate.
- ⚠ **A new `@pytest.mark.isolated` module runs NOWHERE until it is added to `ISOLATED` in `tests/run_gui.py`** — the shared leg deselects it, and CI uses the same runner. The suite stays green and the count does not move.
- ⚠ **`tests/signals/test_signal.py` (22 tests) is collected by nothing** — not in `testpaths`, not in `run_gui.py`. It passes when run directly.
- ⚠ **Never pipe a build/test command** (`| tail`, `| Select-String`) — you read the pipe's exit code. Redirect to a file, capture the exit code on the next statement, then grep the file.

**Docs:** always clean-build — incremental builds mask warnings. `rm -rf docs/_build && sphinx-build -b html docs docs/_build/html -W --keep-going`. The build is warning-free; keep it so. ⚠ `-W` does not catch a dangling py xref — only `-n` does.

---

## Current state

### ★ START HERE — next: the #474 comment and docstring scrub (maintainer: later the week of 2026-09-14)

Trim comments AND docstrings in `src/` that narrate history instead of describing behavior. **Read #474 first** — it carries the keep/cut rule, the measurement and the order. In short:

1. **Measure:** `py -3.12 development/probe_474_docstring_census.py` (public view + internal by area); `--list <area>` prints each flagged docstring. Record the before/after flagged count in each PR.
2. **Order, one area per PR, comments and docstrings together:** (a) the public docstrings — ~5 real Tk leaks (`Signal.name`, `Signal.clear`, `App.on`, `ContextMenu`, `Shortcuts.bind_to`) and `guide_layout` naming `_internal`; leave the `.tk`/`.var` escape hatches; (b) `_runtime` + `_core` + `widgets/_core`; (c) `widgets/_impl` in two or three PRs by package.
3. **Keep** a behavior contract or a trap a later edit would undo (the `keysym != "KP_Enter"` block, `_reject_legacy_child_kwargs`'s positional `kind`, the `NOTE(#383)` markers). **Cut** issue narration, "measured" asides, before/after history, review rationale and shouting. A flag means look, not cut — every cut is a judgment call, so no mechanical strip.
4. **Verify per PR:** clean docs build (`-W`), `import bootstack`, the full suite — docstring edits cannot change behavior, so the count must not move.

**Released: `0.4.5` (2026-09-15)** — *Special characters and popup focus* (#515, #516), verified 11/11 by `development/verify_release.py 0.4.5`. History of every release is in the archive.

**`## [Unreleased]` holds two fixes.** Archive each the day it ships.

- **#525** (PR #526, merged) — `NumberField`/`SpinnerField` step on the wheel only while focused. The guard is `wheel.has_focus()` (same check as `_commit_if_not_editing`), and `apply_class_bindings` strips the `TSpinbox` class wheel binding; the value/text split is pinned by `test_field_wheel_focus.py`.
- **#520** (branch `fix/iso-left-tab-x11-only-520`) — `<ISO_Left_Tab>` is bound only when `winsys == "x11"`, at both sites (`textarea.py`, `extensions/smart_indent.py`). **The trigger is the Tk build, not Windows:** uv-managed CPython carries Tk 8.6.12, which rejects the keysym; python.org carries 8.6.15, which accepts it. `test_textarea_reverse_tab_keysym.py` pins both halves — construction survives a Tk that rejects it, and the binding is installed iff x11, so deleting it outright fails too. Plan: `development/plan-520-iso-left-tab-x11-only.md`.

⚠ **`release.yml` appends GitHub's generated "What's Changed" list (`generate_release_notes: true`), which lists EVERY merged PR, chores included.** Kept by decision (maintainer, 2026-09-15); remove the chore lines after publishing — `RELEASE.md` step 8.

⚠ **`v0.3.1`/`v0.3.2` and `main` differ by design** — the CHANGELOG was reworded after tagging and the Release bodies edited to match. **Never move a tag a release has already run on.**

| | |
|---|---|
| `main` | `8c1a0ff0` (merge of #526, the #525 fix). Verify with `git rev-parse origin/main` |
| branches | `main` only, local and remote |
| next release | None scheduled; `[Unreleased]` carries #525 and #520, a `0.4.6` candidate. `0.4.x — Patch line` has six issues open |
| CI | `ci.yml`: `headless`, `tests` (ubuntu + windows matrix), `tests-uv`, `docs`. **No macOS leg** (#452). Green on PR #526 (shared leg `1357 / 15` on both OSes, +5 over `079c72c3` with skips unchanged, so the new wheel tests ran rather than skipped); the `8c1a0ff0` run was still in progress when recorded |
| `tests-uv` | Added on the #520 branch, never yet run by GitHub. Windows, uv-managed Python — **a different Tk from every other leg**, which is the whole point. ⚠ `--python-preference only-managed` is load-bearing: without it uv may resolve the `setup-python` interpreter and the leg goes green having re-tested Tk 8.6.15 |
| suite, Windows | **`1787 passed / 22 skipped`, 34 legs, exit 0** — 2026-09-11 at `e88d38eb`; `py -3.12`, pandas + matplotlib present. **Not re-measured since:** +5 (#515), +2 in a 35th, Windows-only isolated leg (#516) and +5 (#525), so expect `1799 / 22`, 35 legs |
| suite, macOS | `1699 / 33`, 33 legs — 2026-08-29 at the #467 merge; **stale**, pandas absent. Not comparable with Windows |

**Counting a suite.** Prefer a number you just measured; record the date and commit beside it. `passed + skipped` cannot exceed the selected count except by module-level skips (read the collection line). A self-consistent total can still have selected the wrong population — bound the movement with `git diff --stat <baseline>..HEAD -- tests/`. On macOS, pandas absent flips two data tests (`125 / 4` vs `123 / 6`); `test_chart.py` is 44 tests behind a matplotlib `importorskip`.

---

## Open work

⚠ **A line here is not proof an issue is open** — `gh issue view <n> --json state`. If this section and `gh` disagree, trust `gh` and fix this section.

### `0.4.x — Patch line` (fixes only)

- **#488 — widest blast radius.** `_MultilineCore._on_destroy` (`textarea/core.py`) guards on `event.widget is not self`, and the only `<Destroy>` it receives names the inner `Text` — so the whole `TextArea`/`CodeEditor` teardown block has never run, including the wheel `unbind_class` sweep. #486, #490 and #491 each released one piece; none is the fix.
- **#469** — an event sent with `when="tail"` is queued against the emitting **window** and can outlive its widget, arriving at a different one. ~20 composites emit this way. The route is unproven (Tk path names are never reused; a 300-round probe never forced handle reuse) — remove the precondition rather than hunt the route. The test harness half is fixed (`_reset_scene` pumps `update()` first).
- **#468** — `Select(allow_custom_values=True)` hands validation rules the raw typed text. Plan: `development/plan-468-select-custom-value-typing.md`.
- **#447** — dialog focus/Enter flake on Windows, ~4/50 (and 2/50 after #407, which is noise). The CI reproduction was a missing window manager; **the Windows flake is not explained by that.** A sibling, `test_enter_on_a_disabled_button_still_reaches_the_default`, is 1 in 37 and 0/40 in a quiet process. ⚠ **Fix `probe_446_disabled_button_enter.py` first** — it counts a barrier timeout (dialog never up, `calls == []`) as a reproduction.
- **#422** — the `DataTable` group-header right-click guard is untested on macOS right-click sequences.
- **#207** — ContextMenu outside-dismiss vs a `'break'` target. Deferred. Agreed fix if revisited: a module-level open-menu registry + dismiss-all from `DataTable._on_header_click`, **not** a grab.

### `0.5.0 — Strictness and value types` — breaks batched into ONE migration

- **#383** — presentation kwargs that degrade silently (`density`, `Tabs.orient`, `Slider.orient`, `Gauge.variant`) and args that leak a raw `TclError`/`AttributeError` (`Button.icon_position`, `Label.justify`, `Scrollbar.variant`, `Expander.icon_position`, `ProgressBar.mode`). **Sweep by argument name, not by widget.** Folds in `Slider.value = None` leaking `TypeError` (reachable via `form.set`) and `show_grid=True` accepted on `Row`. Unknown *names* already raise (#472); what is left is bad *values* — and `App`/`AppShell`/`Workbench`/`Window` still report unknown names as `Tk.__init__` or a bare `TclError`, never the widget.
- **#369** — the selection family disagrees on off-list values (`SelectButton` raises both ways; `RadioGroup` accepts at construction, raises on assignment; `ToggleGroup` accepts both; where accepted, `value` says `'MX'` while `selection` says `None`). **One family decision, not four patches.**
- **#408** — `emit()` drops the payload for the 13 public names that map to real sequences.
- **#416** — `PathField.value` → `Path`. ⚠ **Decided in a COMMENT on the issue, not its body:** `open_multiple` → `tuple[Path, ...]`, empty `()`; every other mode → `Path | None`, empty `None`. `()` is a deliberate exception to the `None`-when-empty convention.
- **#445** — `attach()`'s grid branch silently filters legacy layout kwargs that a flex child rejects. It raises where the framework accepts, hence here.
- **#479** — `OptionMenu` never cancels its signal subscription: a destroyed widget keeps emitting (the `TclError` is raised inside the Tk trace, invisible to the caller) and stays pinned in memory. `ValueSignalMixin._bind_value_signal` (`widgets/_core/field_mixin.py`) is the pattern — hold the id, release it in `on_destroy`. Its placement here is the maintainer's call; do not "correct" it.

A raise-where-accepted fix can still ship as a patch when **no working code can reach the break** — #481 did (every call it rejects had built a signal that could never hold a value). That is an exception, not a reason to move #445.

### `0.6.0 — Form, signals, and composite authoring`

- **#389** — `Form.reset()` / `Form.clear()`, design settled on the issue. Different verbs: reset = construction-time originals (not user-implementable, so it needs an `__init__` snapshot), clear = `None` (Slider clears to `min_value`). Both clear validation state.
- **#412** — publish `register_widget_events()` for composite authors, keeping the typo guard. Until then `docs/reference/events.rst` stays silent on custom events. Folds in narrowing `resolve_event()`'s error, which lists every class's events process-wide, not the widget's.
- **#415** — 10 of 12 field-family widgets are `Form` editors; `PathField` and `TimeField` are not, and an unknown `editor=` silently builds a `TextField` (`_impl/composites/form.py`).

### Other milestones

| Milestone | Issues |
|---|---|
| `0.7.0 — Guided flows` | #311 `Timeline`, #312 `Wizard` |
| `0.8.0 — Power-user interactions` | #315 `DropZone`, #316 command palette |
| `0.9.0 — Structured editing` | #192 color-swatch select (lock shape/naming with the maintainer first), #314 `PropertyInspector` |
| `Tcl/Tk 9 support` (blocked on hardware) | #376 DataTable cell padding, #378 suite dies on Tk 9 |
| `Hot reload (provisional)` | #322, #328 (the E2E multi-file reload test — the maintainer will write it) |
| `Additions awaiting a minor` | #208 persistent DataTable selection, #317 top-line tab indicator, #352 Markdown render |
| `Wrapper and internal parity` | #466 — needs three amendments recorded on the issue (it cannot see missing methods/properties; the 84 unanalysed params are a hole; add an AST check that every `bs.<Widget>(kw=…)` in `docs/**/*.py` is real). #477 is adjacent but deliberately not here |

### Unmilestoned

- **#477 — collapse the `_impl` layer before 1.0** (maintainer's framing; a pre-1.0 goal, since the surface freezes at 1.0). The `_impl` widgets were the original standalone implementation; much of their own variable/signal/event plumbing now serves no consumer. Static AST scoping (2026-08-26, needs a construction cross-check): 174 `_impl` classes; 125 imported somewhere; **49 imported nowhere** (a separate question); 83 shared; **24 imported by exactly one wrapper, all leaves** — 14 with a generic base (cheap), 10 with a behavioral base (`OptionMenu`→`MenuButton`, the three `Field` entries, `TimeEntry`→`SelectBox`, `Switch`→`CheckButton`, two raw ttk).
  - ⚠ **A mechanical signal sweep breaks three things:** `localization_mixin.py` *replaces* `_textsignal` with a derived formatted signal; `Form.field_textsignal()` and `Field.textsignal` are live consumers; and eight-plus wrappers forward `textsignal=` legitimately. `OptionMenu` (#461/#476) is the counter-example, not the rule.
  - ⚠ The #463 audit could not see any of this — its unit was the constructor keyword.
  - **Fold in the windowing-system probe:** `_runtime/wheel.py::_windowingsystem` returns `""` on failure (degrades to the generic path — correct); `widgets/toast.py::_windowing_system` returns `"win32"` (asserts Windows, and drives `_resolve_corner`'s default). 9 raw `tk.call("tk", "windowingsystem")` sites; 15 cache it as `self.winsys` at construction, so consolidating changes *when* the probe runs.
- **#452 — the GUI suite hangs on GitHub macOS runners** (90 min for a 90 s suite), so aqua has no automated coverage. Setup and the Tk report succeed; "Run the suite" never returns. **Step 1 decides everything: does a bare `tkinter.Tk()` → `update()` → `destroy()` complete on the runner?** A hang means the runner lacks a window-server session; a pass means the hang is ours — bisect the legs. Debug-by-push: make each push answer one question and name the step after it. ⚠ The local macOS box is not a substitute (it has a window server and a session). Every job has `timeout-minutes`; a cancelled leg whose log stops inside `apt-get` is a runner outage — re-run it.
- **#431** — open on purpose, waiting on a scope decision: its fix skips on aqua (no NumLock modifier for `Mod1`) and is **unverified on a real Aqua build** — fold into the #452 trip.
- **#436** — adopt `versionadded` across the public API (the docs serve one version). Undecided: retroactive to `0.2.x`, or forward-only.
- **#474** — trim comments and docstrings that narrate the code back to what is hard to recover. **Next up** — see ★ START HERE.

⚠ **"Do not assign a milestone unasked" guards SCOPE calls, not blockers.** Would shipping the milestone without this issue be a decision, or a defect? A defect means it belongs on the milestone; a decision means ask.

### Backlog not on the tracker

- **`value=` is silently ignored when `signal=` is also passed** on `Checkbox`/`Switch`/`ToggleButton` (re-measured 2026-09-11). Seed the Signal instead.
- **`bs.Window`** forwards uncurated `**kwargs` to the internal Toplevel (`init_kwargs.update(kwargs)`), and `size`/`topmost` are construction-only. `title` and `result` are live. Own branch.
- **`EditFilter`** was demoted (Tk-coupled indices/tags); design a de-Tkintered `CodeEditor` extension API before re-promoting. `NOTE(editfilter-public-api)` in `textarea/filter.py`.
- **Code-review follow-ups #4–#10** in `docs/_dev/widget-api-audit.md` (SelectButton stale value after `options=`, screenshot HWND hardening, group/window/date duplication, Calendar batch-redraw).
- Gallery opt-in **keyboard**-focus ring (not hover) and deferred Gallery perf; `add_spacer()` → public `Spacer`; AppShell improvements (nav density/font, group active-child highlight); bare landing pages; localization/windowing how-tos; pending screenshots (Tooltip/Toast, 7 Dialog pages).
- **Visual theme builder** — do NOT build yet.

---

## Milestones — the rules

- **Numbered milestones are releases; unnumbered ones hold work not yet assigned to a release.** Nothing gets a number until its order is real. Subject lives on **labels** (`tk9`, `test-infra`, `hot-reload`, `new-widget`).
- **Close a milestone when its release ships**, so the open list is exactly the live work.
- **Ordering:** breaks batched, not dribbled (one migration instead of four); then near-ready API; then new widgets. Numbers past the next release are ordering hints — retitling is cheap. ⚠ Milestones were renumbered; **never trust a number quoted in the archive** — read `gh`.
- **The patch line is bug fixes only.** SemVer since `0.1.0`: adding public surface is a MINOR even when nothing breaks. The rule is one-directional — a minor may carry any number of fixes, so when a minor is cut, ask what else is ready; and for a fix, ask whether it needs a minor at all.
- **A rolling line that turns over gets a NEW milestone, never a rename** (renaming relabels shipped work). Fix the description, not just the title. Sweep a turning-over line with `--state all`.
- ⚠ **The milestone API counts pull requests as issues.** `gh issue list --milestone <title> --state all` is the authority for issues; `gh api repos/:owner/:repo/milestones` only for the open/closed shape.
- Unmilestoned open issues: `gh issue list --state open --json number,milestone --jq '[.[]|select(.milestone==null)]'`.

---

## Release flow

**Follow `RELEASE.md`** — never copy it here. What you need when writing a FIX:

- A fix commit writes under `## [Unreleased]`; the promotion commit renames the heading and adds the `[X.Y.Z]:` link.
- **An entry earns its place by being reachable from public API** — a CHANGELOG answers "was I affected?". CI/harness work and unreachable defects get no entry; say so in the commit message. Check `__all__` and the public event registry first.
- **Check a claim about prior behavior against the OLD code** (`git show main:<file>`), not the fix.
- **One paragraph per line — never hard-wrap** entries, PR bodies, issue bodies or review comments; the Release body renders soft breaks. Do not reformat shipped sections.
- A fix that changes working behavior may ship under `### Fixed` with an explicit upgrade note (`0.4.3`'s `CodeEditor.on_change` is the precedent).
- ⚠ **A closing keyword next to an issue number closes it — in a PR body OR a commit message on `main`, and even when QUOTED.** #479 was closed twice this way. Write the keyword and the number apart.

---

## Working agreements

**Hold commits until the user tests; per-commit approval.** Never commit feature work to `main` — branch first. A fix pushed to a branch after its PR merged is stranded; verify it landed.

**Standing principles:**
- Live properties only for legitimate runtime needs (`surface` is build-time).
- Prefer Tk native/virtual-event bindings; don't undo a convention without a reason.
- Docs describe the clean public surface — no implementation or toolkit detail.
- **Adversarially verify reviewer and agent claims** — agents over-flag. But a clean review is not proof either: tests called "better than average" have been vacuous and flaky.
- **Pause and ask when a fix outgrows its issue.**
- Test public paths, not internal side-hacks.
- **The framework absorbs the problem, not the developer.** A fix that hands the app author a new problem, or leaves the end user worse off than the bug, is not a fix.
- **Drive the thing by hand before calling it done** — demos have caught blockers that a green suite and a written review both missed.

### Branch and worktree hygiene

- **Do not touch a branch while a review runs** — reviews read files on disk. Use a `git worktree`.
- ⚠ A worktree runs `main`'s source unless `PYTHONPATH=$W/src` **and** you pass the worktree's absolute test paths. Prove it: `py -3.12 -c "import bootstack,os;print(os.path.dirname(bootstack.__file__))"`.
- `git rev-parse` both branches before reading; review committed blobs (`git show <sha>:<path>`).
- **Handoff edits ride the branch they describe.** Before merging, check `git diff main...HEAD -- CLAUDE.md` contains only this branch's own handoff changes — a branch cut from a stale handoff can silently revert `docs(claude):` commits.
- **Non-ancestor ≠ unmerged** (squash merges). Check `git merge-base --is-ancestor`, then `gh pr list --head <branch> --state all`. Record head SHAs before deleting.
- Merge commits, not squashes, when one-commit-per-issue granularity is the deliverable.
- ⚠ **`git mv` stages the indexed blob** — edits made before it stay unstaged, and the commit ships a 100%-similarity rename. `git add` after `git mv`; treat 100% similarity as a failure when you meant to change content.

### Techniques that beat static reading

- **Run an empirical probe instead of reading tangled code.** Rebuild it rather than re-reading.
- **Tests must fail for the RIGHT reason** — a pre-fix `AttributeError` proves nothing. Make the failure behavioral; "construction doesn't raise" is not a test.
- **Run the baseline** before the fix — and on a branch, baseline means actually checking out `main`.
- **A control separates cause from correlation — and a control that never reaches the path under test is indistinguishable from a working fix.** Force the condition itself.
- **A probe that finds nothing must be proven able to find something** (a BOM-choked `ast.parse` inside `except: continue` once reported zero hits). Run the control against the pre-fix commit.
- **A probe must run on every box it informs** — SKIP and continue, never `sys.exit` on a missing platform feature.
- **A green suite is not evidence of stability.** At 1-in-8, one green run is the expected outcome of a broken branch. Never re-run to disprove a flake — build a control that creates the condition and reports a rate; run the narrow combination as well as the full leg.
- **Verify at the commit you ship**, and re-run a recorded measurement after any commit that changes what it measures.
- **State the boundary when you claim completeness** — write the command (`grep -rn "grab_set" src/bootstack/`), not the conclusion.
- **To prove a guard does not over-reject, enumerate the producers**, not the consumer.
- **Before fixing a silent no-op, find what leans on it** — a long-shipped no-op is load-bearing somewhere.
- **When state becomes derived, every existing writer becomes a silent no-op** — grep them all, and pin each way a value arrives (constructor, setter, `configure`).
- **Bisect order-dependent failures; don't theorize.**
- **Measure the surface before scoping a sweep** (an AST pass + a bogus-value construction probe).
- **A platform backend is often constructible off-platform** — ask before accepting "unverifiable from this box".
- **Re-enter an existing routine rather than re-emitting an event by hand.**
- **A docstring outlives its code** — check for stale behavior as well as toolkit leaks, and grep the built HTML. A warning for whoever EDITS a line belongs in a `#` comment.

### Measurement traps

- Pair every geometry assertion with a precondition that the setup took effect; compare geometry only within one process.
- ⚠ **Compare captures only within ONE `bs.App` instance** — the first app in a process renders content white, later ones grey. Build the noise floor across the same kind of change you measure.
- Measure **depth**, not call count, to separate re-entrancy from "ran twice".
- ⚠ **A synthesized click cannot test a pointer-routed guard** (`tk busy` intercepts by window position). Some questions need a human; say so.
- **A rate is not evidence for a timing-dependent flake** — a fix and a timing shim both reached 0/5. Assert the invariant (`test_harness_event_queue.py` is the pattern).
- Probe output must be ASCII — the Windows console is cp1252.
- ⚠ **Windows refuses `focus_force()` to take the foreground from a process that did not receive the last input** — a foreground-dependent test then skips silently. `AttachThreadInput` to the foreground thread first (`test_popup_app_focus_loss.py::_bring_to_foreground`).

### Tk and tkinter traps

- ⚠ **Virtual events are DROPPED while the window is unmapped** — use `shown_app`, not `app` (withdrawn). And `shown_app` is not enough if the widget itself is unmapped in the crowded shared root: build the target in its own `Toplevel` and assert `winfo_ismapped()` first.
- ⚠ **`focus_set()` is a silent no-op when the widget or any ancestor is unmapped.** Under X11 the window manager assigns focus to a new top-level; `focus_lastfor() == ''` means nothing ever held focus (no WM). Assert focus via `focus_lastfor()`, not `focus_get()`.
- ⚠ **`dlg.show()`'s modal loop is not broken by an `after`-scheduled close** — invoke a real footer button, and poll for the grab rather than a fixed delay. The grab is set before the footer's children map at idle, so scope the barrier to the subtree you need.
- ⚠⚠ **Tk drops a grab when its holder is destroyed but never restores the one it displaced.** `_runtime/grab.py` (`capture_grab`/`restore_grab`) is the ONE home for the pairing. Capture BEFORE grabbing; restore holder AND kind (global vs local). `grab_current()` raises `KeyError` for a Tcl-created window (a posted combobox popdown).
- **Do not synthesize keys in the shared-root suite** — drive the bound routine (`ttk::treeview::ToggleFocus`).
- ⚠ **`event_generate("<Up>")` on a widget delivers to the FOCUS window, not that widget** — a `SpinnerField` wheel once stepped whichever field held focus (#525). Generate a virtual event, or guard on focus.
- ⚠ **An instance handler returning `None` still runs the native class binding** — `TSpinbox`/`TCombobox` bind the wheel themselves; strip the class binding when the instance handler owns the behavior (`apply_class_bindings`).
- ⚠ **Which keysyms exist is a property of the Tk BUILD, not the platform** — `<ISO_Left_Tab>` is rejected by Tk 8.6.12 and accepted by 8.6.15, both on win32, so an unguarded bind raises at construction for some users and not others (#520). Bind an X11-only keysym behind `winsys == "x11"`; Tk wraps its own `<<PrevWindow>>` add in `catch` for the same reason.
- `event_generate("<Double-1>")` is rejected — send two presses with explicit `time=` (synthesized events default to `time=0`).
- `winfo_ismapped()` on a destroyed widget RAISES `TclError`.
- ⚠ **`update_idletasks()` does not service queued window events — only `update()` does.** It can silence a flake while fixing nothing.
- ⚠ **Some failures are invisible to Python** — install a `bgerror` collector (`root.tk.createcommand('bgerror', fn)`, delete it in `finally`). When a bug has no public observable, that channel is the observable.
- ⚠ **Defer widget cleanup on the ROOT, never the widget** — `widget.after_idle(cb)` is owned by the widget and orphans on destroy. Guard `TclError` and `AttributeError`.
- ⚠ **Tkinter binding names are recycled** (~498/499 cycles reuse the name) — never let a deferred `deletecommand` hold one. When a symptom is allocator- or timing-dependent, assert the invariant (e.g. 50 cycles → 50 distinct ids).
- ⚠ Check any `_impl` code that subscribes to a signal it does not own for a matching cancel on destroy (#479).
- ⚠ **Never build a Tcl script from text** (`tk.eval(f"… {{{text}}}")`) — braces break it and `[…]` executes. Use `tk.call(cmd, *args)`; each argument is one word, never parsed (#515).
- ⚠ **`instate(['!disabled'])` returns True when ENABLED** — write `not instate(['disabled'])`.
- A test that schedules a hang guard must cancel it in `finally`; a leaked `after` fires in a later test.
- Spying on an instance attribute is useless once the bound method was captured — patch the CLASS before constructing.
- ⚠ **Never `warnings.warn` from a Tk dispatch or teardown path** — use `debug_log` (`_runtime/utility.py`), which never raises.

### Line endings — CRLF

Files are **CRLF** (`core.autocrlf=true`, `.gitattributes` `eol=crlf`). **`git diff` cannot see a flip to LF.** The only signals are the "LF will be replaced by CRLF" warning and a byte check.
- `sed -i`, bulk `pathlib` rewrites and `read_text`/`write_text` flip CRLF→LF; a `$`-anchored `sed` pattern silently matches nothing.
- Prefer the Edit tool. The Write tool writes LF — convert new files by bytes.
- A stray byte before a BOM once made the whole package unimportable: **verify `import bootstack` at the committed state** after hand-editing source.

---

## Gotchas

### Layout and wrappers

- **Self-placement rides `**kwargs`** — route through `self._split_layout_kwargs(kwargs)` (an instance method). **It is default-strict: leftovers raise `TypeError` naming the widget**, so a new wrapper needs no guard. Only a deliberate forwarder opts out with `_forwards_kwargs = True` (Chart, MenuButton, Picture, StatusBar, Toolbar); a sixth fails `test_declared_forwarders_are_exactly_the_five` on purpose. A crafted error for a specific key goes ABOVE the split.
- The catch-all is always named `**kwargs`.
- **User options merge over framework kwargs; structural keys raise** — route through `merge_kwargs` (`widgets/_core/kwargs.py`). ⚠ Legacy exception: `MenuButton`'s `_RESERVED_INTERNAL_KEYS` silently skips collisions — do not copy it.
- `margin_x=` / `margin_y=`, never `padx`/`pady`.
- **`bs.Row` and `bs.Column`** are the stacks (no `HStack`/`VStack`). Container defaults: `horizontal_items=`, `vertical_items=`, `grow_items=`, `weights=`; `Grid` adds `columns`/`rows`/`auto_flow` (`columns=3` ≡ `[1,1,1]`, `0` ≡ `'auto'`).
- **`fill=`/`expand=`/`anchor=`/`sticky=`/`side=` on a layout child RAISE**, with advice that depends on how the child is placed: a **flex child** (`Row`, `Column`, and `Card`/`GroupBox`/`Accordion` in column mode) is told `grow=` + `horizontal=`/`vertical=`; a **grid cell** is told `horizontal=`/`vertical=` and to weight the row/column — never `grow=`, which a grid cell silently filters. 11 `_reject_legacy_child_kwargs` call sites; its `kind` argument is required so a caller cannot get the wrong message. `attach()`'s grid branch is the exception (#445).
- `height=`/`width=` on a stack collapses the other axis — add `fill=` + `expand=True`. `show_border=True` needs padding. Use `bs.Card` for a card look.

### Widgets and API

- **The public namespace is curated** — `bs.*` holds only what you compose a UI from (widgets, `App`/`AppShell`/`Workbench`/`Window`, `Signal`, dialog verbs, `set_theme`/`toggle_theme`). Everything else from its submodule (`bootstack.data`, `.style`, `.i18n`, `.validation`, `.events`, `.streams`, `.scheduling`, `.shortcuts`, `.store`, `.errors`, `.types`, `.dialogs`). Guard: `tests/test_public_surface.py`. ⚠ Write `from bootstack.events import ChangeEvent`, not `bs.events.…` — `events` is not in `__all__` and the surface test does not catch it.
- ⚠ **`emit()` and `on()` do not always hit the same target** — `emit()` uses `_event_target()` only for `<<Virtual>>` sequences; native-mapped names fire on `_internal`.
- Dialogs live in `bootstack.dialogs` (impl in `dialogs/_impl/`); `bootstack.dialogs.FormDialog` is a public wrapper — the impl is `._internal`.
- **`App`/`AppShell` config is flat kwargs** — no `settings=`/`AppSettings`. Symmetric `app.*` properties; `app.on_theme_change`, `app.on_locale_change`; `bs.App.from_store(store)`.
- `bs.Signal()` is safe at module level (the Tk var is created lazily). `textsignal=` for text-bearing widgets, `signal=` for the rest; never expose `textvariable=`/`variable=`.
- ⚠ Do not re-propose per-type empties (`empty(int) = 0`) for `Signal(allow_empty=True)` — `''` is a real `str` member, not a repurposed value. And a checkbox's indeterminate state is a widget state, not a variable value (the toolkit has no tristate variable) — #483 was documentation.
- `TTKWrapperBase.__init__` overwrites `self._accent` — store it before `super().__init__()`, reassign after.
- **Theme:** `<<BsThemeChanged>>` fires after the full rebuild (use it); ttk `<<ThemeChanged>>` fires ~1400× per rebuild — never bind it on the root. An imperatively painted widget defines `_bs_apply_theme(self)`; a hide/show container calls the stale-only walk on show. See `docs/_dev/theme-repaint-architecture.md`.
- `bs.DataTable` takes any `DataSourceProtocol`; identity reads go through `_record_id`/`_public_record`/`_internal_fields`. A double-click delivers `on_row_click` click, double, click.
- `RadioGroup.set()` validates keys, not values. `bs.Form` uses `col_count=`.
- ⚠ **The field family disagrees on whether a programmatic `value =` is a change** (`Select`/`TimeField`/`SelectButton` emit one; `NumberField`/`DateField` none). **Maintainer: keep in mind, do not fix, do not file** — raise it only if a real defect lands on it.
- The property is `read_only`, not `readonly` — a typo'd attribute sticks silently on a plain-Python widget.
- Boolean controls: `Checkbox` is the only one with `tristate`; `Switch` has no `on_icon`/`off_icon`/`icon_only`/`show_indicator`/`density`; `ToggleButton` has `density` but no `tristate`/`show_indicator`. **Keep `show_indicator=`** (#144 won't-do). Give each subclass its own `__init__` for Sphinx; `:inherited-members: PublicWidgetBase`.
- Slider tracks: separate with `margin_y=`, not `gap=`. `on_change` is live by design; `on_commit` is the release event.
- `configure_style_options()` does not rebuild — call `rebuild_style()` after. `Frame.configure(surface=)` does not work at runtime.
- MenuButton item types are `'command'`/`'check'`/`'radio'`/`'separator'`, translated to ContextMenu's names via `_ITEM_TYPE_MAP`. Check disabled state with `instate(("disabled",))`.
- `Expander` is internal — use `bs.Accordion`. `select.py`/`calendar.py` would shadow stdlib — the files are `selectfield.py`/`calendarwidget.py`.
- `bootstack.shortcuts` exposes `Shortcuts`, `Shortcut`, `get_shortcuts()`; `format_shortcut` is internal.
- Headings are already bold (`font="heading-md"`). American English everywhere.

### Dialogs

- `content_builder` fills a public content `Column` set as the active parent — write the body parent-free. Built-in verb/Form dialogs opt out with `_raw_content=True`.
- `Dialog.__init__` is keyword-only; `parent=`, `min_size=`/`max_size=`. `ButtonRole`: `"primary"`, `"secondary"`, `"danger"`, `"cancel"`.
- ⚠ `Dialog._toplevel` is never reset — after a modal `show()` it is destroyed. Resolve the result target from `master`.
- ⚠ **Enter handling tests `keysym != "KP_Enter"`, NOT `== "Return"`, deliberately** (an unknown keysym reads as consumed; pinned by a test). Windows cannot reach this path end to end — only X11 can. A disabled default button must not swallow Enter. `event_add` to a virtual `<<Submit>>` does not change dispatch (the physical binding wins).

### Docs, examples and screenshots

- **Run `docs/examples/<widget>.py` after editing** an example. Doc snippets are not executed — check every call against the API.
- Screenshot patterns are in `docs/_dev/docs-authoring-patterns.md`. Traps: stacks center children (wrap button rows in a `fill="x"` row); `minsize=(720, 1)` for field rows, `size=(W, H)` for full-app widgets; popdown menus — call `show_menu()` at t=850ms (topmost at 800, grab at 950); dialog heroes open non-modally at 200, lift at 850, shoot at 950 with `app._capture_target`; the runner crops 2px per edge.

---

## Architecture (settled)

Public widgets are plain Python objects (**not** `tk.Widget` subclasses) holding `self._internal`. Constructor order: resolve parent → split layout kwargs → construct internal → attach. `.tk` is the escape hatch.

```python
import bootstack as bs

with bs.App(title="Demo", size=(800, 600), padding=16, gap=8) as app:
    with bs.Row(gap=4, vertical_items="center"):
        bs.Label("Hello", font="heading-lg")
        bs.Button("OK", accent="primary", on_click=lambda: ...)
app.run()

with bs.AppShell(title="My App", theme="bootstrap-light") as shell:
    with shell.page_nav() as nav:
        with nav.add_page("home", text="Home", icon="house"):
            bs.Label("Welcome!")
    shell.navigate("home")
shell.run()
# Workbench: shell.add_workspace(key, text=, icon=) -> ws.page_nav() -> nav.add_page(...)

sig = bs.Signal("World")
bs.TextField(textsignal=sig)                       # two-way
sub = widget.on_change(handler)                    # -> Subscription
widget.on_change().debounce(300).listen(handler)   # -> Stream

# Tokens
accent  = "primary|secondary|info|success|warning|danger|default"
variant = "solid|outline|ghost|toggle"
surface = "content|card|chrome|overlay"
font    = "body|heading-lg|heading-md|caption|code|body+2[italic]"

bs.alert("Done."); bs.confirm("Delete?")          # -> bool
bs.ask_string("Name:"); bs.ask_integer("Age:", min_value=0); bs.ask_date("Pick:")
bs.ask_color(); bs.ask_font()
```

`__enter__` pushes the container, `__exit__` pops; an App hides on enter and shows on exit.

**Events.** Every `on_*()` is `@overload`ed: no handler → `Stream`, handler → `Subscription`. Data events (`change`, `input`, `select`, validation) pass the typed payload dataclass from `bootstack.events` (ListView item events pass a record `dict`). Native events pass a curated Tk-free `Event` (`widget`, `x/y`, `x_root/y_root`, `width/height`, `delta`, `ctrl/shift/alt/meta`, `key/char`, `time`). The transform is `adapt_handler()` (`widgets/_core/base.py`); `on()` resolves through the one seam `PublicWidgetBase._event_target()`, which the ten retargeting wrappers override (`test_event_target_seam.py`).

```
src/bootstack/
├── _core/       signal_binding, localization, mixins, images, capture, variables
├── _runtime/    app, toplevel, grab, shortcuts, events, wheel, utility (debug_log)
├── data/        DataSource (Base, Memory, Sqlite, File)
├── dialogs/     public dialogs; _impl/
├── signals/     Signal, integration (the Tk bridge)
├── style/       Theme (public), themes/, Style/Typography/Font (internal)
├── validation/  ValidationRule, ValidationResult
└── widgets/     ~40 public wrappers; _core/ (base, container, events); _impl/; types.py
```

---

## Code standards

- **Docstrings:** one-line summary + description + `Args:` (name: description, no types). Single backticks, never double; no RST roles. Valid values + default per kwarg (an aliased `Literal` type carries its value list in the alias docstring instead).
- **Dataclass fields use attribute docstrings, never `Args:`** (it renders them twice). ⚠ **No colon on the FIRST line of an attribute docstring** — napoleon turns the pre-colon text into a bogus `:type:`, silently.
- **No Tkinter in docs or docstrings** except the `.tk`/`.var` escape hatches and `signals/integration.py`.

```python
@dataclass
class ChangeEvent:
    """Fires when a field's value is committed (on blur or Enter)."""

    value: Any = None
    """The committed, parsed value."""

@overload
def on_change(self) -> Stream: ...
@overload
def on_change(self, handler: Callable[[ChangeEvent], Any]) -> Subscription: ...
def on_change(self, handler=None):
    return self.on("change", handler)
```
