# PLAN — mode-3 strictness: unknown keyword names (#383 gap 3)

⚠ **PARKED 2026-08-21, NOT ABANDONED — this is a plan waiting for its branch, not the record of a shipped one.** It was moved out of the repo root so `PLAN.md` could hold #465, which gates the nearer release. **Move it back to `PLAN.md` when `fix/unknown-kwarg-strictness-383` is cut**, and re-check the base SHA below before trusting it.

⚠ **Its milestone was RE-CONFIRMED the same day, so do not re-open the question:** #383 stays on `0.5.0`, not `0.4.0`. `0.5.0`'s other three issues (#369, #408, #416) all change what the framework accepts or returns, so moving #383 forward would not spare users a migration — it would give them **two** strictness migrations instead of one. That is the "breaks batched, not dribbled" rule, and it is the whole reason for the grouping.

**Issue:** [#383](https://github.com/israel-dryer/bootstack/issues/383) · **Milestone:** `0.5.0 — Strictness and value types`
**Branch:** not yet cut — suggested `fix/unknown-kwarg-strictness-383`
**Base when written:** `main` @ `c9fda068` — ⚠ **STALE, and it will keep going stale while this sits parked.** Re-base on `main`'s tip when the branch is cut; the analysis below does not depend on the SHA, but a round record that quotes it will.
**Status:** ⏭ **NOT STARTED, NO LONGER BLOCKED.** §1 was answered by the maintainer 2026-08-21 — **default-strict at the seam, with a declarative class-flag opt-out.** Everything below is measured and settled.
**Round cap: 3** — it lands on a minor.

Analysis done 2026-08-20; **the numbers come from the merged audit (#463, PR #464) and were re-verified against the source, not recalled.**

---

## What is broken

`bs.TextField(bogus_xyz=1)` constructs silently. The internal it wraps does not:

```
bs.TextField(bogus_xyz=1)        -> constructs, the name is discarded
TextEntry(None, bogus_xyz=1)     -> TclError: unknown option "-bogus_xyz"
```

**The public layer is the less strict of the two.** Wrappers build `internal_kwargs` from named parameters only; `**kwargs` exists to feed `_split_layout_kwargs`, and whatever survives the split is never read again. A typo'd real parameter (`densty="compact"`) and a typo'd layout key (`filll="x"`) both vanish the same way.

## The population — measured, not estimated

Of the **52** public wrappers with a `**kwargs` catch-all:

| policy | count | who |
|---|---|---|
| **DROPPED — the defect** | **40** | Accordion, Avatar, Badge, Button, ButtonGroup, Calendar, Card, Carousel, CodeEditor, Column, DataTable, DateField, Divider, Form, Gallery, Gauge, Grid, GroupBox, Label, ListView, NumberField, PageStack, PasswordField, PathField, ProgressBar, RadioGroup, RangeSlider, Row, ScrollView, Select, SelectButton, Slider, SpinnerField, SplitView, Tabs, TextArea, TextField, TimeField, ToggleGroup, Tree |
| REJECTED — already correct | 5 | Checkbox, Radio, RadioToggleButton, Switch, ToggleButton |
| FORWARDED, and calls the split | **5** | Chart, MenuButton, Picture, StatusBar, Toolbar |
| FORWARDED, never calls the split | 2 | App, Window |

⚠ **`App` and `Window` ARE NOT A THIRD SHAPE — an earlier reading of this said they were.** They forward deliberately (`app.py:172` `init_kwargs.update(app_kwargs)`, `window.py:179` `init_kwargs.update(kwargs)`) and simply never call `_split_layout_kwargs`, because a top-level window is never placed in a layout. **A seam-based guard does not touch them and they need no opt-out.**

Reproduce any of this with `py -3.12 development/probe_wrapper_parameter_delta.py --arm leftovers` (constructs all 52 and compares against the static verdict: 51 agree, 0 disagree).

## The fix already ships

`_BooleanControlBase.__init__`, covering five public widgets today:

```python
layout_kw = self._split_layout_kwargs(kwargs)
if kwargs:
    raise TypeError(
        f"{type(self).__name__}() got unexpected keyword argument(s): "
        f"{', '.join(sorted(kwargs))}"
    )
```

**There is no design work here. There is only placement.**

---

## §1 — ✅ DECIDED (maintainer, 2026-08-21): DEFAULT-STRICT AT THE SEAM, DECLARATIVE OPT-OUT

`_split_layout_kwargs` itself rejects whatever survives the split. The **5** deliberate forwarders (Chart, MenuButton, Picture, StatusBar, Toolbar) opt out with a **class flag**, not a per-call keyword. **~5 edits, not 40.**

```python
# _core/base.py — the seam
def _split_layout_kwargs(self, kwargs):   # was @staticmethod
    layout_kw = _pop_layout_keys(kwargs)
    if kwargs and not getattr(type(self), "_forwards_kwargs", False):
        raise TypeError(
            f"{type(self).__name__}() got unexpected "
            f"keyword argument(s): {', '.join(sorted(kwargs))}"
        )
    return layout_kw

# toolbar.py — and the other four forwarders
class Toolbar(PublicWidgetBase):
    _forwards_kwargs = True   # forwards leftovers on purpose
```

**The rejected option, so it is not re-proposed:** opt-in, a sibling `self._reject_unknown_kwargs(kwargs)` after each of 40 splits. ⚠ **Under opt-in the next wrapper anyone writes silently joins the 40.** Under default-strict a new wrapper is strict for free and the drift cannot recur. Given the defect class this whole milestone exists for — *"the wrappers were not sufficiently designed or reviewed"* — a fix that has to be remembered is the wrong shape. **The edit count was never the reason.**

⚠ **The class flag was chosen over a `strict=False` keyword deliberately** — see §1's second-order argument below. It is what collapses the durable guard (§5) to about ten lines instead of another source scan.

**The seam is cheaper than it looks.** `_split_layout_kwargs` is a `@staticmethod` (`_core/base.py:119`), so it cannot name the widget in an error message — but **all 51 call sites already spell it `self._split_layout_kwargs(...)`** (verified: `grep -rn "_split_layout_kwargs(" | grep -v "self\._split_layout_kwargs"` returns nothing). Converting it to an instance method is source-compatible at every call site and yields `type(self).__name__`, which is exactly what the shipped guard uses.

**Second-order argument for a DECLARATIVE opt-out** (the class flag over the keyword): the durable guard (§5) collapses to about ten lines — *assert every public wrapper either rejects an unknown keyword or is on the opt-out list*. With a per-call-site keyword, that test has to go back to scanning source, which is the thing that cost this project five tool defects during the audit.

---

## §2 — ⚠ THE TRAP: four crafted error messages die silently

`Select` (`select.py:117-118`), `DateField` (`datefield.py:101-102`), `NumberField` (`numberfield.py:124-125`) and `TimeField` (`timefield.py:91-92`) all do this, **in this order**:

```python
layout_kw = self._split_layout_kwargs(kwargs)     # <- runs FIRST
if "textsignal" in kwargs:
    raise TypeError("Select does not accept 'textsignal=' — a select binds the option's value, not the label shown for it. Use signal= …")
```

**Make the split strict and the generic error fires before the specific one ever runs.** Four bespoke messages become unreachable — including #458's public explanation of a deliberate behaviour change.

**Fix: move each `textsignal` check ABOVE its split.** Trivial, but it must be done in the same commit, and ⚠ **these four are exactly the wrappers most likely to be skipped**, because they *look* strict already. **A specific-key guard is not a leftover guard** — the audit's own static pass credited all four with rejecting until construction disproved it.

**Pin it with a test.** Each of the four should have a test asserting the *specific* message survives, or the next simplification re-orders them back.

## §3 — What does NOT collide (checked, not assumed)

Legacy layout kwargs never reach the new guard. `fill`, `expand`, `anchor`, `sticky`, `side` are all in `PACK_KEYS`/`GRID_KEYS` (`_core/container.py:6-32`), so the split pops them into `layout_kw` and `_reject_legacy_child_kwargs` rejects them at attach time with the flex-vs-grid-specific message. **The ordering is already correct by construction.** Do not add a second rejection path for them.

A *typo* of a layout key (`filll="x"`) is not a layout key, falls through, and is caught by the new guard. That is intended.

## §4 — Open sub-questions (not blocking; decide during, not before)

- **Should the 5 forwarders get a better error rather than an opt-out?** `bs.Toolbar(bogus=1)` today reaches the internal and surfaces a raw `TclError: unknown option "-bogus"`. That is #383's *other* complaint — "args that raise but leak a raw `TclError`/`AttributeError`" — so it may want folding in rather than exempting.
- **Should the message attempt "did you mean?"** The audit's vocabulary resolver already computes the candidate set (`internal_signature()` in the probe unions `Unpack[TypedDict]` over the internal's MRO). ⚠ **But #426 is the precedent for an error that confidently recommended the wrong thing** — it advised kwargs that had been renamed before release.
- **Cosmetic, unrelated, do not scope-creep it:** `App`'s catch-all is `**app_kwargs`, against the standing "catch-all must be named `**kwargs` throughout" convention.

## §5 — The follow-on, deliberately NOT in this branch

A parameter-level guard test written to the audit's five failure modes. **This branch makes it cheap** (see §1's second-order argument) but does not build it.

⚠ Two things it must not inherit:

- `tests/test_public_surface.py`'s blind spot — it gates the top-level *name set* and never asserts a submodule is unreachable as `bs.*`, which is how the `bs.events.X` drift survived two months.
- The audit probe's coverage hole. **84 params across `AppShell` (31), `Workbench` (34), `ThemeToggle`, `Notification` and `Snackbar` are UNANALYZED, not clean.**

---

## Scope boundaries

**IN:** the guard, its placement, the 5 opt-outs, the 4 re-orderings, tests for each.
**OUT:** #383's other two gaps (bad *values*, and raw `TclError` leakage) unless §4 folds the second in deliberately — **say so in the commit if it does**. Also out: the durable guard (§5), and every `_impl` naming inconsistency the audit turned up.

## Verification

- **Before/after, both measured:** `--arm leftovers` must move all 40 from `dropped` to `rejected`, and must leave the 5 opt-outs and 5 already-correct wrappers unchanged. ⚠ **Run it on `main` first** — a baseline claimed rather than observed is how this project has been burned repeatedly.
- **The 4 crafted messages:** assert the specific text, not just that *something* raised.
- **Full suite** on the Windows box, `py -3.12 tests/run_gui.py`. Baseline at `6b2a3219` is **1500 passed / 22 skipped, 33 legs, exit 0** with `matplotlib` and `pandas` both present — ⚠ check both imports before comparing, or you will re-open this file's ninth count discrepancy.
- ⚠ **Expect test churn:** any existing test passing a bogus kwarg to a wrapper starts failing. That is the fix working, but count them before assuming.
