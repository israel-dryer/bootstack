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
