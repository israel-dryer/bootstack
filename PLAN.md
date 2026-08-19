# PLAN — #458: a `Select` bound to a `Signal` binds text, not value

**Branch:** `fix/select-signal-value-458` · **Base:** `main` @ `5b009456`
**Issue:** [#458](https://github.com/israel-dryer/bootstack/issues/458) (external report, `bLynnb2762`)
**Release line:** `0.3.x — Patch line`. Adds no public surface and does not raise where working code used to succeed.
**Round cap: 2** (patch branch, REVIEW-PROTOCOL.md gate 3). Declared before implementation. Survivors at the cap are filed as issues, not fixed here.

---

## What is wrong

`Select` maps its public `signal=` onto the internal **`textsignal=`** (`select.py:130`), which installs the `Signal`'s Tk variable *as the entry's `textvariable`*. Measured: both are `SIG1`. Signal writes therefore land directly in the entry's display text, bypassing two things at once:

- `_resolve_display()` — the value-to-display-text map that the `value=` path goes through (`selectbox.py:131`);
- the entry's commit path, which is what maintains `TextEntryPart._value` — the cache `.value` actually reads.

That single wiring line produces two symptoms.

**A — the reported one.** With decoupled `(text, value)` options, the field displays the raw value. `Signal('2')` shows `2`, where `value='2'` shows `Two`.

**B — not reported, and worse.** Writing to a bound signal moves the display but not the selection: `.value` and `.selection` keep reporting the previous option and **no `<<Change>>` fires**. This needs no decoupling — it hits plain `list[str]` options too, and it does not self-heal (measured: survives a `<Return>`; only a real pick through the popup resyncs). So the widget shows one option and reports another, indefinitely, and code reading `.value` on submit gets the option the user is not looking at.

Symptom B is why this is not cosmetic. `.value` decodes text back to value via `_value_by_text`, which is exactly why the reporter saw correct event data and read the whole thing as a display glitch.

## How it got here (so the fix is aimed at the cause)

| date | commit | |
|---|---|---|
| 2026-05-28 | `3cc69e5b` | `Select` ships with `text_signal=` mapped to `textsignal`. Honest: `options: list[str]`, text *was* value. |
| 2026-05-31 | `4b50f2f2` | *"Rename `text_signal=` to `signal=` for consistency"*. Name became value-space; wiring stayed text-space. Still not a defect — options were still plain. |
| 2026-06-10 | `ee3345d4` | Shared option shape adds `(text, value)` and `_resolve_display`. The two spaces split. `value=` was routed through the new map; the signal path was not. **Defect A born.** |
| 2026-06-12 | `d05ecd8a` | `ValueSignalMixin` built and applied to Number/Date/Time. `select.py` untouched. |

Symptom B is older than A: `TextEntryPart.value()` already returned the committed `self._value` at `3cc69e5b`, so a raw variable write has never updated it. B dates from 2026-05-28.

`d05ecd8a`'s design doc records why `Select` was skipped (`docs/_dev/field-value-dtype.md:55`): *"`Select` already had `signal=`."* The sweep checked for the **presence of the kwarg name**, not **which space it bound** — and the rename 12 days earlier is precisely what made `Select` pass that check.

## The fix

Adopt the pattern the three sibling field widgets already use. `TimeField` is the direct precedent: it rides the **same `SelectBox` internals**, binds through `ValueSignalMixin`, and explicitly rejects `textsignal=` (`timefield.py:92`).

1. `Select(ValueSignalMixin, PublicWidgetBase)`.
2. Stop passing `internal_kwargs["textsignal"]`. After the internal is constructed, `self._bind_value_signal(signal)`.
3. `Select.value` setter calls `self._sync_value_set(...)`, so a programmatic set pushes to the signal (the mixin's `on_change` sync only covers commits).
4. Reject `textsignal=` with a message pointing at `signal=`, mirroring `TimeField`.

The mixin binds through the `value` property, which is the path that runs `_resolve_display` **and** maintains the committed value **and** emits `<<Change>>`. That is why one change fixes both symptoms — and why they are not separable: any fix for B has to bind through `value`, and that binding is inherently value-space.

## Contract after this change

`signal=` carries the option's **value**, matching `Select.value`, `DateField`, `NumberField` and `TimeField`.

```python
sig = bs.Signal('2')
sel = bs.Select(options=[('One', '1'), ('Two', '2')], signal=sig)   # shows 'Two'
sig.set('1')        # shows 'One', .value == '1', <<Change>> fires
sel.value = '2'     # sig() == '2'
```

**Both directions move.** Today `sel.value = '2'` writes the *text* `'Two'` into the signal; after this it writes `'2'`. Same one-line cause, and leaving the write-back in text-space would make the signal round-trip lossy.

## Invariants — must not move

- `.value` and `.selection` stay value-space. Not touched.
- **Plain `list[str]` options seed identically** to today. Text == value, so both readings coincide. This is the control that scopes the change.
- An **off-list value still displays and does not raise** (#368 retired-value path). Measured on `main`: `value='99'` shows `'99'`. Must hold via a signal.
- `read_only` (#453) untouched — it is derived, never storage. The value setter already brackets its write with the readonly state; binding must not defeat it.
- No emit loop: the mixin's `_value_syncing` guard must hold in both directions.
- The subscription is released on destroy — a `Signal` outlives its widgets.

## Blast radius

- **No test constructs `Select` with a signal.** Verified across full repo history, not just the current tree.
- `docs/widgets/select.rst:225` demos `signal=` with `["Red", "Green", "Blue"]` — plain options, where both readings are indistinguishable. Unaffected.
- The text-space contract is asserted **only** in `Select.signal`'s own docstring (`select.py:40`), which describes the behavior rather than designing it. Rewritten here.
- `textsignal=` on `Select` is **silently swallowed today** (measured: falls into `**kwargs`, never read — #383's third gap). It cannot be in working use, so raising on it breaks nobody.

## Risks

- `ValueSignalMixin._push_to_signal` reconciles numeric types off `signal._type`. Select values are usually `str` (measured: `Signal('1')._type is str`), so the numeric branch is inert — but a `Select` over int-valued options is legal and must be exercised.
- `Select` is a `Form` editor. `Form` binding must be checked, not assumed.
- Seeding order: `_bind_value_signal` runs *after* `_attach_to_parent`, matching `TimeField`. A signal and an explicit `value=` together — the signal wins, since it seeds last. Pin it so it is a decision, not an accident.

## Tests — `tests/widgets/public/test_select_signal_value.py`

Every test must fail against pre-fix source for a **behavioral** reason. Nothing here raises `AttributeError` pre-fix (`signal=` is accepted today), so a failure means wrong behavior, not a missing method.

**Planned 10; 15 were written.** The five extra are the seed-emit guard found during implementation (below), a round trip through a second `Select` sharing one signal, the `value=`/`signal=` equality pinned as a pair rather than as two expectations, the `value=` + `signal=` precedence, and the destroy-release split out of row 10 so the loop guard and the subscription release are pinned separately.

| # | pins |
|---|---|
| 1 | the report: decoupled options plus `Signal('2')` displays `Two` |
| 2 | signal write moves display **and** `.value`/`.selection` (decoupled) |
| 3 | **symptom B on plain options** — signal write moves `.value` |
| 4 | signal write fires `<<Change>>` exactly once |
| 5 | write-back: `sel.value = '2'` puts `'2'` (not `'Two'`) in the signal |
| 6 | control: plain options seed identically to `value=` |
| 7 | off-list signal value displays, does not raise (#368) |
| 8 | int-valued options round-trip |
| 9 | `textsignal=` raises and names `signal=` |
| 10 | no feedback loop; subscription released on destroy |

## Verification

- `py -3.12 tests/run_gui.py` — full suite, all legs, exit 0. Record the count and the commit measured at, per CLAUDE.md.
- `development/probe_458_select_signal_display.py` re-run: arms 1 and 2 agree, arm 3 (control) unchanged, arm 4 tracks.
- Clean `-W` docs build (`Select.signal`'s docstring is rendered API surface).
- Manual: the reporter's exact snippet from #458.

---

## Verification results — measured on the working tree before commit

Windows box, `py -3.12`, `pandas` absent.

| check | result |
|---|---|
| `py -3.12 tests/run_gui.py` | **exit 0, 33 legs, 1458 passed / 21 skipped** |
| `main` on the same box, **derived** | **1443 / 21** — this branch's only change under `tests/` is one new file of 15 tests, so the delta is bounded at exactly +15 (1443 + 15 = 1458, and it reconciles) |
| new tests vs **pre-fix** `select.py` | **11 failed, 4 passed** |
| clean `-W` docs build | succeeded, **0 warnings** |
| reporter's snippet from #458 | displays `Two`; **0 change events at startup** |
| probe arms 1/2/3/4 | 1 and 2 agree, 3 (control) unchanged, 4 tracks every write |

⚠ **One test breaks the behavioral-failure standard stated above, and it is called out rather than smoothed over.** `test_destroying_the_field_releases_the_signal_subscription` fails pre-fix with `AttributeError: 'Select' object has no attribute '_value_sub'` — structural, not behavioral. It cannot be otherwise: it guards a leak in machinery that does not exist before this branch, and pre-fix there is no subscription to leak, so any behavioral form of it would pass vacuously. Accepted as an invariant guard on new machinery; a reviewer should not read its pre-fix failure as evidence the defect reproduces.

The 4 tests that pass pre-fix are **meant to** — they are the control
(`test_plain_options_are_unaffected`) and the invariant guards (off-list value,
read-only, seed-emit). A test that passes on both sides of the fix is only
vacuous if it claims to pin the defect; these claim to pin what must NOT move.

Pre-fix failures are behavioral, not `AttributeError`: `'2' == 'Two'` (the
report), `'One' == 'Three'` (the unreported symptom, plain options), and
`[] == ['2', '3']` (the missing change events).

## Found during implementation, and fixed here

**Binding a signal emitted `<<Change>>` at construction, where `value=` does
not.** The mixin seeds by assigning `value`, and `SelectBox`'s setter emits. The
event is **queued**, so a handler bound on the line after the constructor still
receives it once the loop turns — the reporter's own snippet binds `on_change`
to `bs.toast`, so this would have toasted on startup. Suppressed for the seed
only, via the `_suppress_changed_event` flag `selectbox.py:1212` already reads.

⚠ **That flag had no writer anywhere in `src/` before this branch** — it was a
read-only seam. This is the first code to set it. Flagged rather than buried,
because a reviewer will not find another caller to compare against.

## Out of scope — filed, not fixed

**[#459](https://github.com/israel-dryer/bootstack/issues/459)** — `TimeField`
has the identical seed-emit behavior, and it is **pre-existing**: it has bound
through `ValueSignalMixin` since `d05ecd8a` (2026-06-12), long before this
branch. Measured with both controls (`TimeField(value=)` is quiet, and the
`NumberField`/`DateField` siblings are quiet), so the finding is scoped to the
signal door on the one select-backed field. Left unmilestoned — it gates
nothing.

## Discharged risks

- **`Form` integration** — checked rather than assumed. `form.get()` after
  `form.set({'size': '2'})` on a select editor returns `{'size': '2'}`, and a
  `Select` with no signal reports `.signal is None`, so the new
  `_sync_value_set()` call in the value setter early-returns and the no-signal
  path is byte-for-byte unchanged in behavior.
- **Non-`str` option values** — int-valued options round-trip in both
  directions (`_push_to_signal`'s numeric reconciliation is exercised). The
  `signal` annotation was widened from `Signal[str]` to `Signal` to match.
- **`value=` + `signal=` together** — the signal seeds last and wins. Pinned, so
  the precedence is a decision rather than an artifact of statement order.
