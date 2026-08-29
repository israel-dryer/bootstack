# bootstack — Handoff archive

Session history split out of `CLAUDE.md` (2026-07-30) to keep the working
handoff small. Every entry below shipped and is merged to `main`; each carries
the root-cause analysis, the decisions and their reasoning, and the gotchas that
bit along the way — the things git history does not record.

**Read the relevant entry before working in an area it covers.** It is indexed
by issue and PR number, so `grep` for `#392` / `PR #385` / a widget name.
`CLAUDE.md` keeps only what is still OPEN plus the standing rules.

---

## Recently completed (all merged to `main`)

Pointers only — these shipped; rationale, detail, and gotchas live in the linked
memories and git history.

- **#409 → PR #414 (MERGED 2026-08-05, unreleased) — `events.rst` documented a
  custom-event spelling that raises.** Docs-only plus one docstring; **no CHANGELOG
  entry, deliberate** (nothing in the package changed, so a reader scanning "was I
  affected?" gets nothing actionable), which is why `## [Unreleased]` is still
  absent. Follow-up left open as **#412**.
  - **⚠ The framing correction matters more than the fix — do not re-derive it, run
    `development/probe_409_custom_events.py`.** The issue said the docs "document a
    feature that was never built," and the first session summary repeated that.
    **It is wrong.** Custom events work today, **two ways**: a **literal virtual
    sequence** on any stock widget (`on("<<RowImported>>")` / `emit(..., data={...})`
    delivers the dict intact), and a **bare name on a class that called
    `register_widget_events()`** (internal, `widgets/_core/events.py`). Absent is
    *only* the bare-name-on-a-**stock**-widget spelling, because `resolve_event()`
    has no fallback branch. Memory `feedback_dont_inherit_issue_framing`.
  - **Why the section was deleted rather than the fallback built.** The fallback is
    ~one line (`return f"<<{name}>>"`) — but it is **the same line that makes
    `on("chnage", …)` raise**, so building it trades a framework-wide typo guard for
    a handler that binds fine and silently never fires. Direct reversal of the
    strictness direction that earned `0.6.0` (#369/#383). The probe's **check B is
    the control** proving this is a tradeoff and not a pure bug; without it check A
    reads as a gap.
  - **The code review found two FALSE claims in the replacement prose** (fixed in
    `ac132ac3`), both settled by running code rather than reading it. (i) *"both are
    limited to the events a widget actually publishes"* — false in **both**
    directions: every `GLOBAL_EVENT_MAP` name resolves on **every** widget
    (`bs.Label(...).on("submit", h)` is accepted though Label never emits one), and
    `resolve_event()` passes any literal `<...>`/`<<...>>` string through unchanged.
    It is a **known-name** check, not a *publishes* check. (ii) *"listing the ones
    that widget knows"* — false: `all_known` is a **process-wide union** of
    `GLOBAL_EVENT_MAP` and every `_CLASS_EVENT_MAPS` entry, so a `Button` typo is
    reported alongside `cursor_move`/`export`/`item_drag_start`. That sentence
    carried the justification for keeping the guard, so it was the one that most
    needed to be true. **Narrowing `all_known` to the widget's own MRO maps plus the
    global map is folded into #412, not done.**
  - **⚠ `emit()` and `on()` take the same names but not always the same target.**
    `emit()` consults `_event_target()` **only for `<<Virtual>>` sequences**;
    native-mapped names (`click`/`focus`/`blur`/`submit`) fire on `_internal`, so
    `field.emit("submit")` on a retargeting composite reaches nothing bound through
    `on()`. `PublicWidgetBase.emit`'s docstring already documented this; the guide
    did not — which left the published guide **less accurate than the source it
    documents**. Both say it now.
  - **⚠ The `bs.events.X` spelling was stale for two months and NO guard could have
    caught it.** `637b2407` (2026-06-08, the PR #104 curation) scoped framework
    primitives into submodules. `docs/reference/events.rst` and `CLAUDE.md` carried
    `bs.events.ChangeEvent` from 2026-06-05 — correct when written, stale three days
    later — and `PublicWidgetBase.emit`'s docstring **acquired** it at 20:06 on
    2026-06-08, roughly **nineteen hours *after*** the refactor, copied from the
    already-stale `events.rst`. Nothing ever broke because `bs.events` resolves
    **transitively** (widget code imports the payloads, so the submodule lands in
    `sys.modules` and becomes a package attribute). And
    `tests/test_public_surface.py` gates the curated top-level **name set** plus each
    moved symbol's importability from its submodule — it **never asserts a submodule
    is unreachable as a `bs.*` attribute**, so this class of curated-namespace drift
    is outside the guard's reach rather than missed by it. Swept in `c08fa1a3`
    (CLAUDE.md) + PR #414 (docs + docstring).

- **#392 → PR #402 (MERGED 2026-07-30, shipped in 0.2.0) — `Subscription.cancel()`
  silenced every other handler on that event.** Four logical changes, four commits.
  Reviewed twice; the second review found a critical hole the first missed.
  - **Root cause (settled — do not re-derive).** `_patched_bind` wrote its own Tcl
    script for **virtual events** (`<<...>>` = every bootstack event) as a bare
    `<funcid> %d %# ...`, but `unbind` was never patched to match. `Misc._unbind`
    filters lines by the prefix `if {"[<funcid> ` that stock `_bind` emits, so
    nothing was filtered (**the binding survived**) while `deletecommand(funcid)`
    still ran (**the command was deleted**). The orphan errored on every dispatch,
    and because bindings use `add='+'` they are ONE concatenated script — so the
    error **aborted every handler after it**. Silent: no Python exception. Fix =
    emit stock's exact `if {"[<funcid> ...]" == "break"} break\n` shape, keeping
    `%d`. **Real events took `_original_bind` and were never affected.**
  - **Change 2 — mid-dispatch cancel.** Stock `unbind` deletes the command
    immediately, and the copy of the script Tk is *running* is not the one a
    removal rewrites, so cancelling from inside a handler for the same event
    aborted the remainder. **Inherited stock behavior, reproduced on raw
    `tkinter`** — not a regression from change 1. `_patched_unbind` neutralizes the
    command in place and deletes it at the next idle point. Two deliberate
    behaviors: (i) when the funcid is **not found** it deletes **nothing** (stock
    deletes anyway, orphaning whatever is still bound — audited all ~95 `unbind`
    sites in `src/`, no caller depended on the old behavior, two are improved);
    (ii) the deferred delete is scheduled on the **root**, never the widget.
  - **Change 3 — `return 'break'` inert on the public surface.** Change 1 made
    handler return values significant where they had been discarded. `adapt_handler`
    (`widgets/_core/base.py`) now returns `None`. No CHANGELOG entry — never
    documented or reachable before, so nothing changed from a user's view. ⚠
    **CORRECTION to the first review: "internal handlers are unaffected" was
    WRONG.** They bypass `adapt_handler`, which is exactly why
    `numberentry_part.py:169,175` still return a live `'break'` into the stock
    script shape → filed **#401**.
  - **★ Change 4 — unique binding names (the critical hole).** `Misc._register`
    names a command `repr(id(f)) + f.__name__` where `f` is a bound method created
    for that registration alone; releasing the command frees it and CPython hands
    back the same address — **498/499** consecutive bind/cancel/bind cycles gave an
    *identical* funcid, and every wrapper shared the `__name__` `wrapper`. Harmless
    while deletes are immediate; NOT harmless once change 2 defers them: a binding
    made in that window inherits a name a deletion is already pending on, and the
    delete removes a **live** handler — #392's symptom on a new trigger,
    interpreter-wide. Fix = serialized `__name__` (`_unique_name`), applied to the
    real-event wrapper too. Measured 498/499 → **0/499**. Full detail in memory
    `reference_tkinter_funcid_recycling`.
  - ⚠ **The second review's headline claim was itself half wrong.** It reported the
    collision as a NEW regression ("stashed, b/c run"); the stashed baseline fails
    **identically** — pre-fix it is just #392. **Verify the baseline claim, not only
    the failure claim**; it decided whether this was a ship-blocker.
  - ⚠ **The failure is NONDETERMINISTIC** (allocator-dependent), so behavioral tests
    pass on a broken build by luck — 1 of 3 caught it on the first pre-fix run. The
    reliable guard is **structural**:
    `test_a_cancelled_handlers_name_is_never_reused` asserts 50 cancel/rebind cycles
    give 50 distinct `_bind_id`s (fails `1 == 50` every time). Deliberate exception
    to "test public paths" — the public symptom is a coin flip. **General rule: when
    a symptom is allocator- or timing-dependent, assert the invariant.**
  - ⚠ **Defer widget cleanup on the ROOT, never the widget** — `widget.after_idle(cb)`
    makes `cb` a command owned by that widget, so destroying it fires an orphan.
    Guard against `TclError` **and `AttributeError`** (`destroy()` nulls
    `_tclCommands`). Also fixed the same class at the data-cache cleanup
    (`events.py`, pre-existing). This class of bug has **no public observable** —
    read the interpreter's **background-error channel**
    (`root.tk.createcommand('bgerror', ...)`), which is what caught it.
  - **Filed, not fixed:** #397 dialog `off_*` target drift · #398
    `on_visibility_alpha` never unbinds · #399 not-found guard leaks the command ·
    #400 `except TclError` spans three operations · #401 above. All `0.2.x`.
  - **Portability (measured, don't re-litigate):** Tk bind substitution codes are
    identical in 8.6 and 9.0; `%d` carries virtual-event `user_data` since Tk 8.5
    (TIP 165). `Misc._subst_format`/`_bind`/`_unbind` are byte-identical across
    CPython 3.12/3.13/3.14. ⚠ Neither box has Tk 9 — that half is source-based, NOT
    executed. Memory `reference_tk_bind_substitutions_86_vs_9`.
  - ⚠ **#396 confirmed twice while writing these tests** — a payload test on
    `bs.TextField` **passed vacuously** (`emit()` hits `self._internal`, `on_change`
    binds the inner entry). **Any test pairing `emit()` with `on_*()` must use a
    widget where the two agree** (`bs.Slider`, `bs.Button`) until #396 lands.
  - Probes kept in `development/`: `probe_392_funcid_recycling.py` (census / repro /
    cross-widget / idle-gap / unique-name control), `probe_392_datacache_afteridle.py`,
    `probe_392_shortcut_rebind.py`, `verify_392_*.py`, `scan_392_break_handlers.py`.

- **#394 → PR #395 (MERGED 2026-07-29) — a validation rule misaligned a row of
  fields.** Reporter `bLynnb2762` on 0.1.8/Windows: adding `required` to two of
  four fields in a row left the other two sitting **9px lower**. **It was TWO bugs
  under one report** — that split is the whole finding, don't re-derive it.
  - **(a) In a `Form`.** `_build_items` grids every cell `sticky='nsew'`, so all
    cells were **already** stretched to the tallest field — the cells were never
    the problem. Inside the `Field` composite the entry row was packed
    **`expand=True`**, so it absorbed the slack and **centered itself in it**,
    putting the extra height *between the label and its own input*. Fix = drop
    that one `expand=True` (`field.py`) so slack collects below the stack. ⚠ The
    reporter's own diagnosis (a `vertical_items` knob on `GroupItem`) was **wrong**
    and so was the first read here — **the Form needed no new alignment knob.**
  - **(b) In a row-mode container.** Different mechanism: the field frames keep
    their **natural** heights (61 vs 80) and the cross-axis default (`center`)
    dropped the shorter ones; (a) does nothing here. Fix (maintainer's call) =
    field widgets contribute **`vertical='top'` as a SOFT default**. Precedence,
    most specific first: child's explicit `vertical=` → container's explicit
    `vertical_items=` → **child-declared default (only when the container's cross
    axis is unset)** → framework `center`. **That gate is the whole trap:** a
    widget default must never silently beat an argument the author wrote (cf.
    #381). To express "unset", `Row`/`Column` moved to `*_items: ... | None = None`
    resolved inside `FlexFrame` — **the `None`-means-unset convention `Card`/
    `GroupBox`/`Expander`/the AppShell page already used**, so this aligned
    `Row`/`Column` with four existing containers rather than inventing anything.
    `None` resolves to exactly what was hard-coded (stacking axis → leading edge,
    cross axis → center), so non-field layouts are unchanged. One
    **`_resolve_cross()`** owns precedence at **BOTH** call sites — `_relayout`
    **and** the O(1) `_grid_appended_plain` append path; covering only one would
    make alignment depend on whether a relayout happened to run.
  - **Scope widened by `/code-review`, which caught two gaps that left the fix
    half-effective.** (1) **Every row-mode container except `Row`** pre-resolved
    its own unset default to `'center'`, suppressing the field default — measured
    `Card(layout="row")` `[248, 257, 248]`, the identical 9px. Since
    `Card(layout="row")` around a form row is common this would have **shipped
    visibly unfixed**; eight copies of that block collapsed into one
    **`resolve_layout_items()`** (`_core/container.py`) — grid mode still gets
    concrete values (the grid engine has no "unset"), column/row pass it through.
    (2) **`bs.Select`** is the ONE `Field`-backed public widget outside
    `FieldAddonMixin` (its `SelectBox` subclasses `Field`) and has had
    `add_validation_rule` since #357, so it sat low beside real fields (562 vs
    553) — it carries `_flex_vertical_default` directly.
  - **⚠ TWO CORRECTIONS to earlier notes.** (i) The prior handoff claimed
    **`bs.Grid` has the same bug** — **it does not.** `Grid` defaults **both** axes
    to `stretch`, so its cells align once the entry stops centering in the slack
    (measured). There was never a Grid decision to make. (ii) A review finding
    claimed the docstrings contradict the signature by stating the effective
    default while rendering `| None = None` — **that is the house style**
    (`card.py:33` already reads that way), so it was left alone.
  - **Known asymmetry, accepted:** `Row()` and `Row(vertical_items='center')` now
    behave **differently** even though the docs call `center` the default — an
    author who writes the default out explicitly gets centered fields. Deliberate
    (the alternative is ignoring an explicit argument) but it is a trap, and it is
    the strongest argument against the soft-default approach if it is ever
    revisited. Also **CHANGELOG `### Changed`:** where a field shares a grid row
    or a `'stretch'` cross axis with a **taller** widget the entry moved from
    centered to under its label (measured 59px → 19px in a 142px cell) — an
    improvement (the input no longer floats below its own caption) but a real
    visual change. Doc screenshot scenes were checked: they pair fields with
    *shorter* siblings, so none needed regenerating.
  - Tests **`test_field_row_alignment.py`** (14) — #394 had none. **5 fail pre-fix
    BEHAVIORALLY** (`entries misaligned across the row: {180, 189}`), not with an
    `AttributeError`, and each geometry assertion carries a precondition proving
    the rule really grew the field so it cannot pass vacuously. Suite **893 passed,
    exit 0**; clean `-W` docs build. **The geometry probes were far more decisive
    than reading the layout code**, which is tangled across FlexFrame / GridFrame /
    raw pack — rebuild one rather than reading, if this area comes up again (the
    scratch probes and the reporter-repro demo were deleted once #394 shipped;
    they were for visual validation only). Two rules that mattered: a
    within-process measurement is required — `winfo_rooty()` is **not** comparable
    across two runs (different window positions), so compare siblings in one run or
    measure the entry's offset *inside* the field frame; and pair any alignment
    assertion with a precondition proving the rule really grew the field, or it can
    pass vacuously. Memory `reference_geometry_probe_same_process`.
  - **Process gotcha that bit here:** a bulk `pathlib` rewrite of 6 files
    **flipped CRLF→LF** (repo is `core.autocrlf=true`) — same class as the `sed -i`
    trap in `reference_autocrlf_sed_gotcha`. Caught from the `git diff` warning and
    restored; prefer the Edit tool, and if scripting, write bytes.

- **0.1.x session 2026-07-29 — discussion #386 triaged into four issues, two
  fixed and merged, plus #385.** User `bLynnb2762` filed **discussion #386** as an
  *idea* ("let me reset a `DateField` to `None`"); investigation found **two real
  bugs underneath it**, both now on `main`, and split the rest into a feature and
  a design question. **All Windows + Tk 8.6.**
  - **#387 → PR #391 (MERGED).** `DateField.value = None` **and its own public
    `clear()`** were silent no-ops — the date stayed on screen and in
    `form.get()`. **Root cause: `TextEntryPart.value()` (`_parts/textentry_part.py`)
    is a combined getter/setter using `None` as its "no argument" sentinel**, so
    `value(None)` called the *getter*. The set branch already handled `None`
    correctly — which is exactly why the `.value = ''` workaround worked, same code
    path. Fix = a module-level **`_UNSET`** sentinel (also in `spinnerentry_part.py`,
    which carries its own copy). Verified no caller passed `None` expecting a get.
    Affected **every** field on `TextEntryPart`; it surfaced on `DateField` only
    because that is the one whose `clear()` passes `None` (the others pass `""` and
    worked by accident). `TimeField` was immune — `TimeEntry` subclasses `SelectBox`.
    ⚠ **The landmine:** `Form.set()` looped **all** items applying
    `_data.get(key)` = `None` for absent keys, harmless ONLY because that write was
    discarded — so **fixing the sentinel alone would have turned every partial
    `form.set()` into a destructive overwrite**, including the reporter's own code.
    `set()` now writes only the keys given and **merges** into `_data` instead of
    replacing (which also fixed a latent bug: partial updates used to *drop* the
    unmentioned keys from `_data`). Deliberate: `configure(data=)` stays a
    whole-record write, so absent keys now genuinely clear.
  - **#388 → PR #393 (MERGED).** Choosing a date in the picker emitted **no
    `<<Change>>`** — a bound `Signal` stayed stale, `on_change` never ran, `Form`
    never registered the edit, while typing the same date and pressing Return
    worked. `_show_date_picker` assigned `value` directly; that event comes only
    from `_check_if_changed()` on FocusOut/Return. **Range mode was already correct**
    (`_set_range` emits) — single mode was the outlier. Fix = both call sites route
    through **`_apply_picked`**, which assigns then calls the entry's **existing**
    `_check_if_changed()`. Reusing it (not hand-building a `ChangeEvent`) is what
    makes it safe: it advances `_prev_changed_value`, so a later focus-out cannot
    re-announce the same pick, and the double application (dialog callback + the
    post-`show()` fallback) is inert on the second pass. Also corrected the
    DateField docs, which claimed `on_change` fires on a `value=` assignment — it
    does not, by design.
  - **#389 FILED** — `Form.reset()` (construction-time values) and `Form.clear()`
    (`None`). **Maintainer decision: they are DIFFERENT verbs** — reset = originals,
    clear = none. Both justified: `reset()` is **not user-implementable** (after an
    edit, `get()` no longer knows the original), `clear()` is the data-entry case.
    Slider clears to `min_value` (it has no null state, and that is already the
    de-facto seeding behavior). Needs an `__init__` snapshot because `set()`
    destroys `_data`; both must clear validation state.
  - **#390 FILED (design, needs a decision)** — see the signal-emptiness entry
    under "Next up".
  - **#385 MERGED** — validated on Windows first (869 passed, exit 0, with `main`
    merged in). Its `test_menu_backend_probe.py` runs **16 tests, zero skips** here.
  - **#383** got the `Slider.value = None` → raw `TypeError` case added to its sweep.

- **0.1.8 PATCH SHIPPED — macOS sizing on Tcl/Tk 9 (PR #377 for #375;
  2026-07-23).** `bootstack 0.1.8` is on **PyPI** + tagged **`v0.1.8`**. Tk 9
  changed the resolution macOS reports (Aqua's **72 → 96 DPI** baseline), and
  `detect_scale_factor()` (`winfo_fpixels('1i')/72`) read that as a high-density
  display — so on any Tk 9-linked Python the whole UI rendered **~1/3 too
  large**. Text, icons, padding, control sizes all restored; matches Tk 8.6
  exactly. Win/Linux unaffected. Tests **`test_tk9_scaling_baseline.py`** (8) —
  and note they **monkeypatch `platform.system()` + `tkinter.TkVersion`, so they
  need no display and no Tk 9**, which is why #380 calls them the cheap CI win.
  ⚠ **CHANGELOG/release gotcha bit this cut** — see the release-flow note under
  "Next up".

- **0.1.x session 2026-07-28 — three PRs merged/open, one issue filed.** Worked
  the open-issue backlog. **All verified on Windows + Tk 8.6 only** (see the
  environment note below).
  - **#381 → PR #382 (MERGED).** A behavior-mode argument is read by comparing
    against one literal, so `selection_mode="multiple"` silently turned
    multi-select **off** — no error, no warning. New **`validate_choice`**
    (`widgets/_core/choices.py`) + public **`InvalidChoiceError`**, applied to
    `selection_mode` (DataTable/ListView/Tree/Gallery/Calendar/DateField),
    DataTable `sorting_mode`/`paging_mode`, `mode` (ToggleGroup/PathField),
    ScrollView `scroll_direction`/`scrollbar_visibility`, `scrollbars`
    (TextArea/CodeEditor), sidebar-toggle `collapse`. `SELECTION_MODES =
    get_args(SelectionMode)` so the check can't drift from the type.
    **Two decisions worth remembering:** (1) the issue cited #367 as precedent
    for raising on a bad `editor=` name — **that is wrong**, #367 made the
    *fallback* safe and never raises; the real precedent is **`ValueError`**
    (`ContextMenu(trigger=)`, RadioGroup), so `InvalidChoiceError` inherits
    **both** `BootstackError` and `ValueError` and those older guards can migrate
    later without breaking callers. (2) **Scope was measured, not guessed** — an
    AST audit found **215** Literal-typed public `__init__` kwargs and a 24-case
    probe found **17 silently accepting** garbage; a blanket sweep is wrong
    because **`| str`-widened args (`accent`/`surface`) must NOT be guarded**
    (`'primary[+1]'`, `'primary[500]'` aren't in the alias). Line drawn at
    *behavior* modes. **Guards run BEFORE `_resolve_parent`** — it raises its own
    "created outside any container" error, which buried the typo.
  - **#332 → PR #384 (MERGED).** Not really a rename: `ShellLayout` held each
    flag **twice** — read-only `statusbar_visible`/`rail_visible`/
    `sidebar_visible`/`dock_visible` properties *and* a separate
    `set_*_visible(bool)` family. Gave the existing properties setters, deleted
    the methods. Properties (not `show_*`/`hide_*` verb pairs) because the
    getters and every sibling region accessor already are, and callers assign
    computed bools that verb pairs would turn back into if/else.
    `AppShell.statusbar`'s reveal hook was a **lambda** (can't hold an
    assignment) → named `_reveal_statusbar`. Internal only.
  - **#379 → PR #385 (MERGED 2026-07-29, after a macOS run AND a Windows
    re-validation).** Six macOS failures, none a
    product bug. New **`menu_probe`** + **`menus_are_native`** fixtures in
    `tests/conftest.py` so the four backend-assuming tests assert the same fact
    on both `ContextMenu` backends instead of the Windows shape (a `skipif` would
    have *preserved* the coverage hole — those are the only tests for menu
    construction + overlay propagation). **Key technique: `_NativeContextMenu` is
    constructible on Windows** (a `tk.Menu` is real everywhere; only the *choice*
    of backend is platform-specific), so `test_menu_backend_probe.py` (16) drives
    **both backend classes directly** and the macOS branch is exercised on
    Win/Linux. That caught a real defect in the helper: **`entrycget(i,'state')`
    raises `TclError` on a SEPARATOR** on the native backend while the themed one
    returns `False`. Measured: both agree count=3 and index alignment for
    `[command, separator, command]` — only the separator's state differed.
    **PageStack order-dependence hypothesis (UNCONFIRMED):** `shown_app` did
    `deiconify()` + **`update_idletasks()`, which does not process the map event
    at all** (idle callbacks only), so `winfo_ismapped()` depended on what was
    queued ahead; now pumps `update()` until mapped (bounded 100). **The PR body
    carries step-by-step macOS tester instructions**, including what each failure
    mode means if PageStack still fails.
  - **#383 FILED** — the follow-up sweep: presentation kwargs still degrading
    silently (`density`, `Tabs.orient`, `Slider.orient`, `Gauge.variant`) **plus**
    args that raise but leak a **raw `TclError`/`AttributeError`**
    (`Button.icon_position`, `Label.justify`, `Scrollbar.variant`,
    `Expander.icon_position`, `ProgressBar.mode`). Suggests sweeping **by argument
    name**, not by widget.

- **0.1.7 PATCH SHIPPED — Tk 9 scroll-event contract + attach theme repaint
  (PRs #373, #374; 2026-07-23).** `bootstack 0.1.7` is on **PyPI** + tagged
  **`v0.1.7`** ("Tcl/Tk 9 scroll support"); verified by installing the published
  wheel into a clean Tk 9 venv. **#372** ("Scroll not
  working on MacOS", user `cleonello`): scrolling
  worked on Python 3.13.9, not 3.14.6. **It is NOT a Python change** — `tkinter`
  is unchanged between those versions apart from docstrings, `after(**kw)`, and
  `trace_variable` deprecation warnings. It is **Tcl/Tk 8.6 → 9.0** (reporter had
  9.0.3; the python.org installer still ships **8.6.17**, which is why 3.13
  "worked"). **Root cause, measured not inferred:** on Tk 9 + Aqua a trackpad
  fires **only `<TouchpadScroll>`** — a probe logged **293 TouchpadScroll, ZERO
  MouseWheel** — and every scrolling widget bound only `<MouseWheel>`. Two more
  breaks in the same contract: Tk 9 normalizes wheel deltas to **±120** on all
  platforms (so Aqua's `-event.delta` scrolled 120 units/notch), and X11
  **Button-4/5 are no longer delivered to scripts** (TIP 474). **Fix:** new
  **`_runtime/wheel.py`** (`wheel_sequences` / `wheel_notches` / `precise_deltas` /
  `scale_num` / `PixelAccumulator`) replacing the delta branch **duplicated across
  9 files**; bindings unconditional, X11 buttons kept only as a Tk ≤8.6 fallback
  gated on **Tk version, not `winsys`**. Widgets copy Tk's **two** conventions:
  *pixel* scrolling (ScrollView/TextArea/ScrolledText/Tabs) vs *accumulated whole
  rows* (ListView/Tree/Gallery), plus a 40px/step throttle on the Spinbox/
  NumberField steppers. **DataTable needed nothing** — Tk 9 binds TouchpadScroll on
  the ttk Treeview class itself (verified). Incidental fix: a ScrollView notch moved
  **10 canvas units on X11** vs 1 elsewhere; now 1 everywhere. Tests
  **`test_scroll_events.py`** (25; 3 fail pre-fix). Verified on **Tk 9.0.4 AND
  8.6.17** + confirmed live on a real trackpad. Full suite on Tk 9: **751 passed**,
  only the 6 known pre-existing failures. `trace_variable`/`trace_vdelete`/
  `trace_vinfo` (removed in Tcl 9) are **not used** anywhere — scrolling was the
  only Tk 9 gap. Memory `reference_tk9_scroll_events`.
  **Repro env:** `brew install python-tk@3.14` → `/opt/homebrew/opt/python@3.14/bin/python3.14`
  (3.14.6 + Tcl/Tk 9.0.4). **⚠ The touchpad tests SKIP on Tk 8.6** — on the default
  `.venv` the file reports "15 passed, 10 skipped" and looks green while testing
  nothing about the fix. **There is no test workflow at all** (`.github/workflows/`
  has only `docs.yml` + `release.yml`), so this can regress invisibly — the top
  open item from that session.
  **UPSTREAM: `ttkbootstrap` has the identical defect** — same code lineage, same
  `winsys` branch in `widgets/scrolled.py` (binding 436-440, delta 546-556) and
  `dialogs/colordropper.py:157-160`. Measured on 2.0.0 + Tk 9.0.4: a trackpad
  gesture does nothing and ONE wheel notch jumps an 80-row `ScrolledFrame` to the
  end (`0.0 → 0.813`). Filed as **israel-dryer/ttkbootstrap#1290** with the fix
  shape; the #373 diff maps closely onto `scrolled.py`. **Repro gotcha:** the wheel
  tag is only added to bindtags on mouse-enter, so synthetic events do nothing until
  `enable_scrolling()` is called — and the content-fits guard silently returns
  early until the scrollregion is actually computed. Both produce a convincing
  false "dead" reading.

- **0.1.6 PATCH SHIPPED — seven form/field/validation fixes
  (PRs #362–#368; released 2026-07-21).** On **PyPI** + tagged **`v0.1.6`**
  (plus #371, a `Decimal`/`value_format` fix, folded into the cut). Kicked off by the user
  `bLynnb2762` reporting on the CLOSED **#358** that tristate still failed; filed
  fresh as **#361** (different root cause). **#362:** a checkbox built by a `Form`
  ignored `tristate` — the form passed an explicit `value=False` over the widget's
  indeterminate default; `editor_options` also COLLIDED with the kwargs the form
  fills (`value`/`label`/`options`) → `TypeError` from an internal class. Two value
  bugs alongside: `TextField`/`PasswordField`/`PathField` gated the initial value on
  **truthiness** (so `value=0` rendered empty, and a form wrote the blank back over
  the record), and the form **stringified** non-text data (a `Decimal`/`date` became
  `str` in `form.data` at construction — a data-integrity regression *my own first
  fix introduced*, caught by review). **#363:** the same collision existed in
  `MenuButton(menu_options=)`, `ButtonGroup.add`/`add_all`,
  `RadioGroup`/`ToggleGroup.add`, `Toolbar`/`StatusBar.add_widget` → all now route
  through **`merge_kwargs`** (`widgets/_core/kwargs.py`); see the corrected Gotcha.
  **#364:** a placeholder is rendered by INSERTING its text, and validation read the
  raw entry, so **`required` passed on an untouched field** (a form with a required
  placeholder field submitted empty); `field.text` also reported the hint while
  `value` said empty. **#365:** deleted the 27 `tests/features/*` visual scripts
  (never collected — `testpaths` covers only `tests/cli`, `tests/widgets/public`,
  `tests/data`). **#367 (#366):** `email`/`pattern`/`stringLength` ran on EMPTY
  values, so an **optional** field left blank blocked `Form.validate()` with no way
  forward — now they pass on empty (matching `range`'s existing precedent); also
  `required` was dropped for an unrecognized `editor=` name (a typo silently let an
  empty field submit). **#368 (#355):** a `Select` REJECTED a value not in its
  option list, so opening a `Form`/`DataTable` editor on a record whose option had
  been retired **raised** — while a later programmatic write was silently dropped.
  **Root cause:** `Select` stores display TEXT and decodes the value back through
  the option list, so the `ValueError` was guarding *decodability*, not policy. Fix
  = register the retired value under its own coerced text (`_register_retired_value`)
  so the decode stays total (an `int` reads back an `int`); it is never added to
  `_records`, so the popup is unchanged. Surfaced two more: a **searchable** Select
  committed its top match when the popup was merely opened and dismissed, and
  validation ran against the **label** (so a rule on a decoupled list rejected valid
  selections). Added **`Select.validate()`** (every other field had one; its own
  `add_validation_rule` docstring already promised it). **#369 filed** — the
  selection family disagrees on off-list values (`SelectButton` raises both ways;
  `RadioGroup` accepts at construction, raises on assignment; `ToggleGroup` accepts
  both; and where accepted, `value` says `'MX'` while `selection` says `None`) —
  wants ONE family decision, not four patches. **PROCESS (the session's real
  lesson): adversarial review caught a defect in EVERY round**, including two
  regressions I introduced — the `Decimal`→`str` coercion, and a
  `_get_validation_value` override that broke **`bs.TimeField`** (`TimeEntry`
  subclasses `SelectBox`, so typed out-of-range input validated clean). Tests that
  only assert *construction doesn't raise* are what let #358 ship twice — and I
  repeated it, writing a test that certified a **broken** documented example
  (`menu_options={'offset': 4}` crashes on open; the docstring now says `(4, 0)`).
  **CHANGELOG convention (I got this wrong on four branches):** a fix commit writes
  `## [Unreleased]`; the `Release X` commit renames it AND adds the `[X]:` link
  definition. Memory `feedback_pause_and_ask_when_stuck` — I over-complicated #355
  for hours (heading toward a `Select` value-model rewrite) before the maintainer
  pointed at the ~15-line map fix; **pause and ask when a fix outgrows its issue.**

- **0.1.5 PATCH SHIPPED — boolean-control state reads + Checkbox tristate (PR #360;
  2026-07-20).** `bootstack 0.1.5` is on **PyPI** + tagged **`v0.1.5`** ("boolean
  control state fixes"). **Three bugs, one root cause (user `bLynnb2762`).** `Checkbox`,
  `Switch`, `ToggleButton` share **`_BooleanControlBase`**, which read state by
  comparing the backing Tk var's *coerced* value against the Python `checked_value`
  (`self._internal.get() == self._checked_value`) — type-fragile, only correct when
  the var type matched the value type. **(#358)** `Checkbox(tristate=True)` never went
  indeterminate — `BooleanVar` can't hold a third value and the dash never rendered;
  `.value` returned `False` not `None`. **(#359)** `ToggleButton(value=True).checked`
  returned **`False`** (StringVar-backed → `'1' == True` is `False`). **Latent:** a
  non-bool `checked_value`/`unchecked_value` (`"yes"`, ints) was silently coerced away
  on Checkbox/Switch. **Fix = read the ttk `selected`/`alternate` STATE** (var-agnostic)
  in `.value`/`.checked`/`_command`; a shared **`_apply_value`** maps the public value
  onto on/off + the indeterminate flag. **Two gotchas the empirical probes caught:**
  (1) **`configure(command=...)` RESETS ttk state** — so seeding must run AFTER it
  (indeterminate `alternate` set earlier is wiped); (2) a **var write clears
  `alternate`**, so indeterminate = set off-value THEN flag `state(('alternate',))`,
  and the explicit `!alternate` clears elsewhere are redundant. **Var-type fix pushed
  to the PRIMITIVE** (`checkbutton.py`), **consistent with RadioGroup/ToggleGroup**
  (both do `StringVar(value=...)` explicitly — the precedent that made the tk import OK):
  inject a `StringVar` **only when non-bool on/off values are given**, else keep the
  `BooleanVar` so the **default control's auto-created `.signal` stays boolean** (the
  code-review caught that always-StringVar leaked `'1'`/`'0'` strings through `.signal`,
  where `"0"` is truthy — a real regression; conditional injection closes it). **Adversarial
  `/code-review` (high) found 5, 2 real** — the `.signal`-type leak (fixed) + a redundant
  `!alternate` (removed); the other 3 were non-issues (tristate+signal is documented;
  `.value` fallback is more-correct; `_prev_value` staleness didn't reproduce). NB
  **ToggleButton was ALREADY StringVar** (its `class_='Toolbutton'` dodges the
  `TCheckbutton`→BooleanVar inference in `infer_default_value_for_widget`), so its
  `.signal` was always string — no regression there. Tests **`test_boolean_controls.py`**
  (the `.value`/`.checked`/tristate coverage these widgets NEVER had — which is why all
  three shipped; 8 fail pre-fix). Docs: tristate scene added to the Full Example +
  **regenerated `checkbox-tristate-*.png`** (old ones rendered indeterminate as
  unchecked). **Process win: running empirical probes beat static reading repeatedly** —
  the `configure(command)` reset, the var-write-clears-alternate rule, and the
  ToggleButton-already-StringVar fact were all discovered by driving the widget, not
  reading it.
- **0.1.4 PATCH SHIPPED — `Select.add_validation_rule` restored (PR #357;
  2026-07-20).** `bootstack 0.1.4` is on **PyPI** + tagged **`v0.1.4`** ("Select
  validation fix"). Also re-worded the PyPI **`description`** (maintainer's pending
  "built on Tk" tagline, folded into this cut). **Bug (user `bLynnb2762`, #356):** a
  **0.1.3 regression** — `form.field(key).add_validation_rule(...)` on a `select`
  editor raised `AttributeError: 'Select' object has no attribute
  'add_validation_rule'`. **Root cause:** PR #354 (0.1.3) made `Form.field()` return
  the **public wrapper** widget; the field-family wrappers carry `add_validation_rule`
  via `field_mixin`, but `bs.Select` did **not** — and among the non-field editors its
  internal `SelectBox` was the only one that had been inheriting it (from the `Field`
  composite). So Select was the single casualty. **Fix (bounty PR #357 by external
  contributor AnasBabari):** add `add_validation_rule` on `bs.Select`. **My review +
  refactor:** the contributor's first pass hoisted `message`/`trigger` params with a
  **`trigger="change"` default — but `'change'` is NOT a valid `RuleTriggerType`**
  (`key`/`blur`/`always`/`manual`), so a rule added with no explicit trigger only ran
  on manual `validate()`, never live. Refactored to **mirror the field-family
  signature exactly** — `add_validation_rule(self, rule_type: RuleType, **kwargs)`
  delegating straight through — which lets `ValidationRule`'s per-rule
  `_default_trigger()` apply (required→`always`). Pushed onto the fork PR branch
  (`maintainerCanModify`), squash-merged (contributor keeps authored credit + bounty).
  Test added to `test_form_editor_options.py`. **CHANGELOG/close gotcha:** #356 used
  `Fixes: <url>` (colon) which GitHub's auto-close does NOT parse → closed manually.
- **0.1.3 PATCH SHIPPED — Form `editor_options` use public widget kwargs (PR #354,
  #353; 2026-07-17, pre-session).** `bootstack 0.1.3` on **PyPI** + tagged **`v0.1.3`**.
  Form built the **internal** impl widgets and forwarded `editor_options` raw, so users
  had to pass Tk option names (`increment` not `step`) and `textarea` couldn't take
  `show_border`. Rewrote `_build_field` to construct the **public wrapper** widgets via
  `_construct_editor`, so `step`/`min_value`/`show_border`/`mask`/slider-bounds work as
  documented; **`field()` now returns the public wrapper** (the change that regressed
  Select validation — see 0.1.4). Also a homepage-tagline docs commit landed on `main`
  the same day. **NB this predates the session** — recorded here because CLAUDE.md had
  gone stale at 0.1.2.
- **0.1.2 PATCH SHIPPED — dropdown/context menus dismiss on window move (PR #345;
  2026-06-25).** `bootstack 0.1.2` is on **PyPI** + tagged **`v0.1.2`**. **Bug
  (user-reported, Win10):** an open toolbar `add_menu` dropdown (and any Win/Linux
  `ContextMenu`/`Select`/`MenuButton` popup) stayed pinned at its old screen
  position when you dragged/resized/minimized the window — it "hung in the air."
  The `_ToplevelContextMenu` (overrideredirect Toplevel backend) only dismissed on
  **outside mouse clicks** bound on the owning window; dragging the native title
  bar fires no click, only `<Configure>`/`<Unmap>` on the toplevel, which nothing
  listened for. **Fix:** while shown, also bind the binding-root's
  `<Configure>`/`<Unmap>` → new `_on_window_change` method dismisses (guarded to
  `event.widget is the toplevel` so a child relayout doesn't close it); torn down
  with the existing outside-click cleanup. Shared backend → fixes ALL Win/Linux
  popups at once. Verified decorated AND undecorated (both move via `wm geometry`
  → `<Configure>`); macOS `_NativeContextMenu` untouched (native menu self-dismisses).
  **NB this is the window-MOVE bug — DISTINCT from #207** (the `'break'`-target
  dismiss case, still OPEN; I confirmed a `'break'` toolbar widget already dismisses
  here). Tests in `test_toolbar_menu.py` (window-change dismissal + binding
  teardown). **Process:** empirical self-driving repro (move window, assert
  `winfo_viewable()`) was decisive — static reading missed that no click fires on a
  title-bar drag. Confirmed Py 3.12.10's `unbind(seq, funcid)` removes only that
  funcid (not the unbind-wipes-all of older Tkinter), so binding `<Configure>` on
  the app toplevel is safe. **CHANGELOG gotcha (fixed):** `## [0.1.1]` was a
  bracketed link with NO `[0.1.1]:` definition (dead link); added `[0.1.1]:` +
  `[0.1.2]:` defs. **Release-notes gotcha:** `release.yml` extracts ONLY the
  `## [x]` section, so the bottom link-defs are excluded → `[0.1.2]` renders as
  literal brackets in the GitHub Release body (see Next-up for the fix).
- **0.1.1 PATCH SHIPPED — `pygments` declared as a runtime dependency (PR #344;
  2026-06-24).** `bootstack 0.1.1` is on **PyPI** and tagged **`v0.1.1`** (GitHub
  Release, notes from the CHANGELOG `## [0.1.1]` section). **Bug:** `CodeEditor`
  hard-imports `pygments` (via `_try_install_highlighter`) for syntax highlighting,
  but it was declared as a dependency **nowhere** in `pyproject.toml` — so a clean
  `pip install bootstack` (no incidental pygments) crashed on any
  `CodeEditor(language=...)`, including the bundled `bootstack` demo's editing page
  (`ModuleNotFoundError: No module named 'pygments'`). Fix = add `pygments>=2.15`
  to `[project].dependencies` (hard dep, per the maintainer — pure-Python, no
  transitive deps, and highlighting is core to a top-level `bs.*` widget; matches
  batteries-included). **Full dependency audit done while here — `pygments` was the
  ONLY gap:** every optional extra (`viz`/matplotlib, `parquet`/pyarrow,
  `excel`/xlsxwriter, `hdf5`/pandas+tables, `viz-seaborn`/seaborn) is lazy-imported
  inside functions and gated by `_require(...)`/`_require_matplotlib` (so `import
  bootstack` + core widget construction never crash); `PyInstaller` is a
  packaging-time tool (`try/except` in the CLI); `tomli` is a dead fallback
  (`tomllib` is stdlib on `requires-python >=3.12`); `cycler` is guarded + ships
  with matplotlib. **Release process note (CORRECTED 2026-07-21):**
  `bump-my-version` IS available — `.venv/Scripts/bump-my-version.exe`, v1.3.0 — so
  the normal `bump-my-version bump patch` flow works. (The 0.1.1 session could not
  reach it and replicated the config by hand: bump BOTH `version` (line 7) and
  `[tool.bumpversion] current_version`, commit `Release X`, annotated tag `vX`.
  That manual path is the fallback, not the norm.)
- **0.1.0 STABLE SHIPPED — ship gate + theme-repaint unification + accent contrast
  (2026-06-24).** `bootstack 0.1.0` is on **PyPI** (`pip install bootstack`, no
  `--pre`) and tagged **`v0.1.0`** (stable GitHub Release, `prerelease=false`).
  Verified on **Windows AND macOS**. **#149 ship gate (PR #335 — MERGED):**
  public-surface audit + lock + CHANGELOG + Release Notes + Roadmap page; the
  folded items shipped in **PR #334** (`text=<Signal>` → `TypeError` guard across
  text-bearing widgets; `cli/run.py` double-cwd fix). `bootstack.__version__` is
  already DYNAMIC (`importlib.metadata`), so the "stale 0.1.0a6" worry was moot.
  **Pre-release framing removed (PR #342):** README/CONTRIBUTING warnings gone;
  pyproject `Development Status` 3-Alpha→**4-Beta** (Beta over Production/Stable —
  no production mileage yet; pandas precedent = bump to 5 once earned, not at 1.0)
  + fixed the bogus `Environment :: X11 :: GTK` (it's **Tk**) → Win32/MacOS X/X11.
  **GitHub Release notes now come FROM the CHANGELOG (PR #343):** `release.yml`
  checks out the repo and extracts the `## [<version>]` section as the release
  body (GitHub's auto "What's Changed" appended below; an alpha tag with no
  section falls back to auto-only). **Theme-repaint unification (PR #338):**
  replaced THREE overlapping mechanisms (STD-publisher + `_enable_theme_repaint`;
  `register_tk_widget` WeakSet + `<Map>` registry — RETIRED the grows-forever
  leak; per-widget hacks) with ONE rule — a tree widget defines
  **`_bs_apply_theme(self)`**, driven by `Style.apply_theme_walk(root,
  only_stale=)` (theme-change → walk VISIBLE from root; container-show → walk
  STALE subtree IGNORING `winfo_viewable()`, unreliable across a canvas boundary);
  show-triggers in PageStack (covers Tabs) + Expander (covers Accordion);
  non-tree reactors (Image handle / window chrome / app `on_theme_change`) stay on
  root `<<BsThemeChanged>>`. The meter canvas takes the surface TOKEN (not a frozen
  hex) so the walk re-resolves it; `style_resolver` now lets an explicit `surface=`
  win over inheritance (the gauge "bg doesn't recolor" root cause). Dev note
  **`docs/_dev/theme-repaint-architecture.md`**. **Accent text-on-color fix (PR
  #340):** `on_color` light-mode white gate 4.5→**3.0** (the large/bold WCAG bar
  that button labels meet) so saturated colored accents read white in BOTH modes
  (dracula-light purple primary was wrongly black) while bright cyan `info`/yellow
  `warning` stay black; + a contrast FLOOR catching bucket-edge cases in either
  mode (catppuccin-dark `warning` was white at ~2:1). Test `test_on_color_contrast.py`.
  **macOS fixes (PR #339, local agent):** kept nav pages mapped (#336) + anchored
  toasts to the visible frame above the Dock (#337). **Dead-test cleanup (PR
  #341):** deleted stale `test_gauge_theme.py` (asserted #338-deleted mechanisms)
  + fixed `test_icon_image_props.py`'s private-fixture/no-container setup. Milestone
  **0.1.0 (stable) CLOSED** (11 issues); **#322** (provisional hot-reload umbrella,
  E2E test still deferred to the maintainer) moved to **0.1.1**.
- **Hot-reload follow-ups #325/#326/#327 + #328 docs (PR #333 — MERGED;
  2026-06-24).** Four fixes on PROVISIONAL `bootstack.dev`, one PR. **#325:**
  AppShell `_dev_reset_region` restores the status band to its forced state
  (`set_statusbar_visible(False)` unless `show_statusbar=True`) so an empty band
  doesn't linger after a no-segment reload — AND `show_statusbar=True` now genuinely
  forces the band visible at construction (was materialize-only; stored
  `self._show_statusbar_forced`); App/AppShell reset now CANCEL a scheduled
  native-menu `after_idle` (new `ChromeHostMixin._cancel_native_menu_pending`) vs
  nulling the handle (macOS double-fire). **#326:** the per-page fast path is gated
  on EVERY changed file being a builder module (`_builder_module_files`) — a changed
  non-builder/state module takes the full reload-then-reexec instead of a selective
  `importlib.reload` that splits object identity without rebinding. **#327:** watch
  root widens from the entry file's dir to the project `src/` tree
  (`_project_watch_root` walks up to `bootstack.toml`; falls back to the file dir for
  loose scripts); watcher snapshot stamps `(mtime, size)` to catch same-tick saves;
  symlink/scope caveats documented. **#328 (docs only):** added a "Gating dev-only
  code" section for `is_dev_mode()` — **the E2E multi-file `@reloadable` reload test
  is the remaining #328 piece, DEFERRED** (the maintainer will do it). Tests: watcher
  tuple + size-change; `_project_watch_root` widen/fallback; shell GUI legs green.
  **Naming note (`set_*_visible` is INTERNAL):** `ShellLayout.set_statusbar_visible`
  / `set_rail_visible` / `set_sidebar_visible` / `set_dock_visible` are an internal
  family (public uses verbs `show_sidebar()`/`hide_sidebar()`/`toggle_sidebar()` +
  `show_statusbar=`); **#332 filed** to rename the internal family to the idiom (low
  priority). Memory `project_hot_reload` (followups thread).
- **Docs-IA: fold Production into the User Guide + caption renames (#323/#324;
  2026-06-24).** The docs navbar dropped from **4 pillars to 3** (**User Guide ·
  Widgets · API Reference**). The former **Production** pillar folded into the User
  Guide as a new **Developer tools** caption (`cli`/`hot-reload`/`debugging`/
  `distribution`); **`App Configuration`** (`/production/app-settings`) moved to the
  **Feature guides** caption (it's a subsystem guide, not tooling/shipping). **#324
  decision = fold-into-User-Guide** (maintainer chose it over rename-in-place /
  reorder). The **Topics** caption was renamed **Feature guides** (more descriptive of
  the subsystem deep-dives; the locked constraint is only "not Concepts/Explanation").
  **#323:** the `Composing Fields` how-to renamed → **`Customizing Fields`**
  (`/tasks/composing-fields` → `/tasks/customizing-fields`) to kill the "Composing X"
  clash with the new **Composing with Builders** how-to (it's about *specializing* a
  field, not decomposition). Leaf pages STAY in `production/` (no URL churn — internal
  dir name only); the one accepted churn is the #323 rename (no redirect mechanism →
  dead old URL, fine per no-shims). `production/index.rst` DELETED. Inbound `:doc:`
  refs + 6 widget See-also links repointed. Clean `-W` build, no orphans. Memory
  `project_docs_ia_pillars`.
- **Builder-function scaffolds + examples audit (PR #330 — MERGED; 2026-06-24).**
  The staged builder-pattern work the roadmap flagged as "START HERE." **#321:**
  every CLI page/view scaffold flipped from a class
  (`__init__`/`_build`/`self.root`) to a **`build_<name>()` builder function**
  (`cli/templates/__init__.py`). Layout moved onto the page region — AppShell pages
  paint **directly** into the page (`padding`/`gap`/`horizontal_items` on
  `nav.add_page(...)`; the page IS the column, no inner wrapper); basic **pack** view
  paints into the padded App body, **grid** view opens a `bs.Grid` (a layout the
  column body lacks — not redundant; needs `horizontal="stretch"` to fill);
  **master-detail** `build_detail(record)` opens its **own** padded `Column` (the
  detail region is a bare `ContentHost` fill area, no padding). Stateful handlers
  became **closures over local field refs** (not `self.*` methods) — the documented
  "builder default, class is the escape hatch" story. `add page`/`add view` emit
  `build_<name>` (suffix-stripped: `DashboardPage`→`build_dashboard`) + matching
  wiring hints (new `_build_func_name`/`_readable_title` helpers). **Naming
  convention LOCKED:** *component* builders are bare (`user_card`), *page/region*
  builders are `build_<name>` — a **Naming** note in the **Composing with Builders**
  how-to ties scaffolds + how-to into one system. **#320 Part 2:** flagship
  `docs/examples/appshell.py` factors its metric cards into a reusable
  `metric_card()` builder; nav examples were already class-free (the reshape did it);
  the `bootstack gallery` demo already uses `_build_*` builders (left as-is — its
  inner `Column` is legit scroll-content padding for `scrollable=True` pages, NOT
  class-view redundancy). **#320 Part 1 + the `_resolve_parent` guard shipped in
  #329** (the guard at `base.py:97` raises a clear `BootstackError` when a builder is
  called with no active container + no `parent=` — matches the how-to's "one rule").
  Verified: all 6 scaffold variants build in isolated subprocesses, the printed
  add-page wiring builds end-to-end, 186 cli/public-surface tests, clean `-W` docs
  build. Memory `project_builder_scaffolds`.
- **Hot reload — `bootstack dev` + feature-review fixes (PR #329 — MERGED;
  2026-06-24).** The dev workflow (BUILT on `feat/hot-reload` in the prior
  session) got a **4-reviewer adversarial audit + fixes**, then merged.
  `bootstack dev app.py` re-execs the `with bs.App()` body in place on save
  (window + module-level signals/sources/stores + active route survive; broken
  edits show an in-window banner); `@reloadable` rebuilds just one page's region
  (multi-file); a restart fallback covers function-wrapped apps (auto-selected;
  `--restart` forces). New **PROVISIONAL** `bootstack.dev` (carved OUT of the
  0.1.0 freeze): `reloadable` + `is_dev_mode`. **Blockers the review caught +
  fixed:** 🔴 **win32 `os.execv` restart was BROKEN** — execv does NOT replace the
  process in place on Windows (new PID + caller exits), so the supervisor died
  after the FIRST reload (the prior session's "Verified Windows" missed it — it
  only exercised in-process). Replaced execv with a **CLI `subprocess.run`
  supervisor loop** on a sentinel exit code (`DEV_RESTART_EXIT_CODE`), made
  **crash-resilient** (a broken edit waits-and-relaunches instead of ending the
  session — surfaced by LIVE testing, not the static review). 🔴 **AppShell/
  Workbench error banner was dead** (`_content_frame` is a method on shells, an
  attr on App — reloader now resolves both). + `relative_to` guard on an
  absolute/`..` entry. **Docs IA:** the builder-functions guide became the
  **"Composing with Builders"** how-to (`docs/tasks/composing-with-builders.rst`
  — goal-indexed, not a subsystem topic) + restart-mode "when to force
  `--restart`" guidance + the demo video / README hero. Reviewers over-flagged
  (the mount-accumulation suspicion was disproved — `reset_mounts` is wired).
  Memories `reference_win32_execv_not_inplace`, `project_hot_reload`.
  **Non-blocking follow-ups filed: #325** (reset-cleanup gaps), **#326**
  (`_reload_modules` identity-split scoping), **#327** (watcher scope/polling),
  **#328** (multi-file reload test + thin is_dev_mode docs). **Docs-IA spin-offs:
  #323** (rename "Composing Fields" → "Customizing Fields") · **#324** (rethink the
  "Production" pillar). Process note: **running it caught what reading it didn't.**
- **Splash screen — cross-platform `windowtype` + `bs.Splash` (PRs #313, #318 —
  MERGED; 2026-06-23).** Two-step feature, each its own branch→PR→`main`.
  **#308 (PR #313):** `Toplevel(windowtype=...)` was honored only on macOS
  (`MacWindowStyle`) and X11 (`-type`); **win32 never read it**. Added a win32
  branch (`_runtime/toplevel.py`) translating the chromeless types
  (`splash`/`tooltip`/`dock`) → `overrideredirect` and `utility` → `-toolwindow` —
  **one switch, all three platforms** (maintainer chose the auto contract: the
  caller need NOT also pass `overrideredirect=True`). macOS asymmetry preserved for
  free (`overrideredirect()` already no-ops on Aqua). **#310 (PR #318):**
  **`bs.Splash`** — a borderless intro screen (its own `Toplevel`,
  `windowtype="splash"`) constructed inside the `App` context. **Registration, not
  suppression:** construction resolves the ambient app and registers on it; the
  internal `App.mainloop` gained ONE branch — if a splash is up, defer `show()`
  until it dismisses (`_notify_app_ready`). **Shows at its own `__exit__`** (after
  content authored, before the synchronous body build it precedes — so it genuinely
  covers that cost) with `update()` to force paint; the `with` block scopes content
  only, not lifetime. One dismiss knob `until=` (`'ready'`|`<float>`|`'manual'`) +
  `skippable`/`dismiss()` on top + `min_duration` floor under all. Best-effort
  `after()`-driven alpha fade (snaps where unsupported). Lean surface: `is_showing`,
  `dismiss()`, `on_dismiss`→`SplashDismissEvent(reason)`; guards (no app / second
  splash → `BootstackError`). Added `SplashDismissEvent`/`SplashDismissReason` to
  `bootstack.events` + the events API ref; **re-homed the drifted `SashMoveEvent`/
  `ScrollEvent`** there too. Docs: `widgets/splash.rst` + a `tasks/splash-screens.rst`
  how-to (cover-startup, timed branding, welcome, **real progress via worker thread
  + Signal**, and the **event-loop timing rule** — motion only shows while the loop
  turns, so a `'ready'` splash over a synchronous build is a STILL image by design).
  Tests `test_splash.py` (14). **Process catches (maintainer caught both):** a stray
  "Tk" in the how-to broke the no-toolkit-in-docs rule; and `events.rst` had silently
  drifted from `events.__all__` — fixed + added a coverage guard (PR #319,
  `test_events_doc_coverage.py`). Memory `project_splash_widget`.
- **Icon-DPI sizing + Tooltip subtree coverage (PRs #306, #307, #309 — MERGED;
  2026-06-23).** Three small fixes off the 0.1.0 cleanup backlog, each its own
  branch→PR→`main`. **#267 (PR #306):** the public `Image` handle (`get_icon` /
  `image=`) and the MenuButton chevron rendered glyphs at their literal *logical*
  size and so read soft at fractional/high DPI. Fix = new **`scale_icon_size(base)`**
  (`_runtime/utility.py`, logical→physical, floored at base like
  `scale_padding_floor`) applied in both `Image` render paths (`_load_pil`,
  `_materialize`; reported `width`/`height` stay logical — public contract unchanged)
  + the chevron routed through `b.scale()` to match combobox/spinbox. **Adversarial
  verification overturned the issue's headline:** the Workbench rail was NOT soft (it
  already scales 28→41 via `normalize_icon_spec`); the soft paths were only the public
  handle + the chevron. **#305 (PR #309):** text+icon `Button`/`MenuButton` icons
  *double-scaled* at high DPI — `icon_size()`'s text branch returned the font ascent
  (already physical), then `normalize_icon_spec` re-scaled it. Fix = that branch now
  returns logical (`round(ascent / ui_scale)`) so normalize is the single scaler.
  **Validated row heights** at both densities × DPIs: this fixed a real ~10px
  inflation of the COMPACT text+icon button at 150% (65→55, matching siblings).
  **#260 (PR #307):** `Tooltip.refresh_bindings()` (public + internal, mirroring
  `ScrollView`) re-covers a container target's subtree for children added *after*
  attach (`propagate_target_bindings` only tags descendants present at attach time).
  **#207 DEFERRED** (maintainer call): no API implication, low self-inflicted impact,
  Win/Linux only; the risky grab fix breaks reopen-at-new-spot — agreed proportional
  fix if revisited is an open-menu registry. Memory
  `reference_icon_dpi_scaling_pipeline`. Process note: the empirical icon-size probe
  (`development/probe_icon_sizes.py`, untracked) was decisive — static reading of the
  4-mechanism scaling pipeline was too tangled to trust.
- **Trust audit of the 2026-06-22 session + fixes (PRs #301, #302 — MERGED;
  2026-06-22).** A prior agent (on another machine) shipped 14 PRs (#289, #291–#299
  + releases `0.1.0a14`); the maintainer found repeated errors/hallucinations and
  asked for a full review. Method: **5 parallel adversarial reviewers** (one per PR
  cluster) + clean `-W` docs build + full GUI suite. Verdict: mostly sound but **not
  trustworthy as-is**. Brief: **`docs/_dev/review-2026-06-22-trust-audit.md`**.
  Fixed in **PR #301**: (1) 🔴 **#299 toolbar regression merged with a FAILING test**
  — `_apply_bar_defaults` used "has `**kwargs`" as a proxy for "accepts
  `density`/`surface`", crashing `add_widget(Checkbox/Switch/ToggleButton/Radio)` and
  no-op for `TextField`/`Select`; fix = inject only **explicitly-declared** params;
  (2) 🟠 **DataTable `iter_rows` clobbered the shared source** — the view-mutation CM
  spanned a `yield`, leaking this view's filter/sort onto the shared source until GC;
  fix = wrap each read, not the yield (+ regression test proven to fail pre-fix);
  (3) 🟠 two **`lambda ok: btn.disabled = not ok`** docstrings (SyntaxError) →
  named-handler; (4) the **`-W` docs build was broken** since PR #266
  (`widget-sizing.rst` titles inside an include skipped a heading level) → `.. rubric::`;
  (5) DataTable test hygiene (hallucinated `enable_search=` → `searchable=`; `_internal`
  pokes → public); (6) `signals/README.md` rewritten (was pervasively stale —
  `get()`/`unsubscribe()`/`bs.Entry`/`app.mainloop()`/the `master=` gotcha #292
  overturned); (7) **CodeEditor #296/#297** (selection API, block indent/dedent) and
  **ScrollView #298** (`on_scroll`/`scroll_position`/keyboard) shipped undocumented +
  untested → docs + **20 new tests** + docstring fixes (incl. `scroll_position` no
  longer claims `(1.0,1.0)` reachable); (8) **#262** — `Toolbar.add_button`/`add_label`
  returned internal `_impl` primitives → now return public `bs.Button`/`bs.Label`
  (live props); added **`surface=` to `bs.Button`** (construction-only — *build-time,
  not a live property*; matches the surface a ghost/outline button sits on so it
  blends; a toolbar sets `'chrome'` for the buttons it builds); preserved
  draggable-titlebar label drag via internal `Toolbar._attach_drag`. **PR #302**:
  documented `surface=` in `button.rst` (usage-only, no implementation detail).
  **Verified clean (no over-flag corrections):** #292 Signal lazy-realization rewrite
  is correct; #295 internal-access scrub, carousel #289, pyinstaller #291, new chart
  example all check out. Two reviewer **over-flags disproved**: the #296 `read_only`
  "fix" was a no-op rename, and `Toolbar._surface` is always defaulted by the base
  Frame (no `AttributeError`). **Process gotchas (bit me):** piping a build/test
  command to `tail` masks its exit code with `tail`'s 0 — *never pipe the command
  whose status you need* (it hid both a failing test leg AND the broken docs build);
  toolbar item spacing is now uniform `padx=2` (the pack-based bar has **no `gap`** —
  a real gap migration is the unified-toolbars rework, `project_unified_toolbars`).
  **Now-DONE issues (close them):** #246, #251, #252, #254, #255, #262, #263.
- **Pre-release `0.1.0a12` shipped + demo rebuild + CONTRIBUTING + Topic-guide
  review** (2026-06-21; all MERGED). Cut **`0.1.0a12`** to PyPI + GitHub Release
  (`bump-my-version bump pre_n` → push `main` + tag → `release.yml` → `docs.yml`).
  Landed in it: the **Topic-guide technical-writer review** (#155, PR **#268** —
  verified all 12 `docs/reference/*` against the standard; the assessment agents
  **over-flagged**, only **2 real fixes** came out: a typed-signal section in
  `signals`, two missing imports in `typography`; the other 10 already met it —
  *adversarially verify agent claims*); the **hero-first demo rebuild** (#269, PR
  **#270** — `cli/demo.py` 995→564 lines, 18→12 hero pages, fixed the
  `AppShell(nav_variant=)` launch crash, the "broken demo"); the **README** refresh
  (centered screenshots, fixed the broken `shell.add_page` example, stale 8→real 10
  theme list, +Workbench/Window/ThemeToggle, +`appicon`/`promote` CLI, demoted
  `add i18n`, re-shot gallery + hero); and **`CONTRIBUTING.md`** (PR **#271** — dev
  setup + feature-branch→`main` PR flow + localization-review section reusing #17's
  language; **closed the localization issue fan-out** #17/#19–#37). Verified
  pre-ship: CLI + all 6 templates scaffold/build/`add`/`doctor`/`icons`/`appicon`.
- **Docs lead-in + screenshot-refresh pass — PR #266 (MERGED)** + the
  **interactive-widget review initiative COMPLETE.** All interactive widgets are
  now reviewed (Button #243/#244, ButtonGroup #245, TextArea #247/#248, CodeEditor,
  ScrollView, SplitView, Tooltip, Toolbar, StatusBar — each its own merged PR). Then
  **PR #266**: ~45 widget pages got a Usage **mental-model lead-in** (intro stays
  definitional; teaching leads the Usage section; no bare Usage); the widget-sizing
  include split **Row vs Column** (different cross-axis options — Column uses
  `horizontal` for cross-align + `grow` fills vertical, Row the mirror); **dialogs
  now capture like app windows** — routed the dialog target through the App/Window
  DWM-extended-bounds + `inset=2` path so the native frame is cropped and a **single
  CSS border + shadow** replaces it (`.bs-dialog-screenshot` shares the
  `.bs-window-screenshot` rule; no native/CSS double border); two **broken dialog
  scenes** (`message-dialogs`, `dialog`) fixed — they parented raw tk primitives
  into the dialog's now-public-`Column` content area (rewritten with public widgets);
  the **filter-dialog value list rebuilt on the managed `FlexFrame` content** the
  public ScrollView uses (dropped the legacy raw `ttk.Frame`-in-canvas + a redundant
  racing `<Configure>` width binding — fixed the clipped/deformed list); stale
  screenshots regenerated (app/window/appshell/workbench/card/home-hero/navigation)
  and the **workbench hero image** wired into its page. **Filed #267** — DPI-aware
  icon sizing (icons render soft at fractional DPI: sizes hardcoded, **no `ui_scale`**
  multiplier anywhere; rail worst at 28px; own branch). Investigation gotcha: the
  workspaces nav shot's softness is the **icon DPI issue (#267)**, not capture width
  — the Workbench renders the same 720px as the AppShell scenes, native capture, no
  downscale (a `_capture_max_width`/size bump was tried and **reverted**).
- **Widget-review initiative — Button · ButtonGroup · TextArea** (prior session;
  all MERGED). Began the "finish reviewing the interactive widgets" sweep
  (audit→fix→test→docs→follow-ups, one PR each). **Button** (#243; walk-backs
  #244): activation-based `on_click` (class map → `<<Click>>` from a command
  dispatcher → fires on mouse/keyboard/`click()`, honors disabled, Stream-composes)
  + `text` setter routes through the bound var; **walked back** an over-eager
  `disabled`/`text` getter change (only broke via an internal side-hack — test
  public paths, not pokes). **ButtonGroup** (#245): no correctness bugs (disabled
  propagation + `on_click` verified); docs (Events/Keyboard) + bare-`except` fix;
  `accent/variant/density/orient` kept construction-only (not runtime needs).
  **TextArea** (#247): read-only state desync (broke programmatic `value=`/`insert`),
  placeholder flipping read-only off, and a **Tab focus-trap** all fixed; docs got
  Validation+Keyboard sections. Native-bindings follow-up (#248): undo/redo now use
  Tk's `<<Undo>>`/`<<Redo>>` virtual events (platform-correct keys; CodeEditor
  benefits too). Swept the rest for hardcoded-key reinventions — none others (custom
  shortcuts are intentional). Memories `project_button_review`,
  `project_widget_review_initiative`, `feedback_live_properties_runtime_need`,
  `feedback_prefer_native_bindings_dont_undo_conventions`. Also this session:
  **#234 SpinnerField parity** (#241, increment/decrement methods only),
  **#222 CLOSED won't-do** (live placeholder/mask).
- **Typed-signal round-trip + high-DPI border fix** (this session; PRs **#238** +
  **#239**, both MERGED). Two field follow-ups closed end-to-end:
  - **#227 — `Signal` now round-trips object values** (PR **#238**). `Signal` chose
    its Tk var from the initial value's type, so a `date`/`time`/object landed in a
    StringVar and `sig()` read back the **string**. Fix = an **object mode** for
    non-Tk-native values (anything not `bool`/`int`/`float`/`str`/`set`): the cached
    Python object is the source of truth (`__call__` returns it), the StringVar is
    just the write-trace bus (`set()` dedupes on the object, writes `str(value)` to
    notify). **Native signals are byte-for-byte unchanged** (branch only activates for
    objects → zero regression). Also fixed: `ValueSignalMixin._sync_value_set()`
    (called from each field's `value` setter) pushes a **programmatic** `field.value=`
    to the bound signal (was on_change-only). **`textsignal=` REMOVED from
    `NumberField`/`DateField`/`TimeField`** (typed fields bind via `signal=`; guarded
    with a `TypeError` since `**kwargs` would silently swallow it) — Date/Time docs
    now feature typed `signal=` with a `.map()`-derived text signal for display. This
    also resolved **#237** (the user report that kicked it off). Escape-hatch caveat:
    `sig.var`/`sig.tk` returns the backing StringVar (string form); `sig()` is the
    supported path. Memory `project_field_value_signal_dtype`.
  - **#90 — high-DPI entry border washout** (PR **#239**). On high-DPI the resting
    (unfocused) field border vanished (focus border fine; `hdpi=False` fixed it). The
    visible border is a **`ttk_class="TField"` nine-patch whose slice scales with
    DPI**, but the gap to the inner widget was a **hardcoded `padding=5`** — at high
    DPI the slice outgrows the gap and the child **overpaints** the border. Fix =
    **`scale_padding_floor(base)`** (`_runtime/utility.py` =
    `max(base, round(base*ui_scale))`): **round** not truncate (1.5x kept clipping the
    rounded corners with `int()`), **floor** at base (low DPI keeps tuned spacing).
    Applied at both TField sites — the `Field` composite (all 7 field widgets) **and**
    `TextArea`/`CodeEditor`. **Not** the image/LANCZOS path (probe proved the image
    keeps full contrast; the cap idea was a dead end). **`show_border` widgets**
    (context menus/toasts/snackbars/tooltips/Select popup) use a fixed ttk relief
    border, **unaffected**. Repro without 4K hardware via `App(scaling=2.667)` (the
    washout is driven by the scale *number*). Memory
    `reference_hidpi_ninepatch_border_padding`.
- **Field-family widget reviews + validation follow-ons** (this session; all
  MERGED) — closed out the `TextField` review that spawned the validation rebuild,
  then reviewed the whole **field family** one PR each (audit→fix→test→docs→
  file-follow-ups). **Validation follow-ons first:** **#216** (PR **#219**) —
  `NumberField(value=None)`/`value=""` crashed at construction (`float('')`; an
  empty number field stores `''`, the guard only checked `is not None`) → normalize
  empty→`None`, skip bounds. **#217 part 1** (PR **#220**) — reactive **`Form.valid`**
  (`Signal[bool]` AND-ed over the member fields' `valid` signals via subscriptions)
  + **`Form.errors`** (live `dict[str,str]` from the fields' `error` signals), on
  internal+public `Form`; a submit button binds `form.valid`. **#217 part 2
  (stream-based triggers) DEFERRED** — re-evaluated as pure internal churn (current
  `_setup_validation_binds`/`after()` works, not Tk-coupled). **Docs cross-ref rule**
  (PR **#221**) — added to `docs/_dev/widget-review-and-docs-standards.md`: a widget
  section on a cross-cutting subject (validation/events/data/layout/…) must
  `:doc:`-link the matching how-to/topic guide (the field-items *Validation* gap was
  the trigger). **Then the 7 reviews:** TextField (#223), NumberField (#224),
  PasswordField (#225 docs + **#229** read-only-reveal fix), DateField (#228),
  TimeField (#230), PathField (#231), SpinnerField (#233). **Pattern:** NO wrapper
  had correctness bugs (every audit-agent "critical" claim died under adversarial
  verification — e.g. the "addon-state bypass" was false: `configure(state=)` routes
  through `Field._delegate_state` which syncs addons; "`.text` needs a setter"
  contradicts the locked read-only value/text contract). The yield was **docs** —
  every page lacked the `/reference/validation` cross-link, the reactive
  `field.valid`/`field.error` surface, and a fleshed See-also; each got a
  mental-model lead, Date/Time/Path gained full Validation sections. **Two real code
  changes (decided with maintainer):** PasswordField reveal toggle now `active_when_
  readonly=True` (#229 — the flag postdates the widget; revealing only flips the mask
  char, safe under read-only); **TimeField now starts EMPTY** (#230 — was
  `datetime.now().time()` in `timeentry.py`, the only field not starting empty, which
  silently **defeated `required=True`**; pre-release clean break). **Systemic bug
  fixed across the family:** validation screenshot scenes called `field.validate("blur")`
  but public `validate()` takes **no** arg (raised in the `after()` tick → error never
  rendered); fixed to `field.validate()` + regenerated. **Open follow-ups (additive,
  not bugs):** **#227** (`Signal` is StringVar-backed for objects → `Date/TimeField`
  `signal=` reads back a *string*, and field→signal doesn't fire on programmatic
  `.value=`; so Date/Time docs keep `textsignal=`; NumberField unaffected) · **#232**
  (PathField dialog-config options as live properties) · **#234** (SpinnerField↔
  NumberField parity: increment/decrement, live min/max/step). Memory
  `project_field_family_review`. **Process gotcha:** a fix pushed to a branch AFTER
  its PR merged is stranded — cherry-pick onto a fresh branch (bit us with #225→#229).
- **Field validation redesign** (PR **#218**, MERGED) — started as a `TextField`
  review (audit→fix→test→docs), surfaced that validation was **fundamentally
  broken for typed fields**, and turned into a 4-phase rebuild. **Phase 1:**
  validation now runs against the field's **typed value** via one resolver
  (`TextEntryPart._get_validation_value` = `_parse_or_none(get())`;
  `NumberEntryPart` override coerces to its numeric type) — all 7 field wrappers
  route through it (was 4 passing the raw datum → `TypeError`, 2 passing text);
  `add_validation_rule` guards the silent `ValidationRule`-object double-wrap with
  a `TypeError`. **Phase 2:** type-aware rule taxonomy — text-rules
  (`stringLength`/`pattern`/`email`) vs value-rules; new **`range`** rule
  (number/date/time bounds with a message, vs silent `min_value`/`max_value`
  clamping); an inapplicable rule is **rejected at attach time** with
  `BootstackError`, keyed off a per-wrapper `_VALIDATION_KIND` class attr
  (`number`/`date`/`time`; `text` default); redundant date/time
  `add_validation_rule` overrides removed (they bypassed the guard). **Phase 3:**
  reactive validity surface — the engine owns `_valid_signal`/`_error_signal`
  (source of truth, set via `_set_validity` on every run); public **`field.valid`**
  / **`field.error`** Signals (`bs.Label(textsignal=field.error)`); the Field
  message label is now bound to the error signal (imperative `_show_error`/
  `_clear_error` gone); `Form.validate()` routed through the entry's validator.
  **Phase 4:** `docs/reference/validation.rst` rewritten (typed-value model,
  `range`, type-aware behavior, reactive signals); api-ref `RuleType` += `range`.
  Brief `docs/_dev/field-validation-system.md`; memory
  `project_field_validation_redesign`. Tests `test_field_validation_typed.py`
  (27). **Follow-ups BOTH DONE this session** (see the field-family entry above):
  **#216** (PR #219) NumberField empty-construction crash · **#217 part 1** (PR #220)
  reactive `Form.valid`/`Form.errors` (part 2 stream-triggers deferred). NB the
  **string-only `add_validation_rule`** decision is locked (a `ValidationRule` object
  carries no info the string form lacks).
- **Slider/RangeSlider review** (PR **#212**, MERGED) — value clamps to range, disabled
  honored on every key (incl. Home/End), Home/End emit `<<Commit>>`, tightening the range
  re-clamps the value(s); widget pages gained Events + Keyboard sections + value/min-max
  screenshots. (The `fix/slider-review` branch is merged — stale.) `step=` follow-up
  (#213/#210) and the Tab focus-trap (#211) are under "Next up".
- **Shell chrome divider + context-menu / DataTable interaction fixes** (this
  session; PRs **#206** and **#209**, both MERGED to `main`) — two batches from
  dogfooding the AppShell + DataTable demos:
  - **#206 — persistent chrome→content border + softer inter-toolbar divider**
    (`fix/shell-content-border`). The chrome→workspace boundary is now owned by
    **`ShellLayout`** (a content-surfaced `_body_sep` at the soft
    `DIVIDER_BORDER_STRENGTH=0.90`, always packed between the chrome stack and the
    body, mirroring the bottom `_status_sep`) — authors no longer rely on
    `add_toolbar(divider=True)` for it, and the stroke matches the rail/sidebar/
    status dividers instead of reading heavy (the original complaint). The
    per-toolbar `add_toolbar(divider=True)` hairline was **softened to 0.90 + kept
    chrome-surfaced** (was the default heavy blend) so an inter-bar divider matches;
    it's now reserved for separating stacked bars. `appshell.rst` notes the
    auto-boundary. Plain `App`/`Window` keep `divider=` as their chrome separator
    (no shell layout, no auto border).
  - **#209 — context-menu dismissal + DataTable right-click/selection + FormDialog
    action result** (`fix/contextmenu-outside-dismiss`). (a) **ContextMenu**: the
    overrideredirect popup's outside-dismiss now watches **all mouse buttons**
    (was `<Button-1>` only — a right-click to open another menu slipped past it);
    a one-shot **`_suppress_next_outside`** guard set in `show()` kills the
    reopen-race that widening introduced (right-click another row reopens, doesn't
    self-dismiss); and **`hide()` now runs BEFORE an item's handler** (a modal
    handler was blocking with the menu still visible). (b) **DataTable**:
    right-click **no longer changes the selection** (it set `_context_iid`; the
    row-menu commands target it via new **`_context_iids()`** = clicked row, or the
    whole selection when the click is inside a multi-selection); a left-click on a
    checkbox/group table now **dismisses an open menu through the `'break'`** path
    (`_dismiss_context_menus()` at the top of `_on_header_click`, since the tree's
    `'break'` stopped the toplevel outside handler); and **selection survives a
    `_refresh_tree` rebuild** for still-visible rows (sort keeps all, search narrows
    — was a full clear on every search/sort/page). (c) **FormDialog**: `show()` was
    overwriting `result` with form data for any non-cancel close, discarding a
    custom button's `result` — so the edit dialog's **Delete** (`{"result":
    "delete"}`) returned data instead of `"delete"` and the row was updated, never
    deleted; new **`_resolve_result()`** maps submit buttons→form data, action
    buttons→their result, cancel→None. (d) **Docs**: fixed stale `event["text"]`
    dict-subscript in ContextMenu/MenuButton examples+guides (`on_select` gets a
    `MenuSelectEvent` dataclass → `event.text`). **Follow-up issues filed:**
    **#207** (general grab-based dismiss so user-attached menus also dismiss when a
    host widget returns `'break'`) · **#208** (persist DataTable selection by record
    id across pages — the "keep visible matches" interim shipped here).
- **Navigation API reshape — `AppShell` + `Workbench` (#200)** (this session; PR
  **#202**, MERGED to `main`) — split the one polymorphic `AppShell` into two
  honest classes along the **topology** axis: **`bs.AppShell`** = single-tier
  *sidebar host*; new **`bs.Workbench`** = two-tier *workspace host*
  (`add_workspace` + rail). Shared **`_SidebarHost`** mixin (on `AppShell` +
  `Workspace`); a private **`_ShellBase`** carries window/chrome/lifecycle. The
  **provider** axis is four parallel front doors — **`page_nav()`** (authored
  pages), **`list_nav()`** / **`tree_nav()`** (data-bound master-detail),
  **`custom_nav()`** (renamed from `panel()`); one per sidebar, only `page_nav`
  authored (`add_page`/`add_header`/`add_divider`). Provider options live on the
  provider: **`page_nav(variant='ghost'|'solid')`** (standalone-only; forced to the
  wash under a rail) and the full `PageStack.add` **layout kwargs on `add_page`**
  (a page IS a column — no inner wrapper). Footer = **`pin_to_footer=`** flag
  (dropped `add_footer_page`/`add_footer_workspace`). Shell kwargs keep only app-wide
  chrome (`nav_accent`, surfaces, `rail_*`). **Framework fix surfaced in review:
  `ContentHost` now FILLS its child** — master-detail/custom content was shrinking
  and centering (the apparent "extra padding"); detail panes left-aligned at
  `padding=(16, 10)`. Internal `Shell`/`Workspace` keep `add_page`/`add_workspace`/
  `panel`/`nav_selection` (public layer is the rename boundary). Built `Workbench`
  doc page + screenshot scenes; AppShell page gained a "Sidebars at a glance" card
  grid + ghost/solid + compact shots; Workbench compact is **not** a mode (rail is
  the icon tier → sidebar is expanded/hidden, documented). **#189 nav_variant
  (PR #199, MERGED) was folded in** — `nav_variant` ctor kwarg → `page_nav(variant=)`;
  its `test_nav_selection.py` removed (superseded by `test_appshell_reshape.py`).
  Tests: `test_appshell_reshape.py` (6) + `test_workbench.py` (2). Memory
  `project_navigation_api_reshape`. **Follow-up: #201 — SHIPPED (sidebar
  hamburger, see top of this list).**
- **Sidebar hamburger toggle — `Toolbar.add_sidebar_toggle()` (#201)** (this
  session; on `feat/nav-expandable-group`) — #201 was filed as an *expandable
  sub-item nav group*, but the maintainer **reinterpreted it** as a built-in
  **hamburger that collapses/expands the AppShell sidebar** (the accordion-style
  sub-items stay parked per the nav-spec Revision-4 cut — compose `bs.Accordion`
  in a `custom_nav`). The collapse machinery already existed (`toggle_sidebar()`/
  `show_sidebar()`/`hide_sidebar()`/`sidebar_mode`, Ctrl-B); what was missing was
  a control. Modeled on `ThemeToggle`/`add_theme_toggle()` but **NOT standalone**
  (a sidebar toggle is meaningless outside one shell): an internal
  `SidebarToggle(Button)` (`widgets/sidebar_toggle.py`, **not** in `bs.*`) built by
  **`Toolbar.add_sidebar_toggle(**kwargs)`**, which wires it to the owning shell.
  **AppShell-only** — the guard is `isinstance(host, AppShell)` (a `_SidebarHost`;
  `Workbench` inherits `toggle_sidebar` from `_ShellBase` so a `hasattr` check is
  too loose), raising `BootstackError` on `Workbench`/`App`/`Window`. Enabler:
  `add_toolbar()` (ChromeHostMixin) now passes `_host=self` into the `Toolbar`;
  `Toolbar.__init__` stores `self._host`. **Author places it wherever they want in
  the bar — no auto-injection.** `collapse='compact'` is the **default** (the
  desktop/Fluent convention: shrink to the icon rail, reusing the shell's
  `_can_compact_active()` so it **falls back to hidden** for non-compactable
  data-bound navs); `collapse='hidden'` always fully hides. **Mode-dependent
  default icon** (`icon=None` resolves to `layout-sidebar` for compact, `list` for
  hidden); single steady glyph unless the author passes a stateful pair
  (`collapse_icon` shown while expanded, `expand_icon` while collapsed, each
  falling back to `icon`). A ~6px toggle-vs-rail offset in compact is **left as-is
  by decision** (only visible compacted; aligning would couple toolbar padding to
  rail width). Tests `tests/widgets/public/test_sidebar_toggle.py` (8). Docs:
  "Sidebar toggle" section in `docs/widgets/toolbar.rst` (full detail) + the
  AppShell page's "Sidebar visibility" section (the user-facing control,
  cross-linked). StatusBar deliberately **not** given the method (scope creep — a
  hamburger belongs in a toolbar).
- **Gallery/Carousel height-floor cleanup (#160)** (PR **#185**, MERGED) — added the
  regression test + hardened two magic numbers into named constants; the floor itself
  shipped in #161. Memory `project_picture_suite`.
- **Tab overflow handling (#168)** (PR **#184**, MERGED) — clipped tabs scroll (wheel +
  selected-tab auto-scroll) with a trailing chevron overflow menu; `max_tabs=`; always-on
  (plain strip kept only for `tab_width='stretch'`). Three framework fixes: PackFrame
  no-repack when `gap==0`, PageStack pre-size-on-swap, deferred `_scroll_into_view`.
- **ContextMenu/Tooltip cover container children (#166)** (PR **#183**, MERGED) —
  `propagate_target_bindings()` adds the container's path bindtag to every descendant so
  the gesture fires anywhere inside. Memory `reference_bindtags_underused`.
- **Theme-repaint cleanup (#177) + docstring-backtick sweep** (PRs **#181**/**#182**,
  MERGED) — code-editor `StyleRegistry`/`SearchOverlay`/`IndentGuides` migrated onto
  `<<BsThemeChanged>>`; dead `FloodGauge` deleted; 754 RST double→single backticks across
  43 `src/` files. Memory `project_docstring_backticks`.
- **Undecorated window chrome (#162/#165) + theme-repaint perf (#167)** (PRs #175/#176/
  #178/#179/#180, MERGED) — undecorated App/Window/AppShell auto-inject titlebar+border;
  canvas widgets re-resolve colors via the STD publisher (post-rebuild), gated on
  visibility (gallery toggle ~2960ms→~580ms). Memories `project_undecorated_window_chrome`,
  `reference_theme_repaint_mechanisms`.
- **Pre-release `0.1.0a10` shipped + docs deploy fixed** (PRs #139/#140, MERGED) — Toast
  split into `toast()`/`Notification`/`Snackbar`; gallery/demo widget coverage; released to
  PyPI + GitHub Release; docs-deploy fixed (restored `docs/CNAME` + `html_extra_path`).
  Memories `project_prerelease_readiness`, `project_toast_notification_split`.
- **0.1.0 API-freeze pass — breaking changes drained + ThemeToggle + media floor** (PRs
  #141–#161, MERGED) — workflow action bump (#141), ttkbootstrap naming purge (#142),
  clipboard scope (#151), nav missing-key errors (#153), `Theme.from_existing` (#156),
  `Signal.subscribe` cancelable handle (#157), VariantToken retirement (#158), `ThemeToggle`
  (#159), media min-height floor (#161). Memories `project_clipboard_api_scope`,
  `project_variant_type_revisit`, `project_picture_suite`.
- **AppShell + navigation clean-slate rewrite** (PRs #133–#136, MERGED; later split into
  AppShell + Workbench by #200/#202 — see top) — VS Code-style rail + swappable sidebar +
  content; `bs.AppShell` swapped onto the new `Shell`, standalone `bs.SideNav` dropped.
  Companions: theme/Bootstrap-alignment v2 (#137), thin-scrollbar exposure (#138),
  nav-patterns docs (#136). Spec `docs/_dev/appshell-navigation-spec.md` (Revision 4).
  Memories `project_appshell_sidenav_refactor`, `project_theme_bootstrap_alignment`,
  `project_thin_scrollbar_initiative`, `project_nav_patterns_section`.
- **Media widget suite — Picture / Gallery / Carousel / Avatar** (PRs #126–#132, MERGED) —
  media-display widgets on the public `Image` handle: Picture (fit modes, animated GIF),
  Gallery (record-native thumbnail grid), Carousel (one-at-a-time stepper), Avatar
  (image-or-initials). Plus `on_select` rename (#130) + theme-aware demo videos (#131).
  Memories `project_picture_suite`, `project_avatar_widget`, `project_doc_demo_videos`.
- **Public Image/Icon API + AppIcon + field signals** (PR #125, MERGED) — `bootstack.images`
  (`Image` handle, `get_icon`/`list_icons`, `AppIcon` → `.ico`/`.icns`/`.png`); `App`/`Window`
  `icon=`; live `icon`/`image` setters; typed `signal=` on Number/Date/Time fields;
  `bootstack.toml` scoped to build/scaffold; public file-dialog verbs; ships `bootstack appicon`.
  Memories `project_image_icon_public_api`, `project_field_value_signal_dtype`.
- **Menu bar + command bar** (PR #124, MERGED) — cross-platform `app.menubar` (themed strip on
  Win/Linux, native `NSMenu` on macOS); `Toolbar`→`CommandBar`; legacy `bs.MenuBar` removed;
  `app.menu`→`app.menubar`, `app.toolbar`→`app.commandbar`. Memory `project_menu_redesign`;
  follow-up `project_macos_window_chrome`.
- **Widget detach/attach** (PR #123, MERGED) — `detach()`/`attach()`/`is_attached` across
  pack/grid/place; `on_attach`/`on_detach`; `attached=False` ctor; new `index=` pack knob.
  Memory `project_widget_attach_detach`; backlog `project_inherited_base_api_docs`.
- **Select grouping + popup height cap** (PR #122, MERGED) — `Select(group_by="field")` clusters
  the popup under verbatim headers (names any bag field, presentational only); `max_visible_items=N`.
  Memory `project_select_options_databag`.
- **Universal `.selection` on ListView/DataTable/Tree** (PR #120, MERGED) — polymorphic by
  `selection_mode` (dict/list, TreeNode handles); replaced `get_selected()`/`selected_rows`/
  `selected_nodes` (clean break); `ListView.select_items`/`deselect_items`. Memory `project_option_databag`.
- **Field value/text/label contract + option data bag** (PRs #113–#116, MERGED) — `label`=caption,
  `text`=formatted display (public read-only), `value`=raw datum (never derived from text); shared
  `Option = str | tuple | OptionDict` + `normalize_option` with a data bag; `.selection` accessor.
  Memories `project_field_value_text_model`, `project_option_databag`.
- **Widget API gap audit + documentation** (PR #111, MERGED) — audited ~49 widgets vs their
  `_impl/` internals; added lifecycle (`destroy`/`on_destroy`), `WindowControlsMixin` on
  App/AppShell/Window (AppShell is now a `PublicWidgetBase`), group management, live properties;
  new **Application** widget category with full-window screenshots. Brief `docs/_dev/widget-api-audit.md`.
- **Linked type aliases + widget-API consistency** (MERGED) — public aliases render as their
  short NAME, linked to a `.. py:type::` entry (dropped `sphinx_autodoc_typehints`;
  `autodoc_type_aliases` FQN map; `python_use_unqualified_type_names`; a `TypeAliasForwardRef`
  patch). Memories `project_enum_option_typing`, `reference_typed_alias_linking`.
- **Unified data bag** (PR #92) — non-scalar fields carried across Tree/DataTable/ListView
  (SQLite `_bs_data` JSON column; `bs.SerializationError` on non-JSON). Memory `project_data_bag`.
- **Large-file streaming** (PRs #93–#96) — chunked `load()`; pluggable reader/writer registries;
  `FileDataSource` → SQLite working store; `export_formats`. Memory `project_file_source_streaming`.
- **Tree public-API modernization** (PR #91) — recycle-view canvas Tree, `TreeNode` handles.
  Memories `project_tree_row_model`, `reference_treeview_perrow_indicator_state`.
- **Icon rendering + DataTable polish** — ink-metric icon renderer; `Table`→`DataTable` +
  DataSource decoupling. Memories `project_icon_rendering`, `project_table_datasource_coupling`.
- **Tree data-source backing** (PR #97) — `Tree(data_source=, parent_field=)` lazy hierarchy
  from a flat adjacency-list source. Memory `project_tree_datasource_backing`.
- **SqliteDataSource schema inference** (PR #98) — `load()` samples leading rows to infer column
  types (fixes the TEXT-affinity-from-leading-NULL bug).
- **Signal runtime cleanup** — `signal()` single getter; `is_signal()` duck-types. Memory
  `reference_signal_duck_typing`.
- **Preferences store `bs.Store`** — dict-like JSON file-backed prefs; shared `_core/paths.py`.
  Memory `project_persistent_kv_store`.
- **AppSettings flattening** (PR #101) — flat `App()`/`AppShell()` kwargs; `settings=`/`AppSettings`
  gone. See the "FLAT kwargs" gotcha. Memory `project_app_settings_flattening`.
- **Reference docs review pass** (PR #103) — enriched `docs/reference/*` + `localization.rst`;
  `compare` rule; `Form.validate()` runs all rules.
- **Top-level namespace curation + dialogs restructure** (PR #104) — `bootstack` slimmed to the
  compose surface (~85 names); dialog classes → `bootstack.dialogs`. Memory `project_toplevel_api_surface`.
- **Docs build warnings cleanup** (PR #106) — clean-build 40→0; keep it warning-free.
- **API Reference restructure — Stages 1–3** (PR #107) — Diátaxis split: narrative (Widgets +
  Guides) + by-module API Reference; templates/recipe in "## API Reference & Guide page pattern".
  Memory `project_api_reference_restructure`. (Stage 4 homing DONE — see "History".)

## Closed backlogs

The pre-ship and per-initiative backlogs, kept for the decisions recorded in
them. Anything still open was carried forward into `CLAUDE.md`.

### ★ NEXT — Pre-ship polish backlog (#186–#195, filed 2026-06-18)

Ten maintainer-requested items to resolve before shipping 0.1.0 — all filed as
tracked issues (each issue links the relevant impl file + has detail).
**Nine of ten SHIPPED:** #186/#190/#193/#194 (PR **#196**), #195 (PR **#197**),
#188 (PR **#198**), **#189 (PR #199 → folded into the nav reshape PR #202)**, **#187
(PR #203)**, **#191 (PR #204 — themed color tab + `ask_color(value=)` rename)** — all
merged to `main`. **One remains** (its own `feat/*` branch → PR → `main`):

- **#189 `solid` sidebar selection variant — DONE.** Shipped as **`nav_variant`**
  on `AppShell` (PR #199, gated to the standalone nav), then **superseded by the
  navigation reshape (#200, PR #202)**: the variant now lives on
  **`page_nav(variant='ghost'|'solid')`**, standalone-only. See the reshape pointer
  at the top of "Recently completed".
- **#187 StatusBar.add_widget class-only? — DONE (PR #203, MERGED).** Decision:
  **class-only** on BOTH `Toolbar` AND `StatusBar` (`add_widget(WidgetClass, **kwargs)`).
  The two were ALREADY polymorphic in lockstep (not StatusBar-only), so class-only on
  both keeps them consistent while dropping the redundant instance branch (couldn't
  inherit bar density/surface; required a manual attach). No flexibility lost — a
  self-built widget drops in via the container protocol (`parent=bar`, auto-attaches).
  `StatusBar` gained the `_apply_bar_defaults` helper it lacked. **NB the public param
  is annotated `widget_cls: Any` not `: type`** — the bare builtin `type` renders an
  ambiguous `ref.python` cross-ref under `python_use_unqualified_type_names` (collides
  with the many `.type` attrs); the precise `: type` stays only on the private
  `_apply_bar_defaults` (not rendered). Also fixed a stale `StatusBar(fill="x",
  side="bottom")` docstring (would raise under the grid engine) → `horizontal="stretch"`,
  and enriched `docs/tasks/composing-fields.rst` with a **"Subclassing for a reusable
  type"** section (`SearchField(bs.TextField)` via `insert_addon`, justified by exactly
  this change — a container can only build your field if it's a class). Test
  `tests/widgets/public/test_statusbar.py` (3).
- **#192 Color-swatch Select control (feature, larger)** — a `Select`-style
  dropdown rendering color swatches inline (complements `ask_color()`). New widget
  or Select variant — lock shape/naming with the maintainer first.

**SHIPPED detail (this session):** #195 (PR #197) — placeholder renders unmasked
under an input mask; `TextEntryPart` captures the mask char, clears `show` while
the placeholder shows, restores it for real input; PasswordEntry eye-toggle no-ops
while placeholder showing. Test `test_field_placeholder_mask.py`. NB `TextField`'s
public mask kwarg is **`mask=`** (not `show=`). #188 (PR #198) — accented Card
border now **`b.border(surface)`** (a soft stroke derived from the card's own
`{accent}[subtle]` tinted surface), NOT `{accent}_emphasis` (the issue's original
suggestion — rejected as too strong on review). Test `test_card_border.py`.

### Field-family review follow-ups

The field family is fully reviewed (see the top "Recently completed" entries).
**#227 (DONE, PR #238 — object-mode Signal) and #232 (DONE — PathField live dialog
props) are merged; #237/#217 closed.** Two additive follow-ups remain OPEN — neither
is a correctness bug:

- **#222 — TextField live properties** (OPEN, ready to build). Expose `placeholder`
  / `mask` (high value — runtime UX toggles) and `allow_blank` / `value_format`
  (lower — the configure-delegate already works imperatively) as live get/set
  properties. The underlying `TextEntryPart` already supports them
  (`_placeholder_text`/`_show_char`/`_delegate_allow_blank`/`_delegate_value_format`).
  Explicitly **NOT** a `.text` setter (read-only by the value/text contract — write
  through `.value`). Clean, low-risk, no decision needed.
- **#234 — SpinnerField↔NumberField parity** (OPEN, decision-gated) — live
  `min_value`/`max_value`/`step` props, `increment()`/`decrement()` methods,
  `on_increment`/`on_decrement` events. **May be won't-do** (SpinnerField is
  intentionally simpler) — get the maintainer's call before any code.

### Slider follow-ups — DONE

Slider `step=` snapping (#210, PR #213) and the RangeSlider `<Tab>` focus-trap
(#211, PR #215) both MERGED. Nothing open here.

### ✅ SHIPPED — Layout redesign (screen-axis grid engine) — MERGED #170

Replaced the Tk pack stack with a **screen-axis** vocabulary on the Tk grid manager:
`horizontal`/`vertical`/`grow` (bare = self, `*_items` = children); edge-name values
(`left`/`center`/`right`/`stretch`) + `space-between`/`-around`/`-evenly`; `HStack`/`VStack`
→ `Row`/`Column`, `Separator`→`Divider`, new `Spacer`; **cross-axis default `center`**;
legacy `fill`/`expand`/`anchor`/`sticky` now RAISE. Post-merge: #171 (GridFrame O(N) build),
#169 (deploy docs on release only), #172 (README/docs-home refresh), #173 (CLI icons on the
public layer + Gallery/MemoryDataSource fixes). Memories `project_layout_redesign`,
`feedback_layout_conversion_rules`, `project_layout_crossaxis_default`, `project_divider_rename`,
`project_dialog_content_builder_native`.

**Live follow-ups (not blockers):**
- **Gallery opt-in keyboard-focus ring** (future) + deferred Gallery perf (debounce
  `<Configure>`, bounded thumbnail-PhotoImage LRU, cache `_fit_caption`). Scope to keyboard
  focus, NOT hover. Memory `project_gallery_focus_ring`.
- **`add_spacer()`→public `Spacer`** still deferred — entangled with `feat/unified-toolbars`
  (internal `Toolbar` is pack-based). Memory `project_unified_toolbars`.

### ✅ SHIPPED — Undecorated window controls + border + maximized-drag — MERGED #175

Undecorated `App`/`Window`/`AppShell` auto-inject a draggable titlebar (min/max/close) +
1px border via `ChromeHostMixin._ensure_default_titlebar()` (layers on `add_toolbar()`, not
a dedicated band); `App` gained `undecorated=`, `Window` gained `window_controls=`; #165
maximized-drag re-anchors under the cursor. Memory `project_undecorated_window_chrome`.

### Toward the 0.1.0 stable release

- **#149** — final public-surface audit + **CHANGELOG** for the stable cut.
- **#150** — test-harness stabilization (the GUI suites need one `App` per process;
  the `.pytest_cache` perms warning on this machine is benign).
- **#155** — Topic-guide technical-writer review pass (the `/reference/*` pages get
  the same no-kitchen-sink edit the how-to guides already had; memory
  `project_user_guide_fleshout`). The maintainer is comfortable with the how-tos.

### Other candidates

- **Docs site fleshout — substantially DONE.** The how-to guides (`docs/tasks/*` —
  getting-input/handling-actions/displaying-data/building-forms/composing-fields/
  dialogs/layout/application-icons + the full `navigation/` set), `getting-started/
  app-structures`, and the production pages (`cli`/`debugging`/`distribution`) are all
  written and substantial. Remaining is only opportunistic: a review pass on
  `installation`/`quickstart` and enrichment of any still-thin page. Memory
  `project_docs_site_fleshout`.
- ~~**Docstring-backtick sweep**~~ — **DONE (PR #182):** 754 RST
  double-backticks → single across 43 `src/` files. Convention is Google + SINGLE
  backticks. Memory `project_docstring_backticks`.
- **Code-review follow-ups #4–#10** — cleanup/altitude items recorded in
  `docs/_dev/widget-api-audit.md` (SelectButton stale value after `options=`; screenshot
  Win64 HWND hardening; group/window/date duplication; Calendar batch-redraw).

**Throwaway demos `development/shell_*_demo.py` stay UNTRACKED** (scratch, not
framework code). Side note logged: a future `Tabs` `variant='secondary'` (top
indicator) — `project_secondary_tab_variant`, a standalone item.

### History — done initiatives

- **Public-API typing sweep — DONE** (branch `feat/api-reference-widgets`, merged via
  PR #109). All widget batches typed (Application → Overlays/Forms/Dialogs): real param
  types, per-widget `variant` Literals sourced from `style/builders/`, typed `on_*`
  payloads (impl signature, not `@overload`), thin docstrings, every public prop/method
  documented. Conventions live in the "API Reference & Guide page pattern" section +
  `docs/_dev/typing-review.md`. Memories `project_enum_option_typing`,
  `project_typed_event_payloads`, `project_variant_type_revisit`. Also shipped here:
  `Tree.find`/`find_all` (predicate or `col(...)` condition; memory `project_tree_find_filter`).
- **API Reference restructure — Stage 4 homing — DONE (PR #109).** The IA was re-cut to a
  semantic-category structure: one page per CONCEPT (Application · Widgets · Reactivity ·
  Events · Data · Validation · Theming · Localization · Scheduling · Shortcuts · Storage ·
  Errors), full-path stub titles, pandas-style card landing; every public name homed,
  guides converted to table-only API sections. Brief `docs/_dev/api-reference-restructure.md`;
  memory `project_api_reference_restructure`. **NEXT (follow-on): flesh out widget Guides
  with examples — the API Reference is a last resort; Guides carry teaching.**
- **Deferred file-streaming items** — background/progressive ingest, keyset pagination,
  auto-index (memory `project_file_source_streaming`).


---

## 0.2.2 through 0.4.0-in-flight — split out of `CLAUDE.md` 2026-08-20

⚠ **This is the SECOND split.** The first (2026-07-30) moved everything up to
`0.2.1` down here; then `0.2.2`, `0.2.3`, `0.3.0`, `0.3.1`, `0.3.2` and the CI
work accreted back into `CLAUDE.md` until it reached **~60,000 tokens** and blew
the context budget. Everything below is **verbatim** as it stood in `CLAUDE.md`
on 2026-08-20 — shipped history, its measurements, and its traps.

**The standing rules and the still-open work were NOT moved** — they stayed in
`CLAUDE.md`, condensed. If a lesson here is one that should bind future work,
it is already restated there; this copy is the detail behind it.

⚠ **The lesson of needing a second split: an entry belongs here THE DAY ITS
RELEASE SHIPS.** `CLAUDE.md` is for what is open. Both splits happened only once
the file had become painful to load.

### Shipped release history — `0.3.0` (capture + dialog results) and its branches

#### The `Current state` section as it stood on 2026-08-20 — HISTORY, not current

⚠ **Every "current", "in flight" and "next" below is frozen at the split.**
Read it for the measurements and the traps, never for the state of the world;
`CLAUDE.md` is the only place that is live. **The milestone numbers here are
pre-2026-08-19 and are STALE by one** — see the renumbering note in `CLAUDE.md`.

**Released:** **`0.3.2` on PyPI, tag `v0.3.2` (2026-08-13)** — titled *Read-only
select fields*, one fix (#453) on the patch line, `release.yml` clean and docs
chained off it. **See START HERE for its verification and the tag-vs-`main`
divergence.** Then `0.3.1` (2026-08-12, *Dialog keyboard and modality*, four
fixes).

⚠ **THE PARAGRAPH BELOW IS `0.3.0`'s AND IS KEPT FOR ITS DETAIL, NOT AS THE
CURRENT RELEASE.** Two releases have shipped since. Same for most of this
section — **`Recently shipped` and START HERE are the current ones; this block is
history with the warnings still attached.**

**`0.3.0` on PyPI, tag `v0.3.0` (2026-08-11)** — titled *Screen
capture and dialog results*, **shipped by `release.yml`, which ran clean end to
end**, with `docs.yml` chaining off it automatically. Two features and six fixes:
`widget.capture()` (#427, #429) and the dialog-result work (#428, #437, #438).
Previous: `0.2.3` (2026-08-08, also clean) and `0.2.2` (2026-08-06, published
**manually** during an Actions outage — that recipe is kept under Release flow
because it will be needed again).

Every post-release step is done and was **verified rather than assumed**: PyPI
proved with a real `pip download` (not the CDN-cached summary endpoint), the
shipped wheel opened and checked, the GitHub Release live with both assets, docs
returning 200, and #428's reporter told it is live via `gh issue comment`.

⚠ **One check worth repeating on every release from now on: `import bootstack`
with `idlelib` BLOCKED.** That is #430's defect, and grep is not enough to
re-prove it — seven `idlelib` mentions survive in the wheel and all are docstring
attributions. Block the module with a `meta_path` finder, assert the block works
as a control, then import. It passed for `0.3.0`.

**⏭ NEXT RELEASE: `0.3.1 — Dialog keyboard and modality`** — #426, #439, #440,
#441, **and #446**, which was moved onto the milestone on 2026-08-12 because it
gates the release (see the milestone table's note). Scoped 2026-08-11
(maintainer). **MERGED to `main` on 2026-08-12 as PR #448 (merge commit
`d307fd2e`) after FOUR review rounds. NOT RELEASED YET** — `## [Unreleased]`
carries all four fixes and the next job is to promote and tag it. See START HERE.

**`main` is GREEN.** ⚠ **STOP RE-RECORDING THESE NUMBERS FROM MEMORY. This file
has now been wrong about them SEVEN times, in both directions.**

**AUTHORITATIVE — derived 2026-08-13 from a measurement on
`fix/select-read-only-453` at `872aa862`**, full `py -3.12 tests/run_gui.py`,
**exit 0, all 20 legs**, `pandas` ABSENT:

| | branch, measured | `main`, derived |
|---|---|---|
| summed, 20 legs | **1225 passed / 21 skipped** | **1208 passed / 21 skipped** |
| shared leg | **1028 / 14** against **1041** selected | **1011 / 14** against **1024** selected |
| data leg | **125 / 4** | same |

**The derivation is exact and is the whole point** — the branch adds ONE test
file of 17 tests and `git diff --stat 288d2596..HEAD -- tests/` proves nothing
else under `tests/` changed since the #407 merge, every other commit being
`docs(*)`. So subtract 17. The shared leg reconciles against its own collection
line the documented way: `collected 1116 / 75 deselected / 1 skipped / 1041
selected`, and `1028 passed + 13 runtime skips = 1041`, the 14th skip being the
collection-time one that is summarized but never selected.

⚠ **THE `1250 / 22` AND `1055 / 13` AGAINST `1068` THIS FILE CARRIED FOR `main`
WERE WRONG — that is the seventh time, and it was a DOUBLE error, since the file
also disputed the right number and picked the wrong one.** It flagged round 3's
`1011 / 14` against a `1024` ceiling as irreconcilable and kept `1068`. `1011 /
14 / 1024` is exactly what today's measurement derives, and `1208 / 21` is
exactly what this file already records for the `0.3.1` branch. Both surviving
figures were the correct ones all along. **A count that reconciles against its
own collection line is still only self-consistent — it does not prove the run
selected everything it should have.** The check that caught this is cheaper than
the one that missed it: `git diff --stat <baseline>..HEAD -- tests/`, which
bounds how much the count is ALLOWED to have moved.

Data leg **125 / 4** here because `pandas` is absent (`py -3.12 -c "import
pandas"` → `ModuleNotFoundError`); it reads **123 / 6** when `pandas` is
installed, two tests running only when it is missing. Check the optional dep
before re-flagging that pair.

⚠ **THE COUNTS DID NOT MOVE ACROSS #407; THE CLOCK DID.** Same totals before and
after, which is the point — a harness fix that changed a count would have been
skipping something into passing. What changed, measured on this box with the
same command either side:

| | before #407 | after |
|---|---|---|
| shared leg (`tests/widgets/public tests/cli -m "not isolated"`) | **215s** | **56s** |
| full `run_gui.py` | ~5 min | **66–88s** |

That is a larger win than the **144s → 80s** this file recorded when the root
cause was first diagnosed — so prefer these, and re-measure rather than trusting
either.

**Previous, kept for the reasoning that refers to it — measured 2026-08-11 on
`main` at `ab11f37c`** (the #443 merge — everything in `0.3.0`), full
`py -3.12 tests/run_gui.py`, **exit 0, all 20 legs passed**:

| leg | result |
|---|---|
| widgets+CLI, shared root | **962 passed / 14 skipped** (75 deselected — capture raised it from 52) |
| data | **125 passed / 4 skipped** |
| `test_capture.py` (isolated) | **23 passed** |
| every leg summed (20 legs) | **1159 passed / 21 skipped** |

The pre-capture figure at `06acd727` was **1136 / 21 over 19 legs**, same shared
leg (962 / 14, 52 deselected) — capture adds 23 isolated tests and nothing to the
shared one.

⚠ **The `1006 / 13` recorded here for `e0092336` was IMPOSSIBLE, and so were
`1001 / 13` and `1005 / 13` in `REVIEW.md`'s rounds 3 and 4.** The shared leg
**selects 975 tests**, so no result summing to 1018 or 1019 can come out of it —
`SHARED_GROUPS[0]` is one pytest process over `tests/widgets/public tests/cli`
with `-m "not isolated"`, printing one summary line. **The ceiling is the
selected count, and checking a reported total against it takes one command:**
`pytest <paths> -m "not isolated" --collect-only -q | tail -2`. That single check
would have caught three of the five wrong figures this file has carried.

⚠ **THE `123 / 6` DATA-LEG FLAG IS ENVIRONMENTAL AFTER ALL — this file's
"RESOLVED: it was wrong, not environmental" was itself wrong** (measured
2026-08-12). Both figures are real and the difference tracks **whether `pandas`
is installed on the box**: two tests in `test_readers.py` / `test_writers.py`
SKIP with *"pandas installed - gating path not exercised"*, i.e. they run only
when it is ABSENT. `pandas` is installed here now and the leg reads **123 passed /
6 skipped**; on 2026-08-11 it was not, and the same leg read `125 / 4`.
`pyarrow` and `tables` are absent on both dates and account for the other four
skips. **So neither number is a defect, and a session seeing either should
check the optional deps rather than re-flagging it.** `py -3.12 -c "import
pandas"` settles it in one command.

Previous, kept because the reasoning below refers to it — measured 2026-08-10 on
`feat/widget-capture-427` at **`bdbdd097`**: widgets+CLI **932 / 14**, data
**125 / 4**, summed **1128 / 22**. That row is consistent with today's: `main`
gained the 30 tests #428/#437/#438 brought (932 → 962).

⚠ **A superset cannot collect fewer than its subset.** That is what exposed the
2026-08-08 pair (`976 / 13` and `1170`), and the selected-count ceiling above is
the same test applied within a single run. **Prefer a number you just measured
over one written here, and fix the table when they disagree.**

**The rule that keeps being broken: record the DATE and the COMMIT beside any
count, and re-measure rather than reasoning from a number already in this
file.** Sum the legs yourself — `run_gui.py` prints no aggregate. And if a count
here disagrees with one you just measured, prefer yours and fix this table.

**✅ BOTH IN-FLIGHT BRANCHES ARE MERGED AND DELETED (2026-08-06).**
`fix/datatable-double-click-417` went in as **PR #423** (merge commit `1ab5cda7`) and
`fix/datatable-click-focus-421` as **PR #424** (merge commit `734d515b`). Both were
**merge commits, not squashes**, deliberately — the one-commit-per-issue granularity
was the deliverable, same call made for #410. Both were verified as genuine ancestors
of `origin/main` with MERGED PRs, then **deleted local and remote after `0.2.2` hit
PyPI**. Head SHAs if either ever needs resurrecting: **`278d579a`** (417) and
**`fa735f99`** (421).

⚠ **A worktree was used for #421 and has been REMOVED**; the branch itself lives in
the repo normally. Do not go looking for a checkout under `scratchpad/`.
**#409 shipped 2026-08-05 via PR #414** (merge
commit `d428f6be`) — docs-only, unreleased, and it left **#412** open on purpose;
full entry in the archive, summary under START HERE. Both `0.2.1` PRs are merged:
**#410** (the #392-review cluster, merged as a **merge commit** so its six
one-per-issue commits landed individually — the granularity was the deliverable)
and **#411** (#405). Every `backup/*` ref and all twelve `: gone` locals were
deleted after the release.

**✅ `0.2.3` SHIPPED 2026-08-08 — #430. `fix/idlelib-import-430` merged as PR #435
(merge commit `3c785759`), then DELETED local + remote; head `57ee3041` if it ever
needs resurrecting.** `import bootstack` raised `ModuleNotFoundError` on any Python
build without `idlelib` (Debian and Ubuntu package IDLE separately, like
`python3-tk`), so the WHOLE framework was unimportable — not a degraded
`CodeEditor`. Fixed by **porting** `WidgetRedirector` into
`textarea/redirector.py` rather than importing it; `idlelib` is stdlib, so it is
not on PyPI and could never have been declared as a dependency. Full root cause and
the Linux repro are on the issue — do not re-derive. Three things worth carrying
here:

- ⚠ **`NOTICE` now carries a PSF attribution, scoped to `redirector.py` ALONE —
  that scope was MEASURED, do not widen it.** The first draft listed six
  IDLE-derived modules. Comparing each against its claimed `idlelib` source
  (docstrings and type hints stripped, normalized through `ast.unparse`) showed
  only `redirector.py` carries IDLE's *expression*: **29% verbatim, 5-line
  identical runs**. The other five — `filter`, `undo`, `sidebar`, `line_numbers`,
  `bracket_matcher` — share **0–7%**, and their longest runs are 1–2 line
  incidentals like `import tkinter as tk`. They implement IDLE's *designs*, which
  is an idea, not protected expression, so declaring them PSF-derived would tell a
  license scanner something untrue. PSF LA v2: **clause 2** is copyright
  retention, **clause 3** is the changes summary — both satisfied. ⚠ `NOTICE`
  reaches users as `dist-info/licenses/NOTICE` via **setuptools' automatic
  license-file globbing, NOT `MANIFEST.in`** (which names only `LICENSE`) —
  verified by opening the published wheel, not assumed.
- ⚠ **A probe must be RUNNABLE ON EVERY BOX IT IS MEANT TO INFORM.**
  `probe_430_idlelib_free_import.py` called `sys.exit(1)` the moment `idlelib`
  imported, so on Windows and macOS it printed arm 1 and stopped — even though arms
  2–4 (interception from Python AND through the Tcl command, the unregistered-op
  control, `close()`, a real `CodeEditor` through `FilterChain`) do not depend on
  `idlelib` at all. It was runnable only on the one box that **cannot finish the
  GUI suite (#432)**. Now SKIPs and continues. **The capture branch had already
  fixed the identical shape in `b005509b`** — this is a recurring failure mode, not
  a one-off.
- ⚠ **`gh issue close --comment` SILENTLY DROPS THE COMMENT if the issue is already
  closed** — and a PR body saying `Closes #430` closes it at merge. It warns about
  the close and says nothing about the comment. Post with `gh issue comment`
  separately, and **check the comment actually landed**. Also: **`bump-my-version`
  had VANISHED from 3.12** despite this file recording it installed 2026-08-05;
  reinstalled as **1.5.1**. Check for it before assuming the release flow works.

**⚠ EVERYTHING IN THIS SECTION ABOUT `feat/widget-capture-427` AND
`fix/formdialog-select-value-428` IS SHIPPED HISTORY — both are in `0.3.0`.** It
is kept for the measurements and traps, not as live state. **The one branch in
flight is `fix/dialog-keyboard-modality` (`0.3.1`) — see START HERE**, which is
the only block in this file describing work that is not merged.

**✅ `fix/formdialog-select-value-428` IS MERGED AND DELETED.** It went in as
**PR #442**, **merge commit `06acd727`** (a merge commit, not a squash — same
call as #410/#423/#424, the one-commit-per-issue granularity being the
deliverable). **#428, #437 and #438 are all CLOSED**, all milestoned
`0.3.0 — Screen capture and dialog results`. Branch head was **`38d01598`** if it
ever needs resurrecting; local and remote refs are gone (GitHub auto-deleted the
remote on merge, which is why `git merge-base --is-ancestor origin/<branch>` now
fails with *"Not a valid object name"* rather than reporting non-ancestry —
**check the recorded head SHA against `origin/main` instead**).

**1. `feat/widget-capture-427` — head `origin/…` is `1654c60e` (moved again on
2026-08-11, after this file recorded `a7d8941a`), 30+ commits.
⚠ ANY LOCAL CHECKOUT IS BEHIND: the maintainer pushed three commits on
2026-08-11 that REPLACED the #429 fix.** See the #429 block below — the approach
changed, and the block that used to live here was describing code that is gone.
⚠ **History was REWRITTEN by an earlier rebase** — a stale checkout needs
`git fetch && git reset --hard origin/feat/widget-capture-427`, not a pull. A
backup ref `backup/widget-capture-427-prerebase` points at the pre-rebase head
`05707330`; delete it once the branch merges.

Adds `widget.capture(path)` — save a widget, window, or app as a `.png`/`.jpg`/
`.pdf` — from discussion #425 (an external user) via **#427**. It ships in the
minor now titled **`0.3.0 — Screen capture and dialog results`**, which the
maintainer RENAMED and widened to also carry #428, #437 and #438 — so capture is
no longer the only thing gating that release.

**Capture is now the ONLY thing gating `0.3.0`** — the dialog half shipped to
`main` in PR #442.
**Read `development/review-brief-427-capture.md` ON THAT BRANCH** — it records the
settled decisions not to re-litigate and the measurements not to re-derive. ⚠ **But
read it as a POINT-IN-TIME record: its six self-flagged soft spots are all resolved
now** (see below), and it was deliberately not rewritten. Run
`development/verify_427_capture.py` on each box; it prints the platform and
backend and SKIPs arms the machine cannot exercise.

**✅ The macOS and Linux legs HAVE NOW BEEN RUN** (maintainer, 2026-08-08) — that is
what the 15 newer commits are: `e9d9f2f4` ask spectacle for a fullscreen grab,
`493a0980` + `ac9a87a3` the Linux docs, `31a4eb46` bounds-check on the library's own
crop path, `575b8400` refuse a scrolled-out widget and a destroyed root, `aae0396c`
run the capture tests in their own process, `67aefdbf` pin the region hand-off on
Windows and macOS, `d66b3440` let the topmost precondition wait for the window
manager. Those legs also produced **#429, #431, #432, #433, #434**.

##### ✅ #429 IS FIXED — but ⚠ **THE FIX WAS REPLACED ON 2026-08-11. The quiet
settle is GONE.**

⚠ **This block described the wrong code for a day. Read the commit messages on
the branch, not a summary, if anything here is load-bearing.** The first fix
(`e616f5dc`) stopped `settle()` dispatching at all. That was REVERSED by
**`e4fd4af7` — "block input while settling instead of not settling"**, plus
`9aada08d` (docs) and `a7d8941a` (probes re-pointed, manual demo added).

`settle()` ran `root.update()` every 10ms so the desktop could repaint, which
dispatched everything queued — so a second click on the export button re-entered
the caller's handler mid-capture and stacked a second save dialog on the END
USER. **It now still dispatches, and holds `tk busy` over the target instead.**

**⚠ THE OPEN QUESTION THIS FILE RECORDED WAS ANSWERED, AND THE ANSWER KILLED THE
FIX: the quiet settle does NOT repaint on macOS.** The area a window uncovers is
repainted by the desktop, and on macOS that does not happen at all unless the
event loop is turning — so the capture returned whatever was there before. The
Windows 0 px result was real but was a property of the DWM backing store, not of
the approach.

⚠ **`tk busy` is now ADOPTED, having been recorded here as REJECTED.** Do not
re-litigate it in either direction; the reason it lost (more machinery than not
calling `update()`) stopped mattering once not calling `update()` was ruled out.

- **Reproduced first, with a control.** Pre-fix the handler reached nesting depth
  2; the same call queued AFTER the capture stayed at depth 1. Measuring DEPTH
  rather than call count is what separates re-entrancy from "it ran twice".
  Post-fix every arm is depth 1 with `calls=2` — the second click is not
  swallowed, it is serialized.
- **Captures are pixel-identical.** A shot taken right after a window closed
  differs from a reference by **0 px**, against a 50 px floor between two shots
  of an unchanged window.
- ⚠ **The fix could NOT live in `capture()`.** The documented pattern calls
  `ask_save_file()` BEFORE `capture()`, so a re-entrant handler opens the second
  dialog before reaching any guard there. Raising or no-oping was considered and
  REJECTED — both hand the application author a problem AND make the end-user
  outcome worse than the bug (an unhandled exception on a double-click, or a file
  silently not written). Memory `feedback_framework_absorbs_not_developer`.
- ⚠ **`tk busy` is invisible to a capture (0 px) — but the first measurement of
  that was WRONG in the other direction** (it "gets photographed", 3906 px). The
  noise floor had been built from two static back-to-back shots, far too tight
  for a comparison that restacks a window; it was measuring text antialiasing.
  Floor measured across a restack now, and busy reads 0 px against it.
- ⚠ **A SYNTHESIZED CLICK CANNOT TEST THE GUARD, and the probes now say so
  instead of pretending otherwise.** `tk busy` intercepts by putting a window
  over the target, so it only catches what the window system routed by pointer
  position; `event_generate` aimed at a widget delivers straight to that
  widget's bindings and re-enters with `tk busy status` reading 1. The real
  question needs a human: **`development/demo_429_busy_during_settle.py`**,
  click Export then keep clicking and read the nesting depth.
- ⚠ **The guard is on INPUT, not on scheduled work.** A capture started from a
  timer still re-enters, by design. `probe_429_capture_reentrancy.py` records
  that as the known limit rather than a failure.
- ⚠ **Three probes silently became their own controls** when the sleep-only
  settle shipped, because every arm drove through `_capture.settle`. Worst case:
  `probe_429_settle_without_input.py` had a "control" arm and a sleep-only arm
  running IDENTICAL code and producing byte-identical images, while reporting
  three FAILs that were all one unrelated thing (a cover window never removed,
  photographed as pure magenta). Every strategy is pinned per-file now, arms that
  read live code are labelled, and an `expect` argument keeps a
  defect-reproducing arm from reporting failure forever.
- ⚠ **THE MEASUREMENT TRAP, worth more than the fix: compare captures only
  within ONE `bs.App` INSTANCE.** The FIRST app in a process renders its content
  white; every later one in the same process falls back to default grey. Two
  captures from different app instances therefore differ in ~99% of pixels for
  reasons unrelated to what is being measured — and a noise control built from
  two same-population shots agreed to 14 px, so it looked sound. That produced a
  confident WRONG conclusion (`tk busy` "gets photographed"). Stricter cousin of
  the standing "measure within one process" rule.
- ⚠ **A test that leaned on the old behavior had to change.**
  `test_widget_closed_while_settling_raises_a_bootstack_error` queued its destroy
  on a timer and relied on settle dispatching it; with the wait quiet that timer
  no longer fires during the capture and the test would have passed **without
  ever destroying anything**. It queues the destroy as IDLE work now. Confirmed
  non-vacuous by disabling the guard.

**⏭ WHAT IS OPEN NOW: is `tk busy` invisible off macOS?** `e4fd4af7` was measured
on macOS, Tk 8.6. The dispatching wait is the shape the Windows and Linux legs
already ran on 2026-08-08, so those legs' results still stand — what rides on top
of them, untested elsewhere, is the busy hold. **Arm 3 of
`development/probe_429_busy_during_settle.py` measures exactly that; run it on
Windows and Linux.** Then `demo_429_busy_during_settle.py` by hand for the input
half, which no automated arm can reach. Also re-run `verify_427_capture.py`,
since `settle()` changed twice underneath it.

⚠ **#431/#432/#433/#434 are NOT capture defects** and must not be bolted onto
this branch — they are pre-existing test-infrastructure bugs that running the
other platforms merely surfaced. #431 and #434 are the SAME modifier-bit
assumption seen from two platforms and are best fixed together, once Linux has
reported.

**The review ran 2026-08-07 and found six things; five were fixed on the branch,
one was documented. Do NOT re-derive these — each has a control committed at
`development/probe_427_review_fixes.py` reproducing the pre-fix behavior.**

- ✅ **The Linux virtual-desktop crop — FIXED (`8e721837`).** This was flagged
  here as "the likeliest real defect" and it was real: `crop((1930, 10, 2200,
  300))` on a 1920x1080 image returns 270x290 pixels, **every one black**, and
  raises nothing. `_crop_desktop()` now bounds-checks and raises. ⚠ **Region
  flags (`grim -g`, `import -crop`) were CONSIDERED and DELIBERATELY SKIPPED —
  do not re-propose them.** None can be verified from the Windows box, and a
  wrong `-g` region fails just as silently as the bug it would replace; the
  bounds check is the part that holds on every backend.
- ✅ **`save()` flattened only `RGBA` — FIXED.** The gate is on the target
  format now, because the subprocess fallback opens whatever the desktop tool
  wrote and mode `P` fails with `cannot write mode P as JPEG`.
- ✅ **`settle()` re-entrancy — FIXED.** It turns the event loop, so a queued
  handler can close the target. **Measured: `winfo_ismapped()` on a destroyed
  widget RAISES `TclError: bad window path name` — it does not return 0**, so a
  raw toolkit error escaped a method documented to raise `BootstackError`. That
  measurement is what made the finding real rather than overstated.
- ✅ **A negative `inset` — FIXED.** It expanded the rect and photographed the
  neighbors; a 60x20 widget with `inset=-8` yields a 76x36 grab, **invisible to
  the existing `right <= left` guard because the box only grew.**
- ✅ **macOS Screen Recording permission — DOCUMENTED** (it returns the desktop
  and raises nothing). ⚠ **`CGPreflightScreenCaptureAccess()` would detect it
  but needs pyobjc, which bootstack does not depend on — decided against, do not
  re-propose.**
- ✅ **A dangling `:func:` xref — FIXED.** It pointed at
  `bootstack.dialogs.ask_save_file`; the verb is top-level and its only autodoc
  home is `bootstack.ask_save_file`. ⚠ **A default `-W` build does NOT catch a
  dangling py xref — only `-n` does.**

#### ✅ `fix/formdialog-select-value-428` — MERGED (PR #442, `06acd727`), branch deleted

Shipped to `main` on 2026-08-11. It grew well past its name and carried **#428**
(the external report from `@bLynnb2762`), **#437** and **#438** — all three now
CLOSED and milestoned `0.3.0 — Screen capture and dialog results`. Head at merge
was **`38d01598`**. ⚠ **Nothing is released yet**: `0.3.0` still waits on
capture, so #428's reporter has NOT been told it is live. Post that comment with
`gh issue comment` after the release — `gh issue close --comment` silently drops
it on an already-closed issue.

⚠ **THE SUITE WAS NOT GREEN WHEN THE BRANCH WAS HANDED OVER, and the way it got
that way is worth more than the fix.** Round 4's verification ran at `70a039ce`
— **one commit before** `f9f1692f` rewrote the very tests it was verifying — so
a flaky test entered `main`'s queue unseen. Fixed pre-merge in `3d24ebbf`.
**Verify at the commit you are shipping, not at the last one you happened to
measure.**

**The flake, because the mechanism will recur:**
`test_enter_on_a_focused_button_does_not_also_press_the_default` failed its own
precondition — `focus_lastfor()` named the toplevel, so the `focus_set()` above
it had done nothing. **Tk's `focus_set()` is a SILENT no-op when the widget or
any ancestor is unmapped**: `TkSetFocusWin` walks the ancestry and returns
without setting anything, reporting nothing, so the miss surfaces one line later
as an inexplicable focus assertion. The test's `_drive` helper polled for the
modal grab as its "the dialog is up" barrier, but **the grab is set before the
geometry manager maps the footer's children at idle** — the failure carried
`button mapped=0 parent mapped=1 top mapped=1 grab=.!toplevel7`. Rate: **1 in 5
full legs, 0 in 60 dialogs in a quiet process.** The barrier now waits for the
grab AND the footer being mapped.

⚠ **A 1-in-5 flake cannot be verified against by re-running.** The control at
`development/probe_437_focus_flake.py` CREATES the condition instead —
packed-but-not-yet-updated widgets leave idle geometry work outstanding when the
dialog goes up: **old barrier 5/10 unmapped and 5/10 focus misses, new barrier 0
and 0**, the two columns tracking one-for-one. Arm 1 is the mechanism alone and
arm 2 is the quiet-process control that returns 0/60.

⚠ **Round 4's review record was never written.** Four fix commits answered
findings that existed nowhere in the repo. Reconstructed into `REVIEW.md` from
the commits and their probes, labelled as reconstructed. **Rounds 1–3 each
landed a `docs(review):` commit; make that the last step of a fix step, not an
optional one.**

**The root cause, so it is not re-derived:** `FormDialog.result` was read AFTER
the dialog closed, by which point the editors were destroyed and the only thing
left to read was the on-screen TEXT — which arrives as a string whatever the
value's real type was. It was never a conversion on the read path (an early
session proved that half and it held). Entries are now captured at the press,
while the form is alive, in `_accept_press`. The same defect hit every editor
whose display differs from its value, not only `select`: a date field handed back
its formatted text.

⚠ **The plan and the full four-round review record are ARCHIVED** at
`development/plan-428-437-438-dialogs.md` and
`development/review-428-437-438-dialogs.md` (they were `PLAN.md` / `REVIEW.md` at
the root while the branch was live). The per-round briefs are
`development/review-brief-437-438-dialog-buttons.md`, `…-round3.md` and
`…-round4.md`. **Four rounds ran — 5 findings, then 8, 7 and 4.** Read those
before reopening any of this rather than re-deriving it.

**Round 4 (2026-08-11) found five things; all five are handled:**

- ✅ **The Dialog page taught reading a content widget after `show()`** —
  `create_project(fields["name"].value)`, i.e. after every widget was destroyed.
  It survived only because `TextField` is `StringVar`-backed; the same idiom with
  a `bs.Select` raises `TclError`. **That is the very pattern #428 exists to
  prevent, in the release that fixes it.** The example binds a `Signal` now.
- ✅ **A DISABLED button swallowed Enter** — the stand-down guard assumed a
  button that received the key had already acted on it, which is false when
  `invoke` does nothing. Any content button that greys itself out on click left
  the keyboard dead for the whole dialog.
- ✅ **The bindtags read went through Tcl for a case that cannot arise here.**
  Tkinter really does hand a callback a bare path string when the target is
  absent from its widget map — but a dialog has 0 such widgets of 32, because
  bootstack creates everything from Python. Simplified to `.bindtags()`.
- ✅ **A CHANGELOG sentence contradicted the branch's own measurement** (claimed
  dialogs resting on their default button were unaffected; #439 says no dialog
  is in that state at open). Removed rather than corrected — the accurate version
  would document #439 as if intended.
- ✅ **A test pinned #439 as a passing precondition.** Loosened, so fixing #439
  cannot turn it into a precondition failure.
- ⏭ **Filed as #441, deliberately NOT fixed here:** Enter in a `TextArea` inserts
  the newline and then the dialog closes on top of it, because the guard
  recognizes only `TButton`. Needs a general rule for "did something already
  handle this key?", not another special case.

⚠ **Traps this branch already paid for — do not re-pay them:**

- **`bootstack.dialogs.FormDialog` is a public WRAPPER**, not the impl in
  `dialogs/_impl/formdialog.py`. Reach the impl through `._internal`.
- **`dlg.show()` runs a modal wait loop that a close scheduled with `after` does
  NOT break.** Drive it by invoking a real footer button instead — and poll for
  the modal grab rather than firing on a fixed delay, because `show()` pumps the
  event loop while building and positioning, so a timer can land on a half-built
  dialog. `_drive()` in `test_dialog_press_contract.py` is the worked pattern.
- **`instate(['!disabled'])` is a QUESTION returning True when the widget is
  ENABLED.** `not instate(['!disabled'])` therefore selects the disabled one —
  a double negative that silently inverts a guard. Write
  `not instate(['disabled'])`.
- Probe output must be **ASCII** — a check mark raised `UnicodeEncodeError` on
  this box's cp1252 console. Same rule #430 hit.

**⚠ THIS LINE IS STALE — see START HERE for the live answer.** As of 2026-08-11
(later still) the refs are **`main` and `fix/dialog-keyboard-modality`**, the
latter LOCAL ONLY. `feat/widget-capture-427` and
`fix/formdialog-select-value-428` both shipped in `0.3.0` and are deleted.

Original line, kept for the reasoning that follows it: *BRANCHES: `main`,
`feat/widget-capture-427` — `fix/formdialog-select-value-428`
merged as PR #442 and was deleted local and remote on 2026-08-11.*
The `main`-only state below
was verified 2026-08-06 after the `0.2.2` release and held until the branch above
was pushed on 2026-08-07.
An earlier sweep on 2026-08-05
(maintainer-approved) deleted all seven survivors together with
their `: gone` locals: three merged ancestors (`docs/custom-events-409` PR #414,
`fix/command-option-modifiers-405` PR #411, `fix/event-cleanup-392-followups`
PR #410) and four squash-merge leftovers (`cleanup/shell-visibility-idiom` PR #384,
`fix/literal-mode-guards` PR #382, `fix/394-field-row-alignment` PR #395,
`fix/403-test-coverage` PR #406). Head SHAs are in the deleting commit's message if
one ever needs resurrecting; GitHub also keeps each PR's head SHA.

⚠ **The method matters more than the result, because this recurs every release.**
**Non-ancestor ≠ unmerged.** Four of the seven were not ancestors of `main` purely
because their PRs were **squash-merged**, and an earlier handoff nearly read that
as live work. Verify with two commands, never by reading this file:
`git merge-base --is-ancestor origin/<branch> origin/main` for ancestry, then
`gh pr list --head <branch> --state all --json number,state,mergedAt` — a MERGED PR
is what makes a non-ancestor safe to delete. Record the head SHAs before deleting.

**`0.2.1` shipped `#396, #398, #399, #400, #403, #405`** in the release notes,
plus **#397 and #401**, which are fixed and merged but **deliberately absent from
the CHANGELOG**. Neither was reachable from public API, so listing them handed a
reader scanning for upgrade risk a false positive — the same call made for #387 in
`0.2.0`. Verified, not assumed: `MessageDialog`/`QueryDialog`/`DateDialog` are
absent from `bootstack.dialogs.__all__` and the public verbs return their result
directly, while the one public dialog class (`ColorChooserDialog`) was the case
that was already correct; and `on("increment")` raises `UnknownEventError` with no
`on_increment` shorthand. **Both remain fully documented in their own commit
messages** (`a93a47a4`, `7e204801`) — that is where the root causes live now.

**0.2.0 shipped `#332, #379, #381, #387, #388, #392, #394`.** It was **a minor,
not a patch**, and that was a deliberate maintainer call: the project committed to
SemVer at 0.1.0 and **#381** raises where it used to accept. ⚠ **This file used to
claim TWO incompatible changes; that was wrong.** The second (`configure(data=)`
clearing absent keys, #387) is **not publicly reachable** — `bs.Form` has no
`configure` method at all (verified: `AttributeError`), so no user can observe it.
One genuine break still warrants a minor, so the version is right — it just rests
on one leg, not two. The CHANGELOG correctly omits it. **#394** also moves pixels
in any layout pairing a field with a taller widget on a stretch axis.

**⏭ ACTIVE: `feat/widget-capture-427` (#427), pushed 2026-08-07. Reviewed, all
findings applied; awaiting the macOS/Linux legs, then a PR** — see the IN FLIGHT
block under Current state. It was
taken ahead of the standing recommendation deliberately: an external user asked
for it in discussion #425, and it is additive, so it cannot destabilize the
batched strictness work. ⚠ **It adds public surface, so it CANNOT ride the patch
line.** ✅ **DECIDED 2026-08-07 (maintainer): it CUTS AHEAD as its own minor.** It
became `0.3.0`, and everything below it shifted up one. ⚠ **That milestone was
later RENAMED to `0.3.0 — Screen capture and dialog results` and widened to carry
#428, #437 and #438** — capture no longer ships alone.

After it, pick
from the table below. ⚠ **The standing recommendation named here for months —
the unnumbered `Test and release confidence` workstream (#407 then #380) — is
DONE and its milestone is CLOSED (2026-08-14).** The live recommendation is at
START HERE: **#452**, because CI now covers ubuntu and windows and not macOS.
After that the next numbered milestone is **`0.4.0 — Signal binding on fields`**
(#458, #459, #460, #461), cut 2026-08-19 and already half-built — #458's branch
has passed round 1. Then `0.5.0 — Strictness and value types` (#383, #369, #408,
#416), deliberately batched so users get one migration rather than four.
**#390** remains a decision that can be taken at any time, and is
still the cheapest item on the board. ⚠ **The milestones have been RENUMBERED
THREE TIMES — read the CURRENT table below, never a number quoted in older
prose.**
Restructured and renumbered 2026-08-05, then renumbered again 2026-08-07 when
`0.3.0 — Screen capture` was inserted ahead of the strictness batch. Two
generations of stale numbers are therefore in circulation:

| written before | says | now means |
|---|---|---|
| 2026-08-05 | `0.3.0 — Guided flows` | `0.7.0 — Guided flows` |
| 2026-08-05 | `0.4.0 — Power-user interactions` | `0.8.0 — Power-user interactions` |
| 2026-08-05 | `0.5.0 — Structured editing` | `0.9.0 — Structured editing` |
| 2026-08-05 | `0.6.0 — Argument and value strictness` | `0.5.0 — Strictness and value types` |
| 2026-08-07 | `0.3.0 — Strictness and value types` | `0.5.0 — Strictness and value types` |
| 2026-08-07 | `0.4.0 — Form, signals, and composite authoring` | `0.6.0 — …` |
| 2026-08-07 | `0.5.0 / 0.6.0 / 0.7.0` | `0.7.0 / 0.8.0 / 0.9.0` |
| **before 2026-08-19** | `0.4.0 — Strictness and value types` | `0.5.0 — Strictness and value types` |
| **before 2026-08-19** | `0.5.0 / 0.6.0 / 0.7.0 / 0.8.0` | `0.6.0 / 0.7.0 / 0.8.0 / 0.9.0` |

⚠ **THE 2026-08-19 ROW IS THE THIRD RENUMBERING, and unlike the first two it was
NOT a restructuring** — nothing was re-scoped. A new minor (`0.4.0 — Signal
binding on fields`) was inserted ahead of the chain because the signal work was
ready and the strictness batch is not started, and everything above it shifted
one step. The renames were done top-down (`0.8.0`→`0.9.0` first) so no title ever
collided with a live one; issue attachments are unaffected by a milestone rename.

⚠ **Prose further down this file still quotes the OLD numbers in places** (e.g.
"#369 and #383 are milestoned `0.6.0 — Argument and value strictness`"). Those
lines were not swept. The table above is the authority; when you touch such a
line, fix it.

**THE RULE, which is the part worth keeping: numbered milestones are RELEASES;
unnumbered milestones hold work NOT YET ASSIGNED to a release.** Membership in a
numbered one is decided by compatibility *and* readiness, and the title names what
actually ships. Nothing gets a number until its order is real.

⚠ **CLOSE A MILESTONE WHEN ITS RELEASE SHIPS** (maintainer, 2026-08-11). The
project had been inconsistent — only `0.1.0` was ever closed, while `0.2.0` and
`0.3.0` sat open with zero open issues, so the milestone list mixed finished
history with live work. All four shipped milestones are closed now
(`0.1.0`, `0.2.0`, `0.2.x`, `0.3.0`), which makes **the open list exactly the
live work and a direct cross-check on the table below.** They agreed 1:1 when
last verified. If they ever disagree, trust `gh` and fix the table. This replaced an
accidental mix in which `0.2.x`/`0.6.0` were compatibility buckets wearing subject
names while `0.3.0`–`0.5.0` were subject themes wearing version numbers — which is
how three of five `0.3.0 — Guided flows` issues came to be form/signal work.

⚠ **The unnumbered half was first written as "workstreams that do not map to a
release." That was wrong** — most of it maps to a release, just an undetermined
one. Each unnumbered milestone says *why* it has no number: Tk 9 is blocked on
hardware, hot reload is outside the SemVer freeze, test confidence rides any patch,
additions ride any minor.

⚠ **The patch line is BUG FIXES ONLY.** The project committed to SemVer at `0.1.0`,
so **adding public surface is a MINOR even when nothing breaks** — someone upgrading
`0.2.1 → 0.2.2` should be able to assume no new API arrived. An audit on 2026-08-05
found **three of the patch line's four issues were additions** (#352 a whole new
widget, #317 and #208 additive), which is why `Additions awaiting a minor` exists.
⚠ **The trap to avoid repeating:** the milestone had *already* been renamed away
from "Fixes and small additions" to stop that creep, while its description still
said "fixes and small additions" — so the rename changed nothing. **Fix the
description, not just the title.**

⚠ **BUT THE RULE IS ONE-DIRECTIONAL, AND THIS FILE USED TO IMPLY OTHERWISE**
(corrected by the maintainer, 2026-08-11). An addition **requires** a minor; a
minor does **not** require additions. `Additions awaiting a minor` is a queue of
work that *cannot* ride a patch — it is **not** a statement that minors are for
additions, and a minor is free to carry as many plain bug fixes as it likes.
`0.3.0` did exactly that: two additions and **six fixes**. So when a minor is
being cut anyway, ask what else is ready rather than parking fixes for a later
patch out of habit. The mirror-image question is just as useful and is what
scoped `0.3.1`: **for a fix, ask whether it needs a minor at all** — if it adds no
public surface it can ship as a patch, which is what let `0.3.0` go out on time
with four known bugs deferred rather than held.

| Order | Milestone | Open |
|---|---|---|
| — | ~~**`0.3.0 — Screen capture and dialog results`**~~ — **SHIPPED 2026-08-11**: #427, #428, #429, #437, #438 | 0 |
| — | ~~**`0.3.1 — Dialog keyboard and modality`**~~ — **SHIPPED 2026-08-12, milestone CLOSED**: #426, #439, #440, #441, #446 | 0 |
| — | ~~**`Test and release confidence`**~~ — **DONE 2026-08-14, milestone CLOSED** at `open=0 closed=3`: #407, #380 (PR #451), #432 (did not reproduce) | 0 |
| 3 | **`0.4.0 — Signal binding on fields`** — #458, #459, #460, #461. **NEW, cut 2026-08-19**, and the next release out the door | 4 |
| 4 | **`0.5.0 — Strictness and value types`** — #383, #369, #408, #416 | 4 |
| 5 | **`0.6.0 — Form, signals, and composite authoring`** — #390, #389, #412, #415 | 4 |
| 6 | **`0.7.0 — Guided flows`** — #311, #312 | 2 |
| 7 | **`0.8.0 — Power-user interactions`** — #315, #316 | 2 |
| 8 | **`0.9.0 — Structured editing`** — #192, #314 | 2 |
| — | **`Tcl/Tk 9 support`** (unnumbered, blocked on hardware) — #376, #378 | 2 |
| — | **`Hot reload (provisional)`** (unnumbered, outside the freeze) — #322, #328 | 2 |
| — | **`Additions awaiting a minor`** (unnumbered, rides any minor) — #208, #317, #352 | 3 |
| — | **`0.3.x — Patch line`** (rolling, FIXES ONLY) — #207, #422, #444, #445, #447, #449. **#453 and #456 are CLOSED** (cut as `0.3.2`, and merged as PR #457), so the milestone reads **`open=6 closed=2`** — verified against `gh` 2026-08-19 (latest), not counted by hand. It is a rolling line, so it does NOT close when a patch ships. ⚠ **#460 was briefly placed here and then MOVED to `0.4.0`** when the signal work was collected into one minor — if an older paragraph says #460 is on the patch line, that paragraph is stale | 6 |

⚠ **`0.2.x — Patch line` was NOT renamed, and that was checked rather than
assumed** (2026-08-11). It holds **15 CLOSED issues** — the whole `0.2.1`/`0.2.2`/
`0.2.3` patch history — so renaming it would have relabelled shipped work as
`0.3.x`. A **new `0.3.x — Patch line`** was created instead and the two open
issues moved onto it (#207 deferred by decision, #422 test-only). `0.2.x` now
reads `open=0 closed=15` and is a finished record. **The check to repeat when a
line rolls over: `gh api repos/:owner/:repo/milestones --jq '.[]|"\(.title)
open=\(.open_issues) closed=\(.closed_issues)"'` — closed issues make a milestone
history, and history is not renameable.**

Ordering reasons, so they are not re-litigated: **confidence first** (nothing runs
the suite, so every release is a gamble, and #407 makes that automation cheaper
before you buy it); **breaks batched, not dribbled** (#383/#369/#408/#416 in ONE
minor = one migration for users instead of four); then near-ready API, then new
widgets. ⚠ **Numbers past `0.4.0` are ordering hints, not commitments** — they
assume three minors land in that sequence, which nobody knows. Retitling is cheap;
that is the point of the rule. **Subject now lives on LABELS** (`tk9`,
`test-infra`, `hot-reload`, `new-widget`) so milestones can stay about *when*.
Reasoning also in memory `project_roadmap_milestones`.

⚠ **RESOLVED 2026-08-14 — but the list below is now STALE by three.** #432, #433
and #434 are CLOSED; **#431 is deliberately still OPEN.** So the live unmilestoned
set is **#431, #436, #452, #455**.

⚠ **#431 IS OPEN ON PURPOSE AND IS WAITING ON A DECISION, not on work.** Its fix
landed with #434's — the NumLock bit resolves per windowing system — but on aqua
it **SKIPS**, because macOS has no NumLock modifier for `Mod1` to carry and
asserting anything about bit 8 there would be asserting something about Command,
which `test_command_binding_exists_only_on_macos` already covers directly. So the
test cannot be made meaningful on Aqua and now says so out loud. **That resolves
the failure; whether it resolves the issue is a scope call.** Close it if "no
longer fails, and says why" is the wanted outcome; re-scope it if macOS should
have positive coverage of the bare-`b` path, which would need a premise other
than NumLock. ⚠ **And it is UNVERIFIED on a real Aqua build** — the skip is driven
by `tk windowingsystem`, read from Tk rather than cached, but nobody has watched
that branch be taken. Fold it into the #452 trip.

**⚠ FOUR UNMILESTONED OPEN ISSUES — re-verified against `gh` on 2026-08-19
(latest)**, not counted by hand: **#431, #436, #452, #455.** All four PREDATE
this work. **#458, #459, #460 and #461 all went onto the new
`0.4.0 — Signal binding on fields`**, so the list is back to where it was before
the signal work started. ⚠ **The list below
is the 2026-08-13 one and names #433 and #434, which are now CLOSED; the two
that replaced them are #458 (the `Select` signal fix, in flight) and #459 (the
`TimeField` seed-emit it surfaced).** Original text follows.

not counted by hand: **#431, #433, #434, #436, #452, #455.** #455 is the one
that moved: the survivor of #453's round 2 (`Field.enable()/disable()/readonly()`
writing the ttk readonly state without re-deriving), left unassigned because it
gates nothing — `0.3.2` ships without it, so its placement is a scope call, not
a fact already decided by a blocker. #453 itself was filed onto
`0.3.x — Patch line` by the maintainer, so it never joined this list. #452 is the macOS CI hang, filed 2026-08-12 and left unassigned per the rule below. #447 and #449 went to `0.3.x — Patch line` when `0.3.1` closed (maintainer, 2026-08-12); the remaining four all PREDATE this work and are deliberately left alone. The new one
is #447, flake C, filed out of round 4 under gate 4's one-attempt rule and left
unmilestoned per the rule below. Earlier the same day **#446 went to `0.3.1` and
#432 to `Test and release confidence`** (maintainer, 2026-08-12).

⚠ **STALE, and left here only for the rule it produced: this said "`0.3.1` STILL
HAS ONE OPEN ISSUE — #446 — so the milestone cannot be closed at release
time."** It was settled on 2026-08-12 — **#446 was CLOSED rather than moved**,
because its scope was exactly the two flakes and both shipped in `48dba181`; the
third became #447, which went to `0.3.x — Patch line`. `0.3.1`'s milestone reads
`open=0 closed=5` and is closed. **The open-milestone list is the cross-check on
the table above and they agree 1:1 — trust `gh`, not a paragraph.**

⚠ **THAT PAIR CORRECTED A MISREADING OF THE "do not assign unasked" RULE, and
the correction is the part worth keeping.** This file had #446 sitting
unmilestoned while simultaneously describing it as a merge blocker for `0.3.1`,
and #432 unmilestoned while describing it as the blocker for #380. **That is
incoherent on the file's own terms: a milestone answers WHEN SOMETHING SHIPS, so
an issue that gates a release has already had its milestone decided by the thing
it blocks.** The maintainer put it directly — *"I'm not sure why you would think
this doesn't belong in a milestone that gates that milestone release."*

**The rule is narrower than it was being applied.** "Do not assign a milestone
unasked" guards against making SCOPE calls for the maintainer — deciding that a
piece of optional work belongs in a release. It was never about a blocker, whose
placement is a fact rather than a choice. **The test: would shipping the
milestone without this issue be a decision, or a defect?** A defect means it
belongs on the milestone; a decision means ask. #430 is the same shape from the
other side — the maintainer said "we release this with 0.2.3", which decided it.

**#431/#433/#434 all came out of running the macOS and Linux legs for #427**
and are **test-infrastructure failures, not user-facing** — which is exactly why
they were kept OUT of `0.3.0`: a CHANGELOG entry earns its place by being
reachable, and a user cannot observe any of these. **They gate nothing, so they
stay unassigned** — that is the rule working, not the exception. **#436** is the
`versionadded` convention, filed 2026-08-10, and it carries an undecided question
(retroactive to `0.2.x`, or forward-only) — worth answering now that `0.3.0` has
shipped new public surface that a reader cannot date.

⚠ **#432 moving onto `Test and release confidence` also fixes the ORDER inside
that milestone.** It is listed as #407 then #380, but #432 is the blocker to
attack first: the shared-root GUI leg cannot complete on Linux at all, which
makes CI unbuyable until it is fixed.

**ZERO UNMILESTONED OPEN ISSUES as of 2026-08-06** (verified against `gh`, not
counted by hand) — the deviation this file used to flag was closed. The maintainer
assigned #417, #418, #419, #420, #421 and #422 to `0.2.x — Patch line` in one call:
all six are bug fixes on existing public API and **none adds public surface**, which
is the test for the patch line. #417 came from an external user; the other five were
filed by us while fixing it. ⚠ **Do not assign a milestone unasked** — that rule
still stands for work whose membership is a SCOPE call, which this was (an
explicit decision). ⚠ **It does NOT cover a blocker** — see the correction above:
if the milestone cannot ship until the issue is fixed, its placement is already
determined and leaving it unassigned just hides the gate.
⚠ **A bullet in this file is not proof an issue is open** — #222, #234
and #379 all sat here as open work after being closed; check the state first.
Check with:
`gh issue list --state open --json number,milestone --jq '[.[]|select(.milestone==null)]'`


#### Shipped release history — `0.3.2`, `0.3.1`, `0.2.2`, the CI workstream (#380/#451), and #456

##### ✅ #456 / PR #457 — MERGED 2026-08-19 as `0aad8427`. Kept for its lessons.

**The bug:** `DataTable`'s `context_menus` option was documented, shown in the
widget guide, and had **no effect** — every table offered both right-click menus
whatever you asked for.

⚠ **The mechanism is the part worth carrying, because it is a REPEAT.** The
internal was never at fault: `_impl/composites/tableview/tableview.py` has read
and honored the option all along. **The public wrapper never delivered it** —
`internal_kwargs` is a closed dict built from named parameters only, so
`context_menus` fell into `**kwargs`, survived `_split_layout_kwargs` as though it
were a layout key, and was discarded. **That is exactly #383's third gap**, already
recorded in this file. Expect it again in any wrapper: the test is
`git show main:<wrapper> | grep <kwarg>`, not reading the impl.

**Two changes.** (1) The option now reaches the widget, validated strictly.
(2) **`on_row_right_click` was DECOUPLED from it** (maintainer, 2026-08-19 — *"I
would not expect that argument to affect `on_row_right_click`"*). The event was
emitted inside `_on_row_context` one line before the menu opened, with the whole
method behind the row-menu gate, so it tracked the **menu** rather than the
**right-click**. The rule now: **`context_menus` chooses which menus the table
offers; it does not choose whether a right-click is reported.** Precedent was
three lines below the edit — `on_row_double_click`, from #417.

⚠ **ONE DELIBERATE BEHAVIOR BREAK, already decided — do NOT re-file it.**
`validate_choice` means `context_menus=None` and `"None"` construct on `0.3.2`
(silently, both menus on) and **raise** here. **Accepted** (maintainer,
2026-08-19 — *"if None is not a valid argument and not specified as an option,
then we should not care about it"*): neither is in the documented `Literal`, so
there is no supported behavior to grandfather. ⚠ `PLAN.md` originally justified
this with *"the argument is unreachable from public code"*, which was **FALSE** —
it was always passable, just inert. Premise corrected, decision unchanged. The
SemVer counter-argument (#381 needed a **minor** because it raises where it used
to accept) is written out in `REVIEW.md` with the distinction that defeats it.

**MERGED — nothing open. The line below described the pre-merge state.** The round is closed,
the record is written, the tree is clean, and **CI came back green on all five
jobs**. ⚠ **That green also answers a real prior worry, so do not re-raise it:**
`test_datatable_right_click_event.py` synthesizes `<Button-3>`, and this file
warns that synthesized events get dropped once the shared root fills up and a
widget goes unmapped. Both Linux legs and the Windows leg passed, so the drive is
sound off the macOS box it was written on.

⚠ **ON MERGE: archive `PLAN.md` → `development/plan-456-context-menus.md` and
`REVIEW.md` → `development/review-456-context-menus.md`, then create `PLAN.md`
fresh.** A stale plan describing shipped work is worse than none. Also comment on
#456 with `gh issue comment` after the *release*, not the merge — `gh issue close
--comment` silently drops it on an already-closed issue.

##### ⚠ FOUR THINGS THIS SESSION PAID FOR — do not re-pay them

- ⚠ **A CHANGELOG claim about PRIOR behavior must be checked against the OLD code,
  not against the fix.** The #456 bullet said a misspelled value *"previously
  turned both menus off silently"*. It did the **opposite** — the value was
  discarded, so both menus stayed **on**. The sentence was written from the fix's
  point of view and read as authoritative. `git show main:<file>` settles it in one
  command. **This project has already reworded two CHANGELOGs AFTER tagging**
  (`0.3.1`, `0.3.2`), each forcing a `gh release edit` on a published body.
- ⚠ **A stale MEASUREMENT block is worse than a stale table, because it reads as
  proof.** `PLAN.md` carried a verification block recording `right-click bound:
  False` — measured **before** the decoupling commit and never re-run, so the
  branch's own record displayed the behavior the branch had just reversed.
  **Re-run a recorded measurement after any commit that changes what it measures.**
  Same file also carried a stale test-count delta (`+8` where the truth was `+7`)
  and a Tests table asserting the pre-decoupling contract. **Cause in all three:
  `63d4cb2d` recorded the decision by APPENDING (34 insertions, 1 deletion) without
  sweeping what it contradicted.**
- ⚠ **LINE ENDINGS BIT THIS BRANCH THREE TIMES.** `.gitattributes` declares
  `eol: crlf`; `PLAN.md` and `probe_456_context_menus.py` were both LF in the
  working tree, the probe already committed that way. **`git diff` cannot see it** —
  only `file <path>` and the *"LF will be replaced by CRLF"* stderr warning can.
  Normalize in binary mode (strip `\r`, then re-add), never with a `$`-anchored
  `sed`. This file has warned about it for weeks and it still recurred.
- ⚠ **A manual edit left a stray `u` byte before `datatable.py`'s BOM
  (`75 ef bb bf`), and the WHOLE PACKAGE became unimportable** —
  `SyntaxError: invalid non-printable character U+FEFF`, every affected test file
  erroring at collection. Committing it would have shipped a broken build. **Verify
  `import bootstack` at the COMMITTED state, not just in the working tree**, when
  anything has hand-edited a source file.

⚠ **THE FULL SUITE WAS NOT RE-RUN after the review round's edits, and that is
stated rather than implied.** Those edits are one source *comment*, `CHANGELOG.md`,
`PLAN.md` and one new file under `development/` — no production behavior moved, and
the 68 tests that ran cover every test file the branch touches. `PLAN.md`'s
recorded full run stands: exit 1, 33 legs, the single failure being **#449**, an
already-filed flake at ~1 in 10 whose file the branch's one-file `src/` diff cannot
reach. **If you want a clean number against the pushed head, measure it — do not
infer one.**

⚠ **NOTHING ON THIS BRANCH HAD EVER OPENED A CONTEXT MENU until 2026-08-19.** The
tests assert on the two gate predicates or on `<<RowRightClick>>` dispatch, and
`probe_456_context_menus.py` reads gates only. `development/demo_456_context_menus.py`
is the manual checklist that closed it — **run by the maintainer, menus confirmed.**
Its own wiring was proven headlessly first (data row increments; group header and
empty space do not), which is also the first live confirmation that #418/#420's "no
row event without a record" invariant survived moving the gate. ⚠ **The header half
still has NO automated end-to-end coverage** — that was left as a gate-2 note, not
filed, because the predicate read *is* the seam the click path consults.

⚠ **#380 SHIPPED WITH NO CHANGELOG ENTRY, AND THAT IS CORRECT — do not "fix" it.**
CI is not reachable by any user, and an entry earns its place by being reachable.
Same call as #407. #433 and #434 rode along on the same reasoning.

⚠ **PR #451 OPENED ZERO REVIEW ROUNDS, and that was the protocol working.** Gate 1
triggers on a non-empty `git diff <range> -- src/`; this branch's was empty at
every point, verified rather than assumed. Declared cap 2, actual 0 — **the second
branch in a row where gate 1 held**, after #407. There is no `REVIEW.md` to
archive because no round was opened.

⚠ **BUT GATE 1 HAS A GAP THIS BRANCH WALKED THROUGH, and it should be settled
before the next infrastructure branch.** Gate 1 exempts commits that change "only
tests, probes, or documentation". **`.github/` is none of those three**, and
`ci.yml` was this branch's actual deliverable — the trigger is defined
mechanically as the `src/` diff, so it read as no-round, but the *reasoning*
behind the exemption (reviewing test instruments never terminates) does not cover
a CI workflow. It was raised with the maintainer rather than resolved silently.
**The mitigating fact: a workflow is checked by RUNNING, and this one ran green
on the real runners.** That is stronger evidence than a reading review — but it
is not the same thing, and gate 1 should say which it means.

##### ⚠ ONE THING WAS NOT VERIFIED — read before trusting the capture leg

**The capture leg reported `21 passed / 2 skipped` on CI against `22 / 1`
locally.** The likely reason is the ordering artifact `_pin()` documents in its
own docstring — a refused always-on-top request still leaves a record, so the two
topmost tests behave differently depending on which ran first. **That was NOT
confirmed on the runner.** The alternative is that `openbox` (CI) and `xfwm4`
(local, because this box has no `openbox` and no passwordless sudo) differ on
whether they honor always-on-top. Neither reading was measured. **Do not cite the
capture leg's count as settled until someone does.**

**⚠ THIS SESSION RAN FROM A THIRD MACHINE — A WSL BOX — AND IT IS SET UP NOW.**
See the Environment section. It is the only box that can run the Linux leg, and
its previous session's environment had been lost; a venv at
`/home/iddryer/.virtualenvs/bootstack` now carries an editable install, and WSL
git is wired to the Windows credential manager so it can push and use `gh.exe`.

##### What closed the Linux question

**#447's CI reproduction is a MISSING WINDOW MANAGER, not a product bug.** Under
X11 it is the window manager, not the server, that assigns input focus to a newly
mapped top-level window. Bare `xvfb-run` starts none, so a dialog is mapped but
never focused and the toplevel's `<Return>` binding has nothing to fire against.
**`focus_lastfor()` returning the EMPTY STRING was the tell** — not "focus is on
the wrong widget" but "nothing in this toplevel ever held focus". Same
silent-no-op family as the fixed #437 flake.

Measured with only the window manager varying — same kernel, distro, Tk, Python
and commit: **7 dialog failures without one, 0 with one**, deterministic in both
directions. **So the `0.3.1` dialog keyboard work is fine on X11.**

⚠ **BUT #447 IS NOT CLOSED, AND MUST NOT BE CLOSED ON THIS.** It was reported as
a **Windows** flake at ~4/50, on a machine that HAS a window manager, and nothing
here explains that. "The same condition needs a race where a WM exists" is a
**hypothesis, not a measurement** — recorded as one on the issue. PR #451 removes
the CI reproduction; the Windows flake stays open.

##### What PR #451 now carries, beyond the workflow itself

| # | change | issue |
|---|---|---|
| 1 | `ci.yml` installs and starts `openbox`, polling `_NET_SUPPORTING_WM_CHECK` | #447 |
| 2 | the NumLock bit resolved per platform instead of hardcoded `8` | **#434, #431** |
| 3 | `cget("padding")[0]` read through `str()`, for Tk's `Tcl_Obj` | **#433** |
| 4 | the capture topmost-restore assertion waits for the WM to answer | — |

⚠ **THE POLL IS LOAD-BEARING — do not replace it with a `sleep`.** A window
manager that fails to start leaves the suite on an unmanaged display and
reproduces #447 **exactly**, which reads as a product bug rather than a broken
step. That false result was measured once already, when `xfwm4 --daemon` silently
failed to start and the arm came back **byte-identical** to the no-WM arm. Both
arms of the guard were exercised before committing: no WM exits 1 loudly, a real
one runs the payload.

⚠ **#4 WAS NOT PREVIOUSLY FILED, AND ONLY A WINDOW MANAGER CAN EXPOSE IT.** That
test *skips* where always-on-top is not honored, so bare Xvfb never ran it — it
is newly reachable, not a regression. Always-on-top is answered asynchronously,
which `_pin()` already polls for on the way IN; the assertion did not on the way
OUT. **The restore lands in ~1 ms and the immediate read still returns the old
value.** Product code is correct and untouched. Non-vacuity confirmed by
disabling that restore and watching the polled assertion still fail — **not** by
re-running.

**AUTHORITATIVE — measured 2026-08-14 on `ci/test-workflow-380` at `5921dc41`**,
WSL box, Ubuntu 22.04.5, Python 3.13.11, Tk 8.6.12, `pandas` ABSENT (so the data
leg reads `125 / 4`), 33 legs:

| arm | exit | passed | failed | skipped |
|---|---|---|---|---|
| Xvfb **+ window manager** | 0 | **1427** | **0** | 22 |
| Xvfb **bare** — what CI did | 1 | 1418 | **7** | 24 |

⚠ **IT RECONCILES AGAINST ITSELF: `1418 + 7 failed + 2 extra skips = 1427`**, the
two extra skips being the capture topmost tests standing down where no WM honors
always-on-top. And the 7 are exactly the #447 cluster, so **the test fixes did
not mask it** — remove the window manager and it returns. CI agrees: its Linux
shared leg reads `1032 passed, 14 skipped, 75 deselected`, identical to local.

⚠ **THE `1449` RECORDED FOR THIS BRANCH IS STILL UNRECONCILED AND IS NOT THE SAME
QUANTITY.** 1427 is a **Linux** figure; 1449 was not, and platform gating differs.
**Do not close the gap by picking whichever number makes the arithmetic work** —
the matrix reports all three platforms now, so re-measure per platform. This
file has been wrong about counts seven times; that is how.

##### ⚠ A DUPLICATE ISSUE WAS ALMOST FILED, AND THE NEAR-MISS IS THE LESSON

`development/issue-draft-appshell-mod1-x11.md` was committed on 2026-08-12 saying
the `bare_b` issue was unfiled and should be opened from the Windows box. **It
was a duplicate — #434 has existed since 2026-08-08**, carrying the same
Mod1-is-Alt diagnosis, and the report's finding 2 was already **#433**. The draft
is **deleted**; the report carries a correction header.

**The scope word is where it went wrong, again.** "Not yet filed" was true of
that *session* and not of the *tracker*, and nothing wrote down which was meant.
Same shape as `0.3.1` round 1's *"no other `grab_set` exists in the package"*,
where "the package" silently meant `dialogs/` and #444 was two rounds away.
⚠ **Committing the draft was still the RIGHT call** — that box genuinely had no
`gh` and no credential, and a guessed issue number would have been worse.

##### ✅ #432 DID NOT REPRODUCE — decide it, don't re-scope it blind

Both Linux legs ran **all 33 legs to completion** and reported normally, twice
now. #407 appears to have removed it. It was the stated blocker on this whole
workstream, so **closing or re-scoping it is a maintainer call that is now
cheap to make.**

⚠ **ONE ITEM IS THE MAINTAINER'S, NOT YOURS: telling `bLynnb2762` that #453 is
live.** They took it on 2026-08-13 (*"I'll respond to the user"*). **Do not post
it as well** — a duplicate to an external reporter is worse than a late one. If
you ever do post one, use `gh issue comment 453`; `gh issue close --comment`
silently drops the comment on an already-closed issue and warns only about the
close.

##### ✅ `0.3.2 — Read-only select fields` IS ON PyPI (2026-08-13)

Tag `v0.3.2`, **`release.yml` ran clean** (build, publish, GitHub Release all
green) and **`docs.yml` chained off it automatically** — no manual kick. One
user-facing fix, #453, on the patch line because it adds no public surface.

**Every post-release check was VERIFIED, not assumed:** PyPI read from
`/pypi/bootstack/0.3.2/json` (never the CDN-cached summary endpoint) **and** a
real `pip download`; the wheel opened and the #453 fix confirmed *inside it*;
`import bootstack` with **`idlelib` BLOCKED by a `meta_path` finder, with a
control asserting the block itself bites** (#430); provenance asserted so the
test could not silently import the editable working tree; `WidgetRedirector`
confirmed as bootstack's own module; `NOTICE` at `dist-info/licenses/`; the
GitHub Release live with both assets; `bootstack.org` 200.

⚠ **THE `idlelib` GREP CAME BACK POSITIVE AND WAS A FALSE ALARM — this is why
the meta_path test exists.** A substring search for `from idlelib` matched
**`"borrowed from idlelib/parenmatch.py"`**, prose inside a docstring
attribution. All seven mentions in the wheel are attributions; none is an import
statement. **Do not re-prove #430 with grep, in either direction.**

⚠ **`bump-my-version` reported `1.5.0` today** where this file recorded `1.5.1`
on 2026-08-08, and it had vanished entirely once before. **Check it exists
before assuming the release flow works.**

⚠ **`v0.3.2` AND `main` DIFFER BY DESIGN, exactly as `0.3.1` did.** The
CHANGELOG entry was **reworded after the tag** (`c2ff50fb`): it was accurate —
every claim traced to a named test — but written in the framework's vocabulary
rather than the reader's (*"rather than an internal state"*, *"built on the same
internals"*), which is the implementation detail the same day's review had just
stripped out of the `Select` docstring. **The GitHub Release body was edited to
match with `gh release edit --notes-file`**, built by running
`release_notes.extract` against the corrected file and splicing the
auto-generated `## What's Changed` tail back verbatim, with an assertion
refusing to overwrite if that tail was missing. **THE TAG WAS NOT MOVED** —
never move a tag a release has already run on. If it happens again, that is the
recipe.

⚠ **The lesson worth keeping: verifying the EXTRACTION is not reviewing the
NOTES.** Checking that the title carries its suffix, the body starts at
`### Fixed` and no link definitions leaked is mechanics. Nobody had read the
bullet as a user reads it until the maintainer asked, and by then it was
published. **Read the entry as its audience before promoting the section**, and
remember the audience is someone asking "was I affected?".

##### What `0.3.2` contained, and what it did not

**One user-facing fix: #453.** `read_only=True` on a `Select` was accepted and
ignored — the arrow greyed out so the field *looked* read-only while a click in
the text area still opened the list and changed the value, and
`select.read_only` read `True` for every `Select` ever built. The entry's ttk
`readonly` state was doing double duty as the widget's own "no free typing" flag
and was recomputed unconditionally, discarding the request. It is **derived,
never storage** now. `TimeField` rides the same internals and is fixed with it.

⚠ **#407 also landed since `v0.3.1` and deliberately has NO CHANGELOG entry** —
it is test-harness only, and an entry earns its place by being reachable. Do not
"fix" its absence.

##### ⚠ The two findings from this branch worth carrying — do NOT re-derive

**1. When a piece of state becomes DERIVED, every existing writer of it becomes
a silent no-op — and the writers outside the file are invisible.** Making the
ttk state an OUTPUT re-derived after every write killed `TimeField.read_only`,
whose setter wrote `state="readonly"` onto a `SelectBox` internal; the applier
wrote `['!readonly']` back over it inside the same call. `main` reported `True`,
the branch `False`. `grep -rn 'state="readonly"' src/` found all seven writers;
only `TimeField` wraps a select.

⚠ **Round 1 fixed that setter and MISSED THE CONSTRUCTOR, one scope up, doing
the identical write.** `bs.TimeField(read_only=True)` still came back freely
typeable with its time list open, because every existing test drove the setter.
**Round 2 found it. The lesson is that a fix to a property is not a fix to the
setting** — enumerate the ways the value can arrive (constructor, setter,
`configure`) and pin each.

**2. A docstring outlives its code, and the expensive half is not the obvious
one.** Two shipped in this branch. `select.py`'s `read_only` docstring carried
`cget`, `configure` and "a 5-tuple" into the **rendered API Reference** — Tkinter
vocabulary on a page describing a framework that exists to hide it. Worse,
`TimeField`'s constructor doc said read-only means *"the user must pick from the
dropdown"* — the pre-#453 reading, which the fix made **actively false**, on a
published page. ⚠ **The toolkit leak looks wrong to any reader; the stale
behavior looks authoritative.** Check both when a fix changes what an option
means, and verify in the BUILT html:
`grep -rlE "cget|instate|5-tuple|textvariable" docs/_build/html --include=*.html`.

⚠ **The `select.py` half REVERSED a round 1 decision, on the maintainer's
instruction** — round 1 had deliberately put that warning *in* the docstring so
the call would not be "simplified" back later. Right instinct, wrong surface: it
is for whoever edits the line, not whoever reads the docs, so it moved verbatim
into a `#` comment. **Do not put it back.**

##### Two review rounds ran, against a declared cap of 2

Record archived at **`development/review-453-select-read-only.md`**, plan at
**`development/plan-453-select-read-only.md`**. Yield **3 findings then 4**, plus
a fifth found during round 2's fix step. ⚠ **Round 2's fixes touched `src/`,
which gate 1 would read as a trigger for a round 3 — the CAP is what stopped it,
and the survivor was filed instead.** That is the stopping rule working; it is
the first branch where it bound.

**The survivor is [#455](https://github.com/israel-dryer/bootstack/issues/455)**
— `Field.enable()/disable()/readonly()` write the ttk readonly state without
re-deriving, merged with `PLAN.md`'s out-of-scope item that
`Field.readonly(False)` disables the field instead of clearing read-only.
**Latent: zero callers in `src`, `tests` or `development`**, and the public
`disabled` setter already routes through `_delegate_state`, which re-derives.
Left **unmilestoned** — it gates nothing, so its placement is a scope call.

**#383 gained a THIRD gap** ([comment](https://github.com/israel-dryer/bootstack/issues/383#issuecomment-5283453605)):
the two in its body are about bad **values**, this one is about unknown **names**
— `bs.TextField(bogus_xyz=1)` constructs silently while the internal
`Field(master, bogus_xyz=1)` raises `TclError`, so **the public layer is the
less strict of the two**. Mechanism measured: wrappers build `internal_kwargs`
from named parameters only and `**kwargs` exists to feed
`_split_layout_kwargs`, so leftovers are never read and never reach the internal.
⚠ **It does NOT reuse `validate_choice`** (the name never reaches a validator),
and the obvious home — the shared split seam — needs the wrappers that
legitimately forward `**kwargs` counted first.

**✅ #380 IS NO LONGER PAUSED — the measurement was taken on 2026-08-14 and PR
#451 is GREEN.** The two blocks marked ⏭ below are ANSWERED and are kept for
their reasoning only. See START HERE.

**✅ RESUME POINT 1 — ANSWERED 2026-08-14: Xvfb-only, the missing window manager
IS the bug.** Report at `development/report-447-linux-focus.md` (read its
CORRECTION header first). Original text follows, for the reasoning that framed
the question correctly.

**⏭ RESUME POINT 1 — the WSL agent's answer on #447.** A brief is committed at
**`development/handoff-447-linux-focus.md`**. It asks ONE question: does the
dialog focus/Enter cluster fail on X11 generally, or only under `xvfb-run`,
**which has no window manager at all**? `focus_lastfor()` returning the EMPTY
STRING is not "the wrong widget" — it is "nothing in this toplevel ever held
focus", which is what a missing WM produces. Xvfb-only means a one-line CI fix
and the product is fine; failing under a compositor too means **a product bug in
`0.3.1`'s dialog keyboard work on Linux**, a platform we publish for, invisible
to both boxes here.

**✅ RESUME POINT 2 — ANSWERED 2026-08-14: FIXED, not merged. PR #451 is green on
all five jobs** (run `31797591244`), both Linux legs included. **Merging it is
the next action.** The instinct recorded below was right and is worth keeping:
understanding Linux first is what turned a red leg into a one-step workflow fix
instead of a hunt through the dialog code.

**⏭ RESUME POINT 2 — then merge or fix PR #451.** It is open and deliberately
NOT merged: its CI is green on Windows, headless and docs, and **red on both
Linux legs** with the #447 cluster. Merging a red workflow trains everyone to
ignore it. The maintainer chose to understand Linux first (2026-08-12).

**STATE OF THE WORLD, so nothing below has to be pieced together:**

| | |
|---|---|
| `main` | **`c2ff50fb`**, pushed. Green. `0.3.2` is released from `c311a9c4`; the one commit after it is the CHANGELOG rewording, which is why `v0.3.2` and `main` differ |
| branch, PAUSED | **`ci/test-workflow-380`** (PR #451), pushed, head **`255c8a42`**. `PLAN.md` lives ON THAT BRANCH. **The only branch alive** |
| suite on `main` | **exit 0, 20 legs, 1229 passed / 21 skipped**, measured 2026-08-13 at `03d981f1`. Shared leg **1032 / 14 against 1045 selected** — `1032 + 13` runtime skips = 1045, the 14th being the collection-time skip that is summarized but never selected. **Everything on `main` since that commit is CHANGELOG, CLAUDE.md and the version bump, so the figure transfers** |
| suite on `ci/test-workflow-380` | **exit 0, 33 legs, 1449 passed / 22 skipped, 98s** — ⚠ **still SUSPECT, see below** |
| root of `main` | **NO `PLAN.md`, NO `REVIEW.md`** — archived to `development/` at `03d981f1`. **Create `PLAN.md` fresh for the next branch** |
| released | **`0.3.2` on PyPI, tag `v0.3.2`, shipped 2026-08-13 and fully verified.** `## [Unreleased]` is ABSENT again — the next fix commit re-creates it |
| open milestones | 10, and they agree 1:1 with the table below |
| `pandas` | **ABSENT on this box now**, so the data leg reads `125 / 4`. It read `123 / 6` on 2026-08-12. Documented environmental pair, not a discrepancy |

⚠ **`1208 → 1229` IS +21 EXACTLY, WHICH IS `test_select_read_only.py`.** That is
the whole delta and it reconciles against the shared leg's own collection line,
so nothing was silently dropped or skipped into passing. **Prefer a number you
just measured over one written here — this file has now been wrong about counts
seven times.** The check is one command:
`pytest tests/widgets/public tests/cli -m "not isolated" --collect-only -q | tail -2`.

⚠ **Round 1 of the #453 review recorded `33 legs` for a branch that has 20.**
33 is `ci/test-workflow-380`'s leg count; the passed figure it quoted was
consistent with the branch it was actually on, so it reads as a transcription
slip rather than a different checkout. **Recorded because a wrong leg count is
how a wrong total gets believed.**

⚠ **THIS RECONCILIATION RESTED ON THE WRONG BASE AND MUST BE RE-MEASURED BEFORE
IT IS QUOTED.** It read: `1250` + **25** tests under `tests/widgets/` that
`testpaths` never collected + **166** in `tests/test_public_surface.py`, which
had never run anywhere + **8** for `test_tk9_scaling_baseline.py`, which now
runs TWICE (once in the headless leg to prove it needs no display, once in the
shared leg as before) = `1449`. **The `1250` base is wrong — `main` was `1208`**
(corrected 2026-08-13), so the same three additions predict **`1407`**, not
`1449`. Either the branch total or one of the addends is off by 42. ⚠ **And the
base has MOVED AGAIN since: `main` is `1229` now that #453 landed, so the
prediction is `1428` against that.** Neither figure closes the gap; the point is
that the branch total was never reconciled. **Both halves need a fresh
`py -3.12 tests/run_gui.py` on `ci/test-workflow-380`, taken after rebasing it
on today's `main`; do not repair the arithmetic by picking whichever number
makes it close.** The
substance is untouched — the 25 and the 166 had literally never been executed by
any automated run, which is what #380 asked to fix.

##### ⚠ WHAT CI FOUND ON ITS VERY FIRST RUN (run `31591527788`)

| job | result |
|---|---|
| `headless` (no display, root creation BLOCKED) | ✅ |
| `tests` windows py3.13 | ✅ |
| `docs` `-W` | ✅ |
| `tests` ubuntu py3.12 **and** py3.13 | ❌ **7 failures, identical on both** |
| `tests` macos py3.13 | ⛔ **HUNG — 90 minutes for a 90-second suite** |

- **The Linux failures are the #447 cluster** — `focus_lastfor()` returning `''`,
  Enter reaching neither the focused button nor the default. Same shape measured
  at 4/50 on Windows and never explained. **This is the first near-deterministic
  reproduction the issue has ever had.** See RESUME POINT 1.
- ✅ **#432 DID NOT REPRODUCE.** The Linux leg **ran all 33 legs to completion**
  and reported normally — it did not exit silently mid-run. #407 appears to have
  removed it. **#432 should be closed or re-scoped on this evidence**; it was the
  blocker on this whole workstream.
- ⛔ **The macOS hang is [#452](https://github.com/israel-dryer/bootstack/issues/452).**
  Setup and the Tk-version report both succeeded, then the suite never returned.
  #380 had flagged Tk-on-Aqua as unverified on GitHub runners; that is answered.
  **The leg is REMOVED from the matrix** rather than left hanging, and **every
  job now sets `timeout-minutes`** — without them that hang would have burned to
  GitHub's 6-hour default. ⚠ **Step 3 of #452 first: does a bare
  `tkinter.Tk()` even complete on the runner?** That control decides how the
  rest reads.
- ⚠ **One more Linux failure is deliberately NOT filed yet:**
  `test_appshell_shortcuts::test_bare_b_does_not_toggle_the_sidebar`
  (`assert '' == 'b'`). It is focus-shaped too, so it may share #447's cause;
  filing now risks a duplicate the WSL run would immediately merge.

⚠ **`REVIEW-PROTOCOL.md` GAINED A `Stopping rules` SECTION ON 2026-08-12 — READ
IT BEFORE ANY REVIEW.** Four mechanical gates, written because this project spent
four review rounds on the `0.3.1` branch and round 4 reviewed a **test-only**
commit whose fixes would have earned a round 5. The one that bites first: **a
round is triggered by a non-empty `git diff <range> -- src/` and by nothing
else.** #407 was its first application and opened **zero** rounds against a
declared cap of 2.

**#380 IS IN FLIGHT, NOT PENDING** — PR #451, branch `ci/test-workflow-380`. It
became affordable because #407 took the suite from ~5 minutes to ~1. The
workflow is written, verified locally, and has run once; what is left is the
Linux question above, not more authoring.

⚠ **DO NOT DESIGN #380 FROM SCRATCH. `D:\Development\ttkbootstrap` HAS ALREADY
SOLVED IT** (maintainer's pointer, 2026-08-12). Same maintainer, same shared-root
design, and its `tests/conftest.py` says outright that it followed bootstack's
approach. Its `.github/workflows/ci.yml` is close to a drop-in answer:

- a matrix of **ubuntu / windows / macos** plus the **floor Python** from
  `pyproject.toml`, with **`fail-fast: false`** and the reason written into the
  file — a green Linux run was once read as a green suite while Windows was red;
- **`xvfb-run -a -s "-screen 0 1280x1024x24 -dpi 96"`** on Linux only, with a
  comment explaining the `-dpi 96`: Xvfb otherwise reports ~100 dpi, a real ~1.05
  scaling factor, too small to hit the quarter-step snap and large enough to
  round asset geometry up a pixel;
- a per-job step that **REPORTS the Tk build** (`tcl=… tk=…`) rather than
  letting anyone infer it from the Python version;
- `concurrency` with `cancel-in-progress`, and a separate `-W` docs job;
- an optional dependency **deliberately not installed**, so the fallback path is
  the one under test.

⚠ **One idea there is worth stealing into `conftest` regardless of CI:** it pins
Tk scaling to baseline in the fixture, which "demotes CI's `-dpi 96` from
load-bearing to belt-and-braces." bootstack has pixel-exact tests too, and a
developer's laptop at 125% is the same hazard. **Not done — its own change.**

**⏭ AND RE-TEST #432 BEFORE SCOPING IT.** The shared-root GUI leg exiting
silently mid-run on Linux was most likely the widget accumulation #407 has now
removed. **It may simply not reproduce.** Neither box here can check that;
it needs a Linux run, which is also the first thing #380's Linux leg would tell
you.

##### ⏭ BRIEF FOR THE macOS BOX — #452, the runner hang

**The job:** CI now covers ubuntu and windows and **not macOS**, because the leg
ran **90 minutes for a 90-second suite** and was removed rather than left
hanging. aqua is a platform this project publishes for and it is now the only one
with zero automated coverage, so the value of #380 is capped until this closes.

**What is already known, so it is not re-derived:**

- Setup and the Tk-version report both **succeeded**; then "Run the suite" never
  returned. So Python and Tk installed fine — it is not a provisioning failure.
- **Every job now sets `timeout-minutes`**, so a retry costs 15 minutes rather
  than GitHub's 6-hour default. That was added in `5921dc41` precisely so this is
  affordable to iterate on.
- #380 had already flagged Tk-on-Aqua as **unverified** on GitHub runners. That
  is now answered in the negative, at least as the suite currently runs.

**⏭ STEP 1, AND IT DECIDES HOW EVERYTHING ELSE READS: does a bare
`tkinter.Tk()` even complete on the runner?** Not the suite — one root, one
`update()`, one `destroy()`, with a timeout. A hang there means aqua needs
something a headless runner does not give it (a window server session), and the
answer is a different runner configuration rather than anything in the suite. A
pass there means the hang is ours, and the next step is bisecting which leg
blocks.

⚠ **This is debug-by-push and there is no way around it** — no box this project
has is a GitHub macOS runner. Budget for that: make each push answer one
question, and write the question into the workflow step name so the log reads as
an experiment rather than a rerun.

⚠ **The local macOS box is NOT a substitute and will mislead you.** It has a
window server, a logged-in session and Tk 8.6; the runner has none of the first
two. **The whole #447 lesson transfers: a display without the thing that manages
windows behaves differently from one with it, and the difference is invisible
until measured.** If the local box passes, that is not evidence about the runner.

⚠ **#431 is waiting on a macOS answer too** and is cheap to fold in — its fix
skips on aqua, and nobody has *observed* that branch being taken on a real Aqua
build. See the ⚠ under the unmilestoned list.

##### ✅ `0.3.1 — Dialog keyboard and modality` IS ON PyPI (2026-08-12)

Tag `v0.3.1`, **`release.yml` ran clean** (build, publish, release all green) and
`docs.yml` chained off it. **Every post-release step is done and VERIFIED, not
assumed:** PyPI proved with a real `pip download` of the wheel (never the
CDN-cached summary endpoint), the shipped wheel opened and **imported with
`idlelib` BLOCKED via a `meta_path` finder, with a control asserting the block
was real** (#430's defect — grep is not enough, seven `idlelib` mentions survive
in the wheel as docstring attributions), `WidgetRedirector` confirmed as
bootstack's own module, `NOTICE` present at `dist-info/licenses/` with the PSF
attribution, the GitHub Release live with both assets, and `bootstack.org`
returning 200.

⚠ **A CHANGELOG WORDING FIX LANDED AFTER THE TAG, so the two disagree by design.**
`v0.3.1` carries the pre-fix text; `main` carries the corrected text; the
**GitHub Release body was edited to match with `gh release edit --notes-file`**,
keeping the auto-generated `## What's Changed` tail. **The tag was NOT moved** —
never move a tag a release has already run on. If this happens again, that is
the recipe.

✅ **`0.3.1`'s MILESTONE IS CLOSED** (maintainer, 2026-08-12), reading
`open=0 closed=5`. **#446 was CLOSED rather than moved**, because its scope was
exactly the two flakes and both shipped in `48dba181`; the third became #447.
Anything unfinished went to **`0.3.x — Patch line`** — #447 and #449 — which is
consistent with #422 already sitting there, so a test-only issue on the patch
line is not a new precedent.

**PR [#448](https://github.com/israel-dryer/bootstack/pull/448) is MERGED** —
merge commit **`d307fd2e`**, a **merge commit, not a squash**, the same call made
for #410/#423/#424/#442. Branch head at merge was **`ba27ab58`**;
`fix/dialog-keyboard-modality` is **DELETED** local and remote (that SHA is the
one to resurrect from). Verified both ways before merging:
ancestor of `origin/main` **and** a MERGED PR. **#426, #439, #440 and #441 are
all CLOSED.**

⚠ **`main`'s only difference from the commit the suite was measured at
(`ba27ab58`) is `CLAUDE.md`** — four `docs(claude):` commits landed while the
branch was out. Docs-only, so the counts below transfer to `main` exactly.

**`PLAN.md` and `REVIEW.md` ARE ARCHIVED** to
`development/plan-426-439-440-441-dialogs.md` and
`development/review-426-439-440-441-dialogs.md`. **The root is deliberately empty
of both — create `PLAN.md` fresh for the next branch.**

##### ⚠ THE DURABLE OUTCOME OF THIS BRANCH IS NOT THE FOUR FIXES

**`REVIEW-PROTOCOL.md` now has a `Stopping rules` section, and it exists because
the loop on this branch did not terminate on its own** (maintainer, 2026-08-12:
*"you can create endless cycles of tests, bugs in tests etc... A test is meant
for assurance. It's important, but at the same time, it is not the product."*).
Round 3 reviewed a production fix; round 4 reviewed the **test-only** commit that
fixed the flakes round 3's verification surfaced; round 5 would have reviewed the
fixes to those tests. **The measured shape: ~430 production lines against ~1,300
test lines and ~750 lines of probes and review records, over 17 commits of which
4 are review records. Rounds 3 and 4 changed ZERO lines under `src/`.**

The four gates, all mechanical because a rule needing judgment gets reasoned
around exactly when it should bind:

1. **A round is triggered by a non-empty `git diff <range> -- src/`, and by
   nothing else.** Test-, probe- and docs-only commits are self-checked. Under
   this gate round 4 would not have opened.
2. **Test code is reviewed on ONE axis — what defect can it let through.** Only
   **vacuity** (passes while the behavior is broken) and **false alarm** (fails
   while it is fine) are actionable. Diagnostics, wording, symmetry and probe
   ergonomics are **notes in the record, never fixes**. Under this gate round 4
   yields 2 findings, not 5.
3. **The round cap goes in `PLAN.md` up front** — 2 for a patch, 3 for a minor —
   and survivors are filed as issues.
4. **Probes are instruments, not reviewed code**, and a flake gets **one** fix
   attempt with a mechanism-reproducing control before quarantine. The one
   exception: a probe whose *conclusion* is cited as settled must still be shown
   capable of finding something — a claim about evidence, not code quality.

##### ✅ Round 4 RAN, and the branch closed there

**#446's two flakes were FIXED at `48dba181`** (test-only — `src/` untouched,
verified not assumed). Round 4 reviewed that diff and found **two vacuity
defects, both fixed in `74991e55`**, plus three notes left unfixed under gate 2.
**A third flake is still open and is now [#447](https://github.com/israel-dryer/bootstack/issues/447)** — filed rather than
chased, under gate 4.

| flake | file | before | after |
|---|---|---|---|
| A `test_the_restored_grab_is_the_same_KIND_it_was` | `test_dialog_nested_modality.py` | 1 in 12 | **fixed** |
| B `test_query_dialog_focuses_its_entry_not_the_default_button` | `test_dialog_initial_focus.py` | 1 in 8 | **fixed** |
| C `test_enter_on_a_disabled_button_still_reaches_the_default` | `test_dialog_press_contract.py` | not seen in 12 | **1 in 37, UNEXPLAINED** |

⚠ **NEITHER FIXED FLAKE HAD THE CAUSE THIS FILE PREDICTED, and the leaked-timer
prediction was WRONG rather than merely incomplete.** It was measured first and
refuted — `probe_446_leaked_after_jobs.py` shows no test-scheduled timer survives
a test. **A named prior is a hypothesis, not a diagnosis**, which is the opposite
of what the previous version of this block said ("both have a named prior with a
worked fix, so neither should need re-deriving").

- **Flake A was a FIXED DELAY where the other files poll.**
  `test_dialog_nested_modality.py` drove on `after(300, drive)`. `show()` creates
  the toplevel, builds the footer and content, positions the window, and only
  **then** grabs — and building and positioning both pump the event loop, so the
  timer fires mid-`show()`, the driver destroys the toplevel, and `show()`
  deiconifies a window that is gone. **The grab is the barrier because it is the
  last thing `show()` does before it waits.** Forced 10/10 → 0/10 in
  `probe_446_fixed_delay_lands_mid_show.py`, against 0/10 for the same fixed
  delay in a quiet process.
- **Flake B was a barrier SCOPE error, not a timing one.** `_drive` waited for
  the grab and for every **footer** child to map — correct where the widget under
  test is a footer button, useless here, where it is `QueryDialog`'s entry in the
  **content** subtree. Measured 4/12 unmapped at the old barrier and the same
  4/12 focus misses, tracking one-for-one → **0/12** once the barrier waits for
  the resolved focus target (`probe_446_barrier_scope.py`).

⚠ **FLAKE C IS THE OPEN QUESTION AND MUST NOT BE CLOSED BY RE-RUNNING.** Enter on
a disabled footer button reached **neither** it nor the default button
(`calls == []`), which reading the guard cannot explain — `_key_was_consumed`
returns `not instate(["disabled"])`, i.e. False, for a disabled button. It does
not reproduce in a quiet process (**0/40**,
`probe_446_disabled_button_enter.py`, already instrumented to separate "the
toplevel binding never ran" from "it ran and `invoke()` did nothing"), and 25
instrumented runs did not catch it again. **Whether the timing change in the fix
exposed it is UNKNOWN** — it appeared once in 37 post-fix runs and zero times in
12 pre-fix runs, which is too little to attribute either way. Record it as
unknown; do not let a later session inherit a guess as a fact.

⚠ **THE LESSON, and it is the same one `0.3.0` round 4 paid for: `run_gui.py`
EXIT 0 IS NOT EVIDENCE OF STABILITY.** The branch reported **1208 passed / 21
skipped, exit 0, all 20 legs**, plus a clean `-W` docs build — and had two flakes
then and one now. At 1-in-8 a full green run is the *expected* outcome of a
broken branch. **Do not re-run to check; re-running is how all three of these
hid.** The #437 control is the pattern: a probe that **CREATES** the condition
and reports a rate, not one that looks for the symptom. Both #446 fixes were
accepted on exactly that evidence, and flake C is unresolved precisely because
nothing has yet made it happen on demand.

**Reproduction is in #446** — the five dialog files in one pytest process, eight
or more times. `git diff main...HEAD -- CLAUDE.md` is empty and must stay that way.

⚠ **THE COUNTS THIS BLOCK RECORDED FOR `48dba181` WERE WRONG — see the corrected
table under `main` is GREEN.** It claimed **1250 / 22** summed and a shared leg
of **1055 / 13** against a **1068** ceiling, and dismissed round 3's `1011 / 14`
against `1024` as the irreconcilable one. **Round 3 was right**; the real figures
are **1208 / 21** summed and **1011 / 14** against **1024**, derived 2026-08-13
by measuring a later branch and subtracting the only test file added since.

⚠ **The reasoning that produced the wrong number is the part worth keeping,
because it looked airtight:** `1055 + 13 = 1068` reconciles against its own
collection line, which this file treats as the check that settles a disputed
count. **It does not.** Self-consistency proves the run summed correctly, not
that it selected the right population — a wrong ceiling reconciles just as
neatly as a right one. Bound the movement instead:
`git diff --stat <baseline>..HEAD -- tests/` says how much the count is ALLOWED
to have changed, and it is one command.

**⏭ SO THE NEXT JOB IS THE RELEASE** (top of this section). After it: the
standing recommendation is `Test and release confidence`, and **#432 is the
blocker to attack first** — the shared-root GUI leg exits silently mid-run on
Linux, which makes CI unbuyable — then #407, then #380. **#447 is filed and can
wait**; #444 and #445 likewise.

**FOUR REVIEW ROUNDS RAN. The full record is
`development/review-426-439-440-441-dialogs.md` — read it rather than
re-deriving.** The yield curve is the part worth carrying:

| round | findings | real | what it cost |
|---|---|---|---|
| 1 | 6 | 3 | 2 refuted by measurement, 1 deferred by the maintainer |
| 2 | 5 | 5 | **all five were round 1's own fix being incomplete** |
| 3 | 4 | 1 | **three were already-triaged items re-filed** |
| 4 | 5 | 2 | **reviewed a TEST-ONLY diff; 3 findings were about a probe's readability** |

⚠ **The old note here said "STOP AT THREE" and blamed a harness gap. That was
half the story and the missing half is now `REVIEW-PROTOCOL.md`'s gate 1.**
Carrying triage state into the reviewer is still right — round 2's reviewer was
handed `REVIEW.md` and re-filed nothing, round 3's was not and re-filed three
settled items. But no amount of triage state stops a round that should never
have opened, and round 4 opened on a diff with **no production code in it at
all**. Gate the round on `git diff -- src/`; triage the findings inside it.

⚠ **Round 4's two real findings were both VACUITY, and the control is worth more
than either fix.** `_nest` in `test_dialog_nested_modality.py` gave up silently
when its barrier never cleared — so nothing was ever nested, the outer grab was
never displaced, and both nesting tests passed measuring nothing. `_outer`'s
error path was unreachable for a different reason: its retry budget ran to
10050ms while its fallback fired at 10000ms, so the fallback always won, `state`
was left empty **with no `"error"` key**, and `assert "error" not in state`
passed. **THE FIRST CONTROL WAS WRONG AND LOOKED RIGHT**: disabling the retry
budget left the test passing, because the inner dialog already held the grab on
the very first check, so the give-up path was never reached. Forcing the
condition itself (*"pretend the grab never arrives"*) is what exercised it —
**pre-fix the test PASSES in 8.83s**, having sat through the entire 8-second
fallback and nested nothing; post-fix it fails naming both routes. **A control
that does not reach the path under test is indistinguishable from a fix that
works.**

⚠ **One claim was DOWNGRADED rather than fixed, and it matters because this file
recorded it as settled.** `probe_446_leaked_after_jobs.py` returns an empty set
on both sides of every test if `_root()` is `None` or `after info` raises —
indistinguishable from a clean result. So **"no test-scheduled timer survives a
test" is UNCONTROLLED, not refuted.** The probe was left alone under gate 4; the
claim it backs was weakened in the record instead.

⚠ **`probe_446_disabled_button_enter.py` COUNTS A BARRIER TIMEOUT AS A
REPRODUCTION** — a run where the dialog never comes up yields `calls == []` with
no other keys, byte-identical to flake C, and the probe's own READING text then
points at the guard when the truth is that Enter was never pressed. **Fix that
before working #447**, or the probe will lie about the exact distinction the
issue turns on. Recorded on the issue too.

⚠ **Round 3's one real finding was OUT OF SCOPE and is filed, not fixed —
[#444](https://github.com/israel-dryer/bootstack/issues/444).** A modal
`bs.Window` never restores the grab it took, so a dialog underneath it loses its
modality. Reproduced (`outer holds grab: True` → `after inner closed: None`).
**Pre-existing in `0.2.3` and `0.3.0`, and `_runtime/toplevel.py` is not in this
branch's diff** — #440 was scoped to the four dialog classes. ⚠ **The reviewer
also claimed the CHANGELOG says this is fixed; that was CHECKED and is FALSE** —
the #440 bullet scopes itself to dialogs and its `modal="app"` sentence is about
restoring a grab's *kind*. Nothing false ships. Agents over-flag; that is the
shape it takes on a finding that is otherwise sound.

⚠ **[#445](https://github.com/israel-dryer/bootstack/issues/445) filed the same
way:** `attach()` drops legacy layout kwargs on a grid cell while rejecting them
on a flex child. Pre-existing, one-liner now that `kind` is required. Both are on
`0.3.x — Patch line`.

**#441's scoping constraint held: the fix stayed INTERNAL.** The issue floated
letting a widget *declare* it consumes Enter — new public surface, which would
have pushed the whole thing to a minor. The shipped rule asks the bindtag **and
the keysym**, both internal.

⚠ **The keysym half was round 1's F1, refuted, then RE-OPENED ON COST rather than
on new evidence.** Round 1 documented it as an unmeasurable X11 limit; round 3
pointed out the remedy is one argument, weighed against shipping a branch that
changes X11 behavior on a platform neither box can test. **Measured before
changing anything — the asymmetry is one-sided:**

```
TButton  <Key-Return> -> button_default_binding   <Key-KP_Enter> -> button_default_binding
Text     <Key-Return> -> tk::TextInsert           <Key-KP_Enter> -> '# nothing'
```

So a button answers both Enter keys and a text widget answers only `Return`.
⚠ **The test is `keysym != "KP_Enter"`, NOT `== "Return"`, deliberately** — an
unknown keysym then reads as consumed, because standing down wrongly costs a dead
key while firing wrongly costs **#441 itself**. Pinned by its own test so it is
not "simplified" into the equality form later. ⚠ **Windows can reach this path by
NEITHER route** (synthesis yields keysym `??`; the physical key folds into
`Return`), so the tests drive the rule directly and only X11 can run it end to
end.

After `0.3.1`, the standing recommendation is still `Test and release confidence`
(#407 then #380) — and **#432 is the blocker to attack first**, since the GUI leg
cannot complete on Linux at all, which makes CI unbuyable.

**⏭ A DESIGN IDEA WORTH CARRYING INTO THAT BRANCH (maintainer, 2026-08-11): map
the real keys onto a virtual name with `event_add`**, so a dialog binds one
`<<Submit>>` instead of `<Return>` + `<KP_Enter>` and the intent becomes
targetable. **Measured before it gets designed around —
`development/probe_439_virtual_event_for_submit.py`, and it needs a MAPPED
window or every arm silently reads empty:**

- ✅ **It works.** `root.event_add("<<Submit>>", "<Return>", "<KP_Enter>")` and a
  `<<Submit>>` binding fires from the real key. One name covers both keys, which
  is exactly the duplication the dialog carries today.
- ⚠ **On a tag carrying BOTH, the PHYSICAL binding wins and the virtual one does
  not run at all.** Measured: with `<<Submit>>` and `<Return>` both bound to the
  widget, only `<Return>` fired. So this is not additive — anything already
  binding `<Return>` directly shadows the virtual name on its own tag.
- ⚠ **The mapping is per-INTERPRETER, not per-widget** (`event info` reads the
  same through the root and through a widget). Adding one is a cross-cutting,
  app-wide change, not a local one.
- ❌ **It does NOT change the bindtag walk.** Order stayed
  `widget → class → toplevel`. So the toplevel still runs after a button's class
  binding and still has to decide whether something already answered the key —
  **#441 is untouched by this.** It is a naming and deduplication win, not a
  dispatch one; adopt it for clarity if wanted, but do not scope #441 around it.

⚠ **#436 was filed 2026-08-10**: adopt `versionadded` across the public API,
because the docs site serves ONE version and a reader cannot tell which release
an API needs. `capture()` is already tagged on its branch as the first case. It
carries one undecided question — whether `versionchanged` gets applied
retroactively to `0.2.0`–`0.2.3` or stays forward-only.

Verified, not assumed:

- **PyPI** — `0.2.3` live, wheel + sdist, proved with a real
  `pip download --no-deps bootstack==0.2.3`. ⚠ The **`/pypi/bootstack/json` summary
  endpoint is CDN-cached and lagged behind a successful `0.2.2` upload** — use
  `/pypi/bootstack/<version>/json` or a real `pip download`, and never read a stale
  summary as a failed upload and re-upload.
- **The fix, inside the published wheel** — `from idlelib` is gone from the shipped
  `filter.py`, and `NOTICE` is present at `dist-info/licenses/NOTICE` carrying the
  PSF attribution. **Checking the artifact, not the source tree, is what proves a
  packaging-shaped bug is actually fixed** — #430 was reported against the shipped
  `0.2.2` wheel in the first place.
- **GitHub Release** — [`v0.2.3`](https://github.com/israel-dryer/bootstack/releases/tag/v0.2.3),
  titled `0.2.3 — Import without IDLE`, both artifacts, not a draft, not a
  prerelease.
- **Docs** — deployed automatically, `http://bootstack.org/` returns 200 (run
  `31274654592`, chained off the successful Release run).
- **Issue** — #430 CLOSED, milestoned `0.2.x — Patch line`, "it's live" comment
  posted ([5227773487](https://github.com/israel-dryer/bootstack/issues/430#issuecomment-5227773487)).
- **Branch** — `fix/idlelib-import-430` deleted local + remote (head `57ee3041`),
  verified merged with the two-command check before deleting.

**⚠ `release.yml` RAN CLEAN for `v0.2.3`** — build, PyPI publish, and GitHub Release
all green, and `docs.yml` chained off it automatically. Actions had recovered from
the 2026-08-06 outage. **The manual recipe below was NOT needed and is kept only as
the fallback for next time.**

##### ⚠ THE FALLBACK, FROM `0.2.2`: publishing BY HAND when Actions is down

`release.yml` **never ran successfully for `v0.2.2`.** GitHub Actions was in a
**major outage** all afternoon (incident opened 15:22 UTC, still *investigating* at
19:43 UTC — "capacity remains constrained and jobs may still be delayed or fail").
Two tag-triggered runs died without publishing anything:

| run | what happened |
|---|---|
| `31115122262` | failed twice; `Failed to resolve action download info: Service Unavailable` — GitHub could not hand the runner its actions. Bound to a tag object that no longer exists. |
| `31121469892` | `Build distribution` sat **queued 15 minutes then was CANCELLED**; publish + release **skipped**. A rerun re-queued and never started. |

⚠ **`gh run` reported this run inconsistently** — `gh run cancel` said *"Cannot cancel
a workflow run that is completed"* while `gh run view` said `queued`, repeatedly. Under
an Actions outage the run state itself is unreliable; **check PyPI, not the run**, to
decide whether anything was published.

**So it was published manually**, which worked cleanly and is the fallback to reuse:

1. `git worktree add <scratchpad>/rel-X.Y.Z vX.Y.Z` — build from a **pristine checkout
   of the tag**, never from the working tree. This repo has ~60 untracked files in
   `development/`; building in place risks them landing in the sdist. (Verified they
   did not: sdist top level is `src`, `tests`, `LICENSE`, `NOTICE`, `MANIFEST.in`,
   `PKG-INFO`, `README.md`, `pyproject.toml`, `setup.cfg`.)
2. `py -3.12 -m pip install --upgrade build twine` (neither was installed).
3. `py -3.12 -m build`, then **`py -3.12 -m twine check dist/*`** — both PASSED.
4. `py -3.12 -m twine upload --config-file D:/Development/bootstack/.pypirc --non-interactive dist/*`
5. `gh release create vX.Y.Z dist/* --title "<from release_notes.py>" --notes-file RELEASE_NOTES.md --generate-notes`
6. `git worktree remove <path> --force`

⚠ **`twine.exe` is NOT on PATH** — always `py -3.12 -m twine`.

⚠ **The token lives at `D:\Development\bootstack\.pypirc`** (repo root, **not**
`~/.pypirc`, which does not exist). It is `[pypi]` + `username = __token__` + a
179-char `pypi-AgEI…` token. It is **gitignored at `.gitignore:29` (`/.pypirc`) and
untracked** — verified, safe. Because it is not in the home directory, **twine needs
`--config-file` explicitly** or it will not find it.

⚠ **A manual publish SKIPS THE DOCS DEPLOY.** `docs.yml` triggers on
`workflow_run` of **"Release" completing successfully** — no successful Release run
means no docs, silently. Its three runs that day all read `completed/skipped`, which
looks like a no-op but meant the site was still serving `0.2.1`. Fix is one command:
**`gh workflow run docs.yml --ref main`** (the workflow has a `workflow_dispatch`
trigger and its `if:` explicitly allows it). It succeeded in ~2 minutes even mid-outage.

⚠ **`release.yml` publishes via OIDC trusted publishing**
(`pypa/gh-action-pypi-publish` + `id-token: write`), so there is **no token in CI** —
the local `.pypirc` is the only credential path for a manual publish, and CI's path
cannot be reproduced locally.

⚠ **If run `31121469892` ever does execute**, its publish step will fail with *file
already exists*. **That is expected and harmless** — PyPI already has the correct
artifacts. Do not "fix" it by re-uploading or burning a version.

##### ⚠ The CHANGELOG said the wrong thing about click order — FIXED at `931edd89`

The `0.2.2` notes claimed a double-click runs `on_row_click` twice **before**
`on_row_double_click`. **It does not.** `on_row_click` rides `<ButtonRelease-1>` while
`<Double-1>` is a **ButtonPress** pattern, so the double lands *between* the clicks.
Measured, with a control:

```
claimed:  ['click', 'click', 'double']
actual:   ['click', 'double', 'click']      <- same shape as Win32's DOWN, UP, DBLCLK, UP
```

It matters practically: **one `on_row_click` fires AFTER the double-click handler has
already run**, so a click handler that moves the selection lands after the double-click
opened a dialog. The earlier session measured *counts* (2 clicks + 1 double) and never
checked *order*; the wrong ordering survived a rewrite of that same line hours earlier.

⚠ **The probe was junk on its first run and said so loudly** — it reported
`['double','click','double','click']`, claiming `double` on the very first press.
**Synthesized events default to `time=0`, and Tk decides `Double` off the event
clock**, so the preceding control click was indistinguishable in time. Supplying an
explicit `time=` to `event_generate` fixed it. Probe with both the control and the
clock: `development/probe_421_click_order.py`.

**A click count on `RowEvent` was considered and DROPPED** (maintainer, 2026-08-06) —
do not re-propose it. DOM has `event.detail` and AppKit has `clickCount`, and either
would let a handler early-return on the second click, but the maintainer is not
worried about it. It would have been new public surface, so a minor, not the patch line.

**⚠ DO NOT TOUCH A BRANCH WHILE A REVIEW RUNS.** This was violated on 2026-08-06: a
branch was handed off and then edited in place while the agent ran. The review reads
files on disk, not only `git diff`, so it reviews a moving target. If follow-up work
cannot wait, do it in a **`git worktree`** or on another branch. Memory
`feedback_dont_touch_branch_under_review`. ⚠ **And a worktree runs against `main`'s
source unless you set `PYTHONPATH`** — the editable install points at
`D:\Development\bootstack\src`, so a worktree's tests import *main's* code. The #421
review hit this; it happened to hand it a free pre-fix control, but it silently
invalidates a post-fix run.

⚠ **`PYTHONPATH` ALONE IS HALF THE FIX, AND THE HALF-FIX IS LOUD — WHICH IS THE
ONLY REASON IT GETS CAUGHT.** Setting `PYTHONPATH` to the worktree's `src` while
passing **test paths relative to the primary checkout** runs the NEW tests against
the OLD source. Measured 2026-08-11: 9–10 failures on every one of eight runs,
where the honest answer was 1 in 8. **Pass the worktree's ABSOLUTE test paths too**
(pytest then picks up its `conftest.py`), and prove which tree you loaded before
trusting a single number:
`PYTHONPATH=$W/src py -3.12 -c "import bootstack,os;print(os.path.dirname(bootstack.__file__))"`.
The failure mode is friendly here only by luck — a version skew that happened to
break loudly. Skew that breaks quietly reads as a real result.

**⚠ AND CHECK `git rev-parse` ON BOTH BRANCHES BEFORE READING ANY FILE.** These two
branches were briefly at the *identical* commit, so a branch name did not tell you
which code you were looking at — reading `tableview.py` would have silently shown
421's work-in-progress while you believed you were on 417. The 2026-08-06 review
caught this itself and reviewed committed blobs (`git show <sha>:<path>`) instead.

##### What shipped in `0.2.2` — commit map (both branches now merged and deleted)

`fix/datatable-click-focus-421` was **stacked on** `fix/datatable-double-click-417`.
All of these are on `main`; the branch column records which PR carried them
(**417** → #423, **421** → #424). Three later commits — `5d169044`, `9e257368`,
`62950b0a` — applied the #421 review findings on top.

| SHA | Branch | What |
|---|---|---|
| `aeffa27d` | 417 | #417 — `<Double-1>` bound unconditionally |
| `638b24e3` | 417 | #420's guard on `_on_row_double_click` (commit says `#417`; re-cited later — history reads oddly, notes are correct) |
| `701cea54` | 417 | #418 — the same guard on `_on_row_context` |
| `14808981` | 417 | #419 — deferred chevron refresh |
| `36ae3720` | 417 | CHANGELOG: chevron bullet, `#420` re-citation, `### Changed` |
| `69f92b05` | 417 | probes + `demo_419_group_chevrons.py` |
| `6718de36` | 417 | **fixes two defective tests** — see below |
| `f7405d97` | 417 | CHANGELOG: the double `on_row_click` bullet |
| `f425430f` | **421** | **#421 — `_take_click_focus` on the two `'break'` paths** |
| `ff814b85` | **421** | CHANGELOG bullet for #421 |
| `6c18d34e` | **421** | the 417 review record into `development/` |

##### ⚠ What the 2026-08-06 review established — do NOT re-derive

Full record committed at **`development/review-417-double-click.md`**. Verdict was
ship-ready. It verified, and these should not be re-checked:

- **The `iid not in self._row_map` guard is exact.** Group parents go only to
  `_group_parents`; data rows only to `_row_map`. All four `_tree.insert` sites were
  enumerated.
- **No binding accumulation** from the unconditional `<Double-1>` — `_build_tree`
  runs once and the bind has no `add=`.
- **The deferred chevron refresh is safe after teardown** — scheduled on
  `self._root()`, and every `item()` call is inside `try/except`.
- **`_update_selection_markers` does not clobber chevrons** — selection markers are
  inactive whenever `_group_by_key` is set. A suspected conflict, chased and closed.

**All six of its findings are handled.** Findings 1–4 landed in `6718de36` and
`f7405d97`; finding 5 became **#422**; finding 6 needed no action.

##### ⚠ THE LESSON WORTH KEEPING: that review MISSED two real defects

It called the tests "better than the repo average". **Two of them were broken**, both
found afterward by running the control the committing session should have run —
*revert the fix, confirm the test fails*:

- **`test_group_chevron_tracks_double_click` was VACUOUS** — it passed against the
  unfixed code. The setup started collapsed, so the double-click's two toggles
  finished on a *collapse*, the direction that was never broken.
- **`test_group_chevron_tracks_keyboard_expand` was FLAKY**, ~1 run in 5, its own
  control tripping. It synthesized key events, and those are dropped once earlier
  tests fill the shared root and the table is unmapped.

**The standing rule is that agents over-flag. This one under-flagged, on exactly what
it praised.** Adversarial verification cuts both ways — a clean review is not proof.

##### Measured facts worth not re-deriving

- **A double-click also fires `on_row_click` TWICE** (measured 2 clicks + 1
  double-click, against a 1/0 single-click control). `<ButtonRelease-1>` has no
  `Double` counterpart. Documented in the CHANGELOG; no test covers the interaction.
- **The toolkit reports an expand BEFORE recording it.** `ttk::treeview::OpenItem`
  generates `<<TreeviewOpen>>` and *then* sets `-open true`; `CloseItem` sets first.
  That asymmetry is the whole of #419. Verified from `info body`, not from memory.
- **Tk REJECTS `event_generate("<Double-1>")`** — `Double` is a binding pattern, not
  an event type. Two presses is the only way to synthesize one.
- **Do not synthesize keys in the shared-root suite.** Drive the routine the key is
  bound to (`ttk::treeview::ToggleFocus`, `ttk::treeview::Keynav w right`). The
  key-to-routine mapping is the toolkit's binding table, not ours.
- **Assert focus via `focus_lastfor()`, not `focus_get()`** — the latter reports
  nothing unless the window is active, which is not dependable here.
- **Probes must stub `_open_form_dialog` AND the row menu** — both block the loop
  forever when driven synthetically.
- Four probes and a visual demo are **committed** in `development/`:
  `probe_group_header_chevron_sync.py`, `probe_021_allow_edit_group_header.py`,
  `probe_group_header_click_focus.py`, and `demo_419_group_chevrons.py` (a
  seven-step manual checklist covering all five issues). Each probe carries a control.

##### ⚠ What the #421 review established — do NOT re-derive

Full record at **`development/review-421-click-focus.md`**. Verified, and not worth
re-checking:

- **#421's two new tests are NOT vacuous.** Run against unfixed source both fail with
  the right symptom (`focus_lastfor()` is the App root, not the tree), and test 1's
  internal control arm — clicking a plain data row — passes. This is exactly the
  control the #417 review skipped, which is how two defective tests got through there.
- **Suite green at the head.** 973 passed / 13 skipped (widgets+CLI) and 123 / 6
  (data), matching the `ff814b85` figure. The previously-flaky
  `test_group_chevron_tracks_keyboard_expand` passed on both of two runs.
- **The group-header focus question is CLOSED — it is a non-issue.** Tk's `<space>` is
  `ttk::treeview::ToggleFocus` → `Toggle $w $item`, which toggles the item's *open
  state*, not selection. Measured after a group-header click: `tree.selection()` is
  `()`, `table.selection` is `[]`, no `SelectionChange`. Item focus on a group header
  cannot leak into selection.
- **`_tree.focus` is read nowhere else in the `tableview` package** — nothing
  downstream assumes the focus item is a data row.
- **Taking focus on an empty-space click is not a regression** — ttk's own `Press`
  does `focus $w` unconditionally.

##### ✅ The three #421 review findings — ALL APPLIED 2026-08-06, nothing left here

Kept only because the measurements are worth not re-deriving. Landed as `5d169044`
(finding 1 + its test), `9e257368` (finding 2), `62950b0a` (finding 3), all now on
`main` via PR #424.

⚠ **Finding 1's test needed a real control to be worth anything**, and got one: run
against unfixed source it fails with `dragging a separator in checkbox mode resized
nothing` **while its own plain-table control arm passes first** — so the failure is
behavioral, not a broken harness. That is exactly the control the #417 review skipped,
which is how two defective tests got through there.

Original write-up follows.

1. **MEDIUM — `tableview.py:2918`: column resizing is DEAD whenever selection
   checkboxes are on.** `_on_header_click` special-cases only `region == "heading"`, so
   a click on a column **separator** falls into `if self._toggle_select_active():`,
   where `identify_row(event.y)` returns `""` — and the branch **still** returns
   `"break"`, swallowing ttk's `resize.press`. **Measured:** a plain table resizes
   (`120 → 156`); with `selection_mode="multi", show_selection_controls=True` none of
   its three separators move at all. The `break` is load-bearing **only when there is a
   row to toggle**. #421's diff compounds it — `_take_click_focus(iid)` sits *above*
   the `if iid:` guard, so a failed resize attempt now also yanks focus into the tree
   body. **Fix: move the call inside `if iid:` and return `"break"` only there.** The
   reviewer verified that change: all three separators resize (`#0` 43→79, `#1`/`#2`
   likewise) and all 23 `test_datatable.py` tests stay green. ⚠ **The breakage predates
   the branch** — but the diff edits exactly these lines. **No test covers the
   separator path either way; add one.**
2. **LOW — `tableview.py:2874`: swap `except Exception: pass` for
   `debug_log_exception`.** The defect #421 fixes *is* "focus silently did not happen";
   if `focus_set()`/`focus(iid)` raises, the fix degrades back to the original bug with
   no signal anywhere. `debug_log_exception` (`_runtime/utility.py`, #399) never
   raises, so it is safe in a Tk dispatch path. Neighbors do the bare `pass`, but this
   is new code.
3. **LOW — `CHANGELOG.md:25`: the headline overstates the blast radius.** "Clicking a
   `DataTable` row now leaves the keyboard pointed at that row" reads as though
   ordinary row clicks were broken. **They never were** — the branch's own control
   proves plain rows always took focus. Scope the headline to group headers and
   checkbox tables; the bullet body already says the right thing. Same standard that
   kept #397/#401 out of `0.2.1`.

#### ✅ The `0.2.2` release sequence — ALL STEPS DONE (2026-08-06)

**Milestones are SETTLED (maintainer, 2026-08-06): #417, #418, #419, #420, #421 and
#422 are all on `0.2.x — Patch line`. There are ZERO unmilestoned open issues** —
verified against `gh`, and it clears the deviation this file used to flag. That
milestone now has **#422 and #207** left open.

All six steps completed: branches rebased (with `git diff main...HEAD -- CLAUDE.md`
empty on both — the trap that nearly bit #410), PR'd and merged as merge commits
(#423 then #424), `## [Unreleased]` promoted in its own commit, `bumpversion` run,
tag pushed, **published manually** (see START HERE), issues closed, #417 commented,
branches deleted. ⚠ The CHANGELOG bullet count is **7**, but do **not** read that as
"unchanged from the 7 recorded at `ff814b85`" — the column-resize fix **added** one
and consolidating the #418/#420 pair **removed** one. Coincidence, not stasis.

⚠ **The posted #417 comment is NOT verbatim the draft this file carried.** The draft
predated the column-resize fix (#421 review finding 1), so it said "four more defects"
and stopped at the focus bug. One sentence was appended covering the separator fix,
which is user-visible in the release notes. **A prepared draft goes stale when the
release grows** — re-read it against the final CHANGELOG before pasting.

Everything below is the backlog to pick from now that `0.2.2` is out.

**#409 is DONE (PR #414) — full entry in `docs/_dev/handoff-archive.md`.** Two
things from it are worth carrying here because they are invisible in the diff and
will bite again:

- ⚠ **`emit()` and `on()` take the same names but NOT always the same target.**
  `emit()` consults the `_event_target()` seam **only for `<<Virtual>>` sequences**;
  the native-mapped names (`click`/`focus`/`blur`/`submit`) fire on `_internal`, so
  `field.emit("submit")` on a retargeting composite reaches nothing bound through
  `on()` — silently. Documented in both `PublicWidgetBase.emit`'s docstring and
  `docs/reference/events.rst` now; it was only in the docstring before.
- ⚠ **`resolve_event()`'s error is process-wide, not per-widget.** `all_known` is a
  union of `GLOBAL_EVENT_MAP` and **every** `_CLASS_EVENT_MAPS` entry, so a `Button`
  typo is reported alongside `cursor_move`/`export`/`item_drag_start`. Narrowing it
  is folded into **#412**, not done. Don't write docs claiming the error lists what
  *that* widget knows — the branch shipped that sentence and the review caught it.

**⚠ `## [Unreleased]` is ABSENT ON `main`** — `0.2.3` consumed it (the top section is
now `## [0.2.3] — Import without IDLE`, with its `[0.2.3]:` link definition at the
bottom). The next fix commit re-creates it, per the convention under Release flow.

**⏭ The next targets, in milestone order (see the table above for why).**

**#390 is the exception to the order and can be taken at ANY time — it is a
DECISION, not work.** Should signals model emptiness at all? (`0.4.0`.) The
write-up below is complete and the maintainer is actively evaluating (discussion
#386); it needs an answer, not more analysis. Cheapest item on the board and the
largest unblock, since it gates #389 shipping *whole*. **Do not re-derive it.**

Otherwise, first substantial work is the **`Test and release confidence`**
workstream, in this order:

1. **#407 — the harness scene reset.** Best-understood open work in this file: root
   cause known, payoff measured (widget leg **144s → 80s**), and it makes PageStack
   pass with no `isolated` marker. Its old blocker (#392) shipped in `0.2.0`. ⚠ The
   patch itself is LOST and must be re-derived from the recorded root cause below.
2. **#380 — CI.** Nothing runs the suite on push; every Tk 9 bug so far was found by
   a user or by hand. Take it *after* #407 so the automation is cheaper and the suite
   it automates actually passes. Largest item here; read the issue before scoping.

Then `0.3.0 — Strictness and value types` as one batch (#383, #369, #408, #416),
then `0.4.0` (#389 behind #390, #412, #415). **#412** is small and well-scoped:
publish an existing internal front door so composite authors get a documented
bare-name path *while keeping the typo guard*. Until it lands,
`docs/reference/events.rst` stays **deliberately silent on custom events** — that
silence is the one real cost of how #409 shipped.

**⚠ #415/#416 came from discussion #413** (a user asking for `PathField` in a
`Form`). Both were filed 2026-08-05 with a probe at
`development/probe_413_pathfield_value.py`; **the maintainer replied on #413 the
same day, so that loop is closed.** The measured finding worth not re-deriving:
**10 of the 12 public field-family widgets are `Form` editors — the two that are
not are `PathField` and `TimeField`** — and an unknown `editor=` name **silently
builds a `TextField`** (`_impl/composites/form.py:774`). `DateField` being an
editor while `TimeField` is not is what makes this drift rather than a design
boundary.

**⚠ `open_multiple` is FULLY DECIDED (maintainer, 2026-08-05) — nothing left to
settle before implementing #416.** The contract: **`open_multiple` → `tuple[Path,
...]`, empty `()`; every other mode → `Path | None`, empty `None`.** #416's body
still presents this as an open question with two options; **the decision lives in a
comment on the issue**, not the body. The rejected option was a second property
holding the tuple — one concept, two names. Two costs accepted deliberately: the
return type depends on a construction argument (`open_multiple` selects a different
*kind* of thing, and the `', '` join it replaces is already lossy), and **`()`
rather than `None` when empty is a deliberate exception to the framework's
`None`-when-empty convention** — the type stays stable so callers iterate without a
guard, and for a multi-select "nothing selected" and "an empty selection" are the
same state.

**⚠ Two test-coverage gaps, same class — fold both into #380.** `testpaths` is
`tests/cli`, `tests/widgets/public`, `tests/data`, so **anything outside those
never runs**: (a) the 12 files / 25 tests directly under `tests/widgets/`, and
(b) **`tests/test_public_surface.py`** — the guard for the curated public namespace
(PR #104), which the widget-review standard lists as a verify step. Run by hand at
the `0.2.1` tag: **166 passed**. It is green; it is just never run by `run_gui.py`.

**⚠ What THIS FILE got wrong about the cluster — the pattern is the lesson.** The
2026-08-05 review re-read `7e204801` (#401) and #397 (then `6520597b`, shipped as
`a93a47a4` after the timer fix was folded in) precisely because
an earlier whole-branch pass had already been wrong three times about #397. That
re-read found two more defects, so the running count is **four** — and one of them
was in this file:

- **This file claimed "the branch no longer touches `CLAUDE.md` at all." It did.**
  The `docs(claude):` *commits* had been dropped, but the CLAUDE.md edits were
  folded into the #396 commit instead — a 252-line rewrite descending from
  `e23207b4`, i.e. `main`'s **pre-cluster** handoff. Merging #410 would have applied
  84 insertions against 168 deletions to `main`'s handoff, silently reverting three
  `docs(claude):` commits. Caught by diffing `main...HEAD -- CLAUDE.md`, not by
  reading. **Run that diff before merging any branch.** The rule it protects still
  holds: handoff state lives on `main` only.
- **The #397 end-to-end test leaked a 10s `after` timer** on the shared root, and
  its module is not in `ISOLATED` — so the timer fired during a later test and
  destroyed an unrelated `Toplevel`. **The test passed either way**, which is what
  made it invisible. Measured 1 leaked timer → 0. A test that schedules a hang guard
  must cancel it in a `finally`.

**⚠ A probe that finds nothing must be proven able to find something.** The #401
completeness check (an AST scan for handlers bound to a virtual sequence that
return `'break'`) reported **zero hits** — because `ast.parse` was choking on a
**UTF-8 BOM** and a bare `except Exception: continue` swallowed it, silently
skipping every file. Reading `utf-8-sig` and re-running against the pre-fix commit
as a control reproduced exactly the two known handlers, which is the only thing
that made the post-fix zero mean anything. **Always run the control.** The same
session produced a second vacuity: a probe set `field.readonly = True` on a public
widget — a plain Python object — so the bogus attribute stuck silently and the field
kept stepping. The property is **`read_only`**.

#392 is DONE and merged — its full root-cause writeup, the four-commit breakdown,
and every gotcha moved to **`docs/_dev/handoff-archive.md`** (grep `#392`). **Read
that entry before touching `_runtime/events.py`**; it records things that cost real
time and are invisible in the diff.

**After 0.2.1, the realistic candidates:**

1. **#390 — should signals model emptiness at all? (DESIGN — milestone `0.3.0`;
   the maintainer is actively evaluating options as of 2026-07-30.)** Gates #389
   shipping *whole*: without it `Form.clear()` works but leaves a bound `Signal`
   stale. **If the answer is no, close #390** and ship #389 with the limitation
   documented. ⚠ The analysis below is COMPLETE — it needs a decision, not more
   work. The maintainer has publicly said they are evaluating (discussion #386),
   so do not re-derive it or ask the reporter to weigh in. `Signal.set(None)` raises
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

2. **#389 — `Form.reset()` / `Form.clear()`.** Milestone `0.3.0` (moved out of
   0.2.0 so that release could cut). Unblocked (#387 merged), design
   settled, implementation sketch on the issue. **They are DIFFERENT verbs** —
   reset = construction-time originals, clear = `None`. Both justified: `reset()`
   is **not user-implementable** (after an edit, `get()` no longer knows the
   original); `clear()` is the data-entry case. Slider clears to `min_value` (no
   null state, and that is already the de-facto seeding behavior). Needs an
   `__init__` snapshot because `set()` destroys `_data`; both must clear
   validation state.

Then the standing items: **#407 (harness leak-fix)**, **#380 (CI)**, and **#383
(kwarg sweep)**.

---

## `0.4.0 — Signal binding on fields` — RELEASED 2026-08-29, split out of `CLAUDE.md`

⚠ **THIRD SPLIT.** Same cause as the first two: shipped work accreted in
`CLAUDE.md` instead of being archived the day its release shipped. At the time of
this split the file was **~168,000 chars / ~42,000 tokens**, 70% of the ~60,000
that forced the second split, and **33% of it was this release**.

Everything below is **verbatim** as it stood in `CLAUDE.md` on 2026-08-29, the
day `v0.4.0` was tagged. Read it for the measurements and the traps, never for
the state of the world.

⚠ **Each of these branches also archived its own `PLAN.md` and `REVIEW.md` into
`development/`** — `plan-<issue>-<slug>.md` and `review-<issue>-<slug>.md`. Those
carry the full round-by-round detail; the entries below are the durable summary.
Read the `development/` file before re-deriving anything.

**Shipped in `0.4.0`:** #390, #444, #449, #456, #458, #459, #460, #461, #465,
#467, #472, #476, #486, plus the three unmilestoned chore PRs #492/#493/#494.

#### ⭐⭐ THE DEAD-CODE SWEEP — **THREE CHORE PRs, ~1,900 LINES REMOVED, THREE LATENT DEFECTS FIXED. 2026-08-29.**

**Not milestoned, no issues filed, no CHANGELOG entries — all three are private-layer removals with no reachable surface.** ⚠ **They were found by ASKING ONE QUESTION OF A MODULE THE MAINTAINER HAPPENED TO OPEN: *is this actually used, and does the framework already do it elsewhere?*** That question found three separate dead layers in a row. **It is the same question that found #476** (*is this internal member reachable from public API at all?*) — **reusable, and cheaper than any sweep.**

| PR | what | merge |
|---|---|---|
| **#492** | `_core/publisher.py` — the STD `Publisher`/`Channel`/`Subscriber` pub-sub | `983cfa45` |
| **#493** | `_core/colorutils.py` — a duplicate of six functions in `style/utility.py` | `5201de45` |
| **#494** | `_core/capabilities/` — the Tk-surface mixin veneer | `20106128` |

⚠⚠ **THE DURABLE LESSON, AND IT IS THE ONE TO CARRY: A PASS-THROUGH LAYER IS NOT INERT — IT SHADOWS.** The capabilities veneer re-declared 91 methods, **66 of them pure `super()` delegation**, and three of those re-declarations were **broken**: `grid_propagate()`/`pack_propagate()` re-typed native's `flag=Misc._noarg_` sentinel as `flag=None` and so took the **setter** branch on a no-arg call (**measured: `None` where plain tkinter says `True`**); `WidgetCapabilitiesMixin.forget()` shadowed `ttk.Panedwindow.forget(child)` with a zero-arg method, so the real ttk API raised `TypeError`; and `selection_own_set()` called a keyword-only native positionally and **had never worked**. **Deleting them WAS the fix for all three.** ⚠ **A layer that only forwards can still be wrong, because the signature is part of the behavior.**

⚠⚠ **AND THE COUNTER-LESSON FROM THE SAME BRANCH: `forget()` HAD ZERO CALLERS, AND THE ONE FILE THAT WANTED IT HAD ALREADY ROUTED AROUND IT.** `splitview.py` carried `tk.call(str(w), "forget", pane)` with a comment naming the collision — **a correct workaround for broken inheritance, not caller misuse.** It reverted to the natural `self._internal.forget(pane._frame)`. **Before pricing a shadowing method as load-bearing, grep its call sites: `grep -rn "\.forget()"` returned ONE hit and it was the comment.**

⚠⚠ **THE BREAK THAT NEARLY SHIPPED, AND IT WAS INVISIBLE TO `git diff` REVIEW: AN IDE "OPTIMIZE IMPORTS" HOISTED A FUNCTION-LOCAL IMPORT TO MODULE SCOPE AND CLOSED AN IMPORT CYCLE.** `base.py` gained `from bootstack.widgets._core.container import resolve_pack_order` at line 7, while `container.py:94` imports `PublicWidgetBase` **from `base.py`** with a comment saying exactly why it is late. **`import bootstack` failed outright** — every test leg would have died at collection. **The fix is to keep it function-local**, inside `attach()`'s existing import list. ⏭ **`.venv/bin/python -c "import bootstack"` IS THE CHEAPEST GATE THERE IS — run it before the suite, not after.**

✅ **A PRE-EXISTING LATENT `NameError` WAS CLOSED AS A SIDE EFFECT.** `resolve_pack_order` was **called at `base.py:526` and never imported** on `main`. It survived because the call sits in the `placement.method == "pack"` branch and bootstack's flex containers **grid** their children, so `attach(index=0)` on a `Column` takes the grid path and never reaches it. **Nobody would guess this from the diff — it is worth knowing that the pack branch of `attach()` is effectively untested.**

⚠ **AN OVER-BROAD FIND/REPLACE CORRUPTED FOUR MARKDOWN FILES AND `git diff` LOOKED FINE.** Renaming the module to `signal_binding.py` swept the bare word `signals` in `development/wrapper-parameter-audit-463.md` (Chart's **parameter destination**), `docs/_dev/api-reference-restructure.md` (the **public** `bootstack.signals` docs subsystem), `docs/_dev/handoff-archive.md` (the `docs/reference/signals` page — **the archive**) and the branch's own plan. **All reverted.** ⚠ **A rename sweep over prose must be scoped to the identifier, not the word** — and the archive is history, so a wrong entry there reads as authoritative.

**Details, with the measurements, are in `development/plan-capabilities-collapse.md`** — the full 91-method classification, the native-signature comparison and the three defect controls. **Do not re-derive it.**

⚠ **`_core/capabilities/` NO LONGER EXISTS.** `signals.py` → **`_core/signal_binding.py`** (renamed to stop it reading as the public `bootstack/signals/` package — the only two live modules in the package were never mixins), `localization.py` → **`_core/localization.py`**, both 100% renames. 13 survivors folded into `_core/mixins/widget.py`: `after_repeat`, four `bindtags_*`, `clipboard_set`, and the seven layout methods that dispatch to `_on_child_*` hooks on `GridFrame`/`PackFrame`. ⚠ **Those hooks are the ONLY load-bearing thing the veneer carried — everything else was delegation.**

⚠ **`_core/colorutils.py` IS GONE — use `bootstack.style.utility`.** The color chooser was its only consumer. ⚠ **The two copies had DIVERGED: `style/utility.conform_color_model` CLAMPS each channel and the `_core` copy did not**, so the chooser gained clamping it never had. Outputs measured identical at every call shape in use.

⚠ **THE `_windowingsystem` DUPLICATION IS STILL OPEN AND BELONGS ON #477.** Two private twins — `_runtime/wheel.py:38` and `widgets/toast.py:25` — plus **18 raw `tk.call("tk", "windowingsystem")` sites** across `_runtime`, `widgets` and `_impl`. ⚠ **Their fallbacks DISAGREE**: wheel returns `""` (degrades to the generic path, correct) and toast returns `"win32"` (**asserts Windows**, which drives a platform-specific default corner). **Not folded into these three because 8 of the 18 cache the value at construction, so consolidating changes WHEN the probe happens, not just where.**

#### ✅ #486 SHIPPED (PR #489, merge commit `313f44fc`, 2026-08-29). Branch deleted local; ⚠ **the REMOTE branch `origin/fix/textarea-signal-binding-486` still exists at `9f45baf5` — delete it.** **Cap 3, spent 2 — round 2 said there was nothing for round 3 to review.**

⚠⚠ **ITS PR BODY SILENTLY CLOSED AN UNRELATED OPEN ISSUE, AND NOBODY NOTICED FOR A DAY. AN ISSUE REFERENCE INSIDE EXPLANATORY PROSE STILL TRIGGERS GITHUB'S CLOSING KEYWORDS.** The body said *"…which closes #479's shape for these two"* — meaning `TextArea`/`CodeEditor` — and GitHub closed **#479**, which is about `OptionMenu`, two seconds after the merge. **Re-measured on `main` at `245b4df2` and REOPENED 2026-08-29: `subscribers 1 -> 1` across destroy, `sig.set()` reports success while a `TclError: bad window path name ".!optionmenu"` is raised inside the Tk trace.** Unchanged; `grep -n destroy optionmenu.py` still returns only the context menu. ⏭ **Write `#479's shape` with NO verb in front of it**, and after any merge check that the PR closed only what it meant to — `gh issue list --state closed --search "closed:>=<merge-date>"`.

**READ `development/review-486-textarea-signal-binding.md` FIRST, THEN `development/plan-486-textarea-signal-binding.md`.** ✅ **BOTH WERE ARCHIVED IN THE BRANCH BEFORE THE PR OPENED** — the rule, and the second branch after #444 to follow it. They carry the design, both rejected alternatives, every measurement and two rounds of cleared lists. **Do not re-derive any of it.**

⚠⚠ **THE ROUND'S HEADLINE: THE FIX WORKS, AND THE FIRST DRAFT OF THE RECORD SAID OTHERWISE.** Scored against the invariant a two-way binding claims — `sig() == widget.value` — **`main` disagrees in 4 of 5 states** (it reads back whatever its own code last wrote, through typing, clearing, blurring and refocusing) while the **branch disagrees in 0 of 5 without a placeholder and 1 of 5 with one.** Every state `main` gets right, the branch gets right.

⚠⚠ **AND THE REASON THE FIRST DRAFT GOT IT BACKWARDS IS THE DURABLE LESSON: A POLLUTION DETECTOR SCORES A DEAD BINDING AS CLEAN.** The first probe only asked *"is the placeholder string in the signal?"*, so `main` — which never writes anything back at all — passed it, and the record called the branch a regression. **Ask whether the value is RIGHT, not whether the known-bad value is absent.** `development/probe_486_review_round1.py` now carries the agreement arm and says in its own docstring that arms 1–2 mislead without it.

⚠⚠ **THE HEADLINE THAT OUTLIVES THE BRANCH: A READER SEAM WITHOUT A WRITER SEAM SILENTLY REVERTS `sig.set(...)` FROM APPLICATION CODE — AND A DEMO CAUGHT IT, NOT THE SUITE.** Round 1's finding was that the placeholder reached the bound signal, and its fix gave the core a reader (`_signal_text_source`) so the composite could answer `""` while its placeholder is up. **With only that half**, a model write landed in the raw document, the reader answered `""` because the flag still stood, and the push sent that `""` **back over the caller's value** — text gone, signal emptied, suite green. `_signal_text_sink` is the write half; **both are installed together, before `bind_signal`, and they must agree about what the widget's text is.**

⚠⚠ **THE GAP THAT PRODUCED IT IS THE ONE TO CARRY: EVERY TEST DROVE THE WIDGET AND THEN THE MODEL, NEVER THE MODEL WHILE THE WIDGET WAS IN THE STATE THE FIX TOUCHED.** That is #390 round 3's finding in a new place — a feature with two doors into the same code, tested through one. **Clicking through the states is not a lesser instrument than the suite**; `development/demo_486_textarea_signal.py` is the demo that found it. The edit door is covered now.

⚠ **THE MIRROR-IMAGE BUG WAS PULLED INTO SCOPE, AND THAT WAS FORCED RATHER THAN CHOSEN. AN EARLIER VERSION OF THIS SECTION SAID "DO NOT LET THE FIX GROW INTO IT" — THAT IS NOW WRONG.** Routing the model write through the composite's setter *is* the fix for it, and the alternative is data loss. **`TextArea` now reports the same thing through screen, `value` and signal in that state.**

⚠ **`_showing_placeholder` IS NOT THE SUSPEND FLAG THE PLAN FORBIDS.** The ban is on a flag raised and lowered *around a write*, which a `when="tail"` event outlives. This is **durable state**, still `True` when the tail delivery arrives. Consulting it is sound; the echo guard's value comparison stays as it is.

✅ **ROUND 2: NOTHING BLOCKING, one gate-2 vacuity in a test.** `test_rebinding_leaves_the_previous_signal_alone` **passed with the release deleted**, because `_push_to_signal` reads `self._signal` at call time — so an orphan can only ever push into the *current* signal and **no value assertion can see a leaked hook.** It asserts the hooks now (stale bind id gone from the binding script, no subscribers left on the replaced signal), each half controlled by deleting it. **Test-only, so gate 1 triggered no round 3.**

⚠ **ROUND 2 MEASURED DESTROY ON BOTH ARMS AND `main` IS WORSE THAN ROUND 1 KNEW:** subscribers `1 -> 1` and `sig.set(...)` after destroy raises `TclError` on `main`; `1 -> 0` and silent here. **That closes #479's shape for these two widgets.** Also cleared, each measured: a rebind releases the push binding (5 rebinds, 0 orphans), two widgets on one signal converge with no echo, `read_only` works both ways, and all five public write paths (`insert`, `append`, `clear`, `undo`, `redo`) keep the signal in step.

✅ **THE DEFERRED CHANGELOG LINE IS RESOLVED AND IN — in STRONGER wording than either round proposed, because the measurement forced it. Do not weaken it back.** On `v0.3.2` (byte-identical to `main` on this path, so the tag is a legitimate arm), writing a bound signal while the placeholder showed left `_showing_placeholder` standing — and `_on_core_change` and `_on_focus_out` both gate on it, so `value` returned `""` and **`on_input`/`on_change` fired ZERO times for everything typed afterwards, permanently.** The deferred wording named only `value` and read as a typing nit.

⏭ **WHAT IS LEFT ON THE TEXTSIGNAL WORK, verified against `gh` 2026-08-29 — FOUR OPEN ISSUES AND ONE UNDECIDED DESIGN CALL.** **#488** (the core teardown has never run), **#490** (`Signal.clear()` never reaches these two), **#491** (`insert()`/`append()` write alongside the placeholder) — **all three unmilestoned**; plus **#479**, reopened above, on `0.5.0`. ⚠ **The design call is the one that is not an issue and will not surface as one:** `.signal` means **two different things** across the family — see the text-space/value-space split recorded under #458 below. **That is a family decision nobody has made, and no bug report will force it.**

⚠ **TWO PRE-EXISTING `TextArea` DEFECTS WERE FILED OUT OF THIS BRANCH AND ARE NOT FIXED BY IT.** **#490** — a `Signal.clear()` never reaches `TextArea`/`CodeEditor`: **7 of the 9 field widgets that take a signal honor it, these two do not**, because `_on_signal_change` drops `None` and `None` is exactly what an empty arrives as for a widget with no Tk variable. ⚠ **The control is the argument it is a defect: the SAME `TextArea` honors the clear when a `TextField` elsewhere happens to realize the signal's variable, and ignores it otherwise.** **#491** — `TextArea.insert()`/`append()` reach `self._internal._core.insert(...)` directly, never clear the placeholder flag, and concatenate onto the placeholder on screen while `value` reads `""` and events stay suppressed. **The CHANGELOG line is scoped to a bound signal on purpose; do not widen it.** Probes: `development/probe_486_clear_divergence.py` and `development/probe_486_changelog_reach.py`.

**`TextArea` and `CodeEditor` bound `textsignal=` in ONE direction, and `.signal` returned `None` unconditionally.** Both from one cause: the textarea core holds the bound signal at a private `_signal` and neither exposed it nor ever wrote to it. **Fixed entirely in `_impl` — the wrappers were reading the right name all along**, so `core` gained a public `signal` property, the `TextArea` composite delegates to it, and the wrappers only lost their now-dead `getattr`.

⚠⚠ **THE ECHO GUARD IS A VALUE COMPARISON AND MUST NOT BE "SIMPLIFIED" INTO A SUSPEND FLAG.** `ChangeNotifier._notify` emits `<<Change>>` with **`when="tail"`**, so a flag raised around the write is already cleared when the handler runs and misses the echo every time. **This is the same trap `Form` hit in PR #354** (`reference_async_change_event_suspend_guard`). Both directions dedupe on value. Measured: **exactly 20 subscriber fires for 20 alternating writes**, no amplification.

⚠ **A non-`str` textsignal is REFUSED AT BIND — maintainer decision, 2026-08-28. Do not re-propose accepting it.** ⚠ **The hazard fires at BIND, not on the first keystroke**, because `bind_signal` seeds the widget and that seed is itself an edit: measured before the guard, `bs.TextArea(textsignal=bs.Signal(123))` printed a bare traceback at construction, left the signal on its old value, and put **nothing on the background-error channel**. The guard reads the **public `Signal.type`** and reproduces `_reconcile`'s message shape, so it is byte-identical to `bs.TextField(textsignal=bs.Signal(123))` — pinned by a test that asserts the two messages match rather than assuming it.

⚠⚠ **A PRE-EXISTING DEFECT WAS FOUND BY THE DESTROY TEST AND IS ONLY HALF FIXED HERE — #488.** `_on_destroy` opens with `if event.widget is not self: return`, and **the only `<Destroy>` it ever receives names the inner `Text`**, so the guard rejects every call and the entire cleanup block has never run. Measured identical on both arms of `git stash push -- src/`, so it is **not** a consequence of this branch. **Only the signal hooks are released here.** ⚠ **DO NOT "FIX" IT BY CORRECTING THE GUARD** — `_chain.destroy()` and the wheel `unbind_class` sweep sit behind the same condition, so repairing it starts running long-dead teardown for the first time, with a blast radius nobody has measured.

**⏭ BOTH ROUNDS CLEARED A LONG LIST WITH MEASUREMENTS — do not re-derive them.** The full account with commands is in `development/review-486-textarea-signal-binding.md`.

- **`off_change(bind_id)` does NOT wipe its siblings**, which was the round's most expected hazard: `core.text` carries **five other `<<Change>>` bindings** (`_on_core_change`, `CodeEditor`'s typed-change emitter, the line-number sidebar, the search overlay, user callbacks), and tkinter's `unbind(seq, funcid)` historically dropped every binding for the sequence. **On the project's `>=3.12` floor `Misc._unbind` is selective** — measured: an unrelated handler still fires after a rebind.
- **The refusal is WIDER than the plan's `int` example and is still consistent.** `signal.type is not str` rejects **any** non-`str` type, `NoneType` included, so `bs.TextArea(textsignal=bs.Signal(None))` is accepted on `main` and refused here — and **`TextField` refuses `Signal(None)` with the byte-identical message.** The consistency claim holds beyond the case the test pins.
- **`Signal.set('')` needs no `allow_empty`** (`''` is an ordinary `str` to `_reconcile`), so clearing a bound field cannot raise.
- **The destroy change touches exactly ONE widget.** `core.bind()` is overridden onto `self.text`, so the handler only ever receives the inner `Text`'s own `<Destroy>` and `_unbind_signal()` runs once. ⚠ The code comment says *"any Destroy in this subtree"*, which overstates it.
- **Chrome-versus-content sweep is complete.** `grep -rn "text\.insert\|text\.delete"` over the package returns the placeholder pair, search-and-replace, undo, smart-indent and the core's own setters — **the placeholder is the only one writing something that is not the user's content**, which bounds Finding 1.
- **Two gate-2 notes, NO test fixes.** `test_a_destroyed_widget_stops_receiving_and_raises_nothing` names the background-error channel as its observable, but the signal is unrealized so `Signal.set` notifies **synchronously** and the control on `main` fails by a raise propagating out of `sig.set(...)` — so its `assert not seen` is the assertion that **cannot** fail, and the load-bearing one is implicit. ⚠ **It becomes vacuous the moment anyone wraps that `sig.set` in a `try`.** And `test_alternating_writes_do_not_echo` bounds at `<= 25` against a measured 20, which is correct slack for an unbounded failure — **do not "tighten" it.**
- ⚠ **Two-way binding doubles the per-keystroke cost and it scales with document size** — measured on a 480 KB / 6000-line `CodeEditor` with a signal bound: **1.99 ms per keystroke on `main`, 3.92 ms on the branch.** Inside a frame budget at that size, linear beyond it, paid only when a signal is bound. **Inherent to the contract — not a defect and not a fix**, recorded so a later `CodeEditor` performance report is not re-derived.

#### ✅ #460 SHIPPED (PR #487, merge commit `6d03a2a9`, 2026-08-28). Branch deleted local + remote, head **`dd15815c`**.

**Seven widgets annotated `.signal` as `Signal | None` and could never return `None`** — each forwarded with `getattr(self._internal, 'signal', None)` while the internal's `signal`/`textsignal` lazily create on first access, so the default was dead code. Dropped the `| None` and collapsed the `getattr` to direct delegation, matching `Slider`. **Plan archived at `development/plan-460-signal-annotation.md`.**

⚠⚠ **IT MERGED WITH NO REVIEW ROUND, AND WITH `PLAN.md` STILL IN `main`'s ROOT** — archived in a follow-up commit (`fdb367cc`), which is exactly the failure the protocol's archive-before-PR rule exists to prevent.

⚠ **THE ISSUE'S OWN TABLE WAS STALE AND SAID SIX LOCATIONS / EIGHT WIDGETS. IT WAS FIVE AND SEVEN.** `SelectButton` was the sixth until **#461 moved it onto `ValueSignalMixin`**, after which it correctly returns `None` when unbound. **Measure the population before trusting an issue written against an older `main`.**

⚠ **`TextArea` and `CodeEditor` were excluded, but NOT for the reason the issue gives.** It lists them as "correct, do not fix" having checked only the *unbound* case. Their `| None` is accurate; the `Signal[str]` half was the unreachable one. **That is #486.**

#### ✅ #444 SHIPPED (PR #485, merge commit `baced70b`, 2026-08-28). Branch deleted local + remote, head **`85c77bde`**. Kept for its traps.

**A modal `bs.Window` took the grab and nothing ever handed it back.** `grep -rn "grab_release\|grab_current" src/bootstack/_runtime/toplevel.py` returned nothing, which is the whole defect in one command. Tk drops a grab when its holder is destroyed but does **not** restore the grab that holder displaced, so a modal opened from inside another modal left the outer one on screen, still blocking its caller, holding nothing — the user clicked straight past it into the main window. **Pre-existing, identical in `0.2.3` and `0.3.0`, NOT a regression from #440**, which fixed the same defect scoped to the dialog classes.

⚠ **The helpers were MOVED, not copied.** #440's `capture_grab`/`restore_grab`/`_log_grab_failure` now live in `_runtime/grab.py`; `dialogs/_impl/dialog.py` imports the two names, so `datedialog.py:19` and #440's eight test call sites keep resolving **through `dialog.py`** with no alias and no re-export. **The move was forced by direction** — `dialogs` imports `Toplevel` from `_runtime`, so `_runtime` reaching back would be a cycle. **Do not write a second pair.**

⚠ **Restore is bound on `<Destroy>`, not paired around `block_until_closed()`, and that was MEASURED before it was chosen.** A modal window does not have to block, so a blocking-only pairing leaves `show()`-then-`destroy()` unfixed. The risk was that Tk's own grab release might land after our handler; `development/probe_444_grab_restore_ordering.py` shows the restore wins the race, on **win32 and X11**. **Do not re-propose option A.**

⚠⚠ **ROUND 1's BLOCKING FINDING IS THE ONE TO CARRY: A GUARD ON ONE HALF OF A PAIR IS NOT A GUARD.** `show()` captured the token **unconditionally** while `_bind_grab_restore` guarded itself against re-entry. On a second `show()` the window already holds the grab, so it captured **itself** and discarded the opener's token — **#444's symptom reintroduced by #444's fix**, on three ordinary public spellings (`show()` twice; `show()` then `block_until_closed()`, which shows it again itself; `show()` then `show(anchor_to=…)`, which is what that parameter is *for*). Measured `restored 2 / lost 3` before, `5 / 0` after. **Both halves now share one gate, `_grab_restore_bound`.** ⚠ **The gate is the BIND flag, not "have we captured before"** — if the first `grab_set()` fails, nothing was bound and a later `show()` **should** capture again.

⚠⚠ **ROUND 2's DURABLE FINDING: THE TESTS DROVE A STAND-IN FOR THE SCENARIO THE CHANGELOG NAMES, AND NOBODY HAD CHECKED THE REAL ONE.** The entry headlines *"an 'Advanced…' button on a dialog"*; the tests use a raw `tkinter.Toplevel` as the opener. **Dialog and window take their grabs through different code paths** (`dialog.py:478` directly, `Toplevel.show()` through the new helpers) **and nothing exercised them against each other.** `development/probe_444_review_round2.py` drives the real pairing: `*** LOST ***` at `main`, `OK` after — with a no-nesting **control OK on both arms**, so a LOST row is the defect and not the instrument. **Three-deep nesting unwinds correctly at every depth; depth had never been measured.** The reverse direction (a dialog inside a modal window) is OK on both arms, which is correct — that is #440's path. **Re-run the probe rather than re-deriving any of it.**

**Two rounds under a cap of 2, each in a fresh session.** Round 1: five findings, all originating outside the author's risk list, one blocking; 1-4 fixed, 5 left under gate 2. Round 2: **nothing blocking**, three structural notes, no fixes. Plan and both records archived **in the branch, before the PR opened** — `development/plan-444-modal-window-grab.md` and `development/review-444-modal-window-grab.md`, so nothing landed in `main`'s root at merge.

⚠ **CROSS-PLATFORM: Windows and Linux MEASURED, macOS NOT.** The no-platform-branch design (read the kind back from Tk rather than assuming) is measured on X11 with a **REAL global grab**, not the stub — an isolated Xvfb display makes that safe, which no live desktop does. Kind reads back faithfully and a displaced global grab survives the round trip as `global`. **macOS is the whole remaining gap** and folds into #452's trip; the arms and commands are in the archived review. ⚠ **`tk busy` is already a measured silent no-op on Aqua (#429), so the worry is concrete** — but only ONE of the two outcomes is this branch's problem, and the archived review says which.

⚠⚠ **`git mv` STAGES THE RENAME OF THE *INDEXED* BLOB, SO EDITS MADE BEFORE IT STAY UNSTAGED — AND THIS PROJECT RUNS THAT EXACT OPERATION ON EVERY BRANCH.** Archiving `PLAN.md`/`REVIEW.md` with `git mv` after editing them produced `RM` in `git status`, and a plain `git commit` then shipped the rename at **100% similarity** with a message describing a record the commit did not contain. Caught only by reading `git show --stat`. **`git add` the moved file after the `git mv`, and check the rename similarity is NOT 100% when you meant to change the content.**


**✅ #461 + #459 MERGED (PR #475, merge commit `c8ebfb7c`, 2026-08-26).** #461 (`SelectButton`'s `signal=` bound the option's LABEL, not its value) and #459 (`TimeField` emitted a change while seeding from a signal). Branch deleted local + remote, head **`e3593cd1`**. Plan and round 1 record archived at `development/plan-461-selectbutton-signal-value.md` and `development/review-461-selectbutton-signal-value.md`. Cap was 3, spent 1.

**✅ #476 MERGED (PR #478, merge commit `5cf398f8`, 2026-08-26).** Every `SelectButton` fired `on_change` **twice** per selection. Branch deleted local + remote, head **`5e72f9b4`**. Plan and round 1 record archived at `development/plan-476-selectbutton-double-change.md` and `development/review-476-selectbutton-double-change.md`. Cap was 2, spent 1 — round 1 found **no blockers in production code**, one should-fix in a test, and filed **#479**.

⚠ **#476 WAS FOUND BY ASKING A QUESTION, NOT BY A SWEEP, AND THE QUESTION IS REUSABLE:** *is this internal member reachable from public API at all?* `OptionMenu._textsignal` is not — #461 deleted the wrapper property that read it and #472 made `bs.SelectButton(textsignal=…)` raise — and chasing that turned up two live `<<Change>>` subscriptions where the code assumed one. **`_bind_change_event` returned its handle for the caller to store; `__init__` stored it, `_delegate_textsignal` discarded it, and the cancel-guard saw `None` both times.** Fixed by having it store the handle itself.

⚠ **DO NOT "FIX" IT AT THE DISCARDING CALL SITE.** `self._bind_id = self._bind_change_event()` at `optionmenu.py:368` works and leaves the identical trap for the next caller — there has already been one. **`_bind_change_event` stores its own handle now; a caller that discards the return is harmless.**

⚠⚠ **ROUND 1'S DURABLE FINDING: A TEST CAN GO RED ON THE BROKEN BUILD AND STILL NOT TEST WHAT IT IS NAMED FOR — because pytest stops at the first assertion.** `test_rebinding_the_textsignal_replaces_the_subscription` closed on `len(menu._textsignal._subscribers) == 1`, the count on the **NEW** signal, which reads **1 on both arms**. It failed pre-fix only on its *first* assertion, so **the control never reached the line the whole test exists for.** What `:368` leaked is the orphan on the **REPLACED** signal — **50 across 50 rebinds before the fix, 0 after** — and that is what it asserts now. **When a control goes red, check WHICH assertion produced it.**

⚠ **#479 CAME OUT OF ROUND 1. ON `0.5.0` (maintainer, 2026-08-26), UNFIXED:** `OptionMenu` never cancels its `<<Change>>` subscription on destroy, so a destroyed widget keeps emitting — `event_generate` on a dead window raises `TclError: bad window path name` **inside the Tk trace**, invisible to whoever wrote the signal, and the subscription **pins the destroyed widget in memory** (measured with a weakref after `gc.collect()`). **Pre-existing, and #476 halved it** (two leaked subscriptions per widget before, one after). **Not reachable from public API** — #472 rejects `textsignal=` at the wrapper and `SelectButton` hands out no property that reads the internal's. ⚠ **The fix has an exemplar in the repo: `ValueSignalMixin._bind_value_signal` (`field_mixin.py:305-310`) holds its id and releases it on destroy**, measured clean (`subs 1 -> 0`, widget collected). ⚠ **It is NOT #469** — that is a *queued* `when="tail"` event reaching a *different* widget; this is a *live subscription* firing new emissions at a dead one. Re-run `development/probe_476_review_round1.py` rather than re-deriving any of it; it prints which arm it is on by reading the source.

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

#### ✅ #458 — MERGED (PR #462, merge commit `41c8bad1`). Kept for its traps.

`Select` mapped its public `signal=` onto the internal **`textsignal=`**, installing the `Signal`'s Tk variable as the entry's textvariable — so writes landed in the display text, bypassing the value-to-label map and the commit path. **One wiring line, two symptoms**, and the reported one was the milder: decoupled options displayed the raw value (reported), while a signal write moved the display but **not** the selection, leaving `.value`/`.selection` stale with **no `<<Change>>`** — on plain `list[str]` options too, and it did not self-heal. Fixed by binding through `ValueSignalMixin`.

⚠ **`signal=` IS NOW VALUE-SPACE — a deliberate, maintainer-approved behavior change.** Both directions moved: `sel.value = '2'` used to write the label `'Two'` into the signal and now writes `'2'`. **Do not re-litigate it.**

⚠ **`.signal` MEANS TWO DIFFERENT THINGS ACROSS THE PUBLIC API, and #458 widened the split rather than causing it.** Text-space: `TextField`, `PasswordField`, `PathField`, `SpinnerField`, `TextArea`, `CodeEditor`, **`SelectButton`**. Value-space: `NumberField`, `DateField`, `TimeField`, `Select`. **That is the real content of #460 and #461 taken together, and it is a family decision nobody has made.** ⚠ The CHANGELOG was corrected pre-merge for claiming the fix *"matches the other fields that take a `signal=`"* — **it does not match `SelectButton`**, which is the nearest sibling and still binds the label. **A closed list cannot over-claim the way an open one did.**

⚠ **THE MINOR WAS FORCED BY #461, NOT BY THE ADDITION.** #458 adds public surface (`Select` gains a `signal` property), and the standing rule says an addition needs a minor — but **#461 BREAKS WORKING CODE**, which is the stronger reason: seeding a `SelectButton` signal with an option's **label** works today and is the only spelling that does. That is #381's shape. **Do not re-read this as "#458 was only an addition".**

⚠ **ONE RESIDUAL, STILL UNDECIDED:** the #458 CHANGELOG bullet does not mention that `Select` gained a public `signal` property. **Announcing it is a maintainer call, not a defect.**

**Two review records, archived to `development/plan-458-select-signal.md` and `development/review-458-select-signal.md`** — round 1 (four findings, none in production code) plus an **off-protocol verification pass** that should not have opened (it reviewed a test-only commit, which gate 1 exists to keep out) and whose two re-reports cost a round of attention because **the reviewer was not handed `REVIEW.md`**. Cap was 2, spent 1.

⚠ **ITS ONE REAL FINDING IS THE ONE TO CARRY: a test can drive the right path and still assert nothing that can fail.** Round 1's own fix added a signal write to the read-only test but no assertion sensitive to the entry state — `read_only` reads the stored **setting** (#453 decoupled it from the entry on purpose) and the shown text is correct either way, so **both assertions passed while the field was silently editable**. Closed by asserting `entry_widget.instate(["readonly"])`, with a control that breaks the applier and watches the three older assertions still clear.

#### Two issues came out of that work — ✅ BOTH NOW SHIPPED

- ✅ **#461 — `SelectButton` had #458's defect.** Identical `signal -> textsignal` wiring at `selectbutton.py:85`. Seeding with the **label** worked; seeding with the **value** — what `value=` takes and what the docstring promises — gave `text='2' value='2' selection=None`, and `sel.value = "3"` wrote the *label* back. **Fixed 2026-08-26 (PR #475) by moving it onto `ValueSignalMixin`, and it is why `0.4.0` is a MINOR.** ⚠ **That move is what made #460's issue text stale** — it removed `SelectButton` from #460's population.
- ✅ **#460 — widgets annotated `.signal` as `Signal | None` and could never return `None`.** The wrappers forwarded with `getattr(self._internal, 'signal', None)` while the internal **lazily creates on first access**, so the default was dead code and the `| None` was **unreachable, not merely unobserved**. **Fixed 2026-08-28 (PR #487): five locations, seven widgets** — ⚠ **not the six/eight the issue said**, see the ★ section. `Slider` was the exemplar. ⚠ **The `ValueSignalMixin` widgets keep their `| None` and are correct.** ⚠ **`TextArea` and `CodeEditor` also keep theirs — but for the OPPOSITE reason to the one #460 gave, and that is #486.**

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

