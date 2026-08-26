# PLAN — #476 (`SelectButton` fires `on_change` twice)

Branch `fix/selectbutton-double-change-476`, off `main` at `6fb3abc9`. Milestone `0.4.0`.
**Round cap: 2.**

Cap 2 rather than the minor's 3, stated deliberately: the diff is a few lines in one internal
file, adds no public surface, raises nowhere, and changes no documented behavior. It is
patch-shaped work riding a minor because #476 was found during `0.4.0` and the maintainer
asked for it in this release. If round 1 finds anything in production code beyond the
`_bind_id` handling, raise the cap rather than spending it.

## Not on #461's branch, deliberately

PR #475 (`fix/selectbutton-signal-value-461`) is open, reviewed, and ready to merge. Adding a
`src/` commit to it re-triggers gate 1 and forces a round 2 on a branch that is done.
`optionmenu.py` is untouched by that branch — its diff is `selectbutton.py` and
`timefield.py` — so the two do not conflict and either can merge first.

## Baseline — measured, not read

`main` at `6fb3abc9`, Windows box, `py -3.12`, event queue drained so `when="tail"` emitters
are not undercounted:

```
SelectButton (decoupled options)   on_change fired 2x  ['2', '2']
SelectButton (plain list[str])     on_change fired 2x  ['b', 'b']
user selection path                on_change fired 2x  ['2', '2']
Select                             1x
TimeField                          1x
NumberField / DateField            0x   (user-commit only; separate question, not this fix)

_bind_change_event calls per construction: 2
   call 1: self._bind_id was None  -> new sub id A     <- from :368, RETURN DISCARDED
   call 2: self._bind_id was None  -> new sub id B     <- from :124, stored
stored _bind_id                  : B
live subscribers on _textsignal  : 2
```

The user path is not a separate mechanism: a menu item is a `radiobutton` bound to
`variable=self._textvariable` with `value=rec.text` (`optionmenu.py:233-235`), so a click
writes that variable exactly as `.value` does.

## Cause

`_bind_change_event` (`_impl/primitives/optionmenu.py:200`) guards with
`if self._bind_id is not None: self._bind_id.cancel()` and then **returns** the new
subscription. `__init__:124` stores the return; `_delegate_textsignal:368` discards it. Since
`:93` sets `_bind_id = None` before either runs, the guard sees `None` on both calls and
cancels nothing. The signal notifies once per change — measured — and each of the two live
`_on_change` closures emits its own `<<Change>>`.

## The change

`src/bootstack/widgets/_impl/primitives/optionmenu.py`

1. `_bind_change_event` assigns `self._bind_id` itself instead of relying on its caller to.
   Every call path is then tracked and the existing guard actually works.
2. `:124` becomes a bare call; `:368` is left as a bare call and is now correct for free.

Assigning inside is chosen over the one-line `self._bind_id = self._bind_change_event()` at
`:368` because the latter leaves the identical trap for the next caller — and there has
already been one.

Net effect: call 1 cancels nothing and stores sub A; call 2 cancels sub A and stores sub B.
Exactly one live subscription.

## Tests — `tests/widgets/public/test_selectbutton_change_once.py`

1. **`test_a_selection_fires_change_exactly_once`** — public path, `sb.value = …`, decoupled
   options. The headline assertion.
2. **`test_plain_string_options_fire_change_exactly_once`** — the other option shape.
3. **`test_repeated_selections_do_not_accumulate`** — three successive sets, three events, not
   six or twelve. Guards against a rebind that re-adds rather than replaces.
4. **`test_reassigning_options_leaves_one_subscription`** — `sb.options = [...]` rebuilds the
   menu (`:349`); prove the rebuild path does not re-add a subscriber.
5. **`test_exactly_one_change_subscription_after_construction`** — structural, asserts
   `len(internal._textsignal._subscribers) == 1`. Breaks the "test public paths" rule on
   purpose and says why in the test: the behavioral tests above pass for any count that
   happens to emit once, while the invariant is "one subscription", and this is the assertion
   that fails deterministically the moment a second call path forgets to track again.
6. **`test_rebinding_the_textsignal_replaces_the_subscription`** — drives `:368` directly on a
   constructed internal (`configure(textsignal=…)`), which is the path that caused the bug and
   is unreachable from public API since #472. Constructs the internal, not a `bs.SelectButton`.

**Control, run before committing:** revert the fix, confirm tests 1–6 fail, and confirm the
failure is the emission **count** rather than an `AttributeError` or a missing attribute — a
test that fails because the fix does not exist yet proves nothing.

## Boundary of the completeness claim

`grep -rn "_bind_change_event" src/bootstack --include=*.py` returns exactly three lines, all
in `optionmenu.py` (`:124`, `:200`, `:368`). `optionmenu.py` contains exactly one
`event_generate('<<Change>>')` (`:211`). `grep -rn "OptionMenu" src/bootstack --include=*.py`
shows `_InternalOptionMenu` constructed in exactly one place, `selectbutton.py:99`. So the
blast radius is `SelectButton` and nothing else. `SelectBox` has no `_bind_change_event`,
which is why `Select` measured clean.

## Out of scope

- `NumberField` / `DateField` emitting **zero** `<<Change>>` on a programmatic set while
  `Select`, `TimeField` and `SelectButton` emit one. That is a family consistency question,
  possibly by design (change == user commit). Note it in the record; do not fix it here.
- Collapsing the `_impl` layer so the subscribe-then-`event_generate` bridge disappears
  entirely. That is #477, pre-1.0, its own pass.

## CHANGELOG

One bullet under `### Fixed` in `## [Unreleased]`, reachable by any user with a
`SelectButton` and an `on_change` handler, so it earns its entry.
