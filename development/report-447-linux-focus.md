# Report — #447 on Linux: the fork is answered

**Written 2026-08-12 from the WSL box**, answering
`development/handoff-447-linux-focus.md`. Everything below is measured on this
box unless it says otherwise. **No product code was changed on this pass.**

---

## The verdict

# It is Xvfb-only. The missing window manager IS the bug.

The seven dialog-focus failures reproduce **only** on a display with no window
manager. Put any window manager on the same Xvfb display -- same kernel, same
distro, same Tk build, same Python, same commit -- and all seven pass.

**#447 is a CI environment problem, not a product bug.** The fix belongs in
`.github/workflows/ci.yml` (PR #451, branch `ci/test-workflow-380`). The dialog
keyboard work `0.3.1` shipped is **fine on X11**.

| arm | window manager | dialog failures |
|---|---|---|
| 1. WSLg (`DISPLAY=:0`) | Weston WM | **0** |
| 2. Xvfb, bare -- what CI does today | none | **7** |
| 3. Xvfb + `xfwm4` | Xfwm4 | **0** |

The window manager is the only variable that moves between arms 2 and 3, and
toggling it toggles the failures.

---

## The box

| | |
|---|---|
| distro | **Ubuntu 22.04.5 LTS** (WSL2, kernel 6.18.33.2-microsoft-standard-WSL2) |
| python | **3.13.11** (system `python3` is 3.10.12, below the 3.12 floor -- unusable) |
| tcl/tk | **8.6**, patchlevel **8.6.12** |
| bootstack | **0.3.1**, editable, from `d6c90534` |
| compositor | WSLg present (`/mnt/wslg`, `WAYLAND_DISPLAY=wayland-0`) |

⚠ **Still no Tk 9 anywhere in this project.** This box is 8.6 like the other
two. The Tk 9 scroll/DPI contract remains unexercised.

⚠ **`openbox` is NOT installed here and there is no passwordless sudo**, so arm 3
used **`xfwm4`**, which was already present. The control below proves it did the
job a window manager has to do; which window manager it is does not matter to the
result.

---

## The minimal reproduction

The two files the handoff names carry all seven failures, and they settle it in
about ten seconds:

```bash
T="tests/widgets/public/test_dialog_enter_key.py tests/widgets/public/test_dialog_press_contract.py"

python -m pytest $T -q -p no:cacheprovider                      # WSLg
xvfb-run -a -s "-screen 0 1280x1024x24 -dpi 96" \
  python -m pytest $T -q -p no:cacheprovider                    # bare Xvfb
xvfb-run -a -s "-screen 0 1280x1024x24 -dpi 96" \
  sh -c 'xfwm4 & sleep 4; exec python -m pytest '"$T"' -q -p no:cacheprovider'
```

```
WSLg           : 25 passed in 1.12s
Xvfb, no WM    : 7 failed, 18 passed in 11.20s
Xvfb + xfwm4   : 25 passed in 1.18s
```

**This is deterministic, not a rate.** Seven for seven, both directions. The
handoff notes that #447 "has never had a near-deterministic reproduction" -- this
is one, and it takes eleven seconds.

The failure messages under bare Xvfb match run `31591527788` **exactly**, all
five distinct strings:

```
precondition: focus is on the body widget, not ''
Enter did not press the default button
one press should run one command, ran []
Enter ran more than the focused button: []
Enter did not reach the default button: []
```

---

## ⚠ The control that saved this result -- read this part

**The first arm-3 run was worthless and looked exactly like a real answer.**

`xfwm4 --daemon & sleep 1` silently fails to start under Xvfb. The suite then
ran on an unmanaged display and produced output **byte-identical to arm 2** --
which reads as "a window manager changes nothing, so this is a product bug." That
is the precise trap `REVIEW-PROTOCOL.md` gate 4 and the handoff both warn about:
*a control that does not reach the code path under test is indistinguishable from
a fix that works.*

What caught it was refusing to accept the arm without proving the condition
existed. `development/probe_447_wm_present.py` asks the display two questions:

1. does the root window carry `_NET_SUPPORTING_WM_CHECK` (EWMH), and
2. does a mapped `Toplevel` get **reparented** into a frame -- `wm frame` differs
   from `winfo id`? A window manager reparents; a bare X server does not.

The reparent check is the load-bearing half: no external tool, it is what Tk
itself sees, and it holds for every window manager rather than only the EWMH ones.

**It reports a different answer on each arm, which is what makes it a control:**

| arm | `_NET_SUPPORTING_WM_CHECK` | reparented | verdict |
|---|---|---|---|
| WSLg | `"Weston WM"` | YES (`id=0x600003` vs `frame=0x20b929`) | WM present |
| Xvfb bare | none | NO (`id=0x200003` == `frame=0x200003`) | **no WM** |
| Xvfb + `xfwm4 --daemon` | none | NO | **no WM -- the arm was fake** |
| Xvfb + `xfwm4 &` | `"Xfwm4"` | YES (`id=0xa00003` vs `frame=0x2001e2`) | WM present |

Run it in CI too, if only once. It is the difference between "we start a window
manager" and "a window manager is running."

⚠ The probe deliberately does **not** call `wait_visibility()`. With no window
manager nothing delivers the `VisibilityNotify` it blocks on, so it hangs on the
exact arm it exists to measure. It pumps a bounded number of `update()` calls
instead. (It hung that way once before being fixed.)

---

## Why this is the mechanism, not a coincidence

It matches the lead the handoff already had. `focus_lastfor()` returning the
**empty string** is not "focus is on the wrong widget" -- it is "no window in
this toplevel has ever held focus." Under X11 it is the window manager that
assigns the input focus to a newly mapped top-level window; the server does not
do it on its own. With no window manager, a dialog is mapped but never focused,
so `focus_set()` inside it lands on an ancestry that is not in the focus path and
returns silently, and the toplevel's `<Return>` binding has nothing to fire
against.

That is the same silent-no-op family as the already-fixed #437 flake. It also
explains the Windows rarity the handoff records (4/50, 2/40): there the condition
needs a race to appear, whereas bare Xvfb creates it on every single run.

---

## The fix, concretely

Two edits to `.github/workflows/ci.yml` on `ci/test-workflow-380`.

**1. Install a window manager alongside Xvfb:**

```yaml
      - name: Install Tk and a virtual display
        if: runner.os == 'Linux'
        run: |
          sudo apt-get update
          sudo apt-get install -y --no-install-recommends xvfb tk openbox
```

**2. Start it before the suite, and wait for it to actually be there:**

```yaml
      - name: Run the suite (Linux)
        if: runner.os == 'Linux'
        run: |
          xvfb-run -a -s "-screen 0 1280x1024x24 -dpi 96" sh -c '
            openbox &
            for i in $(seq 1 50); do
              xprop -root _NET_SUPPORTING_WM_CHECK 2>/dev/null | grep -q "window id" && break
              sleep 0.2
            done
            exec python tests/run_gui.py -q'
```

⚠ **Do not use a bare `sleep 1`.** That is what produced the fake arm here. Wait
for the property, or run `development/probe_447_wm_present.py` as its own step
and let a missing window manager fail the job loudly. `xprop` comes from
`x11-utils`; add it to the apt line if the runner lacks it.

⚠ Keep `-dpi 96` -- the workflow's own comment explains why, and it is unrelated
to this.

**Everything else in that workflow is unaffected.** The `headless` job builds no
root, and Windows/macOS talk to win32/aqua directly.

---

## Ruled out, so nobody re-derives it

- **NOT a product bug in the `0.3.1` dialog keyboard work.** Green on X11 with a
  compositor (arm 1) and green on X11 with a plain reparenting window manager
  (arm 3). Two independent window managers, both clean.
- **NOT Wayland-versus-X11.** Arm 3 is X11 through and through and passes. The
  axis is window-manager-present, not the windowing system.
- **NOT Python 3.12-versus-3.13.** Measured on 3.13, which is one of the two legs
  CI reports failing identically. The 3.12 leg needs no separate check for this.
- **NOT #432.** Confirming the handoff: every leg ran to completion in all three
  arms and reported. Nothing exited silently mid-run.
- **NOT test-count drift.** All three arms select the same **1025** tests in the
  shared leg (`2 + 1009 + 14` and `9 + 1002 + 14`), and CI's `7 + 1004 + 14` is
  the same 1025. The 43-test gap against Windows is platform gating, as expected.
- **The `xfwm4 --daemon` failure is a launcher quirk, not a finding.** `xfwm4 &`
  works. `openbox` has no `--daemon` and is unaffected.

---

## Three other failures, none of them #447

All three are **window-manager-independent** -- they behave the same with and
without one -- so none of them belongs in this issue.

### 1. `test_bare_b_does_not_toggle_the_sidebar` -- real, Linux, deterministic

```
assert expanded._field.text == "b"
E  AssertionError: assert '' == 'b'
```

Fails in **all three arms**, including WSLg with a real compositor, and **5 runs
out of 5** on its own. The handoff guessed this was separate; it is, and it is
now stronger than a guess -- a window manager does not fix it. A `b` typed into a
focused field does not reach the field on this platform.

**This one is worth its own issue.** I have not filed it; that is the
maintainer's call.

### 2. `test_field_hidpi_padding` (2 tests) -- a test bug, this box only

```
low_pad = low._internal._field.cget("padding")[0]
assert int(high_pad) > int(low_pad)
E  TypeError: int() argument must be a string, a bytes-like object or a real
   number, not '_tkinter.Tcl_Obj'
```

Fails in all three arms here and **passed in CI**. `cget("padding")[0]` returns a
`_tkinter.Tcl_Obj` on **Tk 8.6.12** (Ubuntu 22.04) where CI's newer Tk returns
something `int()` accepts. The product is not implicated -- the test reads the
value without `str()`. It is a portability hole in the test that happens to be
invisible on all three machines CI currently uses.

### 3. `test_capture` -- environment-dependent, not a regression

| arm | result |
|---|---|
| WSLg | **9 failed** -- `OSError: X get_image failed: error 8` |
| Xvfb bare | 20 passed, 3 skipped |
| Xvfb + xfwm4 | 1 failed (`test_capture_restores_a_window_that_was_not_topmost`), 21 passed |

Under WSLg the capture rect comes back at coordinates like `(-32730, -32709)`,
so Weston is placing these windows where no screen covers them and the pixels
cannot be read. **`bootstack`'s own error message is correct and useful here** --
it names the rectangle and the likely cause. Nothing to fix for #447; note only
that screen capture is not measurable under WSLg.

---

## Runs, in full

Full logs are in this session's scratchpad and are not worth committing; the
per-leg summaries are:

| leg | arm 1 WSLg | arm 2 Xvfb bare | arm 3 Xvfb + WM |
|---|---|---|---|
| shared: `widgets/public` + `cli` | 2 F / 1009 P / 14 S, 42.9s | **9 F** / 1002 P / 14 S, 48.2s | 2 F / 1009 P / 14 S, 37.9s |
| `tests/data` | 125 P / 4 S | 125 P / 4 S | 125 P / 4 S |
| `test_appshell_shortcuts` | 1 F / 3 P | 1 F / 3 P | 1 F / 3 P |
| `test_capture` | 9 F / 12 P / 2 S | 20 P / 3 S | 1 F / 21 P / 1 S |
| all other isolated legs | pass | pass | pass |

Arm 2's 9 failures = CI's 7 dialog failures + this box's 2 `hidpi` failures.
Arms 1 and 3 are identical to each other on every leg but `test_capture`.

---

## Artifacts committed with this

- `development/probe_447_wm_present.py` -- the window-manager control. Reports a
  different answer per arm; that is the point.
- `development/report-447-linux-focus.md` -- this file.
