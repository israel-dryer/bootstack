# REVIEW — #467

Two rounds, both recorded here. Round 1 reviewed the branch at `8b8e0964`; round 2 reviewed
round 1's fix diff at `d010214f`. **Cap 2, spent 2.**

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

Reviewed at `d010214f`. Scope: `git diff 8b8e0964..HEAD` — **the fix diff only**, per the protocol's
"every later round reviews only the fix diff". Gate 1: `git diff 8b8e0964..HEAD -- src/` is
non-empty (`validation_rules.py`, +85/-7), so the round is triggered.
**Cap 2, spent 2. This is the last round — surviving findings are filed as issues, not fixed.**

Environment: macOS box, `.venv/bin/python` 3.14.0, `matplotlib` 3.11.0 present, `pandas` ABSENT.

The control arm for this round is the branch's own pre-fix commit **`8b8e0964`**, not `main` —
round 1's fix step is what is under review. Run from a `git worktree` with `PYTHONPATH` set and
provenance printed; the branch was not touched while the review ran.

**Instrument: `development/probe_467_review_round2.py`**, four arms, each with the control that
makes it mean something. It prints its provenance and which arm it is on by reading
`validation_rules.py`.

**Round 1's four committed instruments were re-run rather than re-derived, and all four reproduce
the record** — `probe_467_review_round1_real_blur.py` (arm 3 still valid, so arm 1's `False` is the
rule deciding), `..._form_manual.py`, `..._formdialog_press.py`, and the demo through
`probe_467_demo_driver.py` (panels 3 and 4 byte-identical, 3 console lines total). The demo was
driven before the round was called clean, per round 1's own lesson.

---

### R1 — BLOCKING. A non-`str` `message` turns the guard's own return into a raise, re-opening #467 on a path this branch had already fixed.

`src/bootstack/validation/validation_rules.py:214-216` (`_uncheckable_message`)

`_uncheckable_message()` calls `self.message.rstrip('.')`. `message` is author-supplied and
validated nowhere — `ValidationRule.__init__` stores whatever it is given — and the composer runs
**inside the `except` block, outside the `try` that `_report_func_error` carries**. A truthy
non-`str` message therefore raises *during handling of* the func's exception, straight out of the
guard.

**Measured, both arms, same probe (arm 1):**

| `message=` | `8b8e0964` (pre-fix) | `d010214f` (post-fix) |
|---|---|---|
| `None`, `''` | `False`, `'Invalid value.'` | `False`, `'Could not check this value.'` |
| `'must exceed 5'` | `False`, `'must exceed 5'` | `False`, `'Could not check this value (expected: must exceed 5).'` |
| **`42`** | `False`, `42` | ***** ESCAPED THE GUARD *** `AttributeError: 'int' object has no attribute 'rstrip'`** |
| **`b'nope'`** | `False`, `b'nope'` | ***** ESCAPED *** `TypeError: a bytes-like object is required, not 'str'`** |
| **`['a']`** | `False`, `['a']` | ***** ESCAPED *** `AttributeError: 'list' object has no attribute 'rstrip'`** |

⚠ **The control is what makes this the composer and not the result object.** The same three
messages on a *genuine verdict* — the func returns `False` rather than raising — pass through
untouched and **identically on both arms** (`message=42`, `message=b'nope'`). Only the raise path
moved, and only in the direction of raising.

**Root cause.** Round 1's F2 fix wrapped `_report_func_error` precisely so that no diagnostic could
become the failure it reports. The message composer was added in the **same commit**, is called from
**the same statement**, is equally made of user-supplied material — and was left unwrapped. The
falsy cases are safe by accident: `not self.message` short-circuits `None`, `''`, `0`, `[]` and
`False` to `UNCHECKABLE_MESSAGE` before any string method runs, so only a *truthy* non-`str`
reaches it.

⚠ **This is a regression against the branch's own pre-fix commit, not against `main`.** On `main`
there is no guard at all, so `message=42` plus a raising func was already #467. At `8b8e0964` the
branch had fixed it. `d010214f` un-fixed it. That is why it is blocking and not a note: the fix step
put a hole back in the one contract the branch exists to establish — nothing escapes.

**Suggested minimal change.** Make the composer total, with the guarantee `_report_func_error`
already makes: wrap its body and fall back to `UNCHECKABLE_MESSAGE`. Coerce with `str()` rather than
requiring one, so an author's `message=42` still reaches the user as *"(expected: 42)"* — that is
what the pre-fix arm did with it. `str()` is itself user code for a custom object, and `__bool__`
runs before it, so the guard must cover the whole body rather than the `rstrip` alone.

### R2 — should-fix (gate 2: FALSE ALARM). One new test fails when the author does what the new message tells them to do.

`tests/widgets/public/test_custom_rule_exception.py:150-162`
(`test_the_report_does_not_repeat_for_the_same_rule`)

The test asserts `capsys.readouterr().err == ""` after the second and third raise. But
`debug_log_exception` runs on **every** occurrence, and `traceback.print_exc()` writes to **stderr**
— so with `BOOTSTACK_DEBUG=1` set the channel is not empty and the test fails, while the one-shot
latch it is named for is working perfectly.

**Measured (arm 2), the whole file, both arms:**

| | `8b8e0964` | `d010214f` |
|---|---|---|
| `BOOTSTACK_DEBUG` unset | 14 passed | 22 passed |
| **`BOOTSTACK_DEBUG=1`** | **14 passed** | **1 failed, 21 passed** |

This is a false alarm under gate 2 — the test fails while the behavior is fine — and the trigger is
not exotic: **the stderr line this branch adds says "Set BOOTSTACK_DEBUG=1 for the traceback."** An
author who follows that advice and then runs the suite gets a red test that has nothing to do with
what they changed. CI does not set the variable, so it will not fail there; it will fail on the desk
of the one person who was already debugging.

**Suggested minimal change:** assert on the report itself rather than on total silence — count the
`"bootstack: a 'custom' validation rule's func raised"` lines and require exactly one — so the test
measures the latch and not the debug channel.

### R3 — should-fix. One `try` covers both diagnostics, so a broken stderr silences the traceback that was explicitly asked for.

`validation_rules.py:238-255` (`_report_func_error`)

The one-line stderr report and `debug_log_exception` sit in the same `try`. The report goes first,
so if `sys.stderr.write` raises, control leaves the block and **`debug_log_exception` never runs** —
the opt-in full traceback is suppressed by the failure of the always-on one-liner. The latch is set
*before* the print, so the rule is then permanently silent on both channels.

**Measured (arm 3), `BOOTSTACK_DEBUG=1`, a `sys.stderr` whose `write()` raises** — a console
redirected into a widget that has since been destroyed, which is an ordinary thing for a desktop app
to do:

| | `8b8e0964` | `d010214f` |
|---|---|---|
| debug context line on the **working** stream (stdout) | `"bootstack DEBUG: custom validation rule raised for value '6'"` | **`''`** |
| control, same run with a working stderr | same line | same line |

The guard itself holds on both arms — nothing escapes, which is F2's guarantee doing its job. What
is lost is the diagnostic, on a stream that was never broken.

**Suggested minimal change:** two `try` blocks rather than one, so each diagnostic fails alone.

### R4 — nit (docs). `UNCHECKABLE_MESSAGE` is named in a public docstring and cannot be imported.

`validation_rules.py:120` — `ValidationRule.validate()`'s `Returns:` block ends *"A rule with no
`message` reports `UNCHECKABLE_MESSAGE`."* `ValidationRule` is autodoc'd
(`docs/reference/validation.rst:340`), so that sentence is rendered API reference. Measured:

```
from bootstack.validation import UNCHECKABLE_MESSAGE
ImportError: cannot import name 'UNCHECKABLE_MESSAGE' from 'bootstack.validation'
__all__ = ['ValidationRule', 'ValidationResult', 'RuleType']
```

Either export it or quote the sentence it produces. **Not fixed** — adding a name to a public
`__all__` is public surface, which is a maintainer call, and quoting the literal is a wording change
to shipped prose.

### R5 — nit. `rstrip('.')` strips a character SET, and a trailing space defeats it.

`validation_rules.py:216`. Shapes the two punctuation tests do not cover, all measured:

| `message=` | composed |
|---|---|
| `'must be over 5. '` (trailing space) | `'... (expected: must be over 5. ).'` — the stop it was meant to remove survives |
| `'must be over 5...'` | `'... (expected: must be over 5).'` — all three stripped |
| `'Enter at least 5 in.'` | `'... (expected: Enter at least 5 in).'` — an abbreviation loses its period |
| `'...'` | `'... (expected: ).'` |
| `'Value must be >= 5…'` (ellipsis char) | unchanged, correctly |

Cosmetic in every case, and the common ones are right. Recorded, not fixed.

### R6 — note. `sys.stderr` can be `None`, and `print(file=None)` falls back to stdout.

Measured: with `sys.stderr = None` — `pythonw.exe`, a windowed `.app` bundle, a `--noconsole`
PyInstaller build, all of which are how a **desktop UI framework** is shipped — `print(..., file=sys.stderr)`
does not raise; Python resolves `file=None` to `sys.stdout` and the report lands **there** instead.
With both streams `None` it goes nowhere, silently. The guard holds in every case.

Not a defect: the author-facing report is aimed at development, where a terminal exists. Recorded
because it bounds the claim — the new channel is not reliably present in the mode this framework's
apps ship in.

### R7 — note. The stderr decision is UPHELD, and the record's justification for it is wrong in a way worth correcting.

REVIEW.md round 1 flags this as the decision most worth overturning, on the grounds that
*"printing to stderr from library code is a framework-wide first for the widget layer —
`grep -rn "sys.stderr" src/bootstack/` returns only the CLI and the dev reloader."*

**Both halves of that are off.** Re-measured:

- `grep -rn "sys\.stderr" src/bootstack/` returns **`dev/_reloader.py` only** (three hits) plus this
  new line. The CLI does not use `sys.stderr` at all — it uses bare `print()`, i.e. **stdout**.
- More to the point, **the framework already has a default-visible author channel and uses it in the
  widget layer**: `warnings.warn`, at `style/fonts.py:59,66,105`, `_runtime/toplevel.py:158,178` and
  `data/_observable.py:235`. So this is a first in *channel*, not in principle. The framework does
  talk to the author by default; it has just been doing it through `warnings`.

**And `warnings` cannot be used here — measured, arm 4.** Under `-W error` a `warnings.warn` becomes
an exception. Unwrapped, it escapes the guard and re-opens #467 on the automatic trigger. Wrapped in
the `try` the code already has, it is *swallowed* — silent for exactly the developer running strict
warnings. This site runs inside a Tk dispatch (the debounced `after`), which is the case
`_runtime/utility.py:353` and `_runtime/events.py:379` already document as the reason this project
does not warn from those paths. The shipped `print` is unaffected by `-W error`.

So the decision stands on evidence rather than on being the last option left, and the alternative
remains what round 1 said it was: a real diagnostic channel, which is #477-sized work.
**Do not re-open this.**

### R8 — nit (docs). The CHANGELOG and the narrative page quote the message without its final period.

Both write *"Could not check this value (expected: must be over 5)"*; the string is
`Could not check this value (expected: must be over 5).` A reader searching for the exact text they
saw on screen does not match it. Recorded, not fixed — shipped prose, one character.

---

### Cleared this round, with the measurement

- **The composition reads `self.message` and not the resolved `msg`, and that is correct.** Verified
  the divergence is exactly the falsy set: `msg` falls back to `_default_message()` → *"Invalid
  value."* for `custom`, and composing that would give *"(expected: Invalid value.)"*. Every falsy
  message — `None`, `''`, `0`, `[]`, `False` — takes the `UNCHECKABLE_MESSAGE` branch. Measured, not
  reasoned.
- **The new user-facing string is hardcoded English, and that is consistent, not a gap.**
  `grep -rn "translate\|MessageCatalog" src/bootstack/validation/` returns nothing;
  `_default_message()` hardcodes all nine of its messages. A localized composer here would be the
  only translated string in the module.
- **The F2 wrap does not swallow anything else it should not.** The exception's `__str__` and the
  value's `__repr__` are the two pieces of user code inside it and both are meant to be absorbed;
  `debug_log_exception` never raises by contract (`_runtime/utility.py:376-383`). **R3 is the one
  thing it swallows wrongly, and that is about the two diagnostics sharing one block, not about the
  wrap existing.**
- **The one-shot latch is per rule instance and every rule instance is per `add_validation_rule`
  call.** `grep -rn "ValidationRule(" src/` returns three construction sites
  (`validation_mixin.py:88`, `textarea.py:310`, `codeeditor.py:496`), all appending to a `_rules`
  list at attach time. Nothing rebuilds a rule per validation, so the latch cannot be defeated by
  reconstruction and cannot be shared across widgets.
- **The new tests are discriminating where round 1 claims they are.**
  `test_a_raise_and_a_verdict_do_not_look_the_same` compares a raise against a real verdict
  (`validate(4)` on `lambda v: v > 5` returns `False` without raising), and the two `Hostile` repr
  tests fail by *raising*, not by asserting. Round 1's pre-fix control (3 failed / 16 passed) was not
  re-run; its claim is not load-bearing for anything found here.
- **Suite on the branch: `1698 passed / 33 skipped`, 33 legs, exit 0** — re-measured at `d010214f`,
  matching round 1's figure exactly, which is what it should be for a round that changed nothing.

---

### Fix step — blockers only

Re-ranked before touching code: **R1 blocking; R2, R3, R4 should-fix; R5, R8 nits; R6, R7 notes.**
**Only R1 is fixed.** R2 and R3 are real and both were introduced by round 1's fix step, but the cap
is spent and the rule for a closing round is that survivors are filed, not fixed — and neither
reaches a user: R2 fails only a developer's own run with `BOOTSTACK_DEBUG=1`, R3 costs a diagnostic
only when the stream it would print to is already broken.

#### R1 — FIXED. `src/bootstack/validation/validation_rules.py`

**Root cause, stated before editing:** `_uncheckable_message` composes an author-supplied,
unvalidated `message` by calling `str` methods on it, and it is called from inside the `except`
block that absorbs the func's exception. Anything the composition raises therefore escapes the
guard. The falsy short-circuit made this invisible for the empty case, which is the case the tests
cover.

**Change:** the composer's whole body is wrapped, falling back to `UNCHECKABLE_MESSAGE` if any part
of it raises, and `self.message` is coerced with `str()` rather than required to be one — so
`message=42` reaches the user as *"(expected: 42)"*, which is what the pre-fix arm did with it. The
wrap covers the truth test as well as the coercion, because `__bool__` is user code too and runs
first.

**Measured after the fix** (`probe_467_review_round2.py`, arm 1):

```
arm 1  a non-str `message`, on the RAISE path
    None           -> is_valid=False message='Could not check this value.'
    '' (empty)     -> is_valid=False message='Could not check this value.'
    str            -> is_valid=False message='Could not check this value (expected: must exceed 5).'
    int 42         -> is_valid=False message='Could not check this value (expected: 42).'
    bytes          -> is_valid=False message="Could not check this value (expected: b'nope')."
    list           -> is_valid=False message="Could not check this value (expected: ['a'])."
```

Nothing escapes, and the control — the same three messages on a genuine verdict — is byte-identical
to what it was before the fix, so the change reached the composer and nothing else.

**Regression test added**, `test_a_message_that_is_not_a_string_does_not_escape_the_guard`: the
three non-`str` messages plus a `__str__` that raises, each asserting the guard holds, plus the
two message shapes (`42` coerces and is shown; the unrenderable one falls back). 22 → 23 tests.

⚠ **The first draft of that test also asserted a `message` whose `__bool__` raises, and it FAILED —
against the fix. That is a different, pre-existing defect and it was cut from the test rather than
fixed.** `validate()` opens with `msg = self.message or self._default_message()`
(`validation_rules.py:124`), so `__bool__` runs before the func is ever called. Measured on both
arms and on **every rule type, including one whose func does not raise at all**:

```
ARM: PRE-FIX 8b8e0964        ARM: POST-R1-FIX (branch)
  custom-raising  -> RAISED    custom-raising  -> RAISED
  custom-passing  -> RAISED    custom-passing  -> RAISED
  email-plain     -> RAISED    email-plain     -> RAISED
```

Identical on both arms and unreachable from the composer, so it is **not** R1 and not this branch's.
Contrived enough (an author whose `message` object refuses to be truth-tested) that it is recorded
here rather than filed. ⚠ **It is worth the note for the method it demonstrates: the assertion that
failed was the one testing a case the finding had not measured.**

**Control against the pre-R1 source**, restored with `git show d010214f:src/.../validation_rules.py`
into a copied tree with `PYTHONPATH` set and provenance printed: **1 failed, 22 passed** — only the
new test fails, and it fails behaviorally, `AttributeError: 'int' object has no attribute 'rstrip'`
raised *during handling of* the func's `TypeError`, which is R1 exactly.

#### R2, R3, R4, R5, R6, R7, R8 — NOT FIXED

Per "fix blockers only" and the closing-round rule. **Filed as issues** — see below.

### Verification — round 2

All on the macOS box, `.venv/bin/python` 3.14.0, at the post-fix working tree, `matplotlib` 3.11.0
present, `pandas` ABSENT.

- **`import bootstack` succeeds** — run before the suite, not after.
- **Suite: `1699 passed / 33 skipped`, 33 legs, exit 0, no failures.** That is `1698 + 1`, the one
  new test, bounded the usual way rather than by looking plausible: `git diff main --stat -- tests/`
  names **one** file, and its `--collect-only` says **23** (was 22). The pre-fix run in this same
  session measured `1698 / 33` at `d010214f`, which is round 1's figure unchanged — the round-2
  review itself moved nothing.
- **Pre-R1 control: `1 failed, 22 passed`**, against `d010214f`'s `validation_rules.py` restored
  into a copied tree with `PYTHONPATH` set and provenance printed. Only the new test fails, and it
  fails behaviorally.
- **Docs clean-build: `build succeeded`, exit 0** with `-W --keep-going` after `rm -rf docs/_build`.
- **`git diff main...HEAD -- CLAUDE.md` is empty.**
- **All four of round 1's instruments re-run and reproduce the record**, plus the demo through its
  driver — panels 3 and 4 byte-identical on both arms, 3 console lines for the whole run.
- ⚠ **`test_capture.py` passed 23/23 in both full runs**, so the display was active and unlocked and
  the documented macOS symptom did not apply this session.

---

### Filed as issues — all five, 2026-08-29, all UNMILESTONED

Milestoning is a scope call and is left to the maintainer. #496 argues its own case for
`0.5.0 — Strictness and value types` (its fix raises where the framework accepts) but was not
assigned there.

| # | what | origin |
|---|---|---|
| [#495](https://github.com/israel-dryer/bootstack/issues/495) | `range` reports its own message for a pair it could not compare | round 1, F10's residue |
| [#496](https://github.com/israel-dryer/bootstack/issues/496) | a non-callable `func` is absorbed rather than refused | round 1, F3 |
| [#497](https://github.com/israel-dryer/bootstack/issues/497) | `'compare'` invokes user code unguarded | round 1, F7 |
| [#498](https://github.com/israel-dryer/bootstack/issues/498) | a broken stderr silences the `BOOTSTACK_DEBUG` traceback | round 2, R3 |
| [#499](https://github.com/israel-dryer/bootstack/issues/499) | a test asserts total stderr silence and fails under `BOOTSTACK_DEBUG=1` | round 2, R2 |

### ⚠ SUPERSEDED SAME DAY BY MAINTAINER TRIAGE (2026-08-29) — read this, not the table

The maintainer asked the question the batch should have been filed against:
***are these contrived cases of the framework being used incorrectly, or are we adding guards
around improper use?*** It splits the five cleanly, and filing them as one batch had flattened the
distinction:

| | guarding misuse? | disposition |
|---|---|---|
| #496 non-callable `func` | **yes**, purely | **CLOSED**, folded into **#500** |
| #495 `range` message | **no** — changes nothing about what is accepted | **CLOSED**, folded into **#500** |
| #497 `'compare'` unguarded | **no** — a `Signal` as `other_field` is documented correct usage | **OPEN**, unmilestoned |
| #498 shared `try` | no — diagnostic plumbing | **CLOSED, not planned** |
| #499 test false alarm | no — a test that fails while the behavior is fine | **OPEN**, unmilestoned |

⚠⚠ **#495 AND #496 WERE ONE DECISION, NOT TWO, AND FILING THEM SEPARATELY IMPLIED TWO FIXES.**
Both are the same cause — `ValidationRule` stores whatever configuration it is handed and only
discovers the problem at validation time, where it cannot report it to the person who caused it.
**Refiled as [#500](https://github.com/israel-dryer/bootstack/issues/500) on
`0.5.0 — Strictness and value types`**, because the fix raises where the framework currently
accepts, which is that milestone's membership rule. Refusing the bad configuration at construction
makes #495's message question *unreachable* for that producer rather than merely better-worded.

⚠ **#500 does NOT subsume all of #495, and it says so in its own body.** A `Select` declares
`_VALIDATION_KIND = None` by #465's decision, so a `'range'` rule over one receives whatever the
chosen option carries — measured, bounds correct: `option value='n/a'` reports
*"Enter a value between 1 and 10."* **A construction-time bound check cannot reach that**, because
the value is data rather than author configuration. The residue is carried into #500 as a question
to answer **with** it, not after it.

⚠ **The realistic producer for #495 is NOT the `min="1"` typo the issue led with.** It is a date
bound written the way dates usually get written — `min="2020-01-01"` where the docs show
`min=datetime.date.today()`. Measured: every date fails, and **the broken rule's message is
character-for-character identical to the working rule's**, because `_default_message()`
interpolates the bound unquoted. There is no tell, and `range`'s `except TypeError` writes nothing
to any channel.

⚠ **#498 was closed as not worth the change**: the cost is a diagnostic that goes missing only when
the stream it would have printed to is already broken, and the guard itself holds on every arm
measured. **The measurement is kept here (R3) and in `probe_467_review_round2.py` arm 3** in case a
real report ever lands on it.

⚠ **#495's substance is not dismissed by this triage and the record should not be read that way.**
It is F10's argument, which the maintainer accepted for `'custom'` two days earlier — and #467's own
code comment now points at `range` as the precedent for behavior the two branches no longer share.
**The inconsistency between them is worse than either answer**, which is why it travels with #500
rather than being closed on its own.

⚠ **#499 was both introduced by round 1's fix step**, like R1 which was fixed. The issue bodies
carry the measurements so neither has to be re-derived.

The original list, kept for what each says:

1. **`range` reports its own message for an incomparable pair** (round 1, F10's residue) — it can
   assert a condition of a value it never compared, the defect this branch fixed for `custom`. The
   family's answer belongs in one place.
2. **A non-callable `func` is absorbed rather than refused** (round 1, F3). A `callable()` check at
   construction **raises where the framework currently accepts** — `0.5.0`'s membership rule.
3. **`'compare'` invokes user code unguarded** (round 1, F7) — `_read_other` calls `other_field`
   when it is a `Signal` or a callable, both documented public surface, and a raise there reproduces
   #467 one rule over.
4. **The `custom` guard's two diagnostics share one `try`** (R3) — a broken stderr suppresses the
   `BOOTSTACK_DEBUG` traceback as well, and the latch is already set, so the rule goes permanently
   silent on both channels.
5. **`test_the_report_does_not_repeat_for_the_same_rule` fails under `BOOTSTACK_DEBUG=1`** (R2) —
   it asserts total stderr silence where `debug_log_exception`'s traceback legitimately lands.

**Maintainer calls, not issues:** F9 (the CHANGELOG frames the manual path as the author's own call
site, which the `FormDialog` measurement shows is incomplete), R4 (export `UNCHECKABLE_MESSAGE` or
re-quote the docstring), and R8.
