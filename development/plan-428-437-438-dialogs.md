# PLAN — #428: `FormDialog` returns a select's display text instead of its value

Branch: `fix/formdialog-select-value-428` (off `main`)
Issue: #428, reported by an external user (`@bLynnb2762`)

## What this is supposed to do

`FormDialog.result[key]` must return the same thing `bs.Form.get()[key]` and
`bs.Select.value` return for the same options list: the option's **value**.

With `options=[('One', 1), ('Two', 2), ('Three', 3)]`, choosing *One* must yield
`1` from all three. Today the dialog yields `'One'`.

## Root cause — measured, not inferred

`development/probe_428_dialog_widget.py` reproduces it:

```
before destroy    : 2          <- correct value
variable holds    : 'Two'      <- the Tk variable holds display TEXT
AFTER destroy     : 'Two'      <- what show() actually reads
```

The chain:

1. The default OK button is `DialogButton(result="ok")`. In `auto_command`,
   `self._dialog.result = btn.result if btn.result is not None else (...)`, so it
   stores the **token** `"ok"` and never touches the form.
2. `show()` returns only after the dialog's wait loop ends — the toplevel and
   every editor in it are destroyed by then.
3. `show()` then calls `_resolve_result("ok")`, which, because `"ok"` is in
   `_DATA_RESULTS`, reads `self.form.data` — **from destroyed widgets**.
4. `Form._read_value_from_widget` does `try: value = widget.value` / `except:
   value = self._variables[key].get()`. On a destroyed widget the read raises,
   so it falls back to the Tk variable — which holds the **display text**.

So the defect is a **read-after-teardown**, not a select bug and not a
value-mapping bug.

### What this rules out — do not re-investigate

- **Not the read path.** `bs.Form.get()` → `_internal.get()` → `return self.data`
  → `_collect_data()`, and `FormDialog` reads that same `.data`. Public
  `FormDialog.result` is a bare passthrough. No conversion exists on that chain.
- **Not the build path.** Measured side by side in one app instance: the dialog
  and a public `bs.Form` build the *same* `Select`, with options normalized
  identically to `{'text','value'}` bags, both returning `1`.
- **Not `bs.FieldItem` vs an impl `FieldItem`** — same class.

## The fix

**Capture the form data at button-press time, while the widgets are alive, and
have `_resolve_result` use that snapshot instead of re-reading `self.form.data`.**

The correct behavior already exists in the same file: a button with
`result=None` stores `self.form.data` inside its command, at click time. Only
buttons carrying a result token (`ok`/`submit`/`save` — i.e. the DEFAULT pair)
defer the read until after teardown. The fix removes that asymmetry.

Touches `_wrap_button_commands` (both `wrapped_command` and `auto_command`) and
`_resolve_result` in `src/bootstack/dialogs/_impl/formdialog.py`.

## Invariants and assumptions

- A submit-style result must reflect the form **as it was when the button was
  pressed**, which is also the only moment it is guaranteed readable.
- Cancel still yields `None`; a custom action token still yields that token, so
  callers can tell an action apart from data. `_DATA_RESULTS` keeps its meaning.
- The snapshot must be taken **after** `form.validate()` passes, matching where
  the existing correct path takes it.
- Re-showing the same dialog must not leak the previous snapshot — reset it in
  `show()` alongside `_initial_layout_done`.
- `Form._read_value_from_widget`'s fallback is **left alone**. It is reachable
  from other callers and narrowing it is a separate change; this fix removes the
  reason `FormDialog` reaches it at all. Whether that fallback should return the
  variable's text for a select is worth a follow-up issue, not scope here.

## The decision: standardize on VALUE

DECIDED (maintainer, 2026-08-10). The reporter deliberately left it open — *"the
same type of data, whether that be the text or the value"* — so this is a choice,
not a given. `FormDialog` is brought in line with the other two paths rather than
the reverse: `.value` means the value framework-wide, `.selection` is the
both-parts bag, and two of three paths already return the value. Standardizing on
text would have touched all three.

## Blast radius — wider than the issue title, MEASURED

`development/probe_428_end_to_end.py` runs the reporter's literal flow and
reports the TYPE beside the value:

```
bs.Select.value            1      int   OK
Form.get()['k']            1      int   OK
FormDialog.result['k']    'One'   str   MISMATCH
```

**The type is not separately recoverable on the broken path.** The fallback
returns whatever the Tk variable holds, and Tk variables are string-backed, so
EVERY value type is flattened to `str` there — an int comes back as its label
here, and a date editor would return its formatted display string rather than a
`date`. #428 is a type-integrity bug across the dialog's whole editor set, not a
select-labelling quirk.

So: the regression test asserts VALUE **and** TYPE, and covers a non-select
editor as well; the CHANGELOG entry must not promise this is select-only.

## How it will be verified

- Regression test asserting `FormDialog`'s result carries the VALUE for a select
  built from `(text, value)` pairs, failing against unfixed source for the right
  reason (returning `'One'`, not an `AttributeError`).
- A control in the same test: a plain `bs.Form` with the identical field, which
  passes before and after, so a failure is attributable to the dialog.
- `development/probe_428_dialog_widget.py` re-run — the `AFTER destroy` arm is
  the pre-fix behavior and should be re-pointed at the fixed path.

---

# PLAN — #437: validation is gated on button *role* instead of button *intent*

Issue: #437. Same branch, because it is the same file and the same defect class
(`FormDialog` result correctness), and both ship in the same minor.

## What this is supposed to do

Validation must run only for a press that is about to **submit the form's data**.
A button whose entire payload is an action token — `DataTable`'s Delete — never
reads the form, so requiring the form to be valid before it runs is meaningless.

And a press that is *refused* must leave nothing behind. Today it does.

## Root cause — one conflation, two symptoms

`_wrap_button_commands` gates on `btn.role != "cancel"`, treating "not cancel" as
"submits data". `DataTable` builds Delete as `{"role": "secondary", "result":
"delete"}` (`tableview.py:1759`), so it validates.

**Symptom 1 — Delete is inert on exactly the records worth deleting.** Validation
lives in the editor widgets, which exist only while the dialog is open, so it can
only gate what *leaves* the dialog. It has no reach over what is already in the
datasource. Measured: `bs.DataTable(rows=[...])` validates nothing, and a sparse
record (key simply absent) makes the edit form invalid on arrival.

**Symptom 2 — backing out of the refused delete performs the delete.**
`Dialog._create_standard_buttons.make_command` (`dialog.py:502`) discards the
command's return value and stamps `self.result = s.result` regardless. Cancel
cannot clear that stamp: the only write in `Dialog` is guarded by `if s.result is
not None`, and Cancel's result *is* `None` — the same sentinel means both "my
answer is nothing" and "I do not touch the result". So Cancel closes the window
and leaves the token standing, and `tableview.py:1787` deletes the record.

Cancel appears to work in every normal case only because `result` still holds the
`None` that `Dialog.show()` set.

> ⚠ **SUPERSEDED IN PART (maintainer, 2026-08-10).** The `submits` field below
> was **not built**. The maintainer's call: #437 is closed by the inference
> alone, and `submits` existed only to override that inference for buttons
> nobody has written — speculative public surface on a dataclass, added ahead of
> demand. The predicate stayed and is named `_button_returns_data`; the tri-state
> flag, its docstring and its two tests are gone. Everything else in this section
> shipped as written. See the #438 section for the same call applied to `closes`.

## The fix — two changes, each at the layer that owns the problem

**1. `Dialog` learns that a press can be refused** (`dialog.py`). `make_command`
honors a `False` return from the button's command:

```python
if s.command and s.command(self) is False:
    return          # refused: no stamp, no close
```

The convention already exists one layer down — `wrapped_command` treats a user
command returning `False` as a veto — it was simply never propagated to the layer
that owns the result and the destroy. With this in place the stale token is not
cleared after the fact, it is **never written**, which also covers a custom
`command` that vetoes.

**2. `FormDialog` gates on intent, not role.** One predicate, consulted where the
third rule used to live:

```python
def _button_submits(self, btn) -> bool:
    if btn.submits is not None:
        return btn.submits
    if btn.role == "cancel":
        return False
    if isinstance(btn.result, str) and btn.result.lower() in self._DATA_RESULTS:
        return True
    return btn.result is None    # non-cancel, no token: carries the form data
```

`_DATA_RESULTS` becomes the single named source of truth. It is currently
duplicated, unnamed, as the bare triple `("ok", "submit", "save")` in
`_normalize_buttons` and as the frozenset in `_resolve_result`, while
`_wrap_button_commands` uses a third rule agreeing with neither.

**3. `DialogButton.submits: bool | None = None`** — new public field, tri-state.
`None` infers via the predicate above; `True`/`False` override.

Tri-state is what makes this safe. Defaulting `False` would silently stop
validating every existing `{"text": "Save", "result": "save"}` spec; defaulting
`True` would leave Delete validating unless the author opts out, which is the
bug. `None` preserves every current behavior, fixes Delete because `"delete"` is
not in the set, and gives `"apply"` a way to say what it is.

It sits beside `closes` — both are per-button behavior flags at the same layer.
Per-button, not per-dialog, because one dialog legitimately has Save *and* Delete
*and* Apply.

## Invariants and assumptions

- The **only** behavior change for existing code is that a non-cancel button
  carrying a result token outside `_DATA_RESULTS` no longer validates. Everything
  else — Cancel, `ok`/`submit`/`save`, and a non-cancel button with no token —
  keeps today's behavior exactly.
- A refused press must not write `dialog.result`, must not close the dialog, and
  must leave the form's error state visible.
- `_resolve_result` is **unchanged**. `submits` governs whether a press validates
  and captures; `result` governs what the caller receives. They are related but
  distinct, and conflating them is what produced this bug.
- Consequence, documented rather than special-cased: `submits=True` with a custom
  token (`"apply"`) validates and captures, and the caller still receives
  `"apply"` — the snapshot goes unused. That is the useful reading ("do not let
  the user Apply an invalid form"), not an oversight.
- `submits=False` with `result=None` yields `None`, indistinguishable from
  cancel. An author asked for it; not special-cased.
- The `closes is False` self-destroy must move **out** of the `role != "cancel"`
  guard added for #428. Nested there, a cancel button declared `closes=False`
  with a command never closes at all — `make_command` also skips its destroy
  because `closes` is False, so `show()` blocks until the user hits the X.

## Blast radius

`DialogButton` is in `bootstack.dialogs.__all__`, so `submits` is new public
surface — a minor, not the patch line. The maintainer confirmed the next release
is a minor, which is why this rides with #428 rather than waiting.

The `make_command` veto is a behavior change on public `Dialog`: a command
returning `False` now vetoes the stamp and the close, where it was previously
ignored. No dialog in the repo returns `False` from a button command
(`query.py`, `fontdialog.py` both return `None`), and `FormDialog` already
honored the convention internally, so nothing in-tree changes. It goes in the
CHANGELOG under `### Changed`.

## How it will be verified

- A test pressing a custom action button on a form that fails validation: the
  action must run (pre-fix it is inert).
- A test for the destructive path: refuse the action press, then cancel, and
  assert the result is `None` (pre-fix it is the action token).
- A test that `ok`/`submit`/`save` and a token-less non-cancel button still
  validate — the no-regression half, which is what makes tri-state worth having.
- A test for `submits=True` on a custom token, and `submits=False` on a data
  token, covering both explicit overrides.
- A test that a cancel button with `closes=False` and a command still closes.
- Coverage for `wrapped_command`'s non-cancel capture, which round 2 found has
  none — every existing test reaches `auto_command` instead.
- Each control run against pre-fix source, so the failures are behavioral rather
  than an `AttributeError` from a method that does not exist yet.

---

# PLAN - #438: `closes=False` means three different things on a FormDialog button

Issue: #438. Same branch as #428/#437, at the maintainer's direction: it is
release-blocking, it touches the same function #437 just rewrote
(`_wrap_button_commands`), and doing it here means one review pass covers both
rather than reopening the same lines twice.

> ⚠ **SUPERSEDED (maintainer, 2026-08-10). `closes` was REMOVED, not repaired.**
> The plan below makes the flag consistent. The maintainer asked instead why it
> exists at all, and the answer did not survive the question:
>
> - **Both in-tree uses were misusing it.** `query.py:99` and `datedialog.py:263`
>   declared `closes=False` and then destroyed the toplevel by hand once the
>   input was acceptable. Neither wanted "a button that does not close" — both
>   wanted "this press may be refused", expressed as a permanent per-button
>   property because a per-press one did not exist. #437's veto is that per-press
>   answer, and it is strictly better: the command returns `False` and `Dialog`
>   keeps the close. Both call sites got shorter.
> - ⚠ **It WAS public, documented, and shipped — an earlier draft of this note
>   said "never documented" and that was WRONG.** What the grep behind that claim
>   actually showed is narrower: no *narrative* page (guide, how-to, widget page)
>   uses `closes=` in an example. The API Reference documented it regardless,
>   because `_templates/autosummary/class.rst` renders `:members:` and every
>   dataclass field with an attribute docstring appears there — a field gets
>   documented by EXISTING, not by anyone choosing to write about it. Verified
>   against the published artifact rather than the source tree: the live
>   `bootstack-0.2.3-py3-none-any.whl` carries `closes: bool = True` with its
>   docstring and exports `DialogButton` from `bootstack/dialogs/__init__.py`,
>   and the field is present at `v0.1.0`, `v0.2.0` and `v0.2.3` — every release
>   since the SemVer freeze. So this is the removal of shipped, reachable,
>   documented public API: a MINOR, a required `### Removed` entry, and NOT the
>   #397/#401 case where an unreachable defect was deliberately left out of the
>   CHANGELOG.
> - **Removed outright rather than deprecated** (maintainer, 2026-08-10). The
>   conservative path — accept `closes` for one more release behind a
>   `DeprecationWarning` — was raised and declined: the project has an explicit
>   no-shims stance, it is pre-1.0, and a deprecation window would mean another
>   release in which the field's documented meaning and its behavior disagree.
> - **The one case the veto does not cover** is a footer button that never
>   dismisses the dialog — the OK/Cancel/**Apply** convention. Rejected as
>   product surface: a dialog's footer is its set of exits, and a non-exit button
>   is body content, where `Dialog(content_builder=...)` already puts a plain
>   `bs.Button` with no framework flag involved.
>
> **⚠ The `show()` reset was removed too, and the measurement is the reason —
> do not re-add it.** `self._submitted_data = None` in `show()` was written for
> a hazard the veto made unreachable: back then `make_command` stamped a
> button's result even when the wrapper refused the press, so run two could
> close carrying a data token it had never captured and resolve it against run
> one's snapshot. Deleting the line left all 15 tests green, which established
> it was dead but not whether it was *load-bearing for test sensitivity* — the
> argument for keeping it was that it might mask, or might catch, a later
> weakening of the veto. Measured across all four combinations of the two knobs:
>
> | reset | veto | re-show test |
> |---|---|---|
> | on | on | passes |
> | on | off | **fails** — regression caught |
> | off | on | passes |
> | off | off | **fails** — regression caught |
>
> The reset changes nothing in any arm. What catches a veto regression is the
> test's PRECONDITION (`assert toplevel.winfo_exists()`), which trips before the
> result is ever asserted, because a press the veto no longer refuses closes the
> dialog. So the reset neither defends nor hides, and one line of inert
> defensive code was costing a three-paragraph docstring explaining a hazard
> that cannot occur. The standing rule it illustrates: **"it is only one line"
> is not an argument for keeping code — measure whether it changes any
> observable, including the sensitivity of the tests around it.**
>
> **What actually shipped:** `closes` deleted from `DialogButton`;
> `Dialog.make_command` closes unconditionally once the press is not refused;
> `query.py` and `datedialog.py` rewritten onto the veto; `FormDialog` no longer
> takes the close over at all, so `took_over` / `declared_closes` and the
> self-destroy are gone with it. The defensive copy in `_normalize_buttons`
> **stayed** — it is the one part of #438 that was a real bug, and it stands on
> its own regardless of what `closes` meant. Sections below are kept as the
> record of what was considered.

## What this is supposed to do

`closes=False` must mean "do not close this dialog", everywhere, exactly as
`DialogButton.closes` documents and exactly as a plain `Dialog` already behaves.

## Root cause - the field is doing two jobs

`_wrap_button_commands` writes `button.closes = False` on every non-cancel
button. That write is not the caller's intent, it is an internal marker meaning
"I have told `Dialog` not to close this one, because I close it myself once the
form validates". The same field is then read back to decide whether to close, at
which point a `False` written by the framework and a `False` written by the
caller are indistinguishable.

Measured (`development/probe_437_closes_false_cancel.py`, plus a third arm):

| declaration | today |
|---|---|
| `closes=False` on a non-cancel button | closes anyway - declaration discarded |
| `closes=False` on a cancel button WITH a command | closes |
| `closes=False` on a cancel button with NO command | does not close |

Same shape as the #437 defect, where `result=None` meant both "my answer is
nothing" and "do not touch the result".

Second defect, same line: `_normalize_buttons` passes caller-supplied
`DialogButton` instances straight through, so that write **mutates the caller's
own object**. A spec reused across two dialogs has been silently rewritten.

## The fix

**1. Stop mutating the caller's spec.** `_normalize_buttons` takes a defensive
copy (`dataclasses.replace`) of a caller-supplied `DialogButton`, since
`_wrap_button_commands` rewrites both `command` and `closes` on it. The other two
input forms already construct fresh instances.

**2. Record the takeover separately from the declaration.** Capture what the
caller asked for before overwriting, and close only when BOTH are true: this
dialog took the close over, and the caller wanted a close.

```python
took_over = button.role != "cancel"
declared_closes = button.closes
if took_over:
    button.closes = False   # Dialog must not close it; we do, after validating
```

and in the wrapper:

```python
if took_over and declared_closes and self._dialog and self._dialog.toplevel:
    self._dialog.toplevel.destroy()
```

A cancel button is never taken over, so `Dialog` keeps deciding it from the
caller's own untouched `closes`.

## Resulting semantics - all three arms agree

| declaration | after |
|---|---|
| non-cancel, `closes` default `True` | closes, after validation (unchanged) |
| non-cancel, `closes=False` | does NOT close - **change** |
| cancel, `closes` default `True` | closes via `Dialog` (unchanged) |
| cancel, `closes=False`, with or without a command | does NOT close - **change on the command path** |

## ⚠ This deliberately REVERSES #437's F7

Round 2 found that #437's new `btn.role != "cancel"` guard had stopped a
`closes=False` cancel button with a command from closing, and asked for the
previous behavior back. That was a regression argument, not a correctness one -
and restoring it is what exposed that the three paths never agreed at all, which
is #438. Under the rule "`closes=False` means do not close", the pre-#437
behavior was itself wrong.

So F7's fix stands as far as the *capture* guard is concerned; only its destroy
half is superseded. The test asserting the old behavior is inverted, its name
changed, and the CHANGELOG bullet rewritten. `REVIEW.md` records the reversal
against F7 so a later reader does not read it as a regression reintroduced.

## Invariants and assumptions

- Nothing in the repo is affected. The only two in-tree `closes=False` uses are
  `datedialog.py:263` and `query.py:99`, and both are plain `Dialog` wrappers,
  not `FormDialog`, so `_wrap_button_commands` never sees them. Both also pair
  `closes=False` with a command that closes the window itself - which is the
  contract this change makes uniform.
- A `FormDialog` button with `closes=False` now leaves the dialog open with no
  built-in way out, exactly as the same declaration does on a plain `Dialog`.
  That is the caller's responsibility, not a hang to design around.
- `closes` is NOT rejected on a submit button. The issue raises whether the
  framework owning the close should make the flag an error there; honoring it is
  the smaller change and matches the documented meaning.

## How it will be verified

- All three arms of `probe_437_closes_false_cancel.py`, extended to cover the
  non-cancel case, agreeing after the fix.
- A test that a caller-supplied `DialogButton` is not mutated by construction.
- The inverted F7 test, closing the dialog by another path so the harness cannot
  stall on the assertion.
- Controls for each against the pre-#438 source.
