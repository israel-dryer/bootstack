# REVIEW — #476 round 1 (`SelectButton` fires `on_change` twice)

Branch `fix/selectbutton-double-change-476`, head `f6a5631a`. Base `main` at `85b051be`.
**Round cap 2, this is round 1 (spent 1).**

Gate 1: `git diff 85b051be..HEAD -- src/` is non-empty (5 lines in
`_impl/primitives/optionmenu.py`), so a round is owed.

Reviewed from a `git worktree` at the branch head with `PYTHONPATH` pointed at the
worktree's `src` and absolute test paths, provenance printed. Windows box, `py -3.12`,
`matplotlib` and `pandas` both present.

## Verdict

**The production change is correct. No blocking findings.** One should-fix in the tests,
three notes.

## What was measured, not read

Every claim below is a before/after pair. `BASELINE` = `optionmenu.py` restored from
`85b051be` in the worktree; `FIXED` = the branch head. Probe:
`development/probe_476_review_round1.py`.

```
                                      BASELINE      FIXED
menu-item click -> on_change          2x ['2','2']  1x ['2']
sb.value = '2'  -> on_change          2x            1x
signal write    -> on_change          2x            1x
subscribers on _textsignal
   plain / localized / signal=        2 / 2 / 2     1 / 1 / 1
50x configure(options=)               2             1
50x configure(textsignal=)
   live subs on current signal        1             1     <- insensitive, see finding 1
   orphans left on the 50 replaced    50            0     <- what :368 actually leaked
```

The `<<Change>>` emitted by the menu path is the same write as the programmatic one — a menu item is a `RadioToggle` bound to `variable=self._textvariable` — but it was driven through the real item's `invoke()` rather than assumed. That is what checks the CHANGELOG's "both to a selection made from the menu and to one set in code" against the **old** code rather than against the fix.

**Suite, branch head, worktree, `py -3.12 tests/run_gui.py`: 1573 -> 1579 passed / 22
skipped, 33 legs, exit 0.** The `+6` is exactly the new file; bounded with
`git diff 85b051be..HEAD --stat -- tests/`, which shows no other test file moved.

**A free control:** one suite run went out against BASELINE source by accident (a
`git checkout <sha> -- src` had staged the revert, so `git checkout -- src` restored from the
index). It read `6 failed, 1179 passed` in the shared leg — the six failures being exactly
the new file. **Nothing else in the suite was leaning on the double emission.**

**Control on the new tests:** with the fix reverted, all six fail, and every one fails on the
emission or subscription **count** (`assert ['2','2'] == ['2']`, `assert 2 == 1`) — not on an
`AttributeError` or a missing attribute. No vacuity.

**Order sensitivity:** the shared leg was run 3x; the six new tests passed every time.

## Findings

### 1. `test_rebinding_the_textsignal_replaces_the_subscription` asserts the wrong side of the rebind — should-fix

`tests/widgets/public/test_selectbutton_change_once.py:113`

**Root cause.** The test's name and docstring claim it drives `optionmenu.py:368`, "the path
that caused #476". Its closing assertion is `len(menu._textsignal._subscribers) == 1` — the
count on the **new** signal. Measured on both arms, that reads **1 on the broken build and 1
on the fixed build**. It cannot fail for #476.

The reason the test goes red in the control is its **first** assertion at `:109`
(`len(...) == 1` right after construction), which is test 5's assertion restated against the
internal. pytest stops at the first failure, so **the control never reaches `:113` at all** —
the rebind claim is untested by the very run that is supposed to validate it.

What the `:368` half of the fix actually repairs is the orphan left behind on the **replaced**
signal, and that is the number that moves: **50 orphans across 50 rebinds on BASELINE, 0 on
FIXED**.

**Suggested minimal change.** Hold the pre-rebind signal and assert it drops to zero:

```python
menu = OptionMenu(app.tk, options=list(DECOUPLED), value="1")
previous = menu._textsignal
assert len(previous._subscribers) == 1

menu.configure(textsignal=bs.Signal("Two"))

# The subscription :368 used to discard: it must LEAVE the signal it was
# bound to, not merely be absent from the new one. 50 -> 0 across 50 rebinds.
assert len(previous._subscribers) == 0
assert len(menu._textsignal._subscribers) == 1
```

**Severity: should-fix, not blocking.** Tests 1-5 cover the production defect and fail
deterministically without the fix; nothing ships broken. But the test as written promises
coverage of `:368` that it does not have, and a record citing it would be citing a refutation
the instrument cannot make.

### 2. The surviving subscription is still never cancelled on destroy — note, pre-existing, FILED AS #479

`optionmenu.py:200-218`. `_bind_id` is created and replaced but never cancelled in a destroy
handler. Measured: destroy an `OptionMenu` bound to an externally held signal, then write that
signal, and `_on_change` runs against a dead widget —
`TclError: bad window path name ".!optionmenu2"` raised **inside the Tk trace callback**,
where the caller cannot see it.

**Not a regression and out of scope.** BASELINE leaks two such subscriptions per widget, the
branch one — the fix strictly improves it. Unreachable from public API since #472 rejects
`textsignal=` at the wrapper, and the internal's own auto-created signal dies with the widget.
Recorded because it is the neighbourhood the fix touches and because #477 passes through here.
**Filed as #479** at the maintainer's request, with the measurement and with
`ValueSignalMixin._bind_value_signal` named as the in-repo exemplar: the public wrapper holds
its subscription id and releases it on destroy, so the internal has a pattern to copy.

### 3. Test 5's structural assertion is a false-alarm surface for a future legitimate second subscriber — note

`test_exactly_one_change_subscription_after_construction` reads
`sb._internal._textsignal._subscribers`. Correct today on every shape measured — plain,
`localize=True` and `signal=` all read 1. The hazard is a future feature that legitimately
adds a second subscriber. `LocalizationMixin._setup_signal_formatting` is the shape of it: it
**replaces** `_textsignal` without re-entering `_bind_change_event`, which on an `OptionMenu`
would silently stop `<<Change>>` altogether. It is unreachable from `OptionMenu` today — the
only `value_format` callers are in `dialogs/_impl/query.py` — so this is a note, not a fix.
The test's docstring already owns the tradeoff explicitly.

### 4. Test 4 drifted from the plan's stated intent — note

`PLAN.md` names it `test_reassigning_options_leaves_one_subscription` and says it should
"prove the rebuild path does not re-add a subscriber". It shipped as
`test_reassigning_options_still_fires_change_once`, asserting the emission count. Equivalent
in practice — measured, 50 `configure(options=)` reassignments leave **1** subscriber on FIXED
and **2** on BASELINE, with no accumulation on either — so no fix. Noted only so the plan and
the file are not read as describing the same assertion.

## Checked and clean

- `git diff main...HEAD -- CLAUDE.md` is **empty**.
- `_bind_id` collides with nothing: `grep -rn "_bind_id" src/bootstack` shows the only other
  uses are `events/_subscription.py`'s slot and the textarea extensions' `_theme_bind_id`.
- `self._bind_id = None` at `:93` precedes every call path, including the one reached from
  inside `super().__init__()` when `textsignal=` is passed — no `AttributeError` window.
- The `Handle` returned by `Signal.subscribe` closes over the signal it was added to, so
  cancelling after `_textsignal` has been replaced removes the subscriber from the **old**
  signal. That mechanism is what finding 1's suggested assertion measures.
- Blast radius confirmed independently of the plan: `_InternalOptionMenu` is constructed in
  exactly one place (`selectbutton.py:99`), and `_bind_change_event` has exactly three lines
  in `src/`, all in `optionmenu.py`.
- No accumulation under churn: 50 `options=` reassignments and 50 `textsignal=` rebinds both
  settle at 1 subscriber.
- Docs need no change; `docs/widgets/selectbutton.rst` never documented the double fire.

## Out of scope, agreed with the plan

- `NumberField` / `DateField` emitting **zero** `<<Change>>` on a programmatic set while
  `Select`, `TimeField` and `SelectButton` emit one. The maintainer's disposition
  (2026-08-26) is **keep in mind, do not fix, do not file**.
- #477, collapsing the `_impl` layer so the subscribe-then-`event_generate` bridge goes away.

## Resolutions

### Finding 1 — FIXED

`tests/widgets/public/test_selectbutton_change_once.py`. The test now holds the pre-rebind
signal and asserts it drops to **0** subscribers, which is the assertion that separates the
arms (`50 -> 0` across 50 rebinds; `1 -> 1` for the assertion it replaced). Control run: with
`optionmenu.py` restored from `85b051be`, the new assertion fails on its own — verified by
deleting the `:109` assertion so the control reaches `:113` rather than stopping short of it.

### Finding 2 — FILED, no branch change

#479. Pre-existing and out of scope for this branch, which strictly improves it (two leaked
subscriptions per widget before the fix, one after).

### Findings 3, 4 — no action

Notes under stopping rule 2. Nothing in the branch changes.
