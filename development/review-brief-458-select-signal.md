# Review brief — #458, round 1

**For the reviewing session. Read this and `PLAN.md`, then the diff.**

`REVIEW-PROTOCOL.md` says the reviewer must not read the implementer's
*rationale* about why the approach was sound. This file is deliberately not
that. It carries only two things: **decisions already taken by the maintainer**
(so a round is not spent re-litigating them) and **measurements already made**
(so they are not re-derived). Both are facts about the state of the work, not
arguments for it. `0.3.1` lost a round to exactly this gap — round 3 there
re-filed three already-triaged items because nobody handed the reviewer the
triage state.

---

## What to review

| | |
|---|---|
| branch | `fix/select-signal-value-458`, head `1f9a62d1`, pushed |
| scope | round 1 reviews the whole branch: `git diff main...HEAD` |
| production diff (gate 1) | `src/bootstack/widgets/select.py` only — **41 lines, and most of them are comment** |
| round cap | **2**, declared in `PLAN.md` before implementation. Survivors at the cap are filed as issues |
| issue | [#458](https://github.com/israel-dryer/bootstack/issues/458), external report from `bLynnb2762` |

---

## Settled by the maintainer — do NOT re-open

1. **`signal=` is value-space.** It carries the option's *value*, not its
   display text. Decided 2026-08-19 after the alternatives were put to the
   maintainer explicitly (keep text-space and fix only the sync; or add a
   separate `textsignal=` escape hatch). Value-space was chosen.
2. **This ships on the patch line**, not as a minor. It adds no public surface,
   and the pre-change behavior — displaying one option while reporting another —
   is not a contract anyone could depend on.
3. **Both defects are fixed under one issue.** Filing the unreported
   value-staleness separately was proposed and rejected: same root cause, same
   one-line fix, and no fix for the staleness exists that does not also pick a
   space.
4. **The CHANGELOG bullet stays at symptom altitude.** Enumerating the
   sub-cases ("also affects plain options") was proposed and rejected —
   *"a reader would know if they are affected, and if not, they weren't."*
   Do not file a finding asking for the sub-cases back.

## Measured — do NOT re-derive

Every number below was taken on the Windows box, `py -3.12`, `pandas` absent.
Prefer a number you measure yourself over one written here, but these were taken
at the committed head and reconcile.

- **Suite: exit 0, 33 legs, 1458 passed / 21 skipped**, at `1f9a62d1`.
  `main` on the same box derives to **1443 / 21**; the branch's only change
  under `tests/` is one new file of 15 tests, so `1443 + 15 = 1458` and the
  delta is bounded, not just self-consistent.
- **Pre-fix control: 11 of the 15 new tests fail**, ten of them behaviorally
  (`'2' == 'Two'`, `'One' == 'Three'`, `[] == ['2', '3']`).
- **Clean `-W` docs build: 0 warnings.** The rendered `Select.signal` text was
  read out of the built HTML, and the `#453` toolkit-vocabulary grep over
  `docs/_build/html` returns nothing.
- **The reporter's exact snippet** displays `Two` and raises **0** change
  events at startup.
- **`Form` is unaffected**: `form.get()` after `form.set({'size': '2'})` on a
  select editor returns `{'size': '2'}`, and an unbound `Select` reports
  `.signal is None`, so the new `_sync_value_set()` call early-returns.

## Two things the implementer flagged against itself

Look at these hardest; they are where a finding is most likely to be real.

1. **`self._internal._suppress_changed_event` now has its first writer.** It
   existed at `selectbox.py:1212` as a flag that was *read and never set*
   anywhere in `src/`. Setting it is how seed-time `<<Change>>` is suppressed.
   There is no second caller to compare against, and the try/finally is the only
   thing guaranteeing it is cleared.
2. **One test fails pre-fix with `AttributeError`, not behaviorally.**
   `test_destroying_the_field_releases_the_signal_subscription` asserts on
   `_value_sub`, which does not exist before this branch. Argued in `PLAN.md` as
   unavoidable for a guard on new machinery — worth a second opinion on whether
   it is vacuous in its post-fix form.

## Known-out-of-scope — already filed, do not file again

- **[#459](https://github.com/israel-dryer/bootstack/issues/459)** — `TimeField`
  has the identical seed-emit behavior. **Pre-existing**, since `d05ecd8a`
  (2026-06-12); measured with both controls. Not fixed here.
- **#383's third gap** — unknown kwargs on a public wrapper are silently
  discarded. This branch refuses `textsignal=` on `Select` specifically, but the
  general sweep is #383's, not this branch's.
- **#449** — `test_select_change_event_value_space` is a known ~1-in-10 flake
  that pins an exact event list against an async change. This branch adds tests
  in the same family (`test_a_signal_write_fires_change_once` pins
  `["2", "3"]`). If that flakes, it is #449's shape; gate 4 gives it one fix
  attempt with a mechanism-reproducing control, then quarantine — not a re-run.

## Worth actually checking

Offered as orientation, not as a list to confine the review to.

- Does the seed suppression have a hole? It is scoped by try/finally around
  `_bind_value_signal`, which also *subscribes*. If any later write could run
  inside that window, it would be silently swallowed.
- `value` setter now calls `_sync_value_set(self.value)` — it re-reads through
  the getter rather than echoing `v`. Is there a value where the getter and the
  setter's argument disagree in a way that matters?
- The `_value_syncing` loop guard is the mixin's, exercised here for the first
  time on a widget whose setter emits. Two `Select`s sharing one signal is
  covered by a test; three, or a `map()`-derived signal, is not.
- `read_only` (#453) brackets the entry's ttk state inside the same value
  setter the signal now drives. Covered only by a property read.
