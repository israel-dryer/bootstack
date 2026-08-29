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

| value | `custom` func `v > 5` (before) | `range` `min=5` | why `range` differs |
|---|---|---|---|
| `None` | **TypeError** | valid | `_is_empty` short-circuit at `:140` |
| `''` | **TypeError** | valid | same short-circuit |
| `'6'` | **TypeError** | **invalid** | its `except TypeError` at `:149-151` |

`range` catches `TypeError` at `:149-151`; `custom` calls `func(value)` bare at `:155-158`.
**Nothing about `custom` justifies the difference.**

⚠⚠ **BE PRECISE ABOUT WHAT THIS MATCHES — AN EARLIER DRAFT OF THIS FILE OVERSTATED IT.** The fix
matches **`range`'s `except TypeError` branch**, not `range`'s whole answer. `range` returns *valid*
for `None`/`''` because of an empty short-circuit that `custom` does not have and **is not getting
here** — `custom` is in neither `TEXT_RULES` nor `ORDERED_RULES` **by existing design**, so its func
already sees empty values and decides for itself. **Adding a short-circuit would stop calling funcs
that DO handle empty, which is a bigger change and out of scope.**

⚠ **SO THERE IS A REAL BEHAVIOR CHANGE TO STATE: an optional empty field whose custom func raises on
`None` now reports INVALID where it previously stayed stale-valid.** Chosen deliberately — an
unjudged value passing into a form submit is worse than a blocked one, and it matches what `range`
does the moment its comparison actually fails. ⚠ **But it is the half most likely to surprise, so it
belongs in the CHANGELOG and in any review of this branch.**

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
   invalid with the rule's message instead of propagating. ⚠ **Do NOT assert this equals `range`'s
   answer for `None`/`''`** — it does not, and the reason is in the table above.
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

---

## FOR THE REVIEWER — round 1

⚠ **`REVIEW-PROTOCOL.md` says not to read the implementer's rationale for why the approach was
sound.** Much of this file is exactly that. **Read the sections above for REQUIREMENTS and for the
DECISIONS that must not be re-litigated; do not read them as an argument that the code is right.**
The list below is what to attack.

**Scope:** round 1 reviews the branch — `git diff main...HEAD`. Two commits: the plan, and
`cc7c6e4c` (the fix, tests, CHANGELOG, docs).

**Round cap 2, spent 0.**

### The five places this is most likely to be wrong

1. **Decision 2 — the manual path now absorbs.** `field.validate()` returns `False` where it used
   to raise. The issue argued the manual path was fine as-is. **Is a rule that behaves the same on
   both triggers worth breaking a caller's traceback for?** If not, the guard belongs at
   `validation_mixin.py:119` instead. **This is the decision most worth overturning.**
2. **The empty-field consequence.** An optional field whose func raises on `None` now reports
   INVALID where it previously stayed stale-valid — so a user can be blocked from submitting a form
   with a blank optional field. **`docs/reference/validation.rst` argues elsewhere that a non-`required`
   rule must not block a blank field.** Is reporting invalid the wrong answer here? The alternative
   is reporting *valid* on a raise, which lets an unjudged value through.
3. **`except Exception` breadth.** Too wide? It swallows programming errors in the func —
   `NameError`, a typo'd attribute — and reports them to the end user as "invalid".
4. **`debug_log_exception` is gated on `BOOTSTACK_DEBUG`, so by default NOTHING is printed.** The
   issue's second option was *"propagate, but not silently."* **This ships the absorb half and a
   surface half that is off by default. Is that actually a fix, or is it the silent-swallow the
   issue warned about wearing a log call?**
5. **Gate 2 on the tests — vacuity and false alarm only.** Specifically:
   `test_the_blur_trigger_leaves_a_defined_validity` calls `_entry.validate(value, "blur")`
   **directly rather than synthesizing a real blur**, so it does not prove the `<FocusOut>` binding
   and the debounced `after()` still reach the rule. ⚠ **It is one layer short of the real path and
   the author knows it** — is that vacuous, or adequately covered by its two controls?

### What was measured, so it need not be re-derived

- **The issue's own reproduction does not fire.** `custom` defaults to `trigger="manual"`
  (`validation_rules.py:221-222`), documented at `docs/reference/validation.rst:190-192`.
  `validate('6','blur')` returns `True` with the rule skipped.
- **Pre-fix control: the new tests fail 9 of 14** against stashed `src/`, each on a propagating
  exception rather than a missing attribute.
- **Suite 1690 / 33, exit 0, 33 legs** on macOS at the branch tip — `1676 + 14`, bounded by
  `git diff --cached --stat -- tests/` returning one file and `--collect-only` saying 14.
- **Docs clean-build passes `-W`.**
- **No import cycle** from the new `_runtime.utility` import; `validation` still imports and
  validates standalone with no Tk root.

### Known not done

- **No test drives a REAL `<FocusOut>`** end to end (see item 5).
- **`range`'s own silence is untouched** and out of scope.
