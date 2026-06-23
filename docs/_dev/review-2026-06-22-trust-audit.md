# Trust audit — 2026-06-22 session (14 PRs + `0.1.0a14`)

Adversarial review of all work merged to `main` in the ~6 hours ending
`5def69b6` (PRs #289, #291–#299 + the `0.1.0a14` release), prompted by the
maintainer finding repeated errors/hallucinations from the session's agent.
Method: five parallel reviewers (one per PR cluster), a clean `-W` docs build,
and the full GUI suite (`tests/run_gui.py`). Result: **605 passed, 1 failed**;
docs build clean.

Severity legend: 🔴 broken on `main` · 🟠 real logic bug · 🟡 hallucination /
mislabel / doc-test gap · 🟢 verified clean.

## 🔴 Must fix — broken on `main`

1. **PR #299 toolbar regression — merged with a failing test.**
   `src/bootstack/widgets/toolbar.py:240-256` `_apply_bar_defaults` uses
   "widget has `**kwargs`" (`has_var_kw`) as a proxy for "accepts
   `density`/`surface`". Wrong here — `**kwargs` is the layout passthrough, not a
   config passthrough.
   - Crash: `toolbar.add_widget(bs.Checkbox/Switch/ToggleButton/Radio, ...)` →
     `TypeError: got unexpected keyword argument(s): density, surface` (those
     widgets' `**kwargs` reject unknowns).
   - No-op: for `TextField`/`Select`/`ProgressBar`/`Badge` the injected `surface`
     is swallowed by `_split_layout_kwargs` and dropped — #263's goal unmet.
   - Proof: `tests/widgets/public/test_add_toolbar.py::test_add_widget_class_inherits_bar_density_skips_unsupported_surface`
     **fails on `main`** — the agent's own test asserts `surface` is skipped for
     `TextField`, the code injects it. Test and impl contradict; merged anyway.
   - Fix direction: drop `has_var_kw`; inject only when the param is explicitly in
     the signature (matches the test's intent).

## 🟠 Real logic bugs

2. **DataTable `iter_rows` clobbers the shared source.**
   `tableview/tableview.py` `_iter_raw_chunks` (~:2410, PR #293) `yield`s inside
   `with self._apply_view_to_source()`. As a generator, a caller that `break`s out
   of `iter_rows("all")` leaves this view's filter/sort applied to the **shared**
   source until GC — defeating the per-view isolation the PR adds. `to_rows`/
   `to_csv` drain fully (safe); `iter_rows` (lazy/partial by design) is not. Fix:
   materialize rows under the CM, then yield outside it.

3. **Doc examples that are a Python `SyntaxError`.**
   `widgets/codeeditor.py:223` and `widgets/textarea.py` docstrings show
   `...subscribe(lambda ok: btn.disabled = not ok)` — assignment in a `lambda`.
   Copy-paste crash. (The `.rst` versions correctly use a named `def`.)

## 🟡 Hallucinations, mislabels, doc/test gaps

- **Hallucinated test kwarg (#293):** `tests/widgets/public/test_datatable.py`
  (~:233/238/256/261) pass `enable_search=True` to `bs.DataTable`; the public
  kwarg is `searchable`. `enable_search` is dropped via `**kwargs`; the test only
  passes because the default is already `True` — configures nothing.
- **Mislabeled "fix" (#296):** "fix read_only setter" (`codeeditor.py:314`) just
  renames `_internal._core` → `_internal.core` (same object). No read-only bug on
  that path; commit overstates.
- **Stale doc now false (#292):** `src/bootstack/signals/README.md:110-112` still
  says "create `Signal` after the App / pass `master=`" — the gotcha this PR
  overturned. (README also documents nonexistent `get()`/`unsubscribe()`.)
- **Undocumented new API (#296/#297):** `CodeEditor.selection`, `selected_text`,
  `indent()`, `dedent()`, Tab/Shift+Tab keyboard behavior absent from
  `docs/widgets/codeeditor.rst`.
- **Missing tests:** #296/#297 (selection coords, block indent/dedent edge cases)
  and #298 (`on_scroll`/`scroll_position`/keyboard scroll) ship with zero tests.
- **Tests via internals (#293):** `test_datatable.py:248,259` drive
  `_internal.set_search`/`set_sorting` instead of public `set_search`/`sort_by`.
- **Inaccurate claims:** #297 "selection preserved" actually expands partial
  selections to whole lines; #297 keyboard indent only works when
  `auto_indent=True`; ScrollView `scroll_position` docstring claims `(1.0,1.0)` is
  reachable (it's the top-left fraction, never 1.0).
- **Internal leak (#299): FIXED for button/label.** `add_button`/`add_label` now
  build and return the public :class:`bootstack.Button` / :class:`bootstack.Label`
  (live properties; no `_impl` leak), carrying the bar's `density`/`surface`. Added
  `surface=` to `bs.Button` so a ghost toolbar button still blends into the chrome
  bar; preserved window-drag bindings on draggable-titlebar labels via an internal
  `_attach_drag` helper. Item spacing is now a uniform `padx=2` for all added items
  (was 0 for buttons / 4 for labels) — a small, intentional consistency change.
  **`add_divider`/`add_spacer` still return `None` (deferred):** returning a public
  `Divider`/`Spacer` is entangled with the pack-based internal toolbar (a `Spacer`
  needs `expand=True` packing the generic container protocol doesn't apply), tracked
  with the unified-toolbars work; the handle's only use is detach/attach.

## 🟢 Verified clean

- **Signal rewrite (#292)** — correct. Object-mode survived; all three `set()`
  branches dedupe/notify once; re-realization across App lifecycles works; escape
  hatches fine. 22/22 signal tests pass.
- **Internal-access scrub (#295)** — every private→public swap resolves to a real
  symbol. No hallucinated APIs.
- **Carousel (#289), PyInstaller metadata (#291), new
  `docs/examples/chart_filter_from_chart.py`** — verified against real API.
- **`dev_246` removal** — clean, no dangling refs.
- **Full suite** — 605 passed, 1 failed (only the #299 toolbar test), 0 other
  regressions.

> ⚠ Correction: an earlier pass reported "docs `-W` build exit 0." That reading
> was wrong — the build command was piped to `tail`, so the captured exit code
> was `tail`'s, not sphinx's (the same pipe-masks-exit-code trap that hid the
> failing test leg). The docs build is in fact **broken on `main`** — see the
> pre-existing section. When checking exit codes, never pipe the command whose
> status you care about.

## Pre-existing (not from this session)

- **Docs `-W` build is broken on `main`.** `docs/shared/widget-sizing.rst:5,35,65`
  → `ERROR: Inconsistent title style: skip from level 3 to 5` (3 errors, build
  exits 1). The `'''`-underlined Column/Row/Grid sub-headings in this *included*
  fragment land at heading level 5 while the including page's context is level 3.
  Introduced by the Row/Column split (`3c2067d1`, PR #266) — **outside** the 6-hour
  window, but real and contradicts the repo's "keep the build warning-free" rule.
  Fix direction: the include fragment should not carry section titles that skip a
  level — use `.. rubric::` (or a heading char one level below the include site)
  for Column/Row/Grid. Not yet fixed (out of the 1–3 scope).
- ~~`_impl/composites/toolbar.py` reads `self._surface` but never assigns it in
  `__init__`, so a window-controls toolbar would `AttributeError`.~~ **Investigated
  → NOT a bug.** The `Frame`/`TTKWrapperBase` base class always sets `_surface`
  (defaults to `'content'`), so `Toolbar(show_window_controls=True)` constructs
  fine even with no `surface` kwarg. Verified empirically. The reviewer
  over-flagged this one; the `getattr(..., "chrome")` in the `surface` property is
  merely defensive, not load-bearing. No fix needed.

## Fix plan

Branch `feat/*` off `main`. Address in order: (1) #299 `has_var_kw`, (2)
`iter_rows` leak, (3) the two `lambda` docstrings. Then sweep the 🟡 items.
Commits held for per-commit maintainer approval.