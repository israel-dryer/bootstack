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
