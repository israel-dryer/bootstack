# PLAN — `Select` lost `FieldAddonMixin` (#465)

**Issue:** [#465](https://github.com/israel-dryer/bootstack/issues/465) · **Milestone:** `0.4.0 — Signal binding on fields`
**Branch:** `fix/select-validation-surface-465`
**Base:** `main` @ `cfae3713`
**Round cap: 2**
**Status:** ⏭ NOT STARTED. Written before code, per `REVIEW-PROTOCOL.md`.

⚠ **External bug report** — filed 2026-08-20 by `bLynnb2762` against `0.3.2`. A real user is waiting, so the CHANGELOG entry matters more than usual.

---

## The finding

The issue reports a missing `.error`. The cause is larger and simpler: **`Select` does not inherit `FieldAddonMixin`, and nothing records a decision to exclude it.**

That one omission accounts for six public members plus the validation gate:

```
valid  error  insert_addon  update_addon  remove_addon  addons  _VALIDATION_KIND
```

**The family is uniform 7/7 without it** — `TextField`, `PasswordField`, `PathField`, `SpinnerField`, `NumberField`, `DateField`, `TimeField` all expose every one. `Select` is the sole outlier.

⚠ **"`Select` opts out deliberately" is NOT SUPPORTED, and this plan supersedes it.** `CLAUDE.md` says so and this file said so twice, but the comment at `select.py:88` explains `_flex_vertical_default` and merely *states* the non-inheritance; no reason is recorded anywhere. The class declaration traces to `a41b539e`, the flat-surface migration — a refactor, not a decision. #357 then hand-restored `add_validation_rule` alone (`884b8027`, 2026-07-20), a month after the mixin already had `valid`/`error` and the kind gate. **It was incomplete at birth, not drifted.**

⚠ **The addon opt-out theory is DISPROVED BY CONSTRUCTION, not argued away.** `Select` already uses addons — its internal reports `addons=['dropdown', 'probe']` after a test insert, so **the dropdown arrow IS an addon**. The machinery is load-bearing for `Select`, not merely compatible with it.

## A SECOND, INDEPENDENT CAUSE — do not stop at the mixin

`on_valid` / `on_invalid` do **not** come from the mixin. They come from the event map:

```
_TEXTFIELD_EVENTS   change, input, valid -> <<Valid>>, invalid -> <<Invalid>>, ...
_SELECT_EVENTS      change                            <- everything else absent
```

Inheriting the mixin does not fix this. It is real rather than cosmetic: `ValidationMixin` on the entry part emits both events, and `Select`'s entry is a `TextEntryPart`, **so `<<Valid>>` and `<<Invalid>>` fire today with nothing listening.**

⚠ **Do not copy `TextField`'s wiring blind.** `Select` overrides `_event_target` to route inner-entry sequences, so the fix must establish **which object the two events actually land on** before adding the map entries.

## The gate ships too — measured, not assumed

Inheriting brings `_VALIDATION_KIND`, which makes `add_validation_rule` reject rules that do not apply. That **raises where the framework currently accepts**, which normally means `0.5.0`.

⚠ **It ships in `0.4.0` anyway, and the reason is measured.** Of the seven rule types, **exactly one is newly rejected — `range` — and it can never pass today**:

```
Select value=1   range 5..10 -> valid=False
Select value=7   range 5..10 -> valid=False      <- 7 IS in range
Select value=12  range 5..10 -> valid=False
value handed to the rule: '7'  (str)
```

The rule receives a string and compares it against numbers, so it fails unconditionally. **No user has working code to break** — anyone who attached one has a permanently-invalid field with no way to read the message, which is #465 compounding it. Rejecting at attach time converts a silent always-fail into a clear error.

**The batching rule protects users from repeated migrations. Here the migration count is zero.** Shipping a gate-less override to honor a rule about a break that does not exist would preserve the exact hand-copy divergence that caused this defect.

Boundary of that claim, so it is checked as written: `rule_applies_to_kind(rt, "text")` over the full rule set — `required`, `stringLength`, `pattern`, `email`, `range`, `compare`, `custom` — cross-checked against live construction on a real `Select`.

## The change

1. **`select.py`** — `class Select(ValueSignalMixin, FieldAddonMixin, PublicWidgetBase)`.
2. **Delete the hand-copied `add_validation_rule`** (line ~175). The mixin's version supersedes it, gate included.
3. **`_SELECT_EVENTS`** — add `valid` and `invalid`, after confirming the target object.
4. **`on_valid` / `on_invalid`** `@overload` pairs, matching `textfield.py:349/366`.
5. Keep `Select`'s own `validate` and `text` overrides — they win in the MRO and carry `Select`-specific bodies.

Everything else is inherited. **Expected: one production file, a net DELETION of wrapper code.**

## Tests

⚠ **Not `hasattr`, and not "construction doesn't raise".** Each test must be able to fail while the member exists — that is the vacuity gate, and #458 round 1 shipped exactly that shape.

1. `error` carries the message after a failing rule; `valid` tracks **both** directions (False after failure, True after a valid selection).
2. `select.valid is select._internal._entry._valid_signal` — catches a "fix" returning a detached `Signal` that reads `True` forever.
3. `bs.Label(textsignal=select.error)` follows a failed validation — the reporter's actual use case.
4. `on_valid` / `on_invalid` fire, with the `ValidationEvent` payload.
5. **The gate**: `range` now raises `BootstackError`; `required`, `stringLength`, `pattern`, `email`, `compare`, `custom` still attach. Pin all seven — the whole point is that only one moved.
6. **Addons work on a `Select`**, alongside the built-in `'dropdown'` addon.
7. **Control, run once and recorded:** break the mixin's `valid` body and confirm 1–3 fail.

## Docs and CHANGELOG

- Check whether `Select`'s reference page claims validation support it lacked.
- CHANGELOG under `## [Unreleased]`, one paragraph per line. **Reachable, so it earns an entry.** It is both `Fixed` (no way to read a validation outcome) and `Added` (`valid`/`error`/addons/events) — say which is which. ⚠ **Mention the `range` rejection**: it is the one visible behavior change, even though nothing working depended on it.

## Follow-ups to file, NOT fix here

- **Mode 6 — capability gap.** The #463 audit's five modes all take a constructor keyword as their unit, so a missing member is invisible to every one of them. #465 proves it. A one-hop scan exists at `development/probe_wrapper_capability_gap.py`; ⚠ **its control shows it CANNOT see #465 itself** (the capability sits two hops down behind underscore names), and ~3,000 candidate members are enumerated with **zero** classified. **It is an instrument with a stated ceiling, not a guard.** #466 needs amending: a parameter-level snapshot cannot see members.
- **Whether `TextArea` / `CodeEditor` have the same shape** — they are `Field`-adjacent but carry their own `_valid_signal` instead of the entry's.
