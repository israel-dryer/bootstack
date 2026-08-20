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

---

## Off-protocol verification pass — 2026-08-19

**Not a round.** `git diff main...HEAD -- src/` is still `select.py` alone and byte-identical to what round 1 reviewed, so **gate 1 did not open this** and **the cap of 2 remains unspent**. It was a `/code-review` run aimed at `37b871a9` — the test-only fix commit from round 1's F1 — i.e. exactly the shape gate 1 exists to keep out (`0.3.1`'s round 4 reviewed a test-only diff and yielded 3 findings about a probe's readability). It is recorded here because it produced one real finding, and because two of its three findings are re-reports that a later round must not pay for a third time.

**Yield: 1 of 3.** Every claim below was re-measured independently with a control before being accepted or rejected; the probe is `verify_review_458.py` (scratchpad, not committed — it is three arms of six lines each and is reproduced inline below).

### V1 — `tests/widgets/public/test_select_signal_value.py:211` — **low** — REAL, OPEN

**Round 1's F1 fix reaches the signal-driven path but still cannot detect a broken readonly bracket.** The rewritten docstring says asserting only on construction "would pass even if that path left the entry editable" — implying the added `signal.set("3")` closes that gap. It does not.

Neither added assertion is sensitive to the entry's ttk state. `sel.read_only` reads `self._internal.cget("readonly")`, the stored **setting**, which #453 deliberately made independent of the entry's state (the comment at `select.py:326` says so outright); and `_shown(sel) == "Three"` holds whether or not the bracket restored `readonly`.

**Control — patch `SelectBox.value`'s setter to leave the entry `!readonly` after every write, then run the test's exact sequence:**

```
real code : read_only=True  shown='Three'  entry_readonly=True
BROKEN    : read_only=True  shown='Three'  entry_readonly=False
            assertions: read_only is True -> True ; shown == 'Three' -> True
```

Both assertions pass while the field is silently editable.

⚠ **The commit message is honest about this and the docstring is not.** `37b871a9` states the scope correctly — *"It does not prove read_only itself would regress"* — so this is a docstring that overclaims relative to its own commit, not a fix that was misrepresented.

**Resolution — ✅ APPLIED 2026-08-20.** `assert sel._internal.entry_widget.instate(["readonly"])` added after the signal write, and the overclaiming docstring rewritten to say which check is load-bearing and why the other two cannot be. Gate 2's actionable **vacuity** axis.

**The control was re-run against the applied fix rather than carried over from the finding.** Breaking the applier in `selectbox.py` — `self.entry_widget.state(['!readonly'])` unconditionally, replacing the `typeable` bracket — and running the single test:

```
real code : 1 passed
BROKEN    : 1 failed
            >  assert sel._internal.entry_widget.instate(["readonly"])
            E  AssertionError: assert False
```

⚠ **The three assertions ABOVE the new one all passed in the broken arm** — the failure traceback shows `read_only is True`, `_shown(sel) == "Three"` and `read_only is True` all clearing before the new line trips. That is the finding's claim reproduced directly: the old test was blind to a silently editable field. `selectbox.py` was restored from a byte copy and `git status -- src/` is clean, so no part of the control survives in the diff.

**This does NOT open a round.** The change is tests-only plus this record, so `git diff main...HEAD -- src/` is unmoved and gate 1 does not trigger. **Cap 2, spent 1.**

### V2 — clearing leaves the signal stale — **RE-REPORT of F4. Do not re-file.**

Identical to **F4** above, down to the mechanism (`_sync_value_set` early-returns on `None`, `_core/field_mixin.py:318`) and the `NumberField` control proving it is the shared mixin's rule. Re-measured and reproduced (`field=None signal='1'`); the finding is *true* and was never in dispute — it is **closed as #390**, whose fix lives in `field_mixin.py` and moves every `signal=` field.

⚠ **Its escalation was checked and does not hold.** This pass claimed the behavior "contradicts the branch's own CHANGELOG line" (*"the signal now carries the option's value in both directions"*). That sentence continues *"set it and the matching option is selected and announced, pick an option and its value is written back"* — selection propagation in two directions, **silent on clearing**. This is the same overstatement F4 already checked and rejected against `docs/widgets/select.rst:233`, arriving a second time against a different file. Nothing false ships, in either place.

### V3 — `Select` gains a public `signal` property — **RE-REPORT of F2, and now DECIDED.**

Identical to **F2** above. Re-measured (`hasattr(bs.Select, "signal")` is `True` here, `False` on `main`) and true — but it was found in round 1 *and acted on*: the maintainer cut **`0.4.0 — Signal binding on fields`** on 2026-08-19 to carry #458/#459/#460/#461, and `main`'s CLAUDE.md records *"Do not re-litigate this as '#458 was only an addition' — the addition was never the binding constraint"* (#461 breaks working code and is the stronger reason).

⚠ **The framing was stale, not merely redundant.** It read the addition as one that "would ship as an accidental addition rather than a decided one", which was true when round 1 found it and false by the time this pass ran. **The milestone question is settled; do not reopen it.**

**One residual is genuinely live and is NOT part of the settled question:** now that the addition is deliberate and ships in a minor, the #458 CHANGELOG bullet still does not mention that `Select` gained a public `signal` property. Deciding whether to announce it is the maintainer's call, not a defect.

### ⚠ The harness failure, which cost two of the three findings

**The reviewer was not pointed at `REVIEW.md`, and it was reading against a `main` that had moved.** Round 1's record was sitting on the branch — F4 and F2 are written up in it *specifically* so a later round would not re-file them, and the round 1 handoff says so in as many words. Meanwhile `main` had advanced two `docs(claude):` commits carrying the `0.4.0` decision, so the branch's own copy of `CLAUDE.md` is behind and does not contain it.

This is `0.3.1` round 3 repeating verbatim: three of its four findings were already-triaged items because its reviewer was handed no triage state, while round 2's reviewer was handed `REVIEW.md` and re-filed nothing. **Hand the reviewer `REVIEW.md` AND check whether `main` has moved under the branch.** Applying this file's own test — *did the evidence change, or the cost of acting?* — for V2 and V3 **neither** changed.
