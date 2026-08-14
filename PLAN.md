# PLAN — #380, a CI workflow that runs the suite

Branch `ci/test-workflow-380`, off `main` at `ece32a38`.

## Round cap: 2

`REVIEW-PROTOCOL.md` gate 3. No public surface changes, so this is patch-safe.

⚠ Gate 1: **a round is triggered by a non-empty `git diff <range> -- src/`.**
This branch is expected to touch `.github/` and `tests/` only, so the likely
number of review rounds is **zero**. If `src/` does change, that is a signal the
branch has grown past its scope — stop and re-read this file before continuing.

## Why now, and what changed

`.github/workflows/` has only `docs.yml` and `release.yml`, so **nothing runs the
suite**. Every Tk 9 bug so far (#372, #375, #376) was found by a user or by hand.

The issue has been open a long time because it was expensive. Both objections
have weakened:

- **The suite was slow.** #407 landed on 2026-08-12: full `run_gui.py` went from
  ~5 minutes to **66–88s**. Running it on every push is now cheap.
- **The design was unknown.** It is not. **`D:\Development\ttkbootstrap` has a
  working `ci.yml`** for the same toolkit and the same shared-root design, whose
  `conftest.py` says it followed bootstack's approach. This is adaptation, not
  design.

## What #380's own measurements say — read before scoping

Recorded on the issue and **not to be re-derived**:

- **`-m "not gui"` is NOT a usable headless filter.** It selects 741 tests, and
  running that selection with root creation blocked gives **11 failed, 222
  passed, 14 skipped, 494 errors** — most nominally non-gui tests still pull the
  session `app` fixture. Growing a headless job past ~222 tests needs marker
  cleanup first, which is **out of scope here**.
- **Some tests run headless and report garbage silently.** `Treeview.bbox()`
  returns `''` — not an error — until the window is mapped, so a geometry
  assertion without a display compares nothing to nothing and passes. This is the
  vacuous-pass mode that let #358 ship twice. **A headless job must therefore be
  an explicit allowlist, never a marker filter.**
- **Scaling assertions cannot be faked.** `detect_scale_factor()` is
  `winfo_fpixels('1i')/72`, so under Xvfb it returns the virtual screen's DPI. At
  Xvfb's common 75 dpi default a padding-scaling bug becomes structurally
  invisible. ttkbootstrap's answer is `-dpi 96`, with the reasoning written into
  its workflow.

## The jobs

1. **`headless`** (ubuntu, no display, no xvfb) — an **explicit allowlist**, per
   the trap above. Measured on this box with `tkinter.Tk.__init__` patched to
   raise: **174 passed**, being `tests/test_public_surface.py` (166) and
   `tests/widgets/public/test_tk9_scaling_baseline.py` (8). A `ubuntu-latest` job
   with no display would have caught #375.
2. **`tests`** — matrix over **ubuntu (xvfb) / windows / macos**, on the floor
   Python (**3.12**, from `requires-python`) and 3.13. Runs
   `python tests/run_gui.py`, NOT bare `pytest`: the isolated legs genuinely need
   their own processes, and bare `pytest` would not give them one.
3. **`docs`** — a clean `-W` Sphinx build. `docs.yml` only deploys after a
   successful release, so a broken cross-reference currently reaches `main`
   unnoticed until release time.

⚠ **NO macOS + Tk 9 leg.** #380 itself says it would be **red from day one**
until #378 is fixed (the suite cannot complete on Tk 9 at all), and it is
unverified whether Tk-on-Aqua works on GitHub's runners. A permanently red leg
teaches people to ignore the workflow.

## The coverage gaps, folded in as #380 asks

`testpaths` is `tests/cli`, `tests/widgets/public`, `tests/data`, so anything
outside those **never runs**, in CI or locally:

- **`tests/widgets/*.py` — 12 files, 25 tests.** Verified today: **all 12 pass
  individually**, each in its own process, because each builds its own root. They
  go into `run_gui.py`'s `ISOLATED` list, which is exactly what that list is for.
- **`tests/test_public_surface.py` — 166 tests**, the guard for the curated
  public namespace (PR #104), which the widget-review standard lists as a verify
  step. It needs no display, so it rides the headless job — and gets a local leg
  too, so `run_gui.py` and CI agree about what "the suite" means.

## Verification

1. `python tests/run_gui.py` green locally **with the new legs**, counts recorded
   beside the commit. Expect **+25 and +166** over today's 1250 / 22.
2. The headless allowlist re-measured with root creation blocked.
3. **The workflow's own first run is the real test**, and it is the one thing
   that cannot be checked from this box. Two questions it answers for free:
   - **#432** — does the Linux shared-root leg still exit silently mid-run? It
     may not, now that #407 removed the widget accumulation. **Do not scope #432
     before reading that run.**
   - Whether Windows and macOS runners agree with the two boxes here.

⚠ **A first CI run that fails is a RESULT, not a setback.** The whole point is
that nothing has ever run this suite anywhere but two developer machines.

## AMENDMENT (2026-08-14) — the Linux leg, after the WSL box reported

The first CI run was the "result, not a setback" this plan anticipated. It came
back red on both Linux legs, and answering *why* is what the WSL box was briefed
to do. It has now reported, so the branch takes on exactly what is needed to make
the Linux leg green — and nothing else.

**#447 was out of scope above and now is not.** That is not scope creep: the
answer turned out to be a property of the *workflow this branch authors*, not of
the product. There is no way to land a Linux leg without deciding what display it
runs on.

### What changed, and why each is here

1. **`ci.yml` starts a window manager.** Under X11 it is the window manager, not
   the server, that assigns input focus to a newly mapped top-level window. Bare
   `xvfb-run` starts none, so a dialog is mapped but never focused and the
   toplevel's `<Return>` binding has nothing to fire against. Measured on WSL
   across three arms with only the window manager varying: **7 dialog failures
   without one, 0 with one**, deterministic in both directions.
   ⚠ The poll on `_NET_SUPPORTING_WM_CHECK` is load-bearing. A window manager
   that fails to start silently reproduces #447 exactly, which reads as a product
   bug — that false result was measured once already on the WSL box.
2. **#434 / #431 — the NumLock bit is resolved per platform.** Bit 8 is `Mod1`,
   and what `Mod1` carries is the platform's business: NumLock on Windows, **Alt
   on X11**, Command on Aqua. Hardcoding 8 asserted a different key on each
   platform. Verified the replacement bit is genuinely delivered (`state seen =
   16`) rather than dropped, so the test still carries a real modifier instead of
   quietly becoming a copy of the no-modifier control beside it.
3. **#433 — `cget("padding")[0]` read through `str()`.** Tk 8.6.12 on Ubuntu
   hands back a `_tkinter.Tcl_Obj` where other builds return a string. The
   padding is identical; only the binding's surfacing of it differs.
4. **`test_capture_restores_a_window_that_was_not_topmost`.** Not previously
   filed, and **only a window manager can expose it**: the test skips where
   always-on-top is not honored, so bare Xvfb never ran it. Always-on-top is a
   request answered asynchronously, which `_pin` already polls for on the way in
   — the assertion did not on the way out. Measured: the restore lands in ~1 ms,
   but the immediate read still returns the old value. **Product code is
   correct**; `capture.py` restores only what it changed. Non-vacuity confirmed by
   disabling that restore and watching the polled assertion still fail.

### `src/` IS UNTOUCHED — gate 1 therefore opens no round

`git diff main...HEAD -- src/` is empty, verified rather than assumed. Every
change above is `.github/` or `tests/`. Under `REVIEW-PROTOCOL.md` gate 1 that is
**zero review rounds**, against the cap of 2 declared at the top of this file.

### Measured, on the WSL box, at `5921dc41`

Ubuntu 22.04.5, Python 3.13.11, Tk 8.6.12, `pandas` absent (so the data leg reads
125 / 4 — the documented environmental pair, not a discrepancy). 33 legs.

| arm | exit | passed | failed | skipped |
|---|---|---|---|---|
| Xvfb **+ window manager** | 0 | **1427** | **0** | 22 |
| Xvfb **bare** — what CI does today | 1 | 1418 | **7** | 24 |

⚠ **It reconciles against itself**: `1418 + 7 failed + 2 extra skips = 1427`,
the two extra skips being the capture topmost tests standing down where no window
manager honors always-on-top. And the 7 are exactly the #447 cluster, so **the
test fixes above did not mask it** — remove the window manager and it returns.

⚠ **This does NOT reconcile with the `1449` recorded for this branch earlier**,
which CLAUDE.md already flags as never having been reconciled. 1427 is a Linux
figure and the 1449 was not; platform gating differs, so they are not the same
quantity. **Do not repair the arithmetic by picking whichever number closes the
gap** — re-measure per platform. CI's own matrix now reports all three.

## Explicitly out of scope

Marker cleanup to grow the headless job (#380 records the 494 errors), the macOS
Tk 9 leg (#378), #452 (the macOS runner hang) beyond leaving that leg out, #432
itself beyond reading what CI reports, #449, and pinning Tk scaling in `conftest`
— that last one is worth doing and is its own change, because it alters what
every pixel-exact test measures.
