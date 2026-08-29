# PLAN — #486: `TextArea`/`CodeEditor` bind `textsignal` one-way, and `.signal` always returns `None`

**Branch:** `fix/textarea-signal-binding-486` off `main` at `fdb367cc`, which
carries #460 (PR #487)
**Milestone:** `0.4.0 — Signal binding on fields`
**Round cap: 3.** This changes behavior in two directions and adds a write path
that has never existed, so it gets the minor's cap rather than the patch's.

## What is wrong

Two defects in the same pair of widgets, sharing one cause: the textarea core
holds the bound signal privately and neither exposes it nor writes to it.

1. **The binding is one-way.** `signal -> widget` works; `widget -> signal` never
   happens. `self._signal` is assigned in `bind_signal` (`core.py:284`), cleared
   in `_unbind_signal` (`:297`), and read only in an `is not None` guard.
   **Nothing anywhere calls `self._signal.set(...)`.** Measured: after
   `ta.value = "typed by user"`, the signal is unchanged across five `update()`
   and `update_idletasks()` pumps — absence, not latency.
2. **`.signal` always returns `None`.** `textarea.py:155` reads
   `getattr(self._internal, "signal", None)` and `codeeditor.py:191` reads
   `getattr(self._internal.core, "signal", None)`. Neither object has a `signal`
   attribute, so the default fires on every call. `git log -S` over the whole
   history of `_impl/composites/textarea/` shows the internal has **never** had
   `signal` or `textsignal`.

The documented contract is two-way — `docs/reference/signals.rst:54`, "Pass a
signal to a widget to create a two-way binding. Text-bearing widgets use
``textsignal=``". The internal docstring is the honest one
(`_impl/.../textarea.py:68`, "displays and **tracks** the signal's value").

**Population is exactly two widgets.** `grep -rn "bind_signal" src/bootstack/`
returns two callers, `textarea.py:186` and `codeeditor.py:152`.

## The read-back spelling is NOT an open question — measured

Fifteen public widgets expose a signal read-back. **All fifteen spell it
`.signal`; none exposes `.textsignal`.** The constructor keyword varies with
what the widget carries (`textsignal=` for text-space, `signal=` for
value-space); the property does not. So this keeps `.signal` and makes it work.
⚠ **An earlier note in this session called it a decision to be made. It is not.
Do not re-open it.**

## Structure of the fix — the wrappers do not change

The wrappers were reading the right name all along; the impl never provided it.
So the whole read-back fix lives in `_impl`:

- **`core.py`** gains a public `signal` property returning `self._signal`. This
  is what `codeeditor.py:191` already reads via `_internal.core`.
- **`_impl/.../textarea.py`** (the composite) gains a `signal` property
  delegating to `self._core.signal`. This is what `textarea.py:155` already
  reads via `_internal`.

⚠ **`Signal[str] | None` STAYS CORRECT on both wrappers and must not be swept.**
`_signal` is `None` until something binds, so unlike #460's seven, these two
genuinely return `None`. **#460 pinned that in
`test_signal_property_contract.py::test_the_widgets_outside_the_sweep_still_report_none_when_unbound`
— that test must keep passing.** The only wrapper edit is collapsing the now-live
`getattr(..., "signal", None)` to direct attribute access, for the same reason
#460 did it: a default that can no longer fire is a trap for the next reader.

## The echo loop, and why a suspend flag CANNOT work here

`value.setter` goes through the `EditFilter` chain, so a programmatic set fires
`<<Change>>` exactly like a keystroke. A naive write-back therefore loops:
`_on_signal_change` -> `self.value = ...` -> `<<Change>>` -> `signal.set(...)` ->
subscribers -> `_on_signal_change` -> ...

⚠⚠ **`ChangeNotifier._notify` emits with `when="tail"` (`change.py:41`), so the
event is ASYNCHRONOUS. A synchronous "I am applying the signal" flag is already
cleared by the time the event is delivered, and the guard misses every time.**
This is a repeat of the trap recorded in `reference_async_change_event_suspend_guard`:
`SelectBox` emits `<<Change>>` the same way, a synchronous suspend flag failed to
contain it, and **the answer that worked in `Form` (PR #354) was to dedupe on
value.** Reuse that, do not re-derive it.

**So both directions dedupe on value:**

- write-back sets the signal only when `self._signal() != self.value`
- `_on_signal_change` assigns only when `self.value != str(new_value)`

Either guard alone breaks the cycle; both are cheap and each documents its own
side. This is timing-independent, which a flag is not.

## ✅ DECIDED (maintainer, 2026-08-28) — a non-`str` textsignal is REFUSED AT BIND

Adding a write path creates a hazard that could not exist while the binding was
one-way. Measured:

| | today |
|---|---|
| `bs.TextField(textsignal=bs.Signal(123))` | **refuses** — `TypeError: Expected int, got str` |
| `bs.TextArea(textsignal=bs.Signal(123))` | **accepted**, displays `'123'` |

`TextField` refuses because its signal *is* the entry's `StringVar`, so the type
clash surfaces at bind time. `TextArea` has no variable, so nothing checks.

Once the write-back exists, typing into that `TextArea` calls `signal.set("123x")`
on an `int` signal. **That raises inside a Tk callback, where nothing can see it** —
the failure mode `debug_log` exists for, and invisible to the application author.

**Two candidate answers, and this is a scope call, not a technical one:**

- **(a) Refuse at bind time, matching `TextField`.** Consistent with the family
  and fails loudly at the line that is wrong. ⚠ **But it RAISES where the
  framework currently accepts**, which is `0.5.0`'s membership rule, on a
  `0.4.0` branch.
- **(b) Keep accepting; skip the write-back when the signal's type is not `str`.**
  No new raise, but it reinstates a silent one-way binding for exactly the case
  the user cannot see, which is the shape this issue exists to remove.

**CHOSEN: (a), refuse at bind.** ⚠ **Do not re-propose (b) or (c).**

⚠ **The hazard fires at BIND, not on the first keystroke, which is worse than the
issue describes.** `bind_signal` seeds the widget with `self.value = str(v)`,
that fires `<<Change>>`, and the write-back then attempts `signal.set('123')`
against an `int` signal. Measured before the guard: a bare traceback on stderr
at construction, the signal silently keeping its old value, and **nothing on the
background-error channel** — so a `bgerror` collector does not see it either.

The guard sits at the top of `bind_signal`, before anything is mutated, so a
refused bind leaves the core untouched. It reads the **public** `Signal.type`
(`signals/signal.py:481`), not the private `_type`, and reproduces `_reconcile`'s
own message shape so the wording cannot drift from the family's:
`f"Expected {signal.type.__name__}, got str"`. **Measured byte-identical to
`bs.TextField(textsignal=bs.Signal(123))` and pinned by
`test_the_refusal_matches_the_entry_backed_fields`.**

## Invariants

- **`signal -> widget` behavior is unchanged.** Existing one-way users see no
  difference except that their signal now also receives edits.
- **`.signal` returns the exact object that was bound** — identity, not equality.
- **`.signal` is still `None` when nothing is bound**, so #460's pin holds.
- **Unbinding releases both hooks.** `_unbind_signal` already cancels the
  subscription; it must also unbind the `<<Change>>` write-back, or a rebind
  leaves an orphan pushing into a signal nobody is watching. ⚠ **This is #479's
  shape** — a live hook outliving what owns it.

## ⚠⚠ A PRE-EXISTING DEFECT FOUND BY THE DESTROY TEST — HALF FIXED HERE, HALF FILED

**This plan originally asserted that `_unbind_signal` "is already called from
destroy (`core.py:486`), so getting it right costs one line." THAT WAS WRONG, and
the destroy test is what caught it.**

`_on_destroy` opens with `if event.widget is not self: return`. **Measured: the
only `<Destroy>` this handler ever receives names the inner `Text` child, never
the core**, so the guard rejects it and the whole cleanup block never runs. A
signal bound to a destroyed `TextArea` therefore keeps its subscription, and the
next `signal.set(...)` reaches `_on_signal_change`, which writes into a destroyed
Tk widget and raises `TclError`.

**Pre-existing, not introduced here** — measured identical on both arms of
`git stash push -- src/`, so this is not a consequence of the write-back.

⚠⚠ **DO NOT "FIX" THIS BY CORRECTING THE GUARD.** `_chain.destroy()` and the
wheel `unbind_class` calls sit behind the same condition and have therefore
**never executed in the life of this widget.** Repairing the guard would start
running all of it for the first time, in a branch about signal binding, with a
blast radius nobody has measured. **What ships here releases only the signal
hooks — the rest stays exactly as dead as it was.** The dead cleanup block is
filed separately.

## Test plan

New `tests/widgets/public/test_textarea_signal_binding.py`, both widgets:

- signal -> widget still works (the half that already worked; guards regression)
- widget -> signal arrives, per edit
- `.signal` returns the bound object by identity
- `.signal` is `None` when unbound
- **the echo control:** bind, drive N alternating writes from both sides, assert
  the subscriber fired a bounded number of times and the values converged — a
  loop shows up as runaway counts, which a single-write test cannot see
- rebinding a second signal leaves the first receiving nothing (orphan check)
- destroy with a bound signal, then write to the signal — nothing raises on the
  background-error channel

⚠ **The write-back tests must fail at the base commit for the RIGHT reason** —
the signal simply never changes, which is behavioral, not an `AttributeError`.
Run each against `main` before trusting it.

⚠ **Assert on the background-error channel, not just on return values.** A raise
inside a Tk callback is invisible to Python; install a `bgerror` collector as
`_runtime` does and fail on anything it catches.

## Verification

- `py -3.12 tests/run_gui.py` — expect `1638 + <new file>` / 22, exit 0.
- Clean `-W` docs build; the two wrapper docstrings render into the API Reference.
- `development/probe_460_signal_never_none.py --arm control` — the two
  `*** NOT THE BOUND SIGNAL ***` rows must become `OK`. **That probe is the
  before/after instrument and it already exists; do not write a second one.**
- Re-run on the base commit as the control arm.

## CHANGELOG

`## [Unreleased]`, `### Fixed`. The write-back is the half worth the words: a
subscriber on a signal bound to one of these widgets **starts firing on user
edits when it never did before**, which is a behavior change an application can
notice. The read-back cannot break anyone, since it was constant `None`.
