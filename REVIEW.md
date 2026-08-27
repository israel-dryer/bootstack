# REVIEW — #390 round 1

---

# ★ READ FIRST — THIS RECORD REVIEWED A DESIGN THAT HAS SINCE BEEN REPLACED. 2026-08-27.

**Round 1 reviewed the `nullable=` design and its findings were committed (`5352d9b9`,
`725b3990`). The branch was then RE-SCOPED by maintainer decision on 2026-08-27** — the concept
is now **empty**, not **null** (`Signal(v, allow_empty=True)`, `Signal.clear()`), and the 11
`StringVar`-backed bindings **accept** where the reviewed design refused all 16. **`PLAN.md`
carries the new design and the measurements behind it; read that first.**

**What survives from this record:** finding 1 (a `NoneType`-typed signal must keep no-opping on
`set(None)`) is carried into the new code and still pinned by its own test; finding 9's text fix
stands and its behavior half is now a *deliberate documented boundary* rather than an
undocumented one. **Findings 2–8 addressed code or wording that no longer exists.** The
"Settled" table below is still good history, except that the fifth question's answer — *refuse
to realize* — now applies only to `bool`, `int` and `float`, not to every binding.

⚠ **A round is still owed and it must be a FRESH session.** `git diff main...HEAD -- src/` is
non-empty and the code is substantially new. Cap 3 (`PLAN.md`), spent 1.

---

## Settled — do NOT re-derive or re-propose

| | |
|---|---|
| the four #390 decisions | Answered by the maintainer 2026-08-26 in a **comment** on the issue. Do it; **declared** `nullable=True`, not automatic; a non-nullable signal **keeps skipping silently**; `map()` **unchanged**, the author guards |
| the fifth question — a nullable signal **refuses to realize** | Made in `PLAN.md`, flagged for the maintainer, and since **corroborated structurally** (below). ⚠ Still wants a formal yes in its general form; **affirmed for boolean controls** on the evidence |
| tristate `Checkbox` + `signal=` | **Affirmed by the maintainer 2026-08-26: a checkbox does not support an indeterminate or null state with signals.** Consistent with ttk, which has **no tristate option at all** — measured, `[o for o in ttk.Checkbutton(root).keys() if "tri" in o]` is empty, a third value in the variable reads as "not on", and `alternate` is a widget state any variable write clears. **This branch neither caused nor worsened it** — `main` and the branch measure identically, and the seed block has read `if signal is None:` since #360 (`9a695588`) |
| the `'None'` string as a universal sentinel | **Rejected on measurement**, `development/probe_390_none_sentinel.py`. It is not the crash that kills it — it is that a user typing the ordinary word `None` produces identical bytes, the end user sees `None` on screen, and a swallowed `TclError` returns the **stale** value, which is the bug #390 exists to remove. The illegal-codepoint variant fixes only the collision |
| per-type empties (`empty(int)=0`, `empty(bool)=False`) | Rejected on #390 before this branch. **Do not re-propose** |

## Why the refusal belongs at `_realize()` and nowhere else

**`None` is representable in Python and provably not in Tcl, so it must stop at the crossing.**
The Tcl wiki's `null` page puts it as *"everything is a string, which implies that nothing is
null"*, completed by *"the concept of null requires a separate data type so it cannot be confused
with any other value."* Python has that separate type; Tcl does not. So this is a property of the
toolkit, not a limitation waiting to be lifted — it holds on every Tk version and every
`Variable` subclass.

`_realize()` **is** that crossing, and the crossings are enumerable rather than argued —
`grep -rn "self\._var = " src/bootstack/signals/signal.py` returns four: `:163` (`_realize`,
guarded), `:252` (`from_variable`, which sets `_nullable = False` because the var is already the
widget's), `:179` (`_drop_var` releasing) and `:42` (`_SignalTrace`'s own field, not a `Signal`).
`_create_variable` has exactly one caller, `:163`. **Two ways in, both closed.**

⚠ **The measured detail that decides it, and it is NOT what #390's body says.** Only `BooleanVar`
fails at write. `IntVar` and `DoubleVar` **accept** `None`, store the literal `'None'`, and
detonate at an arbitrary later `.get()` — possibly in another widget, another callback, a
repaint. `StringVar` displays the four characters. **Three of four corrupt, two with delayed
action.**

## Where nullability makes sense — the two gates

Census of all 24 public widgets taking a signal, `development/probe_390_signal_census.py`:
**16 realize** (the Signal *is* the widget's Tk variable), **8 stay pure Python**.

1. **Gate 1, mechanical — is the signal the widget's variable?** If yes, `None` cannot be stored.
   16 out, on measurement. **A property of the toolkit; it cannot change.**
2. **Gate 2, semantic — does the value type lack a natural empty member?** Of the 8 survivors:
   `NumberField`, `DateField`, `TimeField`, `Select`, `SelectButton` pass — `int`/`float`, `date`,
   `time` and an option key have no empty member. `TextArea` and `CodeEditor` **fail**: their value
   is text, `''` is already empty, and a second empty adds ambiguity without meaning. **`Chart` is
   the one genuinely open candidate** — arbitrary render payload, and "no data yet" is a real
   state. **A design judgment per widget; it could change.**

**The rule is self-maintaining**: a widget whose type has no empty member cannot be bound through
a Tk variable anyway, so it lands in the eligible set on its own. The five are not a hand-drawn
list.

⚠ **`RadioGroup` / `ToggleGroup` are the near-miss worth naming.** "Nothing selected" is genuinely
meaningful and structurally identical to `Select`'s case — but they are realized `StringVar`s
where unselected is `''`, so they fail gate 1 and would need the same Python-side rebinding a
tristate `Checkbox` would. **#369 is the home if it is ever wanted.** `Slider` is not a candidate:
a slider always has a position, and its `value = None` raw `TypeError` is #383's.

## OPEN — what the next session needs answered

1. **Formally affirm the fifth question** (refuse to realize) in its general form. Affirmed for
   boolean controls; the general yes is not on record.
2. **Is `Chart` a nullable candidate?** The only gate-2 survivor not decided. Out of scope here
   either way.
3. **`docs/widgets/checkbox.rst:102`** claims *"The checkbox and signal stay in sync"*
   unconditionally, which is measurably false in the indeterminate state (widget `None`, signal
   `False`, subscriber told `False`). Now that the boundary is **deliberate**, documenting it is
   correct rather than documenting around a defect. **Two lines, not written.**
4. **File finding 7?** `_push_to_signal`'s `except TypeError: pass` swallows the mismatch once a
   deferred type locks to `int`. Pre-existing, widened in reach.
5. **Finding 9 needs no new issue** — its behavior half is the existing open bug *"`value=`
   silently ignored when `signal=`/`variable=` also passed (all boolean widgets)"*
   (`CLAUDE.md:1537`). ⚠ **And nullable signals are the missing half of its fix**: honoring
   `value=` alone would give a checkbox that starts indeterminate while its signal says `False`.
6. **Commit approval**, then **round 2 by a FRESH session** — round 1's fixes touch `src/`, so
   gate 1 owes a round, and this session has now written code.

---

Branch `fix/signal-nullable-390` @ `6491fd3c`, reviewed against `main` @ `028b8392`.
Cap 3 (`PLAN.md`), spent 1. Gate 1: `git diff main...HEAD -- src/` is non-empty (2 files,
+79/-12), so a round is owed.

## What was measured, not read

Windows box, `py -3.12`, provenance printed on every arm
(`D:\Development\bootstack\src\bootstack`).

| | |
|---|---|
| suite | `py -3.12 tests/run_gui.py` — **1595 passed / 22 skipped, 33 legs, exit 0** as reviewed; **1598** after this round's fixes. `main` measured in the worktree the same way is **1579 / 22**, so the deltas are `+16` and `+19`, exactly what the one new test file collects. `git diff main...HEAD --stat -- tests/` returns that one file and nothing else, which is what bounds it. ⚠ **A first pass summed the legs by hand and got 1596** — one too many, self-consistent, and it would have read as an unexplained test. Sum with `awk`, not by eye |
| docs | `rm -rf docs/_build && sphinx-build -b html docs docs/_build/html -W --keep-going` — **exit 0**. (A `-n` build warns, all pre-existing; `grep -ci "signals.rst"` over that log returns **0**) |
| control | `git checkout main -- src/bootstack/widgets/_core/field_mixin.py`, then the new test file: **6 failed on the behavior** (8 after finding 3's fix) — `assert datetime.date(2024, 5, 5) is None`, `assert 5 is None`, `assert datetime.time(9, 30) is None`. Not one failed on `unexpected keyword argument 'nullable'`, which is the failure that would have proved nothing. ⚠ **Reverting only `field_mixin.py` is what makes this control worth running** — reverting all of `src/` would have failed every test at the constructor |
| baseline | `main` in a worktree, `PYTHONPATH=$W/src` **and** the worktree's absolute script path |
| probes | `development/probe_390_review_round1.py`, `_round1b.py`, `_round1c.py` |

**The fix does what it claims.** All five value-space widgets clear in both directions —
`NumberField`, `DateField`, `TimeField`, `Select`, `SelectButton`; field→signal and
signal→field; and none of the five realizes the signal (`realized=False` on all five), which
is the precondition the whole design rests on.

---

## 1. BLOCKING — `set(None)` on a `NoneType`-typed signal: a silent no-op became a `TypeError`

`src/bootstack/signals/signal.py:278`

The new branch raises whenever the signal is not nullable, without asking whether `None` is
already the signal's type. Before, `type(None) is self._type` matched at the old guard and the
call fell through to the equality no-op.

**Reachable with no nullable signal anywhere in the program** — measured on both arms:

```python
src = bs.Signal(0)
derived = src.map(lambda v: None)     # derived._type is NoneType
src.set(1)
```

```
main    src.set(1) -> OK, d2 = None
branch  src.set(1) RAISES TypeError: Expected NoneType, got NoneType. Pass nullable=True
        to Signal() if this value can be empty.
```

The raise comes out of the **source's** `set()`, through the subscriber fan-out — so when the
source is realized it detonates inside a Tk trace instead. The realistic shape is not
`lambda v: None`; it is `.map(lambda rec: rec.get("email"))` where the first record has no
email, which types the derived signal `NoneType` and then raises on every later record that
also has none.

Two smaller things fall out of the same line: the message reads **`Expected NoneType, got
NoneType`**, and `PLAN.md` §1's claim that `Signal(None)` without `nullable=True` is "left
exactly as it is" is false — `bs.Signal(None).set(None)` is a no-op on `main` and raises here.

**Minimal change** — raise only when `None` is not already the type:

```python
if value is None:
    if not self._nullable and self._type is not type(None):
        raise TypeError(...)
```

Falling through lands on the existing `self._last == value` early return, which is exactly the
baseline. `Signal(None).set(5)` still raises `Expected NoneType, got int`, unchanged.

## 2. SHOULD-FIX — the CHANGELOG contradicts itself inside one release section

`CHANGELOG.md:22` (#461) and `CHANGELOG.md:30` (#458)

Both bullets still say **"A `Signal` cannot hold an absent value yet, which is being decided in
[#390]"**, three and eleven bullets below the new entry announcing that it can. Unqualified,
they are wrong for exactly the case a reader would care about. `PLAN.md` §4 and `CLAUDE.md`
both flag this as a promotion-time trap; deferring it to promotion time is how the trap fires,
and the branch that makes the sentences wrong is the one that should reword them.

**Minimal change:** qualify both with `nullable=True` and drop the "being decided" clause. The
skip is still the default (decision 3), so neither bullet is deleted.

## 3. SHOULD-FIX — the parametrized field test covers three of the five it claims

`tests/widgets/public/test_signal_nullable.py:130`

Its docstring says *"Every field that binds a typed value, not display text"* and the
parameters are `NumberField`, `DateField`, `TimeField`. `Select` and `SelectButton` are
missing — the two widgets #390 was moved onto `0.4.0` **for**, since #458 and #461 are what
turned staleness into a regression there, and the two named in the new error message, the
docs note and the CHANGELOG bullet.

Both work (probe arm A: `widget=None signal=None subscriber_saw=[None]`, and
`signal.set(None) -> widget=None`), so this is a coverage hole rather than a defect — but it is
the hole most likely to matter, and it costs two lines.

## 4. NIT — the message names a remedy a derived signal cannot use

`src/bootstack/signals/signal.py:280`

`map()` gives no way to declare the derived signal nullable, and decision 4 rejected propagating
`None` into it on purpose (a derived signal is usually bound straight to
`bs.Label(textsignal=…)`, the `StringVar` corruption path). So a transform returning `None`
produces `… Pass nullable=True to Signal() if this value can be empty` naming a fix the caller
cannot apply. **No change proposed** — decision 4 settles the behavior and the new docs prose
teaches the guard. Recorded so it is not re-derived.

## 5. NIT — a property that raises a non-`AttributeError` breaks duck-typing

`src/bootstack/signals/signal.py:154`, consumed at `_core/capabilities/signals.py:36`

`is_signal()` is `hasattr(obj, 'var') and …`, and `hasattr` swallows only `AttributeError`, so
it now *raises* for a nullable signal instead of answering. Measured: `bs.Label(text=sig)` gives
the binding `BootstackError` rather than the crafted `TypeError: text= expects a string; pass a
Signal via textsignal=`. Self-correcting in practice — every mis-binding still lands on a
message that says `drop nullable=True` — and the alternative (making `is_signal` robust) has
blast radius well outside this branch.

## 6. NIT — bind-time seeding ignores nullability

`src/bootstack/widgets/_core/field_mixin.py:277`

`current = signal(); if current is not None: … else: self._push_to_signal(self.value)` reads
`None` as *unseeded*. With nullability, `None` is a value. Measured:

```
bs.DateField(value=date(2024, 5, 5), signal=bs.Signal(None, nullable=True))
  -> field=date(2024, 5, 5)  signal=date(2024, 5, 5)
```

The signal's `None` does not clear the field, while `_from_signal` does. Defensible — an
explicit `value=` is the more specific instruction — but asymmetric and undocumented.

## 7. NOTE, FILE IT — the deferred type locks on the first keystroke and the mismatch is swallowed

`src/bootstack/widgets/_core/field_mixin.py:352` (`except TypeError: pass`)

```
bs.NumberField(signal=bs.Signal(None, nullable=True))
  value = 5     -> signal_type=int  signal=5
  value = 5.5   -> signal_type=int  signal=5    field=5.5
```

Silently stale, which is the failure #390 exists to remove. **Pre-existing** — the control with
`bs.Signal(0)` is identical (signal stuck at `0` while the field shows `5.5`) — so it is out of
scope here. What the branch changes is reachability: with the deferred-type spelling the author
never chose `int`; the first value entered chose it.

## 8. NIT — docs

`docs/reference/signals.rst:207` — `shout = name.map(str.upper)` sits 98 lines below new prose
saying the empty-case guard is *"worth keeping even when the value cannot be empty today"*. Safe
as written (a non-nullable `str` source can never hand it `None`), so no change required.

---

## Not findings — checked and cleared

- **Every value-space binding stays unrealized**, so the `_realize()` refusal cannot fire on the
  five widgets nullability exists for. Measured on all five, not inferred.
- **`_push_to_signal` with a deferred type** — `target = getattr(signal, "_type", None)` is
  `None`, the reconciliation is skipped, and `set()` locks the type. Correct.
- **The async `<<Change>>` re-entry** — `_from_signal` sets `_value_syncing`, and the `when="tail"`
  `<<Change>>` that lands after it clears pushes a value the signal already holds, so `set()`'s
  equality check absorbs it.
- **`_signal_is_nullable()` defaults to `False`** for a signal-like object without the attribute
  (`Signal.from_variable`, a foreign duck), so the old behavior is what a non-`Signal` gets.
- **The em-dash in the new `BootstackError`** is house style — `data/base.py:521`,
  `memory_source.py:202` and a dozen others do the same.
- **`Signal.type` retyping to `Type[T] | None`** is a public retype, `0.5.0`'s rule — but it only
  widens, for a spelling that did not exist before, and `0.4.0` is a minor already. Same
  disposition the maintainer gave #460.

## 9. SHOULD-FIX — "a checkbox is already empty at `False`" is false for a tristate checkbox

`src/bootstack/signals/signal.py:160`, `docs/reference/signals.rst`, `CHANGELOG.md:15`

All three said a checkbox does not need nullability because its empty is `False`. A **tristate**
`Checkbox` reports indeterminate as `.value is None` (`boolean_controls.py:154`), so its empty is
`None`. Measured:

```
tristate Checkbox, signal=bs.Signal(False):
   value = True   -> widget=True   signal=True
   value = None   -> widget=None   signal=False    <- the two surfaces disagree
   subscriber saw: [True, False]
   sig.set(None)  -> TypeError: Expected bool, got NoneType. Pass nullable=True ...
   nullable=True at the binding -> BootstackError
```

Sharper than the `Select` case #390 was moved for: there the signal goes stale, here a subscriber
is affirmatively told `False` while the widget reads `None`. And the new hint chain leads to a
dead end — the `TypeError` points at `nullable=True`, which the binding then refuses.

**The design decision is not what is wrong.** Indeterminate is carried in the ttk `alternate`
state, not in the variable — `_apply_value` writes the *off* value and then flags the state
(`boolean_controls.py:129`) — and the variable is a `BooleanVar`, which raises on `set(None)`.
Realizing a nullable signal here could not carry the state either; it would raise at a different
moment. **Fixed the text only:** the false clause is gone from the error message, the docs note and
the CHANGELOG bullet. Per `feedback_docs_dont_document_around_defects`, no caveat was added in its
place.

**The underlying gap is pre-existing and wants an issue.** A tristate `Checkbox` bound to a
`Signal` cannot report indeterminate, because `signal=` on a boolean control **is** the widget's
variable. The only real fix is to bind it Python-side the way `ValueSignalMixin` does, which
changes what `signal=` means on boolean controls — well outside this branch. `Form` already treats
`None` as a real value here (`_impl/composites/form.py:766`), so `form.set({k: None})` on a
tristate editor with a signal reaches it too.

⚠ **This was found by the maintainer asking a question, not by the review.** The review repeated
the plan's "a checkbox's empty is `False`" three times without constructing one.

---

## Round 1 fixes — applied

| # | severity | disposition |
|---|---|---|
| 1 | blocking | **FIXED.** `signal.py:280` raises only when `self._type is not type(None)`. Pinned by `test_a_none_typed_signal_still_no_ops_on_none`, which **fails on the unfixed branch at `src.set(1)`** and **passes against `main`'s `signal.py`** — both arms run, so it pins the baseline rather than the fix. `probe_map2.py` now reads identically on the two arms |
| 2 | should-fix | **FIXED.** Both bullets now say *"Declare the signal `nullable=True` and the clear reaches it"* and point at the `Added` entry. Neither is deleted — the skip is still the default (decision 3) |
| 3 | should-fix | **FIXED.** `Select` and `SelectButton` added to the parametrize, which now carries an explicit `name` so a failure names the widget instead of `<lambda>-seed1`. The control fails 8 |
| 4, 5, 6, 8 | nit | **NO ACTION**, by the record above. 4 is settled by decision 4; 5 costs more than it saves; 6 is a design call the plan did not scope; 8 is safe as written |
| 7 | note | **FILE IT.** Pre-existing, widened in reach. Not fixed here |
| 9 | should-fix | **TEXT FIXED** in all three places. The behavior gap behind it is pre-existing — **FILE IT** |

**Suite after the fixes: 1598 passed / 22 skipped, 33 legs, exit 0.** `1579 + 19`, the file's
full collected count.

⚠ **One process trap paid for in this round:** `git checkout HEAD -- <path>` to undo a control
**silently discarded an uncommitted fix in the same file** — `HEAD` is the branch commit, not the
working tree. The suite still passed, because the fix's own test had not been re-run in the same
breath. **Stash or copy the file before a `git checkout` control, and re-run the pinning test
after restoring.**
