# PLAN — #390 (Signals cannot represent an empty value)

Branch `fix/signal-nullable-390`, off `main` at `028b8392`. Milestone `0.4.0`.
**Round cap: 3.**

Cap 3 because this is a minor and it adds public surface (`nullable=`, `Signal.nullable`) on
the most-used type in the framework. Written before any code.

## What the four decisions settle

Answered by the maintainer 2026-08-26, recorded in a **comment** on #390 (its body still reads
as an open design question — read the comment, not the body).

1. **Do it at all?** YES.
2. **Declared, not automatic** — `Signal(v, nullable=True)` plus a public read-only
   `Signal.nullable`. Automatic-by-mode cannot cover `int`.
3. **A field bound to a NON-nullable signal is cleared: keep skipping, silently.** This is the
   status quo and needs no code — `_to_signal` already returns early on `None`
   (`field_mixin.py:297`), as does `_from_signal` (`:285`).
4. **`map()` is unchanged** — the transform is called with `None` and the author guards.
   Docs-only.

## Baseline — measured on this branch before any change

`development/probe_390_nullable_baseline.py`, Windows box, `py -3.12`:

```
Signal(date).set(None)         RAISES TypeError: Expected date, got NoneType
Signal(0).set(None)            RAISES TypeError: Expected int, got NoneType
Signal(None) constructs, type  <class 'NoneType'>          <- already spellable, already useless

realization, by binding
   NumberField(signal=)        realized=False  object_mode=False
   DateField(signal=)          realized=False  object_mode=True
   Checkbox(signal=)           realized=True   object_mode=False
   TextField(textsignal=)      realized=True   object_mode=False

the regression
   DateField cleared           field=None  signal=date(2024,5,5)  subscribers_saw=[]

map()
   guarded   .map(lambda d: … if d else "")   derived type str
   unguarded .map(lambda d: d.strftime(…))    RAISES AttributeError on a None source
```

⚠ **ONE RECORDED MEASUREMENT ON #390 IS WRONG AND THE CORRECTION WIDENS THE HAZARD.** The
issue body says `IntVar.set(None) -> TclError`. Measured in plain tkinter:

```
IntVar       set OK; raw tcl='None'; get -> TclError: expected floating-point number but got "None"
DoubleVar    set OK; raw tcl='None'; get -> TclError: expected floating-point number but got "None"
BooleanVar   set(None) RAISES TypeError
StringVar    set OK; raw tcl='None'; get -> 'None'
```

**Only `BooleanVar` fails at write.** `IntVar` and `DoubleVar` accept `None`, store the literal
`'None'` in Tcl, and detonate at an arbitrary later `.get()` — which may be in a different
widget, a different callback, or a repaint. **So the corruption path is three var types out of
four, and two of them are delayed-action.** This is the measurement that decides the design
below; it is why `None` must never reach a realized signal rather than merely being discouraged.

## The fifth question, which the four decisions do NOT cover

**What happens when a nullable signal is bound to a widget that takes the Tk variable?**

`ValueSignalMixin` syncs in pure Python and never touches `.var`, so `DateField(signal=)`,
`NumberField(signal=)`, `TimeField(signal=)`, `Select(signal=)` and `SelectButton(signal=)` —
every binding nullability exists to serve — stay **unrealized**. `Checkbox(signal=)` and
`TextField(textsignal=)` **are** the widget's variable, and there `None` takes the corruption
path above.

**Decision taken here: a nullable signal REFUSES TO REALIZE.** `_realize()` raises
`BootstackError` naming the problem and the fix. Rationale:

- It cannot break existing code — `nullable=True` does not exist today, so nothing can reach it.
- The alternative is writing a per-type empty into the var as a display shadow, and **per-type
  empties were already considered and rejected on #390** (`empty(int)=0` contradicts the shipped
  `NumberField.clear()` decision, `empty(bool)=False` collapses tristate). It also cannot work
  for `BooleanVar`, which raises at write.
- The failure is loud, immediate and at the binding site, instead of a `'None'` string surfacing
  later somewhere else.
- Text-space and boolean widgets do not need it: a text field's empty is `''` and a checkbox's
  is `False`, both representable already.

⚠ **This is a call made in this plan, not one handed down. It is flagged for the maintainer.**
If the answer is "allow it and shadow the var" instead, §2 and §4 change and the tests with them.

## The change

### 1. `src/bootstack/signals/signal.py`

- `__init__(self, value, name=None, master=None, *, nullable=False)`. Keyword-only, so no
  positional call site can be affected.
- **Type inference when seeded `None`.** `Signal(None, nullable=True)` has **no type yet** —
  `_type` stays `None` and is **locked on the first non-None `set()`**, along with
  `_object_mode`. `Signal.type` returns `None` while undetermined. This is what makes
  `bs.Signal(None, nullable=True)` — the spelling the #386 reporter's `clear_form` needs —
  work at all.
- `set()`: accept `None` when `self._nullable`; otherwise the existing guard is untouched.
  A `None` on a nullable signal stores `_last = None` and notifies subscribers directly.
- `_realize()`: raise `BootstackError` when `self._nullable`.
- `nullable` read-only property.

⚠ **`Signal(None)` WITHOUT `nullable=True` is left exactly as it is** — it constructs with
`_type = NoneType` and every `set()` raises. It is useless but it is **existing behavior**, and
making it raise is a strictness change, which is `0.5.0`'s rule, not this branch's. **File it,
do not fix it here.**

### 2. `src/bootstack/widgets/_core/field_mixin.py`

The two early returns are the whole regression. Both become conditional on the bound signal
declaring nullability:

- `_to_signal` (`:297`) — push `None` through when `self._value_signal.nullable`.
- `_from_signal` (`:285`) — accept `None` and clear the field when nullable.
- `_sync_value_set` — same rule, for the programmatic `field.value = None` path.

**A non-nullable signal keeps skipping, silently, exactly as on `0.3.2`** (decision 3).

### 3. Docs

- `docs/reference/signals.rst:109` — the unguarded `due.map(lambda d: d.strftime(…))` is the
  only shipped example that breaks on a `None` source. Guard it and state the rule beside it.
- A short nullability section: what `nullable=True` is for, that it serves value-space field
  signals, and that binding one to a text or boolean widget raises.

### 4. CHANGELOG

One bullet under `### Added` in `## [Unreleased]`.

⚠⚠ **AND THE PROMOTION TRAP, WHICH FIRES AT RELEASE TIME.** The `0.4.0` bullets for **#458 and
#461 currently document the empty-selection exception and link to #390.** That wording is
correct only while the limitation ships. **If this lands in `0.4.0`, both sentences must come
out before `## [Unreleased]` is promoted.**

## Tests — `tests/widgets/public/test_signal_nullable.py`

1. `test_a_nullable_signal_accepts_none` — `Signal(date(…), nullable=True).set(None)`; value is
   `None`, subscribers saw `None`.
2. `test_a_non_nullable_signal_still_raises` — the guard is untouched. The control for 1.
3. `test_nullable_seeded_none_locks_its_type_on_first_value` — `Signal(None, nullable=True)`
   has `type is None`, takes a `date`, then rejects an `int`. The monomorphic guarantee is
   deferred, not abandoned.
4. `test_clearing_a_bound_field_reaches_a_nullable_signal` — the reported bug, end to end on
   `DateField`. Fails on baseline with a stale date.
5. `test_clearing_a_bound_field_still_skips_a_non_nullable_signal` — decision 3, pinned so a
   later "harmonization" cannot quietly widen it.
6. `test_binding_a_nullable_signal_to_a_text_field_raises` — the fifth question's answer,
   pinned with its message.
7. `test_form_clear_reaches_nullable_signals` — the reporter's actual shape
   (`form.set({k: None})`).

**Control, before committing:** revert `src/`, confirm 1, 3, 4, 6, 7 fail, and confirm each
fails on the **behavior** — a stale value or a missing `None` — not on `TypeError: unexpected
keyword argument 'nullable'`, which only proves the parameter does not exist yet.

## Boundary of the completeness claim

`grep -rn "nullable" src/bootstack` returns nothing today, so the name is free.
`grep -rn "_object_mode\|_realize()" src/bootstack` bounds who is affected by the deferred
type. The value-space bindings are enumerated by `grep -rn "_bind_value_signal" src/bootstack`.
Each of these is run and recorded in the review, not asserted from here.

## Out of scope

- `Signal(None)` without `nullable=True` — see §1. **File it.**
- #389 (`Form.reset()` / `Form.clear()`). This unblocks it; it does not implement it.
- Widening `map()` in any way (decision 4).
