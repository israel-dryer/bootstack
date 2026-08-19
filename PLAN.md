# PLAN — #456: `DataTable(context_menus=...)` is documented but never reaches the widget

**Issue:** [#456](https://github.com/israel-dryer/bootstack/issues/456) — *DataTable cannot close the right-click menu, the `context_menus` parameter is invalid*, reported by `@yaojia25` against `0.3.2` on Windows 11
**Branch:** `fix/datatable-context-menus-456` (off `main` at `2a55ff96`)
**Milestone:** `0.3.x — Patch line` *(maintainer, 2026-08-18 — "a patch", answering the scope question below)*
**Round cap:** **2** (patch line, per `REVIEW-PROTOCOL.md` gate 3)

---

## The report

> `bs.DataTable(context_menus="none")` — when I run the app, right-click on header or rows, the context menu will still be displayed.

The reporter also read the source and landed on the right line themselves: `context_menus` never makes it into `internal_kwargs`.

## Root cause — confirmed by probe, with a control

`context_menus` is **not a parameter of `DataTable.__init__`** (`src/bootstack/widgets/datatable.py:107-134`). It therefore falls into `**kwargs`, is handed to `self._split_layout_kwargs(kwargs)` as though it were a layout placement option, matches nothing, and is discarded without error. The internal never hears about it and applies its own default.

The internal `TableView` implements the feature correctly and completely — this is purely a wrapper plumbing failure:

| `tableview.py` | what it does |
|---|---|
| `:288` | `context_menus: Literal['none','headers','rows','all'] = 'all'` |
| `:411` | `self._context_menus = (context_menus or 'all').lower()` |
| `:1159` | binds the right-click handler **only** when `!= "none"` |
| `:1247` | `_header_context_enabled()` → `in ("all", "headers")` |
| `:1250` | `_row_context_enabled()` → `in ("all", "rows")` |
| `:3034` | `_on_tree_context` early-returns when `== "none"` |

Measured on the macOS box (`.venv/bin/python`, Python 3.14, Tk 8.6), `development/probe_456_context_menus.py`:

```
public wrapper, context_menus="none"   ->  internal _context_menus = 'all'    <- the bug
CONTROL: internal constructed directly ->  internal _context_menus = 'none'   <- feature works
```

**The control is the load-bearing half.** It proves the gate itself is sound, which is what scopes this fix to the wrapper and keeps `tableview.py` out of the diff entirely.

## Why it was invisible

This is the mechanism already recorded as **#383's third gap** ([comment](https://github.com/israel-dryer/bootstack/issues/383#issuecomment-5283453605)): public wrappers build `internal_kwargs` from **named parameters only**, and `**kwargs` exists to feed `_split_layout_kwargs`, so any name the wrapper does not declare is swallowed silently. `bs.DataTable(context_menus="none")` and `bs.TextField(bogus_xyz=1)` are the same failure.

The docs make this one worse than a typo: `docs/widgets/datatable.rst:566-573` **teaches** the argument, with a worked example. The public layer promises a feature it cannot accept.

`docs/_dev/widget-api-audit.md:337` already listed the `context_menus` gate as an unexposed DataTable capability, so the gap was known internally — filed as a missing exposure, never as a bug. It became a bug the moment the docs page taught it.

---

## Scope

### In

1. **`datatable.py`** — add `context_menus: Literal["none", "headers", "rows", "all"] = "all"` to `__init__`, validate it, forward it into `internal_kwargs`.
2. **Docstring** — an `Args:` entry, matching the docs page's wording.
3. **Tests** — pass-through and gate behavior (below).
4. **CHANGELOG** — re-create `## [Unreleased]` (absent on `main`; `0.3.2` consumed it) with a `### Fixed` bullet.

### Out — deliberately, and why

- ~~**`tableview.py` is untouched.**~~ ⚠ **REVISED 2026-08-19 — it is now in the diff.** See "The event coupling" below. The original reasoning held for the pass-through fix itself: the internal resolves and gates the value correctly, which the probe's control arm proves. What it missed is that making the argument reachable made a *pre-existing* gate reachable with it.
- **No live `context_menus` property.** Standing principle `feedback_live_properties_runtime_need`: a property is live only when changing it has a complete effect a user would bind to a control. DataTable's four existing properties (`selection`, `current_page`, `page_count`, `data_source`) are all *runtime state*; every construction flag beside this one (`striped`, `density`, `show_status_bar`, `show_column_chooser`, …) is construction-only. A property here would also be *more* public surface than the fix needs, and would push the release question below firmly to a minor. **A setter would technically work** — `:1247`/`:1250`/`:3034` re-read the attribute on every click, though `:1159`'s binding is installed once — which is exactly why this needs to be a decision on the record rather than an omission.
- **The general #383 gap.** Fixing the seam that swallows unknown names is `0.4.0 — Strictness and value types` work, and the audit it needs (counting wrappers that legitimately forward `**kwargs`) is not this branch's. **Cross-reference #456 from #383 as a concrete user-facing instance** — the individual fix does not stop the next one.
- **The other unexposed DataTable capabilities** at `widget-api-audit.md:337` (`move_rows`/`hide_rows`, `show_hscrollbar`, `search_mode`, `first_page`/`last_page`). Those are genuine additions and need a minor.

---

## Which line does this ship on? — the one real decision

**Not mine to make; flagged rather than assumed.** The two readings:

| reading | argument |
|---|---|
| **Fix** (recommended) | The documented public contract of `DataTable` already includes `context_menus`. Restoring conformance to what ships in the docs is a bug fix; a user reading `bootstack.org` today already believes this argument exists. |
| **Addition** | Mechanically `DataTable.__init__` gains a name. On `0.3.2` the call is impossible; on `0.3.3` it works. Per the standing rule, *adding public surface is a MINOR even when nothing breaks*. |

⚠ **#453 is the nearest precedent but is NOT identical, and the difference is exactly the one that matters here.** There, `read_only` was already in the `Select` signature and merely ignored — nothing was added, so the patch line was uncontroversial. Here the signature genuinely grows.

Recommendation is **patch**, on the strength of the docs already promising it, but the maintainer should confirm before the CHANGELOG bullet is written as a `### Fixed`.

✅ **DECIDED: patch** (maintainer, 2026-08-18). The CHANGELOG bullet stands as `### Fixed` and #456 goes on `0.3.x — Patch line`. ⚠ Worth carrying as precedent, because it is **not** the same call as #453's: this one *does* add a name to a public signature and was taken as a patch anyway, on the grounds that the shipped docs already promised the argument. The rule that survives is unchanged — an addition needs a minor — but **a wrapper that fails to accept what its own published docs teach is a defect in the wrapper, not a missing feature.**

---

## The event coupling — added 2026-08-19, after the first two commits

**Missed at scoping, and it was already written down.** [#383's comment of 2026-08-06](https://github.com/israel-dryer/bootstack/issues/383#issuecomment-5202818511) recorded this exact defect twelve days before #456 was filed, with its own probe (`development/probe_417_context_menus_reachable.py`), and closed with a warning this plan did not act on:

> wiring it through is not purely additive — `context_menus="none"` also silences `on_row_right_click` […] That may well be the intended reading of "disable them", but it should be a deliberate call rather than a side effect.

It shipped in `e97b91ff` as a side effect. **Measured, and worse than predicted — `'headers'` silences it too:**

| `context_menus` | header menu | row menu | `on_row_right_click` (before decoupling) |
|---|---|---|---|
| `'all'` | ✓ | ✓ | ✓ |
| `'headers'` | ✓ | ✗ | **✗** |
| `'rows'` | ✗ | ✓ | ✓ |
| `'none'` | ✗ | ✗ | **✗** |

`<<RowRightClick>>` is emitted inside `_on_row_context`, one line before the menu is shown, and the whole method sat behind `_row_context_enabled()`. So the event tracked the **row menu** rather than the right-click. `'headers'` was the incoherent case: `<Button-3>` still bound, header menu still opening, widget visibly alive — and the row event silently dead.

✅ **DECIDED: decouple** (maintainer, 2026-08-19 — *"I would not expect that argument to affect `on_row_right_click`"*).

**`context_menus` chooses which menus the table offers; it does not choose whether a right-click is reported.** Three edits in `tableview.py`:

1. `:1159` — `bind_right_click` is now unconditional. ⚠ **This is the pre-`0.3.2` binding behavior restored**, not new: the kwarg never landed before #456, so every table bound it.
2. `_on_tree_context` — the blanket `== "none"` early return is gone; the header branch keeps its own gate, the row branch dispatches always.
3. `_on_row_context` — the leading `_row_context_enabled()` guard moved to *below* the emit, so it gates the menu only.

⚠ **The precedent was already in the file, three lines below the edit.** `on_row_double_click` is bound unconditionally with the comment *"public API and does not depend on editing"* — #417's fix, the same rule for the same reason. The new comment mirrors it deliberately.

**The user-visible consequence: `on_row_right_click` behaves exactly as it does on `0.3.2`, for all four values.** Nothing about the event changes for anyone; only the menus become controllable. That strengthens the patch-line call rather than weakening it.

**Tested in `tests/widgets/public/test_datatable_right_click_event.py`**, driving a real `<Button-3>` rather than reading the gate — the gate is what moved, so asserting on it would restate the implementation. Both halves are pinned: the event fires for all four values, **and** the menu still obeys all four, so a "fix" that merely deleted the gate would fail the second half.

**Non-vacuity, measured:** against the pre-decoupling commit, exactly `[headers]` and `[none]` fail and the six menu-gating cases stay green.

## Invariants

1. **The default stays `"all"`.** Every `DataTable` ever constructed must behave byte-identically after this change. This is the whole compatibility argument for the patch line, and it gets its own test.
2. **Validation runs before parent resolution.** Per `choices.py`'s module docstring and pinned by an existing test (`test_bad_value_is_reported_before_parent_resolution`): a bad value must be reported as a bad value, not buried under "created outside a container".
3. **The public layer validates strictly against the lowercase set** — `validate_choice(context_menus, ("none","headers","rows","all"), ...)`, matching `selection_mode`/`sorting_mode`/`paging_mode` in the same constructor.
   ⚠ **This is deliberately stricter than the internal**, which does `(context_menus or 'all').lower()` and so accepts `"NONE"` and `None`. **Nothing can break**: the argument is unreachable from public code today, so there is no caller to grandfather. Strictness matters here more than usual because of the failure shape — a typo like `"nones"` passes `!= "none"` at `:1159` (menus get bound) but fails **both** predicates at `:1247`/`:1250`, so it **silently disables every menu**. That is the exact "reads as a broken widget rather than a typo" case `choices.py` was written for.

---

## Tests

Placed with their siblings, not in a new file.

**`tests/widgets/public/test_datatable.py`** — behavior. Assert the *named predicates*, not the raw attribute: `_header_context_enabled()` / `_row_context_enabled()` are the seams the click path actually consults, so a pass-through test that only reads `_context_menus` could pass while the gates disagree.

| `context_menus` | header | row | right-click bound (`:1159`) |
|---|---|---|---|
| default (omitted) | True | True | yes |
| `"all"` | True | True | yes |
| `"headers"` | True | False | yes |
| `"rows"` | False | True | yes |
| `"none"` | False | False | **no** |

The `"none"` row's binding check is the strongest observable and is closest to what the reporter sees.

**`tests/widgets/public/test_choice_guards.py`** — add to the existing parametrized tables: one `BAD` row (`context_menus="None"` — a plausible near-miss that also pins invariant 3's strictness) and one `GOOD` row covering all four valid values.

**Non-vacuity, per the standing rule.** Each new test must be run against `main`'s wrapper and observed to fail for the *right* reason — the behavior tests must fail on the gate assertion, not on `TypeError: unexpected keyword argument`. Since `main` silently swallows the kwarg, they will fail on the assertion; **confirm that rather than assume it**, and record the pre-fix output in `REVIEW.md`.

## Verification

1. `.venv/bin/python tests/run_gui.py` — exit 0, all legs, counts recorded **with the commit SHA and date** beside them, reconciled against the shared leg's own collection line and bounded by `git diff --stat main..HEAD -- tests/`.
2. The issue's exact repro script, by hand, right-clicking both a header and a row.
3. Clean docs build — `rm -rf docs/_build && sphinx-build -b html docs docs/_build/html -W --keep-going`. The docs page needs **no edit**; the point is to confirm its existing example is now true. Read the `context_menus` paragraph as a user once the fix is in.
4. Probe `development/probe_456_context_menus.py` committed, carrying both arms.

## Round cap

**2 rounds.** Survivors are filed as issues, not fixed here. Set now, before any findings exist.

---

# MEASURED — appended after implementation, for the reviewer

**Box:** macOS 26.5.2, `.venv/bin/python` = Python 3.14.0, **Tk 8.6**, editable install. **Date:** 2026-08-18. **`pandas` present** on this box, so the data leg is not the `125 / 4` pair.
⚠ These are **macOS** figures. Platform gating differs — do **not** compare them against the Linux `1427 / 22` in `CLAUDE.md` or reconcile the two by arithmetic.

### Probe — `development/probe_456_context_menus.py`, both arms

| | pre-fix (wrapper reverted via `git stash`) | post-fix |
|---|---|---|
| ARM 1 public wrapper | `all` for **every** input | tracks the argument |
| ARM 2 CONTROL internal | tracks the argument | tracks the argument |

The probe is shown capable of finding the defect, so the post-fix agreement means something.

### Non-vacuity — every new test run against the unfixed wrapper

**4 of 6** behavior tests and **1 of 2** guard rows fail pre-fix, **on the assertion, not on `TypeError`** — the argument was silently swallowed, so construction always succeeded:

```
assert True is False   where True = _header_context_enabled()
assert True is False   where True = _row_context_enabled()
assert not 'if {"[...]" == "break"} break'   where ... = bind('<Button-3>')
Failed: DID NOT RAISE <class 'bootstack.errors.InvalidChoiceError'>
```

The two that pass on both sides are correct and deliberate: the `[all]` case (pre-fix behavior coincides with the default) and `test_context_menus_defaults_to_all`, whose whole point is that it must pass either side.

### Suite — `.venv/bin/python tests/run_gui.py`

**exit 1**, 33 legs, **1466 passed / 1 failed / 33 skipped.**

The single failure is **`test_select_change_event_value_space` — [#449](https://github.com/israel-dryer/bootstack/issues/449), an already-filed flake** measured at ~1 in 10 full runs.

⚠ **Not dismissed by re-running** — the standing rule forbids that. The argument is scope: `git diff --stat main..HEAD -- src/` is **one file**, `src/bootstack/widgets/datatable.py`, which `test_select_options.py` cannot reach. Production changes and failing test do not intersect.

**Count movement bounded rather than asserted**, per the rule that has caught this file out seven times. `--collect-only` over the two changed test files: **main 53 → branch 61 = +8**, exactly the 8 tests added (4 parametrized gates + default + unbound-handler + 1 `BAD` row + 1 `GOOD` row). Nothing else moved.

### Docs

Clean `-W --keep-going` build after `rm -rf docs/_build`: **exit 0, no warnings.** `context_menus='all'` now renders in the `DataTable` signature in the API Reference. `docs/widgets/datatable.rst` needed **no edit** — the point was to make its existing example true, which it now is.

### The reporter's script

Their code verbatim, with an introspection callback in place of a human right-click:

```
resolved         : 'none'
header menu      : False
row menu         : False
right-click bound: False
```

⚠ **A human right-click on a header and a row is still worth doing** before merge. Every check above is an assertion about the gates; nobody has watched the menu fail to appear.

### ⚠ One process note worth carrying

Appending the tests with a heredoc **flipped 61 lines of `test_datatable.py` to LF in a CRLF file**, and `git diff --stat` showed the correct `61 insertions(+)` either way — the flip was invisible to it, exactly as `CLAUDE.md` warns. The only signal was the *"LF will be replaced by CRLF"* warning on stderr. Rewritten to uniform CRLF in binary mode and re-verified with `file`; the diffstat is unchanged at 67 insertions and the tests still pass. **Use the Edit tool for appends to existing files on this repo.**