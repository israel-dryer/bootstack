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

---

# Round 2 — #437 / #438

Reviewed `git diff 9a55742f..HEAD` at head `065ef56a` (code head `7c2cfde5`). Read the diff, `PLAN.md`'s pre-implementation sections, and the surrounding source; did not read the commit messages.

**Verdict: not blocking.** I read `query.py` and `datedialog.py` line by line against their pre-diff forms and both rewrites are behavior-preserving on every branch I can trace (details in F5). The coverage gap is real and should be closed, but it is not a reason to hold the branch. Findings are ordered by severity.

## F1 — should-fix — `src/bootstack/widgets/_impl/composites/form.py:993`

**The new `DialogButton.command` veto is honored by `Dialog` and silently ignored by `Form`.**

`DialogButton.command`'s docstring (`dialog.py:90`) now states unconditionally that returning `False` refuses the press. `DialogButton` has two consumers, not one. The second is `Form._build_buttons` → `_make_button_command`:

```python
def command():
    if spec.command:
        spec.command(self)          # return value discarded
    self.result = spec.result if spec.result is not None else self.data
```

`bs.Form(buttons=[...])` is a public path (`src/bootstack/widgets/form.py:55`, documented as accepting `DialogButton` instances). So `bs.Form(buttons=[DialogButton(text="Save", role="primary", command=lambda f: False)])` stamps `form.result` with the entered data even though the command declined — the *exact* "a declined press still records a result" shape #437 removed from `Dialog`, left standing one file over, and now documented as impossible.

Root cause: the contract was written onto the dataclass field but implemented in only one of the two places that call `spec.command`.

Minimal change: in `_make_button_command`, `if spec.command and spec.command(self) is False: return` before the stamp. If the maintainer would rather not extend the veto to `Form`, then the field docstring has to say *where* it applies — otherwise this is #438's own failure mode (a declaration that means different things in different places) reintroduced by the fix for it.

## F2 — should-fix — `src/bootstack/dialogs/_impl/formdialog.py:585`

**A custom action button without an explicit `result=` is still classified as a submit, so #437's reported symptom survives for that shape.**

`_button_returns_data` ends with `return btn.result is None`. So `DialogButton(text="Delete", role="danger", command=lambda dlg: do_delete())` — no `result=`, because the command does the work — is treated as a data submission: `_accept_press` runs `self.form.validate()`, an invalid record fails it, the press is refused, and Delete does nothing. That is the reported defect, unchanged, reached by the most natural way to write an action button that carries a command rather than a token.

`DataTable` escapes only because `tableview.py:1759` happens to pass `{"result": "delete"}`. Nothing tells a user that a `result=` token is what buys them out of validation.

This also makes **`CHANGELOG.md:23`** inaccurate: *"The same applied to any custom action button you added to a `FormDialog`. Validation now runs only for the buttons that actually submit the form."* It runs for any non-cancel button with no `result=`, whether or not it submits.

Minimal change: either treat "has a `command` and no `result`" as an action rather than a submit, or leave the inference as-is and correct the CHANGELOG plus the `FormDialog` docstring to state that an action button must carry a `result=` token. The second is smaller and does not re-open the `submits` question the maintainer closed.

## F3 — should-fix — `src/bootstack/dialogs/_impl/formdialog.py:572`

**`_button_returns_data` and `_resolve_result` *can* disagree, and where they do the stale `_submitted_data` from a previous run leaks out.**

The docstring claims: *"This is the same question `_resolve_result` answers when the dialog closes… Keying the snapshot to it means the capture cannot disagree with the read."* They are not the same question. `_button_returns_data` gives **role** precedence (`if btn.role == "cancel": return False`); `_resolve_result` gives the **token** precedence (`if isinstance(dialog_result, str) and dialog_result.lower() in self._DATA_RESULTS`). They diverge for a cancel-role button carrying a data token.

Scenario: `FormDialog(items=[...], buttons=[DialogButton(text="Close", role="cancel", result="ok"), ...])`. Pressing Close takes no snapshot (`_accept_press` returns early on the role test), `Dialog` stamps `"ok"`, and `_resolve_result("ok")` hands back `self._submitted_data` — `None` on the first run, and **the previous run's entries** on a re-show.

Narrow, but it matters beyond itself: it is a live counter-example to the "measured inert" table for the removed `show()` reset. The reset was inert *for the arms one test exercises*; on this path it was the thing turning a stale snapshot into `None`. The four-way measurement is sound as far as it goes — the conclusion drawn from it ("it changes nothing in any arm") is broader than the measurement supports.

Minimal change: make `_button_returns_data` check the token before the role, so the two agree; or have `_resolve_result` yield `None` when no capture happened during the press that closed the dialog. Either way the docstring's invariant becomes true rather than asserted.

## F4 — should-fix — `src/bootstack/dialogs/_impl/query.py:159`

**`_submit_from_key` cannot fire, and the comment above it states the opposite.**

The comment reads *"A key press has no button behind it, so it closes here."* It does have a button behind it: `Dialog._create_standard_buttons` binds `<Return>` on the **toplevel** to the default button (`dialog.py:543`), and the Submit spec is `default=True`. That is the path Enter actually takes, and it routes through `make_command`, the veto and `Dialog`'s close.

The new closure is bound with `entry.bind(...)` on the **composite frame**. Focus never lands there: `_focus()` (`query.py:167`) prefers `entry.entry_widget`, and every widget `_create_content` can build — `TextEntry`, `NumericEntry`, `DateEntry`, `SelectBox` — inherits `entry_widget` from `field.py:291`. The composite frame is not in the inner entry's bindtags and Tk does not bubble child→parent, so the handler is unreachable. It was equally unreachable before the diff; the diff rewrote it rather than deleting it, and wrote a comment asserting a mechanism that does not exist.

If it ever does become reachable (an entry without `entry_widget`, or a focus change), it is wrong twice over: it does not `return "break"`, so the toplevel `<Return>` binding still runs afterwards and calls `invoke()` on a button inside the toplevel it just destroyed — a background Tcl error Python cannot see; and its close uses a bare `if self._dialog.toplevel:` truth test, the exact check `dialog.py:514` was just changed away from, with a comment explaining why.

Minimal change: delete the `<Return>`/`<KP_Enter>` bindings and let the default-button binding own the key. Deleting is smaller than fixing and removes a comment that documents behavior the code does not have.

## F5 — should-fix — `src/bootstack/dialogs/_impl/query.py:180`, `src/bootstack/dialogs/_impl/datedialog.py:320`

**Both rewritten paths ship with zero coverage.** Confirmed independently of the brief: nothing under `tests/` drives `_on_submit` or `_on_confirm_range` through a press, and the only `DateDialog` test (`test_dialog_result_subscription.py:67`) builds a single-mode dialog and never touches the range footer.

I traced both by hand and believe they are equivalent:

- `query._on_submit` — the `.value` branch keeps `items`-membership rejection → refuse, `result is None` → refuse, otherwise set + accept; the `.get()` branch keeps `_validate` → refuse, otherwise set + accept. The Submit spec has no `result=`, so `Dialog`'s `if s.result is not None` write cannot clobber what `_on_submit` stored.
- `datedialog._on_confirm_range` — same three outcomes as before (no picker → open, incomplete range → open, complete → record + close), and the OK spec likewise has no `result=`.

So this is not blocking. But "verified by reading" is what the branch currently rests on for two of its four source files, and both are cheap to cover with the `_drive`/`_press` pattern already in `test_formdialog_result_value.py`: one test asserting an incomplete range leaves the range dialog open while a complete one closes carrying the tuple, and one asserting a `QueryDialog` submit sets the value and closes. Those two would also have caught F6.

## F6 — nit — `src/bootstack/dialogs/_impl/datedialog.py:332`

**The range-confirm path lost its `grab_release()`.** `_confirm` (line 340) still calls `grab_release()` before `destroy()`; the range OK button now returns to `Dialog`, which destroys without it. Tk releases the grab when the grabbing window is destroyed, so this is almost certainly harmless — but the two close paths in one file now differ for no stated reason, and `_confirm`'s `try/except` around `grab_release` suggests someone once hit a case where it mattered. Either drop it from `_confirm` too (consistent with every other dialog in the tree) or note in a comment why the button path does not need it.

## F7 — nit — `docs/widgets/dialog.rst:68`

**The Guide does not teach the veto.** `DialogButton.command`'s new contract is a user-facing behavior change on a public class, and the Guide is the teaching layer — the API Reference is meant to be a last resort. `dialog.rst`'s "Reading the result" section walks through `result=` and never mentions that a command can now refuse its own press. Add a short subsection (validate in the command, `return False` to keep it open) using the example the CHANGELOG already contains.

## F8 — nit — `src/bootstack/dialogs/_impl/formdialog.py:618`

**A removed kwarg produces a worse error through `FormDialog` than through `Dialog`.** `Dialog._normalize_buttons` (`dialog.py:378`) wraps a bad mapping in `ValueError: Invalid button mapping {...}: ...`. `FormDialog._normalize_buttons` does a bare `DialogButton(**btn)`, so the common upgrade case — `FormDialog(buttons=[{"text": "Apply", "closes": False}])` — raises `TypeError: __init__() got an unexpected keyword argument 'closes'` with no dialog context and no pointer to the replacement. Given `closes` was just deleted, this is the error users of the removal will actually hit. Mirror `Dialog`'s wrapping.

## Checked and clear — not worth re-deriving

- **The `winfo_exists()` destroy guard covers every path into it.** The three ways to reach `make_command`'s `cmd()` are the button widget, the toplevel `<Return>` → `default_button.invoke()`, and `<Escape>` → `cancel_button.invoke()`. All three go through the same closure, `winfo exists` returns 0 on a destroyed path rather than raising, and the FormDialog wrapper is installed once in `__init__` (not per-show), so it cannot stack.
- **No stale-token leak on re-show through the ordinary paths.** `Dialog.show()` already resets `self.result = None` (`dialog.py:330`), so removing `FormDialog`'s `_submitted_data` reset cannot resurrect a previous run's snapshot via a leftover `Dialog.result`. The only remaining route is F3's role/token disagreement.
- **`replace(btn)` is safe.** `DialogButton` has no `init=False` fields, `_wrap_button_commands` runs once on the copies, and `Dialog._normalize_buttons` never mutates a spec — so the copy is sufficient and nothing double-wraps.
- **`Form.data` returns `dict(self._collect_data())`**, a fresh dict, so the snapshot is a real copy and not an alias that keeps mutating.
- **The other three in-tree `Dialog` commands cannot trip the veto**: `filterdialog._on_ok`, `fontdialog._on_submit` and `message._make_command_callback` all return `None` on every path, and the last one discards the user's return, so `MessageBox(command=...)` is unaffected.
- **`_press` / `_press_text` pair correctly.** `_create_standard_buttons` iterates `reversed(self._buttons)`, and the only children of `_footer` are the buttons (the `_Separator` is packed into the toplevel), so `zip(reversed(specs), footer.winfo_children())` is a sound pairing and the length assertion protects it.

---

## Round 2 fix step — 2026-08-10

Same session as the review, at the maintainer's direction to apply the findings rather than the blockers only. All eight are handled. Controls for every new test are committed at `development/probe_437_review2_controls.py`; the three cross-platform facts the fixes rest on are measured in `development/probe_437_review2_fixes.py`.

### F1 — resolved by extending the veto to `Form`

`_make_button_command` returns before the stamp when the command returns `False`, matching `Dialog`. `DialogButton.command`'s field docstring now says the contract applies wherever the specifications are used, `Form` included, rather than naming only the dialog. Control: `test_a_form_button_command_can_refuse_its_press` fails against the reverted line with `a refused press recorded {'k': 'typed'}`, and a paired control test proves a `Form` that recorded nothing at all would not pass it.

### F2 — resolved by documentation, NOT by reclassifying the button

⚠ **The reviewer's first option was rejected, and the reason should not be re-litigated.** Treating "has a `command` and no `result`" as an action would change what such a button returns: `_record_press` would stop capturing, and `FormDialog(buttons=[DialogButton(text="Apply", command=fn)])` — which returns the entered data today — would start returning `None`. #437's plan lists that arm under "keeps today's behavior exactly". So the inference stands and the contract is stated instead: **a result token is what makes a button an action**. Written in three places a caller actually reads — the public `FormDialog(buttons=...)` docstring, `_button_returns_data`, and the CHANGELOG line the review flagged, which no longer claims validation is scoped to the buttons that submit without saying what makes a button one.

### F3 — resolved by reordering the predicate, which is what makes its docstring true

`_button_returns_data` checks the result token BEFORE the role, so it asks the question in the same order `_resolve_result` does. A `role='cancel', result='ok'` button now captures its own run instead of resolving against whatever the previous run left in `_submitted_data`.

⚠ **This closes the leak without re-adding the `show()` reset that #438 removed** — worth stating, because that removal rested on a four-arm measurement and re-adding it would read as the measurement having been wrong. It was not wrong; it was narrow. With the ordering fixed, every write of a data token to `dialog.result` is again paired with a capture in the same press, which is the invariant the reset was defending. Control: `test_a_cancel_role_button_carrying_a_data_token_captures_its_own_run` fails against the reverted order with `run two reported run one's entries: {'k': 3}`.

### F4 — resolved by deleting the dead binding AND wiring the key it was reaching for

The `_submit_from_key` closure and its two bindings are gone, and the comment asserting a mechanism that does not exist went with them. Measured before deleting (`probe_437_review2_fixes.py` arm 2): focus lands on a `TEntry` whose bindtags are `[the entry, 'TEntry', the toplevel, 'all']` — the composite frame is not among them, so the handler was unreachable, exactly as the review said.

⚠ **Deleting it alone would have left a real gap, and this is the cross-platform half.** `Dialog` bound only `<Return>` on the toplevel, and `KP_Enter` is a separate keysym from `Return` on Windows, X11 and Aqua alike — so the keypad Enter key did nothing in any dialog in the framework. Measured, arm 3. Both sequences are bound now, in one loop, so they cannot drift apart. One physical key yields one keysym, so this cannot double-invoke.

⚠ **`<KP_Enter>` CANNOT BE SYNTHESIZED on Windows Tk 8.6.15 — do not write a behavioral test for it.** `event_generate("<KP_Enter>")` produces an event with keysym `'??'` and keycode `0`: a `<Key>` catch-all sees it, `<KP_Enter>` does not, and passing `keycode=13` makes it arrive as `Return` instead. The first draft of that test looked sound — its `winfo_ismapped` precondition passed — then failed on the result after the harness's ten-second timeout. It asserts the binding structurally now, with `test_enter_presses_the_default_button` carrying the behavior through the key that can be driven. Same family as the standing "assert the INVARIANT, not the symptom" rule.

### F5 — resolved with four tests, two of which were VACUOUS until the control ran

`tests/widgets/public/test_dialog_press_contract.py` covers both arms of `query._on_submit` and both of `datedialog._on_confirm_range`, through the real footer button.

⚠ **The two accept-path tests passed against deliberately broken source, and the tell was the clock: `1 passed in 10.78s`.** Both routines write the result BEFORE returning, so a version that refuses every press leaves the value standing, the window open, and `_drive`'s `force_close` tears it down ten seconds later — the result assertion is satisfied without the press ever having closed anything. That is #417's chevron test and #437's `test_an_action_button_runs_on_a_form_that_fails_validation` for the third time. Both now assert the dialog closed **at the press**, where it happens. All eight controls fail correctly.

⚠ Note for whoever adds the next refusal test: the other two refusal branches in `query._on_submit` open a `MessageBox`, which would stack a second modal inside the first and stall the run. A date query with nothing entered is the one refusal reachable without it.

### F6 — resolved by measuring, then stating the reason in the docstring

Tk releases a grab held by a window when that window is destroyed — measured, arm 1: `grab_current()` is `None` after the destroy. So the range path needs no `grab_release()` of its own, and `_confirm` keeps its own because it destroys the window itself, where the call at least documents intent. `_on_confirm_range`'s docstring now says both, so the difference is no longer unexplained.

### F7 — resolved with a Guide subsection

`docs/widgets/dialog.rst` gains **Refusing a press** after *Reading the result*: validate in the command, `return False` to keep the dialog open, plus a note that it is per press rather than per button and that Enter takes the same path. Teaching layer, per the standing rule that the API Reference is a last resort.

### F8 — resolved by mirroring `Dialog`

`FormDialog._normalize_buttons` wraps a bad mapping in `ValueError: Invalid button mapping {...}: ...`. Control: `test_a_removed_kwarg_names_the_button_it_came_from` fails against the bare construction with the context-free `TypeError` the review predicted.

### Verification — measured 2026-08-10, working tree on `fix/formdialog-select-value-428` at `065ef56a` plus these changes

| leg | result |
|---|---|
| widgets+CLI, shared root | **957 passed / 14 skipped** (52 deselected) |
| data | **125 passed / 4 skipped** |
| `py -3.12 tests/run_gui.py` | **exit 0, all legs passed** |

The branch head collected 947 in the shared leg; these changes add exactly 10 tests — 8 in the new file, 2 in `test_formdialog_result_value.py`. Docs: `rm -rf docs/_build && sphinx-build -b html docs docs/_build/html -W --keep-going` → **exit 0, zero warnings**. A `-n` build reports 89 warnings, **all pre-existing and none on `docs/widgets/dialog.rst`** — dangling xrefs in autogenerated stubs (`ContentBuilder`, `FooterBuilder`, `ButtonSpec`, the `forms.rst` item classes), not this branch's to fix.

### Still open for the next reviewer

- **`FormDialog` infers "action" from the presence of a result token, and nothing makes a caller aware of that.** F2 is closed by documentation, which is the smaller change and does not re-open the `submits` field the maintainer declined. If action buttons written without a token keep arriving, the inference is the thing to revisit — not the CHANGELOG.
- **The keypad Enter binding has no behavioral coverage on this box.** It is assertable structurally here; a Linux run could drive it for real, since X11 carries `KP_Enter` in its keymap. Worth adding if #380's CI leg lands.

# Round 3 — #428 / #437 / #438

Reviewed `git diff 065ef56a..HEAD` at head `eab58129`. Read the diff, `PLAN.md`, and round 2's F1–F8; did not read the commit messages or the `## Round 2 fix step` section until after forming a view. Findings are ordered by severity.

**Verdict: blocking.** Round 2's eight findings are all genuinely closed. But the scope the fix step added on its own initiative — the `<KP_Enter>` binding, which the brief itself nominates as "the thing to judge first" — is built on a premise that does not hold, and it makes a single Enter press invoke a footer button **twice**. That is the branch's own headline feature (a command refusing its press) misbehaving on the keyboard path the new documentation points readers at. Measured, with controls, in `development/probe_437_round3.py`.

Convergence: round 1 found 5, round 2 found 8, round 3 finds 7 — not materially fewer, and the one blocking finding is in scope the review did not ask for. The right read is not "loop again": it is that R1/R2 should come off this branch as their own issue, at which point what remains is a clean #428/#437/#438 branch with four small findings against it.

## R1 — blocking — `src/bootstack/dialogs/_impl/dialog.py:550`

**One Enter (or keypad Enter) press invokes a footer button twice, and the second invoke can press a *different* button than the one that had focus.**

The comment above the loop reasons that "One physical key produces one keysym, so binding both cannot invoke the button twice." That is true of the two toplevel bindings and beside the point: the second invoke does not come from the other sequence, it comes from a **`TButton` class binding that was already there**. `_runtime/app.py:141-153` installs `button_default_binding` on `bind_class("TButton", "<Key-Return>")` **and** `bind_class("TButton", "<KP_Enter>")`, and it calls `widget.invoke()` on whichever button has focus. `Dialog._create_standard_buttons` calls `default_button.focus_set()` (`dialog.py:544`), so a dialog opens with a ttk button focused. The focused button's bindtags are `['.!toplevel.!frame.!button', 'TButton', '.!toplevel', 'all']` — measured — so a real key press runs the class binding *first* and the new toplevel binding *second*.

Before #437 that was invisible: the first invoke always destroyed the toplevel, and Tk abandons the remaining bindtags once the event's window is gone. **The veto is what makes the second dispatch survive** — a command returning `False` leaves the window standing, so the toplevel binding runs on a live dialog.

Measured (`development/probe_437_round3.py`):

| arm | what | calls |
|---|---|---|
| control | toplevel `<Return>`/`<KP_Enter>` unbound, class binding only | **1** |
| shipped | as on this branch, command returns `False` | **2** |
| shipped | command returns `None` (accepts) | 1 — the destroy aborts the second dispatch |

And the worse shape, same probe: a footer of `Apply` (`role='secondary'`, command returns `False`) plus `OK` (`default=True`). Focus `Apply`, press Enter once:

```
log:    ['apply', 'ok']
open:   0          <- the dialog closed
result: 'ok'       <- the user pressed Apply
```

So pressing Enter on a button that *declines* its press submits the dialog through a different button and hands the caller that button's result. The user-visible version of arm 2 is milder but still wrong: a Save command that validates and calls `bs.alert(...)` before returning `False` shows the alert twice per Enter.

Root cause: a `bind` on the toplevel is additive to the class binding on the widget that actually has focus, and nothing suppresses the first when the second applies.

Minimal change: make the toplevel handler stand down when the event already reached a footer button, since the class binding has handled it — capture the footer's buttons and `if e.widget in buttons: return` before `b.invoke()`. That keeps Enter working while focus is in an entry (the case the toplevel binding exists for) and removes the double dispatch. Deleting the toplevel bindings instead is *not* equivalent: it would break Enter in `QueryDialog`, where focus is deliberately moved off the button.

## R2 — should-fix — `CHANGELOG.md:27`, `src/bootstack/dialogs/_impl/dialog.py:545`

**The keypad-Enter claim is broader than the measurement behind it.** The entry says "Only the main Enter key did… so a dialog filled in from the number pad had to be finished with the mouse or with the other Enter", and the code comment says "measured: without it the key does nothing at all in a dialog."

Verified at runtime: `root.bind_class('TButton')` returns `['<<Invoke>>', '<B1-Enter>', '<B1-Leave>', '<Button-1>', '<ButtonRelease-1>', '<Enter>', '<Key-KP_Enter>', '<Key-Return>', '<Leave>']`. `<Key-KP_Enter>` is bound at class level and invokes the focused button. So in every dialog that leaves focus where `Dialog` put it — a bare `Dialog`, `MessageBox`, `FormDialog` before the user tabs into a field — **the keypad key already pressed the default button.** The dialog where it genuinely did nothing is `QueryDialog`, which moves focus to the entry (`query.py:167`), and that is the one arm 3 of `probe_437_review2_fixes.py` measures. The conclusion was generalized from the single dialog that does not represent the others — the same "narrow rather than wrong" shape round 2 flagged in F3, one round later.

This matters beyond wording, because it is what R1 falls out of: had the class binding been in the picture, "bind a second sequence on the toplevel" would not have looked free.

Minimal change: scope the claim to dialogs that move focus off the default button, or re-measure and restate. The bullet is also the only one in the section with no issue reference — this was scope the fix step added, so it should carry its own issue number.

## R3 — should-fix — `src/bootstack/dialogs/_impl/formdialog.py:593`

**The reorder that closed F3 put cancel buttons under form validation, and the dialog can no longer be dismissed.**

`_button_returns_data` now answers `True` for `role='cancel', result='ok'`, and `_accept_press` (`formdialog.py:541`) uses that same answer to decide whether to run `self.form.validate()`. So the contradictory-input button F3 was about does not merely capture its own snapshot now — it is also **refused when the form is invalid**.

Measured:

```python
FormDialog(items=[bs.FieldItem(key='name', label='Name', editor='text', required=True)],
           buttons=[DialogButton(text='Close', role='cancel', result='ok'),
                    DialogButton(text='OK', role='primary', result='ok', default=True)])
```

with the field left blank: `open_after_close_press: 1`, `open_after_escape: 1`. Pressing Close does nothing, and **Escape does nothing either** — `Dialog` binds `<Escape>` to the same cancel button (`dialog.py:554`), so both routes out of a modal window are gone and only the window manager's X remains. Before the reorder, Close returned early on the role test and closed the dialog.

The new test does not see this because `_select_item()` carries no required rule, so `validate()` passes and the press goes through.

Root cause: one predicate is being asked two different questions — "does this press hand back the data?" (which the token must win) and "must this press satisfy the form?" (which the role must win). F3 was right that the first must match `_resolve_result`; that does not make the second follow.

Minimal change: leave `_button_returns_data` as the fix left it and exempt the cancel role from the gate in `_accept_press` — `if btn.role != "cancel" and self.form and not self.form.validate(): return False`. The capture below it still runs, so F3 stays closed. Worth a test with a `required=True` item, since the existing one cannot fail.

## R4 — should-fix — `tests/widgets/public/test_dialog_press_contract.py:233`

**`test_enter_presses_the_default_button` cannot see R1, because it does not send the key where a key goes.**

`top.event_generate("<Return>", when="now")` makes the *toplevel* the event widget, so Tk walks the toplevel's bindtags and only the binding this diff added runs. A real press goes to the focus widget — the default button — and walks `[button, 'TButton', toplevel, 'all']`. The test therefore exercises exactly the one path that works and is structurally blind to the double dispatch, which is why an eight-test file written specifically about "what a button press means" ships with the press being wrong.

Minimal change: assert `top.focus_get()` is the default button as a precondition, generate the event on that widget, and assert the command ran **exactly once** (a counter, not a boolean). Against the shipped code that fails with 2.

## R5 — should-fix — `docs/widgets/dialog.rst:104`

**The refusal pattern the Guide now teaches silently drops the dialog's modality.**

The example calls `bs.alert("A name is required.")` and then returns `False`. Measured from inside that command: `grab_current()` is the dialog before the alert and **`None` after it**. The nested `MessageBox` takes the grab with its own `grab_set()`, and destroying it releases the grab outright rather than restoring the outer one — so from the first refused press onward, the "modal" dialog no longer blocks the parent window, while `show()` is still blocking the caller. A user can click straight back into the main window and drive the app underneath a dialog that is waiting on them.

This is a framework gap rather than something the diff broke (`query._on_submit` has the same shape), but the diff is what promotes it to the recommended way to refuse a press, in the teaching layer.

Minimal change: refuse without a nested modal — set the field's validation message, or `bs.toast(...)` — and if `alert` is kept, say what it costs.

## R6 — nit — `docs/widgets/dialog.rst:112`

**The example cannot demonstrate the sentence directly beneath it.** No button in the snippet carries `default=True`, and the paragraph that follows says the veto "applies to the :kbd:`Enter` key as well, which triggers the default button through the same command." With this dialog, Enter does nothing at all — `Dialog` installs the binding only when a spec sets `default=True` (`dialog.py:543`). The "Reading the result" example two sections up gets it right.

The snippet also references `name`, `write` and `build` without defining any of them and never calls `show()` or reads `result`, where every other example on the page is self-contained — against the standing rule that doc examples are API-verified and must run.

Minimal change: add `default=True` to the Save spec, and either define `name` in the builder or key the refusal off something the snippet owns.

## R7 — nit — `src/bootstack/widgets/_impl/composites/form.py:997`

**A refused `Form` press leaves the previous press's result standing.** The veto returns before the stamp, which is right, but `Form.result` is never cleared — so after a press the command declined, `form.result` still holds whatever the last *accepted* press wrote. Concrete: press Save with a command that accepts (`form.result == {'k': 'a'}`), edit the field, press Save again with the command now returning `False` — a caller reading `form.result` gets `{'k': 'a'}`, data the user has since changed and a press that was refused.

`Dialog` has no equivalent exposure because the accepted press closes the window. `Form` keeps its button row up, so the sequence is ordinary rather than contrived.

Minimal change: `self.result = None` on the refusal path, or state on `bs.Form.result` that it holds the last accepted press. Either is fine; leaving it undefined is what is worth avoiding.

## Checked and clear — not worth re-deriving

- **F1, F5, F6, F7, F8 are closed as claimed.** The `Form` veto matches `Dialog`'s shape; the four new `QueryDialog`/`DateDialog` tests drive the real footer widget and assert the close where it happens; the `datedialog` docstring states the grab reasoning; the Guide has the subsection; `FormDialog._normalize_buttons` now mirrors `Dialog._normalize_buttons` exactly, including the message text.
- **F3's stale-snapshot leak has no other route.** `Dialog.show()` still resets `self.result = None` (`dialog.py:331`), so the window-X path, a plain cancel and an action token all resolve without touching `_submitted_data`. With the token checked first, every write of a data token to `dialog.result` is paired with a capture in the same press. The invariant the removed `show()` reset defended does now hold — R3 is about a second, separate consequence of the reorder, not a reason to restore it.
- **The `query.py` deletion removed no behavior.** Confirmed independently: the bindings were on the composite frame, and the focused inner entry's bindtags are `[entry, 'TEntry', toplevel, 'all']`. Enter still reaches Submit through the toplevel binding, and the Submit spec has no `result=`, so `Dialog`'s `if s.result is not None` cannot clobber what `_on_submit` stored.
- **No vacuity survivors in the new file beyond R4.** Every accept-path test asserts `not top.winfo_exists()` at the press; both refusal tests assert the window is still up and then leave by a second, different route. `_drive`'s `after_cancel` sweep is safe on already-fired ids.
- **The `_drive` duplication is the right trade.** The two copies differ in the one line that matters (`dialog._dialog` vs `dialog._internal._dialog`); factoring them together would mean a helper parameterized on how deep to reach into private state, which is worse than the copy.

---

---

## Round 3 fix step — 2026-08-10

Nothing here is committed. The working tree on `fix/formdialog-select-value-428`
at `eab58129` carries all of it, and `development/round3-fixes.patch` is a copy
of that diff in case the tree is disturbed.

Four of the seven findings are applied. R5, R6 and R7 are deliberately NOT —
see "Still open" below. Two things were measured along the way that change what
earlier rounds recorded, and both are written down here rather than left to be
re-derived.

### R1 — resolved by a guard, but the review's diagnosis of WHERE was wrong

The defect is real and the fix is the one R1 proposed: the toplevel handler
stands down when the key was already delivered to a button.
`dialog.py:568` asks `bindtags` for `TButton`, through Tcl — `tk.call("bindtags",
event.widget)` rather than `event.widget.bindtags()`, because Tkinter's
`_substitute` hands a callback the bare path STRING whenever the target is
absent from its widget map. `_runtime/app.py:144-148` already carries a
`nametowidget`/`KeyError` fallback for exactly that, so it has been hit here
before.

⚠ **R1 attributed this to the `<KP_Enter>` scope creep. It is not there.**
`_runtime/app.py` is untouched by this branch, and `main` already binds BOTH
`<Key-Return>` and `<Key-KP_Enter>` on the `TButton` class (app.py:150-153),
while `main`'s `Dialog` already bound `<Return>` on the toplevel. The double
dispatch predates the branch on PLAIN Enter — every arm of
`probe_437_round3.py` generates `<Return>`, not `<KP_Enter>`. What is new is
the veto: on `main`, `make_command` ignores the command's return value and
destroys the toplevel, so the first invoke always took the second dispatch with
it. Reverting the keypad work would NOT have fixed this.

⚠ **It also needs a CLICK to be reachable, not merely an open dialog** — see
the focus finding below.

### R2 — resolved by rewriting the bullet to what was measured, plus one new bullet

The old bullet claimed the keypad key did nothing in any dialog. It works
wherever a button holds focus, because the class binding covers it. The place
it genuinely did nothing is a dialog that starts with the cursor in a field —
`ask_string`, `ask_integer` — which is what the bullet says now.

A second bullet covers R1's user-visible half. It earns a place under the
"reachable" rule: on `0.2.3` a footer button declared `closes=False` kept the
dialog open, so the second dispatch survived there too. `closes` is removed in
this release, and the veto replaces it, so a caller migrating would have
inherited the bug.

⚠ **The keypad bullet had no issue reference.** (The note originally said
neither did; the R1 bullet in fact ends `(#437)` — that was added after this
paragraph was written.) **RESOLVED 2026-08-11: folded into #437**, at the
maintainer's instruction, rather than filed separately. The keypad binding and
R1's stand-down guard are now the same three lines in `press_default`, and #437
is the button-press-contract issue — a separate issue would have tracked the
detour (binding a key that turned out to be mostly bound already) rather than a
defect a user hits.

### R3 — resolved by excluding cancel from validation, not by reordering again

`_accept_press` now reads `if btn.role != "cancel" and self.form and not
self.form.validate()`. The cancel still falls THROUGH to the capture, which is
what keeps R3's own earlier finding (F3) closed: a contradictory
`role='cancel', result='ok'` button takes a fresh snapshot and so cannot report
a previous run's entries. Refusing it was the part that had to go — `Dialog`
binds Escape to that same button, so a refused cancel is a modal with no way
out but the window manager.

### R4 — resolved, but the test shape changed once focus was actually measured

R4 said to generate on `top.focus_get()` and assert one invocation. Both halves
needed adjusting:

- `focus_get()` reports nothing unless the window is active, which the standing
  rules in CLAUDE.md already warn about. The tests use `focus_lastfor()` for
  assertions and address the widget structurally for `event_generate`.
- A test with an ACCEPTING command reads one invocation whether the guard is
  there or not — the destroy aborts the second dispatch. The command has to
  refuse for the defect to be observable at all.

Three tests now, replacing the one:

| test | what it pins |
|---|---|
| `test_enter_presses_the_default_button` | the fresh-dialog case: nothing holds focus, the toplevel binding is the only answer, Enter still works |
| `test_enter_on_the_default_button_invokes_it_once` | focus on the default button + a refusing command → one command run |
| `test_enter_on_a_focused_button_does_not_also_press_the_default` | the crossfire: Apply refuses, OK must not submit on top of it |

Plus `test_a_cancel_closes_even_when_the_form_cannot_be_satisfied` in
`test_formdialog_result_value.py` for R3, which had no test at all.

**Controls run, each fix reverted on its own.** The failures are behavioral,
not incidental:

```
guard stripped     one press should run one command, ran ['ok', 'ok']
                   Enter ran more than the focused button: ['apply', 'ok']
cancel fix rev'd   the cancel button could not close an invalid form   (12.2s: the 10s force_close fired)
```

### ⚠ NEW — `default_button.focus_set()` at `dialog.py:544` is a NO-OP

Measured on a real dialog, with nothing forced: `focus_lastfor()`, `focus_get()`
and Tcl's own `focus` all report the TOPLEVEL, not the button. The footer is
built before the window is deiconified and the request never takes.

This is pre-existing, out of scope here, and NOT filed. It matters three ways:

1. **It rescopes R1.** With no button focused, opening a dialog and pressing
   Enter dispatches once. The double invoke needs a button to hold focus, which
   a CLICK provides — ttk's `Press` does `focus $w` unconditionally. So the
   reachable path is: click a button whose command refuses, then press Enter.
   Real, but not "any dialog, any Enter".
2. **`probe_437_round3.py` overstated its own arm.** `_invoke_arm` calls
   `top.focus_force()` and `button.focus_set()` before generating. It measured a
   state it created. The crossfire arm is unaffected — it focuses Apply
   deliberately, which is the point.
3. **Keyboard users get no focus ring and a Tab order starting from nowhere**,
   in a dialog that documents `default=True` as "focused, triggered by Enter".

### Verification — measured 2026-08-10, working tree at `eab58129` plus these changes

Full `py -3.12 tests/run_gui.py`, **exit 0, all legs passed**.

| leg | baseline at `eab58129` | with these changes |
|---|---|---|
| widgets+CLI, shared root | **1001 passed / 13 skipped** (52 deselected) | **1004 / 13** |
| data | **123 passed / 6 skipped** | **123 / 6** |

Exactly +3, matching the 3 net tests added.

⚠ **The counts in `460687eb`'s commit message — `957 / 14` and `125 / 4` — are
WRONG.** The baseline was re-measured by stashing these changes and running the
suite at HEAD, rather than by reasoning from the recorded figure. This is the
same failure mode CLAUDE.md records four previous instances of. Record the date
AND the commit beside any count.

### Still open for the next session

Three round-3 findings are deliberately not applied, to stop the fix step
growing scope the way round 2's did:

- **R5 — `docs/widgets/dialog.rst:104`, the taught refusal pattern drops the
  dialog's grab.** Measured: `grab_current()` is the dialog before the nested
  `bs.alert(...)` and `None` after. This is a real bug in a pattern the branch
  is actively teaching, and is the one of the three worth folding in.
- **R6 — `docs/widgets/dialog.rst:112`**, no button sets `default=True` while
  the prose says the veto applies to Enter; `name`, `write` and `build` are
  undefined and it never calls `show()`.
- **R7 — `form.py:997`**, the `Form` veto returns before the stamp without
  clearing `result`, so a refused press leaves the previous accepted press's
  data readable at `form.result`.

And two decisions:

- ~~**The keypad CHANGELOG bullet needs an issue number**, or folding into
  #437.~~ **DECIDED 2026-08-11 (maintainer): folded into #437.** The bullet now
  ends `(#437)`; no separate issue was filed. Reasoning above under the R2 fix.
- **`focus_set()` being a no-op needs an issue.** Do not fix it on this branch.

Nothing is committed. The suite is green and the controls have been run, so
this is ready for the maintainer to test and then approve commit-by-commit.
