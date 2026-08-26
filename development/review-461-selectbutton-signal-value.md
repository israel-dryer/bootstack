# REVIEW — round 1 of `fix/selectbutton-signal-value-461`

Branch base `main` at `ede2d57e`. Commits reviewed: `c85d9220` (#461), `f39b0a88` (#459).
**Cap 3, spent 1.** Fresh session; did not write this code.

**Gate 1 — round is triggered.** `git diff ede2d57e..HEAD -- src/` is non-empty:
`selectbutton.py` (+15/−11), `timefield.py` (+9/−1).

## What was verified independently, not read

| check | result |
|---|---|
| Full suite, Windows box, `py -3.12 tests/run_gui.py` | **1573 passed / 22 skipped, 33 legs, exit 0** — reproduces the plan's figure exactly. `matplotlib` and `pandas` both present |
| `tests/test_public_surface.py` (never run by `run_gui.py`) | 166 passed |
| `tests/widgets/test_icon_image_props.py` (orphan file, touches `SelectButton`) | 5 passed — the MRO change does not disturb `IconProperty` |
| Clean docs build, `-W --keep-going` | **exit 0, warning-free**; no `textsignal` / `Signal[str]` in either built `SelectButton` page |
| Probe: seed emit, shared-signal round trip, destroy release, off-list write, empty-string seed, `options=` reassign, `value=None` clear | all match the plan's post-fix claims |
| Probe: `DateField` / `NumberField` seed silence | `[]` both — and confirmed structurally: `DateEntry` and `NumericEntry` are `Field`-based, `TimeEntry` is the only remaining `SelectBox` subclass, so #459's population really is exactly one |
| `_suppress_changed_event` blast radius (`selectbox.py:1212`) | gates **only** the `event_generate`; `_prev_changed_value` is still written above the guard, so a later genuine change is neither lost nor doubled |

## Findings

### 1 — BLOCKING. `docs/widgets/selectbutton.rst:117` — the widget page's own example now raises at construction

```python
theme = bs.Signal("light")
bs.SelectButton(["Light", "Dark", "Auto"], signal=theme)
```

`"light"` is not one of the options — `"Light"` is. Post-fix the seed runs through
`_bind_value_signal` → `OptionMenu.set("light")` → **`ValueError: 'light' is not one of the
options`**. Run verbatim on this branch:

```
RESULT: ValueError: 'light' is not one of the options
```

Pre-fix `signal=` became the internal's `textsignal`, so the variable simply held `'light'`
and the button face showed the raw string — wrong-looking, but it constructed. (Boundary:
this is read from the pre-fix wiring plus the plan's own ARM 1 baseline, which shows the
analogous off-list seed constructing; it was not re-run at `ede2d57e`.)

**Root cause is the shape of the docs sweep, not the fix.** `PLAN.md` checked the four
`signal=` sites for *decoupled options* — "all with plain `list[str]` options … text ==
value, so none is affected". Correct as far as it goes, and the other three seed `"All"`,
which is an option. The question that decides this one is a different one: **does the seed
value name an option?** A plain-strings button is affected too when it does not.

Nothing could have caught it: an `.. code-block::` is executed by nothing — the suite does
not read `docs/`, and unlike `literalinclude` there is not even a file to run. That is
#472's lesson arriving through a third door.

**Minimal change:** `theme = bs.Signal("Light")`. The `lambda v: bs.set_theme(v.lower())`
below it already lowercases, so the example stays correct end to end.

**Resolution:** fixed. `docs/widgets/selectbutton.rst:117` now seeds `bs.Signal("Light")`,
and the snippet was run verbatim afterwards (constructs, and `theme.subscribe` still
receives `"light"` for the initial option).

### 2 — SHOULD-FIX. The CHANGELOG tells the affected population it is unaffected

The #461 bullet says: *"Buttons built from plain strings, where the label and the value are
the same text, are unaffected"*, and scopes the migration to *"if you seed a `SelectButton`
signal with an option's label"*.

Both are narrower than what shipped. A plain-strings button **is** affected when its signal
is seeded with any string that is not one of the options — which is not a hypothetical, it
is finding 1: our own documented example. A reader with `list[str]` options scanning "was I
affected?" stops at that sentence and skips.

**Resolution:** fixed. The migration sentence now covers seeding with *any* string that is
not one of the option values, and the "unaffected" sentence is scoped to buttons whose seed
already names an option.

### 2b — SHOULD-FIX, raised by the maintainer during the round. Both bullets claim the signal carries the value "in both directions"; it stops carrying anything at empty

See **N1** for the measurement. `Select`'s case is user-reachable and its `on_change` and its
signal disagree, which is a "was I affected?" answer a reader is entitled to.

**Resolution:** fixed. Both the #461 and the #458 bullets now name the empty-selection
exception and point at #390. The #458 bullet is `main`'s work, but it is still under
`## [Unreleased]` and this branch had already amended it once; shipped history is untouched.

### 3 — NIT. Same bullet: "the same defect as the `Select` fix above"

The `Select` entry (#458) is **below**, under `### Fixed`; `### Changed` renders first.
Fixed in the same sentence edit — reworded to name the release rather than a direction.

## Notes — recorded, not fixed (gate 2, and scope)

- **N1. Clearing leaves the bound signal stale and silent. NOT fixable here — it is #390's,
  already filed with this exact mechanism and line numbers — but `0.4.0` grows its blast
  radius by two widgets, and for those two it is a REGRESSION against `0.3.2`.** Measured
  across the whole `ValueSignalMixin` family: `w.value = None` leaves every one of
  `SelectButton`, `Select`, `NumberField`, `DateField`, `TimeField` holding its previous
  signal value with **zero subscriber notifications**, because `_sync_value_set` and
  `_to_signal` both early-return on `None` — `Signal.set(None)` raises. Same for
  `sb.options = [...]`, the dependent-dropdown pattern.

  What is new is that `Select` (#458) and `SelectButton` (#461) have just *joined* that
  population. Their signals used to be the widget's own `StringVar`, which can hold `''`.
  Reproduced against the pre-fix wiring in-process (no worktree, no `PYTHONPATH` skew — the
  internals still accept `textsignal=`):

  ```
  PRE-#461 SelectButton clear      widget=None signal=''  subscriber_saw=['']
  PRE-#461 SelectButton reopts     widget=None signal=''  subscriber_saw=['']
  PRE-#458 Select user-clear       widget=None signal=''  subscriber_saw=['']
  post-fix, all three              widget=None signal='2' subscriber_saw=[]
  ```

  **`Select`'s is the sharper one and it is USER-reachable** (`SelectButton`'s popup offers
  only options, so its is code-only): a user clearing the field fires `<<Change>>` with
  `value=None`, so `on_change` handlers see the clear while the bound signal silently keeps
  the old selection — **two surfaces on the same widget disagreeing about the same event.**

  **Not fixed, and it should not be fixed on this branch.** The only fix that does not wait on
  #390 is a per-type empty sentinel, which #390's own analysis considered and rejected, and
  which cannot work for the siblings anyway (measured: `Signal(int).set('')` raises). Patching
  `SelectButton` alone would re-create the family divergence #461 exists to remove and would
  leave the more reachable `Select` broken. **Two follow-ups instead:** the CHANGELOG claim
  was corrected (below), and #390 should be told at merge — its body frames the staleness as
  affecting fields whose signals were never widget-attached, and does not yet know it acquires
  two widgets and a regression edge in `0.4.0`, nor the `on_change`/signal disagreement.
  ✅ **DECIDED (maintainer, 2026-08-25): #390 MOVES TO `0.4.0`** — *"doesn't make sense to have
  half solved solution while we introduce new bugs."* Done, and the measurement above is posted
  on the issue. It fits that milestone's title (`Signal binding on fields`) without a retitle.
  **Do not re-propose deferring it**; the narrow-fix option was measured and does not exist.

  ⏭ **CONSEQUENCE FOR THIS BRANCH'S CHANGELOG, and it is a trap for whoever promotes the
  section.** The #458 and #461 bullets now DOCUMENT the empty-selection exception and link to
  #390, which is correct only while the limitation ships. **If #390 lands in `0.4.0` as now
  planned, both sentences must come back out before `## [Unreleased]` is promoted.** Recorded
  on #390 as well, so it is not held only here.

  ⏭ **#390 IS BLOCKED ON DECISIONS, NOT ON WORK, AND NONE OF THE FOUR HAS BEEN ANSWERED.**
  Do it at all (settled by the milestone move), declared vs automatic nullability, what a
  non-nullable signal asked to go empty should do, and what `map()` does over a nullable one.
  `CLAUDE.md` carries the standing recommendations and says the analysis is COMPLETE — **it
  needs an answer, not more analysis. Do not re-derive it.** Its own branch, its own `PLAN.md`
  up front; nothing about it belongs on this one.
- **N2. `SelectButton` gets seed silence from emit timing, where its two siblings suppress.**
  `OptionMenu` emits with the default `when='now'`, so the seed lands before a handler can
  bind; `Select` and `TimeField` suppress a `when='tail'` emit. Pinned by
  `test_seeding_a_signal_does_not_fire_change`, which is the right call — but note the test
  binds *after* construction, so it pins the application-visible outcome and would not catch a
  `<<Change>>` forwarder added inside `OptionMenu.__init__` later.
- **N3. An off-list write into a shared signal now raises inside whatever wrote it** — at the
  caller's `set()` when that is application code, into the Tk event loop when it is another
  widget committing. `#369` already records `SelectButton` as raising on both doors and asks
  the selection family for one decision; the branch only extends the existing `value=`
  behavior to the signal door, and its test pins the raise rather than the state left behind.
  Correctly out of scope.
- **N4. Tests: no vacuity and no false-alarm finding.** Both files carry the controls that
  matter — `test_the_seeded_value_actually_landed` blocks the "seeding does nothing, so of
  course nothing was announced" vacuity, and the two `still_fires_change` tests block the
  over-suppression that would pass the headline test while silencing the widget. The
  value-not-count assertion is right given the pre-existing multi-emit quirk (measured here:
  `['2', '2']` for one set).
- **N5. For #466.** Its third amendment (an AST check that every `bs.<Widget>(kw=…)` in
  `docs/**/*.py` names a real parameter) would **not** have caught finding 1 twice over: the
  site is an `.rst` code-block, and the defect is an argument *value*, not a keyword name.
  What would catch it is narrower and cheaper — for the option-taking widgets, check that a
  `signal=`/`value=` seed named in a docs snippet is one of the options written beside it.
  Worth recording on #466; too big for this branch's cap.
