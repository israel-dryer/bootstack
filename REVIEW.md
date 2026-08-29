# REVIEW — #482 round 1

Branch `fix/field-value-lags-signal-482`, diff `main...HEAD` (36 lines of `src/`,
13 tests). Round cap 2, this is round 1.

Measured on the macOS box, `.venv/bin/python` 3.14.0, against a `main` worktree
arm with `PYTHONPATH` set and provenance printed. Probes:
`development/probe_482_commit_in_trace.py`.

---

## 1 — BLOCKING. An in-trace `commit()` cannot repaint the entry, so the signal and the display diverge permanently

`textentry_part.py:190` / `spinnerentry_part.py:174` — `_commit_if_not_editing`
calls the whole of `commit()`, including its display-normalizing
`textsignal.set(new_text)`.

**Root cause.** That call now runs inside the variable's own write trace. Tcl
suppresses every other trace on a variable while one of its traces is executing,
so the nested `set()` moves the signal and the entry's own textvariable trace
never runs — the widget keeps the old text. Measured in plain `tkinter`: a
nested `set` from inside a write trace fires no trace at all. `commit()`'s
cancel/resubscribe dance is therefore also inert on this path.

Worse, it does not heal. Because the signal has already been advanced to the
formatted text, the real commit at blur finds `new_text == self.textsignal()`
and skips the display update, so the entry shows the raw text for the rest of
its life.

`TextField(textsignal=sig, value_format="#,##0.00")`, then `sig.set("1234.5")`:

| | main | branch |
|---|---|---|
| after the write | sig `'1234.5'` · display `'1234.5'` · value `1.0` | sig **`'1,234.50'`** · display `'1234.5'` · value `1234.5` |
| after a later blur | sig `'1,234.50'` · display `'1,234.50'` · value `1234.5` | sig `'1,234.50'` · display **`'1234.5'`** · value `1234.5` |

Three consequences, all new: the widget displays text neither the caller nor the
signal holds; the caller's own `Signal` is silently rewritten by a write they
made; and an application subscriber on that signal is handed `'7.00'` where it
used to receive the `'7'` it set.

`value_format` is not required to reach it — `commit()` also `.strip()`s.
`sig.set("  padded  ")` on a plain `TextField` leaves sig `'padded'` and display
`'  padded  '`.

**Minimal change.** Re-derive the value; do not normalize the display. Split
`commit()`'s parse half into `_reparse()` and call that from
`_commit_if_not_editing`. Normalizing stays where it was — at blur/Return,
outside any trace — which is also where the family's committed-value contract
puts it: a programmatic write has no editing session to normalize the end of.

**RESOLVED** — `_reparse()` extracted in both parts; `_commit_if_not_editing`
calls it behind the placeholder guard. Both arms of the table above now match
`main` except for `value`, which is the fix. Regression test:
`test_a_formatted_write_leaves_the_display_and_the_signal_alone`.

## 2 — BLOCKING (same fix). The change reaches a fifth widget by inheritance, and PLAN's population does not

`NumberEntryPart` subclasses `TextEntryPart`, so it inherits `_handle_change`
and the new helper. PLAN scopes the fix to four widgets on the grounds that
`NumberField` already followed; the code does not respect that scope, and
`NumberEntryPart.commit()` applies bounds and re-normalizes.

`NumberField(value=5, min_value=0, max_value=10, value_format="#,##0.00")`:

| | main | branch |
|---|---|---|
| `f.value = 7` | `7.0` | `7` — return type changed |
| `f.value = 99` | value `99.0`, display `'99.00'` | value **`10`**, display `'99.00'` |

The second row is the same divergence as finding 1 in a widget the branch
claims not to touch: `.value` reports the clamp while the widget shows the
unclamped number.

**Minimal change.** Finding 1's fix makes this inert — `_reparse()` does not
reach `NumberEntryPart`'s bounds override, so `NumberField` returns to `main`'s
behavior exactly.

**RESOLVED** — verified byte-identical to `main` on both rows.

## 3 — NOTE. Re-entrancy: no recursion, no leak, subscription stays live

The attack that motivated the round comes back clean, for a reason worth
recording. `commit()` cannot re-enter `_handle_change` — not because of its
cancel/resubscribe, but because Tcl has already suppressed the trace (finding
1). 50 successive programmatic writes leave `_on_input_fid` live and the
subscriber count where it started. An application subscriber on the same signal
is called once per write, not twice.

## 4 — NOTE. Per-keystroke cost is 1.5 us

2000 signal writes with the field focused: 13.5 us/write on `main`, 16.6 us at
round 0, 14.8 us after the fix. `focus_get()` alone is 1.1 us. The existing
`<FocusIn>`/`<FocusOut>` bindings could carry a boolean for free, but 1.3 us on
a keystroke is not worth the diff.

## 5 — NOTE. `except (TclError, KeyError): return` is right, and unreachable

`destroy()` cancels `_on_input_fid` before the widget goes, so `_handle_change`
does not run for a destroyed entry; a write to a signal whose field's toplevel
was destroyed raises nothing on either arm. Kept as written — skipping the
commit is the correct answer during teardown, and `KeyError` out of
`_nametowidget` is a real shape (see `grab_current`).

## 6 — NOTE (gate 2, diagnostics only).

`test_typing_is_still_uncommitted_until_blur` rests on `focus_force()` taking
effect. Where it does not — an unmapped widget, or X11 with no window manager —
`focus_get()` is not the entry, the write commits, and the test fails while the
product is fine. A precondition assert would label that as setup rather than
product; gate 2 makes it a note, not a fix.

## 7 — NOTE. No third part needs the helper

`grep -rn "def _handle_change\|def commit" src/bootstack/` returns three
`commit`s and two `_handle_change`s: `textentry_part`, `spinnerentry_part`, and
`numberentry_part`, which inherits both from the first. The duplication is the
two copies already flagged for #477.
