# REVIEW — `fix/select-signal-value-458`

**Round cap:** 2 (patch line, declared in `PLAN.md` before implementation).

---

## Round 1 — 2026-08-19

Reviewed `git diff main...HEAD` at `028e7cc0` — seven files, of which **`src/bootstack/widgets/select.py` is the only production change**. The rest are `PLAN.md`, `CHANGELOG.md`, `docs/widgets/select.rst`, one probe, one review brief and one new test file.

Gate 1 was satisfied: `git diff main...HEAD -- src/` is non-empty (one file), so a round was warranted.

The reviewer was handed `PLAN.md` and `development/review-brief-458-select-signal.md` up front, per the harness rule that cost `0.3.1` a round of re-litigation. Nothing already settled in either was re-filed.

**Four findings — none of them in production code.** One is a real test defect and is FIXED; one is a false claim in `PLAN.md` and is CORRECTED; one is out of scope and belongs to #390; one was raised as a fix and then **withdrawn on re-examination**, which is recorded here in full because the reasoning matters more than the outcome.

Two unrelated defects were found while verifying the findings and are filed rather than fixed: **#460** and **#461**. Neither is in this branch's diff.

---

### What the round CONFIRMED as correct — do not re-derive

The production change is sound. Each of these was checked rather than assumed:

- **The seed-suppression window is tight and correct.** `_suppress_changed_event` is set immediately before `_bind_value_signal` and cleared in a `finally`, so an exception during binding cannot leave the widget permanently silent. `_prev_changed_value` is still updated inside the window, so the first real change after construction is not swallowed as a duplicate.
- **The two-way binding terminates.** `SelectBox.value` only emits when `new_value != prev_value`, and an unrealized `Signal.set` dedups on `_last == value`, so the signal to field to signal path cannot cycle.
- **The `textsignal=` guard survives `_split_layout_kwargs`.** That helper only pops layout keys, so `textsignal` is still present in `kwargs` when the guard reads it. Rejecting it breaks no working code: pre-fix it fell into `**kwargs` and was silently discarded, so nothing could have been relying on it.
- **`disabled=True` does not defeat the seed.** `TextEntryPart.value()` writes through the entry's own textsignal rather than `insert`/`delete`, so a disabled entry still takes the seeded value.
- **`Form` is unaffected.** `getattr(field_widget, "signal", None)` was `None` for form-built selects before this branch and still is, because `Form` does not pass `signal=`.
- **Value round-trips hold** for decoupled options, plain `list[str]` options, `int` values and off-list values.

---

### F1 — `tests/widgets/public/test_select_signal_value.py:211` — **low** — FIXED

`test_read_only_is_still_honored_with_a_bound_signal` did not test what its docstring claims.

The docstring states that it pins the interaction between the readonly bracket in `SelectBox.value`'s setter and **a signal-driven write** — "the signal now drives that same setter, so this pins the interaction rather than assuming it". The body constructed the widget and asserted `sel.read_only is True`. It never called `signal.set()`.

Not fully vacuous: construction seeds through the `value` property, so one write did cross the readonly bracket. But the case the docstring names — a *later* write arriving from the signal, which is the new path this branch introduces — was untested, and the test would have passed unchanged if such a write left the entry editable. That is precisely the #453 regression the docstring invokes.

**Resolution.** The test now drives `signal.set(...)`, pumps the loop, and re-asserts both `read_only` and the displayed text. Gate 2's actionable **vacuity** axis; no other change to the file.

**The control was run rather than assumed.** With `main`'s `select.py` swapped in and everything else on the branch, the rewritten test fails **behaviorally**, not with an `AttributeError`:

```
assert sel.read_only is True      <- passes, so the precondition holds
assert _shown(sel) == "Three"
E   AssertionError: assert '3' == 'Three'
```

⚠ **State the scope of what that proves.** It proves the added write now exercises the signal-driven path, which the old body did not reach — the pre-fix field displays the raw value. It does **not** prove `read_only` itself would regress: that assertion holds on both sides. The finding was vacuity with respect to the signal path, and the control matches the finding.

---

### F2 — `PLAN.md:5` — **low** — CORRECTED

`PLAN.md` reads *"Adds no public surface and does not raise where working code used to succeed"*, and that sentence is the stated basis for putting the branch on the patch line. The first half is false.

**Measured.** Inheriting `ValueSignalMixin` gives `Select` a public `signal` property (`_core/field_mixin.py:357`). On `main`, `hasattr(bs.Select(["a","b"]), "signal")` is `False`; on this branch it is `True`. Nothing mechanical catches this — `tests/test_public_surface.py` guards the curated top-level *namespace*, not per-widget attributes.

**But the finding is weaker than it first looks, and the record should say so rather than hand a later round an inflated premise.** `.signal` is not a new concept: nine public wrappers already define the property and three more inherit it from the same mixin, so twelve public widgets have it and `Select` was the gap. The property is also *not* a passthrough of the internal `SelectBox.signal`, which returns the entry's **textsignal** — the text-space object at the heart of this very bug. Publishing the impl's version would have exposed the defect as API; the mixin's returns the caller's own value signal, or `None` when nothing is bound.

**Resolution.** The `PLAN.md` sentence is corrected to state the addition and why it is small. **Whether it changes the release line is a maintainer call and is deliberately left open** — the standing rule is that an addition requires a minor even when nothing breaks, but the counter-argument is that this closes a family gap rather than introducing surface. The second half of the sentence is accurate and unchanged.

⚠ **A consequence worth carrying:** after this branch, `Select.signal` returns `None` when unbound while `SelectButton.signal` returns a live signal, for the same property name and the same annotation. That divergence is pre-existing on the `SelectButton` side and is now filed as **#460** (the annotation) and **#461** (the wiring).

---

### F3 — `tests/widgets/public/test_select_signal_value.py:111` — **low** — RAISED, THEN WITHDRAWN

`test_a_signal_write_fires_change_once` asserts an exact event list — `assert seen == ["2", "3"]` — against an asynchronous `<<Change>>` emitted with `when="tail"`. That is byte-for-byte the shape of `tests/widgets/public/test_select_options.py:272`, already filed as **#449** for flaking roughly 1 run in 10 in the shared-root leg with an unexplained cause. The finding was that the branch plants two more such round-trips in the same leg.

**The proposed fix was to relax the assertion to the sibling's `seen and set(seen) == {...}` form (`test_select_options.py:290`). That recommendation is WITHDRAWN.**

The exact-list form is not incidental here — the "exactly once" half is the guard against the two-way binding feeding its own write back as a second change, which is a regression this branch could plausibly introduce and which the looser form would not catch. The sibling relaxed for a reason that does not apply: `SelectButton`'s `StringVar` legitimately emits more than once per set, whereas `Select` does not. Relaxing would trade real coverage of this branch's own risk against a flake whose cause is still unexplained and which has not been observed in this test.

**Resolution.** No change to the test. The #449 linkage is recorded here so that, if it does flake, the cause is already identified rather than re-derived from scratch — which is the only thing the finding was actually worth.

---

### F4 — `src/bootstack/widgets/select.py:242` — **low** — OUT OF SCOPE, belongs to #390

Setting a signal-bound `Select` to `None` clears the field but leaves the bound `Signal` holding the previous value: the field is blank, `.value` is `None`, and the signal still reports the old option indefinitely.

**Measured, and the mechanism is not in this diff.** `_sync_value_set` returns early on `value is None` (`_core/field_mixin.py:318`) and the queued `_to_signal` handler does the same (`:293`). `field_mixin.py` is untouched by this branch, so every mixin-bound field behaves this way today. Confirmed on `main` with `NumberField`, which has bound through this mixin since `d05ecd8a`:

```
set 7    : field=7    signal=7
set None : field=None signal=7      <- stale
```

For `Select` specifically this is a **directional change**: the old text-space wiring pushed `''` into the signal on clear (control, same probe: `field=None signal=''`). So the branch does alter the behavior — by making `Select` consistent with `NumberField`, `DateField` and `TimeField` rather than by inventing a new gap.

⚠ **The reviewer also claimed the new documentation "states the contract as unconditional in both directions". That was CHECKED and is overstated.** `docs/widgets/select.rst:233` describes seeding the signal with a value and picking an option; it makes no claim about clearing. Nothing false ships.

**Resolution.** No change. This is #390 — *"should signals model emptiness at all"* — which is an open design decision the maintainer is actively evaluating, and any real fix lives in `field_mixin.py` and changes every field that takes a `signal=`. Filing a duplicate would be noise. **Do not re-file this on a later round.**

---

### Gate 1 after the fix step

The fixes applied in this round touch `tests/` and `PLAN.md` only. **`git diff main...HEAD -- src/` is unchanged by the fix step**, so gate 1 does not open a round 2 on their account. The cap of 2 remains unspent.
