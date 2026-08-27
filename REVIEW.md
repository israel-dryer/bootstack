# REVIEW — #390 round 3

**Reviewed:** `git diff 4adf868d..HEAD -- src/` — the range round 2's record named as the honest
one, and it is. No design is being replaced mid-branch this time, so everything before `4adf868d`
is covered by the round 2 record at **`7a76e115`** (its first form is at `b2ed348d`). The diff is
one file, `signals/signal.py`, 91 insertions: `dtype=`, `_reconcile()`, `_is_tk_native_type()`,
`_create_variable`'s new dispatch, `clear()` and `_empty_value()`.

**Cap 3 (`PLAN.md`), spent 3 — this was the last one.** Three findings, all three reproduced by
construction before any was acted on. Two were fixed in `src/`, one in the docs. One survivor is
filed rather than carried.

⚠ **The instrument is `development/probe_390_review_round3.py`** (seven arms, HOLDS/REFUTED) plus
`development/probe_390_round3_numberfield.py` for F1 and `development/probe_390_round3_docs.py`,
which runs every factual claim in the new prose instead of reading it. **Re-run them rather than
re-deriving any of this.**

⚠ **This round was handed `PLAN.md` as well as `REVIEW.md`**, which round 2's Process section asked
for. It cost nothing and no dispositioned item was re-derived — F7, which round 2 spent a finding
on, was recognized as settled from the plan's out-of-scope section and never opened.

---

## Findings and dispositions

| # | what | verdict |
|---|---|---|
| **F1** | **A field bound to a signal that STARTS empty loses the declared empty at construction.** `NumberField` starts at `0` and the signal is silently moved off `None` | **HIGH, FIXED** |
| **F2** | **A `set`-typed signal that STARTS empty reads `None`**, where the same signal emptied by `clear()` reads `set()` | **MEDIUM, FIXED** |
| **F3** | **`signals.rst` states the empty rule as a two-way choice**, so it predicts the empty string for a multi-select's `set` signal, which empties to `set()` | **LOW, DOCS FIXED** |

### F1 — the headline case, broken by the door the tests do not have

`bs.Signal(None, allow_empty=True, dtype=int)` bound to a `bs.NumberField` **starts at `0`, and
the signal reads `0` too** — the declared empty is destroyed before the app ever runs, with no
error anywhere. That is the spelling the class docstring, the CHANGELOG and `signals.rst` all
advertise, on the widget family #390 was moved onto `0.4.0` for.

`_bind_value_signal` (`field_mixin.py:275`):

```python
current = signal()
if current is not None:
    self.value = current
else:
    self._push_to_signal(self.value)      # <- seeds the SIGNAL from the WIDGET
```

The `else` reads a `None` from the signal as *"this signal has nothing to give"* and seeds it from
the widget instead. **That was correct for the whole life of the branch's baseline** — an empty
could not be declared, so a `None` really did mean "nothing yet". The moment `allow_empty=True`
made an empty a value the author asked for, the same line started overwriting it.

⚠ **It is invisible on four of the five value-space fields, and that is why it survived.**
`DateField`, `TimeField`, `Select` and `SelectButton` all default to `None` themselves, so the
write happens and changes nothing observable. `NumberField` defaults to `0`. Measured, pre-fix:

```
NumberField   widget.value=0        signal=0         SIGNAL CLOBBERED
DateField     widget.value=None     signal=None      OK
TimeField     widget.value=None     signal=None      OK
Select        widget.value=None     signal=None      OK
SelectButton  widget.value=None     signal=None      OK
```

⚠⚠ **THE TEST SHAPE IS ROUND 2'S F1 AGAIN, ONE TURN OUT, AND IT IS THE DURABLE FINDING HERE.**
`test_the_value_space_fields_all_report_a_clear` parametrizes all five widgets — and **seeds every
one of them with a value**, then clears. Round 2 hit exactly this with the refusal tests and fixed
it *there* by parametrizing over `value-seeded` and `starts-empty`; **the same treatment was not
carried to the value-space test, and the defect is in precisely the arm it does not have.** A
parametrize over widgets looks like breadth and is breadth along one axis only. **When a feature
has two doors into the same code — a seed and a later write — a test that only ever uses one of
them is half a test, whatever its parametrize covers.**

**Fixed** by making a declared empty win over the widget's default the way a real value does:

```python
if current is not None or self._signal_allows_empty():
    self.value = current
else:
    self._push_to_signal(self.value)
```

⚠ **The `current is not None` arm is byte-for-byte unchanged, deliberately.** Guarding it with
`_value_syncing` to suppress the push-back was considered and **not** done: that push runs
`_push_to_signal`'s numeric reconciliation, this file's own rule is to find what is leaning on a
no-op before removing it, and the fix does not need it. **Control: `NumberField(signal=Signal(0))`
reads `0` and `Signal(7)` reads `7`, unchanged either side of the fix.**

### F2 — `clear()` was normalized and the constructor was not

Round 2's F4 decided a `set`-typed signal's empty is `set()` **"realized or not — a deliberate
departure from the binding-decides rule"**, and pinned it on both arms. Both arms go through
`clear()`. **The constructor stores the raw seed**, so:

```
starts-empty  sig() = None    type = set
cleared       sig() = set()
```

Same signal type, same declared empty, two different answers depending on which door it came
through — and the seed door is the one that returns something that is not an instance of the type
`sig.type` reports. **That is round 2's F2 shape re-entered through the constructor**, at a much
lower cost: a subscriber doing `for x in sig()` gets a `TypeError` instead of an empty loop.

**Fixed** by routing the empty seed through the same `_empty_value()` that `set(None)` uses, which
required moving the `_var`/`_trace` initialization above `_last` so the helper has what it reads.
⚠ **Scoped by measurement, not by argument:** `str` and `int` seeds still read `None`, because
`_empty_value()` answers `None` for an unrealized signal of either — so **F5's binding-decides
rule for `str` is untouched**, and only `set` moves. Pinned on both types in the new test.

### F3 — the prose states a rule the framework does not follow

*"Empty is `None` — except where the signal is the widget's own variable ... so there empty is the
empty string."* A multi-select `bs.ToggleGroup`'s signal **is** the widget's variable, and it
empties to `set()`. The section is titled *What "empty" means* and reads as the complete rule, so a
reader hits the one case it does not cover with the wrong expectation. **One sentence added**,
naming the `set` case and noting the falsiness check the passage already recommends covers it too.

⚠ **Every other factual claim in the new prose was RUN, not read** —
`development/probe_390_round3_docs.py`, fourteen claims across `signals.rst` and `checkbox.rst`
including the `map()` guidance, the `dtype` contradiction raising at construction, both halves of
the `str`-empties-two-ways example, and *"a signal bound to an indeterminate checkbox reads
`False`"*. **All fourteen hold.**

---

## The unswept ground round 2 listed — all four dispositioned, none actionable

**Doubt 3 — `set(None)` normalizes silently rather than raising.** Working as designed and the
design is load-bearing: `clear()` routes through `set(None)` precisely so one declaration check
covers both verbs (round 2's F3). Raising would put the check back in two places. **No action.**

**Doubt 5 — `SpinnerField(textsignal=Signal(1.0, allow_empty=True))` refuses while a `str` seed
accepts.** Reproduced. **Correct, and the message is actionable**: a `float` seed realizes a
`DoubleVar`, which is the floor, and the refusal text names `NumberField` as the way out. The
asymmetry is the binding being honest about what the variable can hold. **No action.**

**Item 2 — `from_variable`'s `py_type` identity chain (`signal.py:325-331`).** Priced: it is
reached only when `tk_var.get()` **raises**, and only a `coerce=` subclass falls through to the
empty string. No caller in `src/` passes `coerce`. **Error-recovery path, unreachable in practice,
left as round 2 left it.**

**Item 3 — have `_reconcile()`'s two callers drifted in what they ACCEPT?** They cannot: it is one
function and the constructor's only extra step is skipping it when `dtype` is absent, where the
type came from the seed and the test is trivially satisfied. **Measured across four cases anyway**
(`int` into `float`, `bool` into `int`, `str` into `str`, `float` into `int`): constructor and
`set()` agree on all four, accept and raise alike. **No drift.**

**Item 4 — `dtype` against `Form`'s `FieldItem.dtype`.** Reviewed by someone who did not make the
call. **It holds.** `FieldItem.dtype` accepts `'date'` because a `Form` is built from data that
often arrives as JSON; a `Signal`'s is written in Python beside the type it names. Accepting the
string here would mean a second parser and a second failure mode on a class that has neither.
**No action, and the divergence is now reviewed rather than merely decided.**

---

## Survivor — FILED AS #484, not carried

**A signal the framework created for you can never be cleared, and the error names a constructor
you did not call.** Every framework-created signal is `allow_empty=False` permanently — two
creation paths in `_core/capabilities/signals.py`, reached lazily from `signal_mixin.py:211` — so
`clear()` on one raises *"Pass `allow_empty=True` to `Signal()`"* pointing at a call that is not in
the caller's code. ⚠ **NOT pre-existing: `clear()` is new in this branch**, so the combination could
not be reached before.

⚠⚠ **THE FIRST FILING WAS TOO NARROW AND NAMED A ROUTE THAT IS NOT PUBLICLY REACHABLE.** It framed
this as a `Signal.from_variable()` defect. **`RadioGroup`, `ToggleGroup` and `Tabs` do build their
signals that way and NONE of the three exposes a public `.signal`** — confirmed by `AttributeError`,
and `from_variable` is excluded from the generated docs beside `tk` and `var`. **The reachable
population is six widgets** whose `.signal` the caller never constructed: `TextField`,
`PasswordField`, `PathField`, `SpinnerField`, `Slider`, `Checkbox`. `TextArea`, `NumberField` and
`Select` answer `None` while unbound and never reach it. **The issue is retitled and the measurement
is a comment on it; do not re-derive either.**

**It splits, and only one half is an artifact.** For the four text fields `''` is a legal empty —
the same signal supplied as `bs.Signal("x", allow_empty=True)` clears to `''` and blanks the entry,
so nothing about the binding forbids it. For `Slider` and `Checkbox` the refusal is **correct on the
merits** (the floor), and only the message is wrong: it advises declaring something the binding
would refuse anyway.

**Moderate, not high** — `field.clear()` is the documented verb and works, and `signal.set("")`
works. **Filed as #484, unmilestoned — it gates nothing, and this file's rule is not to make a
scope call for the maintainer.**

---

## Notes — gate 2, not fixes

- **`_reconcile`'s widening test is `self._type is float`, an identity survivor** in a file that
  otherwise asks `issubclass` after `baacc48f`/`1040a62d`. Consequence is narrow and
  one-directional: a `float` **subclass** declared as `dtype=` does not widen an `int`, it raises.
  No caller, no known use, and widening it would need a rule for what the widened value's type
  should be. **Recorded so the next `issubclass` sweep does not read the file as uniform.**
- **`test_signal_empty.py:189` uses the word `nullable` in prose** describing the superseded
  concept. The plan's `grep -rn "nullable" src/bootstack tests/ docs/` boundary check is otherwise
  **clean** — the only other hits are `docs/_dev/handoff-archive.md`, which is shipped history and
  must not be swept. **Wording, not behavior.**
- The refusal message lists the five typed-value fields as the way out and **`SpinnerField` is not
  among them**, correctly — but a reader who reached it *from* a `SpinnerField` has to work out
  that `NumberField` is the substitute. **Note only; the message is not wrong.**

## Boundary of the completeness claims — the commands, not the conclusions

```
grep -rn "nullable" src/bootstack tests/ docs/        -> 1 prose hit (note above) + handoff-archive
grep -rn "allow_empty\|allows_empty" src/bootstack    -> signal.py + field_mixin.py:287,299,327,335
grep -n  "_type is \|_type in (" signal.py            -> 3 sites, all priced above
git diff main...HEAD --stat -- tests/                 -> test_signal_empty.py, and nothing else
```

**Census re-run at the shipped commit** (`development/probe_390_signal_census.py`) — the plan's
three-way table is a measurement here, not a plan-time estimate: 24 widgets take a signal, 16
realize, 8 stay pure Python, and the 11 `StringVar` rows are the ones the widening reaches.

**Round 2's probe re-run after these fixes: F1 through F4 still REFUTED**, F5/F6/F7 still HOLD by
disposition. **Neither fix regressed round 2's.**

## Suite

**1628 passed / 22 skipped, 33 legs, exit 0** — Windows box, `py -3.12 tests/run_gui.py`,
`matplotlib` and `pandas` both present. Docs clean-build warning-free under `-W`.

⚠ **Reconciled by BOUNDING THE MOVEMENT.** `git diff main...HEAD --stat -- tests/` returns
`test_signal_empty.py` and nothing else, that file collects **49**, and `main` is **1579**:
`1579 + 49 = 1628`. The intermediate steps agree independently — the file collected **40** at round
2's record (`b2ed348d`, suite 1619), **43** after the two subclass fixes, and **49** now.

**Control for the fixes, at the shipped commit:** reverting `signal.py` and `field_mixin.py`
**only**, with the new tests in place, turns exactly two arms red — `AssertionError: NumberField:
the binding overwrote the declared empty / assert 0 is None`, and `assert None == set()`. **Both
behavioral, neither an `AttributeError` nor an unexpected-keyword error**, and the other four
parametrize arms stay green on both builds, which is the asymmetry that makes the parametrize mean
something. ⚠ **Both source files were copied out before the `git checkout`** — round 1 lost an
uncommitted fix that way.

## The branch is done

**Cap 3, spent 3, and the round earned its place**: F1 is a HIGH in the feature's headline path,
reached by the documented spelling, and nothing in two prior rounds or a 1622-test green suite was
positioned to see it. But the shape of the round says stop — **the two src findings are both the
same defect class as round 2's**, one door out (a seed instead of a write) rather than new ground,
and the four items round 2 flagged as unswept all came back clean or unreachable. **That is the
signature of a branch that is finished, not of one with more in it.**

⚠ **The promotion trap from `PLAN.md` is DISCHARGED:** `grep -n nullable CHANGELOG.md` is empty,
and the #458 and #461 bullets now say *"declare it `allow_empty=True` and the clear reaches it"*.

⚠⚠ **AN EARLIER VERSION OF THIS LINE SAID BOTH BULLETS "MUST COME OUT ENTIRELY" AT PROMOTION.
THAT WAS WRONG AND ACTING ON IT WOULD DELETE ACCURATE SENTENCES.** `allow_empty=True` ships in the
SAME release, so those tails document the opt-in rather than a removed limitation, and #461's even
points the reader at the `Signal` entry under `Added`. **The real trap was the earlier `nullable=`
wording, and it is already swept. Leave both bullets alone.**

⚠ **A SECOND COPY OF F3 WAS MISSED BY THIS ROUND AND FOUND AFTER THE MERGE.** The CHANGELOG's own
#390 bullet stated the same two-way empty rule the docs did — *"`None` … except … `''`; a falsiness
check covers both"* — which is wrong for a multi-select's `set` signal. **F3's completeness claim
was scoped to `signals.rst` and that boundary was never written down**, which is exactly the failure
this project's own rule names: a completeness claim whose scope is unstated reads as global and gets
checked as local. Fixed on `main` in `a13b64f3`. **Write the command, not the conclusion.**
