# PLAN — #467 (a `custom` rule's exception leaves the field's validity stale)

Branch `fix/custom-rule-exception-467`, off `main` at `fd59cf0d`. Milestone `0.4.0`.

**Round cap: 2** (patch-shaped change; see Compatibility below).

⚠ **READ THE 2026-08-29 COMMENT ON #467 BEFORE THIS FILE.** It carries the re-measurement that
narrows the issue, and **the reproduction in the issue BODY does not reproduce.** Do not re-derive.

---

## The defect, as measured — not as filed

⚠⚠ **THE ISSUE'S REPRODUCTION DOES NOT FIRE, AND THE REASON IS DOCUMENTED BEHAVIOR.** `custom`
rules default to `trigger="manual"` (`validation_rules.py:221-222`), which
`docs/reference/validation.rst:190-192` states outright. The repro never passes `trigger=`, so
the rule is **skipped** on blur:

```
rule.trigger as written : manual
validate('6','blur')    -> True      -- rule SKIPPED, no exception
validate('6','manual')  -> TypeError -- reaches the CALLER, which the issue calls acceptable
```

**Reaching it requires a deliberate `trigger="blur"` or `"always"`.** With that opt-in, driven
through the real debounced `after()` path:

```
exceptions reaching report_callback_exception : 1
  TypeError: '>' not supported between instances of 'str' and 'int'
f.valid : True     <- validity did NOT update
f.error : ''
```

⚠ **THE HARM THAT MATTERS IS THE SECOND ONE, AND THE ISSUE MENTIONS IT ALMOST IN PASSING.** That
the author cannot catch the exception is defensible as author error — they wrote a raising func
and opted into automatic evaluation, and Tk prints the traceback via
`report_callback_exception`. **What is NOT theirs is the field silently keeping stale validity:**
the end user sees a field that has quietly stopped validating, with nothing to indicate it.
**That is the standing principle — the framework absorbs the problem, and an end-user outcome
worse than the bug is not a fix.**

## The asymmetry is the argument

Identical comparison, two rule types, measured at unit level:

| value | `custom` func `v > 5` | `range` `min=5` |
|---|---|---|
| `None` | **TypeError** | absorbed -> invalid |
| `''` | **TypeError** | absorbed -> invalid |
| `'6'` | **TypeError** | absorbed -> invalid |

`range` catches `TypeError` at `:149-151`; `custom` calls `func(value)` bare at `:155-158`.
**Nothing about `custom` justifies the difference** — and `custom` is in neither `TEXT_RULES` nor
`ORDERED_RULES`, so `None` and `''` reach the func unguarded too.

---

## The fix

Guard `func(value)` in `ValidationRule.validate`'s `custom` branch, mirroring the `range` branch
directly above it:

```python
elif self.type == "custom":
    func: Callable[[str], bool] = self.params.get("func")
    if func:
        try:
            ok = func(value)
        except Exception:
            # A custom func that cannot judge this value has not produced a
            # verdict. Report invalid -- the same answer `range` gives an
            # incomparable pair -- rather than leaving validity stale.
            debug_log_exception(f"custom validation rule raised for value {value!r}")
            return ValidationResult(False, msg)
        if not ok:
            return ValidationResult(False, msg)
```

**Three decisions, each with its reason:**

1. ⚠ **AT THE RULE, NOT THE MIXIN.** `range`'s guard is here, so putting `custom`'s anywhere else
   re-creates the asymmetry one layer up. It also covers every caller at once.
2. ⚠⚠ **THIS MAKES THE MANUAL PATH ABSORB TOO, AND THAT IS DELIBERATE — FLAG IT TO THE MAINTAINER.**
   The issue says the manual path "is fine" because the exception reaches the caller. **`range`
   does not distinguish manual from automatic and neither should this.** A rule that behaves
   differently by trigger is the same arbitrary split in a new place. **Cost, stated plainly: an
   author whose `field.validate()` used to raise now gets `False` back instead.** ⏭ **If the
   maintainer wants the manual raise preserved, the guard moves to `validation_mixin.py:119` and
   this decision reverses — do not silently keep both.**
3. ⚠ **`except Exception`, not `except TypeError`.** `range` only compares, so `TypeError` bounds
   it. A user func can raise anything — `AttributeError`, `KeyError`, a domain exception. Narrowing
   to `TypeError` would leave every other exception escaping, which is the bug with extra steps.
   **`BaseException` is deliberately NOT caught** — `KeyboardInterrupt`/`SystemExit` must pass.

⚠ **`debug_log_exception` is gated on `BOOTSTACK_DEBUG`, so by DEFAULT nothing is printed.** That
matches `range`, which is silent today. **It is a weak surface and worth knowing about**, but the
alternative — printing unconditionally from inside a Tk dispatch — is the trap this file already
warns about. **Never `warnings.warn` here.**

## Tests

New `tests/widgets/public/test_custom_rule_exception.py`:

1. **The unit asymmetry closes.** A `custom` func raising `TypeError` on `None`/`''`/`'6'` reports
   invalid with the rule's message — the same verdict `range` gives the same values.
2. **`except Exception` breadth.** A func raising `AttributeError` and one raising a custom
   exception class are both absorbed. ⚠ **This is the arm that fails if someone "tightens" the
   catch to `TypeError`.**
3. **`KeyboardInterrupt` still propagates.** The control for decision 3.
4. **The automatic path leaves a DEFINED state.** With `trigger="blur"`, driven through the real
   debounced `after()`, the field ends `valid=False` with the message — **not** `valid=True`.
   ⚠ **Its control is a func returning `False`**: without one, an arm that never fires the trigger
   is indistinguishable from a fix that works. **The first probe written for this issue failed
   exactly that way and its quiet arms were meaningless.**
5. **A passing func is unaffected** — no behavior change for the ordinary case.

⚠ **Gate 2 applies to the tests: the only actionable defects are vacuity and false alarm.**

## Compatibility

**Patch-shaped: adds no public surface and does NOT raise where the framework accepts — it stops
raising.** It rides `0.4.0` because that minor is being cut anyway and this file's standing rule is
to ask what else is ready rather than park a fix out of habit. ⚠ **It does NOT meet `0.5.0`'s
membership rule** (raises, or retypes a public property), so it does not belong there.

## CHANGELOG

⚠ **This one EARNS an entry, unlike PRs #492/#493/#494** — the behavior is reachable from public
API (`add_validation_rule('custom', ..., trigger='blur')`) and an app's observable outcome changes.
**Say what the user sees**: a field that silently stopped validating now reports invalid. **Name the
manual-path change too** (decision 2) — that is the half an upgrader could be surprised by.

## Out of scope

- **The `Select` decode bug** the issue's repro leans on. Filed separately; not needed to reach this.
- **Whether `range`'s silence is right.** This fix matches `range` deliberately. Changing both is a
  different question.
- ⚠ **Making `debug_log_exception` louder.** Real, but it is a framework-wide diagnostics decision,
  not this issue's.
