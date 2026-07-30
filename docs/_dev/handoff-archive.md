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

