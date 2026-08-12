# Handoff — #447 on Linux: dialog focus and Enter reach nothing

**For an agent on the WSL box.** Written 2026-08-12 from the Windows box, which
cannot run any of this. Everything below is measured unless it says otherwise.

**Read `CLAUDE.md` and `REVIEW-PROTOCOL.md` first.** This file assumes them.

---

## The one question you are here to answer

**Is this X11, or is it X11 WITH NO WINDOW MANAGER?**

CI runs the suite under `xvfb-run`, and **Xvfb has no window manager at all.**
Nothing assigns focus to top-level windows, nothing maps them the way a real
session does. Tk's focus model leans on the WM for exactly that, and the failures
below are all focus-shaped — including `focus_lastfor()` returning the **empty
string**, which is not "the wrong widget", it is "no window in this toplevel has
ever held focus".

WSL is the only box in the project that can tell those apart, because **WSLg
gives you a real compositor** while `xvfb-run` gives you none, on the same
kernel, the same distro and the same Tk build.

That distinction decides what #447 IS:

| if it fails under | then |
|---|---|
| Xvfb only, passes under WSLg | a **CI environment** problem. Fix by running a WM in CI (`openbox`/`matchbox`), not by touching the product |
| **both** | a **real X11 product bug** in dialog keyboard handling — which `0.3.1` just shipped, on a platform bootstack publishes for |
| neither (all green) | the CI failures are specific to GitHub's runner; say so and stop |

⚠ **Do not skip straight to fixing.** This is the fork the whole issue turns on,
and it is one command each way.

---

## Environment setup

Debian/Ubuntu **package tkinter separately, and IDLE too** — that is #430's whole
story. Install both plus a display:

```bash
sudo apt-get update
sudo apt-get install -y python3-tk python3-pip xvfb openbox
python3 -m pip install --upgrade pip
python3 -m pip install -e .          # from the repo root
python3 -m pip install pytest
```

Python floor is **3.12** (`requires-python`). Check what you have and record it —
CI runs 3.12 and 3.13 and both fail identically.

**Record the Tk build before anything else.** This project has no Tk 9 box at all,
and the whole scroll-event and DPI contract differs between 8.6 and 9:

```bash
python3 -c "import sys, tkinter; print(sys.platform, sys.version.split()[0], 'tcl', tkinter.TclVersion, 'tk', tkinter.TkVersion)"
```

---

## The three runs, in this order

```bash
# 1. WSLg — a real compositor.  Do NOT set DISPLAY by hand; use what WSLg gives.
python3 tests/run_gui.py -q

# 2. Xvfb, no window manager — what CI does today.
xvfb-run -a -s "-screen 0 1280x1024x24 -dpi 96" python3 tests/run_gui.py -q

# 3. Xvfb WITH a window manager — the arm that isolates the WM.
xvfb-run -a -s "-screen 0 1280x1024x24 -dpi 96" sh -c 'openbox & sleep 1; python3 tests/run_gui.py -q'
```

⚠ **Never pipe these to `tail`** — you capture `tail`'s exit 0 and lose the real
one. Redirect to a file, capture `$?` on the very next line, then grep the file.

⚠ **`run_gui.py`, not bare `pytest`.** Creating a second Tk root in one process
crashes natively, so several modules need their own process.

If you want the fast loop instead of the full suite, these two files carry 7 of
the 8 failures:

```bash
python3 -m pytest tests/widgets/public/test_dialog_enter_key.py \
  tests/widgets/public/test_dialog_press_contract.py -q -p no:cacheprovider
```

---

## What CI measured, for comparison rather than trust

GitHub `ubuntu-latest`, xvfb, **identical on Python 3.12 and 3.13**, run
`31591527788`. Shared leg: **7 failed, 1004 passed, 14 skipped in 74s**.

| test | message |
|---|---|
| `test_dialog_enter_key::test_enter_in_a_text_area_inserts_a_newline_and_keeps_the_dialog_open` | `precondition: focus is on the body widget, not ''` |
| `test_dialog_enter_key::test_enter_in_a_text_field_still_submits` | same |
| `test_dialog_enter_key::test_enter_in_a_read_only_text_area_still_submits` | same |
| `test_dialog_press_contract::test_enter_presses_the_default_button` | `Enter did not press the default button` |
| `test_dialog_press_contract::test_enter_on_the_default_button_invokes_it_once` | `one press should run one command, ran []` |
| `test_dialog_press_contract::test_enter_on_a_focused_button_does_not_also_press_the_default` | `Enter ran more than the focused button: []` |
| `test_dialog_press_contract::test_enter_on_a_disabled_button_still_reaches_the_default` | `Enter did not reach the default button: []` |

Plus one that is probably a **separate issue** — investigate only after the
above, and file it on its own rather than folding it in:

| `test_appshell_shortcuts::test_bare_b_does_not_toggle_the_sidebar` | `assert '' == 'b'` |

⚠ **The Linux shared leg selects ~1025 tests where Windows selects 1068.** That
43-test gap is expected (platform-gated tests), not tests vanishing. Confirm with
`--collect-only -q` rather than assuming either way.

---

## Already ruled out BY MEASUREMENT — do not re-derive

Each of these cost real time on the Windows box. Re-testing them is waste.

- **NOT a `Select` emitting at construction.** With `bind_all("<<Change>>")`
  installed *before* the widget is built: **0 events** from construction, with or
  without `value=`, and exactly one from an ordinary set. (An earlier session
  claimed the opposite; it was wrong and is withdrawn.)
- **NOT an event leaked by the scene reset destroying a widget.** Arm 2 of
  `development/probe_407_scene_reset.py`: **0 leaked, with and without a drain.**
  A drain was added to `_reset_scene` on that basis and then removed.
- **NOT an exception inside the Tk callback.** That was the one candidate reading
  the guard could not exclude — anything raising in the toplevel's Return binding
  goes to `report_callback_exception`, which prints and returns, so the binding
  completes having done nothing and the test sees only `calls == []`.
  `development/probe_446_disabled_button_enter.py` now collects that channel and
  `bgerror`, and a real failing run carried **neither**.
- **NOT #432.** The Linux leg **ran to completion** — all 33 legs executed and
  reported. It did not exit silently mid-run. #407 appears to have removed that,
  and #432 should be closed or re-scoped on this evidence.
- **NOT the guard's logic.** `_key_was_consumed` sees `TButton` in the bindtags
  and returns `not instate(["disabled"])`, which is `False` for a disabled
  button, so the toplevel binding should invoke the default every time. On the
  failures the preconditions all passed first: toplevel mapped, footer button
  mapped, focus asserted taken.

---

## What is known about the mechanism

`focus_lastfor()` returns the **empty string**. Not the toplevel, not a wrong
widget — empty. In the same family, `focus_set()` is a **silent no-op** when the
widget or any ancestor is unmapped: `TkSetFocusWin` walks the ancestry and
returns without setting anything, reporting nothing. That is the mechanism behind
the already-fixed #437 flake, and it is the strongest lead here.

On Windows the same shape appears at **4/50 and 2/40 of five-file runs** — rare
and never explained. On Linux/Xvfb it is 7 failures in one run on both Python
versions. **A near-deterministic reproduction is the thing this issue has never
had.** Use it.

---

## Traps this project has already paid for

- ⚠ **Do not settle anything by re-running.** At a low rate a green batch is the
  expected outcome either way. The control has to **create** the condition and
  report a rate. `development/probe_437_focus_flake.py` is the worked example:
  it forces packed-but-not-yet-updated widgets and reports 5/10 vs 0/10.
- ⚠ **A probe that finds nothing must be proven able to find something.** Note
  that `probe_446_leaked_after_jobs.py` has **no positive control**, so its zero
  is uncontrolled — do not cite it as settled.
- ⚠ **Tests must fail for the right reason.** A pre-fix `AttributeError` proves
  nothing.
- ⚠ **Run the baseline before the fix**, so the transition is observed.
- ⚠ **A control that does not reach the code path under test is
  indistinguishable from a fix that works.** This happened on 2026-08-12: a
  control disabled a retry budget, the test passed, and it looked like the fix
  held — the give-up path was simply never reached. Forcing the condition itself
  showed the pre-fix test passing while measuring nothing.
- ⚠ **Compare within one process.** `winfo_rooty()` is not comparable across runs.
- ⚠ **Probe output ASCII-only** — a Windows console is cp1252 and this file has
  to be readable on both boxes.

---

## What to hand back

Write it into **`development/`**, not a scratch directory. This project has
already lost one handoff artifact and one whole patch that way: **an artifact
only survives if it is IN THE REPO.**

Report, in this order:

1. The three runs' results, with the **Tk version and distro** beside them.
2. **The verdict on the fork at the top** — Xvfb-only, or X11 generally.
3. If it is the missing WM: say so plainly, because the fix is then one line in
   `.github/workflows/ci.yml` (PR #451, branch `ci/test-workflow-380`) and the
   product is fine.
4. If it is real on X11 with a compositor: that is a **product bug in `0.3.1`'s
   dialog keyboard work on Linux**, and it needs an issue of its own with the
   measurement, not a test change.
5. Anything you ruled out, so the next session does not re-derive it.

⚠ **Do not change product code on this pass.** Measure, decide the fork, report.
`REVIEW-PROTOCOL.md` gate 1 exists because this project spent four review rounds
on test scaffolding a week ago.

---

## Context you may want

- **#447** — this issue. On `0.3.x — Patch line`.
- **PR #451** / branch `ci/test-workflow-380` — the CI workflow whose first run
  produced all of the above. Not merged, deliberately, until this is understood.
- **#407** (merged, `288d2596`) — the scene-reset fix; the suite went 215s → 56s
  on the shared leg and #432 stopped reproducing.
- **#449** — a separate flake, `test_select_change_event_value_space`.
- `development/review-426-439-440-441-dialogs.md` — the four-round record for the
  dialog work these tests cover.
