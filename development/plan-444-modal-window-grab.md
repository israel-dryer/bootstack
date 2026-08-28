# PLAN — #444 (a modal `bs.Window` never restores the grab it took)

Branch `fix/modal-window-grab-444`, off `main` at `a5f2c71d`. Milestone `0.4.0`.
**Round cap: 2, spent 1** — round 1 ran 2026-08-27 and its record plus the fix step are in
`REVIEW.md`. ⚠ **Read `REVIEW.md` before this file**: round 1 found a blocker in the fix this plan
describes, and the shape below is what shipped BEFORE that fix.

Patch-shaped — **adds no public surface** — riding `0.4.0` because that minor is being cut
anyway and the standing rule is to ask what else is ready rather than park a fix out of habit.
Moved onto the milestone from `0.3.x` by maintainer decision 2026-08-27, in the same pass that
cut `0.4.x — Patch line` and closed `0.3.x`.

## The defect

`_runtime/toplevel.py:222-233` — `show()` takes a modal grab and **nothing ever hands it back**:

```python
if self._modal:
    if self._modal == "app":
        self.grab_set_global()
    else:
        self.grab_set()
```

`grep -rn "grab_release\|grab_current" src/bootstack/_runtime/toplevel.py` returns **nothing**,
which is the whole defect in one command. Tk drops a grab when its holder is destroyed but does
**not** restore the grab that holder displaced, so a modal window opened from inside another
modal leaves the outer one on screen, still blocking its caller, **holding no grab at all** —
the user clicks straight past it into the main window.

**Pre-existing, identical in `0.2.3` and `0.3.0`. NOT a regression from #440.** #440 fixed this
same defect and was scoped to the dialog classes; `toplevel.py` is the only other `grab_set` in
the tree and was not touched. `grep -rn "grab_set" src/bootstack/` returns `dialogs/_impl/`
(covered by #440), `_core/capabilities/grab.py` (the capability methods themselves, which take a
grab on request and are not a policy site) and `_runtime/toplevel.py` — **this one.**

## The fix has an exemplar and it must be MOVED, not copied

#440 already built `capture_grab(widget)` / `restore_grab(token)` in
`dialogs/_impl/dialog.py:185-262`. They are module-level, carry no dialog state, read the grab
**kind** back from Tk rather than assuming, and degrade a failed global restore to local rather
than to nothing. **Do not write a second pair.**

⚠ **The import direction forbids using them where they are.** `dialogs/_impl/dialog.py:20` does
`from bootstack._runtime.toplevel import Toplevel`, so `dialogs` → `_runtime`. `_runtime`
importing back from `dialogs` would be a cycle.

- **Move `capture_grab`, `restore_grab` and `_log_grab_failure` to a new `_runtime/grab.py`**,
  docstrings intact. That module already has the right neighbours — `_log_grab_failure` calls
  `_runtime.utility.debug_log_exception` today.
- **`dialogs/_impl/dialog.py` imports the two names.** ⚠ **This is NOT a compat shim.** An
  ordinary `from … import` binds the names in `dialog.py`'s namespace, so
  `from bootstack.dialogs._impl.dialog import restore_grab` — which `datedialog.py:19` and
  **eight call sites in `tests/widgets/public/test_dialog_nested_modality.py`** use — keeps
  resolving with no alias and no re-export machinery.
- ⚠ **The test imports are deliberately LEFT pointing at `dialog.py`.** Retargeting them is
  churn inside #440's tests for no behavioral gain, and gate 2 says test findings are only
  actionable for vacuity or false alarm. **Recorded so a reviewer reads it as a choice.**

## ✅ The open question is ANSWERED — **B, by measurement.**

`development/probe_444_grab_restore_ordering.py`: the destroy-time restore **wins** its race
with Tk's own grab release. The `<Destroy>` handler saw the inner window still holding, restored,
and `grab_current()` read the opener again once the dust settled — holder **and** kind.

```
outer holds:        ('.!toplevel', 'local')
inner holds:        ('.!toplevel2', 'local')
destroy fired       ('.!toplevel2', 'local')
restore attempted   ('.!toplevel', 'local')
after the dust:     ('.!toplevel', 'local')   VERDICT: OPTION B HOLDS
```

**So B ships and the non-blocking gap never opens** — nothing is filed, because nothing is left
uncovered. `block_until_closed()` is untouched: destroy fires on that path too.

⚠ **The boundary greps came back CLEAN, and one candidate was measured rather than assumed.**
Every real `grab_set` site now pairs with capture/restore: `datedialog.py:135/140`,
`dialog.py:477/482`, `toplevel.py:234/265`. The other `grab_set` hits are the capability methods
themselves and the restore helper's own calls. Of the two outright `grab_release` sites,
`datedialog.py:381` is explained by its own docstring (it destroys the window), and
**`contextmenu.py:1423` was suspected as a sibling and is NOT one** —
`development/probe_444_contextmenu_grab.py` shows `grab_release()` on the menu leaves an outer
grab untouched, because the menu does not hold it. **Do not re-raise it.**

⚠ **A `Dialog` does NOT now restore twice, and this was measured with a control after the first
probe silently lied.** `Dialog._create_toplevel` (`dialog.py:515`) builds its `Toplevel` with
`master`, `window_style` and `transient` and **never passes `modal=`**, so `Toplevel._modal` is
falsy on the dialog path and `show()`'s grab block never runs — the dialog takes its own grab
directly at `:478`. The two paths are disjoint. `development/probe_444_double_restore.py`
reports **1 restore, not 2**. ⚠⚠ **ITS FIRST RUN REPORTED 0, WHICH LOOKED LIKE EVEN BETTER NEWS
AND WAS A BROKEN SPY:** patching `_runtime.grab.restore_grab` does nothing to a name already
bound by `from … import` in `toplevel.py`. **Patch where the name is BOUND, not where it is
defined** — and the probe now carries a control asserting the spy can see a call at all, because
a no-op patch and a genuine absence are the same reading.

## The question as it stood before the measurement — kept for why B was not assumed

The issue suggests pairing around `show()` and restoring in `block_until_closed()`'s `finally`.
**That covers only the blocking path**, and a modal `bs.Window` does not have to block: `show()`
then a later `destroy()` is reachable, and it would keep the defect.

| | covers | risk |
|---|---|---|
| **A** — restore in `block_until_closed()`'s `finally` | the blocking path only | none; it is the dialog's own proven shape, and it runs strictly AFTER `wait_window` returns, so after Tk has dropped the grab |
| **B** — restore from a `<Destroy>` binding on the window | **every** path | **ordering.** If Tk releases the displaced grab AFTER our handler runs, the restore is undone and B is worse than A — it would look fixed and not be |

⚠ **B'S RISK IS NOT HYPOTHETICAL AND IS THE ONE THING THIS PLAN WILL NOT ASSUME.** Build
`development/probe_444_grab_restore_ordering.py` first: an outer window holding a known grab, an
inner modal `bs.Window`, restore attempted from `<Destroy>`, then read `grab_current()` **and
`grab_status()`** once the dust settles. **If B holds, take B** — it covers the non-blocking
path A cannot reach. **If B loses the race, ship A and file the non-blocking gap**, rather than
shipping a restore that silently does nothing.

⚠ **A `<Destroy>` binding fires for every descendant, not just the window** — guard on
`event.widget is self` or the restore runs once per child widget.

⚠ **Capture BEFORE the grab, always.** `capture_grab`'s own docstring records why: once another
window grabs, the previous holder's `grab_status()` reads `None`, so a kind read afterwards is
always wrong. That is measured, and it is why the pairing is one function rather than two steps.

## Tests — `tests/widgets/public/test_window_modal_grab.py`

**Pin the invariant #440's tests use, which is holder AND kind, never identity alone** — a
downgraded global-to-local grab passed every test before #440, and that is the failure this
family repeats.

1. `test_a_modal_window_hands_the_grab_back_to_its_opener` — outer holds a grab, inner
   `bs.Window(modal=True)` opens and closes, `grab_current()` is the outer **and**
   `grab_status()` is what it was. The headline case.
2. `test_an_app_modal_window_hands_back_a_GLOBAL_grab_as_global` — the kind half, which is the
   part identity-only assertions miss.
3. `test_the_outermost_modal_window_restores_nothing` — nothing held the grab, so nothing is
   re-grabbed. `restore_grab(None)` is already covered for dialogs; this pins the window path.
4. Whichever of A/B the probe selects, a test that **exercises that path specifically** — the
   non-blocking `show()`/`destroy()` pair if B, and if A, a test asserting the blocking path and
   an `xfail`-free note recording that non-blocking is not covered.

⚠ **`grab_set_global()` GRABS THE WHOLE SCREEN AWAY FROM THE TEST RUNNER.** #440's tests solved
this — `test_dialog_nested_modality.py:321-340` drives `restore_grab` against a **recording
stub** that logs which call was made without taking a real grab. **Reuse that shape for the
global arm; do not take a real global grab in the suite.**

**Control, before committing:** revert `toplevel.py` alone and confirm the new tests fail **on
the grab state** — `grab_current()` is `None`, or the kind came back `local` where it was
`global` — and not on an import error or a missing attribute. A pre-fix `AttributeError` proves
nothing.

## Boundary of the completeness claim

Run these and record the output in the review, rather than asserting the conclusion.

- `grep -rn "grab_set" src/bootstack/ --include=*.py` — bounds who takes a grab at all.
- `grep -rn "capture_grab\|restore_grab" src/bootstack/ tests/ --include=*.py` — bounds who
  pairs correctly after the move, and proves the `dialog.py` import still resolves for the eight
  test call sites and `datedialog.py`.
- `grep -rn "grab_release" src/bootstack/ --include=*.py` — anything releasing outright rather
  than handing back is a sibling of this defect.

## Out of scope — file, do not fix

- **`_core/capabilities/grab.py`'s `grab_set`/`grab_set_global`** are the capability methods a
  caller invokes deliberately. They are not a policy site and must not start capturing on their
  own — that would restore grabs behind the back of every caller, including ones that want the
  grab kept.
- **The non-blocking path, IF the probe rejects B.** File it; do not force B through.
- **#207, #422, #447** — the rest of the old `0.3.x` line, now on `0.4.x — Patch line`.
