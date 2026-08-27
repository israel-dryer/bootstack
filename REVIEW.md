# REVIEW — #390 round 2

**Reviewed:** `git diff main...HEAD` in full, not the incremental diff — the design was replaced
mid-branch (`590bfa87`), so round 1's baseline describes a `nullable=` parameter that no longer
exists. **Round 1's record is at `725b3990`**; what still binds from it is folded into "Settled"
below.

**Cap 3 (`PLAN.md`), spent 2.** Seven findings, **all seven reproduced** — verified independently
by construction before any was acted on, not read off the source. Four were fixed (`d0c0c591`),
two became docs corrections, one was already dispositioned.

⚠ **The instrument is `development/probe_390_review_round2_verify.py`.** One arm per finding,
each printing HOLDS or REFUTED. It read `HOLDS` seven times before the fix and now reads REFUTED
for F1–F4. **Re-run it rather than re-deriving any of this.**

---

## Findings and dispositions

| # | what | verdict |
|---|---|---|
| **F1** | **The `_realize()` empty-guard missed every signal seeded empty**, so the exact binding it exists to refuse went through | **HIGH, FIXED** |
| **F2** | **An empty-seeded signal always realized as a `StringVar`**, so it stopped returning its own type | **HIGH, FIXED** |
| **F3** | **`clear()` bypassed the `allow_empty` declaration entirely once the signal was realized** | **MEDIUM, FIXED** |
| **F4** | **A `set`-typed signal emptied to `''`**, which `SetVar` refuses | **MEDIUM, FIXED** |
| **F5** | **What "empty" means is decided by whether the signal is realized**, so a second binding changes the first one's clear | **MEDIUM — DOCS CORRECTED, MECHANISM KEPT.** See below; it is forced, not chosen |
| **F6** | **`map()` does not propagate `allow_empty`**, so the guard the docs recommend does not work | **MEDIUM — DOCS CORRECTED.** Decision 4 stands |
| **F7** | A push the signal's type cannot take is swallowed by `_push_to_signal` | **NO ACTION — already dispositioned.** See below |

### F1 and F2 — one root, and it was in the plan, not just the code

`Signal(None, allow_empty=True)` left `_type is None` until the first non-empty `set()`.
**`self._type in (bool, int, float)` is False while the type is deferred**, so
`bs.Slider(signal=bs.Signal(None, allow_empty=True))` **built**, and then:

```
File "...slider.py", line 342, in _value_to_pos
    ratio = max(0.0, min(1.0, (val - self._minvalue) / span))
TypeError: unsupported operand type(s) for -: 'str' and 'float'
```

on stderr from a Tk callback, app still running, `slider.value` returning `''`. **That is verbatim
the failure `_realize()`'s own comment at `:169-174` says the guard prevents**, reached by the
spelling the CHANGELOG advertises two sentences before promising a slider binding raises.

⚠ **THE PLAN CONTAINED THIS, NOT ONLY THE CODE.** `PLAN.md` specified both the deferred type and
the `bool`/`int`/`float` guard, in adjacent bullets, and did not notice they cannot both hold.
**A design review would have caught it; reading the diff for implementation fidelity would not.**

Second, `_create_variable` dispatched on the **seed**, which is `None`, so it fell through to the
`else` branch: an empty-seeded signal was a `StringVar` for life. After `set(5)` it reported
`type is int` while `__call__` returned `'5'`, subscribers received `'7'`, and `clear()` raised
`Expected int, got str` **out of the signal's own setter**.

**Fixed by replacing deferred inference with a declared `dtype=`** — required when the seed is
`None` and `allow_empty=True`, honored whenever given, seed checked against it. The full rule and
the two rejected alternatives (*reject* beside a value seed, *ignore* beside one) are in
`PLAN.md`; **do not re-propose either.**

⚠ **`Signal.type` is `Type[T]` again.** The deferred design retyped it to `Type[T] | None`, which
is `0.5.0`'s membership rule; the declared type removes that retype from the branch entirely.

### F3 — the rule was true only where the test looked

`clear()` called `set(self._empty_value())`, and `_empty_value()` returns `''` for a realized
non-object-mode signal — **a perfectly valid `str`, so `set()`'s `value is None` guard never
ran.** `bs.Signal("hello")` with no declaration, bound to a `TextField`, cleared successfully.

⚠⚠ **`test_clear_still_needs_the_declaration` asserts *"One rule, whatever the type"* and both of
its arms were UNREALIZED, so it passed while the rule it states was false.** This is the same
shape as #476 round 1's durable finding, one turn out: **a test can be green on a broken build
because the arm that breaks is the arm it does not have.** It has a realized arm now, with a
precondition asserting the binding realized the signal.

**Fixed by `clear()` calling `set(None)`**, so it routes through the declaration check instead of
around it.

### F4 — a plan assertion that was not checked

`PLAN.md` says every non-refused type realizes as a `StringVar` *"(or `SetVar`), which can"* hold
an empty. **`SetVar.set('')` raises `Expected set or frozenset, got str`** — so
`bs.ToggleGroup(mode="multi", signal=bs.Signal({"a"}, allow_empty=True))` built and `clear()`
raised out of the caller.

**Fixed by `_empty_value()` returning `set()` for a `set`-typed signal, realized or not** — a
deliberate departure from the binding-decides rule, because **the empty set is a legal value of
the type in both stores**, where `''` is legal only because a `str`'s empty happens to be a `str`.
Pinned on both arms so realization cannot move it.

### F5 — the mechanism is forced by the toolkit, so only the docs were wrong

`_empty_value()` keys on `self._var is not None`, which flips when anything touches `.var`. A
`Select` bound to `bs.Signal("1", allow_empty=True)` clears to `None`; add `bs.Label(textsignal=)`
on the same signal and it clears to `''` while `select.value` is still `None`.

⚠ **THE SCOPE IS ONE TYPE, AND WORKING THAT OUT IS WHAT DECIDED THE DISPOSITION.** `''` is
returned only when realized **and** native-mode. `bool`/`int`/`float` with `allow_empty` are
refused at realize (F1's guard), `set` is now `set()` either way (F4), and object-mode types like
`date` always return `None` regardless. **Only `str` can diverge** — the one type a text widget's
variable and a `Select`'s option values both use.

⚠⚠ **AND IT CANNOT BE FIXED BY MAKING THE PROXY HONEST, WHICH WAS THE OBVIOUS MOVE.** Once a
native-mode signal is realized, **`None` cannot survive the round trip**: a Tk variable cannot
hold it, so `set()` writes `''`, the bridge trace reads the var back, and `_last` becomes `''` —
**even if `_empty_value()` had returned `None`.** So `_var is not None` is not a proxy for "is
this the widget's variable"; it is the operative condition itself, *"does a Tk variable now own
this value"*. **A flag set at bind time would change nothing observable. Do not build one.**

**The docs claim was the defect** and it is corrected: *"The signal always agrees with the widget
it is bound to, so comparing `signal()` against the widget's `value` is safe either way"* was
false, in `signals.rst` and in the CHANGELOG bullet. Both now name the one case where it cannot
hold and point at the falsiness check the same passage already recommended.

### F6 — decision 4 is right; the guard it recommends was not

Decision 4: *the transform is called with the source's empty and the author guards.* **The
recommended guard does not work.** `lambda x: x.isoformat() if x else None` returns `None`, and
the derived signal from `Signal(transform(self()))` was never declared able to hold one, so
`src.clear()` raises `Expected str, got NoneType. Pass allow_empty=True to Signal()` — **advice
the caller cannot act on for a signal they did not construct.** Worse, when the same clear arrives
through a bound field, `_push_to_signal`'s `except TypeError: pass` swallows it: source reads
`None`, derived still reads `'2024-05-05'`, no error anywhere.

⚠ **Propagating `allow_empty` into the derived signal is now WORSE, not merely out of scope** —
the derived signal would need a `dtype` too, and it cannot be known while the source is empty. That
means `map(transform, dtype=…)`, which is widening `map()`, excluded by `PLAN.md`.

**Docs-only, as decision 4 said, with the rule stated precisely: return a value, never `None`.**
⚠ The shipped examples were already right (`docs/examples/datefield.py`, `timefield.py` both use
`if d else ""`); **only the new prose was loose.** The silent half is F7's swallow, not a
separate defect.

### F7 — already dispositioned, and the branch's claim to that is now stronger

Round 1's finding 7, dispositioned by the maintainer 2026-08-27 as pre-existing and **not to be
filed**, recorded in `PLAN.md` only. The reviewer re-derived it without that context.

⚠ **What changed: the plan justified it partly as *"the branch widens its reach"*, because
deferred typing let a field's first write decide the type. With `dtype` that widening is gone** —
the type is declared at construction, so a mismatch now requires the author to declare a type the
bound field cannot produce. **The branch no longer widens it at all.**

---

## Settled — do NOT re-derive or re-propose

| | |
|---|---|
| the four #390 decisions | Maintainer, 2026-08-26, in a **comment** on the issue |
| decisions 5 and 6 (accept where the variable has an empty member; widen to the 11 `StringVar` bindings) | Maintainer, 2026-08-27 |
| **`dtype` is honored whenever given, not rejected and not ignored** | 2026-08-27. Rejecting breaks the computed seed (`bs.Signal(record.get('due'), allow_empty=True, dtype=date)`, where whether the seed is `None` is **data**); ignoring makes `Signal(5, dtype=str)` an `int` signal, which is the audit's mode 5 |
| **the seed is CHECKED against `dtype`, never coerced** | Coercing would accept `Signal('5', dtype=int)` at birth while `sig.set('5')` raised forever after — two type policies on one object |
| **`dtype` takes the type, not `Form`'s string spelling** | `FieldItem.dtype` accepts `'date'` and `date`; a signal's takes only the type. Unifying belongs to the `dtype`/codec follow-up |
| **F5's mechanism** | Forced by the toolkit, not chosen. **A bind-time flag changes nothing observable** |
| per-type empties, the `'None'` sentinel string | Rejected before this branch. `725b3990` carries the measurements |

## Notes — gate 2, not fixes

- The refusal tests (`..._to_a_checkbox_raises`, `..._to_a_slider_raises`) exercised **only the
  value-seeded arm**, which is why F1 survived them. Both are parametrized over `value-seeded`
  and `starts-empty` now. **The empty-seeded arm fails on the pre-fix build; the value-seeded arm
  passes on both** — that asymmetry is the whole point of the parametrize.
- `test_clear_still_needs_the_declaration` — see F3. Vacuity-adjacent under gate 2: it did not
  pass while the behavior was broken *in general*, it passed while the rule in its own docstring
  was false.
- **Control run for the fixes, at the shipped commit:** reverting `clear()` and `_empty_value()`
  turns exactly the three new assertions red — `DID NOT RAISE`, `Expected set, got str`,
  `None == set()`, all behavioral, none an `AttributeError` — while the other 37 stay green.

## Suite

**1619 passed / 22 skipped, 33 legs, exit 0** — Windows box, `py -3.12 tests/run_gui.py`,
`matplotlib` and `pandas` both present. Reconciles as `1579 + 40` against `main`, bounded with
`git diff main...HEAD --stat -- tests/`, which returns `test_signal_empty.py` and nothing else.
Docs clean-build warning-free under `-W`.

## Process — the review prompt carried the author's residual doubts

The prompt supplied six labelled doubts and told the reviewer to find what was **not** on the
list. **Outcome: 3 of the 7 findings originated outside it** (F3, F4, F6). Of the doubts, two
became findings (F1/F2 from doubt 2, F5 from doubt 1) and one retired itself (doubt 4 — the
`Signal.type` retype no longer exists). **The anchoring risk the prompt flagged did not
materialize**, and the count is recorded here because a round that dispositions only the author's
own list looks thorough and is not.

⚠ **Doubts 3, 5 and 6 are UNEXAMINED, by this round and by round 1** — `set(None)` normalizing
silently rather than raising; `SpinnerField(textsignal=Signal(1.0, allow_empty=True))` refusing
while a `str` seed accepts (still true — a `float` seed realizes a `DoubleVar`); and
`from_variable` forcing `_allow_empty = False`. **Not findings, not cleared either.**

⚠⚠ **THE REVIEWER WAS POINTED AT THE DIFF AND NOT AT `PLAN.md`, AND IT COST A FINDING'S WORTH OF
ATTENTION.** F7 was re-derived after the maintainer had dispositioned it, and F6's obvious fix had
been excluded by a decision the reviewer could not see. **This is the mirror of "hand `REVIEW.md`
to the next reviewer": hand `PLAN.md` too** — the out-of-scope section exists precisely to stop
this, and it only works if the reviewer reads it.

## If a round 3 is opened

Cap allows one. `git diff d0c0c591^..d0c0c591 -- src/` is non-empty, so a round is **owed** by
gate 1. The new surface is `dtype=`, `_reconcile()`, `_is_tk_native_type()`, `_create_variable`'s
dispatch, `clear()` and `_empty_value()`. **Hand over this file and `PLAN.md`.** The three
unexamined doubts above are the obvious unswept ground.
