# Branch handoff — #429, the settle guard (`feat/widget-capture-427`)

Written 2026-08-10, on the branch, because `CLAUDE.md` **must not be edited on a
feature branch** — its handoff state lives on `main` only, and a branch that
edits it silently reverts main's copy at merge (the trap that nearly bit #410).
Everything below is what `CLAUDE.md` will need to say once this merges; the
last section lists the exact lines to change.

⚠ **`CLAUDE.md` is STALE about this branch on both counts.** It says
"**24 commits, head `ac9a87a3`**" and "**#429 is open against its own code** —
settle that, then PR it", which reads as though nothing had been done. Read
this file instead.

Measured 2026-08-10: **31 commits ahead of `origin/main`, head `d7dfd5a1`**.
⚠ Do not arrive at that by adding this session's 4 commits to the recorded 24 —
that gives 27, and it is wrong. The branch was rebased onto `main` after `0.2.3`
and the old figure was counted against a different base. `git rev-list --count
origin/main..HEAD` settles it in one command, which is the rule this file's
parent already states.

## Where #429 stands

**Half fixed, half documented as a known limitation. Not open in the sense
CLAUDE.md implies.**

#429 was filed as *a click during `settle()` re-enters the handler and starts an
overlapping capture*. The first fix (`e616f5dc`) stopped `settle()` dispatching
at all. **That fix caused a worse defect and has been reversed.**

### The defect the first fix caused — REAL, and fixed

On macOS the area a closing window uncovers is repainted only while the event
loop is turning. A settle that dispatches nothing photographs whatever was
there before.

Measured through the **public** method, following the pattern its own docstring
teaches — a real modal dialog (`grab_set()` + `wait_window()`) dismissed through
its own close path, then `capture()`:

| settle | result |
|---|---|
| sleep-only (`e616f5dc`) | **51400 of 60800 px wrong** — the saved file is a picture of the dismissed dialog |
| dispatching | 0 px |

⚠ **It needs no dialog at all.** `capture()` raises the window as documented
behavior, so *any* other window sitting over the application is uncovered by the
capture itself. With one window overlapping and left open, the saved file is a
picture of that window: **53314 px against a 145 px reference**. This is the
ordinary state of a desktop app, which is what makes it a real bug rather than
an edge case.

`settle()` dispatches again. Regression coverage is
`test_settling_repaints_the_area_a_closed_window_uncovered`, which fails against
unfixed source at 64000/64000 px.

### The input half — NOT fixed on macOS, and that is a decision

`tk busy hold` blocks input while the loop turns. **It does nothing on macOS.**

```
tk 8.6.17, windowingsystem aqua
tk busy status -> 1          (reports success)
._Busy         -> winfo_ismapped() == 0    (never mapped)
winfo containing at the button's position -> the button
```

Reproduced in **plain tkinter with no bootstack involved**, and identically
whether the hold is placed on the toplevel, on the content frame, or followed by
an explicit `raise`. So it is the toolkit, not the framework, and not a wrong
invocation. Confirmed end to end by hand: a real click re-enters the handler.

**Maintainer decision (2026-08-10): keep the hold anyway.** X11 and Win32 map
the busy window and are expected to honor it, and it costs nothing where it does
not work. What changed instead is that nothing claims it works everywhere — the
`settle()` docstring records the measurement, the how-to carries a note plus the
workaround (disable the button around the export), and the test that asserts the
hold is requested and released says in its docstring that this is **not**
evidence input is blocked.

⚠ **Do not "fix" this by making `settle()` stop dispatching again.** That is
where this started, and it trades a UX annoyance for wrong output. The relative
cost is the whole point: the repaint defect produces a picture of the wrong
thing; the input defect produces a stacked save dialog on an impatient
double-click.

## What the Windows/Linux leg must answer

**Arm 0 of `probe_429_busy_during_settle.py` is the headline result**, not arm 3.
It reports whether the busy window is actually mapped and whether Tk's hit test
at a button resolves to it. If arm 0 says **no** on Windows too, the hold is dead
weight on every platform and should be stripped before the PR — that is a
one-line probe run rather than another manual click round.

```
py -3.12 development/probe_429_busy_during_settle.py      <- arm 0 decides the hold's fate
py -3.12 development/probe_429_settle_without_input.py
py -3.12 development/verify_427_capture.py
py -3.12 tests/run_gui.py
py -3.12 development/demo_429_busy_during_settle.py       <- manual, needs clicks
```

Also worth reading off the settle probe: if its **sleep-only arm comes back
clean on Windows**, the defect is macOS-specific and `e616f5dc` only broke one
platform. If it comes back stale, the branch has been broken on Windows since
2026-08-10 too.

## Things measured here that should not be re-derived

- **A synthesized click cannot test `tk busy`, by construction.**
  `event_generate` aimed at a widget delivers straight to that widget's bindings
  and never consults the busy window — it re-enters with `tk busy status`
  reading 1. Every automated attempt at the input question is a false negative.
  That is why `demo_429_busy_during_settle.py` needs a human.
- **`tk busy status` is not evidence the hold works.** It returns 1 on a
  platform that never maps the window. Check `winfo_ismapped()` and the hit
  test, which is what arm 0 does.
- **An invisibility measurement cannot prove a busy overlay is harmless.**
  "Busy is invisible in the photograph, 0 px" was recorded as evidence the
  approach worked; it was invisible because it was never mapped. Wherever arm 0
  says no, arm 3 is trivially true and means nothing.
- **The guard is on input, not on scheduled work.** A capture started from a
  timer still re-enters, because `tk busy` blocks what the window system routes
  by pointer position. `probe_429_capture_reentrancy.py` arm 1 records this as
  the known limit rather than a failure.
- **All three #429 probes used to drive their arms through `_capture.settle`**,
  so when the sleep-only version shipped their controls silently became the
  test — identical code in both arms, byte-identical images, and verdicts that
  said nothing. Strategies are pinned per-file now; only arms explicitly labeled
  `shipped` read the live implementation.
- **A destroyed target reaches `settle()`.** It flushes pending drawing first,
  so idle work queued before the capture can destroy the widget; the toplevel
  lookup is guarded for that, not just the `tk busy` calls.

## Suite state on this branch

Measured 2026-08-10 on macOS (Tk 8.6, `.venv/bin/python`), at **`d7dfd5a1`**:

| leg | result |
|---|---|
| widgets+CLI, shared root | 969 passed / 20 skipped |
| data | 125 passed / 4 skipped |
| `test_capture.py` (isolated) | 23 passed |

Clean `-W` docs build.

Two pre-existing reds, neither from this work:

- `test_appshell_shortcuts.py::test_bare_b_does_not_toggle_the_sidebar` fails at
  baseline with every change stashed. Not filed as far as this session knows.
- The capture leg showed environmental flakiness under `run_gui.py` on one of
  two full runs — 11 failures, all "cannot identify image file", passing clean
  on the re-run. Standalone it passes every time.

## The four commits

| SHA | What |
|---|---|
| `e4fd4af7` | the fix — dispatching settle + `tk busy` hold, `capture.py` / `base.py` / `test_capture.py` |
| `9aada08d` | how-to: correct what the pause guarantees |
| `a7d8941a` | re-point the three probes, add the manual demo |
| `d7dfd5a1` | say the input guard does nothing on macOS; add probe arm 0 |

## What `CLAUDE.md` needs when this merges

Do this **on `main`**, not here:

- `24 commits, head ac9a87a3` → **31 commits, head `d7dfd5a1`** (line ~164),
  counted with `git rev-list --count origin/main..HEAD` on 2026-08-10.
- The IN FLIGHT block and START HERE both say **#429 must be settled before the
  PR**. Replace with: the repaint half is fixed, the input half is a documented
  macOS limitation by maintainer decision, and what remains is the Windows leg
  (arm 0) then the PR.
- The unmilestoned-issues list counts **#429** among seven. It stays open —
  the input half is genuinely unresolved on macOS — but it is no longer
  "a defect in `capture()`'s own code" that blocks the PR.
- ⚠ The `944 / 14 at ef7e6421` figure is already flagged as stale in that file.
  Replace with the table above, **with its commit and date**, per the standing
  rule.
