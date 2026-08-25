# PLAN — mode-3 strictness: unknown keyword names (#383 gap 3)

✅ **UNPARKED 2026-08-25 — the branch is cut and this file is back at the repo root.** #465 shipped (PR #471) and freed it. The base SHA below has been re-based on `main`'s tip, as the parked note required.

⚠⚠ **THE MILESTONE MOVED, 2026-08-25 (maintainer). This paragraph used to say "do not re-open the question" — it was re-opened and the answer changed, so read this and not the old reasoning.** Gap 3 is now its own issue, **[#472](https://github.com/israel-dryer/bootstack/issues/472), on `0.4.0`**. **#383 keeps gaps 1 and 2 and stays on `0.5.0`** — those are about bad *values*, which is the batch #369/#408/#416 belong to.

**Why the batching rule did NOT argue for holding it, measured rather than asserted:** the rule minimizes the number of releases that force a migration, and **`0.4.0` already forces one** — #465's rule-type guard raises where the framework used to accept, and #461 breaks working code outright. Without gap 3 that is two migration-forcing releases (`0.4.0` and `0.5.0`); with it, still two. **The count does not move, so waiting buys nothing.** Gap 3's blast radius on *working* code is close to nil besides: the only behaviour that changes belongs to code passing a keyword that provably did nothing.

**Issue:** [#472](https://github.com/israel-dryer/bootstack/issues/472) (split out of [#383](https://github.com/israel-dryer/bootstack/issues/383) gap 3) · **Milestone:** `0.4.0 — Signal binding on fields`
**Branch:** `fix/unknown-kwarg-strictness-383`, cut 2026-08-25
**Base:** `main` @ **`339177f5`** (re-based 2026-08-25 when the branch was cut; it was written against `c9fda068`). ⚠ **A round record must quote THIS SHA**, and `git rev-parse origin/main` settles it rather than trusting the line.
**Status:** ✅ **IMPLEMENTED at `6808de00`, NOT YET REVIEWED.** §1 was answered by the maintainer 2026-08-21 — default-strict at the seam, declarative class-flag opt-out — and that is what shipped.
**Round cap: 3 · SPENT: 0.** ⚠ **THE REVIEWER MUST BE A FRESH SESSION** — the session that wrote this implementation also wrote this paragraph, which is exactly what `REVIEW-PROTOCOL.md`'s core rule exists to separate. **Round 1 reviews `git diff origin/main...HEAD -- src/`**: base `339177f5`, 74 insertions across 11 files.

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

## ⏭ WHAT THE IMPLEMENTATION ACTUALLY DID — written for the reviewer, by the implementer

**Read this before the diff.** It records where the implementation left the plan, so a round-1 finding
lands on the decision rather than re-deriving it. It is NOT an argument that any of it was right — that is
the review's job, and the plan's rationale sections below are deliberately not repeated here.

**In scope, as planned:** the seam guard (`_core/base.py`, `@staticmethod` → instance method plus the
raise), the five `_forwards_kwargs` opt-outs, the four `textsignal` re-orderings, tests for each.

### Three deviations, each of which a reviewer should weigh independently

1. ⚠ **`form.py` was changed, and it is NOT in the scope boundary below.** `choice_list()` returned as soon
   as `items` matched, leaving the losing `values` alias in the bag, where it reached `Select(values=[...])`.
   The split had been discarding it silently; the guard turns that into a hard failure, so the branch could
   not ship without it. **The test covering it says in its own comment that the alias "must not leak into
   the editor's constructor" — it did, and the test passed only because of the defect this branch fixes.**
   Whether a production fix outside the stated scope belongs in this commit is a real question.
2. **`test_chart.py` passed `surface="card"` to `bs.Card`, which has no such parameter** and computes its
   own surface from the parent. A silent no-op; removed. The assertion it guards still holds.
3. **The verification instrument was swapped.** See the Verification section — the probe the plan named
   would have reported this fix as a tool bug.

### ⚠ Three things the implementer did NOT verify, listed so silence is not read as coverage

- **That the five forwarders NEED the opt-out.** The plan asserts they forward on purpose; that was taken as
  given. What was checked is only that each still rejects a bogus key *via its internal*. §4 leaves open
  whether they deserve a real error instead of an exemption — unanswered here.
- **Where `_forwards_kwargs` should live.** It is a new class-level contract on `PublicWidgetBase`, chosen
  by the implementer without a second opinion.
- **Anything about #383's gaps 1 and 2.** Untouched, still on `0.5.0`.

## Scope boundaries

**IN:** the guard, its placement, the 5 opt-outs, the 4 re-orderings, tests for each.
**OUT:** #383's other two gaps (bad *values*, and raw `TclError` leakage) unless §4 folds the second in deliberately — **say so in the commit if it does**. Also out: the durable guard (§5), and every `_impl` naming inconsistency the audit turned up.

## Verification

- **Before/after, both measured.** ⚠ **`probe_wrapper_parameter_delta.py --arm leftovers` IS THE WRONG INSTRUMENT for this and would report the fix as a tool bug** — it compares the STATIC verdict against construction, so a wrapper whose source still looks like a dropper but now rejects reads as a DISAGREE, under a banner saying a disagreement is a probe defect. **Use `development/probe_383_unknown_kwarg_policy.py`**, which classifies by construction only. **Baseline OBSERVED on this branch before any edit: `dropped=40 rejected=10 other=0`** (the 10 are the 5 boolean controls plus the 5 forwarders, whose internals already raise). **Target: `dropped=0 rejected=50`.** Its `--arm control` proves both outcomes are visible, so a later `dropped=0` is a measurement and not a blind probe.
- **The 4 crafted messages:** assert the specific text, not just that *something* raised.
- **Full suite** on the Windows box, `py -3.12 tests/run_gui.py`. ⚠ **The baseline this file was written against (`6b2a3219`, 1500/22) is SUPERSEDED** — #465 and #449 landed since, and `main` at `339177f5` is **1524 passed / 22 skipped, 33 legs, exit 0** with `matplotlib` and `pandas` both present. Check both imports before comparing, or you will re-open this file's ninth count discrepancy.
- ⚠ **Expect test churn:** any existing test passing a bogus kwarg to a wrapper starts failing. That is the fix working, but count them before assuming.
