# PLAN — #482: a field's `value` lags a programmatic signal write

**Branch** `fix/field-value-lags-signal-482` off `main` at `99990cc4` (post-`0.4.0`).
**Round cap: 2** (patch-shaped — no new public surface, nothing raises that did not).
Milestone: `0.4.x — Patch line`.

## The defect

Writing to a bound `Signal` moves what the field displays but not what `.value`
reports, until something commits the field. Measured on `0.4.0`:

```
sig.set('world')  ->  entry shows 'world',  tf.value 'hello'
after FocusOut    ->  tf.value 'world'
```

## Population — measured, and the issue is wrong about it

`sig.set()` then read `.value`, unfocused, no commit:

| widget | result |
|---|---|
| `TextField`, `PasswordField`, `PathField`, `SpinnerField` | **LAGS** |
| `TextArea`, `CodeEditor` | follows |
| `NumberField`, `Select` | follows |

**Four widgets, not six.** The issue's "boundary of the claim" names `TextArea` and
`CodeEditor` as the obvious candidates; they do not use the entry part and are
already correct. The four that lag are exactly those backed by `TextEntryPart`.

## Mechanism

`TextEntryPart._value` is the committed value and `value()` returns it directly.
It is re-derived **only** in `commit()`, called from `_handle_focus_out` and
`_handle_return`. A programmatic `sig.set()` reaches `_handle_change`, which emits
`<<Input>>` and never touches `_value`.

So the committed-value contract is right for *typing* — `value` should not follow
keystrokes — and wrong for a write the application itself performed, where there
is no editing session to commit and no blur coming.

## The fix

Commit when a text change arrives while the widget **does not hold keyboard
focus**. Measured as a usable discriminator: unfocused, `focus_get()` is not the
entry part; while typing it always is.

⚠ **Do not emit an event from this.** `commit()` and `_check_if_changed()` are
separate, and only the latter emits `<<Change>>`. The fix calls the former. The
family already disagrees about whether a programmatic set is a change, and the
maintainer's standing disposition (2026-08-26) is *keep in mind, do not fix, do
not file* — so event behaviour must be byte-identical before and after.

## Stated residual, not a gap to close later

**A programmatic write while the field has focus still lags.** It is
indistinguishable from typing at this seam — both arrive as a variable trace with
focus held — and closing it means tracking edit provenance, which is a larger
change than the defect warrants. The common case is a write from application code
while the user is elsewhere, and that is fixed.

## Rejected

**Commit on every text change.** Makes `value` follow keystrokes, which discards
the committed-value contract the whole family is built on, and would change what
`value` reports mid-edit for every existing app. The staleness during typing is
deliberate; only the programmatic case is the defect.

## Risks to check in review

1. `commit()` early-returns while the placeholder shows — confirm a programmatic
   write onto a placeholdered field behaves.
2. `commit()` re-formats the display through `_format_value`. On a field with a
   `value_format`, does committing a programmatic write reformat what the caller
   wrote? Measure before and after.
3. `commit()` keeps the prior value on a parse failure. A programmatic write of
   unparseable text must not silently revert the display.
4. `SpinnerField` and `PathField` have their own write paths; confirm the fix
   reaches all four and breaks none.
5. Event counts unchanged — `<<Input>>` and `<<Change>>` before and after, on both
   a programmatic write and a real typed edit.
