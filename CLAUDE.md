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
**Branch strategy:** `feat/*` branches off `main`. PRs go `feat/*` → `main`.

> 📓 **Session history lives in `docs/_dev/handoff-archive.md`** — every shipped
> initiative with its full root-cause analysis, decisions, and gotchas. This file
> keeps only what is OPEN plus the standing rules. **Read the archive when you
> touch an area it covers** (it is indexed by issue/PR number); don't re-derive a
> root cause that is already written down there.
>
> ⚠ The archive spent a while **untracked** — it was split out of this file on
> 2026-07-30 and that session ended before committing either half. Committed
> 2026-07-30 (`docs(claude): split session history…`). **Lesson worth keeping: a
> handoff artifact only survives if it is IN THE REPO.** The same failure mode
> already cost us #379's `leakfix.patch`, which was saved to a per-session temp
> `scratchpad/` and is genuinely gone.

---

## Environment — TWO MACHINES. Check which one you are on first.

**Windows box** (`D:\Development\bootstack`): the checked-in `.venv` is **STALE**
— it points at a `Python314\python.exe` that fails with *"Access is denied"*. Use
the launcher. **`py -3.12` for BOTH tests and docs** — **pytest is installed ONLY
on 3.12** (9.0.3); `py -3.13 tests/run_gui.py` fails every leg with *"No module
named pytest"* **while still printing a plausible-looking harness summary**. 3.13
and 3.14 have neither pytest nor the docs deps. `py -3.13` (3.13.7, Tk 8.6) is
fine for **running demo scripts**, which is all it is good for.
`bootstack.__version__` reports a stale `0.1.0a9` from old install metadata —
harmless, ignore it.

**macOS box:** repo at **`/Users/israeldryer/PycharmProjects/bootstack`**. Here
**`.venv` WORKS**: `.venv/bin/python` = **Python 3.14.0, Tk 8.6**, editable
install, macOS **26.5.2**. `python tests/run_gui.py` runs the full GUI suite in
~2 min with a real display. ⚠ Tk here is **8.6, not 9** — this box does NOT
exercise the Tk 9 paths, so `test_scroll_events.py`'s touchpad tests SKIP.
`python3.13` exists system-wide but does **NOT** have bootstack installed.

**Running tests:** `python tests/run_gui.py` (one root per process, `#150`).
**Docs:** clean-build always — incremental builds MASK warnings.
`rm -rf docs/_build && sphinx-build -b html docs docs/_build/html -W --keep-going`.

**⚠ `tests/widgets/*.py` NEVER RUNS.** `testpaths` is `tests/cli`,
`tests/widgets/public`, `tests/data`, and `run_gui.py` passes those same paths —
so **12 files / 25 tests** directly under `tests/widgets/` (`test_shell_*`,
`test_icon_image_props`, `test_rebuild_regressions`, `test_toolbar_drag`) are
collected by nothing. All 25 **pass** run individually (each builds its own root,
so they'd need `isolated` treatment). Dead coverage — fold into #380.

**⚠ Never pipe a build/test command to `tail`** — you capture `tail`'s exit 0 and
miss real failures (it once hid a failing test leg AND a broken docs build).
**This bites in PowerShell too**: `pytest ... | Select-String ...` leaves
`$LASTEXITCODE` from the *pipeline*. Redirect to a file, capture `$LASTEXITCODE`
on the next statement, then grep the file.

---

## Current state

**Released:** `0.1.8` on PyPI, tag `v0.1.8` (2026-07-23); `pyproject.toml` is at
`0.1.8`. **`main` is GREEN** (Windows, 893 passed, exit 0) with **no open PRs**.
A failing test is a real signal — treat any red as a regression.
**Working branch: `fix/392-subscription-cancel`** — green too (899 passed), all
changes uncommitted. `main` itself is untouched.

**⏭ THE ACTIVE TARGET IS `0.2.0`** — milestone **`0.2.0 — Form and field
correctness`** (`gh` milestone **#6**). **A minor, not a patch, and that was a
deliberate maintainer call:** the project committed to SemVer at 0.1.0 and two
merged changes are not backward compatible (**#381** raises where it used to
accept; **#387** made `configure(data=)` genuinely clear absent keys). **#394**
also moves pixels in any layout pairing a field with a taller widget on a stretch
axis. Merged already: #332, #379, #381, #387, #388, #394. **#392 is FIXED but
UNCOMMITTED on `fix/392-subscription-cancel`, awaiting the review in item 0
below. Remaining after that: #389, #390.** Every themed milestone shifted OUT one
minor —
`0.2.x — Widget polish` (#2) · `0.3.0 — Guided flows` (#3) ·
`0.4.0 — Power-user interactions` (#4) · `0.5.0 — Structured editing` (#5).
Mapping + reasoning: memory `project_roadmap_milestones`.

### ★ START HERE — CODE REVIEW the #392 branch, then #390 / #389, then cut 0.2.0

0. **⇦ THE ASK FOR THIS SESSION: review `fix/392-subscription-cancel`.** The fix
   is written, verified, and **UNCOMMITTED** — branch exists, nothing staged, the
   maintainer wanted a review pass before any commit. `git diff` +
   `git status --short` is the whole change:
   - `src/bootstack/_runtime/events.py` — ~15 lines, the actual fix
   - `tests/widgets/public/test_subscription_cancel.py` — NEW, 6 tests
   - `CHANGELOG.md` — one `### Fixed` bullet under `## [Unreleased]`
   - `development/verify_392_subscription_cancel.py` — NEW, hands-on demo
     (untracked by convention, like the other `verify_*.py`; do NOT commit)

   The tree is otherwise clean, so **`git diff` really is just #392** — the
   handoff-archive split that was sitting uncommitted alongside it was committed
   first, on purpose, so this review is not reading a 1500-line docs diff.

   **Do not re-derive the root cause or re-run the baseline — both are recorded
   below and were observed, not assumed.** Review altitude: the change is small
   and green; spend the pass on whether emitting stock's script shape has
   consequences nobody measured yet, not on restating what it does.

   **The four things actually worth attacking in review:**
   (a) **`return 'break'` is now effective on virtual events** where it was
   silently ignored — a real behavior change. An AST scan of all **75**
   `return 'break'` sites in `src/` found exactly **two** bound to a `<<...>>`
   sequence: `_handle_increment_event` / `_handle_decrement_event`
   (`_impl/_parts/numberentry_part.py:127-128`), and both break **only** when the
   field is non-interactive. Every gesture path and `numericentry.increment()`
   already refuse to generate the event on a disabled field, so the only
   reachable path is a hand-written `event_generate` on a disabled field — where
   suppressing is arguably more correct. Scan script preserved at
   **`development/scan_392_break_handlers.py`** (untracked, like the `verify_*`
   scripts). **Re-run it rather than re-reading 75 sites.**
   Deliberately NOT in the CHANGELOG: `break` is documented nowhere in `docs/`,
   so advertising it would newly commit the project to it. Reviewer may disagree
   — that's a legitimate call to reopen.
   (b) The two omitted substitution codes: bootstack's list is stock's plus `%d`,
   minus `%f` and `%W`. `%W` is unused because the wrapper recovers the widget
   from a weakref. Confirm that's still true rather than assuming.
   (c) The `wrapper` positional parameters must stay in lockstep with the
   `subst` string — the fix keeps `%d` FIRST. There is no test that would catch a
   reordering; consider whether one is worth adding.
   (d) The new tests were checked to fail **pre-fix for behavioral reasons**
   (5 of 6 — `{'c': 0} != {'c': 1}`, not `AttributeError`). The 6th
   (cancel-everything) passes pre-fix **on purpose**: the bug silenced everything
   too, so it guards the opposite error. Don't "fix" it as a dud.

   **Root cause (settled, do not re-derive).** `_patched_bind` wrote its own Tcl
   script for **virtual events** (`<<...>>` = every bootstack event) as a bare
   `<funcid> %d %# ...`, but **`unbind` was never patched to match**:
   `Misc._unbind` filters lines by the prefix `if {"[<funcid> ` that stock
   Tkinter's `_bind` emits, so nothing was filtered (**the binding survived**)
   while `deletecommand(funcid)` still ran (**the Tcl command was deleted**). The
   orphan errored on every dispatch, and because bindings use `add='+'` they are
   ONE concatenated script — so the error **aborted every handler after it**.
   Silent: no Python-level exception. Fix = emit stock's exact
   `if {"[<funcid> ...]" == "break"} break\n` shape, keeping `%d`. **Real events
   (`<Configure>`/`<Unmap>`/`<Destroy>`) take `_original_bind` and were never
   affected.** ⚠ This **contradicts the old note that 3.12.10's
   `unbind(seq, funcid)` removes only that funcid** — true only for
   *stock-format* bindings, which is why it checked out against `<Configure>`.

   **Measured baseline → after** (3 subs on one `bs.Button`, public API only):

   | | all live | cancel B | cancel A |
   |---|---|---|---|
   | before | `a=1 b=1 c=1` | `a=1 b=0 c=0` | `a=0 b=0 c=0` |
   | after | `a=1 b=1 c=1` | `a=1 b=0 c=1` | `a=0 b=0 c=1` |

   **Verification already done — reproduce only if you distrust it:** full suite
   `py -3.12 tests/run_gui.py` **exit 0**, main leg **899 passed** (893 + the 6
   new), 18 legs, zero failures. Clean `-W` docs build succeeded warning-free
   (CHANGELOG is in the docs via `docs/release-notes.rst` — a CHANGELOG edit
   ALWAYS needs a docs build).

   **Portability, established by measurement (don't re-litigate):** Tk's bind
   substitution codes are **identical in 8.6 and 9.0** — `%d` carries virtual-event
   `user_data` in both and dates to Tk **8.5** (TIP 165); nothing is new in 9,
   nothing was dropped. `tkinter.Misc._subst_format` is identical across CPython
   3.12/3.13/3.14 (Python does not vary it by Tk version), and `_bind`/`_unbind`
   are **byte-identical** across those three — so the emitted format matches on
   the macOS box's 3.14 too. What Tk 9 changed about events is `%D`'s *values*
   (±120 deltas / `<TouchpadScroll>` / TIP 474, handled back in 0.1.7), not any
   code's syntax. ⚠ **Neither box has Tk 9** — all three Pythons here report Tk
   **8.6.15** and the macOS box is 8.6, so the Tk 9 claim is source- and
   docs-based, NOT executed. Memory `reference_tk_bind_substitutions_86_vs_9`.

2. **#390 — should signals model emptiness at all? (DESIGN, needs the
   maintainer's call.)** Gates #389 shipping *whole*: without it `Form.clear()`
   works but leaves a bound `Signal` stale. **If the answer is no, close #390**
   and ship #389 with the limitation documented. `Signal.set(None)` raises
   unconditionally (`signal.py:248` — strictly monomorphic, type inferred from the
   seed). **Four decisions, in order:** (1) *do it at all?* (2) *declared or
   automatic?* — recommend **declared** (`Signal(v, nullable=True)`), because
   automatic-by-mode cannot cover `int` and isn't safe to lean on: `Signal(0)` is
   Python-authoritative only *while unrealized*, so the moment anything touches
   `.var`, `__call__` starts reading the IntVar and a stored `None` is lost;
   (3) *what happens to a non-nullable signal asked to go empty?* — recommend a
   public `Signal.nullable` so `ValueSignalMixin` skips rather than crashing
   `Form.clear()`; (4) *what does `map()` do over a nullable signal?* — it calls
   the transform unconditionally and infers the derived type from the first result
   (`signal.py:295, 302`), so a `None` source breaks the **documented** Date/Time
   pattern (typed `signal=` plus a `.map()`-derived text signal). **No existing
   code is at risk either way** — `set(None)` raises today, so nothing can
   currently receive it. **KEY MEASURED FINDING, don't re-derive it:** the
   dividing line is **attached-vs-not, not object-vs-native**. `NumberField(signal=)`
   / `DateField(signal=)` are **unrealized** — `ValueSignalMixin` syncs via
   `subscribe()` + `on_change` in pure Python and never touches `.var`, so **for a
   number field's value signal there is no IntVar at all**. `Checkbox(signal=)` and
   `TextField(textsignal=)` **are** the widget's `variable`/`textvariable` — there
   `None` either raises (`IntVar`) or **silently corrupts**: `StringVar.set(None)`
   stores the literal `'None'`, the widget displays it, and every subscriber gets
   the 4-character string. That is why a blanket guard relaxation must not ship.
   **Per-type "empty" values were considered and REJECTED** — `empty(int) = 0`
   contradicts the shipped `NumberField.clear()` decision, `empty(bool) = False`
   collapses tristate (#358), `date` has only a **sentinel** indistinguishable from
   data, and it makes emptiness type-dependent at every call site. The framework
   already runs both models in separate channels (`value` is `None` when empty,
   `text` is `''`) and keeping them separate is what stops either leaking into the
   other. Memory `reference_signal_nullability_attached_vs_not`.

3. **#389 — `Form.reset()` / `Form.clear()`.** Unblocked (#387 merged), design
   settled, implementation sketch on the issue. **They are DIFFERENT verbs** —
   reset = construction-time originals, clear = `None`. Both justified: `reset()`
   is **not user-implementable** (after an edit, `get()` no longer knows the
   original); `clear()` is the data-entry case. Slider clears to `min_value` (no
   null state, and that is already the de-facto seeding behavior). Needs an
   `__init__` snapshot because `set()` destroys `_data`; both must clear
   validation state.

Then the standing items: **#380 (CI)**, **#383 (kwarg sweep)**, and the harness
leak-fix.

### Then — standing infrastructure work

- **#379 harness leak-fix — NOT in #385, do it after #392.** The real root cause
  of the order-dependence was found and deliberately left out: `conftest._region()`
  returns `_region_root`, which on a decorated App **is the root**, so
  `_snapshot`/`_reset_scene` never look inside the App's `_content_frame` — **the
  scene reset has been a no-op for content widgets for the entire life of the
  shared-root harness**, and every test's widgets pile up all session. Fixing it
  makes PageStack pass with no `isolated` marker and cuts the widget leg
  **144s → 80s**. Held back because it exposes **#392** and a second latent bug
  (`test_select_change_event_value_space` picking up 5 change events from earlier
  tests — looks like stale bindtag bindings surviving destroy while Tk recycles
  widget path names; not chased down). Own branch, after #392 lands.
  ⚠ **The patch is LOST.** It was saved to a per-session temp `scratchpad/`, not
  into the repo — searched every session dir under
  `%LOCALAPPDATA%\Temp\claude\D--Development-bootstack\`, nothing. **It must be
  re-derived from the root cause above, which is fully recorded.** Lesson: a
  handoff artifact belongs in `development/` (persistent) — a bare `scratchpad/`
  path in this file does NOT survive the session.

- **#380 — CI test workflow.** `.github/workflows/` still has only `docs.yml` +
  `release.yml`, so **nothing runs the suite**; every Tk 9 bug so far was found by
  a user or by hand. Branch `ci/test-workflow` was created and deleted unused —
  recreate it. Plan agreed: **(1)** headless `ubuntu-latest` logic job —
  `test_tk9_scaling_baseline.py` monkeypatches `platform.system()`/
  `tkinter.TkVersion` so it needs **no display and no Tk 9**, and would have caught
  #375; **(2)** an `xvfb-run` Linux job for the widget suite; **(3)** fold in the
  never-collected `tests/widgets/*.py` gap. **DEFER the macOS/Tk 9 leg** — blocked
  on #378 (the suite cannot complete on Tk 9 at all), red from day one. Read the
  issue before scoping: it carries measurements showing the naive "just run
  pytest" plan fails (`-m "not gui"` selects 741 tests but yields **494 errors**
  headless — only ~222 genuinely run without a display), and warns that
  `Treeview.bbox()` returns `''` rather than erroring on an unmapped window, so
  geometry assertions **vacuously pass** headless.

### Open, additive items (not ship-blockers)

- **#396 — `emit()` and `on()` target DIFFERENT widgets on 11 wrappers.** Found
  while writing the #392 tests. Milestoned `0.2.x — Widget polish`: it is
  **additive** (a silent no-op starts working), so unlike #369/#383 it is
  patch-safe and does NOT need a minor of its own. The 11 wrappers that
  override `on()` — `textfield`, `datefield`, `numberfield`, `passwordfield`,
  `pathfield`, `select`, `spinnerfield`, `tabs`, `textarea`, `timefield`,
  `codeeditor` — retarget inner-entry sequences to the inner entry widget
  (`_INNER_ENTRY_SEQUENCES`, e.g. `textfield.py:169`), but **`emit()` is not
  overridden** and still fires on `self._internal`. So
  `field.emit("change", data=…)` **never reaches** a handler registered by
  `field.on_change(…)` — measured, not inferred (`field.on_change` binds on
  `.!textentry.!frame.!textentrypart` while `emit` generates on `.!textentry`).
  That contradicts `emit()`'s own docstring, which says it takes "the same name
  you pass to `on()`". Fix is presumably to override `emit()` alongside `on()`
  (or hoist the retarget into one shared seam so they cannot drift again) — the
  duplication IS the bug, so prefer the shared seam. Widgets whose `on`/`emit`
  agree (e.g. `Slider`) are fine, which is why the suite never caught it.

- **#383** — follow-up sweep from #381: presentation kwargs still degrading
  silently (`density`, `Tabs.orient`, `Slider.orient`, `Gauge.variant`) **plus**
  args that raise but leak a **raw `TclError`/`AttributeError`**
  (`Button.icon_position`, `Label.justify`, `Scrollbar.variant`,
  `Expander.icon_position`, `ProgressBar.mode`). Sweep **BY ARGUMENT NAME**, not
  by widget. Also folds in: **`Slider.value = None`** leaks a raw
  `TypeError: float() argument must be...` (reachable from user code via
  `form.set({'slider_key': None})`), and **`show_grid=True` is silently accepted
  on `Row` and does nothing** — not a kwarg anywhere in `src/`, but swallowed into
  the layout kwargs without error (the #394 reporter used it *while trying to
  diagnose the bug* and got no feedback).
- **#369** — the selection family disagrees on off-list values (`SelectButton`
  raises both ways; `RadioGroup` accepts at construction, raises on assignment;
  `ToggleGroup` accepts both; and where accepted, `value` says `'MX'` while
  `selection` says `None`). Wants ONE family decision, not four patches.
- **#369 and #383 are deliberately un-milestoned** — both would raise where the
  framework currently accepts, so they cannot ride the `0.2.x` patch line and need
  a minor of their own. #352 and #328 are also homeless.
- **#208** — DataTable: persist selection by record id across search/sort/page.
- **#192** — color-swatch `Select` control (decision-gated; lock shape/naming with
  the maintainer first). A `Select`-style dropdown rendering color swatches inline,
  complementing `ask_color()`. New widget or Select variant?
- **#222** — TextField live properties: expose `placeholder` / `mask` (high value
  — runtime UX toggles) and `allow_blank` / `value_format` (lower — the
  configure-delegate already works imperatively). `TextEntryPart` already supports
  them (`_placeholder_text`/`_show_char`/`_delegate_allow_blank`/
  `_delegate_value_format`). Explicitly **NOT** a `.text` setter (read-only by the
  value/text contract — write through `.value`). Clean, low-risk, no decision needed.
- **#234** — SpinnerField↔NumberField parity (live `min_value`/`max_value`/`step`,
  `on_increment`/`on_decrement`). **May be won't-do** (SpinnerField is
  intentionally simpler) — get the maintainer's call before any code.
- **#207** — ContextMenu outside-dismiss vs a `'break'` target — **DEFERRED** (no
  API implication, low/self-inflicted impact, Win/Linux only; agreed proportional
  fix if revisited = a module-level open-menu registry + dismiss-all from
  `DataTable._on_header_click`, NOT the risky grab). Analysis on the issue.
- **#328** — the E2E multi-file `@reloadable` reload test is the one OPEN piece,
  **DEFERRED** (the maintainer will write it). On PROVISIONAL `bootstack.dev`.
- **Gallery opt-in keyboard-focus ring** (future) + deferred Gallery perf (debounce
  `<Configure>`, bounded thumbnail-PhotoImage LRU, cache `_fit_caption`). Scope to
  keyboard focus, NOT hover. Memory `project_gallery_focus_ring`.
- **`add_spacer()` → public `Spacer`** — deferred, entangled with
  `feat/unified-toolbars` (the internal `Toolbar` is pack-based). Memory
  `project_unified_toolbars`.
- **Code-review follow-ups #4–#10** — cleanup/altitude items recorded in
  `docs/_dev/widget-api-audit.md` (SelectButton stale value after `options=`;
  screenshot Win64 HWND hardening; group/window/date duplication; Calendar
  batch-redraw).
- **Docs site fleshout — substantially DONE.** Remaining is only opportunistic: a
  review pass on `installation`/`quickstart` and enrichment of any still-thin page.
  Memory `project_docs_site_fleshout`.

---

## Release flow

`bump-my-version` IS available — `.venv/Scripts/bump-my-version.exe`, v1.3.0.
`bump-my-version bump patch` → push `main` + the `v*` tag → `release.yml` (PyPI +
GitHub Release) → `docs.yml` deploys. There is **no `development` branch**
(CONTRIBUTING.md + the localization workflow target `main`).

**CHANGELOG convention:** a fix commit writes `## [Unreleased]`; the `Release X`
commit renames it AND adds the `[X]:` link definition. **`main` has a GROWING
`## [Unreleased]` section** — the #381 mode guard (PR #382), PR #384, then
#387/#388/#393 and #394/#395 (which added the first `### Changed` entry). The
next cut must sweep all of them.

**⚠ Release-flow gotcha:** `bump-my-version bump patch --allow-dirty` commits
**ONLY `pyproject.toml`** — it will NOT sweep the CHANGELOG rename into the
`Release X` commit, which ships a release whose notes still say `## [Unreleased]`
and breaks `release.yml`'s section extraction. **Promote `## [Unreleased]` to the
version in its OWN commit BEFORE running `bump-my-version`.** Confirmed working on
0.1.8: `docs(changelog): promote Unreleased to 0.1.8` (`7c136b20`) ran *before*
`Release 0.1.8` (`b2f37f0f`, which again touched only `pyproject.toml`).
`release.yml` extracts ONLY the `## [x]` section, so bottom link-defs are excluded
from the GitHub Release body.

---

## Working agreements

**Hold commits until the user tests; per-commit approval.** Never commit feature
work to `main` — create a dedicated `feat/*` branch first. A fix pushed to a branch
AFTER its PR merged is **stranded** — verify it landed in `main`.

**Standing principles** (apply in every review):

- **Live properties only for legitimate runtime needs**
  (`feedback_live_properties_runtime_need`) — e.g. `surface` is **build-time, not
  live**.
- **Prefer Tk native/virtual-event bindings**; don't undo a convention without
  reason (`feedback_prefer_native_bindings_dont_undo_conventions`).
- **Describe the clean public surface in docs — no implementation/toolkit detail**
  (`feedback_no_toolkit_internals_in_docs`).
- **Adversarially verify reviewer and agent claims** — agents over-flag. The
  2026-06-22 trust audit disproved 2 of the "bugs" it was handed; the Topic-guide
  review agents over-flagged 10 of 12 pages.
- **Pause and ask when a fix outgrows its issue**
  (`feedback_pause_and_ask_when_stuck`) — #355 burned hours heading toward a
  `Select` value-model rewrite before the maintainer pointed at the ~15-line fix.
- **Test PUBLIC paths, not internal side-hacks.**

### Techniques that have repeatedly beaten static reading

- **Run an empirical probe instead of reading tangled code.** Decisive on the
  icon-DPI pipeline, the boolean-control ttk state rules, the menu window-move
  dismiss, and the #394 field alignment (FlexFrame / GridFrame / raw pack are too
  tangled to trust by eye). **Rebuild the probe rather than reading**, if one of
  these areas comes up again.
- **Tests must fail for the RIGHT reason.** A pre-fix `AttributeError` proves
  nothing — it only shows the new method doesn't exist yet. Stub the collaborator
  (e.g. a tiny fake `DateDialog` with `on_result`/`show`/`result`) so the failure
  is *behavioral*. Tests that only assert "construction doesn't raise" are what let
  #358 ship twice. Memory `feedback_tests_must_fail_for_the_right_reason`.
- **Pair any alignment/geometry assertion with a precondition** proving the setup
  really took effect, or it can pass vacuously. **Measure within one process** —
  `winfo_rooty()` is NOT comparable across two runs (different window positions).
  Memory `reference_geometry_probe_same_process`.
- **⚠ `event_generate` on a virtual event is DROPPED for some widgets while the
  window is unmapped — use the `shown_app` fixture, not `app`.** The `app`
  fixture's root is **withdrawn** (`wm_state() == 'withdrawn'`, everything
  `winfo_ismapped() == 0`). A `bs.Button` still dispatches `<<Click>>` there, but a
  composite like `bs.Slider` receives **nothing** — not even a **raw Tcl** binding
  bypassing Python entirely, which is what proves it is Tk dropping the event and
  not a bootstack wiring problem. So a payload test can look like a broken fix
  when the fix is fine. `shown_app` maps the window and it works
  (`winfo_ismapped() == 1`). **Pre-existing** — it measures identically with any
  event-system change stashed, so confirm that with `git stash` before blaming
  your own diff. Cost real time during #392. Memory
  `reference_virtual_event_needs_mapped_window`.
- **Run the BASELINE before the fix**, so a before/after transition is *observed*
  rather than assumed. That is what turned "the branch fixes only 2 of 6" from a
  suspicion into a fact.
- **A control experiment separates causation from correlation.** For #392 it was
  not enough that cancelling `sub_a` silenced `sub_b`; stripping the orphaned
  binding line by hand and watching `sub_b` come back is what proved the cause. Do
  this before filing any "X breaks Y" claim.
- **Bisect order-dependent failures; do not theorize.** A scripted prefix-bisect
  found the culprit file in 6 runs; a geometry probe turned "state pollution" into
  "reqheight 1242 > window 828, so the geometry manager unmapped it".
- **Measure the surface before scoping a sweep.** An AST pass over public
  `__init__` signatures + a construct-with-a-bogus-value probe turned "audit the
  siblings" from guesswork into a table (215 kwargs, 17/24 silently accepting) —
  which is what justified drawing #381's line at behavior modes.
- **A platform-specific backend is often constructible off-platform.**
  `_NativeContextMenu` (macOS) is a `tk.Menu` wrapper and instantiates fine on
  Windows, so macOS-only code got real coverage — and that caught a
  `TclError`-on-separator bug. Ask "can I build the other platform's object
  directly?" before accepting "unverifiable from this box".
- **Before fixing a silent no-op, find what is LEANING on it.** `Form.set()`
  applied `None` to every absent field and only worked because the write was
  discarded — repairing the sentinel alone would have turned every partial
  `form.set()` into a destructive overwrite. A no-op that has shipped for a while
  is load-bearing somewhere.
- **Prefer re-entering an existing routine over re-emitting an event by hand.**
  The #388 fix calls the entry's own `_check_if_changed()` rather than building a
  `ChangeEvent`, getting the `_prev_changed_value` bookkeeping for free.
- **⚠ Spying on an instance attribute is USELESS if the bound method was already
  captured.** `self.on_destroy(self._cleanup_x)` captures at construction, so
  `obj._cleanup_x = spy` set afterward never fires and reads as "cleanup never
  ran". **Patch the CLASS attribute before constructing**, or assert on the
  observable side effect.
- **⚠ A bulk `pathlib` rewrite flips CRLF→LF** (repo is `core.autocrlf=true`) —
  same class as the `sed -i` trap. Prefer the Edit tool; if scripting, write bytes.
  Memory `reference_autocrlf_sed_gotcha`.

---

## Recently shipped — pointers only

Full detail (root causes, decisions, gotchas) is in
**`docs/_dev/handoff-archive.md`**, indexed by issue/PR number.

| Release | Contents |
|---|---|
| unreleased → **0.2.0** | #332 internal `set_*_visible` → properties · #379/#385 menu-backend test portability · #381 `InvalidChoiceError` on bad behavior-mode kwargs · #387 `DateField` clear + `Form.set()` merge · #388 date-picker `<<Change>>` · #394/#395 field row alignment |
| **0.1.8** | macOS sizing on Tcl/Tk 9 (Aqua 72→96 DPI baseline broke `detect_scale_factor()`) |
| **0.1.7** | Tk 9 scroll-event contract (`<TouchpadScroll>`, ±120 deltas, X11 TIP 474) + attach theme repaint |
| **0.1.6** | Seven form/field/validation fixes (#362–#368, #371) |
| **0.1.5** | Boolean-control state reads + Checkbox tristate (#360) |
| **0.1.4** | `Select.add_validation_rule` restored (#357) |
| **0.1.3** | Form `editor_options` take public widget kwargs (#354) |
| **0.1.2** | Dropdown/context menus dismiss on window move (#345) |
| **0.1.1** | `pygments` declared as a runtime dependency (#344) |
| **0.1.0** | STABLE. Ship gate (#335) + theme-repaint unification (#338) + accent contrast (#340). Public compose API FROZEN under SemVer. `bootstack.dev` stays PROVISIONAL (excluded from the freeze). |

Pre-0.1.0 initiatives — also in the archive: hot reload (`bootstack dev`),
builder-function scaffolds, docs-IA 3-pillar restructure, splash screen, icon-DPI
sizing, navigation API reshape (AppShell + Workbench), layout redesign
(screen-axis grid engine), undecorated window chrome, media widget suite, the
field-family reviews, field validation redesign, and the API Reference restructure.

---

## Carryover (deferred)

- **Reference docs examples** — LARGELY DONE in PR #103 (errors/scheduling/
  shortcuts/validation enriched; new `localization.rst`). `reference/store.rst`
  already carries the persistence patterns (`from_store`/`update(**kwargs)`,
  store hygiene, version skew, window-geometry-stays-a-flag) from the AppSettings
  work. Remaining: opportunistic enrichment of any still-thin reference page.
  Memories `project_docs_initiative`, `project_app_settings_flattening`.
- **Docs build is now warning-free** (PR #106). ⚠ Keep it that way: incremental
  Sphinx builds MASK warnings — always clean-build (`rm -rf docs/_build`, then
  `sphinx-build -W --keep-going`) to verify. When adding dataclass/attribute
  docstrings, follow the attribute-docstring pattern (NO `Attributes:`/`Args:`
  block for fields) and keep any colon OFF the first line of an attribute
  docstring (see the colon-space gotcha under PR #106 above).

---

## Prior initiative — Sphinx docs + public API audit (MERGED)

Branch `feat/docs-api-improvements`, merged to `main`. Shipped: the docs structure,
the public Table (`DataTable`), the typed-event redesign, the theming + font public
APIs, the DataSource verb rename + filtering DSL, and the observable-query layer.
Full detail lives in git history and memories; only the still-live conventions and
the open backlog are kept here.

### Still-live conventions

- **Docs structure** — top-level navbar is **3 pillars** (numpy-style):
  **User Guide · Widgets · API Reference** (`docs/index.rst`). (The old **Production**
  pillar was folded into the User Guide as the **Developer tools** caption — PR after
  #330, 2026-06-24; navbar overflow stays low.)
  - **User Guide** (`docs/user-guide/index.rst`) folds Getting Started + Tasks +
    Reference + the former Production pages into ONE pillar with four `:caption:`
    toctree groups — **Getting started** (`/getting-started/*`), **How-to guides**
    (`/tasks/*`, goal-indexed recipes), **Feature guides** (`/reference/*` +
    `/production/app-settings`, subsystem-indexed usage guides — renamed from
    **Topics** 2026-06-24; both how-to and feature guides are example-rich — the split
    is goal-vs-subsystem, NOT recipe-vs-theory, so do NOT call them
    "Concepts"/"Explanation"), and **Developer tools** (`/production/cli` ·
    `hot-reload` · `debugging` · `distribution`). The leaf pages STAY in their
    `getting-started/`/`tasks/`/`reference/`/`production/` dirs (no URL churn — the
    `production/` dir name is now just an internal artifact); only the landing + top
    toctree changed. The section `index.rst` landings (incl. `production/index.rst`)
    are DELETED. **`composing-fields` → `customizing-fields`** (#323, the one accepted
    URL churn — the title clashed with "Composing with Builders"; no redirect, per the
    no-shims stance).
  - **Widgets** (`docs/widgets/index.rst`) = flat leaf pages grouped by
    `.. toctree:: :caption:` blocks (curated common-first order, NOT alphabetical);
    kept as its own pillar (large *visual* catalog). The 10 old category landing pages
    are RETIRED. `docs/api/` + `docs/deeper/` are GONE.
  - **API Reference** (`docs/api-reference/index.rst`) = the by-concept lookup layer
    (semantic groups, full-path stub titles, pandas-style card landing — see the IA
    re-cut in `docs/_dev/api-reference-restructure.md`).
  - `show_nav_level: 1` (collapsed by default). Do NOT promote sub-groups to top-level
    (pydata navbar overflows ~6+). The old "Reference page pattern" is SUPERSEDED by the
    API Reference & Guide pattern below.
- **Title casing + how-to naming** (2026-06-15) — TWO-TIER casing, applied
  consistently: **page titles (H1) and card/sidenav titles are Title Case**
  (`Building Forms`, `Images and Icons` — conjunctions like `and` stay lowercase);
  **in-page section headers are sentence case** (`Backing a widget with a data
  source`). **How-to (`/tasks/*`) titles are action-driven gerunds** —
  `‹Gerund› ‹object›` (`Displaying Data`, `Using the Clipboard`, `Showing Dialogs`),
  NOT topical nouns. **Feature guides (`/reference/*`) keep noun/subsystem titles**
  (`Events`, `Data Sources`) — that's correct, not a violation. Keep titles short enough to not
  wrap in the sidenav (~≤20 chars; drop articles: `Setting App Icons`, not `Setting an
  Application Icon`). **A page's H1, its User-Guide card title, and its sidenav entry
  must all match** (the sidenav shows the H1, so a card/H1 mismatch shows as drift).
  How-to card grid + the hidden toctree are ordered by **learning progression** (build
  a screen → compose → app structure → ship), and both must stay in the SAME order.
- **No Tkinter in docs or docstrings** — no `tk.*` types/terms unless strictly
  necessary; don't feature the escape hatch. Full `src/` docstring scrub still
  pending. LEFT BY DESIGN: `.tk`/`.var` escape-hatch property docstrings,
  `signals/integration.py` (the Tk bridge).
- **Event / theming / DataSource APIs are DONE** — reflected in the Architecture +
  Gotchas sections below and in memories `project_typed_events`,
  `project_theming_public_api`, `project_datasource_api_naming`,
  `project_datasource_change_events`. Deferred-only: the visual theme builder
  (Phase 5, near-ship — emits `bs.Theme(...)` code; do NOT build yet).

### API/cleanup backlog (deferred, memory-tracked)

- `project_capabilities_relevance` — `_core/capabilities` may be redundant now the
  public layer abstracts Tk; still imported by data/i18n/mixins.
- `project_docstring_backticks` — **DONE (PR #182):** swept to single backticks
  (`default_role="code"` makes them render as inline code). Convention is Google +
  SINGLE backticks; RST cross-ref roles (`:class:`/`:doc:`/`:ref:`) are kept (deliberate).
- `project_event_naming_revisit` — past-tense event names pending rename:
  `SideNav.on_pane_toggled`/`on_display_mode_changed`, `ListView.on_selection_changed`,
  `Calendar.on_date_selected`.
- ~~`project_signal_subscribe_subscription`~~ — **DONE (#157)**: `Signal.subscribe()`
  now returns a cancelable `streams.Handle` (was a `str` token), unifying with
  events/streams.
- `project_editfilter_public_api` — `EditFilter` DEMOTED (Tk-coupled raw text
  indices/tags); investigate a de-Tkinter-ed CodeEditor extension API before any
  re-promotion. `NOTE(editfilter-public-api)` in
  `widgets/_impl/composites/textarea/filter.py`.
- `project_window_api_hardening` — `bs.Window` leaks uncurated `**kwargs` to the
  internal Toplevel (raw Tk options in; useful `icon`/`alpha`/`toolwindow`/
  `window_style` only via the escape hatch), has no live properties
  (`title`/`size`/`topmost` are construction-only), and never releases the modal
  grab. Curate to typed params + add a live `title` + release on close. Own branch.
- `project_show_indicator_removal` — **KEEP (reversed 2026-06-15).** `show_indicator=`
  was briefly flagged for removal but is being kept: the `show_indicator=False` +
  `on_icon`/`off_icon` combo is exactly what makes an icon-driven custom checkbox, and
  removing it would orphan that. GitHub #144 closed won't-do. Do NOT re-propose removal.
- `project_enum_option_typing` — promote recurring enumerated `str` kwargs to NAMED
  `Literal` aliases in `widgets/types.py` (re-exported from `bootstack.types`); the
  ALIAS docstring carries the value list once, widget docstrings describe meaning only
  (no value enumeration — REVERSES the Code-standards "valid values per kwarg" rule for
  aliased types; keep the default). First fixes: `accent: str`→`AccentToken` in
  `form.py`/`menubar.py`. New aliases: `SelectionMode`/`IconPosition`/`LayoutKind`/
  `AutoFlow`/`ExportScope`; reuse existing `Orient`/`Fill`/`Anchor`/`Sticky`. Own branch.
- Lower-priority: bare index/landing pages (root, `widgets/`, `reference/`);
  localization/windowing `tasks/` how-tos; screenshots pending (Tooltip/Toast, 7
  Dialog pages); AppShell deferred improvements (`nav_pane_width=` not wired to
  `SideNav(pane_width=)`, hardcoded nav density/font, group active-child highlight +
  indentation, footer non-page widgets).

---

## API Reference & Guide page pattern (established — follow exactly)

The docs are a **Diátaxis-style split** (PR #107): a narrative layer (**Widgets** +
**Guides**) plus a **unified, complete API Reference** that mirrors each submodule's
`__all__`. **Load-bearing rule: every object has exactly ONE autodoc home, and it
lives in the API Reference.** Narrative pages cross-link in (`:class:` / `:func:` /
`:meth:`) and may carry a *table-only* `autosummary` summary; they never re-document.
A second autodoc home reintroduces the "duplicate object description" warnings PR #106
removed. Full brief + all staged-sweep decisions: `docs/_dev/api-reference-restructure.md`.
Memory `project_api_reference_restructure`.

### The autosummary templates (locked, PR #107 + Stage 2)

THREE custom templates under `docs/_templates/autosummary/`, one per documenter
kind autosummary uses for the data surface — `class.rst`, `function.rst`,
`data.rst`. **All THREE must title the stub page with the bare `{{ objname }}`**
(not `{{ fullname }}`). This is load-bearing: autosummary picks the template by
object kind, and the **stub's title is what the sidebar shows**. The built-in
fallback templates title with the full dotted path (`bootstack.data.col`), so
relying on the fallback for functions/data produces a sidebar where classes read
bare (`MemoryDataSource`) but functions/aliases read fully-qualified
(`bootstack.data.col`) — the exact inconsistency Stage 2 fixed. Keep the bare-title
line identical across all three.

`class.rst` (also serves dataclasses + Protocols):

```rst
{{ objname | escape | underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :members:
   :inherited-members:
   :show-inheritance:
```

`function.rst` → `.. autofunction:: {{ objname }}`; `data.rst` →
`.. autodata:: {{ objname }}` — each with the same bare-title + `currentmodule`
header.

- `:inherited-members:` (class template) is what makes a concrete-source stub
  **complete** (e.g. `SqliteDataSource` shows inherited
  `save`/`on_change`/`observe`/`export_csv`).
- The Protocol page stays noise-free because `undoc-members` is off and there is no
  `:special-members:` — `_private`/dunder/Generic members are filtered out.
- Some type aliases classify as class-like and pick up `class.rst` (e.g.
  `Primitive`), others as data and pick up `data.rst` (e.g. `Record`) — both now
  title bare, so it no longer matters which. A new documenter kind a future module
  needs (e.g. `exception.rst`) must get the SAME bare-title treatment.
- **Per-class curation** (a class needing different members than the global
  `class.rst`): add a per-class template file `_templates/autosummary/<name>.rst`
  and point that class's `autosummary` entry at it with `:template: <name>` —
  **WITHOUT the `.rst` extension**. Sphinx's autosummary resolves `:template: X`
  as `autosummary/X.rst`; passing `signal.rst` builds `autosummary/signal.rst.rst`,
  silently misses, and falls back to the built-in `base.rst` (full title, no
  members) — NOT even `class.rst`. `:template:` applies to every name in that
  directive block, so put the curated class in its own one-name block. Exemplar:
  `signal.rst` (Signal needs `__call__` shown + `tk`/`var`/`name`/`from_variable`
  excluded); wired in `api-reference/signals.rst` as `:template: signal`.

### API Reference page recipe (the autodoc home — one per submodule)

A page like `docs/api-reference/data.rst`. Text-only, **NO screenshots, NO hero**.

1. Title = the dotted module path (`bootstack.data`), then `.. currentmodule::` it.
2. One prose paragraph orienting the module + a `:doc:` link to its Guide.
3. **Group the surface into labeled sections** (`---` headings), each: a one-sentence
   prose lead-in, then an `.. autosummary::` table with `:toctree: generated` and
   `:nosignatures:`. The table renders as a two-column **name | first-line-summary**
   table (pandas/SciPy style) and toctrees each name into an auto-generated per-object
   stub under `docs/api-reference/generated/` (gitignored — regenerates at build).
   **Grouping conventions** (from the batch-1 review, applied across all pages):
   (a) **Don't mix kinds in one list** — separate the things you *call*
   (functions/constructors) from the *supporting types* they produce/consume, from
   *enumerations/aliases*. E.g. `events` = payload sections + "Supporting types"
   (`TabRef`, a value carried *inside* a payload) + "Enumerations" (`ChangeReason`…);
   `data` = "Query language" (`col`/`any_of`/`all_of`) vs "Query expression types"
   (`Column`/`Condition`/`SortKey`) vs "Type aliases" (`Record`/`Primitive`). A type
   that only appears *inside* another object (not handed to the user directly) is a
   supporting type, not a primary entry. (b) **Order sections most-reached-for first,
   lowest-level lookups last** — primary objects → common callables → their supporting
   types → feature areas → bare type aliases at the bottom (`data` order: Data sources
   → Query language → Query expression types → Readers and writers → Type aliases).
   (c) **Don't sub-section a small/uniform module** — follow the
   `bootstack.streams` model (intro prose + ONE `autosummary` table, no `---`
   sub-headings) whenever a module is just a few names of the same kind. Sub-section
   only when the surface is large OR genuinely mixes kinds (a). `streams`
   (`Stream`/`Handle`), `validation` (`ValidationRule`/`ValidationResult`),
   `scheduling` (`Schedule`/`Job`), `shortcuts` (3), and `errors` (5 exceptions) are
   all single-table; `data`/`events`/`style` earn their groups. The intro carries
   any rule-vs-result / base-vs-specific nuance — don't spend a heading on it.
   (d) **Order ENTRIES within a group ALPHABETICALLY** — the API Reference is the
   lookup layer, so within-group order should be predictable for scanning (the
   pandas/NumPy convention), NOT curated/common-first. Curated common-first order
   is the GUIDES' job (the `widgets/index.rst` caption toctrees keep it). The
   category grouping + a one-line lead-in already carry the semantics; clusters
   mostly stay adjacent alphabetically anyway (`Radio`/`RadioGroup`/`RadioToggleButton`,
   `Select`/`SelectButton`, `ToggleButton`/`ToggleGroup`). (e) The audit also
   surfaces half-public names to demote — e.g. `TraceOperation` (internal trace
   tag, no public signature exposes it) was dropped from `bootstack.signals.__all__`
   during this sweep.
4. List **exactly** the module's `__all__` across the grouped tables (the reference
   IS `__all__`). Good first-line docstrings matter — that line is the summary cell.
5. Wire the page into `docs/api-reference/index.rst`'s toctree.

Re-exported names (shallowest path wins): a name exported at two public paths gets
ONE stub, on the **shallowest** page (`Signal` → top-level `bootstack` page). Deeper
module pages list it in a **table-only** summary (no `:toctree:`, links up to the
stub) and own only their module-local names.

### Guide page recipe (the former `reference/*` prose pages)

A page like `docs/reference/data-sources.rst`. This is the teaching layer.
**Guiding principle: the API Reference is a LAST RESORT — the Guide carries the
practical teaching load** (generous worked examples, common compositions, recipes,
do/don't). A user should build real things from the Guide alone.

1. Prose intro → task-ordered usage sections (code blocks) → See also.
2. **No bottom `autoclass`** — instead end with an **"API reference"** section: a
   one-line pointer (`:doc:` link to the API Reference page) + an at-a-glance
   `.. autosummary::` table **WITHOUT `:toctree:`** (a table is NOT an object
   description, so it's not a second autodoc home; its links resolve to the stubs).
3. Cross-link types inline with roles (`:class:` / `:func:` / `:meth:` / `:data:`)
   at the **public home path** (`bootstack.data.SqliteDataSource`, not the impl path).
4. Inline usage only — NO separate Full Example file. Non-visual: NO screenshots.

### Verify (every stage)

Clean-build, always — incremental builds MASK warnings:
`rm -rf docs/_build && sphinx-build -b html docs docs/_build/html -W --keep-going`.
Build is warning-free; keep it there. Attribute-docstring rules (PR #106) still
apply (no `Attributes:`/`Args:` for dataclass fields; no colon on the first line of
an attribute docstring). A `-n` nitpicky build surfaces dangling cross-refs once a
home moves — fix the link or add a `nitpick_ignore_regex`.

---

## Reviewing a widget + docs standards (read first)

**Before any widget review or widget-docs work, read
`docs/_dev/widget-review-and-docs-standards.md`** — the consolidated checklist.
It is the single source of truth for both halves; the highlights:

- **A review is audit → fix → test → document → file follow-ups**, not a
  read-through. Audit the public wrapper vs `_impl` for correctness bugs AND
  unexposed capability. Recurring bug classes: value clamping (setters + re-clamp
  on range change), disabled state honored on *every* input path (incl. Home/End),
  event consistency (keyboard jumps commit like a drag-release), no Tab focus-trap.
  Then API hygiene (typed params, `on_*` payload audit, drop dead kwargs,
  live-vs-construction props). **File additive features / out-of-scope bugs as
  tracked issues — don't scope-creep the review branch.**
- **Docs: the Guide teaches; the API Reference is a last resort.** **Lead with the
  mental model** (foundational concept up front, not buried later). **No
  kitchen-sink — one idea per paragraph, scannable**, teach the decisions not every
  kwarg. Examples are **tight, API-verified, with the relevant import on first
  use** (and they must run). Use a `.. note::` for an **adjacent-but-distinct topic**
  (placed by the relevant screenshot, linking the other section) rather than inline
  prose — keep each topic its own section/TOC entry. Document the **Events** (change
  vs commit — public, not an impl detail) and **Keyboard** behavior of interactive
  widgets. **One screenshot per visually-distinct usage section**, not just the hero;
  a behavioral-only feature (e.g. step snapping) gets prose, no screenshot.
  Sentence-case section headers; Title Case page title.
- Verify: GUI test files run **one per process** (#150); `tests/test_public_surface.py`
  green; examples run; clean `-W` docs build; held for user test + per-commit approval.

## Widget documentation pattern (established — follow exactly)

> ⚠ **Migrating a widget = also clean up its public API** (the maintainer's
> standing pattern, memory `feedback_cleanup_api_while_documenting`). When you home
> a widget into the API Reference, audit it the way `App`/`AppShell`/`Window` were:
> drop dead/redundant kwargs, demote set-once config from runtime properties to
> construction-only (a property is "live" only if changing it has a complete effect
> a user would bind to a control), de-Tkinter leaks, fix docstring nits.
> **In particular, complete the typed-payload `on_*` audit for that widget** (memory
> `project_typed_event_payloads`, INCOMPLETE): a DATA event gets its specific
> `bootstack.events` payload type in `@overload` + impl signature; a NATIVE event
> (`click`/`hover`/`focus`/`blur`/`resize`) keeps `Event`. Known offenders: the
> boolean/selection controls (`Checkbox` etc.) still type `on_change`/`on_check`/…
> as generic `Callable[[Event]]`. (Payloads render in the autodoc "Overloads:"
> block, so fixing the source is enough.)

1. **Audit** — Explore agent comparing public wrapper vs `_impl/` internals.
2. **Fix wrapper** — typed params (`AccentToken`, the widget's own per-widget
   `variant` Literal, `WidgetDensity`);
   `@overload` event shorthands; no low-level color kwargs; layout via `**kwargs`
   + `_split_layout_kwargs`; catch-all must be `**kwargs` not `**extra_kw`.
3. **`docs/widgets/<widget>.rst`** (NOTE: was `docs/api/` — moved 2026-06-04) —
   intro sentence → hero screenshot → Usage sections (code block then screenshot)
   → Widget sizing include → See also → table-only `autosummary` API section +
   cross-links (NO bottom `autoclass`, per the Guide-page recipe) → Full Example
   literalinclude. No intro code block above hero.
4. **`docs/examples/<widget>.py`** — runnable visual-states-only demo. No
   `app.tk.after()`, no screenshot scaffolding, no `fill="x"` in RST snippets.
5. **`docs/screenshots/<widget>.py`** — SCENES dict. Each scene: own `bs.App`,
   tight `size=(W,H)`, `HStack(fill="x")` for button rows to avoid centering
   offset, `app.run()`. Hero for button/action widgets: single representative
   state with menu/popdown open if applicable.
6. **Screenshots:** `py -3.12 docs/scripts/take_screenshots.py <widget> [--scene X] [--light]`
   Outputs: `docs/_static/examples/<widget>-<scene>-light/dark.png`
7. **Wire** into the matching `:caption:` toctree in `docs/widgets/index.rst`
   (category landing pages are retired — captions group the widgets now).
8. **Commit** on a dedicated `feat/*`/`docs/*` branch.

### Screenshot image pattern

```rst
.. image:: /_static/examples/<widget>-<scene>-light.png
   :class: bs-screenshot-light
   :alt: <Widget> <scene> — light theme

.. image:: /_static/examples/<widget>-<scene>-dark.png
   :class: bs-screenshot-dark
   :alt: <Widget> <scene> — dark theme
```

Hero uses `-hero-light/dark.png`. Dialogs add `bs-dialog-screenshot` to the class
(e.g. `:class: bs-screenshot-light bs-dialog-screenshot`).
Margin/radius owned by `docs/_static/custom.css` — no inline styles.

### Widget sizing section pattern

```rst
Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst
```

Path is file-relative from `docs/api/`. Omit from dialog pages.

---

## Gotchas

### Layout and wrappers
- **Self-placement via `**kwargs`** — `fill`, `expand`, `anchor`, `row`, `column` etc.
  are NOT explicit params. Route through `self._split_layout_kwargs(kwargs)`.
- **`**kwargs` not `**extra_kw`** — catch-all must be named `**kwargs` throughout.
- **User options MERGE OVER framework kwargs; structural keys RAISE** (#363,
  0.1.6). A widget that builds another widget for you — `Form`'s `editor_options`,
  `MenuButton`'s `menu_options`, the `**kwargs` passthrough on `ButtonGroup.add` /
  `RadioGroup.add` / `Toolbar.add_widget` — must route through
  **`merge_kwargs`** (`widgets/_core/kwargs.py`): the caller's options win, and a
  short `reserved` map (keys the widget must own — its `parent`, the command that
  emits its events) raises `BootstackError` naming the API called and what to use
  instead. Splatting a user dict alongside explicit kwargs raises
  `TypeError: got multiple values for keyword argument` from an internal class the
  caller never wrote — that was a live bug in six widgets. **Legacy exception:**
  `MenuButton.__init__`'s `_RESERVED_INTERNAL_KEYS` still SILENTLY SKIPS collisions
  (so `bs.MenuButton("X", command=fn)` quietly does nothing). Flipping a silent
  no-op to a raise can break working user code, so converging it is a 0.2.0 item —
  do NOT copy the silent-skip pattern into new code.
- **`margin_x=` / `margin_y=`** — axis-specific external spacing. Never `padx=`/`pady=`.
- **`.. include::` path is file-relative** — from `docs/api/`, use `../shared/widget-sizing.rst`.

### Screenshots
- **HStack centering** — App's VStack centers children. For button-row scenes, wrap in
  `HStack(fill="x")` so buttons are left-aligned, not centered with dead space on the left.
- **No `size=` by default** — omit `size=` from `bs.App` in screenshot scenes unless there
  is a specific reason (popdown/dropdown needs room to render inside the capture bbox). Let
  the window auto-fit its content. For input/field/slider rows use `minsize=(720, 1)` to
  enforce a minimum width without locking height. Never add `size=` just to "feel right".
- **Popdown menus in screenshots** — runner sets app `topmost=True` at t=800ms, grabs at
  t=950ms. Call `mb.show_menu()` at t=850ms (after topmost set, before grab). Size the
  app window tall enough to contain the menu within its capture bbox — the menu Toplevel
  is captured via `ImageGrab.grab(bbox=app_region)` which is a screen grab, not a window
  grab.
- **`_ToplevelContextMenu` topmost** — `show()` now sets `-topmost True` on the
  overrideredirect Toplevel so it appears above a parent with `-topmost True`.
- **SelectBox popup topmost** — `_create_popup_toplevel` sets `-topmost True` so the
  popup appears above the screenshot runner's topmost window.
- **Screenshot runner 2px inset** — crops 2px from each edge to remove Windows border artifact.
- **Dialog hero pattern** — open non-modally at t=200ms, lift dialog at t=850ms, screenshot
  at t=950ms. Use `app._capture_target = <toplevel>` to capture a dialog instead of the app.
- **Full-app widget sizing** — PageStack, SideNav, AppShell use `fill="both", expand=True`
  and need `size=(W, H)` (not `minsize=`) to give the canvas a defined size.
- **Navigation window padding** — use `padding=8` on the App for full-app nav scenes to
  give footer-pinned items breathing room at the bottom edge.
- **Tabs vertical scene** — use `padding=16` and `size=(W, H)` since `fill="both"` needs
  a canvas; `minsize=` is sufficient for horizontal tabs scenes.

### MenuButton specifics
- **`icon_only` inferred** — `DropdownButton.__init__` auto-sets `icon_only=True` in
  `style_options` when `icon` is in style_options and `text` is None/empty. The public
  wrapper doesn't need to infer it.
- **Menubutton layout centering** — `Menubutton.label` has `side="left"` in the ttk
  layout. When `icon_only=True` and no dropdown, drop `side="left"` so the label fills
  the full content area and `anchor="center"` can take effect.
- **Item type names** — public API uses `'command'`, `'check'`, `'radio'`, `'separator'`.
  Internal ContextMenu uses `'checkbutton'` / `'radiobutton'`. Translate at the wrapper
  boundary via `_ITEM_TYPE_MAP`. Legacy names accepted for backwards compat.
- **Radio group variable** — `add_radio_item()` auto-creates a shared `StringVar` on the
  internal widget. Values are stored as strings internally. Use `selected=True` to
  pre-select. Multiple `add_radio_item()` calls share one group variable per MenuButton.
- **`show_menu()` respects disabled state** — guard with
  `self._internal.instate(("!disabled", "!readonly"))` before delegating.
- **`disabled` property** — use `instate(("disabled",))`, not string comparison on `cget`.
- **`shortcut=` in `add_item()`** — display-only label. Passes through `format_shortcut()`
  which handles: registered key name → platform display, `"Mod+S"` pattern → `"Ctrl+S"` /
  `"⌘S"` (no registration required), literal string → pass-through.
- **MenuButton hero pattern** — show a standalone "Actions" button (Edit/Duplicate/Archive/
  Delete), NOT a File/Edit/View menubar pattern. Shortcuts section uses the File menu example.

### Style rebuild pattern
- **`configure_style_options` alone doesn't rebuild** — it only updates the stored
  `_style_options` dict. Call `rebuild_style()` immediately after to regenerate the TTK
  style with the new options and apply it to the widget.
- **`emit` wraps `event_generate`** — `PublicWidgetBase.emit(event, data=...)` calls
  `self._internal.event_generate(sequence, data=data)` directly. For internal widgets
  use `event_generate` with `data=` natively (the event system is patched to support it).

### Widgets and API
- **Public namespace is CURATED (PR #104)** — top-level `bootstack` (`bs.*`) holds
  ONLY what you compose a UI from: every widget, `App`/`AppShell`/`Window`,
  `Signal`, the dialog VERBS (`alert`/`confirm`/`ask_*`/`toast`), and
  `set_theme`/`toggle_theme`. Import everything else from its submodule —
  `from bootstack.data import SqliteDataSource, col`; `from bootstack.style import
  Theme, get_theme_color`; `from bootstack.i18n import L, LV`;
  `from bootstack.validation import ValidationRule`; `from bootstack.events import
  Event, Subscription`; `from bootstack.streams import Stream`;
  `from bootstack.scheduling import Schedule`; `from bootstack.shortcuts import
  get_shortcuts`; `from bootstack.store import Store`; `from bootstack.errors
  import ...`; `from bootstack.types import AccentToken`; dialog CLASSES
  `from bootstack.dialogs import FormDialog`. `MessageCatalog`/`IntlFormatter`/
  `get_current_app`/`Image` are INTERNAL (not public). Do NOT write `bs.Theme`/
  `bs.col`/`bs.SqliteDataSource`/`bs.FormDialog` etc. — they no longer exist at
  top level. Map: the `docs/api-reference/index.rst` landing (public-contract +
  submodule list; `api-overview` was retired into it); guard:
  `tests/test_public_surface.py`. Memory `project_toplevel_api_surface`.
- **Dialogs live in `bootstack.dialogs`** — impl under `bootstack/dialogs/_impl/`,
  public façade `bootstack/dialogs/__init__.py` (verbs + classes).
  `bootstack.widgets.dialogs` is GONE. Internal deep imports use
  `bootstack.dialogs._impl.<module>`.
- **`disabled` on Label** — not appropriate. Label is display-only.
- **`color=` / `background_color=`** — removed. Use `accent=` / `surface=`.
- **`bs.App` / `bs.AppShell` config is FLAT kwargs** (settings-flattening, branch
  `feat/app-settings-flatten`). All former `AppSettings` fields are direct
  constructor kwargs — `theme`, `light_theme`, `dark_theme`,
  `follow_system_appearance`, `available_themes`, `inherit_surface_color`,
  `locale`, `localize_mode`, `window_style`, `macos_quit_behavior`,
  `remember_window_state`, `state_path`, `app_author`, `app_version`. There is
  **NO public `settings=` / `AppSettings` / `app.settings`** (clean break, no
  shim — passing `settings=` raises `TypeError`). `AppSettings` survives only as
  an internal resolved-config holder; `get_app_settings()` is internal-only.
  Read/write config as symmetric `app.*` properties: `app.theme`/`app.locale`/
  `app.title` set live; locale-derived values are flat read-only props
  (`app.locale_date_format`, `app.locale_time_format`, `app.locale_decimal`,
  `app.locale_thousands`, `app.locale_language`). Config-change events:
  `app.on_theme_change(fn)` (→ theme name) and `app.on_locale_change(fn)`
  (→ locale code). Persistence: `bs.App.from_store(store)` (tolerant of version
  skew — filters to known kwargs) + `store.update(theme=...)` write-back. Shared
  impl in `widgets/_core/app_config.py` (`AppConfigMixin`, `APP_CONFIG_KWARGS`).
- **`bs.Signal()` is safe at module level** — the backing Tk var is created lazily on first widget binding.
- **`textsignal=`** — standard kwarg for text-bearing widgets. `signal=` for non-text
  (Slider, Checkbox, etc.). Never expose `textvariable=` / `variable=` publicly.
- **`TTKWrapperBase.__init__` overwrites `self._accent`** — store accent before `super().__init__()`,
  re-assign after.
- **`<<BsThemeChanged>>`** fires after full rebuild (use this). `<<ThemeChanged>>` fires before.
- **Canvas/imperatively-painted widgets — theme repaint:** NEVER bind ttk
  `<<ThemeChanged>>` on the **root/toplevel** — it re-fires **~1400× per rebuild**
  (once per style reconfigure); root-bound × instances = thousands of redraws (was
  the gallery's ~3s toggle lag, PR #180). Re-resolve colors via the **STD
  `Publisher`** (fires once, after rebuild) and **gate the redraw on visibility**.
  `Frame` subclasses: call `self._enable_theme_repaint(self._redraw)` (the shared
  hook — subscribes, gates on `winfo_viewable()`, defers off-screen to `<Map>`,
  releases on `<Destroy>`). Non-`Frame` (Slider/RangeSlider/chrome): publisher +
  own gate. Memory `reference_theme_repaint_mechanisms`. **#177 DONE (PR #181):**
  textarea/code-editor (`StyleRegistry`/`SearchOverlay`/`IndentGuides`) migrated onto
  `<<BsThemeChanged>>`; dead `FloodGauge` deleted. Nothing left on the racy event.
- **`bs.SelectButton`** — button-styled non-editable picker. Distinct from `bs.MenuButton`
  (action menu) and `bs.Select` (editable combobox).
- **`bs.DataTable`** (renamed from `bs.Table`) — works with any
  `DataSourceProtocol` source (decoupled from `SqliteDataSource`); identity reads
  route through `_record_id`/`_public_record`/`_internal_fields`. Defaults to an
  in-memory `SqliteDataSource` when given `rows=`. No built-in border (wrap in a
  `Card`/`Frame`); `density=` and a footer separator are supported.
- **`RadioGroup.set()` validates against keys**, not values.
- **`bs.Form` uses `col_count=`**, not `columns=`.
- **`ToggleGroup(padding=N)`** — bug fixed; safe to pass.
- **`value=` ignored when `signal=` also passed** on boolean widgets — seed the Signal directly.

### Boolean controls
- **Switch/ToggleButton unsupported features** — Switch: no `on_icon`/`off_icon`/`icon_only`/
  `show_indicator`/`tristate`/`density`. ToggleButton: no `tristate`/`show_indicator`.
  Checkbox: only widget supporting `tristate`.
- **Density** — Checkbox and Switch do NOT support `density=`. ToggleButton DOES.
- **Sphinx signatures** — give each subclass its own `__init__` to avoid inheriting
  unsupported params. Use `:inherited-members: PublicWidgetBase` in autoclass.

### Layout widgets
- **`height=`/`width=` on VStack/HStack** — setting one collapses the other axis.
  Add `fill=` + `expand=True` for the unconstrained axis.
- **`show_border=True` needs padding** — border is inside the frame edge.
- **`Grid columns=N` shorthand** — `columns=3` ≡ `[1,1,1]`. `0` == `'auto'`.
- **`**extra_kw` removed from layout wrappers** — `Card`, `GroupBox`, `VStack`,
  `HStack`, `Grid` only accept `**kwargs`.
- **`variant=` removed from VStack/HStack** — use `bs.Card` for card-variant layout.

### Dialogs
- **7 doc pages** — `dialogs.rst` is toctree-only. `ColorDropperDialog` is internal.
- **`content_builder`** fills a PUBLIC content `Column` set as the active parent —
  write the body parent-free (`def build(): bs.Label(...)`), like an App body;
  `Dialog(padding=, gap=)` configures it. `def build(content)` gets an explicit
  handle; old `def build(frame): with bs.Column(parent=frame)` still works (frame
  is the public Column, via the `_RawTkContainer` bridge in `_resolve_parent`).
  bootstack's own verb/Form dialogs render raw and opt out with `_raw_content=True`.
- **`Frame.configure(surface=...)`** does NOT work at runtime — use `configure_style_options(surface=...)`.
- **`Dialog.__init__`** is fully keyword-only; `parent=` not `master=`; `min_size=`/`max_size=`.
- **`ButtonRole`** values: `"primary"`, `"secondary"`, `"danger"`, `"cancel"`.
- **`bs-dialog-screenshot` CSS class** — dialog screenshots only; adds border + drop shadow.

### Sliders / fields
- **Slider/RangeSlider spacing** — `VStack gap=` does not visually separate tracks.
  Use `margin_y=10` on each widget. Track heights: plain ≈ 24px, ticks ≈ 45px, badge+ticks ≈ 65px.
- **Screenshot widths** — use `minsize=(720, 1)` for all input/field/slider scenes.
- **`anchor_items="baseline"`** — invalid. Use `"s"`.
- **`select.py` / `calendar.py` shadow stdlib** — use `selectfield.py` and `calendarwidget.py`.

### Misc
- **American English** — all docstrings and user-facing text. Spelling scrub still pending.
- **`font="heading-md"`** not `"heading-md[bold]"` — headings already bold.
- **`&` in `bs.Label` text** — Tkinter strips `&`. Use `"and"`.
- **`Expander` is internal** — use `bs.Accordion`.
- **Run examples after editing** — always `python docs/examples/<widget>.py` before committing.
- **Dark mode Note admonition** — override in `custom.css` inside `html[data-theme="dark"]`:
  `--pst-color-info: #6ea8fe; --pst-color-info-bg: #0d306e`.
- **`Shortcuts` service** — public surface is `bootstack.shortcuts`: the `Shortcuts`
  class, the `Shortcut` dataclass, and the `get_shortcuts()` accessor.
  `register(key, "Mod+S", fn)` + `bind_to(app)` wires the keyboard handler.
  `format_shortcut(spec)` (in `_runtime/shortcuts.py`) resolves display text only
  (no binding side effect) — it is INTERNAL, not exported from `bootstack.shortcuts`.

---

## Architecture (settled)

**Public API** is a composition layer over internal widgets. Public widgets are plain Python
objects (NOT `tk.Widget` subclasses) holding `self._internal`.

Constructor order: resolve parent → split layout kwargs → construct internal → attach to parent.
`_split_layout_kwargs` strips pack/grid/place keys before internal widget construction.

`.tk` property returns the underlying ttk widget — escape hatch, user's responsibility.

### Context-manager parenting

```python
with bs.App(title="Demo", padding=16, gap=8) as app:
    with bs.HStack(gap=4):
        bs.Label("Hello")
        bs.Button("OK", on_click=lambda: ...)
app.run()
```

`__enter__` pushes container, `__exit__` pops. App hides on enter, shows on exit.

### Events  (redesigned 2026-06-05 — see memory `project_typed_events`)

```python
sub = widget.on_change(handler)   # → Subscription (cancellable)
widget.on_change().debounce(300).listen(handler)  # → Stream (composable)
```

All `on_*()` shorthands use `@overload`: no-arg → `Stream`, with handler → `Subscription`.

**What the handler receives** (the redesign):
- **Data events** (`change`, `input`, `select`, validation, …) → the typed
  payload dataclass, **unpacked**: `on_change(lambda e: e.value)`. Payloads live
  in `bootstack.events` (the catalog) — `bs.events.ChangeEvent`, `SliderEvent`,
  etc. Namespaced there ONLY, not top-level. ListView item events are the
  exception: a plain record `dict` (`e["field"]`).
- **Native events** (`click`, `hover`, `focus`, `blur`, `resize`, key, scroll) →
  a curated, Tk-free `Event`: `widget`, `x/y/x_root/y_root`, `width/height`,
  `delta`, modifier bools `ctrl/shift/alt/meta`, clean `key/char`, `time`.
- `Button`/`Label` `on_click()` METHOD now passes the `Event` (the no-arg
  `on_click=` constructor command is unchanged).
- The generic `on(name, handler)` is typed `Callable[[Any], Any]` (string-keyed,
  can't infer the payload); the precise types are on the `on_<event>()` shorthands.
- Transform happens in `adapt_handler()` (`widgets/_core/base.py`); emit sites
  build the dataclass: `event_generate("<<Change>>", data=ChangeEvent(...))`.
  `_runtime/events.py` (the data-cache transport) is untouched.

### Signals

```python
sig = bs.Signal(value)
bs.TextField(textsignal=sig)   # two-way binding
sig.subscribe(lambda v: ...)
```

### Layout

⚠ **This file's layout examples were STALE and are only partly swept — verify
against a real signature before copying any of them.** Measured 2026-07-30 via
`inspect.signature`:

- **`bs.HStack` / `bs.VStack` DO NOT EXIST** — the stacks are **`bs.Row`** and
  **`bs.Column`**. Every `HStack`/`VStack` still left in this file (the screenshot
  patterns around the "HStack centering" gotcha, the layout-widget gotchas, the
  context-manager example) is wrong. **Not yet swept** — do it opportunistically,
  checking each replacement, rather than in one blind find-and-replace.
- **`fill=` / `expand=` on a flex child now RAISE**, they don't degrade:
  `BootstackError: fill is not a valid layout option for a Row/Column/Grid child.
  Use grow= / align_self= (and justify_self= in a Grid) instead`. Good error —
  trust it over this file.
- **Container defaults are `horizontal_items=` / `vertical_items=` /
  `grow_items=` / `weights=`.** `fill_items=`, `expand_items=`, `anchor_items=`
  and `sticky_items=` are all GONE from `Row`/`Column`/`Grid`.

```python
bs.Column(padding=20, gap=12)
bs.Row(gap=8, vertical_items="center")
bs.Grid(columns=["auto", 1], gap=8)
```

Full current signatures — `Row`/`Column`: `parent`, `horizontal_items`,
`vertical_items`, `grow_items`, `weights`, `gap`, `padding`, `surface`,
`show_border`, `width`, `height`, `**kwargs`. `Grid` swaps `grow_items`/`weights`
for `columns`, `rows`, `auto_flow`.

---

## Source structure

```
src/bootstack/
├── _core/       infrastructure (capabilities, colorutils, mixins, publisher, images)
├── _runtime/    Tk patches (app, toplevel, menu, shortcuts, events)
├── assets/      locales, icons (themes are now Python, see style/themes/)
├── data/        DataSource (Base, Memory, Sqlite, File)
├── dialogs/     dialog implementations
├── signals/     Signal, TraceOperation
├── style/       Theme (public), themes/ (built-in Theme instances),
│                Style/Typography/Font (internal engine), builders
├── validation/  ValidationRule, ValidationResult
└── widgets/
    ├── _core/   public framework internals (base, container, context, events)
    ├── _impl/   internal implementation (primitives, composites, mixins)
    ├── app.py, button.py, ...  (~40 public wrapper files)
    └── types.py AccentToken, WidgetDensity, SurfaceToken, per-widget variant Literals, etc.
```

---

## Key API reference

```python
import bootstack as bs

with bs.App(title="My App", size=(800,600), padding=16, gap=8) as app:
    sig = bs.Signal("World")
    bs.Label("Hello!", font="heading-lg")
    bs.Button("OK", accent="primary", on_click=lambda: ...)
app.run()

# AppShell
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
bs.confirm("Delete?")          # → bool
bs.ask_string("Name:")         # → str | None
bs.ask_integer("Age:", min_value=0)  # → int | None
bs.ask_date("Pick date:")      # → date | None
bs.ask_color()                 # → ColorChoice | None
bs.ask_font()                  # → Font | None
```

---

## Code standards

**Docstrings:** one-line summary + description + `Args:` (name: description, no types).
Single backtick `` `X` `` — never double. No RST roles. Valid values + defaults per kwarg.

**Dataclasses — document fields with ATTRIBUTE DOCSTRINGS, never `Args:`.** Put a
one-line class summary (+ optional prose), then a short docstring string literal
*directly under each field*. Do NOT also list the fields in an `Args:` block —
that renders them twice (a synthesized "Parameters" block + the attribute list).
autodoc `:members:` then renders each field once with its type + description.
(Functions/methods keep using `Args:`.) The conf setting
`autodoc_typehints_description_target = "documented"` suppresses the redundant
synthesized Parameters block for dataclasses. Exemplars: `bootstack.events`
payloads, `bootstack.style.theme.Theme`.

⚠ **No colon on the FIRST LINE of an attribute docstring.** napoleon splits the
first line at the first `:` and jams the pre-colon text into a bogus `:type:`
field — SILENTLY mangling the rendered type (it only *warns* when the split also
breaks a backtick pair). A colon on line 2+ is fine. Use an em-dash/period to
introduce an enum list: `"""Side to pack against — \`'top'\`, \`'bottom'\`..."""`,
not `"""Side to pack against: ..."""`. (PR #106 swept all existing offenders.)

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

---

## Open bugs

- `value=` silently ignored when `signal=`/`variable=` also passed (all boolean widgets)
- `Style._tk_widgets` grows forever — partially resolved; pages are never destroyed

ButtonGroup/ToggleGroup now have **separate** style builders: `ButtonGroup`
(action widgets) uses `style/builders/buttongroup.py`; `ToggleGroup` (selection
widgets) uses `style/builders/togglegroup.py` (registered for the `ToggleGroup`
ttk class; composite sets `ttk_class='ToggleGroup'`). They share the baked
`button_group_*` nine-patch shapes but have independent colors/normal states. The
old ToggleGroup solid-variant contrast issue is fixed.
