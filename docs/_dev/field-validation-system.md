# Field Validation System — Redesign Brief

Status: **proposed** (design approved; implementation not started)
Branch: `feat/field-validation-system`
Surfaced by: the TextField widget review (audit → the validation path is broken
for typed fields).

---

## 1. The problem

Field validation does not work as expected for typed (numeric / date / time)
fields, and the engine is a hand-rolled imperative version of mechanisms the
framework already provides natively (signals, streams, events).

Two concrete defects, both proven empirically during the TextField review:

1. **Validation runs against the wrong thing, inconsistently.** The seven field
   wrappers split on what they hand the rule engine:

   | Field | passes to `validate()` | result |
   |-------|------------------------|--------|
   | DateField, TimeField | `entry.get()` — display **text** | string rules run on `"Jan 2, 2024"` |
   | TextField | `entry.value()` — committed value | stale; not the live input |
   | NumberField, SpinnerField, PathField, PasswordField | `entry.value()` — raw datum | **`TypeError`** on a `float`/`date` |

   A `stringLength`/`pattern`/`custom` rule on a NumberField raises
   `TypeError: object of type 'float' has no len()` /
   `expected string or bytes-like object, got 'float'`. So a NumberField with
   *any* string rule attached crashes on `validate()`.

2. **No type-aware behavior and no rule for what typed fields need.** The rule
   catalog is string-only (`required`, `email`, `stringLength`, `pattern`,
   `compare`, `custom`). There is no `range`/bounds **validation** rule — numeric
   and date bounds are enforced only by silent `min_value`/`max_value` clamping,
   which is a different UX from validating with a message ("must be ≥ 18").

Supporting evidence that the *intended* model is value-based and type-aware:

- The `required` rule body is already written to accept any type
  (`# Everything else is valid (non-empty string, number, date, etc.)`).
- `Form.validate()` already validates `widget.value` (the raw typed value,
  `form.py:289`) — so the form aggregator assumes value-based validation and
  hits the same crash.

## 2. What exists today (and is *not* the coupling we feared)

The rule engine is **already event-driven** — it does **not** use Tkinter's
built-in input validation (`validatecommand`/`-validate`). Those options appear
only as unused passthrough annotations on the primitive `Entry`
(`entry.py:26-27,58-59`) and can be dropped.

The current engine (`widgets/_impl/mixins/validation_mixin.py`):

- Hand-binds `<KeyRelease>` and `<FocusOut>`, debounces with `after()`
  (`_setup_validation_binds`, `_debounced`).
- Resolves the value to validate via `_get_validation_value()` → prefers
  `get()` (text) with a `value()` fallback.
- Runs `ValidationRule.validate(value)` per rule, honoring each rule's trigger
  policy.
- Emits `<<Valid>>` / `<<Invalid>>` / `<<Validate>>` with a `ValidationEvent`
  payload (`value`, `is_valid`, `message`).

Error display is **imperative**: `Field._dispatch_invalid` pokes
`_message_lbl['text']` and sets accent `danger`; `_dispatch_valid` resets it.

So there is nothing to *un*-bind from Tk. The work is to re-ground the engine on
the reactive layer and make it type-aware.

## 3. Goals / non-goals

**Goals**
- Validate the field's **typed value**, with **type-appropriate** rule logic.
- Re-ground the engine on **signals + streams + events** — the trigger policy is
  expressed as streams, validity is reactive state, no hand-rolled `after()`
  debounce or raw `<KeyRelease>` binding in the rules layer.
- Validity is **reactive state** a UI binds to (`field.valid`, `field.error`);
  the existing `on_valid`/`on_invalid`/`on_validate` events become a thin derived
  layer.
- Add the missing **`range`** rule (numeric / date / time bounds → message).
- A rule that cannot apply to a field's dtype is **rejected at attach time** with
  a clear error — not silently coerced.
- One consistent path: a field's own `validate()`, the auto blur/key path, and
  `Form.validate()` all agree.

**Non-goals**
- Reworking `min_value`/`max_value` **clamping** (that stays; `range` is the
  *validation message* counterpart, opt-in).
- A general constraint solver / cross-field rule DSL beyond the existing
  `compare`.
- Async / IO-backed validation (future; the stream shape leaves room).

## 4. Design

### 4.1 Validate the typed value

The value handed to rules is the field's parsed, typed value — `str` for
TextField/PasswordField/PathField, `int`/`float` for Number/Spinner, `date`/
`time` for Date/Time. The single lever is the live parse the entry already owns
(`TextEntryPart._parse_or_none(get())` and subclass parses); the resolver returns
the parsed live value, not the display text or the stale committed value.

### 4.2 Reactive engine (signals / streams / events)

A `FieldValidator` owns a field's rule list and its validity state. It depends
only on the reactive layer — it is handed value updates; it never touches
`get()` / `state()` / `after()` / `<KeyRelease>`.

- **Trigger policy is streams**, replacing `_setup_validation_binds` +
  `_debounced`:
  - key-trigger rules → the field's input stream
    (`on_input().map(parse).debounce(ms)`)
  - blur-trigger rules → the commit stream (`on_change()`)
  - manual → `field.validate()`
- **Validity is state** → two reactive signals, kept consistent from one result:
  - `valid: Signal[bool]`
  - `error: Signal[str]` (empty string when valid)
- **Events are derived** — `<<Valid>>`/`<<Invalid>>`/`<<Validate>>` fire off the
  signal transition, preserving the `on_valid`/`on_invalid`/`on_validate` API and
  the `ValidationEvent` payload. Good for "the moment it became invalid" cases.
- **Error display becomes declarative** — the field's message label binds the
  `error` signal (text) and a danger accent; the imperative `_dispatch_invalid`/
  `_dispatch_valid` poking goes away.

### 4.3 Rule taxonomy (type-aware)

Two honest families. A rule declares which it is; the field knows its dtype and
rejects an inapplicable rule when it is attached.

- **value-rules** (any typed value): `required`, `compare`, `custom`, **`range`**
  — operate on the parsed value. `custom`'s `func` now receives the **typed**
  value (`lambda v: v >= 18` on a NumberField — clean, no string parsing).
- **text-rules** (string fields only): `stringLength`, `pattern`, `email` — and
  `add_validation_rule("stringLength", …)` on a non-text field raises a clear
  `BootstackError`/`ValueError` ("`stringLength` applies to text fields").

New **`range`** rule: comparable bounds (`min=`, `max=`) over `int`/`float`/
`date`/`time` — one rule covers all three since they are orderable. Produces a
message ("must be between …"); distinct from silent clamping.

### 4.4 Forms integration

`Form.valid` becomes a computed signal AND-ing the fields' `valid` signals;
`Form.error`(s) surface from the field `error` signals. `Form.validate()` (manual,
run-all) stays, but routes through the same typed-value engine, so it stops
double-implementing rule iteration and stops crashing on typed fields.

## 5. Public API surface (proposed)

- `field.valid` → `Signal[bool]` (read; reactive).
- `field.error` → `Signal[str]` (read; reactive; `""` when valid).
- `field.validate()` → `bool` (manual, runs all rules against the typed value).
- `field.add_validation_rule(rule_type: str, **kwargs)` — unchanged signature;
  now (a) guards non-string `rule_type` with a clear `TypeError` (no more silent
  double-wrap of a `ValidationRule` object), and (b) rejects a text-rule on a
  non-text field at attach time.
- `on_valid` / `on_invalid` / `on_validate` — retained, derived from `valid`.
- New `RuleType` member: `"range"`.
- `Form.valid` / `Form.error` reactive aggregates.

`add_validation_rule` stays **string-only** (decided during the review): a
`ValidationRule` object carries no information the string form lacks, so there is
no second object-taking door.

## 6. Blast radius

- `validation/validation_rules.py` — type-aware rule application; `range` rule;
  value-rule vs text-rule classification.
- `widgets/_impl/mixins/validation_mixin.py` — replace imperative bind/debounce
  with the stream-driven `FieldValidator`; expose `valid`/`error` signals; emit
  events as derived.
- `widgets/_impl/_parts/textentry_part.py` (+ `numberentry_part.py`,
  spinner/date/time parse paths) — the typed live-value resolver.
- `widgets/_impl/composites/field.py` — bind the message label to `error`; drop
  imperative dispatch.
- `widgets/_impl/composites/form.py` — route through the engine; reactive
  aggregates.
- `widgets/_core/field_mixin.py` — `add_validation_rule` guards; expose
  `valid`/`error`.
- The 7 public field wrappers — drop the divergent `validate()` bodies; inherit
  one correct path.
- Tests + docs (TextField/NumberField/DateField validation sections; the
  `/reference/validation` topic guide).

## 7. Staging

1. **Engine + typed value** — typed live-value resolver; unify all wrappers and
   the auto path on it; make string rules type-safe enough not to crash. Fixes
   the crash and the value/text inconsistency. *(Smallest correct slice.)*
2. **Rule taxonomy** — value-rule vs text-rule split; `range` rule; attach-time
   dtype rejection.
3. **Reactive surface** — `valid`/`error` signals; declarative message label;
   `Form` aggregates; events become derived.
4. **Docs + tests** — per-widget validation sections; validation topic-guide
   rewrite; headless rule tests + GUI delivery tests (one App per process, #150).

## 8. Decisions locked

- Validate the **typed value**, not display text or committed value.
- **Signals primary** for validity state; events derived.
- **Split** value-rules / text-rules; add **`range`**; **reject** inapplicable
  rules at attach time (no silent coercion).
- `add_validation_rule` stays **string-only**, with a guard.
- Drop the unused Tk `validatecommand`/`invalidcommand` passthrough on `Entry`.

## 9. Open questions

- `valid`/`error` as two signals vs one `Signal[ValidationResult]` exposing
  `.valid`/`.message` — leaning two for binding ergonomics.
- Whether `range` on a string field is an error or maps to `stringLength`
  (leaning: error — keep the families clean).
- Debounce default for key-trigger streams (current code uses 50 ms).
