# REVIEW — `fix/select-read-only-453`

**Round cap:** 2 (patch line, declared in `PLAN.md`).

---

## Round 1 — 2026-08-13

Reviewed `git diff main...HEAD` at `545e98f4`. Three findings: one blocking,
two nits. The fix step follows each finding under **Resolution**.

Suite at review time: `py -3.12 tests/run_gui.py` exit 0, 33 legs, shared leg
1023 passed / 14 skipped. Branch collection is main + 12 exactly, so no tests
were silently dropped.

---

### F1 — `_impl/composites/selectbox.py:1087` — **blocking**

`TimeField.read_only` is permanently dead on this branch.

**Root cause.** `TimeField.read_only`'s setter wrote
`configure(state="readonly")` onto its internal, which is a `TimeEntry` —
a `SelectBox` always constructed `allow_custom_values=True, enable_search=True`.
The branch makes the entry's ttk `readonly` state an OUTPUT of
`_apply_interaction_state()` rather than storage, and the new `_delegate_state`
override re-derives it after every state write. Nothing maps an incoming ttk
`readonly` onto `self._readonly`, so `_entry_is_typeable()` was still `True` and
the applier wrote `['!readonly']` straight back over the request, inside the
same call.

Measured on `main` and on the branch:

```
main    : t.read_only = True -> True   entry state ('readonly',)
branch  : t.read_only = True -> False  entry state ()
```

So a `TimeField` an app locks stayed freely typeable. Not covered by any test —
the suite was green on both refs.

**Resolution — fixed in `timefield.py`, not in `selectbox.py`.** The setter
routes through the `readonly` option instead:

```python
self._internal.configure(readonly=bool(v))
```

Mapping an incoming `state="readonly"` onto `self._readonly` was considered and
rejected: `_delegate_readonly`'s own docstring draws the distinction that a
plain select is already untypeable while its list still opens, so that mapping
would suppress the popup for every select that asked only for "no typing".

`TimeField` is the only member of the field family whose internal is a
`SelectBox` (`datefield`, `pathfield`, `spinnerfield`, `passwordfield`,
`numberfield` and `textfield` all wrap plain entries), so nothing else moved.
Side benefit, now pinned by a test: `read_only = False` no longer clears
`disabled` as a side effect of sending `state="normal"`.

Regression tests: `test_timefield_read_only_is_not_discarded`,
`test_timefield_read_only_closes_the_list`,
`test_timefield_read_only_survives_a_disabled_round_trip` — all three fail
behaviorally against the unfixed source (`assert False is True`,
`assert True is False`). `test_timefield_clearing_read_only_restores_typing`
passes pre-fix as well, because both writes were no-ops there; it pins the end
state, not the transition, and says so in the test.

---

### F2 — `_impl/composites/selectbox.py:113` — **nit**

`self._show_dropdown_button` was stored and never read, and the invariant the
comment states was not the one the code enforced.

**Root cause.** The only consumer of the setting is the construction-time check,
which reads the local parameter, not the attribute. Meanwhile
`_apply_interaction_state()` had an arm that *added* the dropdown addon whenever
a runtime change made the entry typeable, and no arm that ever removed one. So
`show_dropdown_button=False` followed by `configure(allow_custom_values=True)`
inserted a button the caller had explicitly refused, permanently.

**Resolution — maintainer's call (2026-08-13): the option is build-time, and the
button must not be added back when it was not requested.** Un-building a button
makes no sense, so the removal arm was not written either. Dropped the runtime
insert arm from `_apply_interaction_state()`, deleted the dead attribute, and
deleted `_has_dropdown_button()`, which had no other caller. Membership is now
decided exactly once, in `__init__`, which is also what `main` does.

The construction-time exception stays: a typeable entry gets a button even when
`show_dropdown_button=False`, because a click there has to place a text cursor
rather than open the list, so the button is the only entrance left. That
exception is bought where the caller can still see the trade.

**Known consequence, accepted.** A box built `readonly=True,
allow_custom_values=True, show_dropdown_button=False` has no button (correct —
it is not typeable at build), and clearing `readonly` later leaves it typeable
with no entrance to the list. There is no keyboard entrance either: the
`<Down>`/`<Up>`/`<Return>` bindings are created inside the popup-open routine
and torn down on close. This is `main`'s behavior today, so removing the arm
restores it rather than regressing it.

Regression test: `test_a_runtime_flip_does_not_build_a_button_that_was_refused`,
which fails against the unfixed source with the button present. It is the
deliberate mirror of the existing
`test_search_forces_the_dropdown_button_like_custom_values_does`, and together
they pin the build-time / runtime boundary from both sides.

---

### F3 — `select.py:295` — **nit**

`read_only`'s getter used `configure("readonly")` where every sibling property on
the class uses `cget`.

**Root cause.** `ConfigureDelegationMixin.configure` answers a query with the
Tkinter 5-tuple `(name, dbName, dbClass, None, value)`, and `bool(<5-tuple>)` is
unconditionally `True`. The property worked only because `SelectBox` resolves
`TTKWrapperBase.configure`, which returns the bare delegate value.

**Verified latent, not live** — measured `configure("readonly")` returning
`True`, a bare bool, on the built widget. So this was a fragility, not an active
bug: an MRO change that put the delegating mixin in front would have restored
exactly the always-`True` behavior #453 was filed to remove, undetectably at
write time.

**Resolution.** Switched to `bool(self._internal.cget("readonly"))` — the
spelling `options`, `group_by` and `max_visible_items` already use, and one with
no such failure mode. Added the reason to the property docstring so it is not
"simplified" back later.

---

### Verification

`development/` probe not added — the fix is pinned by the four tests above plus
the existing 13 in `tests/widgets/public/test_select_read_only.py`. The control
was run the required way: `src/` reverted, the new tests run against the
unfixed source, 4 of 5 failing behaviorally with the symptoms quoted above.

---

## Round 2 — 2026-08-13 — **the cap; the branch closes here**

Reviewed `git diff main...HEAD` at `6d3c7f56`, the reviewer handed round 1's
record per the standing rule. Four findings: one medium, three low. Three fixed,
one filed. A fifth defect was found during the fix step and is recorded below
with the rest.

`PLAN.md` declares a cap of **2**, so this is the last round. The fixes below
touch `src/`, which gate 1 would otherwise read as a trigger — the cap is what
stops it, and the survivor is filed rather than reviewed.

---

### F1 — `timefield.py:117` — **medium**

`TimeField(read_only=True)` was discarded at construction.

**Root cause.** Round 1's F1 fixed the `read_only` **setter** and left the
constructor sending `internal_kwargs["state"] = "readonly"` — the same write,
through the same doomed path, one scope up. A `TimeEntry` is always built
`allow_custom_values=True, enable_search=True`, so `_apply_interaction_state()`
at the end of `SelectBox.__init__` recomputes `typeable=True` and writes
`['!readonly']` over it before `__init__` returns. No test constructed a
read-only `TimeField`; all four of round 1's use the setter, which is exactly
why round 1's own fix looked complete.

**Resolution.** `internal_kwargs["readonly"] = read_only`, mirroring
`select.py:125`. The `elif` went with it: `disabled` no longer shadows
`read_only`, so both are set and clearing `disabled` cannot hand back an
unlocked field.

Control, five arms in one process, committed at
`development/probe_453_timefield_read_only_ctor.py`:

```
pre-fix   arm 1  read_only=False  typeable=True   popup=True   states=()
post-fix  arm 1  read_only=True   typeable=False  popup=False  states=('readonly',)
```

Arms 2–4 (the setter, a plain field, `disabled` alone) read identically either
way, so arm 1's difference is behavioral rather than a broken harness.

Regression tests: `test_timefield_read_only_at_construction_is_not_discarded`,
`test_timefield_disabled_and_read_only_together_at_construction`, plus
`test_timefield_construction_defaults_to_typeable` as the control that lets the
first one's assertions come out the other way. Pre-fix: 2 failed, 18 passed.

---

### F2 — `timefield.py:166` — **low**

The `read_only` getter read the derived ttk state while its setter wrote the
flag — the getter shape #453 was filed for, on the property the same diff had
just fixed at the other end.

**Verified reachable, but only through the escape hatch.** The value setter
clears and restores the ttk `readonly` state around a write, and anything
observing inside that window sees the wrong answer:

```
during timefield var trace   read_only=False    <- derived read
during select var trace      read_only=True     <- reads the flag
```

Through documented public surface — a time-typed `Signal` subscriber,
`on_change` — it never diverges: 5 of 5 observations `True`. So this was a
latent wrong answer, not a live user bug. Recorded that way rather than as the
stronger claim.

**Resolution.** `bool(self._internal.cget("readonly"))`, matching `Select`. The
correctness argument for a one-line change: today the derived read agrees only
because a `TimeEntry` is `allow_custom_values=True` forever, so
`typeable == not _readonly` by coincidence of two constants.

Regression test:
`test_timefield_read_only_reports_the_setting_not_the_derived_state`. It drives
a textvariable trace, which fires synchronously inside the write, so the test
reproduces the mechanism deterministically rather than racing a symptom.
Pre-fix: `AssertionError: read_only answered [False] during a value write`.

---

### F3 — `_impl/composites/selectbox.py:210` — **low** — FILED, NOT FIXED

`Field.enable()`, `disable()` and `readonly()` write the ttk `readonly` state
directly and none re-derives, against `_apply_interaction_state`'s own
docstring: *"the ttk `readonly` state is an OUTPUT of this method, never
storage."*

Measured on `bs.Select(["A","B"], read_only=True)` followed by
`_internal.enable()`: entry states `('readonly',)` → `()`, so the entry becomes
freely typeable while `read_only` still reports `True` and the re-lit arrow is
inert (`_popup_allowed()` is `False`).

**Not fixed, deliberately.** Widened the reviewer's grep from `src/` to `src`,
`tests` and `development`: **zero callers anywhere in the repo**. The public
`disabled` setter routes through `configure(state=)` → `_delegate_state`, which
already re-derives. So closing it means writing three overrides against a hole
nothing reaches, on the branch whose point is that the invariant now lives in
one place.

Filed together with `PLAN.md`'s out-of-scope item *"`Field.readonly()` never
clears the readonly state"* — same three methods, same file, one issue.

---

### F4 — `select.py:287` — **low**

The public `read_only` docstring carried `#453`, `cget` vs `configure`, and
"the delegating form of `configure` answers a query with a 5-tuple" into the
rendered API Reference.

**This reverses a round 1 decision, on the maintainer's instruction
(2026-08-13).** F3 of round 1 resolved with *"added the reason to the property
docstring so it is not 'simplified' back later"* — correct instinct, wrong
surface. `Select` is autodoc'd `:members:`, so it shipped Tkinter vocabulary to
users on a page describing a framework that exists to hide it.

**Resolution.** Docstring reduced to what the property means; the maintenance
warning moved verbatim into a `#` comment above the `return`, where it still
guards against the "simplification" round 1 was protecting. Verified in the
rebuilt site rather than assumed: `grep -rlE "cget|instate|5-tuple|textvariable"
docs/_build/html --include=*.html` returns nothing.

---

### F5 — `timefield.py:55` — **found during the fix step, not by the reviewer**

`TimeField`'s constructor doc for `read_only` read *"free-text entry is blocked;
user must pick from the dropdown."* That is the pre-#453 misunderstanding
written down as documentation, and F1 made it actively false — the dropdown is
precisely what read-only now closes. It renders on the public page, so a user
would have been told the opposite of what the widget does.

Rewritten to match `select.py:62`'s, in `TimeField`'s vocabulary (clock button,
time list), and checked in the rebuilt HTML.

Worth carrying: F4 and F5 are the same defect class — a docstring that outlived
its code — but F4 leaked *toolkit detail* while F5 leaked *stale behavior*. The
second is the more expensive kind, because nothing about it looks wrong to a
reader.

---

### Verification

Full `py -3.12 tests/run_gui.py` at the fixed head: **exit 0, all 20 legs**,
summed **1229 passed / 21 skipped**. Shared leg **1032 passed / 14 skipped
against 1045 selected**, which reconciles the documented way — `1032 + 13`
runtime skips = 1045, the 14th being the collection-time skip that is summarized
but never selected.

Count reconciliation against `main`, run because this file has been wrong about
counts seven times: `main` selects **1024**, the branch selected **1041** before
this round (main + 17), and **1045** after — exactly the four tests added here.
Nothing was silently dropped.

⚠ Round 1's verification block records **33 legs**; this branch has **20**.
33 is `ci/test-workflow-380`'s leg count. The passed figure it quotes (1023) is
consistent with this branch at that commit, so the leg count looks like a
transcription error rather than a different checkout — but prefer a measured
number over either.

Clean docs build: `rm -rf docs/_build && sphinx-build -W --keep-going` exit 0,
warning-free.

Control run the required way for every behavioral fix: `src/` reverted, the new
tests run against the unfixed source, each failing with the symptom quoted under
its finding.
