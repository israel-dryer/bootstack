# REVIEW.md — `fix/formdialog-select-value-428`

## Round 1 — 2026-08-10

**Scope:** `git diff main...HEAD` at `e3556609`. One source file (`src/bootstack/dialogs/_impl/formdialog.py`, +20/−3), one new test file, CHANGELOG, plus `PLAN.md` / `REVIEW-BRIEF-428.md` / three probes. Per the protocol the reviewer did not read `PLAN.md` or `REVIEW-BRIEF-428.md`.

**Fix step:** same session, at the maintainer's instruction to fix everything rather than blockers only. Pre-fix SHA for round 2 scoping is **`e3556609`**.

### Verification the review ran

- **The fix is real and the tests are non-vacuous.** Restoring `main`'s `formdialog.py` under the new tests: 3 failed / 2 passed, failing with the right symptom (`assert 'Two' == 2`). Branch restored: 5 passed.
- **Every write to `_dialog.result` traced.** `Dialog._create_standard_buttons.make_command` calls the spec command, then `if s.result is not None: self.result = s.result`. `_wrap_button_commands` forces `closes=False` on every non-cancel button, so every data-token result (`ok`/`submit`/`save`) passes through `auto_command`/`wrapped_command` first. There is no path that stamps a data token without also capturing `_submitted_data`. The fix has no result-loss hole.
- **`Form.data` returns `dict(self._collect_data())`** and `Form.__init__` copies its `data=`, so the snapshot is a real copy with no aliasing back into the caller's dict.
- **The read-after-teardown mechanism confirmed** at `form.py:889-895`: `widget.value` raises on a destroyed editor and falls back to `self._variables[key].get()`, which is string-backed.

---

### F1 — `tests/widgets/public/test_formdialog_result_value.py:134` — should-fix

**`test_a_reshown_dialog_does_not_report_the_previous_entries` did not cover the guard it names.** Measured: deleting both `self._submitted_data = None` lines from `show()` left all 5 tests passing.

**Root cause.** The cancel path can never reach `_submitted_data` — `_resolve_result` short-circuits on `dialog_result is None` first, and a cancel button leaves `_dialog.result` at the `None` that `Dialog.show()` set. The reset is only load-bearing when `_dialog.result` holds a data token that *this* run did not capture. The docstring's stated control ("cancelling the second run would hand back the first run's data") is not the mechanism. Same shape as #417's `test_group_chevron_tracks_double_click`.

**Suggested minimal change.** Drive the case that needs the guard: press OK on a form that fails validation (`make_command` stamps `result = "ok"` regardless of the wrapper's early return, and the forced `closes=False` keeps the window open), then close via the X.

**Resolved.** Rewritten to that mechanism — a second `required` field left empty in run two, `_press(impl, cancel=False)`, a precondition asserting the dialog is still open, then `impl._dialog._on_close_request()`. The docstring now says outright that cancelling is *not* the mechanism. Control: with the reset deleted, **1 failed / 4 passed**, failing `assert {'k': 3, 'r': 'filled'} is None`.

### F2 — `tests/widgets/public/test_formdialog_result_value.py:44` — should-fix

**No hard fallback: a failure inside the timer hung the whole suite instead of failing.**

**Root cause.** If `impl.form is None` the helper returned early, and if `fill(...)` raised (e.g. a `form._widgets["k"]` KeyError after a rename) Tkinter printed the traceback and swallowed it. Either way nothing closed the dialog and the modal `wait_window` never returned. `_cancel`'s `dismiss` had the same exposure if `button.command()` raised before the unconditional destroy. The sibling file solves exactly this at `test_dialog_result_subscription.py:132` with a `force_close` timer.

**Suggested minimal change.** Add the `force_close` backstop.

**Resolved.** Both: a 10 s `force_close` timer, *and* the action is wrapped so an exception destroys the toplevel and is re-raised after the modal loop unwinds — so a broken helper now fails immediately with its own traceback rather than after a 10 s stall.

### F3 — `tests/widgets/public/test_formdialog_result_value.py:53` — should-fix

**Fixed 200 ms delay where the repo's own precedent polls for a mapped toplevel.**

**Root cause.** `Dialog.show()` runs `_build_content()` (which for a `FormDialog` reaches `_schedule_initial_layout` → `top.update()` on win32, pumping the loop) and then `_position_dialog()` (another `update()` at `dialog.py:598`, before `deiconify()` at 599) *before* `grab_set()`/`wait_window()`. If the build exceeds 200 ms under a loaded shared-root run, `press_ok` destroys the toplevel mid-build; `_position_dialog`'s `if not self._toplevel: return` does not catch it, because a destroyed Toplevel object is still truthy, so `geometry()`/`update_idletasks()` raise `TclError` out of `show()`. `test_dialog_result_subscription.py:111` documents this precise hazard.

**Suggested minimal change.** Poll instead of firing on a fixed delay.

**Resolved.** `_drive()` polls (50 ms, 200 attempts) until `top.grab_current() is top`. `grab_set()` is the last thing `show()` does before it starts waiting, which puts the barrier past both loop-pumping windows — a stricter signal than the sibling's `winfo_ismapped()`, which is reached at `dialog.py:599` with a second centering pass still to come. Side effect: the file got *faster* (1.75s → 1.23s), since the action now fires at 50 ms rather than a padded 200 ms.

### F4 — `tests/widgets/public/test_formdialog_result_value.py:53` — nit

**The `after` job was never cancelled.**

**Root cause.** If `show()` raised or returned before the timer fired, the job stayed queued on the **session-shared** root and fired during a later test, where `press_ok`/`dismiss` would destroy or press a button on whatever dialog was then live. `test_dialog_result_subscription.py:143-151` cancels its pending jobs in a `finally` for this exact reason.

**Suggested minimal change.** Track the job ids and cancel them in a `finally`.

**Resolved.** `_drive()` accumulates every id (including the re-scheduled poll attempts) in `pending` and cancels them in a `finally` around `dialog.show()`.

### F5 — `src/bootstack/dialogs/_impl/formdialog.py:519` — should-fix

**A cancel button with a custom `command` returned the form data, contradicting the new CHANGELOG line.**

**Root cause.** `wrapped_command` skipped validation for `role == "cancel"` but then unconditionally ran `self._submitted_data = self.form.data` and `self._dialog.result = btn.result if btn.result is not None else self._submitted_data`. A cancel button's `result` is `None`, so `_dialog.result` became the data dict, which `_resolve_result` passes straight through as a non-string. `FormDialog(buttons=[DialogButton(text="Cancel", role="cancel", command=fn)])` therefore returned the entered data where the user cancelled. The behavior is pre-existing, but the diff rewrites this exact statement and the CHANGELOG now asserts "Cancelling still returns `None`" — which held only for the default, command-less Cancel.

**Suggested minimal change.** Guard the capture on `btn.role != "cancel"`.

**Resolved.** `if self._dialog and btn.role != "cancel":`, mirroring the early return `auto_command` already does for cancel. New test `test_a_cancel_button_with_its_own_command_still_returns_none`. Control: with the guard removed, **1 failed / 5 passed**, failing `cancelling returned the entered data: {'k': 1}` with its "the custom command ran" precondition passing first. CHANGELOG left unchanged — its claim is now true unconditionally rather than needing to be narrowed.

---

### Checked and clear (not findings)

- **`show(modal=False)`** skips `wait_window` entirely, so `_resolve_result` runs while the dialog is still open and `result` stays `None` forever. Identical before and after this diff, so not a regression — though it does make the new comment's "the dialog and every editor in it are already destroyed" untrue on that path.
- **The `DataTable` consumer** (`tableview.py:1781`) is safe: `result is None` is handled before `dict(data)`, and the `"delete"` token still bypasses `_DATA_RESULTS`.
- **Non-ASCII in the two probes** is confined to comments and docstrings and never reaches `print()`, so the cp1252 console trap from #430 does not apply.
- **CHANGELOG** is a single unwrapped line and correctly re-creates `## [Unreleased]` with no link definition.

### Incidental observation, not actioned

A custom button `command` is handed the **impl** `FormDialog`, not the public wrapper — `test_a_cancel_button_with_its_own_command_still_returns_none` asserts on `dialog._internal` because of it. A public callback receiving an internal object is its own issue; deliberately out of scope for this branch.

---

### Post-fix verification

- `py -3.12 -m pytest tests/widgets/public/test_formdialog_result_value.py` → **6 passed**.
- Against `main`'s `formdialog.py`, the six fail as **4 failed / 2 passed** with the right symptoms: `'One' == 1`, `'Two' == 2`, `{'k': 1}` returned from a cancel, and `'Three' == 3` at the reshown test's precondition.
- Full `py -3.12 tests/run_gui.py` — **exit 0, all legs passed**: widgets+CLI shared root **938 passed / 14 skipped** (52 deselected), data **125 passed / 4 skipped**. `main` alone is 932/14 and 125/4; this branch adds exactly the 6 tests above.

---

## Round 2 — 2026-08-10

**Scope:** `git diff e3556609` (the round-1 fix diff) plus the working tree. Run via `/code-review` in a fresh session.

**Fix step:** same session. The maintainer scoped the fix to all four findings plus the root cause behind F6, which was filed as **#437** and planned in `PLAN.md`.

### Verification the review ran

- New suite: **6 passed**. Against `main`'s `formdialog.py`: **4 failed / 2 passed** — non-vacuous, failing behaviorally.
- Against committed `HEAD` with the uncommitted cancel guard reverted: `test_a_cancel_button_with_its_own_command_still_returns_none` fails with `cancelling returned the entered data: {'k': 1}`. The guard is load-bearing.
- `FormDialog.result` for a date field returns `datetime.date(2026, 3, 4)`, confirming the CHANGELOG's non-select claim.
- `Form.__init__` copies `data=`, so `FormDialog._data` is not mutated between shows — the re-show test's premise holds.

### F6 — `src/bootstack/dialogs/_impl/formdialog.py:240` — blocking

**A stale *action* token survives a failed validation plus a Cancel, and destroys user data.** The round-1 fix closes this for `ok`/`submit`/`save` via the `_submitted_data` reset, but the `return dialog_result` branch has no equivalent guard.

Measured with `buttons=[Cancel, {"text": "Delete", "result": "delete"}, "Save"]` and a `required` field left empty: pressing Delete runs `auto_command`, which early-returns at `validate()`, yet `make_command` still stamps `self.result = 'delete'` and the forced `closes = False` leaves the window open. Cancelling then closes without clearing it — `FormDialog.result == 'delete'`. Probe: `after Delete press: dialog.result='delete', open=1` → `FormDialog.result after cancel = 'delete'`.

`DataTable._open_form_dialog` uses exactly this shape (`tableview.py:1759` builds the button, `:1787` acts on it), so a user who is refused a delete and then cancels **loses the record**.

**Root cause.** Two of them, and the review named the first. (a) `make_command` discards the command's return value, so `FormDialog`'s "this press was refused" signal is structurally invisible to the layer that owns the result. (b) Validation is gated on `role != "cancel"`, which treats an action button as a data submission — so the refused press should never have happened at all. Filed as **#437**; see `PLAN.md`.

**Resolved.** Both root causes, per `PLAN.md` #437. `make_command` now honors a `False` return from the button's command, so a refused press is never stamped rather than being cleared after the fact; and `_button_submits` replaces the role test, so the delete is not refused in the first place. Control: `test_a_refused_press_leaves_no_result_behind` fails against the reverted logic with `cancelling performed the refused action: 'delete'`.

### F7 — `src/bootstack/dialogs/_impl/formdialog.py:521` — should-fix

**The new `btn.role != "cancel"` guard also disabled the `closes is False` self-destroy**, so a cancel button declared `closes=False` with a command never closes. Measured with `DialogButton(text="Cancel", role="cancel", closes=False, command=fn)`: at committed `HEAD` the press closes the window; with the guard it does not, and `make_command` skips its own destroy too because `closes` is False, so `show()` blocks until the user hits the X.

**Suggested minimal change.** Narrow the guard to the capture/result assignment, leaving the destroy branch as it was.

**Resolved.** The destroy moved back out of the guard. Control: `test_a_cancel_button_that_declares_closes_false_still_closes` fails against the nested version with `the dialog stayed open; show() would block until the X was used`.

### F8 — `src/bootstack/dialogs/_impl/formdialog.py:523` — should-fix

**`wrapped_command`'s non-cancel capture — one of the two changed capture sites — has no test coverage.** All five dialog tests use default or command-less submit buttons, so every submit press goes through `auto_command`; the only test reaching `wrapped_command` exercises the *skip* path. A regression that dropped or mis-ordered the capture at line 523 would pass the whole suite.

**Suggested minimal change.** A `DialogButton(role="primary", result="ok", command=...)` variant of the first test.

**Resolved.** Added as `test_a_submit_button_with_its_own_command_captures_the_value`. Control against `main`'s `formdialog.py`: fails with `the command path lost the value: {'k': 'Two'}` - the #428 symptom, on the branch the suite never entered.

### F9 — `REVIEW-BRIEF-428.md:1` — nit

**Branch-scoped artifact committed at the repo root.** Every prior brief lives in `development/` (`review-417-double-click.md`, `review-421-click-focus.md`, `review-brief-427-capture.md`); the root is reserved for `CLAUDE.md` / `PLAN.md` / `REVIEW.md` / `REVIEW-PROTOCOL.md` / `CHANGELOG.md` / `CONTRIBUTING.md` / `README.md`.

**Resolved.** Moved to `development/review-brief-428-formdialog.md`.


### Round 2 controls - every new test observed failing

`development/` carries no probe for this; the control was run by reverting the logic in place (script kept at the session scratchpad) with each revert asserting it matched, so a silently-missed revert could not produce a control that proves nothing. That guard earned its keep twice: the first scripted attempt matched nothing because these two sources are **CRLF** while the test file is **LF**, and a second, partial attempt reported only 2 of 5 failures.

| test | against reverted logic |
|---|---|
| `test_an_action_button_runs_on_a_form_that_fails_validation` | FAIL - `the delete press was refused: the dialog is still open` |
| `test_a_refused_press_leaves_no_result_behind` | FAIL - `cancelling performed the refused action: 'delete'` |
| `test_submits_true_validates_a_button_the_tokens_cannot_describe` | FAIL - `assert 'apply' is None` |
| `test_submits_false_skips_validation_but_still_returns_the_data` | FAIL - `submits=False still validated, or lost the data` |
| `test_a_cancel_button_that_declares_closes_false_still_closes` | FAIL - `the dialog stayed open` |
| `test_a_data_token_button_still_validates` | pass (no-regression, by design) |
| `test_a_button_with_no_result_token_still_validates` | pass (no-regression, by design) |
| `test_a_submit_button_with_its_own_command_captures_the_value` | pass here; FAILs against `main` with `{'k': 'Two'}` |

⚠ **`test_an_action_button_runs_on_a_form_that_fails_validation` was VACUOUS on its first draft and the control is the only reason that is known.** Asserting `result == "delete"` alone passed against the unfixed code: the refused press still stamped `'delete'`, the window stayed open, and `_drive`'s ten-second `force_close` destroyed it, so the assertion was satisfied without the delete ever running. The tell was the run time - 21.78s against 1.8s, two `force_close` timeouts. It now asserts the dialog **closed** as a result of the press, which is what separates "the action ran" from "a stale token happened to match". Same shape as #417's `test_group_chevron_tracks_double_click`.

### One design correction found by a failing test, not by review

The first implementation keyed BOTH validation and the data capture to `_button_submits`. `test_submits_false_skips_validation_but_still_returns_the_data` then failed with `None`: `submits=False` on a `save` token skipped the capture, but `_resolve_result` still maps that token to the snapshot, so the caller got nothing from a press that had closed the dialog.

Split into two predicates. `_button_returns_data` answers the same question `_resolve_result` asks, so the capture cannot disagree with the read; `_button_submits` governs validation alone and is what `submits` overrides. That is what makes `submits=False` on a data token mean "return this without checking it" - a Save draft - rather than "return nothing".

---

## Round 2 addendum - #438 supersedes part of F7

Filed as **#438** and fixed on this branch at the maintainer's direction: it is release-blocking, and it touches the same function #437 rewrote, so folding it in means one review pass covers both instead of reopening the same lines.

### ⚠ F7's destroy half is REVERSED, deliberately

F7 found that #437's new `btn.role != "cancel"` guard had stopped a `closes=False` cancel button with a command from closing, and asked for the previous behavior back. That was a **regression** argument, not a correctness one - and restoring it is what exposed that the three paths never agreed at all:

| declaration | before #438 |
|---|---|
| `closes=False` on a non-cancel button | closed anyway - declaration discarded |
| `closes=False` on a cancel button WITH a command | closed |
| `closes=False` on a cancel button with NO command | did not close |

Root cause: `_wrap_button_commands` writes `button.closes = False` as an internal marker meaning "`Dialog` must not close this one, I close it after validating", then reads that same field back to decide whether to close. The framework's marker and a caller's declaration are the same value by then. Same shape as the #437 defect it sits next to, where `result=None` meant both "my answer is nothing" and "do not touch the result".

Under the flag's documented meaning the pre-#437 behavior was itself wrong, so all three arms now agree that `closes=False` does not close. **F7's capture guard stands; only its destroy half is superseded.** The test asserting the old behavior is inverted and renamed to `test_closes_false_is_honored_on_a_cancel_button`, with the reversal stated in its docstring so a later reader does not read it as a regression reintroduced.

A second defect found with it: `_normalize_buttons` passed caller-supplied `DialogButton` instances straight through, so that write **mutated the caller's own object**. It takes a `dataclasses.replace` copy now.

### Verification

`development/probe_437_closes_false_cancel.py` (extended to four arms) after the fix:

```
arm 1: cancel closes=False WITH command      closed = False
arm 2: cancel closes=False NO command        closed = False
arm 3: NON-cancel closes=False               closed = False

CONSISTENT: closes=False -> closed=False on all three paths

arm 4: caller's DialogButton mutated by construction = False
```

Controls via `development/probe_438_control_revert.py`, which asserts each revert matched:

| test | against reverted logic |
|---|---|
| `test_closes_false_is_honored_on_a_cancel_button` | FAIL - `closes=False still closed the dialog` |
| `test_closes_false_is_honored_on_a_submit_button` | FAIL - `closes=False was discarded on a submit button` |
| `test_a_caller_supplied_button_spec_is_not_mutated` | FAIL - `the caller's command was rewritten` |

### Not affected

The only two in-tree `closes=False` uses are `datedialog.py:263` and `query.py:99`. Both are plain `Dialog` wrappers rather than `FormDialog`, so `_wrap_button_commands` never sees them; both also pair `closes=False` with a command that closes the window itself, which is the contract this change makes uniform. Neither command can return `False`, so #437's `make_command` veto does not affect them either - both are typed `-> None`.

### Still open for the next reviewer

The #438 issue raises, and this branch does NOT settle, whether `closes=False` should be **rejected** on a submit button rather than honored - i.e. whether the framework owning the close for validated buttons is the intended contract. Honoring it was the smaller change and matches the documented meaning.

### ⚠ #437 made round 1's F1 fix unreachable - flagged, not silently left

F1 rewrote `test_a_reshown_dialog_does_not_report_the_previous_entries` around the one mechanism that could reach the `_submitted_data = None` reset: `make_command` stamping the button's result even when the wrapper refused the press, so run two could close carrying a data token it never captured.

**#437's veto removes exactly that mechanism.** A refused press returns `False`, the stamp is suppressed, and every write to `dialog.result` is now paired with a capture in the same call. Measured with `check_reset_still_load_bearing.py`: deleting the reset line from `show()` leaves **all 16 tests green**.

So the reset is dead code, and the test that named it was passing for a reason its docstring no longer described - the #417 failure mode, arriving by a different route (the code moved out from under a correct test rather than the test being wrong when written).

**Decision: keep the reset, correct the docstring.** The reset defends the invariant *"a result write is always paired with a capture"*, which nothing enforces structurally and which a future change could break silently. Removing it would make that invariant implicit. But the docstring now states outright that the veto is what carries the test, that deleting the reset changes nothing, and that **no test covers the reset itself because nothing can currently reach it**.

Left for the next reviewer to weigh: whether unreachable defensive code with no coverage should stay at all, or whether the invariant deserves a structural guard instead.
