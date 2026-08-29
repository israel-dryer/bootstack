# REVIEW — #467 round 1

Branch `fix/custom-rule-exception-467`, reviewed at `8b8e0964`. Scope: `git diff main...HEAD`.
**Round cap 2, spent 1 after this round.**

Environment: macOS box, `.venv/bin/python` 3.14.0, `matplotlib` present, `pandas` ABSENT.

Probes written for this round, kept as the record:
`development/probe_467_review_round1_real_blur.py` (the real `<FocusOut>` path, both arms) and
`development/probe_467_review_round1_form_manual.py` (`Form.validate()`, both arms). Both print
which arm they are on by reading `validation_rules.py`. The `main` arm was run from a
`git worktree` at `main` with `PYTHONPATH` set and provenance printed — the branch was never
touched while the review ran.

---

## Findings

### F1 — BLOCKING. The fix removes the only diagnostic that was visible by default, on both paths it changes.

`src/bootstack/validation/validation_rules.py:161-177`

**Measured, not argued.** Both arms, same probe:

| path | `main` | branch |
|---|---|---|
| real `<FocusOut>` → debounced `after()` | **full traceback on stderr** (Tk's `report_callback_exception`), `field.valid()` stale `True` | `field.valid()` `False`, **nothing printed** |
| `Form.validate()` (`form.py:351`, trigger `manual`) | **raises `TypeError` at the call site**, `form.valid()` stale `True` | returns `False`, **nothing printed** |

Root cause: `debug_log_exception` returns immediately unless `BOOTSTACK_DEBUG` is set
(`_runtime/utility.py:375`), so by default the guard writes nothing anywhere. The end-user half of
#467 is genuinely fixed; the **author-facing** half is worse than before the branch. An author whose
predicate is broken now sees a field that reports "must exceed 5" for every value, with no console
output, no exception, and no way to find the function that raised unless they already know
`BOOTSTACK_DEBUG` exists.

**The plan's "this matches `range`, which is silent today" does not transfer, and that is the
discriminator the symmetry argument hides.** `range`'s silence is about *data* — an incomparable
pair can arrive from user input against a bound the author typed correctly. A `custom` func that
raises is *always* a defect in the author's own code. Staying silent about bad data is a policy
choice; staying silent about a bug in the caller's function is the framework hiding a defect from
the only person who can fix it. That is the standing principle inverted: the framework has absorbed
the problem *and* the evidence.

The issue offered two options and this ships neither: not "propagate", and not "not silently".

**Suggested minimal change.** Keep the absorb. On the **first** raise per rule instance, write one
line to stderr naming the exception and pointing at `BOOTSTACK_DEBUG`; keep `debug_log_exception`
for the traceback on every occurrence. One-shot is required, not cosmetic: `trigger="always"` runs
the rule on every keystroke through `_debounced("key", 50)`, so an unconditional print floods the
console as the user types.

⚠ **This is deliberately NOT "make `debug_log_exception` louder"**, which the plan correctly scopes
out as a framework-wide decision. It is narrower: do not let *this* site end up quieter than the
code it replaced.

### F2 — should-fix. The guard's own diagnostic can raise, escaping the guard.

`validation_rules.py:174-176`

`debug_log_exception(f"custom validation rule raised for value {value!r}")` builds its f-string
**eagerly, inside the `except` block, whether or not debug is enabled**, so `repr(value)` runs on
every raise. Measured:

```
hostile repr ESCAPED THE GUARD: RuntimeError repr exploded
```

A value whose `__repr__` raises re-opens exactly the defect the branch exists to close, now with a
chained traceback. Reachability is thin but real — a rule's value is the field's *typed* value, and
a `Select`'s value kind is whatever its options carry (#465), so arbitrary user objects reach here.

**Suggested minimal change:** wrap the whole diagnostic block in `try/except Exception: pass`, the
same guarantee `debug_log_exception` already makes internally ("Never raise from debug logging").

### F3 — should-fix (file, do not fix here). A non-callable `func` is now absorbed as "invalid".

`validation_rules.py:157`

Measured: `ValidationRule("custom", func="not a function").validate("6")` returned
`is_valid=False, message='m'`. On `main` it raised `TypeError: 'str' object is not callable`. So a
*configuration* error — `func=my_validator()` where `my_validator` was meant unevaluated — now
reports the end user's value invalid with no signal at all by default.

This is the plan's item 3 in its sharpest form, and the plan considered only errors *inside* the
func, not the func not being one.

⚠ **F1's fix substantially mitigates it** — the one-line stderr warning names
`TypeError: 'str' object is not callable`, which is the whole diagnosis. The residue is that it no
longer raises. Closing that properly means a `callable(func)` check at rule construction, which
**raises where the framework currently accepts** — `0.5.0`'s membership rule, not this branch's
shape. **File it; do not widen this branch.**

### F4 — should-fix (docs). The API-reference docstring does not carry the new behavior.

`validation_rules.py:97-105`

`ValidationRule.validate()`'s `Returns:` still says only "`is_valid=True` on success or
`is_valid=False` with an error message on failure". `ValidationRule` is autodoc'd
(`docs/reference/validation.rst:340`) and `docs/reference/validation.rst:304-318` tells readers to
use the rule engine **without a widget** — that reader gets the narrative page's new paragraph only
if they scroll back to the widget section. Add one sentence to the docstring.

### F10 — BLOCKING (raised by the maintainer while driving the demo). A crashed predicate wore the rule's message, and the message could be false.

`validation_rules.py` — the `custom` raise path returned `ValidationResult(False, msg)`, where `msg`
is the rule's own `message`.

**Found by clicking, not by reading.** Driving
`development/demo_467_custom_rule_exception.py`, the maintainer hit a field holding **6** reporting
**"must exceed 5"** — a message that is plainly false of the value in it. The rule's `message`
describes a *condition*; the predicate had crashed rather than evaluated, so nothing had been
established about that value at all, and the framework asserted the condition anyway.

That is the standing principle failing on the far side: the framework absorbed the author's problem
and handed the **end user** a false explanation instead. It also makes a crashed predicate and a
genuine verdict indistinguishable on screen, which is the one distinction anyone debugging needs.

⚠ **Round 1 had this in its hands and let it through.** The plan's item 3 named it — "it swallows
programming errors in the func and reports them to the end user as 'invalid'" — and the first pass
of this review upheld the breadth of `except Exception` without noticing that the *message* was the
sharper half. **The tests encoded the wrong answer too**: two of them asserted
`message == "must exceed 5"` on the raise path, so the suite was pinning the defect.

**Resolution, in two maintainer decisions.** First: a distinct message on the raise path, never the
rule's own. Then, on reading it: *"'this value could not be checked' is not very useful either"* —
correct, and the bare sentence threw away the one thing the framework still knew. The shipped answer
**demotes the author's message from a verdict to an expectation** rather than discarding it:

| the rule's `message` | what a raise reports | what a genuine `False` reports |
|---|---|---|
| `"must be over 5"` | `Could not check this value (expected: must be over 5).` | `must be over 5` |
| `"Enter a valid email address."` | `Could not check this value (expected: Enter a valid email address).` | `Enter a valid email address.` |
| *(none given)* | `Could not check this value.` | `Invalid value.` |

⚠ **`_uncheckable_message` reads `self.message`, NOT the resolved `msg`.** When the caller supplied
none, `_default_message()` returns *"Invalid value."*, and composing that yields
*"Could not check this value (expected: Invalid value.)"* — nonsense. The empty-`self.message` case
is the fallback, and `test_a_rule_with_no_message_falls_back_to_the_bare_sentence` pins it.
⚠ The author's trailing period is stripped before composing, or the message ends `.).` — pinned by
`test_the_expectation_is_not_double_punctuated`.

⚠ **This deliberately diverges from `range`**, which still reports its own message for an
incomparable pair. The divergence is commented at the constant so it reads as a decision rather than
an oversight. ⏭ **`range` has the identical flaw and is NOT fixed here — file it**, and decide the
family's answer in one place.

**Tests:** the two assertions that pinned the old message now assert the composed form and
`!= "must exceed 5"`; `test_the_blur_trigger_control_a_failing_func_is_visible` gained an assertion
that a *verdict* still carries the rule's message on its own; and three new tests pin the
distinction, the no-message fallback and the punctuation. 19 → 22 tests.

⚠⚠ **THE DURABLE LESSON, AND IT IS THE SAME ONE #486 PAID FOR: A DEMO FOUND WHAT TWO PASSES OF
READING DID NOT.** The suite was green, the review was written, and the defect was visible in the
first five seconds of anyone actually using the thing. **Build the demo before declaring the round
clean, not after.** ⚠ **And the demo's own first draft hid it** — it labelled the panel "must exceed
5" with no hint that the predicate never ran, so the misleading message read as the demo being
broken rather than the framework. An instrument that obscures the thing it is pointed at is worse
than no instrument.

### F5 — note (gate 2). One of the two blur controls cannot fail.

`tests/widgets/public/test_custom_rule_exception.py:105` —
`test_the_blur_trigger_control_a_passing_func_stays_valid`.

`ValidationMixin.validate` returns `True` **vacuously when no rule ran for this trigger**
(`validation_mixin.py:135`), and `_valid_signal` is seeded `True` at construction
(`validation_mixin.py:57`). So both of this test's assertions pass whether the rule ran or not —
it carries no weight as a control.

**Not actionable**, and no fix: its sibling
`test_the_blur_trigger_control_a_failing_func_is_visible` **is** discriminating (`False` is only
reachable if the rule ran), which is the control the regression test needs. Recorded so a later
round does not mistake the pair for two controls.

### F6 — note (gate 2). The blur test is a layer short, and it is not vacuous.

`test_custom_rule_exception.py:88` calls `field._internal._entry.validate(field.value, "blur")`
rather than synthesizing a real `<FocusOut>`. The author flagged this.

**Verified independently rather than accepted.** `probe_467_review_round1_real_blur.py` drives a
real focus change plus the 50 ms debounce:

```
ARM: MAIN (no guard)
  arm1 raising func      : valid=True  error=''        <- stale, plus a traceback on stderr
  arm2 control False func: valid=False error='must exceed 5'
  arm3 control True func : valid=True  error=''
ARM: BRANCH (guard present)
  arm1 raising func      : valid=False error='must exceed 5'
  arm2 control False func: valid=False error='must exceed 5'
  arm3 control True func : valid=True  error=''
```

Arm 3 is what makes arm 1 mean something: the trigger fires and can still report valid, so
`valid=False` is the rule deciding rather than a field stuck invalid.

So the untested layer (`<FocusOut>` → `_debounced` → `after`) does reach the rule, is untouched by
this diff, and the test cannot pass while the fix is broken. **No fix**: a real-blur test in the
shared-root harness buys the false-alarm risk this file warns about repeatedly (`focus_set()` is a
silent no-op on an unmapped widget; a widget packed into the shared root may not be mapped at all).
The probe is the record instead.

### F7 — note (file). `'compare'` invokes user code too, and stays unguarded.

`validation_rules.py:180-181` → `_read_other` (`:190-199`) calls `other()` when `other_field` is a
`Signal` or any zero-argument callable — documented public surface
(`docs/reference/validation.rst:153-156`). A callable that raises reproduces #467 one rule over.
Out of this branch's scope; worth its own issue so the asymmetry is closed rather than moved.

### F8 — nit. `if not passed` sits outside the guard.

`validation_rules.py:178`. A func returning an object whose `__bool__` raises still escapes
(measured: `weird bool ESCAPED: RuntimeError bool exploded`). Contrived, and moving the truthiness
test inside the `try` changes what the guard means. Recorded, not fixed.

---

## Cleared, with the measurement — do not re-derive in round 2

- **Decision 1 (guard at the rule, not the mixin) is right and load-bearing.** `TextArea` and
  `CodeEditor` do **not** go through `ValidationMixin` — they carry their own rule loop calling
  `rule.validate(value)` at `textarea.py:330` and `codeeditor.py:496`. A guard at
  `validation_mixin.py:119` would have missed both widgets entirely.
- **Decision 2 (the manual path absorbs too) is upheld — but NOT by the symmetry argument the plan
  gives, and the issue's premise is false.** The framework itself drives the manual trigger from
  inside a Tk dispatch with no author call site: `FormDialog`'s submit handler calls
  `self.form.validate()` (`formdialog.py:552`) → `entry.validate(..., trigger="manual")`
  (`form.py:351`). Measured: on `main` `form.validate()` raises out of the handler and
  `form.valid()` stays `True`; on the branch it returns `False` and `form.valid()` is `False`.
  **"The manual path is fine because the caller catches it" is not true of the framework's own
  caller.** ⏭ Round 2 should not re-open this.
- ⚠⚠ **#467 IS REACHABLE WITH THE DEFAULT TRIGGER AND NO OPT-IN AT ALL, THROUGH A `FormDialog`
  SUBMIT — AND BOTH THE PLAN AND THE CHANGELOG UNDERSTATE THIS.** The plan's framing is that the
  issue's repro does not fire because `custom` defaults to `trigger="manual"`, so reaching the harm
  "requires a deliberate `trigger='blur'` or `'always'`". True of a field in isolation, **false of a
  form**: `Form.validate` passes `trigger="manual"`, under which the loop skips nothing and **every
  rule runs**, including a default-trigger `custom` one. Driven through `_accept_press`
  (`formdialog.py:526`), which is what a submit button press calls
  (`development/probe_467_review_round1_formdialog_press.py`):

  ```
  ARM: MAIN     _accept_press RAISED: TypeError '>' not supported ...   form.valid -> True
  ARM: BRANCH   _accept_press -> False                                  form.valid -> False
  ```

  On `main` the press raises inside the button handler: the submit does nothing, the dialog stays
  open, and `form.valid` still reads `True`. **No `trigger=` anywhere.** ⏭ **This is the strongest
  argument for decision 2 and it is stronger than the symmetry the plan gives it.**

- **F9 — should-fix (round 2 or maintainer). The CHANGELOG's last sentence frames the manual path as
  yours alone.** It reads *"The same guard applies when you call `validate()` yourself, so a raising
  function returns `False` there instead of propagating to your call site."* Accurate but
  incomplete: the measurement above shows a manual-trigger raise with **no call site of yours**,
  inside a `FormDialog` press. A reader deciding "does this affect me?" would conclude they are only
  affected if they call `validate()` themselves or opt into an automatic trigger, and that is wrong.
  **Not fixed here** — it is user-facing prose about blast radius, and widening it is the
  maintainer's call, not a reviewer's drive-by.

- **Item 2 (an optional field whose func raises on empty now reports invalid) is upheld.** The
  blank-field value reaching the func is `None` (measured through `Form`), and
  `validation.rst:139-141` already told authors that `custom` runs on an empty field and that they
  must accept it explicitly. The new paragraph is consistent with it and the CHANGELOG carries the
  upgrade warning. Reporting *valid* on a raise would let an unjudged value into a submit.
- **Item 3 (`except Exception` breadth) is upheld**, with F3 as the residue.
- **The fix has exactly one call site to cover.** `grep -rn 'params.get("func")' src/` returns one
  hit (`validation_rules.py:157`); nothing else in the package invokes a `custom` rule's func.
- **The CHANGELOG's claim about prior behavior was checked against `main` by running it, not by
  reading the fix.** "the field silently kept whatever validity it already had" — reproduced on the
  `main` arm of both probes.
- **No import cycle and no new import cost.** `bootstack._runtime.utility` has no module-level
  imports beyond the stdlib it defers into functions; `import bootstack` succeeds, and the
  `validation` package imports and validates standalone.
- **Suite:** see the resolution block below.

---

## Fix step — blockers only

Re-ranked before touching code: **F1 blocking; F2 should-fix; F3, F4 should-fix; F5–F7 notes; F8 nit.**
Only F1 was fixed on its own account. **F2 was fixed with it because both live in the same statement**
— the blocker's fix rewrites the diagnostic line, and re-emitting a known escape while rewriting it
would be perverse. F3, F4 and F5–F8 were left, per "fix blockers only".

### F1 + F2 — FIXED. `src/bootstack/validation/validation_rules.py`

**Root cause, stated before editing:** the branch implemented the *absorb* half of the issue's second
option and not the *"not silently"* half. `debug_log_exception` returns at its first line unless
`BOOTSTACK_DEBUG` is set, so the guard replaced two default-visible signals — Tk's
`report_callback_exception` traceback on the automatic path, and the propagated exception on the
manual one — with nothing. Separately, the diagnostic built `f"... {value!r}"` eagerly inside the
`except` block, so `repr(value)` ran on every raise and could throw straight back out.

**Change:** the `except` block now calls a new `ValidationRule._report_func_error(exc, value)`.
On the **first** raise per rule instance it writes one line to stderr naming the exception type, its
message, and `BOOTSTACK_DEBUG`; `debug_log_exception` still carries the traceback on every
occurrence. The whole body is wrapped in `try/except Exception: pass`, the same guarantee
`debug_log_exception` already makes internally, so no diagnostic can become the failure it reports.
A `_func_error_reported` latch is initialised in `__init__`.

⚠ **One-shot is load-bearing, not cosmetic.** A rule with `trigger="always"` runs on every keystroke
via `_debounced("key", 50)`; an unconditional print would flood the console as the user types. That
is why this is not "make `debug_log_exception` louder" — which stays out of scope, correctly.

**Measured after the fix, on the real automatic path** (`development/probe_467_review_round1_real_blur.py`):

```
bootstack: a 'custom' validation rule's func raised TypeError: '>' not supported
between instances of 'str' and 'int' -- the value is reported invalid. Set
BOOTSTACK_DEBUG=1 for the traceback.
ARM: BRANCH (guard present)
  arm1 raising func      : valid=False error='must exceed 5'
  arm2 control False func: valid=False error='must exceed 5'
  arm3 control True func : valid=True  error=''
```

The end-user half of #467 still holds, and the author now gets a pointer to the function that raised.

⚠ **F10 (below) changes what this path returns.** The message comes from `_uncheckable_message()`,
not from `msg`.

⚠ **F3 is substantially mitigated as a side effect and needs no separate change here.** A
non-callable `func` now prints
`a 'custom' validation rule's func raised TypeError: 'str' object is not callable`, which is the
whole diagnosis. The residue — that it no longer raises — is still worth an issue.

**Regression tests added** to `tests/widgets/public/test_custom_rule_exception.py` (14 → 19):

| test | what it pins |
|---|---|
| `test_the_first_raise_is_reported_on_stderr` | F1: the message exists, names the exception, names the env var |
| `test_the_report_does_not_repeat_for_the_same_rule` | the one-shot latch |
| `test_a_func_that_does_not_raise_reports_nothing` | CONTROL: the channel is quiet for the ordinary case |
| `test_a_value_whose_repr_raises_does_not_escape_the_guard` | F2 |
| `test_a_value_whose_repr_raises_does_not_escape_with_debug_on` | F2's other arm, where `debug_log_exception` really runs |

**Control run, against the pre-fix guard** (`git show HEAD:src/.../validation_rules.py` into a copied
tree, `PYTHONPATH` set and provenance printed): **3 failed, 16 passed** — the three that name F1 and
F2 fail, and the rest are untouched.

⚠ **The two that pass on both arms are controls, not regression tests, and the record says so on
purpose.** `test_the_report_does_not_repeat_for_the_same_rule` and
`test_a_func_that_does_not_raise_reports_nothing` both assert *silence*, which the pre-fix code gives
for free. They only carry weight next to `test_the_first_raise_is_reported_on_stderr`. Same shape as
F5 — recorded so a later round does not read four discriminating tests where there are three.

**Docs and CHANGELOG updated with the fix, not separately from it.** The branch's new paragraph in
`docs/reference/validation.rst` and its CHANGELOG bullet both said only "the traceback goes to the
debug log"; both now name the one-line stderr report as well. Leaving them behind would have shipped
a console message the docs do not mention.

### F4 — FIXED, as part of F10

`ValidationRule.validate()`'s `Returns:` block now states that a raising `custom` func is reported
invalid and carries `UNCHECKABLE_MESSAGE` rather than the rule's own. F10 changed what that path
returns, so leaving the docstring describing the old answer was no longer a should-fix — it would
have been wrong rather than merely thin.

### F3, F5, F6, F7, F8 — NOT FIXED

Per "fix blockers only". F3 is should-fix and survives to round 2 or to an issue; F5–F8 are notes and
nits and are recorded, not fixed — gate 2 makes test diagnostics and probe ergonomics notes by
construction, and F7/F8 are out of the branch's scope.

⏭ **Two issues to file if the cap runs out** (both pre-existing, neither introduced by this branch):

1. **`range` reports its own message for an incomparable pair** (F10's residue), so it can assert a
   condition of a value it never compared — the same defect this branch just fixed for `custom`. Not
   touched here on purpose; the two rule types now differ, and the family's answer belongs in one
   place.
2. **A non-callable `func` is absorbed rather than refused** (F3). A `callable()` check at rule
   construction is the fix, and it **raises where the framework currently accepts** — `0.5.0`'s
   membership rule.
3. **`'compare'` invokes user code unguarded** (F7). `_read_other` calls `other_field` when it is a
   `Signal` or a callable — public, documented surface — and a raise there reproduces #467 one rule
   over.

---

## Verification

Everything below was run on the macOS box, `.venv/bin/python` 3.14.0, at the post-fix working tree.

- **Suite: `1698 passed / 33 skipped`, 33 legs, exit 0, no failures.** That is `1690 + 8`, the eight
  new tests, bounded the usual way: `git diff main...HEAD --stat -- tests/` names one test file and
  its `--collect-only` says 22 (was 14). ⚠ **This figure moved three times as F10 was settled**
  (`1695` → `1696` → `1698`). **Record the last one and the commit it was taken at; the earlier two
  describe test files that no longer exist in that shape.**
- **Pre-fix control for the new tests: `3 failed, 16 passed`** against the branch's own pre-fix
  `validation_rules.py`, restored with `git show HEAD:...` into a copied tree with `PYTHONPATH` set
  and provenance printed. The three that fail are the three that name F1 and F2.
- **Docs clean-build: `build succeeded`, exit 0** with `-W --keep-going` after `rm -rf docs/_build`.
- **`import bootstack` succeeds** — run before the suite, not after.
- **`git diff main...HEAD -- CLAUDE.md` is empty.**

⚠ **One environmental note, recorded so it is not read as a finding.** An earlier full-suite run
**hung** in the shared leg inside `tests/widgets/public/test_tree.py`, on the same run where all 11
of `test_capture.py`'s screenshot tests failed with `PIL.UnidentifiedImageError` — the documented
macOS symptom of a display that is not active and unlocked. `test_tree.py` passes **40/40
standalone** (13 s), the run before the fix got through the same file, and the re-run after the fix
is green end to end. **This is the display state, not the branch**; `test_capture.py`'s 11 failures
also reproduced identically on a `main` worktree.

---

## A demo, for driving it by hand

`development/demo_467_custom_rule_exception.py`, with
`development/probe_467_demo_driver.py` to drive it headlessly and print an expectation beside each
panel.

⚠ **The demo went through three drafts and only the third one teaches the right thing** — the
maintainer redirected it twice, and both redirections were correct. Draft 1 used `lambda v: v > 5`
on a `TextField`, which raises on **every** value, so a field holding **6** displayed
*"must exceed 5"* and read as a validation bug rather than a demonstration. That is what surfaced
F10. Draft 2 used `int(v) > 5` — a predicate someone would really write, which judges `"6"`
correctly and raises only on the inputs its author forgot. Draft 3, the one committed, is built
around the maintainer's framing: **the real issue is making the predicate match the type the field
hands it.** Measured, and the table is the demo:

| the predicate | `'6'` | `'abc'` | `None` (empty TextField) |
|---|---|---|---|
| `v > 5` | **raises** | **raises** | **raises** |
| `int(v) > 5` | valid | **raises** | **raises** |
| `not v or int(v) > 5` | valid | **raises** | valid |
| `not v or (v.isdigit() and int(v) > 5)` | valid | invalid | valid |

| on a `NumberField`, which passes a real number | `6` | `4` | `0` (its empty) |
|---|---|---|---|
| `v > 5` | valid | invalid | invalid |

**So there are two right answers and the demo shows both**: guard the predicate for the type the
field passes (panel 3), or pick the field whose type the predicate already wants (panel 4). ⚠ **The
guard this branch adds is the safety net for doing neither — it is not a substitute for either, and
the demo says so in its own docstring.**

⚠ **An empty `TextField` passes `None`, not `''`** — measured, and it is why `int(v) > 5` is not
enough. ⚠ **An empty `NumberField` passes `0`**, so the right-type pairing never reaches the raise
path at all.

**Both arms, same driver:**

| panel | `main` | branch |
|---|---|---|
| 1 wrong type, `v > 5` on a TextField | `valid=True` for `'6'` **and** `'abcdef'` | `valid=False`, "could not be checked", **1** console line for 7 keystrokes |
| 2 converts, `int(v) > 5` | `'6'` valid; `'abc'` and empty **also** `valid=True` | `'6'` valid; `'abc'` and empty report "could not be checked" |
| 3 guarded predicate | verdict for all four inputs, 0 lines | **byte-identical** |
| 4 `NumberField` + `v > 5` | verdict for both, 0 lines | **byte-identical** |
| 5 manual `validate()` | **raises** `ValueError` | returns `False` |
| stderr across the run | **13 raw tracebacks** | **3 one-line reports** |

⚠ **Panels 3 and 4 reading identically on both arms is the control that makes the rest mean
something** — a predicate that cannot raise is untouched by this branch either way, so the
differences in 1, 2 and 5 are the guard and not the instrument.

⚠ **Two driver traps worth keeping, both of which make a WORKING fix look broken.** The debounce is
50 ms of **wall time**, so pumping `update()` in a tight loop never reaches it; and
`event_generate("<KeyRelease>")` **with no `keysym=`** is not delivered as a key at all, so an
`always` trigger never runs. The first driver hit both and reported three quiet panels against a fix
that works. They are written into its docstring.

---

## Round 2

**Cap 2, spent 1.** Round 2 is triggered — `git diff cc7c6e4c..HEAD -- src/` is non-empty — and its
scope is **the fix diff only**, not the branch: `src/bootstack/validation/validation_rules.py`
(the `_report_func_error` reporter), the five tests added to
`tests/widgets/public/test_custom_rule_exception.py`, and the two documentation lines that now name
the stderr report.

⚠ **Do not re-open the cleared list above.** Decision 1, decision 2, the empty-field consequence and
the breadth of `except Exception` were each settled against a measurement this round, and the probes
that produced them are committed at `development/probe_467_review_round1_real_blur.py` and
`development/probe_467_review_round1_form_manual.py`. Re-run them rather than re-deriving.

**The one thing worth attacking in the new code:** printing to stderr from library code is a
framework-wide first for the widget layer — `grep -rn "sys.stderr" src/bootstack/` returns only the
CLI and the dev reloader. If the maintainer would rather the framework never wrote to a console,
that is a decision to take here, and the alternative is not "back to `debug_log_exception` alone"
(which is what round 1 rejected) but a real diagnostic channel, which is #477-sized work rather than
this branch's.
