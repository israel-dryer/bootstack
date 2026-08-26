# PLAN — #461 (`SelectButton` signal space) + #459 (`TimeField` seed emit)

Branch `fix/selectbutton-signal-value-461`, off `main` at `ede2d57e`. Milestone `0.4.0`.
**Round cap: 3** (minor line).

## Why the two ride together

#461's fix is "bind through `ValueSignalMixin`, as #458 did for `Select`". The mixin seeds by
assigning `.value`, so any widget whose value setter emits raises `<<Change>>` during
construction — which is #459's defect, still live in `TimeField`. #461's own issue body names
#459 as the thing to check rather than inherit. Fixing them apart means writing the same seed
handling twice and reviewing it twice.

Two commits, one per issue. Merge commit, not squash.

## Baseline — measured, not read

`development/probe_461_selectbutton_signal_space.py`, run on this branch before any source
change (working tree identical to `main` at `ede2d57e`), Windows box, `py -3.12`:

```
ARM 1  options [('One','1'), ('Two','2'), ('Three','3')]
  signal seeded with LABEL 'Two'   text='Two'   value='2'  selection='2'   signal='Two'    is-same-object=False
  signal seeded with VALUE '2'     text='2'     value='2'  selection=None  signal='2'      is-same-object=False
  value='2'   (control door)       text='Two'   value='2'  selection='2'   signal=None
  after sb.value = '3'             text='Three' value='3'  selection='3'   signal='Three'
ARM 2  TimeField(signal=Signal(time(9,0)))   -> [datetime.time(9, 0)]
       TimeField(value=time(9,0))   control  -> []
       NumberField / DateField / Select      -> []
ARM 3  SelectButton(signal=Signal('Two'))    -> []      (no seed emit today)
       SelectButton(value='2')      control  -> []
```

Reproduces both issues verbatim. **ARM 3 is the one that was not obvious**: `OptionMenu` emits
from a `textsignal` subscription with the default `when='now'`, so today's seed is delivered
before any handler can be bound. Whether the fix keeps that property is measured after, not
assumed from the `Select` precedent.

## Cause

`SelectButton.__init__` maps public `signal=` onto the internal `textsignal=`
(`selectbutton.py:84`). That variable is `OptionMenu._textvariable`, which holds the option's
**text** — `get()` maps text→value and `set(value)` maps value→text. So the signal is
label-space while `value=`, `.value`, `.selection` and the `<<Change>>` payload are all
value-space.

`TimeField.__init__` calls `_bind_value_signal` unguarded (`timefield.py:136`). Its internal is
`TimeEntry(SelectBox)`, and `SelectBox`'s value setter emits `<<Change>>` on a programmatic set
(`selectbox.py:1212`) unless `_suppress_changed_event` is set.

## The change

**#461 — `src/bootstack/widgets/selectbutton.py`**

1. `class SelectButton(ValueSignalMixin, IconProperty, PublicWidgetBase)`.
2. Drop `internal_kwargs["textsignal"] = signal`; call `self._bind_value_signal(signal)` after
   `_attach_to_parent`, mirroring `select.py:167-177`.
3. `value` setter calls `self._sync_value_set(self.value)` — read back, do not echo `v`.
4. Delete the local `signal` property (`selectbutton.py:148`); the mixin's replaces it.
5. Docstring: `signal` is value-space, mirroring `Select`'s wording.

**#459 — `src/bootstack/widgets/timefield.py`**

Wrap `_bind_value_signal` in `self._internal._suppress_changed_event = True/False`, exactly as
`select.py:173-177`, with the same reason comment.

## Decisions taken, with their reasons

- **`signal=` becomes value-space. This is a behavior change** — label seeding is the only
  spelling that works today. Same call taken deliberately for `Select` in #458; `0.4.0` already
  forces a migration. **Needs maintainer confirmation before the commit lands** (#461 asks for
  it explicitly rather than letting it carry over).
- **A label-seeded signal will now raise `ValueError: 'Two' is not one of the options`** at
  construction, from `OptionMenu.set`. Not softened: it is byte-for-byte what
  `SelectButton(value='Two')` raises today, and the `value=` door is the standard both #459 and
  #461 hold the signal door to. The migration is explained in the CHANGELOG, not in a bespoke
  error.
- **`sb.signal is sig` becomes `True`** (baseline: `False` — the property forwarded to a
  different `Signal` wrapping the same variable). #461's secondary observation, closed by the
  same edit.
- **No seed suppression is added to `OptionMenu` unless ARM 3 says the fix needs it.** Measure
  post-fix; pin the outcome with a test either way.
- **#460's population shrinks by one.** Deleting `SelectButton.signal` removes
  `selectbutton.py:149` from that issue's table of eight. Comment on #460 at merge; do not
  silently leave the table wrong.

## Tests

New `tests/widgets/public/test_selectbutton_signal_value.py`, modelled on
`test_select_signal_value.py`. Every test must fail pre-fix for a **behavioral** reason —
`signal=` is accepted today, so nothing may pass merely because an attribute appeared.

- seeded `Signal('2')` selects Two (text, `.value`, `.selection` all agree)
- `value=` and `signal=` seed identically — the equality IS the contract
- a signal write moves the selection, on plain and on decoupled options
- `sb.value = '3'` pushes `'3'` (not `'Three'`) to the signal
- round-trip through a second `SelectButton` sharing the signal
- `sb.signal is sig`
- a label-seeded signal raises, and `value=` raises the same way (paired, so the two doors
  cannot drift apart again)
- plain `list[str]` options unaffected (the control population)
- seeding does not fire `<<Change>>` — whatever ARM 3 measures post-fix, pinned
- destroying the button releases the signal subscription
- assert on values carried, **never on event counts**: `SelectButton` emits `<<Change>>` more
  than once per set today, a pre-existing `StringVar` quirk noted at
  `test_select_options.py:290`

New `tests/widgets/public/test_timefield_signal_seed.py`:

- `TimeField(signal=…)` fires no change event at construction, with `TimeField(value=…)` as the
  in-file control
- a later signal write still fires normally — the suppression must be seed-only
- `NumberField`/`DateField` siblings stay quiet (they already do; guards the mixin edit)

## Docs and CHANGELOG

Four docs sites pass `signal=` to a `SelectButton`, all with plain `list[str]` options
(`custom_sidebar.py:48`, `screenshots/navigation.py:198`, `custom-sidebar.rst:29`,
`selectbutton.rst:117`) — text == value, so none is affected. Checked before the change, per
#472's lesson that a guard's blast radius was measured over `src/` and `tests/` and bit in
`docs/`. Re-run `python docs/examples/selectbutton.py` and the custom-sidebar example anyway.

`## [Unreleased]` gains a `### Fixed` bullet for #459 and a `### Changed` bullet for #461 — it
raises where it used to accept, so it belongs beside #472's under `Changed`, not `Fixed`.

## Out of scope

#460 (the `| None` sweep), #467 (the `custom`-rule escape), and the `SelectButton` multi-emit
quirk. Filed, not touched.

## Outcome — measured AFTER the change, not planned

Recorded here for the reviewer. Everything above this line was written before any source edit.

- **The plan's one open measurement is settled: `SelectButton` needs NO seed suppression.** ARM 3
  post-fix reads `[]`. Its internal emits with the default `when='now'`, so the seed is delivered
  before a handler can be bound, where `Select` had to suppress a QUEUED emit. No new internal
  surface on `OptionMenu`. **Pinned by a test, because that difference is invisible in the source
  and a later change to the emit's `when=` would silently break it.**
- **Post-fix probe, same arms:** `signal=Signal('2')` -> `text='Two' value='2' selection='2'
  signal='2' is-same-object=True`; `sb.value='3'` -> `signal='3'` (was `'Three'`);
  `signal=Signal('Two')` -> `ValueError`, and `value='Two'` raises identically. #459's row is `[]`
  with its `value=` control still `[]`.
- **Suite: 1573 passed / 22 skipped, 33 legs, exit 0**, Windows box, `py -3.12`, `matplotlib` and
  `pandas` both present. Baseline `main` was 1552/22, so **+21 — exactly the 15 + 6 new tests**,
  with `git diff --stat -- tests/` empty (no existing test touched) bounding the movement.
- **Pre-fix control run: 14 failed / 7 passed.** No defect test passed pre-fix; the 7 are the
  controls and guards (the plain-options population, `TimeField`'s `value=` door, the mixin
  siblings, the seeded-value precondition, and the two over-suppression guards). Run by stashing
  ONLY the two source files, so the new tests met genuinely pre-fix source in the same tree —
  no worktree, no `PYTHONPATH` skew.
- **Both affected docs examples build and pump without raising** (`docs/examples/selectbutton.py`,
  `docs/examples/navigation/custom_sidebar.py`), driven headlessly with `run()` replaced by a
  bounded pump. Neither is reached by the suite or by CI, which is #472's lesson applied.
- ⚠ **NEW, and NOT fixed here: an off-list signal write now raises and leaves the two out of
  step.** `signal.set('99')` raises `ValueError` at the caller's own `set()` call site — visible,
  not swallowed into the event loop — but the signal keeps `'99'` while the button stays on its
  previous option. Pre-fix that write displayed `'99'` instead. **This is #369's**, which already
  records `SelectButton` as raising on both doors and asks the selection family for ONE decision;
  the fix only extends the existing `value=` behavior to the signal door. The test pins **the
  raise**, deliberately not the state it leaves behind.
- **The #458 CHANGELOG bullet was amended.** It ended *"`SelectButton` is unchanged and still
  binds the label shown for an option"* — false as of this branch, and both bullets ship in the
  same release. Legitimate because that section is still `## [Unreleased]`; shipped history stays
  untouched.
