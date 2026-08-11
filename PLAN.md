# PLAN — `0.3.1 — Dialog keyboard and modality`

Branch `fix/dialog-keyboard-modality`, off `main` at `78f107f9`.
Issues: **#426, #439, #440, #441**. Written before implementation, per
`REVIEW-PROTOCOL.md`.

## What this branch is supposed to do

Four bug fixes, all **patch-safe**: none adds public surface, and none is a
regression from `0.3.0` — all four exist in `0.2.3` too. That is what made
shipping `0.3.0` first and patching after the right call.

Three of the four (#439, #441, and #426's blast radius) are keyboard behavior;
#440 is modality. They are batched because #439 and #441 touch the same binding
in `Dialog._create_standard_buttons` and would otherwise conflict.

## Standing constraints

- **#441 must stay INTERNAL.** The issue floats three options and one of them —
  letting a widget *declare* that it consumes Enter — is new public surface,
  which would push the whole release to a minor. A bindtag test or asking the
  focus widget whether it is multi-line both stay inside a patch.
- **No new public surface anywhere on this branch**, for the same reason.
- Probes go in `development/` (persistent), never a session scratchpad — a
  handoff artifact only survives if it is in the repo.
- Probe output must be **ASCII** (this box's console is cp1252).

## The four fixes

### #426 — the migration error names kwargs that do not exist

`widgets/_core/container.py:229` tells the user to use `align_self=` /
`justify_self=`. The shipped keys are `FLEX_CHILD_KEYS` at `container.py:29`:
`grow`, `horizontal`, `vertical`, `margin*`, `index`. `align_self` appears
nowhere else in `src/` — the error string is its only occurrence. They were the
design-stage names; the rename is recorded in `docs/_dev/layout-redesign.md:13`.

Because `align_self` is not a recognized layout kwarg it is not stripped by
`_split_layout_kwargs` and reaches the ttk constructor, so following the advice
verbatim yields `TclError: unknown option "-align_self"`.

**Fix:** rewrite the message to name the real keys and their per-axis values
(from `grid_sticky`, `container.py:234`). Message-only.

**Also fix `CLAUDE.md`**, which quotes the wrong message as a *good* error under
Layout and tells the reader to trust it over the file. The issue calls this out
explicitly; fixing one without the other leaves the wrong names in circulation.

### #439 — the default button never receives focus

`dialog.py:544` calls `default_button.focus_set()` and `DialogButton.default` is
documented as "focused, triggered by Enter". Measured: `focus_lastfor()`,
`focus_get()` and Tcl's `focus` all report the **toplevel**.

**Hypothesis to verify before fixing:** this is the mechanism already recorded in
`CLAUDE.md` from #437's flake — **Tk's `focus_set()` is a silent no-op when the
widget or any ancestor is unmapped.** `TkSetFocusWin` walks the ancestry and
returns without setting anything, reporting nothing. The footer is built before
the window is deiconified, so the button is unmapped at the call.

**Fix direction:** re-issue focus once the window is actually mapped. Defer on
the **root**, not the widget (a widget-owned `after` callback is deleted with the
widget and fires as an orphan), and guard for a dialog closed before it runs.

⚠ **This rescopes #437's Enter stand-down guard.** Today no dialog rests on its
default button at open, so the guard is mostly dormant; once focus lands the
guard becomes live on the first Enter of every dialog. That is what it was
written for, but it must be re-tested rather than assumed. A `0.3.0` test was
deliberately loosened so fixing #439 could not turn it into a precondition
failure — check that it still means something.

### #441 — Enter in a multi-line field submits the dialog

The toplevel's `<Return>`/`<KP_Enter>` binding stands down only when
`"TButton" in pressed.bindtags()` (`dialog.py:571`). A `TextArea` handles Enter
too and carries no such tag, so the newline is inserted **and then** the dialog
closes on top of it (measured on the issue: text is `'\n'` at the press).

**Rule chosen: a bindtag test, generalized from `TButton` to a small set.**
Bindtags are how Tk itself decides dispatch, so asking "does this widget's class
already bind Return?" is the same question the toolkit answers. `Text` covers
`TextArea` and `CodeEditor`. This is the option that stays internal.

Open question to settle empirically: how a **disabled/read-only** multi-line
widget should behave. The `TButton` arm already has a disabled exception — a
disabled button's class binding runs but `invoke` does nothing, so nothing
answered the key. Measure whether the same holds for a read-only `Text` before
deciding whether it needs the same exception.

### #440 — a nested modal drops the outer dialog's grab permanently

Measured on the issue: `grab_current()` is the dialog before a nested
`bs.alert(...)` and **`None`** after. The inner dialog's `grab_set()` takes the
grab over; destroying it releases the grab outright rather than restoring the
one it displaced. The outer dialog stays on screen and still blocks its caller
in `show()`, while the user can click straight back into the main window.

**The blast radius is smaller than the issue assumes.** Every dialog in the
framework composes `Dialog` — `MessageDialog`, `QueryDialog`, `FormDialog`,
`ColorChooserDialog` and `FontDialog` all hold a `Dialog` rather than
reimplementing modality. So `grab_set` appears at exactly **two** sites:

- `dialog.py:357` — the shared modal path
- `datedialog.py:114` — `DateDialog.show` overrides `show` and has its own

**Fix:** at each site, capture `grab_current()` *before* `grab_set()`, and
restore it after `wait_window` returns. Guard the restore: the previous grabber
may have been destroyed in the meantime, so check `winfo_exists()` and swallow
`TclError` — a failed restore must never escape into a teardown path.

`query._on_submit` is named on the issue as a second instance of the shape. It
is a *caller* of the nested-modal pattern, not a second grab owner, so the
centralized fix should cover it; verify rather than assume.

## Invariants

- **No grab leaks.** After any dialog closes, `grab_current()` is whatever it
  was before that dialog opened — `None` at the outermost level.
- **A dialog that is visually modal is actually modal**, at every nesting depth.
- **Exactly one thing answers Enter.** Either the focused widget handles it or
  the default button fires — never both, never neither.
- **Escape still closes**, at every nesting depth, unchanged by this branch.
- Nothing here changes public API. `tests/test_public_surface.py` must stay
  green.

## Verification

Each fix needs a probe in `development/` **with a control** — an arm that
reproduces the pre-fix behavior, so a passing post-fix run means something. The
recurring failure mode to avoid: a probe whose arms all drive through the same
changed code path silently becomes its own control.

Specifically:

- A probe must be **runnable on every box it is meant to inform** — SKIP an arm
  the machine cannot exercise, never `sys.exit` on the first one.
- A probe that **forces the precondition it is measuring** proves nothing. This
  is exactly how #439 hid: `probe_437_round3.py` called `top.focus_force()` and
  `button.focus_set()` before generating the key, so it measured a state it had
  created. Do not force focus in the #439 probe.
- `dlg.show()` runs a modal wait loop that a close scheduled with `after` does
  **not** break. Drive it by invoking a real footer button, and poll for the
  modal grab **and the footer being mapped** as the barrier — the grab is set
  before the geometry manager maps the footer's children at idle. `_drive()` in
  `test_dialog_press_contract.py` is the worked pattern.
- Regression test per fix, per the protocol.

Full suite before handoff: `py -3.12 tests/run_gui.py` — **and at the commit
being shipped**, not at the last one that happened to be measured. `0.3.0` let a
flake into `main` exactly that way.

Baseline to beat, measured 2026-08-11 on `main` at `ab11f37c`: **1159 passed /
21 skipped over 20 legs**, shared leg 962/14. Re-measure rather than trusting
this number; the shared leg selects 975 tests, so any reported total above that
is impossible.

## What measurement changed about this plan

Recorded because each of these was decided by a probe rather than by reading,
and a reviewer should not have to re-derive them.

- **#439's obvious fix does not work.** Focusing after `deiconify()` was the
  plan; measured, the button is **still unmapped** once both `deiconify()` and
  `update_idletasks()` have returned, so that would have been another silent
  no-op. Focus waits for the button's own `<Map>`
  (`probe_439_focus_timing.py`).
- **#439 needed a focus PRECEDENCE, not just a timing fix.** Making the default
  button focusable meant it stole focus from `QueryDialog`'s entry, which would
  have left `ask_string()` unable to accept typing and Space submitting an
  empty value. The control proved the entry had **never** been focused — the
  same defect, second instance — so this is a fix, not a regression, but the
  ordering had to become explicit: `Dialog._focus_target` (claimed by content)
  beats `Dialog._default_button`, resolved once in `show()` after the content
  is built.
- **#441's "general rule" is a trap.** Interrogating the bindtags for a real
  binding on the key looks principled and is measurably wrong: bootstack's own
  `TextField` binds `<Return>` as an instance binding to emit `submit`, so the
  widget that MUST keep submitting reads as "already handled". Tk also binds
  `TEntry <Return>` to the literal no-op script `# nothing`. The shipped rule
  is the bindtag allowlist, and `_key_was_consumed`'s docstring records why so
  it is not re-proposed (`probe_441_key_already_handled.py`).
- **A raw-tkinter probe measures the wrong population.** `TButton` has no
  Return binding in bare ttk; bootstack installs one at app construction
  (`_runtime/app.py:151`). A first draft concluded the framework's existing
  guard rested on a false premise. Measure inside a `bs.App`.
- **#440's blast radius was two sites, not four.** Every dialog composes
  `Dialog`, so the fix is `restore_grab` plus one call each in `Dialog.show`
  and `DateDialog.show`.

## Left deliberately undone

- **`CLAUDE.md` still quotes the wrong #426 message** as a good error. It must
  be fixed, but handoff state goes **straight to `main`**, never on a branch —
  a branch that edits it silently reverts `main`'s handoff at merge, which
  nearly happened with #410. Do it as its own `main` commit, and check
  `git diff main...HEAD -- CLAUDE.md` is empty before merging this branch.
- **`docs/widgets/dialog.rst` still refuses a press with `bs.toast(...)`**,
  which was adopted as a workaround while #440 was open. It is left alone: the
  page is now correct rather than merely lucky, and a toast is the better fit
  for a refusal anyway. Reverting it to `bs.alert(...)` is not required by this
  fix.

## Out of scope

- **#436** (`versionadded` convention) — undecided question, not scoped here.
- **#431/#432/#433/#434** — test-infrastructure bugs from the `0.3.0` capture
  work. Not dialog defects; do not bolt them on.
- Anything requiring new public surface (see #441's constraint above).
