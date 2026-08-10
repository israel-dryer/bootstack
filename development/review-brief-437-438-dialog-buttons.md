# Review brief — #437 / #438, round 2

Hand this to a **fresh session**. Per `REVIEW-PROTOCOL.md`, the session that
wrote this code cannot review it, and this brief exists so intent travels in a
file rather than in a conversation.

## What to review

Branch **`fix/formdialog-select-value-428`**, head **`9ed5cad2`**.

Round 1 reviewed `9a55742f` (#428 only). This round's new work is:

```
git diff 9a55742f..HEAD
```

Two dots — everything since round 1's reviewed head. `main` is a genuine
ancestor, so `git diff origin/main...HEAD` also works if you want the whole
branch; the #428 half has already been through a round.

## What to read

- **The diff.**
- **`PLAN.md`** — but see the warning below; it is no longer purely a plan.
- `REVIEW-PROTOCOL.md` for the format and the severity split.

## What NOT to read

- **The commit messages.** `7c2cfde5`'s message is long and argues why the
  approach is sound. That is exactly the input the protocol excludes — it
  produces "yes, that seems right" instead of scrutiny. Resist `git log`.
- **`REVIEW.md`'s round-1 section.** It describes the `closes` takeover and the
  `show()` reset, both of which this work deleted. Reading it will send you
  looking for code that is gone.
- Any prior chat transcript.

⚠ **`PLAN.md` is a mixed document now.** Its three original sections (#428,
#437, #438) were written before implementation and are legitimate plan input.
The blocks marked **SUPERSEDED** were added *after* the fact and are
implementer rationale — read them as *decisions of record* (what was decided,
by whom, and what measurement backed it) rather than as argument you are meant
to agree with. If a superseded block's reasoning does not survive your reading
of the diff, that is a finding, not a misunderstanding on your part.

## Shape of the diff

| file | what it is |
|---|---|
| `src/bootstack/dialogs/_impl/dialog.py` | `closes` + `submits` removed; `False`-return veto in `make_command`; `winfo_exists` destroy guard |
| `src/bootstack/dialogs/_impl/formdialog.py` | button pipeline rewritten: `_accept_press` / `_record_press` / `_button_returns_data`; close takeover gone; defensive copy; dead `show()` reset removed |
| `src/bootstack/dialogs/_impl/query.py` | rewritten onto the veto |
| `src/bootstack/dialogs/_impl/datedialog.py` | rewritten onto the veto; `_confirm` split into `_record` + close |
| `tests/widgets/public/test_formdialog_result_value.py` | 15 tests (4 removed, 3 added) |
| `CHANGELOG.md`, `PLAN.md` | `### Removed` entry; superseded notes |

## ⚠ Where the risk actually is — read this first

**`query.py` and `datedialog.py` have NO test coverage of the paths that were
rewritten.** Measured, not assumed: nothing under `tests/` references
`_on_submit`, `_on_confirm_range`, or drives `ask_item` / `ask_string` /
`ask_date_range` through a button press. The full suite is green at this head,
and that greenness says nothing about these two files. They are the least
verified part of the diff and deserve the most attention.

Specific things worth checking there:

1. **`query.py`'s Enter-key path.** `_on_submit` no longer closes the dialog; it
   returns `True`/`False` and a new `_submit_from_key` closure closes on
   acceptance. `entry.bind("<Return>", ...)` binds on the *composite* widget,
   and Tk bindings do not bubble from a child to a parent widget — so it is
   unclear whether that binding ever fired, before or after. `Dialog` separately
   binds `<Return>` on the toplevel to the default button. Two handlers may both
   run, or the composite one may be dead code. This was not resolved.
2. **`datedialog`'s grab release.** The old range-confirm path called
   `grab_release()` before destroying. The button path now goes through
   `Dialog`, which never calls `grab_release` — it relies on Tk releasing the
   grab when the grabbing window is destroyed. Consistent with every other
   dialog in the tree, but it is a behavior change on this path.
3. **Double-close.** `Dialog` now always destroys an accepted press, where it
   previously skipped when `closes` was `False`. The `winfo_exists()` guard is
   what stops a command that closes the dialog itself from hitting a
   `TclError`. Check the guard covers every path that can reach it.

## Settled — do NOT re-litigate

Each of these was decided by the maintainer during this session. Flagging them
again costs a round.

- **`DialogButton.closes` was REMOVED, not repaired.** The plan was to make it
  consistent; the maintainer asked why it existed at all. Both in-tree uses were
  misusing it as a per-press veto expressed as a per-button property. The one
  case the veto does not cover — a footer button that never dismisses the dialog
  (OK/Cancel/**Apply**) — was rejected as product surface, on the grounds that a
  dialog's footer is its set of exits and a non-exit button is body content.
- **Removed outright rather than deprecated.** No-shims stance, pre-1.0, and a
  deprecation window would mean another release in which the field's documented
  meaning and its behavior disagree.
- **`submits: bool | None` was built and then dropped.** #437 is closed by the
  inference (`_button_returns_data`) alone; the field only overrode that
  inference for buttons nobody has written.
- **Commit granularity.** One commit for both issues rather than one per issue.
  A per-issue split needed a #437-only intermediate carrying `submits` and the
  `closes` takeover — code the maintainer had rejected.

## Measured — do NOT re-derive

- **`closes` was shipped, reachable, and documented.** Verified inside the
  published `bootstack-0.2.3-py3-none-any.whl` (not the source tree): the field
  and its docstring are present and `DialogButton` is exported from the shipped
  `bootstack/dialogs/__init__.py`. Present at `v0.1.0`, `v0.2.0`, `v0.2.3`. The
  API Reference documented it because `_templates/autosummary/class.rst` renders
  `:members:` — a dataclass field is documented by *existing*. So the `###
  Removed` CHANGELOG entry is required; this is not the #397/#401 case.
- **The `show()` reset was inert.** `self._submitted_data = None` was removed
  after measuring all four combinations of that line and the veto against
  `test_a_reshown_dialog_does_not_report_the_previous_entries`:

  | reset | veto | result |
  |---|---|---|
  | on | on | passes |
  | on | off | **fails** — regression caught |
  | off | on | passes |
  | off | off | **fails** — regression caught |

  It changes nothing in any arm. What catches a weakened veto is the test's
  precondition, which trips before the result is asserted.
- **Both new ordering tests are non-vacuous**, with controls run against
  deliberately broken source: capturing after the command yields
  `{'k': 'Two'}` where `2` is required (the #428 signature); recording before
  the command yields `{'k': 2}` where `None` is required.
- **Suite at this head:** `py -3.12 tests/run_gui.py` exit 0, all legs —
  **947 passed / 14 skipped** (shared root), **125 / 4** (data), 50 across the
  isolated legs. `main` alone is **932 / 14**, so the delta is exactly this
  file's 15 tests. `tests/test_public_surface.py` 166 passed. Clean `-W` docs
  build, zero warnings.

## Harness traps, already paid for

- `dlg.show()` runs a modal wait loop that neither `app.close()` nor a scheduled
  destroy escapes — it hangs. Drive the buttons instead.
- ⚠ **Round 1's brief said cancel buttons keep `closes = True` while non-cancel
  buttons are switched to `False`. That is now WRONG** — `closes` does not
  exist. Every accepted press closes via `Dialog`; a refused press does not.
- Press the real footer *widget*, not the spec's `command`. Invoking the command
  skips `Dialog`'s wrapper, which is where the veto, the result stamp and the
  close all live. `_press` / `_press_text` in the test file do this correctly.
- Probe output must be ASCII — this box's console is cp1252.

## Deliverable

Append a **Round 2** section to **`REVIEW.md`** at the repo root: for each
finding, `file:line`, root cause (not just symptom), the suggested minimal
change, and a severity of **blocking** / **should-fix** / **nit**. Triage
everything — there is always something to find, and without the severity split
there is no stopping rule.

The coverage gap named above is the most likely place for a blocking finding.
If you conclude `query.py` and `datedialog.py` need tests before this ships,
say so — the implementer flagged it rather than fixing it precisely so the call
would be yours.
