# #468 — type a `Select`'s custom value from its options

**Status:** plan for the maintainer. Written 2026-08-30 against `main` @ `60fc256e` (the `v0.4.1` tag). Every table below is measured, not reasoned.

## What is actually broken

One path. A custom value **typed by the user** stays a `str` when the option values carry a type. Everything else already types correctly:

| path | result |
|---|---|
| text names an option (`'Seven'` → `7`) | correct |
| plain options where value *is* the label | correct |
| off-list value set from code (`select.value = 42` → `42`) | correct |
| empty entry (`None`) | correct |
| **custom value typed by the user** | **`str`** |

**This is not a validation defect.** `select.value` is wrong too — `select.value == 6` is `False` for an app comparing against its own option value. Validation is one consumer that happens to expose it; `Form._coerce_value` patches the other (`form.get()` returns `6`), which is why the two disagree.

It violates the project's own value model: **`label` = caption, `text` = display, `value` = raw — never derive value from text.** The custom path returns the display text *as* the value.

## Why the type is knowable

`Select` declares `_VALIDATION_KIND = None` deliberately — its value kind belongs to its **options**, and `add_validation_rule`'s docstring says so publicly: *"its value kind is whatever its options carry"*. The widget already honors that on four of five paths. The off-list case is already solved **for values arriving from code**: `_register_retired_value` (`selectbox.py:405`) registers an off-list value under its own coerced text so the decode finds it again. Its docstring names the exact failure mode this issue reports.

The asymmetry is the whole bug: a programmatic write arrives already typed, so registration preserves it; a keystroke arrives as a string and nothing parses it.

## Scope — who this reaches

`SelectBox` has four consumers. Verified with `grep -rln "SelectBox" src/bootstack/ --include=*.py`:

| consumer | `allow_custom_values` | effect |
|---|---|---|
| `Select` (public) | caller's choice | **the target** |
| `TimeEntry(SelectBox)` → `TimeField` | `True`, **plus `value_format='shortTime'`** | **already correct — must not regress** |
| `TableView` search-mode picker | `False` | cannot reach the path |
| `dialogs/_impl/query.py` | `False` | cannot reach the path |

`dateentry.py` only mentions `SelectBox` in a comment; it does not use it.

⚠ **`TimeField` is a `SelectBox` subclass whose custom values ALREADY parse**, through its entry part's `value_format`. Measured: `'2:30 PM'` → `time(14, 30)`, `'banana'` → `None`. **The new coercion must not fire when the entry already carries a `_value_format`**, or it competes with a path that works.

## The rule

1. Infer the option type from the option values — a single type across all of them, or no answer.
2. `bool` is excluded — check it **before** `int`, since `bool` is an `int` subclass.
3. No answer (heterogeneous, empty, `str`, `bool`, or any non-primitive) → **no parse**, identity, exactly as today.
4. `int`/`float` → `IntlFormatter.parse(text, "decimal")`.
5. Parse raises → fall back to today's behavior (keep the text).

Every branch except 4 is today's behavior, so the change is strictly additive: the only thing that moves is the case that is currently wrong.

## Where the code goes

At `SelectBox`'s own decode seam — `_validation_value` (`selectbox.py:384`) and the commit path that sets `.value`, so **both** consumers are fixed at one point rather than validation alone.

⚠ **Do NOT route this through `value_format`.** It looks like the obvious lever — it is what makes `NumberField` parse — but it drives **display** as well as parse (`textentry_part.py:308-309` formats the value and writes it back to the entry). A `Select` shows the option's *label*, not a rendering of its value, so giving its entry a `value_format` would fight the label. Type and format are separate concerns here, and that separation is exactly what the unbuilt codec in `docs/_dev/field-value-dtype.md` proposes.

## Decisions, with the rejected alternatives

**Types: `str`, `int`, `float`. Not `bool`, not `date`/`time`.**

- **`bool` rejected.** A bool `Select` has exactly two options, so a *custom* bool is a contradiction — there is no third boolean to type. And the naive coercion inverts intent: `bool('False')` is `True`. That trap is already live at `form.py:972`.
- **`date`/`time` rejected for now, and this reverses an earlier "nearly free" reading.** The parser exists but is deliberately lenient — measured: `shortDate` turns `'abc123'` into `date(123, 8, 30)`, `'5'` into `date(2026, 5, 30)`, and `'yesterday'` into a real date. That leniency is a *feature* in a `DateField`, where the user is unambiguously entering a date; in a `Select` custom entry it silently invents values, which is worse than the bug being fixed. Including them needs a strict temporal parse that does not exist — a follow-up, not a smuggled extra.
- **Types stay unrestricted as OPTION values.** Measured: `enum`, `tuple`, `Decimal`, `date`, and even an unhashable `list` all round-trip correctly through a pick today. Narrowing that would break working code for no gain.

**Unparseable text keeps its `str`** (`'banana'` against `int` options). The alternative is `None`, which is type-honest and is what `TimeField` does. Rejected because it **removes** behavior an app may rely on today, where keeping the `str` changes nothing. Strict additivity is what makes this a patch. ⚠ `TimeField` and `Select` therefore differ here on purpose — do not "harmonize" them.

**Narrow `float` → `int` only when `float.is_integer()`.** `IntlFormatter.parse` returns `float`, so `int` options need narrowing; but options `[1, 7, 12]` with a typed `'6.5'` must not silently become `6`. Truncating user input is the same class of harm as the date parser inventing a year. A value whose type differs slightly from the options is honest; a truncated one is not.

## Tests

Pin each branch of the rule, so that no single wrong implementation passes:

- `int` options, typed `'6'` → `select.value == 6`, `type is int`, and the same value reaches a `range` rule (the reported defect).
- `float` options, typed `'2.5'` → `2.5`.
- `int` options, typed `'6.5'` → **not** `6` (guards the truncation decision).
- `int` options, typed `'banana'` → still `'banana'` (guards additivity).
- `str` options and bare options → unchanged (the 104-of-157 majority case).
- heterogeneous and empty option lists → unchanged.
- `bool` options → unchanged, and `bool` not treated as `int`.
- picked-from-list and `select.value = 42` → unchanged (must not reach the parse).
- **`TimeField` regression:** `'2:30 PM'` → `time(14, 30)` and `'banana'` → `None`, unchanged.

## Out of scope

- The `dtype`/codec initiative (`docs/_dev/field-value-dtype.md`, designed 2026-06-12, never started). It would prevent this **class** of bug, and its motivating example is this bug's twin in `NumberField` — but it is an architecture investment to decide on its own merits. ⚠ CLAUDE.md records that #355 "burned hours heading toward a `Select` value-model rewrite before the maintainer pointed at the ~15-line fix" — same widget, same pull. Name the boundary before starting.
- Strict temporal parsing (would unlock `date`/`time`).
- `Form._coerce_value`'s `bool(value)` trap and its non-parsing `date` arm.

## Round cap

2 (patch).

## Artifacts

- `development/demo_468_select_custom_value_validation.py` — runnable GUI demo: a `Select` and a `NumberField` carrying the identical `range` rule, so the control does the discriminating.
