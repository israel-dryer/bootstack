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

## Explicitly out of scope

Marker cleanup to grow the headless job (#380 records the 494 errors), the macOS
Tk 9 leg (#378), #432 itself beyond reading what CI reports, #447/#449, and
pinning Tk scaling in `conftest` — that last one is worth doing and is its own
change, because it alters what every pixel-exact test measures.
