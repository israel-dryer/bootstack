# Review brief — `widget.capture()` (#427)

Branch `feat/widget-capture-427`, off `main`. Written for the review session so
the reviewer does not re-derive what has already been measured, and knows where
the genuine soft spots are.

Origin: discussion #425, an external user wanting to share a dashboard view
without using the snipping tool. Comment posted on the discussion 2026-08-07.

## What it adds

One public method, no new top-level names:

```python
widget.capture(path, *, inset=0, settle=0.1) -> Path
```

On `PublicWidgetBase`, so it reaches every widget plus `App`, `AppShell`, and
`Window`. Backed by a new internal module `src/bootstack/_core/capture.py`.

## Decisions already settled — please do not re-litigate

Each of these was decided deliberately with the maintainer; the reasoning is on
#427 and in the session that produced this branch.

- **Path in, path out — no Pillow type in the public signature.** Returning an
  image object would couple the public API to Pillow and pre-empt the deferred
  public image handle. A no-argument `capture()` returning that handle stays
  available later as a pure addition.
- **No printing.** The Windows shell `print` verb cannot honor a printer name or
  a copy count, so those parameters would be documented and silently ignored on
  a whole platform. Measured on this box: `.pdf` resolves to `MSEdgePDF`, which
  registers no print verb at all.
- **Monitor enumeration stays internal.** `_runtime/window_utilities.py` already
  enumerates monitors for window positioning; publishing a second `Monitor` type
  would give the framework two answers to the same question. Unifying them is
  its own branch.
- **No capture event.** `capture()` is synchronous and returns the path, so an
  event would have no producer the caller did not invoke. Revisit only if
  capture ever becomes async or gains a framework-triggered entry point.
- **The window is raised before the grab, unconditionally.** Not a parameter.
  Capturing whatever happens to be on top is never what a caller wants.

## Verified, with measurements

Full GUI suite on this branch, `py -3.12 tests/run_gui.py`, exit 0:
**940 passed / 14 skipped** on the widgets+CLI leg (the recorded `main` baseline
is 930/14 — the difference is exactly the 10 new tests), **125 passed / 4
skipped** on data, all isolated legs green.

Docs: clean `-W --keep-going` build after `rm -rf docs/_build`, `build
succeeded`, exit 0.

## Controls that were run — this is the part worth trusting

A passing test proves nothing until it has been shown to fail. Three controls:

1. **The topmost-clobber defect reintroduced** (restore unconditionally rather
   than only when this code changed it): `test_capture_leaves_a_deliberately_topmost_window_pinned`
   fails with `assert 0`, while its opposite-direction arm still passes. So the
   failure is behavioral, not a broken harness.
2. **The `winfo_ismapped()` guard removed**: `test_detached_widget_cannot_be_captured`
   fails with `DID NOT RAISE`. Without the guard, capturing a detached widget
   silently succeeds and saves whatever was behind it.
3. **The negative-origin monitor trap**, on the `x=-2560` display attached to
   this machine: a naive `ImageGrab.grab(bbox, all_screens=False)` returns
   **1 distinct color** (pure black, no exception), while `capture()` returns
   **169**. The `all_screens` handling is load-bearing, not defensive.

An earlier version of the probe **passed all ten of its checks while capturing a
browser window** — it verified the rectangle and never the content. That is why
the probe now toggles the theme between two captures and requires the pixels to
change: it is causal proof the grab is reading this application. Measured delta
211.6 where identical would be 0.0.

## NOT verified — the open gap

**Windows only.** Nothing here has run on macOS or Linux. Run
`development/verify_427_capture.py` on each; it prints the platform, Tk version,
Pillow version, monitor layout, and which capture backend is active, and skips
arms that do not apply rather than failing them.

On macOS specifically: a missing **Screen Recording permission** makes the system
return a picture of the desktop with no windows in it and raise nothing. The
theme-toggle arm detects exactly that, and the probe prints a hint naming the
permission when it trips.

## Look hard at these

Self-flagged; each is a place I am not confident.

1. **The Linux subprocess fallback crops with the wrong origin, probably.**
   `_grab_via_subprocess` shells out to a full-screen tool and then does
   `image.crop(bbox)`, where `bbox` is in *virtual-desktop* coordinates. The
   grabbed image's origin is whatever the tool treats as (0, 0), which on a
   multi-monitor setup — and certainly with a negative-origin display — is not
   the virtual-desktop origin. Single-monitor Linux should be fine; multi-monitor
   is likely wrong. I could not test it. This is the most likely real defect on
   the branch.
2. **`settle()` pumps the event loop, so a capture is re-entrant.** It calls
   `root.update()` in a loop, and `update()` from inside a click handler
   processes further events — including a second click on the same Export
   button, which would start a second capture inside the first. Whether that
   matters in practice, and whether it wants a guard, is a real question.
3. **`winfo_ismapped()` does not catch an *obscured* widget**, only a hidden or
   detached one. That is by design and documented, but confirm the how-to page's
   wording matches the actual guarantee.
4. **Capturing the app grabs the client area, not the window frame.**
   `winfo_rootx/rooty` exclude the native title bar on Windows. macOS geometry
   conventions differ and need measuring on that box.
5. **`settle=0.1` means every capture blocks for a tenth of a second.** Chosen so
   a capture taken right after a save dialog closes does not photograph the
   dialog's leftover pixels. Reasonable default or not?
6. **The tests deliberately assert no image content.** What the pixels show
   depends on what else is on the machine's screen, which no assertion controls;
   content correctness is the probe's job. The test module says so at the top —
   worth a look to confirm that division is the right one rather than a gap.

## How to run everything

```
py -3.12 -m pytest tests/widgets/public/test_capture.py -q
py -3.12 tests/run_gui.py
py -3.12 development/verify_427_capture.py
rm -rf docs/_build && py -3.12 -m sphinx -b html docs docs/_build/html -W --keep-going
```

`development/screencap.py` and `screencap_demo.py` are the original prototype the
issue references, kept for provenance. They are **not** what shipped — the
prototype's printing half was dropped and its topmost handling was a defect.