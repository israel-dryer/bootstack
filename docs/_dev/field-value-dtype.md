# Field value model — a `dtype`/codec on the base field (follow-up initiative)

**Status:** designed 2026-06-12, NOT started. Grew out of the image-icon branch
(`feat/image-icon-api`) while wiring `NumberField(signal=...)`.

## Motivation

Two value-plumbing bugs surfaced in `NumberField` in one session, both fixed
surgically:

1. **`.value` returned a string** after a programmatic set (the internal stored
   the value as text when no `value_format` was set). Fixed by coercing in the
   public getter (`numberfield.py` `_as_number`).
2. **Stepping accumulated float error** (`0.05 + 0.05 + … → 0.15000000000000002`).
   Fixed by quantizing to the increment's decimal precision in
   `numberentry_part.py` `step()` / `_increment_decimals()`.

Both are the same root problem: **no single owner of "this field holds a `float`
with step `0.05`."** Set / get / parse / format / step each independently
re-derive the type and precision, and drift apart — so bugs leak out one
operation at a time and get patched one at a time. The same fragility lives in
`DateField`/`TimeField` (date/time parse+format) and any future typed field.

## Proposal

Give the base field a small **codec** keyed off a `dtype`:

```
dtype = {
    type:    the Python type of .value (int|float|date|time|str|...)
    parse:   text  -> value      (raises on invalid)
    format:  value -> text       (display)
    quantum: optional step/precision for numeric snapping
}
```

The base `Field` owns value↔text using the codec, so:

- `.value` returns the correct type **by construction** (retire `_as_number`).
- stepping quantizes via `quantum` (retire the ad-hoc `_increment_decimals`).
- the bound `signal` is typed off the dtype.
- a new typed field = "declare a dtype," not "re-implement value handling."

Typed subclasses become thin configs: `NumberField` → numeric codec
(int/float + step), `DateField` → date codec (+ format), `TimeField` → time
codec, `TextField` → identity (str). `Select` already carries its own value
map — fold it in or leave it.

## Already shipped on `feat/image-icon-api` (the near-term half)

- **`ValueSignalMixin`** (`widgets/_core/field_mixin.py`): generic, type-agnostic
  two-way `value ↔ signal` binding (seed, signal→field, field→signal on
  `on_change`, loop guard) + a `signal` property returning the value signal.
- **`signal=`** added to `NumberField`, `DateField`, `TimeField` (binding the
  TYPED value — number/date/time, not text). `Select` already had `signal=`.
- The two surgical bug fixes above, with regression tests in
  `tests/widgets/public/test_field_text_value.py`.

So value↔signal **consistency** is done; the codec is the remaining
**architecture** investment (prevents future drift; retires the two patches).

## Scope / files (when built)

- `widgets/_impl/composites/field.py` (base `Field`) + `_parts/*entry_part.py`
  (numeric/date/time/text parts) — relocate parse/format/quantize onto the codec.
- `widgets/numberfield.py`, `datefield.py`, `timefield.py`, `textfield.py` —
  declare their dtype; drop per-field value coercion.
- Public contract unchanged (`.value` returns the same types) → can migrate one
  field at a time behind tests, no big-bang break.

## Open questions

- Is `dtype` a **public** knob (a generic `Field(dtype=...)`) or purely an
  internal base mechanism the typed subclasses configure? (Lean internal-first.)
- Naming: `dtype` vs `value_type` vs a `Codec`/`Converter` object.
- How `value_format` (display format string) relates to the codec's `format`
  (the codec should own it; `value_format` becomes a codec parameter).
- Range-mode `DateField` (`value` is a `tuple[date, date]`) — the codec/signal
  binding currently assumes scalar; decide tuple handling.
