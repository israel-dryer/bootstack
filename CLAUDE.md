# bootstack — Claude Handoff

## Project overview

bootstack is a batteries-included Python desktop UI framework. It is **not**
advertised as a Tkinter wrapper — the goal is to abstract Tkinter away entirely
so that Tkinter's warts, naming conventions, and legacy API are invisible to the
user. Widget names, arguments, methods, and events are designed for modern Python
and ease of use, not compatibility with the raw tk/ttk surface.

**Design philosophy:** Opinionated and configurable within a reasonable range.
Go from nothing to something fast. The user should never need to `import tkinter`.

**Working directory:** `D:\Development\bootstack` (Windows box) — see Environment.
**Branch strategy:** `feat/*` branches off `main`. PRs go `feat/*` → `main`.

> 📓 **Session history lives in `docs/_dev/handoff-archive.md`** — every shipped
> initiative with its full root-cause analysis, decisions, and gotchas. This file
> keeps only what is OPEN plus the standing rules. **Read the archive when you
> touch an area it covers** (it is indexed by issue/PR number); don't re-derive a
> root cause that is already written down there.
>
> ⚠ The archive spent a while **untracked** — it was split out of this file on
> 2026-07-30 and that session ended before committing either half. Committed
> 2026-07-30 (`docs(claude): split session history…`). **Lesson worth keeping: a
> handoff artifact only survives if it is IN THE REPO.** The same failure mode
> already cost us #379's `leakfix.patch`, which was saved to a per-session temp
> `scratchpad/` and is genuinely gone.

> 📋 **`REVIEW-PROTOCOL.md` in the repo root is the STANDING WORKFLOW for
> iterative development** (maintainer, 2026-08-10). Read it before starting
> implementation or review work. The core rule: **a session that has written
> code never reviews code** — start a fresh session before every review, because
> written artifacts transfer intent while session memory transfers
> self-justification.
>
> ⚠ **If you are implementing, write `PLAN.md` at the repo root UP FRONT, before
> you write code.** The whole protocol depends on that file existing, and a plan
> reconstructed after the fact is a justification rather than a plan — which is
> precisely what the session boundary exists to keep out. `PLAN.md` and
> `REVIEW.md` are live working files for the branch in hand; this file keeps
> standing rules and what is open; `docs/_dev/handoff-archive.md` keeps shipped
> history.
>
> ⚠ **THE ROOT IS DELIBERATELY EMPTY OF BOTH RIGHT NOW (2026-08-11).** `0.3.0`
> shipped, so its `PLAN.md` and `REVIEW.md` were archived to
> `development/plan-428-437-438-dialogs.md` and
> `development/review-428-437-438-dialogs.md`, matching where the #417 and #421
> review records already live. **Create `PLAN.md` fresh for the next branch —
> finding a stale one describing shipped work is worse than finding none.**
>
> ⚠ **AND CLOSE EACH ROUND WITH ITS RECORD.** Rounds 1–3 of the `0.3.0` dialog
> work each landed a `docs(review):` commit; **round 4 did not**, so the branch sat
> with four fix commits answering findings that existed nowhere in the repo, and
> the record had to be reconstructed from commit messages afterwards. Writing the
> record is the last step of a fix step, not an optional one.

---

## Environment — TWO MACHINES. Check which one you are on first.

**Windows box** (`D:\Development\bootstack`): the checked-in `.venv` is **STALE**
— it points at a `Python314\python.exe` that fails with *"Access is denied"*. Use
the launcher. **`py -3.12` for BOTH tests and docs** — **pytest is installed ONLY
on 3.12** (9.0.3); `py -3.13 tests/run_gui.py` fails every leg with *"No module
named pytest"* **while still printing a plausible-looking harness summary**. 3.13
and 3.14 have neither pytest nor the docs deps. `py -3.13` (3.13.7, Tk 8.6) is
fine for **running demo scripts**, which is all it is good for.
`bootstack.__version__` reports a stale `0.1.0a9` from old install metadata —
harmless, ignore it.

**macOS box:** repo at **`/Users/israeldryer/PycharmProjects/bootstack`**. Here
**`.venv` WORKS**: `.venv/bin/python` = **Python 3.14.0, Tk 8.6**, editable
install, macOS **26.5.2**. `python tests/run_gui.py` runs the full GUI suite in
~2 min with a real display. ⚠ Tk here is **8.6, not 9** — this box does NOT
exercise the Tk 9 paths, so `test_scroll_events.py`'s touchpad tests SKIP.
`python3.13` exists system-wide but does **NOT** have bootstack installed.

**Running tests:** `python tests/run_gui.py` (one root per process, `#150`).
**Docs:** clean-build always — incremental builds MASK warnings.
`rm -rf docs/_build && sphinx-build -b html docs docs/_build/html -W --keep-going`.

**⚠ `tests/widgets/*.py` NEVER RUNS.** `testpaths` is `tests/cli`,
`tests/widgets/public`, `tests/data`, and `run_gui.py` passes those same paths —
so **12 files / 25 tests** directly under `tests/widgets/` (`test_shell_*`,
`test_icon_image_props`, `test_rebuild_regressions`, `test_toolbar_drag`) are
collected by nothing. All 25 **pass** run individually (each builds its own root,
so they'd need `isolated` treatment). Dead coverage — fold into #380.

**⚠ Never pipe a build/test command to `tail`** — you capture `tail`'s exit 0 and
miss real failures (it once hid a failing test leg AND a broken docs build).
**This bites in PowerShell too**: `pytest ... | Select-String ...` leaves
`$LASTEXITCODE` from the *pipeline*. Redirect to a file, capture `$LASTEXITCODE`
on the next statement, then grep the file.

---

## Current state

**Released:** **`0.3.0` on PyPI, tag `v0.3.0` (2026-08-11)** — titled *Screen
capture and dialog results*, **shipped by `release.yml`, which ran clean end to
end**, with `docs.yml` chaining off it automatically. Two features and six fixes:
`widget.capture()` (#427, #429) and the dialog-result work (#428, #437, #438).
Previous: `0.2.3` (2026-08-08, also clean) and `0.2.2` (2026-08-06, published
**manually** during an Actions outage — that recipe is kept under Release flow
because it will be needed again).

Every post-release step is done and was **verified rather than assumed**: PyPI
proved with a real `pip download` (not the CDN-cached summary endpoint), the
shipped wheel opened and checked, the GitHub Release live with both assets, docs
returning 200, and #428's reporter told it is live via `gh issue comment`.

⚠ **One check worth repeating on every release from now on: `import bootstack`
with `idlelib` BLOCKED.** That is #430's defect, and grep is not enough to
re-prove it — seven `idlelib` mentions survive in the wheel and all are docstring
attributions. Block the module with a `meta_path` finder, assert the block works
as a control, then import. It passed for `0.3.0`.

**⏭ NEXT RELEASE: `0.3.1 — Dialog keyboard and modality`** — #426, #439, #440,
#441. Scoped 2026-08-11 (maintainer). See START HERE.

**`main` is GREEN.** ⚠ **STOP RE-RECORDING THESE NUMBERS FROM MEMORY. This file
has now been wrong about them FIVE times, in both directions.**

**AUTHORITATIVE — measured 2026-08-11 on `main` at `ab11f37c`** (the #443 merge —
everything in `0.3.0`), full `py -3.12 tests/run_gui.py`, **exit 0, all 20 legs
passed**:

| leg | result |
|---|---|
| widgets+CLI, shared root | **962 passed / 14 skipped** (75 deselected — capture raised it from 52) |
| data | **125 passed / 4 skipped** |
| `test_capture.py` (isolated) | **23 passed** |
| every leg summed (20 legs) | **1159 passed / 21 skipped** |

The pre-capture figure at `06acd727` was **1136 / 21 over 19 legs**, same shared
leg (962 / 14, 52 deselected) — capture adds 23 isolated tests and nothing to the
shared one.

⚠ **The `1006 / 13` recorded here for `e0092336` was IMPOSSIBLE, and so were
`1001 / 13` and `1005 / 13` in `REVIEW.md`'s rounds 3 and 4.** The shared leg
**selects 975 tests**, so no result summing to 1018 or 1019 can come out of it —
`SHARED_GROUPS[0]` is one pytest process over `tests/widgets/public tests/cli`
with `-m "not isolated"`, printing one summary line. **The ceiling is the
selected count, and checking a reported total against it takes one command:**
`pytest <paths> -m "not isolated" --collect-only -q | tail -2`. That single check
would have caught three of the five wrong figures this file has carried.

⚠ **The `123 / 6` data-leg flag is RESOLVED: it was wrong, not environmental.**
Measured `125 / 4` on every one of six runs on 2026-08-11 — five on the branch
head and one on merged `main`. Nothing moved from passed to skipped.

Previous, kept because the reasoning below refers to it — measured 2026-08-10 on
`feat/widget-capture-427` at **`bdbdd097`**: widgets+CLI **932 / 14**, data
**125 / 4**, summed **1128 / 22**. That row is consistent with today's: `main`
gained the 30 tests #428/#437/#438 brought (932 → 962).

⚠ **A superset cannot collect fewer than its subset.** That is what exposed the
2026-08-08 pair (`976 / 13` and `1170`), and the selected-count ceiling above is
the same test applied within a single run. **Prefer a number you just measured
over one written here, and fix the table when they disagree.**

**The rule that keeps being broken: record the DATE and the COMMIT beside any
count, and re-measure rather than reasoning from a number already in this
file.** Sum the legs yourself — `run_gui.py` prints no aggregate. And if a count
here disagrees with one you just measured, prefer yours and fix this table.

**✅ BOTH IN-FLIGHT BRANCHES ARE MERGED AND DELETED (2026-08-06).**
`fix/datatable-double-click-417` went in as **PR #423** (merge commit `1ab5cda7`) and
`fix/datatable-click-focus-421` as **PR #424** (merge commit `734d515b`). Both were
**merge commits, not squashes**, deliberately — the one-commit-per-issue granularity
was the deliverable, same call made for #410. Both were verified as genuine ancestors
of `origin/main` with MERGED PRs, then **deleted local and remote after `0.2.2` hit
PyPI**. Head SHAs if either ever needs resurrecting: **`278d579a`** (417) and
**`fa735f99`** (421).

⚠ **A worktree was used for #421 and has been REMOVED**; the branch itself lives in
the repo normally. Do not go looking for a checkout under `scratchpad/`.
**#409 shipped 2026-08-05 via PR #414** (merge
commit `d428f6be`) — docs-only, unreleased, and it left **#412** open on purpose;
full entry in the archive, summary under START HERE. Both `0.2.1` PRs are merged:
**#410** (the #392-review cluster, merged as a **merge commit** so its six
one-per-issue commits landed individually — the granularity was the deliverable)
and **#411** (#405). Every `backup/*` ref and all twelve `: gone` locals were
deleted after the release.

**✅ `0.2.3` SHIPPED 2026-08-08 — #430. `fix/idlelib-import-430` merged as PR #435
(merge commit `3c785759`), then DELETED local + remote; head `57ee3041` if it ever
needs resurrecting.** `import bootstack` raised `ModuleNotFoundError` on any Python
build without `idlelib` (Debian and Ubuntu package IDLE separately, like
`python3-tk`), so the WHOLE framework was unimportable — not a degraded
`CodeEditor`. Fixed by **porting** `WidgetRedirector` into
`textarea/redirector.py` rather than importing it; `idlelib` is stdlib, so it is
not on PyPI and could never have been declared as a dependency. Full root cause and
the Linux repro are on the issue — do not re-derive. Three things worth carrying
here:

- ⚠ **`NOTICE` now carries a PSF attribution, scoped to `redirector.py` ALONE —
  that scope was MEASURED, do not widen it.** The first draft listed six
  IDLE-derived modules. Comparing each against its claimed `idlelib` source
  (docstrings and type hints stripped, normalized through `ast.unparse`) showed
  only `redirector.py` carries IDLE's *expression*: **29% verbatim, 5-line
  identical runs**. The other five — `filter`, `undo`, `sidebar`, `line_numbers`,
  `bracket_matcher` — share **0–7%**, and their longest runs are 1–2 line
  incidentals like `import tkinter as tk`. They implement IDLE's *designs*, which
  is an idea, not protected expression, so declaring them PSF-derived would tell a
  license scanner something untrue. PSF LA v2: **clause 2** is copyright
  retention, **clause 3** is the changes summary — both satisfied. ⚠ `NOTICE`
  reaches users as `dist-info/licenses/NOTICE` via **setuptools' automatic
  license-file globbing, NOT `MANIFEST.in`** (which names only `LICENSE`) —
  verified by opening the published wheel, not assumed.
- ⚠ **A probe must be RUNNABLE ON EVERY BOX IT IS MEANT TO INFORM.**
  `probe_430_idlelib_free_import.py` called `sys.exit(1)` the moment `idlelib`
  imported, so on Windows and macOS it printed arm 1 and stopped — even though arms
  2–4 (interception from Python AND through the Tcl command, the unregistered-op
  control, `close()`, a real `CodeEditor` through `FilterChain`) do not depend on
  `idlelib` at all. It was runnable only on the one box that **cannot finish the
  GUI suite (#432)**. Now SKIPs and continues. **The capture branch had already
  fixed the identical shape in `b005509b`** — this is a recurring failure mode, not
  a one-off.
- ⚠ **`gh issue close --comment` SILENTLY DROPS THE COMMENT if the issue is already
  closed** — and a PR body saying `Closes #430` closes it at merge. It warns about
  the close and says nothing about the comment. Post with `gh issue comment`
  separately, and **check the comment actually landed**. Also: **`bump-my-version`
  had VANISHED from 3.12** despite this file recording it installed 2026-08-05;
  reinstalled as **1.5.1**. Check for it before assuming the release flow works.

**⚠ ONE BRANCH IN FLIGHT (2026-08-11, later the same day).** The other merged —
see below.

**✅ `fix/formdialog-select-value-428` IS MERGED AND DELETED.** It went in as
**PR #442**, **merge commit `06acd727`** (a merge commit, not a squash — same
call as #410/#423/#424, the one-commit-per-issue granularity being the
deliverable). **#428, #437 and #438 are all CLOSED**, all milestoned
`0.3.0 — Screen capture and dialog results`. Branch head was **`38d01598`** if it
ever needs resurrecting; local and remote refs are gone (GitHub auto-deleted the
remote on merge, which is why `git merge-base --is-ancestor origin/<branch>` now
fails with *"Not a valid object name"* rather than reporting non-ancestry —
**check the recorded head SHA against `origin/main` instead**).

**1. `feat/widget-capture-427` — head `origin/…` is `1654c60e` (moved again on
2026-08-11, after this file recorded `a7d8941a`), 30+ commits.
⚠ ANY LOCAL CHECKOUT IS BEHIND: the maintainer pushed three commits on
2026-08-11 that REPLACED the #429 fix.** See the #429 block below — the approach
changed, and the block that used to live here was describing code that is gone.
⚠ **History was REWRITTEN by an earlier rebase** — a stale checkout needs
`git fetch && git reset --hard origin/feat/widget-capture-427`, not a pull. A
backup ref `backup/widget-capture-427-prerebase` points at the pre-rebase head
`05707330`; delete it once the branch merges.

Adds `widget.capture(path)` — save a widget, window, or app as a `.png`/`.jpg`/
`.pdf` — from discussion #425 (an external user) via **#427**. It ships in the
minor now titled **`0.3.0 — Screen capture and dialog results`**, which the
maintainer RENAMED and widened to also carry #428, #437 and #438 — so capture is
no longer the only thing gating that release.

**Capture is now the ONLY thing gating `0.3.0`** — the dialog half shipped to
`main` in PR #442.
**Read `development/review-brief-427-capture.md` ON THAT BRANCH** — it records the
settled decisions not to re-litigate and the measurements not to re-derive. ⚠ **But
read it as a POINT-IN-TIME record: its six self-flagged soft spots are all resolved
now** (see below), and it was deliberately not rewritten. Run
`development/verify_427_capture.py` on each box; it prints the platform and
backend and SKIPs arms the machine cannot exercise.

**✅ The macOS and Linux legs HAVE NOW BEEN RUN** (maintainer, 2026-08-08) — that is
what the 15 newer commits are: `e9d9f2f4` ask spectacle for a fullscreen grab,
`493a0980` + `ac9a87a3` the Linux docs, `31a4eb46` bounds-check on the library's own
crop path, `575b8400` refuse a scrolled-out widget and a destroyed root, `aae0396c`
run the capture tests in their own process, `67aefdbf` pin the region hand-off on
Windows and macOS, `d66b3440` let the topmost precondition wait for the window
manager. Those legs also produced **#429, #431, #432, #433, #434**.

#### ✅ #429 IS FIXED — but ⚠ **THE FIX WAS REPLACED ON 2026-08-11. The quiet
settle is GONE.**

⚠ **This block described the wrong code for a day. Read the commit messages on
the branch, not a summary, if anything here is load-bearing.** The first fix
(`e616f5dc`) stopped `settle()` dispatching at all. That was REVERSED by
**`e4fd4af7` — "block input while settling instead of not settling"**, plus
`9aada08d` (docs) and `a7d8941a` (probes re-pointed, manual demo added).

`settle()` ran `root.update()` every 10ms so the desktop could repaint, which
dispatched everything queued — so a second click on the export button re-entered
the caller's handler mid-capture and stacked a second save dialog on the END
USER. **It now still dispatches, and holds `tk busy` over the target instead.**

**⚠ THE OPEN QUESTION THIS FILE RECORDED WAS ANSWERED, AND THE ANSWER KILLED THE
FIX: the quiet settle does NOT repaint on macOS.** The area a window uncovers is
repainted by the desktop, and on macOS that does not happen at all unless the
event loop is turning — so the capture returned whatever was there before. The
Windows 0 px result was real but was a property of the DWM backing store, not of
the approach.

⚠ **`tk busy` is now ADOPTED, having been recorded here as REJECTED.** Do not
re-litigate it in either direction; the reason it lost (more machinery than not
calling `update()`) stopped mattering once not calling `update()` was ruled out.

- **Reproduced first, with a control.** Pre-fix the handler reached nesting depth
  2; the same call queued AFTER the capture stayed at depth 1. Measuring DEPTH
  rather than call count is what separates re-entrancy from "it ran twice".
  Post-fix every arm is depth 1 with `calls=2` — the second click is not
  swallowed, it is serialized.
- **Captures are pixel-identical.** A shot taken right after a window closed
  differs from a reference by **0 px**, against a 50 px floor between two shots
  of an unchanged window.
- ⚠ **The fix could NOT live in `capture()`.** The documented pattern calls
  `ask_save_file()` BEFORE `capture()`, so a re-entrant handler opens the second
  dialog before reaching any guard there. Raising or no-oping was considered and
  REJECTED — both hand the application author a problem AND make the end-user
  outcome worse than the bug (an unhandled exception on a double-click, or a file
  silently not written). Memory `feedback_framework_absorbs_not_developer`.
- ⚠ **`tk busy` is invisible to a capture (0 px) — but the first measurement of
  that was WRONG in the other direction** (it "gets photographed", 3906 px). The
  noise floor had been built from two static back-to-back shots, far too tight
  for a comparison that restacks a window; it was measuring text antialiasing.
  Floor measured across a restack now, and busy reads 0 px against it.
- ⚠ **A SYNTHESIZED CLICK CANNOT TEST THE GUARD, and the probes now say so
  instead of pretending otherwise.** `tk busy` intercepts by putting a window
  over the target, so it only catches what the window system routed by pointer
  position; `event_generate` aimed at a widget delivers straight to that
  widget's bindings and re-enters with `tk busy status` reading 1. The real
  question needs a human: **`development/demo_429_busy_during_settle.py`**,
  click Export then keep clicking and read the nesting depth.
- ⚠ **The guard is on INPUT, not on scheduled work.** A capture started from a
  timer still re-enters, by design. `probe_429_capture_reentrancy.py` records
  that as the known limit rather than a failure.
- ⚠ **Three probes silently became their own controls** when the sleep-only
  settle shipped, because every arm drove through `_capture.settle`. Worst case:
  `probe_429_settle_without_input.py` had a "control" arm and a sleep-only arm
  running IDENTICAL code and producing byte-identical images, while reporting
  three FAILs that were all one unrelated thing (a cover window never removed,
  photographed as pure magenta). Every strategy is pinned per-file now, arms that
  read live code are labelled, and an `expect` argument keeps a
  defect-reproducing arm from reporting failure forever.
- ⚠ **THE MEASUREMENT TRAP, worth more than the fix: compare captures only
  within ONE `bs.App` INSTANCE.** The FIRST app in a process renders its content
  white; every later one in the same process falls back to default grey. Two
  captures from different app instances therefore differ in ~99% of pixels for
  reasons unrelated to what is being measured — and a noise control built from
  two same-population shots agreed to 14 px, so it looked sound. That produced a
  confident WRONG conclusion (`tk busy` "gets photographed"). Stricter cousin of
  the standing "measure within one process" rule.
- ⚠ **A test that leaned on the old behavior had to change.**
  `test_widget_closed_while_settling_raises_a_bootstack_error` queued its destroy
  on a timer and relied on settle dispatching it; with the wait quiet that timer
  no longer fires during the capture and the test would have passed **without
  ever destroying anything**. It queues the destroy as IDLE work now. Confirmed
  non-vacuous by disabling the guard.

**⏭ WHAT IS OPEN NOW: is `tk busy` invisible off macOS?** `e4fd4af7` was measured
on macOS, Tk 8.6. The dispatching wait is the shape the Windows and Linux legs
already ran on 2026-08-08, so those legs' results still stand — what rides on top
of them, untested elsewhere, is the busy hold. **Arm 3 of
`development/probe_429_busy_during_settle.py` measures exactly that; run it on
Windows and Linux.** Then `demo_429_busy_during_settle.py` by hand for the input
half, which no automated arm can reach. Also re-run `verify_427_capture.py`,
since `settle()` changed twice underneath it.

⚠ **#431/#432/#433/#434 are NOT capture defects** and must not be bolted onto
this branch — they are pre-existing test-infrastructure bugs that running the
other platforms merely surfaced. #431 and #434 are the SAME modifier-bit
assumption seen from two platforms and are best fixed together, once Linux has
reported.

**The review ran 2026-08-07 and found six things; five were fixed on the branch,
one was documented. Do NOT re-derive these — each has a control committed at
`development/probe_427_review_fixes.py` reproducing the pre-fix behavior.**

- ✅ **The Linux virtual-desktop crop — FIXED (`8e721837`).** This was flagged
  here as "the likeliest real defect" and it was real: `crop((1930, 10, 2200,
  300))` on a 1920x1080 image returns 270x290 pixels, **every one black**, and
  raises nothing. `_crop_desktop()` now bounds-checks and raises. ⚠ **Region
  flags (`grim -g`, `import -crop`) were CONSIDERED and DELIBERATELY SKIPPED —
  do not re-propose them.** None can be verified from the Windows box, and a
  wrong `-g` region fails just as silently as the bug it would replace; the
  bounds check is the part that holds on every backend.
- ✅ **`save()` flattened only `RGBA` — FIXED.** The gate is on the target
  format now, because the subprocess fallback opens whatever the desktop tool
  wrote and mode `P` fails with `cannot write mode P as JPEG`.
- ✅ **`settle()` re-entrancy — FIXED.** It turns the event loop, so a queued
  handler can close the target. **Measured: `winfo_ismapped()` on a destroyed
  widget RAISES `TclError: bad window path name` — it does not return 0**, so a
  raw toolkit error escaped a method documented to raise `BootstackError`. That
  measurement is what made the finding real rather than overstated.
- ✅ **A negative `inset` — FIXED.** It expanded the rect and photographed the
  neighbors; a 60x20 widget with `inset=-8` yields a 76x36 grab, **invisible to
  the existing `right <= left` guard because the box only grew.**
- ✅ **macOS Screen Recording permission — DOCUMENTED** (it returns the desktop
  and raises nothing). ⚠ **`CGPreflightScreenCaptureAccess()` would detect it
  but needs pyobjc, which bootstack does not depend on — decided against, do not
  re-propose.**
- ✅ **A dangling `:func:` xref — FIXED.** It pointed at
  `bootstack.dialogs.ask_save_file`; the verb is top-level and its only autodoc
  home is `bootstack.ask_save_file`. ⚠ **A default `-W` build does NOT catch a
  dangling py xref — only `-n` does.**

### ✅ `fix/formdialog-select-value-428` — MERGED (PR #442, `06acd727`), branch deleted

Shipped to `main` on 2026-08-11. It grew well past its name and carried **#428**
(the external report from `@bLynnb2762`), **#437** and **#438** — all three now
CLOSED and milestoned `0.3.0 — Screen capture and dialog results`. Head at merge
was **`38d01598`**. ⚠ **Nothing is released yet**: `0.3.0` still waits on
capture, so #428's reporter has NOT been told it is live. Post that comment with
`gh issue comment` after the release — `gh issue close --comment` silently drops
it on an already-closed issue.

⚠ **THE SUITE WAS NOT GREEN WHEN THE BRANCH WAS HANDED OVER, and the way it got
that way is worth more than the fix.** Round 4's verification ran at `70a039ce`
— **one commit before** `f9f1692f` rewrote the very tests it was verifying — so
a flaky test entered `main`'s queue unseen. Fixed pre-merge in `3d24ebbf`.
**Verify at the commit you are shipping, not at the last one you happened to
measure.**

**The flake, because the mechanism will recur:**
`test_enter_on_a_focused_button_does_not_also_press_the_default` failed its own
precondition — `focus_lastfor()` named the toplevel, so the `focus_set()` above
it had done nothing. **Tk's `focus_set()` is a SILENT no-op when the widget or
any ancestor is unmapped**: `TkSetFocusWin` walks the ancestry and returns
without setting anything, reporting nothing, so the miss surfaces one line later
as an inexplicable focus assertion. The test's `_drive` helper polled for the
modal grab as its "the dialog is up" barrier, but **the grab is set before the
geometry manager maps the footer's children at idle** — the failure carried
`button mapped=0 parent mapped=1 top mapped=1 grab=.!toplevel7`. Rate: **1 in 5
full legs, 0 in 60 dialogs in a quiet process.** The barrier now waits for the
grab AND the footer being mapped.

⚠ **A 1-in-5 flake cannot be verified against by re-running.** The control at
`development/probe_437_focus_flake.py` CREATES the condition instead —
packed-but-not-yet-updated widgets leave idle geometry work outstanding when the
dialog goes up: **old barrier 5/10 unmapped and 5/10 focus misses, new barrier 0
and 0**, the two columns tracking one-for-one. Arm 1 is the mechanism alone and
arm 2 is the quiet-process control that returns 0/60.

⚠ **Round 4's review record was never written.** Four fix commits answered
findings that existed nowhere in the repo. Reconstructed into `REVIEW.md` from
the commits and their probes, labelled as reconstructed. **Rounds 1–3 each
landed a `docs(review):` commit; make that the last step of a fix step, not an
optional one.**

**The root cause, so it is not re-derived:** `FormDialog.result` was read AFTER
the dialog closed, by which point the editors were destroyed and the only thing
left to read was the on-screen TEXT — which arrives as a string whatever the
value's real type was. It was never a conversion on the read path (an early
session proved that half and it held). Entries are now captured at the press,
while the form is alive, in `_accept_press`. The same defect hit every editor
whose display differs from its value, not only `select`: a date field handed back
its formatted text.

⚠ **The plan and the full four-round review record are ARCHIVED** at
`development/plan-428-437-438-dialogs.md` and
`development/review-428-437-438-dialogs.md` (they were `PLAN.md` / `REVIEW.md` at
the root while the branch was live). The per-round briefs are
`development/review-brief-437-438-dialog-buttons.md`, `…-round3.md` and
`…-round4.md`. **Four rounds ran — 5 findings, then 8, 7 and 4.** Read those
before reopening any of this rather than re-deriving it.

**Round 4 (2026-08-11) found five things; all five are handled:**

- ✅ **The Dialog page taught reading a content widget after `show()`** —
  `create_project(fields["name"].value)`, i.e. after every widget was destroyed.
  It survived only because `TextField` is `StringVar`-backed; the same idiom with
  a `bs.Select` raises `TclError`. **That is the very pattern #428 exists to
  prevent, in the release that fixes it.** The example binds a `Signal` now.
- ✅ **A DISABLED button swallowed Enter** — the stand-down guard assumed a
  button that received the key had already acted on it, which is false when
  `invoke` does nothing. Any content button that greys itself out on click left
  the keyboard dead for the whole dialog.
- ✅ **The bindtags read went through Tcl for a case that cannot arise here.**
  Tkinter really does hand a callback a bare path string when the target is
  absent from its widget map — but a dialog has 0 such widgets of 32, because
  bootstack creates everything from Python. Simplified to `.bindtags()`.
- ✅ **A CHANGELOG sentence contradicted the branch's own measurement** (claimed
  dialogs resting on their default button were unaffected; #439 says no dialog
  is in that state at open). Removed rather than corrected — the accurate version
  would document #439 as if intended.
- ✅ **A test pinned #439 as a passing precondition.** Loosened, so fixing #439
  cannot turn it into a precondition failure.
- ⏭ **Filed as #441, deliberately NOT fixed here:** Enter in a `TextArea` inserts
  the newline and then the dialog closes on top of it, because the guard
  recognizes only `TButton`. Needs a general rule for "did something already
  handle this key?", not another special case.

⚠ **Traps this branch already paid for — do not re-pay them:**

- **`bootstack.dialogs.FormDialog` is a public WRAPPER**, not the impl in
  `dialogs/_impl/formdialog.py`. Reach the impl through `._internal`.
- **`dlg.show()` runs a modal wait loop that a close scheduled with `after` does
  NOT break.** Drive it by invoking a real footer button instead — and poll for
  the modal grab rather than firing on a fixed delay, because `show()` pumps the
  event loop while building and positioning, so a timer can land on a half-built
  dialog. `_drive()` in `test_dialog_press_contract.py` is the worked pattern.
- **`instate(['!disabled'])` is a QUESTION returning True when the widget is
  ENABLED.** `not instate(['!disabled'])` therefore selects the disabled one —
  a double negative that silently inverts a guard. Write
  `not instate(['disabled'])`.
- Probe output must be **ASCII** — a check mark raised `UnicodeEncodeError` on
  this box's cp1252 console. Same rule #430 hit.

**BRANCHES: `main`, `feat/widget-capture-427`** — `fix/formdialog-select-value-428`
merged as PR #442 and was deleted local and remote on 2026-08-11.
The `main`-only state below
was verified 2026-08-06 after the `0.2.2` release and held until the branch above
was pushed on 2026-08-07.
An earlier sweep on 2026-08-05
(maintainer-approved) deleted all seven survivors together with
their `: gone` locals: three merged ancestors (`docs/custom-events-409` PR #414,
`fix/command-option-modifiers-405` PR #411, `fix/event-cleanup-392-followups`
PR #410) and four squash-merge leftovers (`cleanup/shell-visibility-idiom` PR #384,
`fix/literal-mode-guards` PR #382, `fix/394-field-row-alignment` PR #395,
`fix/403-test-coverage` PR #406). Head SHAs are in the deleting commit's message if
one ever needs resurrecting; GitHub also keeps each PR's head SHA.

⚠ **The method matters more than the result, because this recurs every release.**
**Non-ancestor ≠ unmerged.** Four of the seven were not ancestors of `main` purely
because their PRs were **squash-merged**, and an earlier handoff nearly read that
as live work. Verify with two commands, never by reading this file:
`git merge-base --is-ancestor origin/<branch> origin/main` for ancestry, then
`gh pr list --head <branch> --state all --json number,state,mergedAt` — a MERGED PR
is what makes a non-ancestor safe to delete. Record the head SHAs before deleting.

**`0.2.1` shipped `#396, #398, #399, #400, #403, #405`** in the release notes,
plus **#397 and #401**, which are fixed and merged but **deliberately absent from
the CHANGELOG**. Neither was reachable from public API, so listing them handed a
reader scanning for upgrade risk a false positive — the same call made for #387 in
`0.2.0`. Verified, not assumed: `MessageDialog`/`QueryDialog`/`DateDialog` are
absent from `bootstack.dialogs.__all__` and the public verbs return their result
directly, while the one public dialog class (`ColorChooserDialog`) was the case
that was already correct; and `on("increment")` raises `UnknownEventError` with no
`on_increment` shorthand. **Both remain fully documented in their own commit
messages** (`a93a47a4`, `7e204801`) — that is where the root causes live now.

**0.2.0 shipped `#332, #379, #381, #387, #388, #392, #394`.** It was **a minor,
not a patch**, and that was a deliberate maintainer call: the project committed to
SemVer at 0.1.0 and **#381** raises where it used to accept. ⚠ **This file used to
claim TWO incompatible changes; that was wrong.** The second (`configure(data=)`
clearing absent keys, #387) is **not publicly reachable** — `bs.Form` has no
`configure` method at all (verified: `AttributeError`), so no user can observe it.
One genuine break still warrants a minor, so the version is right — it just rests
on one leg, not two. The CHANGELOG correctly omits it. **#394** also moves pixels
in any layout pairing a field with a taller widget on a stretch axis.

**⏭ ACTIVE: `feat/widget-capture-427` (#427), pushed 2026-08-07. Reviewed, all
findings applied; awaiting the macOS/Linux legs, then a PR** — see the IN FLIGHT
block under Current state. It was
taken ahead of the standing recommendation deliberately: an external user asked
for it in discussion #425, and it is additive, so it cannot destabilize the
batched strictness work. ⚠ **It adds public surface, so it CANNOT ride the patch
line.** ✅ **DECIDED 2026-08-07 (maintainer): it CUTS AHEAD as its own minor.** It
became `0.3.0`, and everything below it shifted up one. ⚠ **That milestone was
later RENAMED to `0.3.0 — Screen capture and dialog results` and widened to carry
#428, #437 and #438** — capture no longer ships alone.

After it, pick
from the table below; the standing recommendation is the unnumbered
`Test and release confidence` workstream (**#407** then **#380**), and **#390** is a
decision that can be taken at any time. ⚠ **The milestones have been RENUMBERED
TWICE — read the CURRENT table below, never a number quoted in older prose.**
Restructured and renumbered 2026-08-05, then renumbered again 2026-08-07 when
`0.3.0 — Screen capture` was inserted ahead of the strictness batch. Two
generations of stale numbers are therefore in circulation:

| written before | says | now means |
|---|---|---|
| 2026-08-05 | `0.3.0 — Guided flows` | `0.6.0 — Guided flows` |
| 2026-08-05 | `0.4.0 — Power-user interactions` | `0.7.0 — Power-user interactions` |
| 2026-08-05 | `0.5.0 — Structured editing` | `0.8.0 — Structured editing` |
| 2026-08-05 | `0.6.0 — Argument and value strictness` | `0.4.0 — Strictness and value types` |
| 2026-08-07 | `0.3.0 — Strictness and value types` | `0.4.0 — Strictness and value types` |
| 2026-08-07 | `0.4.0 — Form, signals, and composite authoring` | `0.5.0 — …` |
| 2026-08-07 | `0.5.0 / 0.6.0 / 0.7.0` | `0.6.0 / 0.7.0 / 0.8.0` |

⚠ **Prose further down this file still quotes the OLD numbers in places** (e.g.
"#369 and #383 are milestoned `0.6.0 — Argument and value strictness`"). Those
lines were not swept. The table above is the authority; when you touch such a
line, fix it.

**THE RULE, which is the part worth keeping: numbered milestones are RELEASES;
unnumbered milestones hold work NOT YET ASSIGNED to a release.** Membership in a
numbered one is decided by compatibility *and* readiness, and the title names what
actually ships. Nothing gets a number until its order is real. This replaced an
accidental mix in which `0.2.x`/`0.6.0` were compatibility buckets wearing subject
names while `0.3.0`–`0.5.0` were subject themes wearing version numbers — which is
how three of five `0.3.0 — Guided flows` issues came to be form/signal work.

⚠ **The unnumbered half was first written as "workstreams that do not map to a
release." That was wrong** — most of it maps to a release, just an undetermined
one. Each unnumbered milestone says *why* it has no number: Tk 9 is blocked on
hardware, hot reload is outside the SemVer freeze, test confidence rides any patch,
additions ride any minor.

⚠ **The patch line is BUG FIXES ONLY.** The project committed to SemVer at `0.1.0`,
so **adding public surface is a MINOR even when nothing breaks** — someone upgrading
`0.2.1 → 0.2.2` should be able to assume no new API arrived. An audit on 2026-08-05
found **three of the patch line's four issues were additions** (#352 a whole new
widget, #317 and #208 additive), which is why `Additions awaiting a minor` exists.
⚠ **The trap to avoid repeating:** the milestone had *already* been renamed away
from "Fixes and small additions" to stop that creep, while its description still
said "fixes and small additions" — so the rename changed nothing. **Fix the
description, not just the title.**

⚠ **BUT THE RULE IS ONE-DIRECTIONAL, AND THIS FILE USED TO IMPLY OTHERWISE**
(corrected by the maintainer, 2026-08-11). An addition **requires** a minor; a
minor does **not** require additions. `Additions awaiting a minor` is a queue of
work that *cannot* ride a patch — it is **not** a statement that minors are for
additions, and a minor is free to carry as many plain bug fixes as it likes.
`0.3.0` did exactly that: two additions and **six fixes**. So when a minor is
being cut anyway, ask what else is ready rather than parking fixes for a later
patch out of habit. The mirror-image question is just as useful and is what
scoped `0.3.1`: **for a fix, ask whether it needs a minor at all** — if it adds no
public surface it can ship as a patch, which is what let `0.3.0` go out on time
with four known bugs deferred rather than held.

| Order | Milestone | Open |
|---|---|---|
| — | ~~**`0.3.0 — Screen capture and dialog results`**~~ — **SHIPPED 2026-08-11**: #427, #428, #429, #437, #438 | 0 |
| 1 | **`0.3.1 — Dialog keyboard and modality`** — #426, #439, #440, #441 | 4 |
| 2 | **`Test and release confidence`** (unnumbered) — #407 then #380 | 2 |
| 3 | **`0.4.0 — Strictness and value types`** — #383, #369, #408, #416 | 4 |
| 4 | **`0.5.0 — Form, signals, and composite authoring`** — #390, #389, #412, #415 | 4 |
| 5 | **`0.6.0 — Guided flows`** — #311, #312 | 2 |
| 6 | **`0.7.0 — Power-user interactions`** — #315, #316 | 2 |
| 7 | **`0.8.0 — Structured editing`** — #192, #314 | 2 |
| — | **`Tcl/Tk 9 support`** (unnumbered, blocked on hardware) — #376, #378 | 2 |
| — | **`Hot reload (provisional)`** (unnumbered, outside the freeze) — #322, #328 | 2 |
| — | **`Additions awaiting a minor`** (unnumbered, rides any minor) — #208, #317, #352 | 3 |
| — | **`0.2.x — Patch line`** (rolling, FIXES ONLY) — #207, #422 | 2 |

⚠ **`0.2.x — Patch line` is now MISNAMED** — the line is `0.3.x`. Its two issues
(#207 deferred by decision, #422 test-only) were not moved, because renaming a
milestone is the maintainer's call. Worth settling next session: rename it, or
fold its contents into `0.3.1`.

Ordering reasons, so they are not re-litigated: **confidence first** (nothing runs
the suite, so every release is a gamble, and #407 makes that automation cheaper
before you buy it); **breaks batched, not dribbled** (#383/#369/#408/#416 in ONE
minor = one migration for users instead of four); then near-ready API, then new
widgets. ⚠ **Numbers past `0.4.0` are ordering hints, not commitments** — they
assume three minors land in that sequence, which nobody knows. Retitling is cheap;
that is the point of the rule. **Subject now lives on LABELS** (`tk9`,
`test-infra`, `hot-reload`, `new-widget`) so milestones can stay about *when*.
Reasoning also in memory `project_roadmap_milestones`.

**⚠ FIVE UNMILESTONED OPEN ISSUES as of 2026-08-11, after the release**
(verified against `gh`, not counted by hand): **#431, #432, #433, #434, #436.**
Down from ten — #426/#439/#440/#441 went to `0.3.1` and #429 was milestoned into
the release it actually shipped in.

**#431/#432/#433/#434 all came out of running the macOS and Linux legs for #427**
and are **test-infrastructure failures, not user-facing** — which is exactly why
they were kept OUT of `0.3.0`: a CHANGELOG entry earns its place by being
reachable, and a user cannot observe any of these. `#432` (the shared-root GUI leg
exits silently mid-run on Linux) is the one that **still blocks #380 (CI)**.
**#436** is the `versionadded` convention, filed 2026-08-10, and it carries an
undecided question (retroactive to `0.2.x`, or forward-only) — worth answering now
that `0.3.0` has shipped new public surface that a reader cannot date.

**They are deliberately left unassigned** — the rule below says do not assign a
milestone unasked, and none has been raised with the maintainer. **#430 was the
exception and it was explicit**: the maintainer said "we release this with 0.2.3",
which decided the milestone, so it was assigned to `0.2.x — Patch line` and shipped.
Absent that kind of direct instruction, leave them alone.

**ZERO UNMILESTONED OPEN ISSUES as of 2026-08-06** (verified against `gh`, not
counted by hand) — the deviation this file used to flag was closed. The maintainer
assigned #417, #418, #419, #420, #421 and #422 to `0.2.x — Patch line` in one call:
all six are bug fixes on existing public API and **none adds public surface**, which
is the test for the patch line. #417 came from an external user; the other five were
filed by us while fixing it. ⚠ **Do not assign a milestone unasked** — that rule
still stands, this was an explicit decision.
⚠ **A bullet in this file is not proof an issue is open** — #222, #234
and #379 all sat here as open work after being closed; check the state first.
Check with:
`gh issue list --state open --json number,milestone --jq '[.[]|select(.milestone==null)]'`

### ★ START HERE (2026-08-11, end of day) — `0.3.0` SHIPPED. Nothing is in flight.

**`0.3.0 — Screen capture and dialog results` is on PyPI**, tag `v0.3.0`, shipped
by a clean `release.yml` with the docs deploy chaining off it. **Every
post-release step is done and verified** — see Current state for the evidence and
for the one new check worth repeating (import with `idlelib` blocked).

**There are NO branches. `main` is the only ref**, local and remote, and it is
green: **1159 / 21 over 20 legs** at `ab11f37c`. Both merged branches and all
backup refs are deleted (`38d01598`, `1f13cea0`, `05707330`, `89386960` recorded
in case anything needs resurrecting).

**⏭ START WITH `0.3.1 — Dialog keyboard and modality`: #426, #439, #440, #441.**
Scoped by the maintainer at release time, on the principle that **all four are
patch-safe** — none adds public surface — and **none is a regression from
`0.3.0`**; all four exist in `0.2.3` too. That is what made shipping first and
patching after the right call rather than holding the release.

| issue | what | size |
|---|---|---|
| **#426** | the layout migration error names `align_self=`/`justify_self=`, neither of which exists; the real keys are `horizontal=`/`vertical=` and only `grow=` is right | smallest — one message |
| **#439** | `default_button.focus_set()` is a no-op, so no focus ring and Tab starts from nowhere, in a dialog whose docs promise otherwise | small, but the fix is UNVERIFIED and focus is platform-sensitive |
| **#441** | Enter in a `TextArea` inserts the newline and then submits the dialog on top of it | needs a RULE, not another special case |
| **#440** | a nested modal drops the outer dialog's grab permanently | largest — save/restore across `Dialog`, `MessageBox`, `QueryDialog`, `DateDialog` |

⚠ **#441 carries a constraint set at scoping time: keep the fix INTERNAL.** The
issue floats three options and one of them — letting a widget *declare* it
consumes Enter — is new public surface, which would push the whole thing to a
minor. A bindtag allowlist or asking the focus widget whether it is multi-line
both stay inside a patch.

⚠ **#426 contradicts THIS FILE**, which quotes `Use grow= / align_self=` as the
*good* error message under Layout. Fix both together. Verified 2026-08-11:
`bs.Picture(align_self="stretch")` raises `TclError: unknown option "-align_self"`
while `horizontal="stretch"` and `grow=1` both construct.

After `0.3.1`, the standing recommendation is still `Test and release confidence`
(#407 then #380) — and **#432 is the blocker to attack first**, since the GUI leg
cannot complete on Linux at all, which makes CI unbuyable.

**⏭ A DESIGN IDEA WORTH CARRYING INTO THAT BRANCH (maintainer, 2026-08-11): map
the real keys onto a virtual name with `event_add`**, so a dialog binds one
`<<Submit>>` instead of `<Return>` + `<KP_Enter>` and the intent becomes
targetable. **Measured before it gets designed around —
`development/probe_439_virtual_event_for_submit.py`, and it needs a MAPPED
window or every arm silently reads empty:**

- ✅ **It works.** `root.event_add("<<Submit>>", "<Return>", "<KP_Enter>")` and a
  `<<Submit>>` binding fires from the real key. One name covers both keys, which
  is exactly the duplication the dialog carries today.
- ⚠ **On a tag carrying BOTH, the PHYSICAL binding wins and the virtual one does
  not run at all.** Measured: with `<<Submit>>` and `<Return>` both bound to the
  widget, only `<Return>` fired. So this is not additive — anything already
  binding `<Return>` directly shadows the virtual name on its own tag.
- ⚠ **The mapping is per-INTERPRETER, not per-widget** (`event info` reads the
  same through the root and through a widget). Adding one is a cross-cutting,
  app-wide change, not a local one.
- ❌ **It does NOT change the bindtag walk.** Order stayed
  `widget → class → toplevel`. So the toplevel still runs after a button's class
  binding and still has to decide whether something already answered the key —
  **#441 is untouched by this.** It is a naming and deduplication win, not a
  dispatch one; adopt it for clarity if wanted, but do not scope #441 around it.

⚠ **#436 was filed 2026-08-10**: adopt `versionadded` across the public API,
because the docs site serves ONE version and a reader cannot tell which release
an API needs. `capture()` is already tagged on its branch as the first case. It
carries one undecided question — whether `versionchanged` gets applied
retroactively to `0.2.0`–`0.2.3` or stays forward-only.

Verified, not assumed:

- **PyPI** — `0.2.3` live, wheel + sdist, proved with a real
  `pip download --no-deps bootstack==0.2.3`. ⚠ The **`/pypi/bootstack/json` summary
  endpoint is CDN-cached and lagged behind a successful `0.2.2` upload** — use
  `/pypi/bootstack/<version>/json` or a real `pip download`, and never read a stale
  summary as a failed upload and re-upload.
- **The fix, inside the published wheel** — `from idlelib` is gone from the shipped
  `filter.py`, and `NOTICE` is present at `dist-info/licenses/NOTICE` carrying the
  PSF attribution. **Checking the artifact, not the source tree, is what proves a
  packaging-shaped bug is actually fixed** — #430 was reported against the shipped
  `0.2.2` wheel in the first place.
- **GitHub Release** — [`v0.2.3`](https://github.com/israel-dryer/bootstack/releases/tag/v0.2.3),
  titled `0.2.3 — Import without IDLE`, both artifacts, not a draft, not a
  prerelease.
- **Docs** — deployed automatically, `http://bootstack.org/` returns 200 (run
  `31274654592`, chained off the successful Release run).
- **Issue** — #430 CLOSED, milestoned `0.2.x — Patch line`, "it's live" comment
  posted ([5227773487](https://github.com/israel-dryer/bootstack/issues/430#issuecomment-5227773487)).
- **Branch** — `fix/idlelib-import-430` deleted local + remote (head `57ee3041`),
  verified merged with the two-command check before deleting.

**⚠ `release.yml` RAN CLEAN for `v0.2.3`** — build, PyPI publish, and GitHub Release
all green, and `docs.yml` chained off it automatically. Actions had recovered from
the 2026-08-06 outage. **The manual recipe below was NOT needed and is kept only as
the fallback for next time.**

#### ⚠ THE FALLBACK, FROM `0.2.2`: publishing BY HAND when Actions is down

`release.yml` **never ran successfully for `v0.2.2`.** GitHub Actions was in a
**major outage** all afternoon (incident opened 15:22 UTC, still *investigating* at
19:43 UTC — "capacity remains constrained and jobs may still be delayed or fail").
Two tag-triggered runs died without publishing anything:

| run | what happened |
|---|---|
| `31115122262` | failed twice; `Failed to resolve action download info: Service Unavailable` — GitHub could not hand the runner its actions. Bound to a tag object that no longer exists. |
| `31121469892` | `Build distribution` sat **queued 15 minutes then was CANCELLED**; publish + release **skipped**. A rerun re-queued and never started. |

⚠ **`gh run` reported this run inconsistently** — `gh run cancel` said *"Cannot cancel
a workflow run that is completed"* while `gh run view` said `queued`, repeatedly. Under
an Actions outage the run state itself is unreliable; **check PyPI, not the run**, to
decide whether anything was published.

**So it was published manually**, which worked cleanly and is the fallback to reuse:

1. `git worktree add <scratchpad>/rel-X.Y.Z vX.Y.Z` — build from a **pristine checkout
   of the tag**, never from the working tree. This repo has ~60 untracked files in
   `development/`; building in place risks them landing in the sdist. (Verified they
   did not: sdist top level is `src`, `tests`, `LICENSE`, `NOTICE`, `MANIFEST.in`,
   `PKG-INFO`, `README.md`, `pyproject.toml`, `setup.cfg`.)
2. `py -3.12 -m pip install --upgrade build twine` (neither was installed).
3. `py -3.12 -m build`, then **`py -3.12 -m twine check dist/*`** — both PASSED.
4. `py -3.12 -m twine upload --config-file D:/Development/bootstack/.pypirc --non-interactive dist/*`
5. `gh release create vX.Y.Z dist/* --title "<from release_notes.py>" --notes-file RELEASE_NOTES.md --generate-notes`
6. `git worktree remove <path> --force`

⚠ **`twine.exe` is NOT on PATH** — always `py -3.12 -m twine`.

⚠ **The token lives at `D:\Development\bootstack\.pypirc`** (repo root, **not**
`~/.pypirc`, which does not exist). It is `[pypi]` + `username = __token__` + a
179-char `pypi-AgEI…` token. It is **gitignored at `.gitignore:29` (`/.pypirc`) and
untracked** — verified, safe. Because it is not in the home directory, **twine needs
`--config-file` explicitly** or it will not find it.

⚠ **A manual publish SKIPS THE DOCS DEPLOY.** `docs.yml` triggers on
`workflow_run` of **"Release" completing successfully** — no successful Release run
means no docs, silently. Its three runs that day all read `completed/skipped`, which
looks like a no-op but meant the site was still serving `0.2.1`. Fix is one command:
**`gh workflow run docs.yml --ref main`** (the workflow has a `workflow_dispatch`
trigger and its `if:` explicitly allows it). It succeeded in ~2 minutes even mid-outage.

⚠ **`release.yml` publishes via OIDC trusted publishing**
(`pypa/gh-action-pypi-publish` + `id-token: write`), so there is **no token in CI** —
the local `.pypirc` is the only credential path for a manual publish, and CI's path
cannot be reproduced locally.

⚠ **If run `31121469892` ever does execute**, its publish step will fail with *file
already exists*. **That is expected and harmless** — PyPI already has the correct
artifacts. Do not "fix" it by re-uploading or burning a version.

#### ⚠ The CHANGELOG said the wrong thing about click order — FIXED at `931edd89`

The `0.2.2` notes claimed a double-click runs `on_row_click` twice **before**
`on_row_double_click`. **It does not.** `on_row_click` rides `<ButtonRelease-1>` while
`<Double-1>` is a **ButtonPress** pattern, so the double lands *between* the clicks.
Measured, with a control:

```
claimed:  ['click', 'click', 'double']
actual:   ['click', 'double', 'click']      <- same shape as Win32's DOWN, UP, DBLCLK, UP
```

It matters practically: **one `on_row_click` fires AFTER the double-click handler has
already run**, so a click handler that moves the selection lands after the double-click
opened a dialog. The earlier session measured *counts* (2 clicks + 1 double) and never
checked *order*; the wrong ordering survived a rewrite of that same line hours earlier.

⚠ **The probe was junk on its first run and said so loudly** — it reported
`['double','click','double','click']`, claiming `double` on the very first press.
**Synthesized events default to `time=0`, and Tk decides `Double` off the event
clock**, so the preceding control click was indistinguishable in time. Supplying an
explicit `time=` to `event_generate` fixed it. Probe with both the control and the
clock: `development/probe_421_click_order.py`.

**A click count on `RowEvent` was considered and DROPPED** (maintainer, 2026-08-06) —
do not re-propose it. DOM has `event.detail` and AppKit has `clickCount`, and either
would let a handler early-return on the second click, but the maintainer is not
worried about it. It would have been new public surface, so a minor, not the patch line.

**⚠ DO NOT TOUCH A BRANCH WHILE A REVIEW RUNS.** This was violated on 2026-08-06: a
branch was handed off and then edited in place while the agent ran. The review reads
files on disk, not only `git diff`, so it reviews a moving target. If follow-up work
cannot wait, do it in a **`git worktree`** or on another branch. Memory
`feedback_dont_touch_branch_under_review`. ⚠ **And a worktree runs against `main`'s
source unless you set `PYTHONPATH`** — the editable install points at
`D:\Development\bootstack\src`, so a worktree's tests import *main's* code. The #421
review hit this; it happened to hand it a free pre-fix control, but it silently
invalidates a post-fix run.

**⚠ AND CHECK `git rev-parse` ON BOTH BRANCHES BEFORE READING ANY FILE.** These two
branches were briefly at the *identical* commit, so a branch name did not tell you
which code you were looking at — reading `tableview.py` would have silently shown
421's work-in-progress while you believed you were on 417. The 2026-08-06 review
caught this itself and reviewed committed blobs (`git show <sha>:<path>`) instead.

#### What shipped in `0.2.2` — commit map (both branches now merged and deleted)

`fix/datatable-click-focus-421` was **stacked on** `fix/datatable-double-click-417`.
All of these are on `main`; the branch column records which PR carried them
(**417** → #423, **421** → #424). Three later commits — `5d169044`, `9e257368`,
`62950b0a` — applied the #421 review findings on top.

| SHA | Branch | What |
|---|---|---|
| `aeffa27d` | 417 | #417 — `<Double-1>` bound unconditionally |
| `638b24e3` | 417 | #420's guard on `_on_row_double_click` (commit says `#417`; re-cited later — history reads oddly, notes are correct) |
| `701cea54` | 417 | #418 — the same guard on `_on_row_context` |
| `14808981` | 417 | #419 — deferred chevron refresh |
| `36ae3720` | 417 | CHANGELOG: chevron bullet, `#420` re-citation, `### Changed` |
| `69f92b05` | 417 | probes + `demo_419_group_chevrons.py` |
| `6718de36` | 417 | **fixes two defective tests** — see below |
| `f7405d97` | 417 | CHANGELOG: the double `on_row_click` bullet |
| `f425430f` | **421** | **#421 — `_take_click_focus` on the two `'break'` paths** |
| `ff814b85` | **421** | CHANGELOG bullet for #421 |
| `6c18d34e` | **421** | the 417 review record into `development/` |

#### ⚠ What the 2026-08-06 review established — do NOT re-derive

Full record committed at **`development/review-417-double-click.md`**. Verdict was
ship-ready. It verified, and these should not be re-checked:

- **The `iid not in self._row_map` guard is exact.** Group parents go only to
  `_group_parents`; data rows only to `_row_map`. All four `_tree.insert` sites were
  enumerated.
- **No binding accumulation** from the unconditional `<Double-1>` — `_build_tree`
  runs once and the bind has no `add=`.
- **The deferred chevron refresh is safe after teardown** — scheduled on
  `self._root()`, and every `item()` call is inside `try/except`.
- **`_update_selection_markers` does not clobber chevrons** — selection markers are
  inactive whenever `_group_by_key` is set. A suspected conflict, chased and closed.

**All six of its findings are handled.** Findings 1–4 landed in `6718de36` and
`f7405d97`; finding 5 became **#422**; finding 6 needed no action.

#### ⚠ THE LESSON WORTH KEEPING: that review MISSED two real defects

It called the tests "better than the repo average". **Two of them were broken**, both
found afterward by running the control the committing session should have run —
*revert the fix, confirm the test fails*:

- **`test_group_chevron_tracks_double_click` was VACUOUS** — it passed against the
  unfixed code. The setup started collapsed, so the double-click's two toggles
  finished on a *collapse*, the direction that was never broken.
- **`test_group_chevron_tracks_keyboard_expand` was FLAKY**, ~1 run in 5, its own
  control tripping. It synthesized key events, and those are dropped once earlier
  tests fill the shared root and the table is unmapped.

**The standing rule is that agents over-flag. This one under-flagged, on exactly what
it praised.** Adversarial verification cuts both ways — a clean review is not proof.

#### Measured facts worth not re-deriving

- **A double-click also fires `on_row_click` TWICE** (measured 2 clicks + 1
  double-click, against a 1/0 single-click control). `<ButtonRelease-1>` has no
  `Double` counterpart. Documented in the CHANGELOG; no test covers the interaction.
- **The toolkit reports an expand BEFORE recording it.** `ttk::treeview::OpenItem`
  generates `<<TreeviewOpen>>` and *then* sets `-open true`; `CloseItem` sets first.
  That asymmetry is the whole of #419. Verified from `info body`, not from memory.
- **Tk REJECTS `event_generate("<Double-1>")`** — `Double` is a binding pattern, not
  an event type. Two presses is the only way to synthesize one.
- **Do not synthesize keys in the shared-root suite.** Drive the routine the key is
  bound to (`ttk::treeview::ToggleFocus`, `ttk::treeview::Keynav w right`). The
  key-to-routine mapping is the toolkit's binding table, not ours.
- **Assert focus via `focus_lastfor()`, not `focus_get()`** — the latter reports
  nothing unless the window is active, which is not dependable here.
- **Probes must stub `_open_form_dialog` AND the row menu** — both block the loop
  forever when driven synthetically.
- Four probes and a visual demo are **committed** in `development/`:
  `probe_group_header_chevron_sync.py`, `probe_021_allow_edit_group_header.py`,
  `probe_group_header_click_focus.py`, and `demo_419_group_chevrons.py` (a
  seven-step manual checklist covering all five issues). Each probe carries a control.

#### ⚠ What the #421 review established — do NOT re-derive

Full record at **`development/review-421-click-focus.md`**. Verified, and not worth
re-checking:

- **#421's two new tests are NOT vacuous.** Run against unfixed source both fail with
  the right symptom (`focus_lastfor()` is the App root, not the tree), and test 1's
  internal control arm — clicking a plain data row — passes. This is exactly the
  control the #417 review skipped, which is how two defective tests got through there.
- **Suite green at the head.** 973 passed / 13 skipped (widgets+CLI) and 123 / 6
  (data), matching the `ff814b85` figure. The previously-flaky
  `test_group_chevron_tracks_keyboard_expand` passed on both of two runs.
- **The group-header focus question is CLOSED — it is a non-issue.** Tk's `<space>` is
  `ttk::treeview::ToggleFocus` → `Toggle $w $item`, which toggles the item's *open
  state*, not selection. Measured after a group-header click: `tree.selection()` is
  `()`, `table.selection` is `[]`, no `SelectionChange`. Item focus on a group header
  cannot leak into selection.
- **`_tree.focus` is read nowhere else in the `tableview` package** — nothing
  downstream assumes the focus item is a data row.
- **Taking focus on an empty-space click is not a regression** — ttk's own `Press`
  does `focus $w` unconditionally.

#### ✅ The three #421 review findings — ALL APPLIED 2026-08-06, nothing left here

Kept only because the measurements are worth not re-deriving. Landed as `5d169044`
(finding 1 + its test), `9e257368` (finding 2), `62950b0a` (finding 3), all now on
`main` via PR #424.

⚠ **Finding 1's test needed a real control to be worth anything**, and got one: run
against unfixed source it fails with `dragging a separator in checkbox mode resized
nothing` **while its own plain-table control arm passes first** — so the failure is
behavioral, not a broken harness. That is exactly the control the #417 review skipped,
which is how two defective tests got through there.

Original write-up follows.

1. **MEDIUM — `tableview.py:2918`: column resizing is DEAD whenever selection
   checkboxes are on.** `_on_header_click` special-cases only `region == "heading"`, so
   a click on a column **separator** falls into `if self._toggle_select_active():`,
   where `identify_row(event.y)` returns `""` — and the branch **still** returns
   `"break"`, swallowing ttk's `resize.press`. **Measured:** a plain table resizes
   (`120 → 156`); with `selection_mode="multi", show_selection_controls=True` none of
   its three separators move at all. The `break` is load-bearing **only when there is a
   row to toggle**. #421's diff compounds it — `_take_click_focus(iid)` sits *above*
   the `if iid:` guard, so a failed resize attempt now also yanks focus into the tree
   body. **Fix: move the call inside `if iid:` and return `"break"` only there.** The
   reviewer verified that change: all three separators resize (`#0` 43→79, `#1`/`#2`
   likewise) and all 23 `test_datatable.py` tests stay green. ⚠ **The breakage predates
   the branch** — but the diff edits exactly these lines. **No test covers the
   separator path either way; add one.**
2. **LOW — `tableview.py:2874`: swap `except Exception: pass` for
   `debug_log_exception`.** The defect #421 fixes *is* "focus silently did not happen";
   if `focus_set()`/`focus(iid)` raises, the fix degrades back to the original bug with
   no signal anywhere. `debug_log_exception` (`_runtime/utility.py`, #399) never
   raises, so it is safe in a Tk dispatch path. Neighbors do the bare `pass`, but this
   is new code.
3. **LOW — `CHANGELOG.md:25`: the headline overstates the blast radius.** "Clicking a
   `DataTable` row now leaves the keyboard pointed at that row" reads as though
   ordinary row clicks were broken. **They never were** — the branch's own control
   proves plain rows always took focus. Scope the headline to group headers and
   checkbox tables; the bullet body already says the right thing. Same standard that
   kept #397/#401 out of `0.2.1`.

### ✅ The `0.2.2` release sequence — ALL STEPS DONE (2026-08-06)

**Milestones are SETTLED (maintainer, 2026-08-06): #417, #418, #419, #420, #421 and
#422 are all on `0.2.x — Patch line`. There are ZERO unmilestoned open issues** —
verified against `gh`, and it clears the deviation this file used to flag. That
milestone now has **#422 and #207** left open.

All six steps completed: branches rebased (with `git diff main...HEAD -- CLAUDE.md`
empty on both — the trap that nearly bit #410), PR'd and merged as merge commits
(#423 then #424), `## [Unreleased]` promoted in its own commit, `bumpversion` run,
tag pushed, **published manually** (see START HERE), issues closed, #417 commented,
branches deleted. ⚠ The CHANGELOG bullet count is **7**, but do **not** read that as
"unchanged from the 7 recorded at `ff814b85`" — the column-resize fix **added** one
and consolidating the #418/#420 pair **removed** one. Coincidence, not stasis.

⚠ **The posted #417 comment is NOT verbatim the draft this file carried.** The draft
predated the column-resize fix (#421 review finding 1), so it said "four more defects"
and stopped at the focus bug. One sentence was appended covering the separator fix,
which is user-visible in the release notes. **A prepared draft goes stale when the
release grows** — re-read it against the final CHANGELOG before pasting.

Everything below is the backlog to pick from now that `0.2.2` is out.

**#409 is DONE (PR #414) — full entry in `docs/_dev/handoff-archive.md`.** Two
things from it are worth carrying here because they are invisible in the diff and
will bite again:

- ⚠ **`emit()` and `on()` take the same names but NOT always the same target.**
  `emit()` consults the `_event_target()` seam **only for `<<Virtual>>` sequences**;
  the native-mapped names (`click`/`focus`/`blur`/`submit`) fire on `_internal`, so
  `field.emit("submit")` on a retargeting composite reaches nothing bound through
  `on()` — silently. Documented in both `PublicWidgetBase.emit`'s docstring and
  `docs/reference/events.rst` now; it was only in the docstring before.
- ⚠ **`resolve_event()`'s error is process-wide, not per-widget.** `all_known` is a
  union of `GLOBAL_EVENT_MAP` and **every** `_CLASS_EVENT_MAPS` entry, so a `Button`
  typo is reported alongside `cursor_move`/`export`/`item_drag_start`. Narrowing it
  is folded into **#412**, not done. Don't write docs claiming the error lists what
  *that* widget knows — the branch shipped that sentence and the review caught it.

**⚠ `## [Unreleased]` is ABSENT ON `main`** — `0.2.3` consumed it (the top section is
now `## [0.2.3] — Import without IDLE`, with its `[0.2.3]:` link definition at the
bottom). The next fix commit re-creates it, per the convention under Release flow.

**⏭ The next targets, in milestone order (see the table above for why).**

**#390 is the exception to the order and can be taken at ANY time — it is a
DECISION, not work.** Should signals model emptiness at all? (`0.4.0`.) The
write-up below is complete and the maintainer is actively evaluating (discussion
#386); it needs an answer, not more analysis. Cheapest item on the board and the
largest unblock, since it gates #389 shipping *whole*. **Do not re-derive it.**

Otherwise, first substantial work is the **`Test and release confidence`**
workstream, in this order:

1. **#407 — the harness scene reset.** Best-understood open work in this file: root
   cause known, payoff measured (widget leg **144s → 80s**), and it makes PageStack
   pass with no `isolated` marker. Its old blocker (#392) shipped in `0.2.0`. ⚠ The
   patch itself is LOST and must be re-derived from the recorded root cause below.
2. **#380 — CI.** Nothing runs the suite on push; every Tk 9 bug so far was found by
   a user or by hand. Take it *after* #407 so the automation is cheaper and the suite
   it automates actually passes. Largest item here; read the issue before scoping.

Then `0.3.0 — Strictness and value types` as one batch (#383, #369, #408, #416),
then `0.4.0` (#389 behind #390, #412, #415). **#412** is small and well-scoped:
publish an existing internal front door so composite authors get a documented
bare-name path *while keeping the typo guard*. Until it lands,
`docs/reference/events.rst` stays **deliberately silent on custom events** — that
silence is the one real cost of how #409 shipped.

**⚠ #415/#416 came from discussion #413** (a user asking for `PathField` in a
`Form`). Both were filed 2026-08-05 with a probe at
`development/probe_413_pathfield_value.py`; **the maintainer replied on #413 the
same day, so that loop is closed.** The measured finding worth not re-deriving:
**10 of the 12 public field-family widgets are `Form` editors — the two that are
not are `PathField` and `TimeField`** — and an unknown `editor=` name **silently
builds a `TextField`** (`_impl/composites/form.py:774`). `DateField` being an
editor while `TimeField` is not is what makes this drift rather than a design
boundary.

**⚠ `open_multiple` is FULLY DECIDED (maintainer, 2026-08-05) — nothing left to
settle before implementing #416.** The contract: **`open_multiple` → `tuple[Path,
...]`, empty `()`; every other mode → `Path | None`, empty `None`.** #416's body
still presents this as an open question with two options; **the decision lives in a
comment on the issue**, not the body. The rejected option was a second property
holding the tuple — one concept, two names. Two costs accepted deliberately: the
return type depends on a construction argument (`open_multiple` selects a different
*kind* of thing, and the `', '` join it replaces is already lossy), and **`()`
rather than `None` when empty is a deliberate exception to the framework's
`None`-when-empty convention** — the type stays stable so callers iterate without a
guard, and for a multi-select "nothing selected" and "an empty selection" are the
same state.

**⚠ Two test-coverage gaps, same class — fold both into #380.** `testpaths` is
`tests/cli`, `tests/widgets/public`, `tests/data`, so **anything outside those
never runs**: (a) the 12 files / 25 tests directly under `tests/widgets/`, and
(b) **`tests/test_public_surface.py`** — the guard for the curated public namespace
(PR #104), which the widget-review standard lists as a verify step. Run by hand at
the `0.2.1` tag: **166 passed**. It is green; it is just never run by `run_gui.py`.

**⚠ What THIS FILE got wrong about the cluster — the pattern is the lesson.** The
2026-08-05 review re-read `7e204801` (#401) and #397 (then `6520597b`, shipped as
`a93a47a4` after the timer fix was folded in) precisely because
an earlier whole-branch pass had already been wrong three times about #397. That
re-read found two more defects, so the running count is **four** — and one of them
was in this file:

- **This file claimed "the branch no longer touches `CLAUDE.md` at all." It did.**
  The `docs(claude):` *commits* had been dropped, but the CLAUDE.md edits were
  folded into the #396 commit instead — a 252-line rewrite descending from
  `e23207b4`, i.e. `main`'s **pre-cluster** handoff. Merging #410 would have applied
  84 insertions against 168 deletions to `main`'s handoff, silently reverting three
  `docs(claude):` commits. Caught by diffing `main...HEAD -- CLAUDE.md`, not by
  reading. **Run that diff before merging any branch.** The rule it protects still
  holds: handoff state lives on `main` only.
- **The #397 end-to-end test leaked a 10s `after` timer** on the shared root, and
  its module is not in `ISOLATED` — so the timer fired during a later test and
  destroyed an unrelated `Toplevel`. **The test passed either way**, which is what
  made it invisible. Measured 1 leaked timer → 0. A test that schedules a hang guard
  must cancel it in a `finally`.

**⚠ A probe that finds nothing must be proven able to find something.** The #401
completeness check (an AST scan for handlers bound to a virtual sequence that
return `'break'`) reported **zero hits** — because `ast.parse` was choking on a
**UTF-8 BOM** and a bare `except Exception: continue` swallowed it, silently
skipping every file. Reading `utf-8-sig` and re-running against the pre-fix commit
as a control reproduced exactly the two known handlers, which is the only thing
that made the post-fix zero mean anything. **Always run the control.** The same
session produced a second vacuity: a probe set `field.readonly = True` on a public
widget — a plain Python object — so the bogus attribute stuck silently and the field
kept stepping. The property is **`read_only`**.

#392 is DONE and merged — its full root-cause writeup, the four-commit breakdown,
and every gotcha moved to **`docs/_dev/handoff-archive.md`** (grep `#392`). **Read
that entry before touching `_runtime/events.py`**; it records things that cost real
time and are invisible in the diff.

**After 0.2.1, the realistic candidates:**

1. **#390 — should signals model emptiness at all? (DESIGN — milestone `0.3.0`;
   the maintainer is actively evaluating options as of 2026-07-30.)** Gates #389
   shipping *whole*: without it `Form.clear()` works but leaves a bound `Signal`
   stale. **If the answer is no, close #390** and ship #389 with the limitation
   documented. ⚠ The analysis below is COMPLETE — it needs a decision, not more
   work. The maintainer has publicly said they are evaluating (discussion #386),
   so do not re-derive it or ask the reporter to weigh in. `Signal.set(None)` raises
   unconditionally (`signal.py:248` — strictly monomorphic, type inferred from the
   seed). **Four decisions, in order:** (1) *do it at all?* (2) *declared or
   automatic?* — recommend **declared** (`Signal(v, nullable=True)`), because
   automatic-by-mode cannot cover `int` and isn't safe to lean on: `Signal(0)` is
   Python-authoritative only *while unrealized*, so the moment anything touches
   `.var`, `__call__` starts reading the IntVar and a stored `None` is lost;
   (3) *what happens to a non-nullable signal asked to go empty?* — recommend a
   public `Signal.nullable` so `ValueSignalMixin` skips rather than crashing
   `Form.clear()`; (4) *what does `map()` do over a nullable signal?* — it calls
   the transform unconditionally and infers the derived type from the first result
   (`signal.py:295, 302`), so a `None` source breaks the **documented** Date/Time
   pattern (typed `signal=` plus a `.map()`-derived text signal). **No existing
   code is at risk either way** — `set(None)` raises today, so nothing can
   currently receive it. **KEY MEASURED FINDING, don't re-derive it:** the
   dividing line is **attached-vs-not, not object-vs-native**. `NumberField(signal=)`
   / `DateField(signal=)` are **unrealized** — `ValueSignalMixin` syncs via
   `subscribe()` + `on_change` in pure Python and never touches `.var`, so **for a
   number field's value signal there is no IntVar at all**. `Checkbox(signal=)` and
   `TextField(textsignal=)` **are** the widget's `variable`/`textvariable` — there
   `None` either raises (`IntVar`) or **silently corrupts**: `StringVar.set(None)`
   stores the literal `'None'`, the widget displays it, and every subscriber gets
   the 4-character string. That is why a blanket guard relaxation must not ship.
   **Per-type "empty" values were considered and REJECTED** — `empty(int) = 0`
   contradicts the shipped `NumberField.clear()` decision, `empty(bool) = False`
   collapses tristate (#358), `date` has only a **sentinel** indistinguishable from
   data, and it makes emptiness type-dependent at every call site. The framework
   already runs both models in separate channels (`value` is `None` when empty,
   `text` is `''`) and keeping them separate is what stops either leaking into the
   other. Memory `reference_signal_nullability_attached_vs_not`.

2. **#389 — `Form.reset()` / `Form.clear()`.** Milestone `0.3.0` (moved out of
   0.2.0 so that release could cut). Unblocked (#387 merged), design
   settled, implementation sketch on the issue. **They are DIFFERENT verbs** —
   reset = construction-time originals, clear = `None`. Both justified: `reset()`
   is **not user-implementable** (after an edit, `get()` no longer knows the
   original); `clear()` is the data-entry case. Slider clears to `min_value` (no
   null state, and that is already the de-facto seeding behavior). Needs an
   `__init__` snapshot because `set()` destroys `_data`; both must clear
   validation state.

Then the standing items: **#407 (harness leak-fix)**, **#380 (CI)**, and **#383
(kwarg sweep)**.

### Then — standing infrastructure work

- **#407 harness leak-fix — UNBLOCKED NOW (#392 shipped in 0.2.0).** ⚠ **Tracked
  under #407 as of 2026-08-04.** It used to be described here under **#379, which
  is CLOSED** — so the best-understood piece of open work in this file had no open
  issue at all and was one handoff-reset away from vanishing. The real root cause
  of the order-dependence was found and deliberately left out: `conftest._region()`
  returns `_region_root`, which on a decorated App **is the root**, so
  `_snapshot`/`_reset_scene` never look inside the App's `_content_frame` — **the
  scene reset has been a no-op for content widgets for the entire life of the
  shared-root harness**, and every test's widgets pile up all session. Fixing it
  makes PageStack pass with no `isolated` marker and cuts the widget leg
  **144s → 80s**. Held back because it exposed **#392** — **shipped in 0.2.0, so
  that blocker is gone** — plus a second latent bug that is still open
  (`test_select_change_event_value_space` picking up 5 change events from earlier
  tests — looks like stale bindtag bindings surviving destroy while Tk recycles
  widget path names; not chased down). Own branch. **This is the best-understood
  piece of open work in the file** — root cause known, payoff measured.
  ⚠ **The patch is LOST.** It was saved to a per-session temp `scratchpad/`, not
  into the repo — searched every session dir under
  `%LOCALAPPDATA%\Temp\claude\D--Development-bootstack\`, nothing. **It must be
  re-derived from the root cause above, which is fully recorded.** Lesson: a
  handoff artifact belongs in `development/` (persistent) — a bare `scratchpad/`
  path in this file does NOT survive the session.

- **#380 — CI test workflow.** `.github/workflows/` still has only `docs.yml` +
  `release.yml`, so **nothing runs the suite**; every Tk 9 bug so far was found by
  a user or by hand. Branch `ci/test-workflow` was created and deleted unused —
  recreate it. Plan agreed: **(1)** headless `ubuntu-latest` logic job —
  `test_tk9_scaling_baseline.py` monkeypatches `platform.system()`/
  `tkinter.TkVersion` so it needs **no display and no Tk 9**, and would have caught
  #375; **(2)** an `xvfb-run` Linux job for the widget suite; **(3)** fold in the
  never-collected `tests/widgets/*.py` gap. **DEFER the macOS/Tk 9 leg** — blocked
  on #378 (the suite cannot complete on Tk 9 at all), red from day one. Read the
  issue before scoping: it carries measurements showing the naive "just run
  pytest" plan fails (`-m "not gui"` selects 741 tests but yields **494 errors**
  headless — only ~222 genuinely run without a display), and warns that
  `Treeview.bbox()` returns `''` rather than erroring on an unmapped window, so
  geometry assertions **vacuously pass** headless.

### Open, additive items (not ship-blockers)

- ~~**#396 / #397 / #398 / #399 / #400 / #401 / #405**~~ — **ALL CLOSED, SHIPPED in
  `0.2.1`.** The event-target facts are worth keeping, because they are invisible in
  the diff. `on()` resolves through **one seam**,
  `PublicWidgetBase._event_target(sequence)` (`widgets/_core/base.py`); the ten
  retargeting wrappers override only that (~5 lines each) and their duplicated
  `on()` overrides are gone (−262 lines). **`tabs.py` never retargeted at all** —
  the issue over-counted at eleven; its `on()` was a byte-for-byte copy of the base
  and was simply deleted. ⚠ **`emit()` consults the seam ONLY for `<<Virtual>>`
  sequences** — for the public names that map onto real Tk sequences
  (`submit`/`focus`/`blur`/`click`) it fires on `_internal`, because generating one
  at the inner entry *drives* the widget instead of notifying about it. Regression
  coverage: `tests/widgets/public/test_event_target_seam.py`. ⚠ The `Slider` control
  test needs **`shown_app`, not `app`** — see the unmapped-window gotcha above.
  **The old warning that a test pairing `emit()` with `on_*()` must pick a widget
  where the two agree is now OBSOLETE everywhere** — they cannot disagree.

- **#376 — DataTable cell padding ignored on Tcl/Tk 9** (checkbox flush to the row
  edge, columns collide). Open in `0.2.x`, **unverifiable on either box** — the
  Windows box is Tk 8.6 and the macOS box is Tk 8.6 too. Needs a Tk 9 environment,
  same blocker family as #378.

- **#383** — follow-up sweep from #381: presentation kwargs still degrading
  silently (`density`, `Tabs.orient`, `Slider.orient`, `Gauge.variant`) **plus**
  args that raise but leak a **raw `TclError`/`AttributeError`**
  (`Button.icon_position`, `Label.justify`, `Scrollbar.variant`,
  `Expander.icon_position`, `ProgressBar.mode`). Sweep **BY ARGUMENT NAME**, not
  by widget. Also folds in: **`Slider.value = None`** leaks a raw
  `TypeError: float() argument must be...` (reachable from user code via
  `form.set({'slider_key': None})`), and **`show_grid=True` is silently accepted
  on `Row` and does nothing** — not a kwarg anywhere in `src/`, but swallowed into
  the layout kwargs without error (the #394 reporter used it *while trying to
  diagnose the bug* and got no feedback).
- **#369** — the selection family disagrees on off-list values (`SelectButton`
  raises both ways; `RadioGroup` accepts at construction, raises on assignment;
  `ToggleGroup` accepts both; and where accepted, `value` says `'MX'` while
  `selection` says `None`). Wants ONE family decision, not four patches.
- **#369 and #383 are milestoned `0.6.0 — Argument and value strictness`** — both
  would raise where the framework currently accepts, so they cannot ride the
  `0.2.x` patch line and needed a minor of their own. `0.6.0` was created for
  exactly this and placed AFTER the themed minors so nothing was renumbered
  again. #352 → `0.5.0 — Structured editing`; #328 → `0.2.x` (follows the
  hot-reload umbrella #322).
- **#208** — DataTable: persist selection by record id across search/sort/page.
- **#192** — color-swatch `Select` control (decision-gated; lock shape/naming with
  the maintainer first). A `Select`-style dropdown rendering color swatches inline,
  complementing `ask_color()`. New widget or Select variant?
- ~~**#222** (TextField live properties) and **#234** (SpinnerField↔NumberField
  parity)~~ — **both CLOSED; removed from the backlog 2026-08-04.** They sat here
  as open items long after the fact. ⚠ **Verify an issue is still open before
  acting on a bullet in this file** —
  `gh issue view <n> --json state --jq .state`.
- **#207** — ContextMenu outside-dismiss vs a `'break'` target — **DEFERRED** (no
  API implication, low/self-inflicted impact, Win/Linux only; agreed proportional
  fix if revisited = a module-level open-menu registry + dismiss-all from
  `DataTable._on_header_click`, NOT the risky grab). Analysis on the issue.
- **#328** — the E2E multi-file `@reloadable` reload test is the one OPEN piece,
  **DEFERRED** (the maintainer will write it). On PROVISIONAL `bootstack.dev`.
- **Gallery opt-in keyboard-focus ring** (future) + deferred Gallery perf (debounce
  `<Configure>`, bounded thumbnail-PhotoImage LRU, cache `_fit_caption`). Scope to
  keyboard focus, NOT hover. Memory `project_gallery_focus_ring`.
- **`add_spacer()` → public `Spacer`** — deferred, entangled with
  `feat/unified-toolbars` (the internal `Toolbar` is pack-based). Memory
  `project_unified_toolbars`.
- **Code-review follow-ups #4–#10** — cleanup/altitude items recorded in
  `docs/_dev/widget-api-audit.md` (SelectButton stale value after `options=`;
  screenshot Win64 HWND hardening; group/window/date duplication; Calendar
  batch-redraw).
- **Docs site fleshout — substantially DONE.** Remaining is only opportunistic: a
  review pass on `installation`/`quickstart` and enrichment of any still-thin page.
  Memory `project_docs_site_fleshout`.

---

## Release flow

**⚠ Use `py -3.12 -m bumpversion`, NOT the `.venv` shim.** This file used to point
at `.venv/Scripts/bump-my-version.exe` — that shim is part of the **stale `.venv`**
and dies with *"Access is denied"* on its `Python314` path, like everything else in
there. ⚠ **It DISAPPEARS — check for it before every release.** Recorded here as
installed 2026-08-05 (v1.5.0), it was **gone by 2026-08-08** (`No module named
bumpversion`) and had to be reinstalled with
`py -3.12 -m pip install --upgrade bump-my-version` (now **v1.5.1**). That is twice
this environment has lost a release-critical tool, so verify rather than assume.
⚠ **The import name is
`bumpversion`, not `bump_my_version`** — probing the wrong one reports "no module"
on an interpreter that has it perfectly well, which cost a wrong conclusion during
the `0.2.1` release.

`py -3.12 -m bumpversion bump patch` → push `main` + the `v*` tag → `release.yml`
(PyPI + GitHub Release) → `docs.yml` deploys. `release.yml` fires on `v*` tags
only. There is **no `development` branch** (CONTRIBUTING.md + the localization
workflow target `main`).

⚠ **POST-RELEASE: `gh issue close --comment "..."` SILENTLY DROPS THE COMMENT when
the issue is already closed** — and a PR body containing `Closes #N` closes it at
merge, which is the normal case. `gh` warns only about the close and says nothing
about the comment, so the "it's live" note is lost without a visible error. Post it
with **`gh issue comment N --body ...`** instead, and **verify it landed** with
`gh issue view N --json comments`. Bit `0.2.3`.

⚠ **`docs.yml` is CHAINED to `release.yml` SUCCEEDING**, not to the tag or the push —
it triggers on `workflow_run` of "Release" `completed` and its `build` job is gated on
`github.event.workflow_run.conclusion == 'success'`. So **any release that does not go
through a green `release.yml` run leaves the docs site stale, silently** (the run shows
as `completed/skipped`, which reads like a no-op). Kick it with
**`gh workflow run docs.yml --ref main`**.

⚠ **When Actions is down, publish by hand** — full recipe under START HERE
(`0.2.2` shipped that way on 2026-08-06). Short version: build from a
`git worktree` of the tag, `py -3.12 -m twine upload --config-file
D:/Development/bootstack/.pypirc dist/*`, then `gh release create`, then the docs
command above. **CI itself has no token** (OIDC trusted publishing), so the
gitignored repo-root `.pypirc` is the only local credential.

**CHANGELOG convention:** a fix commit writes `## [Unreleased]`; the promotion
commit renames it AND adds the `[X]:` link definition. **`## [Unreleased]` is absent
on `main`** — `0.2.3` consumed it, so the top section is
`## [0.2.3] — Import without IDLE` (1 `### Fixed` bullet) with its link definition at
the bottom. The next fix commit re-creates it. ⚠ **Verify the extraction against the
REAL file before tagging, not a simulation** — `release_notes.extract('X.Y.Z', ...)`
returns `(title, body)`; confirm the title carries the descriptive suffix, the body
starts at `### Fixed`, and no bottom link definitions leaked in.

**⚠ An entry earns its place by being REACHABLE.** `0.2.1` deliberately omitted
#397 and #401 because no public API could reach either defect; `0.2.0` did the same
for #387. A CHANGELOG is read by someone asking "was I affected?", so an entry for
an unreachable defect is a false positive. Check `__all__` and the public event
registry before writing the bullet — and say so in the commit message, since that
is where the omitted work stays documented.

**⚠ Verify the rendered release notes BEFORE tagging** — the extraction is scriptable:
`py -3.12 -c "import sys; sys.path.insert(0,'.github/scripts'); from release_notes import extract; print(extract('X.Y.Z', open('CHANGELOG.md',encoding='utf-8').read())[0])"`.
The **title** comes from the descriptive suffix after `## [X.Y.Z] —`, so a section
promoted without one ships a release titled bare `X.Y.Z`. Confirm the body starts
at `### Fixed` and that no bottom link definitions leaked in.

**⚠ Write CHANGELOG entries ONE PARAGRAPH PER LINE — do not hard-wrap them.**
`.github/scripts/release_notes.py` lifts a version's section verbatim into the
**GitHub Release body**, which renders a soft line break as a visible one, so
80-column wrapping produced ragged notes that could not reflow to the reader's
window. Unwrapped renders identically in the repo file view and in the Sphinx docs
(both treat a soft break as a space) and correctly on the release page. The 0.2.0
section is unwrapped; **older sections are left wrapped — do not reformat shipped
history.** Same rule for PR bodies, issue bodies, and review comments. Memory
`feedback_no_hard_wrap_in_responses`.

**Read the whole `## [Unreleased]` section before promoting it.** 0.2.0's had
accreted across five fixes and nobody had read it end to end: **three entries were
filed under `Changed` but were plain bug fixes** (#388 picker, #387 clear, #387
`Form.set`), which handed a reader scanning for upgrade risk three false positives
before the one that mattered. Section order also contradicted the file's own
declared Keep a Changelog format (`Fixed/Changed/Added` instead of
`Added/Changed/Fixed`). Both fixed in `199b4081`.

**⚠ Release-flow gotcha:** `bump-my-version bump patch --allow-dirty` commits
**ONLY `pyproject.toml`** — it will NOT sweep the CHANGELOG rename into the
`Release X` commit, which ships a release whose notes still say `## [Unreleased]`
and breaks `release.yml`'s section extraction. **Promote `## [Unreleased]` to the
version in its OWN commit BEFORE running `bump-my-version`.** Confirmed working on
0.1.8: `docs(changelog): promote Unreleased to 0.1.8` (`7c136b20`) ran *before*
`Release 0.1.8` (`b2f37f0f`, which again touched only `pyproject.toml`).
`release.yml` extracts ONLY the `## [x]` section, so bottom link-defs are excluded
from the GitHub Release body.

---

## Working agreements

**Hold commits until the user tests; per-commit approval.** Never commit feature
work to `main` — create a dedicated `feat/*` branch first. A fix pushed to a branch
AFTER its PR merged is **stranded** — verify it landed in `main`.

**Standing principles** (apply in every review):

- **Live properties only for legitimate runtime needs**
  (`feedback_live_properties_runtime_need`) — e.g. `surface` is **build-time, not
  live**.
- **Prefer Tk native/virtual-event bindings**; don't undo a convention without
  reason (`feedback_prefer_native_bindings_dont_undo_conventions`).
- **Describe the clean public surface in docs — no implementation/toolkit detail**
  (`feedback_no_toolkit_internals_in_docs`).
- **Adversarially verify reviewer and agent claims** — agents over-flag. The
  2026-06-22 trust audit disproved 2 of the "bugs" it was handed; the Topic-guide
  review agents over-flagged 10 of 12 pages.
- **Pause and ask when a fix outgrows its issue**
  (`feedback_pause_and_ask_when_stuck`) — #355 burned hours heading toward a
  `Select` value-model rewrite before the maintainer pointed at the ~15-line fix.
- **Test PUBLIC paths, not internal side-hacks.**

### Techniques that have repeatedly beaten static reading

- **Run an empirical probe instead of reading tangled code.** Decisive on the
  icon-DPI pipeline, the boolean-control ttk state rules, the menu window-move
  dismiss, and the #394 field alignment (FlexFrame / GridFrame / raw pack are too
  tangled to trust by eye). **Rebuild the probe rather than reading**, if one of
  these areas comes up again.
- **Tests must fail for the RIGHT reason.** A pre-fix `AttributeError` proves
  nothing — it only shows the new method doesn't exist yet. Stub the collaborator
  (e.g. a tiny fake `DateDialog` with `on_result`/`show`/`result`) so the failure
  is *behavioral*. Tests that only assert "construction doesn't raise" are what let
  #358 ship twice. Memory `feedback_tests_must_fail_for_the_right_reason`.
- **Pair any alignment/geometry assertion with a precondition** proving the setup
  really took effect, or it can pass vacuously. **Measure within one process** —
  `winfo_rooty()` is NOT comparable across two runs (different window positions).
  Memory `reference_geometry_probe_same_process`.
- **⚠ `event_generate` on a virtual event is DROPPED for some widgets while the
  window is unmapped — use the `shown_app` fixture, not `app`.** The `app`
  fixture's root is **withdrawn** (`wm_state() == 'withdrawn'`, everything
  `winfo_ismapped() == 0`). A `bs.Button` still dispatches `<<Click>>` there, but a
  composite like `bs.Slider` receives **nothing** — not even a **raw Tcl** binding
  bypassing Python entirely, which is what proves it is Tk dropping the event and
  not a bootstack wiring problem. So a payload test can look like a broken fix
  when the fix is fine. `shown_app` maps the window and it works
  (`winfo_ismapped() == 1`). **Pre-existing** — it measures identically with any
  event-system change stashed, so confirm that with `git stash` before blaming
  your own diff. Cost real time during #392. Memory
  `reference_virtual_event_needs_mapped_window`.
- **⚠ `shown_app` is NOT enough — a widget packed into the shared root may still be
  UNMAPPED.** The `shown_app` root is mapped, but `pack()`ing a raw frame into it
  competes with the App's own geometry management, and **once earlier tests have
  filled the root the frame does not get mapped at all** — so synthesized key
  events are dropped exactly as above. The tell is a test that **passes alone and
  fails in the suite** (#405 cost a full suite run here). Worse, it fails as a
  *false negative about the thing under test* — the #405 control read "the trap is
  gone" when the trap was fine and the window was not. **Build a real event target
  in its own `Toplevel`** (`geometry(...)`, `deiconify()`, `update()`,
  `focus_force()`), and **assert `winfo_ismapped()` as a precondition** so a repeat
  cannot be silent. Same family as the "pair a geometry assertion with a
  precondition" rule.
- **⚠ Never `warnings.warn` from inside a Tk dispatch or a teardown path — use
  `debug_log`.** `_runtime/utility.py` has **`debug_log(message)`** (added by #399)
  beside `debug_log_exception`; both honor `BOOTSTACK_DEBUG` and **never raise**.
  A `warnings.warn(..., RuntimeWarning)` measurably escapes `Subscription.cancel()`
  and its `__exit__` under `-W error`, turning a diagnostic into a failure on two
  paths documented as safe to call on an already-dead handler. A diagnostic that
  can fail the program it is diagnosing is not one. Use `debug_log` when there is
  no exception to log; `debug_log_exception` when there is.
- **Run the BASELINE before the fix**, so a before/after transition is *observed*
  rather than assumed. That is what turned "the branch fixes only 2 of 6" from a
  suspicion into a fact. ⚠ **On a branch, "baseline" means CHECK OUT `main`** — a
  #417 probe read zero on both arms until it turned out to be running against
  `main` the whole time. Print the branch, or `git checkout` it deliberately.
- **⚠ To prove a fix does not over-reject, ENUMERATE THE PRODUCERS, don't reason
  about the consumer.** #417's guard tightened `if not iid` to
  `if not iid or iid not in self._row_map`. Arguing from the handler could not
  settle whether some legitimate row is missing from `_row_map`; grepping all four
  `self._tree.insert` sites settled it in one command — three write
  `_row_map[iid] = rec` on the very next line, the fourth is the group parent. **A
  guard's safety is a property of who fills the collection, not of who reads it.**
- **⚠ A stale METRIC in this file becomes a phantom regression signal.** A recorded
  `919 passed` went unrevised while `main` grew to 976 collected, so the next
  session read the difference as an unexplained 46-test gap in a branch that added
  2. `--collect-only -q` on both refs settled it in seconds. **Record the date and
  commit beside any count, or don't record it.**
- **A control experiment separates causation from correlation.** For #392 it was
  not enough that cancelling `sub_a` silenced `sub_b`; stripping the orphaned
  binding line by hand and watching `sub_b` come back is what proved the cause. Do
  this before filing any "X breaks Y" claim.
- **Bisect order-dependent failures; do not theorize.** A scripted prefix-bisect
  found the culprit file in 6 runs; a geometry probe turned "state pollution" into
  "reqheight 1242 > window 828, so the geometry manager unmapped it".
- **Measure the surface before scoping a sweep.** An AST pass over public
  `__init__` signatures + a construct-with-a-bogus-value probe turned "audit the
  siblings" from guesswork into a table (215 kwargs, 17/24 silently accepting) —
  which is what justified drawing #381's line at behavior modes.
- **A platform-specific backend is often constructible off-platform.**
  `_NativeContextMenu` (macOS) is a `tk.Menu` wrapper and instantiates fine on
  Windows, so macOS-only code got real coverage — and that caught a
  `TclError`-on-separator bug. Ask "can I build the other platform's object
  directly?" before accepting "unverifiable from this box".
- **Before fixing a silent no-op, find what is LEANING on it.** `Form.set()`
  applied `None` to every absent field and only worked because the write was
  discarded — repairing the sentinel alone would have turned every partial
  `form.set()` into a destructive overwrite. A no-op that has shipped for a while
  is load-bearing somewhere.
- **Prefer re-entering an existing routine over re-emitting an event by hand.**
  The #388 fix calls the entry's own `_check_if_changed()` rather than building a
  `ChangeEvent`, getting the `_prev_changed_value` bookkeeping for free.
- **⚠ Spying on an instance attribute is USELESS if the bound method was already
  captured.** `self.on_destroy(self._cleanup_x)` captures at construction, so
  `obj._cleanup_x = spy` set afterward never fires and reads as "cleanup never
  ran". **Patch the CLASS attribute before constructing**, or assert on the
  observable side effect.
- **⚠ Some failures are INVISIBLE TO PYTHON — read the interpreter's
  background-error channel.** A binding or `after` script that references a deleted
  Tcl command raises nothing Python can see; the suite stays green and the symptom
  is "handlers mysteriously stopped running". Install a collector
  (`root.tk.createcommand('bgerror', collector)`, and `deletecommand` it in a
  `finally` so the shared root is left clean) and assert the list is empty. This is
  what #392 was, and it is what caught a scheduling defect in #392's own fix. When a
  bug has no public observable, this channel IS the observable — reach for it before
  concluding "cannot be tested".
- **⚠ Defer widget cleanup on the ROOT, never on the widget.** `widget.after_idle(cb)`
  registers `cb` as a command owned by that widget, so destroying the widget deletes
  `cb` while the timer is still pending and Tcl fires an orphan. Use
  `widget._root().after_idle(...)`: the root outlives every widget, and when the root
  goes the pending callback goes with it. Guard the callback against both `TclError`
  **and `AttributeError`** — `destroy()` sets `_tclCommands` to `None`, which
  `deletecommand` then cannot update. Cost a real defect in the #392 follow-up.
- **⚠ Tkinter binding names are recycled — never let a deferred cleanup hold one.**
  `Misc._register` names a command `repr(id(bound_method)) + func.__name__`, and
  that bound method exists only for the registration, so releasing the command
  frees the address for immediate reuse: **498/499** consecutive bind/cancel/bind
  cycles returned the *identical* name. Anything that postpones a
  `deletecommand` can therefore delete a *different, live* binding. If you defer
  cleanup keyed on a tkinter callback name, make the name unique first (a serial
  in `func.__name__` is enough and keeps stock's bookkeeping). Cost a critical
  defect in #392's own fix. Memory `reference_tkinter_funcid_recycling`.
- **⚠ When a symptom is allocator- or timing-dependent, assert the INVARIANT, not
  the symptom.** The above fails only when the allocator happens to hand the
  address back, so behavioral tests passed on a broken build — 1 of 3 caught it
  on the first pre-fix run. A structural test (50 cancel/rebind cycles → 50
  distinct ids) fails every time. Worth breaking "test public paths" for; say why
  in the test.
- **⚠ A bulk `pathlib` rewrite flips CRLF→LF** (repo is `core.autocrlf=true`) —
  same class as the `sed -i` trap. Prefer the Edit tool; if scripting, write bytes.
  Memory `reference_autocrlf_sed_gotcha`.

---

## Recently shipped — pointers only

Full detail (root causes, decisions, gotchas) is in
**`docs/_dev/handoff-archive.md`**, indexed by issue/PR number.

| Release | Contents |
|---|---|
| **0.3.0** | SHIPPED 2026-08-11 (PyPI + tag `v0.3.0`), titled *Screen capture and dialog results*. **`release.yml` ran clean**, docs chained off it. **A minor carrying two additions and SIX fixes** — the release that proved the "minors are for additions" reading of this file wrong. **#427** `widget.capture(path)` writes a widget, window or app to `.png`/`.jpg`/`.pdf` (PR #443, from an external user's discussion #425) · **#429** a click during `settle()` re-entered the handler: `settle()` still dispatches, and holds `tk busy` — the first fix, which stopped dispatching, was REVERSED because it photographed stale pixels on macOS · **#428** `FormDialog.result` returned display text instead of the value, because it read after the dialog closed and every editor was destroyed (external report, PR #442) · **#437** a refused press still recorded its result, so cancelling after a refused `DataTable` Delete **deleted the record**; validation now runs only for buttons that submit · **#438** `DialogButton.closes` meant three different things and is REMOVED, replaced by returning `False` from a command. ⚠ `tk busy` is a no-op on macOS (measured in plain tkinter — a toolkit limitation, not a wrong invocation) and real on Windows; the input guard is documented as such rather than claimed to work everywhere |
| **0.2.3** | SHIPPED 2026-08-08 (PyPI + tag `v0.2.3`), titled *Import without IDLE*. **Published by `release.yml`, which ran clean** — Actions had recovered, so the docs deploy chained off it with no manual kick. Single issue: **#430** — `import bootstack` raised `ModuleNotFoundError` on any Python build without `idlelib` (Debian/Ubuntu package IDLE separately), taking down the WHOLE framework rather than degrading `CodeEditor`; `idlelib` is stdlib so it could never be a declared dependency, and the fix ports `WidgetRedirector` into `textarea/redirector.py` (PR #435). Also added a PSF attribution to `NOTICE`, scoped by measurement to `redirector.py` alone — see Current state for why the other five IDLE-derived modules are deliberately NOT listed |
| **0.2.2** | SHIPPED 2026-08-06 (PyPI + tag `v0.2.2`), titled *DataTable group headers and row events*. **Published MANUALLY with `twine` during a GitHub Actions major outage** — `release.yml` never ran, and the docs deploy had to be kicked with `gh workflow run docs.yml` because it triggers off a successful Release run (see START HERE). #417 `<Double-1>` bound unconditionally so `on_row_double_click` fires on a read-only table (PR #423) · #418/#420 group headers no longer fire row events with an empty record · #419 deferred chevron refresh after an event-driven expand · #421 click focus on group-header and checkbox-mode rows, plus the column separator that could not be dragged in checkbox mode (PR #424). ⚠ Two behavior notes shipped under `### Changed`: a double-click delivers `on_row_click` **click, double, click** (the double lands BETWEEN the clicks), and a read-only table's second press no longer repeats the first press's action |
| **0.2.1** | SHIPPED 2026-08-05 (PyPI + tag `v0.2.1`), titled *event and shortcut correctness*. #403/#404 sidebar shortcut + #406 its test coverage · #405 `Command`/`Option` modifier map (PR #411) · the #392-review cluster (PR #410, merged as a **merge commit** to keep its six one-per-issue commits): #396 `emit()`/`on()` share one `_event_target()` seam · #398 `on_visibility_alpha` self-unbind · #399 unmatched-unbind report under `BOOTSTACK_DEBUG` · #400 failed cancellation no longer reports success · **#397** dialog result fired at a destroyed widget and **#401** `'break'` from a non-interactive field — both fixed and merged but **absent from the CHANGELOG**, being unreachable from public API (root causes live in `a93a47a4` / `7e204801`) |
| **0.2.0** | SHIPPED 2026-07-30 (PyPI + tag `v0.2.0`). #332 internal `set_*_visible` → properties · #379/#385 menu-backend test portability · #381 `InvalidChoiceError` on bad behavior-mode kwargs · #387 `DateField` clear + `Form.set()` merge · #388 date-picker `<<Change>>` · #394/#395 field row alignment · #392 subscription cancel (script shape + mid-dispatch `unbind` + return values inert + unique binding names) |
| **0.1.8** | macOS sizing on Tcl/Tk 9 (Aqua 72→96 DPI baseline broke `detect_scale_factor()`) |
| **0.1.7** | Tk 9 scroll-event contract (`<TouchpadScroll>`, ±120 deltas, X11 TIP 474) + attach theme repaint |
| **0.1.6** | Seven form/field/validation fixes (#362–#368, #371) |
| **0.1.5** | Boolean-control state reads + Checkbox tristate (#360) |
| **0.1.4** | `Select.add_validation_rule` restored (#357) |
| **0.1.3** | Form `editor_options` take public widget kwargs (#354) |
| **0.1.2** | Dropdown/context menus dismiss on window move (#345) |
| **0.1.1** | `pygments` declared as a runtime dependency (#344) |
| **0.1.0** | STABLE. Ship gate (#335) + theme-repaint unification (#338) + accent contrast (#340). Public compose API FROZEN under SemVer. `bootstack.dev` stays PROVISIONAL (excluded from the freeze). |

Pre-0.1.0 initiatives — also in the archive: hot reload (`bootstack dev`),
builder-function scaffolds, docs-IA 3-pillar restructure, splash screen, icon-DPI
sizing, navigation API reshape (AppShell + Workbench), layout redesign
(screen-axis grid engine), undecorated window chrome, media widget suite, the
field-family reviews, field validation redesign, and the API Reference restructure.

---

## Carryover (deferred)

- **Reference docs examples** — LARGELY DONE in PR #103 (errors/scheduling/
  shortcuts/validation enriched; new `localization.rst`). `reference/store.rst`
  already carries the persistence patterns (`from_store`/`update(**kwargs)`,
  store hygiene, version skew, window-geometry-stays-a-flag) from the AppSettings
  work. Remaining: opportunistic enrichment of any still-thin reference page.
  Memories `project_docs_initiative`, `project_app_settings_flattening`.
- **Docs build is now warning-free** (PR #106). ⚠ Keep it that way: incremental
  Sphinx builds MASK warnings — always clean-build (`rm -rf docs/_build`, then
  `sphinx-build -W --keep-going`) to verify. When adding dataclass/attribute
  docstrings, follow the attribute-docstring pattern (NO `Attributes:`/`Args:`
  block for fields) and keep any colon OFF the first line of an attribute
  docstring (see the colon-space gotcha under PR #106 above).

---

## Prior initiative — Sphinx docs + public API audit (MERGED)

Branch `feat/docs-api-improvements`, merged to `main`. Shipped: the docs structure,
the public Table (`DataTable`), the typed-event redesign, the theming + font public
APIs, the DataSource verb rename + filtering DSL, and the observable-query layer.
Full detail lives in git history and memories; only the still-live conventions and
the open backlog are kept here.

### Still-live conventions

- **Docs structure** — top-level navbar is **3 pillars** (numpy-style):
  **User Guide · Widgets · API Reference** (`docs/index.rst`). (The old **Production**
  pillar was folded into the User Guide as the **Developer tools** caption — PR after
  #330, 2026-06-24; navbar overflow stays low.)
  - **User Guide** (`docs/user-guide/index.rst`) folds Getting Started + Tasks +
    Reference + the former Production pages into ONE pillar with four `:caption:`
    toctree groups — **Getting started** (`/getting-started/*`), **How-to guides**
    (`/tasks/*`, goal-indexed recipes), **Feature guides** (`/reference/*` +
    `/production/app-settings`, subsystem-indexed usage guides — renamed from
    **Topics** 2026-06-24; both how-to and feature guides are example-rich — the split
    is goal-vs-subsystem, NOT recipe-vs-theory, so do NOT call them
    "Concepts"/"Explanation"), and **Developer tools** (`/production/cli` ·
    `hot-reload` · `debugging` · `distribution`). The leaf pages STAY in their
    `getting-started/`/`tasks/`/`reference/`/`production/` dirs (no URL churn — the
    `production/` dir name is now just an internal artifact); only the landing + top
    toctree changed. The section `index.rst` landings (incl. `production/index.rst`)
    are DELETED. **`composing-fields` → `customizing-fields`** (#323, the one accepted
    URL churn — the title clashed with "Composing with Builders"; no redirect, per the
    no-shims stance).
  - **Widgets** (`docs/widgets/index.rst`) = flat leaf pages grouped by
    `.. toctree:: :caption:` blocks (curated common-first order, NOT alphabetical);
    kept as its own pillar (large *visual* catalog). The 10 old category landing pages
    are RETIRED. `docs/api/` + `docs/deeper/` are GONE.
  - **API Reference** (`docs/api-reference/index.rst`) = the by-concept lookup layer
    (semantic groups, full-path stub titles, pandas-style card landing — see the IA
    re-cut in `docs/_dev/api-reference-restructure.md`).
  - `show_nav_level: 1` (collapsed by default). Do NOT promote sub-groups to top-level
    (pydata navbar overflows ~6+). The old "Reference page pattern" is SUPERSEDED by the
    API Reference & Guide pattern below.
- **Title casing + how-to naming** (2026-06-15) — TWO-TIER casing, applied
  consistently: **page titles (H1) and card/sidenav titles are Title Case**
  (`Building Forms`, `Images and Icons` — conjunctions like `and` stay lowercase);
  **in-page section headers are sentence case** (`Backing a widget with a data
  source`). **How-to (`/tasks/*`) titles are action-driven gerunds** —
  `‹Gerund› ‹object›` (`Displaying Data`, `Using the Clipboard`, `Showing Dialogs`),
  NOT topical nouns. **Feature guides (`/reference/*`) keep noun/subsystem titles**
  (`Events`, `Data Sources`) — that's correct, not a violation. Keep titles short enough to not
  wrap in the sidenav (~≤20 chars; drop articles: `Setting App Icons`, not `Setting an
  Application Icon`). **A page's H1, its User-Guide card title, and its sidenav entry
  must all match** (the sidenav shows the H1, so a card/H1 mismatch shows as drift).
  How-to card grid + the hidden toctree are ordered by **learning progression** (build
  a screen → compose → app structure → ship), and both must stay in the SAME order.
- **No Tkinter in docs or docstrings** — no `tk.*` types/terms unless strictly
  necessary; don't feature the escape hatch. Full `src/` docstring scrub still
  pending. LEFT BY DESIGN: `.tk`/`.var` escape-hatch property docstrings,
  `signals/integration.py` (the Tk bridge).
- **Event / theming / DataSource APIs are DONE** — reflected in the Architecture +
  Gotchas sections below and in memories `project_typed_events`,
  `project_theming_public_api`, `project_datasource_api_naming`,
  `project_datasource_change_events`. Deferred-only: the visual theme builder
  (Phase 5, near-ship — emits `bs.Theme(...)` code; do NOT build yet).

### API/cleanup backlog (deferred, memory-tracked)

- `project_capabilities_relevance` — `_core/capabilities` may be redundant now the
  public layer abstracts Tk; still imported by data/i18n/mixins.
- `project_docstring_backticks` — **DONE (PR #182):** swept to single backticks
  (`default_role="code"` makes them render as inline code). Convention is Google +
  SINGLE backticks; RST cross-ref roles (`:class:`/`:doc:`/`:ref:`) are kept (deliberate).
- `project_event_naming_revisit` — past-tense event names pending rename:
  `SideNav.on_pane_toggled`/`on_display_mode_changed`, `ListView.on_selection_changed`,
  `Calendar.on_date_selected`.
- ~~`project_signal_subscribe_subscription`~~ — **DONE (#157)**: `Signal.subscribe()`
  now returns a cancelable `streams.Handle` (was a `str` token), unifying with
  events/streams.
- `project_editfilter_public_api` — `EditFilter` DEMOTED (Tk-coupled raw text
  indices/tags); investigate a de-Tkinter-ed CodeEditor extension API before any
  re-promotion. `NOTE(editfilter-public-api)` in
  `widgets/_impl/composites/textarea/filter.py`.
- `project_window_api_hardening` — `bs.Window` leaks uncurated `**kwargs` to the
  internal Toplevel (raw Tk options in; useful `icon`/`alpha`/`toolwindow`/
  `window_style` only via the escape hatch), has no live properties
  (`title`/`size`/`topmost` are construction-only), and never releases the modal
  grab. Curate to typed params + add a live `title` + release on close. Own branch.
- `project_show_indicator_removal` — **KEEP (reversed 2026-06-15).** `show_indicator=`
  was briefly flagged for removal but is being kept: the `show_indicator=False` +
  `on_icon`/`off_icon` combo is exactly what makes an icon-driven custom checkbox, and
  removing it would orphan that. GitHub #144 closed won't-do. Do NOT re-propose removal.
- `project_enum_option_typing` — promote recurring enumerated `str` kwargs to NAMED
  `Literal` aliases in `widgets/types.py` (re-exported from `bootstack.types`); the
  ALIAS docstring carries the value list once, widget docstrings describe meaning only
  (no value enumeration — REVERSES the Code-standards "valid values per kwarg" rule for
  aliased types; keep the default). First fixes: `accent: str`→`AccentToken` in
  `form.py`/`menubar.py`. New aliases: `SelectionMode`/`IconPosition`/`LayoutKind`/
  `AutoFlow`/`ExportScope`; reuse existing `Orient`/`Fill`/`Anchor`/`Sticky`. Own branch.
- Lower-priority: bare index/landing pages (root, `widgets/`, `reference/`);
  localization/windowing `tasks/` how-tos; screenshots pending (Tooltip/Toast, 7
  Dialog pages); AppShell deferred improvements (`nav_pane_width=` not wired to
  `SideNav(pane_width=)`, hardcoded nav density/font, group active-child highlight +
  indentation, footer non-page widgets).

---

## API Reference & Guide page pattern (established — follow exactly)

The docs are a **Diátaxis-style split** (PR #107): a narrative layer (**Widgets** +
**Guides**) plus a **unified, complete API Reference** that mirrors each submodule's
`__all__`. **Load-bearing rule: every object has exactly ONE autodoc home, and it
lives in the API Reference.** Narrative pages cross-link in (`:class:` / `:func:` /
`:meth:`) and may carry a *table-only* `autosummary` summary; they never re-document.
A second autodoc home reintroduces the "duplicate object description" warnings PR #106
removed. Full brief + all staged-sweep decisions: `docs/_dev/api-reference-restructure.md`.
Memory `project_api_reference_restructure`.

### The autosummary templates (locked, PR #107 + Stage 2)

THREE custom templates under `docs/_templates/autosummary/`, one per documenter
kind autosummary uses for the data surface — `class.rst`, `function.rst`,
`data.rst`. **All THREE must title the stub page with the bare `{{ objname }}`**
(not `{{ fullname }}`). This is load-bearing: autosummary picks the template by
object kind, and the **stub's title is what the sidebar shows**. The built-in
fallback templates title with the full dotted path (`bootstack.data.col`), so
relying on the fallback for functions/data produces a sidebar where classes read
bare (`MemoryDataSource`) but functions/aliases read fully-qualified
(`bootstack.data.col`) — the exact inconsistency Stage 2 fixed. Keep the bare-title
line identical across all three.

`class.rst` (also serves dataclasses + Protocols):

```rst
{{ objname | escape | underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :members:
   :inherited-members:
   :show-inheritance:
```

`function.rst` → `.. autofunction:: {{ objname }}`; `data.rst` →
`.. autodata:: {{ objname }}` — each with the same bare-title + `currentmodule`
header.

- `:inherited-members:` (class template) is what makes a concrete-source stub
  **complete** (e.g. `SqliteDataSource` shows inherited
  `save`/`on_change`/`observe`/`export_csv`).
- The Protocol page stays noise-free because `undoc-members` is off and there is no
  `:special-members:` — `_private`/dunder/Generic members are filtered out.
- Some type aliases classify as class-like and pick up `class.rst` (e.g.
  `Primitive`), others as data and pick up `data.rst` (e.g. `Record`) — both now
  title bare, so it no longer matters which. A new documenter kind a future module
  needs (e.g. `exception.rst`) must get the SAME bare-title treatment.
- **Per-class curation** (a class needing different members than the global
  `class.rst`): add a per-class template file `_templates/autosummary/<name>.rst`
  and point that class's `autosummary` entry at it with `:template: <name>` —
  **WITHOUT the `.rst` extension**. Sphinx's autosummary resolves `:template: X`
  as `autosummary/X.rst`; passing `signal.rst` builds `autosummary/signal.rst.rst`,
  silently misses, and falls back to the built-in `base.rst` (full title, no
  members) — NOT even `class.rst`. `:template:` applies to every name in that
  directive block, so put the curated class in its own one-name block. Exemplar:
  `signal.rst` (Signal needs `__call__` shown + `tk`/`var`/`name`/`from_variable`
  excluded); wired in `api-reference/signals.rst` as `:template: signal`.

### API Reference page recipe (the autodoc home — one per submodule)

A page like `docs/api-reference/data.rst`. Text-only, **NO screenshots, NO hero**.

1. Title = the dotted module path (`bootstack.data`), then `.. currentmodule::` it.
2. One prose paragraph orienting the module + a `:doc:` link to its Guide.
3. **Group the surface into labeled sections** (`---` headings), each: a one-sentence
   prose lead-in, then an `.. autosummary::` table with `:toctree: generated` and
   `:nosignatures:`. The table renders as a two-column **name | first-line-summary**
   table (pandas/SciPy style) and toctrees each name into an auto-generated per-object
   stub under `docs/api-reference/generated/` (gitignored — regenerates at build).
   **Grouping conventions** (from the batch-1 review, applied across all pages):
   (a) **Don't mix kinds in one list** — separate the things you *call*
   (functions/constructors) from the *supporting types* they produce/consume, from
   *enumerations/aliases*. E.g. `events` = payload sections + "Supporting types"
   (`TabRef`, a value carried *inside* a payload) + "Enumerations" (`ChangeReason`…);
   `data` = "Query language" (`col`/`any_of`/`all_of`) vs "Query expression types"
   (`Column`/`Condition`/`SortKey`) vs "Type aliases" (`Record`/`Primitive`). A type
   that only appears *inside* another object (not handed to the user directly) is a
   supporting type, not a primary entry. (b) **Order sections most-reached-for first,
   lowest-level lookups last** — primary objects → common callables → their supporting
   types → feature areas → bare type aliases at the bottom (`data` order: Data sources
   → Query language → Query expression types → Readers and writers → Type aliases).
   (c) **Don't sub-section a small/uniform module** — follow the
   `bootstack.streams` model (intro prose + ONE `autosummary` table, no `---`
   sub-headings) whenever a module is just a few names of the same kind. Sub-section
   only when the surface is large OR genuinely mixes kinds (a). `streams`
   (`Stream`/`Handle`), `validation` (`ValidationRule`/`ValidationResult`),
   `scheduling` (`Schedule`/`Job`), `shortcuts` (3), and `errors` (5 exceptions) are
   all single-table; `data`/`events`/`style` earn their groups. The intro carries
   any rule-vs-result / base-vs-specific nuance — don't spend a heading on it.
   (d) **Order ENTRIES within a group ALPHABETICALLY** — the API Reference is the
   lookup layer, so within-group order should be predictable for scanning (the
   pandas/NumPy convention), NOT curated/common-first. Curated common-first order
   is the GUIDES' job (the `widgets/index.rst` caption toctrees keep it). The
   category grouping + a one-line lead-in already carry the semantics; clusters
   mostly stay adjacent alphabetically anyway (`Radio`/`RadioGroup`/`RadioToggleButton`,
   `Select`/`SelectButton`, `ToggleButton`/`ToggleGroup`). (e) The audit also
   surfaces half-public names to demote — e.g. `TraceOperation` (internal trace
   tag, no public signature exposes it) was dropped from `bootstack.signals.__all__`
   during this sweep.
4. List **exactly** the module's `__all__` across the grouped tables (the reference
   IS `__all__`). Good first-line docstrings matter — that line is the summary cell.
5. Wire the page into `docs/api-reference/index.rst`'s toctree.

Re-exported names (shallowest path wins): a name exported at two public paths gets
ONE stub, on the **shallowest** page (`Signal` → top-level `bootstack` page). Deeper
module pages list it in a **table-only** summary (no `:toctree:`, links up to the
stub) and own only their module-local names.

### Guide page recipe (the former `reference/*` prose pages)

A page like `docs/reference/data-sources.rst`. This is the teaching layer.
**Guiding principle: the API Reference is a LAST RESORT — the Guide carries the
practical teaching load** (generous worked examples, common compositions, recipes,
do/don't). A user should build real things from the Guide alone.

1. Prose intro → task-ordered usage sections (code blocks) → See also.
2. **No bottom `autoclass`** — instead end with an **"API reference"** section: a
   one-line pointer (`:doc:` link to the API Reference page) + an at-a-glance
   `.. autosummary::` table **WITHOUT `:toctree:`** (a table is NOT an object
   description, so it's not a second autodoc home; its links resolve to the stubs).
3. Cross-link types inline with roles (`:class:` / `:func:` / `:meth:` / `:data:`)
   at the **public home path** (`bootstack.data.SqliteDataSource`, not the impl path).
4. Inline usage only — NO separate Full Example file. Non-visual: NO screenshots.

### Verify (every stage)

Clean-build, always — incremental builds MASK warnings:
`rm -rf docs/_build && sphinx-build -b html docs docs/_build/html -W --keep-going`.
Build is warning-free; keep it there. Attribute-docstring rules (PR #106) still
apply (no `Attributes:`/`Args:` for dataclass fields; no colon on the first line of
an attribute docstring). A `-n` nitpicky build surfaces dangling cross-refs once a
home moves — fix the link or add a `nitpick_ignore_regex`.

---

## Reviewing a widget + docs standards (read first)

**Before any widget review or widget-docs work, read
`docs/_dev/widget-review-and-docs-standards.md`** — the consolidated checklist.
It is the single source of truth for both halves; the highlights:

- **A review is audit → fix → test → document → file follow-ups**, not a
  read-through. Audit the public wrapper vs `_impl` for correctness bugs AND
  unexposed capability. Recurring bug classes: value clamping (setters + re-clamp
  on range change), disabled state honored on *every* input path (incl. Home/End),
  event consistency (keyboard jumps commit like a drag-release), no Tab focus-trap.
  Then API hygiene (typed params, `on_*` payload audit, drop dead kwargs,
  live-vs-construction props). **File additive features / out-of-scope bugs as
  tracked issues — don't scope-creep the review branch.**
- **Docs: the Guide teaches; the API Reference is a last resort.** **Lead with the
  mental model** (foundational concept up front, not buried later). **No
  kitchen-sink — one idea per paragraph, scannable**, teach the decisions not every
  kwarg. Examples are **tight, API-verified, with the relevant import on first
  use** (and they must run). Use a `.. note::` for an **adjacent-but-distinct topic**
  (placed by the relevant screenshot, linking the other section) rather than inline
  prose — keep each topic its own section/TOC entry. Document the **Events** (change
  vs commit — public, not an impl detail) and **Keyboard** behavior of interactive
  widgets. **One screenshot per visually-distinct usage section**, not just the hero;
  a behavioral-only feature (e.g. step snapping) gets prose, no screenshot.
  Sentence-case section headers; Title Case page title.
- Verify: GUI test files run **one per process** (#150); `tests/test_public_surface.py`
  green; examples run; clean `-W` docs build; held for user test + per-commit approval.

## Widget documentation pattern (established — follow exactly)

> ⚠ **Migrating a widget = also clean up its public API** (the maintainer's
> standing pattern, memory `feedback_cleanup_api_while_documenting`). When you home
> a widget into the API Reference, audit it the way `App`/`AppShell`/`Window` were:
> drop dead/redundant kwargs, demote set-once config from runtime properties to
> construction-only (a property is "live" only if changing it has a complete effect
> a user would bind to a control), de-Tkinter leaks, fix docstring nits.
> **In particular, complete the typed-payload `on_*` audit for that widget** (memory
> `project_typed_event_payloads`, INCOMPLETE): a DATA event gets its specific
> `bootstack.events` payload type in `@overload` + impl signature; a NATIVE event
> (`click`/`hover`/`focus`/`blur`/`resize`) keeps `Event`. Known offenders: the
> boolean/selection controls (`Checkbox` etc.) still type `on_change`/`on_check`/…
> as generic `Callable[[Event]]`. (Payloads render in the autodoc "Overloads:"
> block, so fixing the source is enough.)

1. **Audit** — Explore agent comparing public wrapper vs `_impl/` internals.
2. **Fix wrapper** — typed params (`AccentToken`, the widget's own per-widget
   `variant` Literal, `WidgetDensity`);
   `@overload` event shorthands; no low-level color kwargs; layout via `**kwargs`
   + `_split_layout_kwargs`; catch-all must be `**kwargs` not `**extra_kw`.
3. **`docs/widgets/<widget>.rst`** (NOTE: was `docs/api/` — moved 2026-06-04) —
   intro sentence → hero screenshot → Usage sections (code block then screenshot)
   → Widget sizing include → See also → table-only `autosummary` API section +
   cross-links (NO bottom `autoclass`, per the Guide-page recipe) → Full Example
   literalinclude. No intro code block above hero.
4. **`docs/examples/<widget>.py`** — runnable visual-states-only demo. No
   `app.tk.after()`, no screenshot scaffolding, no `fill="x"` in RST snippets.
5. **`docs/screenshots/<widget>.py`** — SCENES dict. Each scene: own `bs.App`,
   tight `size=(W,H)`, `HStack(fill="x")` for button rows to avoid centering
   offset, `app.run()`. Hero for button/action widgets: single representative
   state with menu/popdown open if applicable.
6. **Screenshots:** `py -3.12 docs/scripts/take_screenshots.py <widget> [--scene X] [--light]`
   Outputs: `docs/_static/examples/<widget>-<scene>-light/dark.png`
7. **Wire** into the matching `:caption:` toctree in `docs/widgets/index.rst`
   (category landing pages are retired — captions group the widgets now).
8. **Commit** on a dedicated `feat/*`/`docs/*` branch.

### Screenshot image pattern

```rst
.. image:: /_static/examples/<widget>-<scene>-light.png
   :class: bs-screenshot-light
   :alt: <Widget> <scene> — light theme

.. image:: /_static/examples/<widget>-<scene>-dark.png
   :class: bs-screenshot-dark
   :alt: <Widget> <scene> — dark theme
```

Hero uses `-hero-light/dark.png`. Dialogs add `bs-dialog-screenshot` to the class
(e.g. `:class: bs-screenshot-light bs-dialog-screenshot`).
Margin/radius owned by `docs/_static/custom.css` — no inline styles.

### Widget sizing section pattern

```rst
Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst
```

Path is file-relative from `docs/api/`. Omit from dialog pages.

---

## Gotchas

### Layout and wrappers
- **Self-placement via `**kwargs`** — `fill`, `expand`, `anchor`, `row`, `column` etc.
  are NOT explicit params. Route through `self._split_layout_kwargs(kwargs)`.
- **`**kwargs` not `**extra_kw`** — catch-all must be named `**kwargs` throughout.
- **User options MERGE OVER framework kwargs; structural keys RAISE** (#363,
  0.1.6). A widget that builds another widget for you — `Form`'s `editor_options`,
  `MenuButton`'s `menu_options`, the `**kwargs` passthrough on `ButtonGroup.add` /
  `RadioGroup.add` / `Toolbar.add_widget` — must route through
  **`merge_kwargs`** (`widgets/_core/kwargs.py`): the caller's options win, and a
  short `reserved` map (keys the widget must own — its `parent`, the command that
  emits its events) raises `BootstackError` naming the API called and what to use
  instead. Splatting a user dict alongside explicit kwargs raises
  `TypeError: got multiple values for keyword argument` from an internal class the
  caller never wrote — that was a live bug in six widgets. **Legacy exception:**
  `MenuButton.__init__`'s `_RESERVED_INTERNAL_KEYS` still SILENTLY SKIPS collisions
  (so `bs.MenuButton("X", command=fn)` quietly does nothing). Flipping a silent
  no-op to a raise can break working user code, so converging it is a 0.2.0 item —
  do NOT copy the silent-skip pattern into new code.
- **`margin_x=` / `margin_y=`** — axis-specific external spacing. Never `padx=`/`pady=`.
- **`.. include::` path is file-relative** — from `docs/api/`, use `../shared/widget-sizing.rst`.

### Screenshots
- **HStack centering** — App's VStack centers children. For button-row scenes, wrap in
  `HStack(fill="x")` so buttons are left-aligned, not centered with dead space on the left.
- **No `size=` by default** — omit `size=` from `bs.App` in screenshot scenes unless there
  is a specific reason (popdown/dropdown needs room to render inside the capture bbox). Let
  the window auto-fit its content. For input/field/slider rows use `minsize=(720, 1)` to
  enforce a minimum width without locking height. Never add `size=` just to "feel right".
- **Popdown menus in screenshots** — runner sets app `topmost=True` at t=800ms, grabs at
  t=950ms. Call `mb.show_menu()` at t=850ms (after topmost set, before grab). Size the
  app window tall enough to contain the menu within its capture bbox — the menu Toplevel
  is captured via `ImageGrab.grab(bbox=app_region)` which is a screen grab, not a window
  grab.
- **`_ToplevelContextMenu` topmost** — `show()` now sets `-topmost True` on the
  overrideredirect Toplevel so it appears above a parent with `-topmost True`.
- **SelectBox popup topmost** — `_create_popup_toplevel` sets `-topmost True` so the
  popup appears above the screenshot runner's topmost window.
- **Screenshot runner 2px inset** — crops 2px from each edge to remove Windows border artifact.
- **Dialog hero pattern** — open non-modally at t=200ms, lift dialog at t=850ms, screenshot
  at t=950ms. Use `app._capture_target = <toplevel>` to capture a dialog instead of the app.
- **Full-app widget sizing** — PageStack, SideNav, AppShell use `fill="both", expand=True`
  and need `size=(W, H)` (not `minsize=`) to give the canvas a defined size.
- **Navigation window padding** — use `padding=8` on the App for full-app nav scenes to
  give footer-pinned items breathing room at the bottom edge.
- **Tabs vertical scene** — use `padding=16` and `size=(W, H)` since `fill="both"` needs
  a canvas; `minsize=` is sufficient for horizontal tabs scenes.

### MenuButton specifics
- **`icon_only` inferred** — `DropdownButton.__init__` auto-sets `icon_only=True` in
  `style_options` when `icon` is in style_options and `text` is None/empty. The public
  wrapper doesn't need to infer it.
- **Menubutton layout centering** — `Menubutton.label` has `side="left"` in the ttk
  layout. When `icon_only=True` and no dropdown, drop `side="left"` so the label fills
  the full content area and `anchor="center"` can take effect.
- **Item type names** — public API uses `'command'`, `'check'`, `'radio'`, `'separator'`.
  Internal ContextMenu uses `'checkbutton'` / `'radiobutton'`. Translate at the wrapper
  boundary via `_ITEM_TYPE_MAP`. Legacy names accepted for backwards compat.
- **Radio group variable** — `add_radio_item()` auto-creates a shared `StringVar` on the
  internal widget. Values are stored as strings internally. Use `selected=True` to
  pre-select. Multiple `add_radio_item()` calls share one group variable per MenuButton.
- **`show_menu()` respects disabled state** — guard with
  `self._internal.instate(("!disabled", "!readonly"))` before delegating.
- **`disabled` property** — use `instate(("disabled",))`, not string comparison on `cget`.
- **`shortcut=` in `add_item()`** — display-only label. Passes through `format_shortcut()`
  which handles: registered key name → platform display, `"Mod+S"` pattern → `"Ctrl+S"` /
  `"⌘S"` (no registration required), literal string → pass-through.
- **MenuButton hero pattern** — show a standalone "Actions" button (Edit/Duplicate/Archive/
  Delete), NOT a File/Edit/View menubar pattern. Shortcuts section uses the File menu example.

### Style rebuild pattern
- **`configure_style_options` alone doesn't rebuild** — it only updates the stored
  `_style_options` dict. Call `rebuild_style()` immediately after to regenerate the TTK
  style with the new options and apply it to the widget.
- **`emit` wraps `event_generate`** — `PublicWidgetBase.emit(event, data=...)` calls
  `self._internal.event_generate(sequence, data=data)` directly. For internal widgets
  use `event_generate` with `data=` natively (the event system is patched to support it).

### Widgets and API
- **Public namespace is CURATED (PR #104)** — top-level `bootstack` (`bs.*`) holds
  ONLY what you compose a UI from: every widget, `App`/`AppShell`/`Window`,
  `Signal`, the dialog VERBS (`alert`/`confirm`/`ask_*`/`toast`), and
  `set_theme`/`toggle_theme`. Import everything else from its submodule —
  `from bootstack.data import SqliteDataSource, col`; `from bootstack.style import
  Theme, get_theme_color`; `from bootstack.i18n import L, LV`;
  `from bootstack.validation import ValidationRule`; `from bootstack.events import
  Event, Subscription`; `from bootstack.streams import Stream`;
  `from bootstack.scheduling import Schedule`; `from bootstack.shortcuts import
  get_shortcuts`; `from bootstack.store import Store`; `from bootstack.errors
  import ...`; `from bootstack.types import AccentToken`; dialog CLASSES
  `from bootstack.dialogs import FormDialog`. `MessageCatalog`/`IntlFormatter`/
  `get_current_app`/`Image` are INTERNAL (not public). Do NOT write `bs.Theme`/
  `bs.col`/`bs.SqliteDataSource`/`bs.FormDialog` etc. — they no longer exist at
  top level. Map: the `docs/api-reference/index.rst` landing (public-contract +
  submodule list; `api-overview` was retired into it); guard:
  `tests/test_public_surface.py`. Memory `project_toplevel_api_surface`.
- **Dialogs live in `bootstack.dialogs`** — impl under `bootstack/dialogs/_impl/`,
  public façade `bootstack/dialogs/__init__.py` (verbs + classes).
  `bootstack.widgets.dialogs` is GONE. Internal deep imports use
  `bootstack.dialogs._impl.<module>`.
- **`disabled` on Label** — not appropriate. Label is display-only.
- **`color=` / `background_color=`** — removed. Use `accent=` / `surface=`.
- **`bs.App` / `bs.AppShell` config is FLAT kwargs** (settings-flattening, branch
  `feat/app-settings-flatten`). All former `AppSettings` fields are direct
  constructor kwargs — `theme`, `light_theme`, `dark_theme`,
  `follow_system_appearance`, `available_themes`, `inherit_surface_color`,
  `locale`, `localize_mode`, `window_style`, `macos_quit_behavior`,
  `remember_window_state`, `state_path`, `app_author`, `app_version`. There is
  **NO public `settings=` / `AppSettings` / `app.settings`** (clean break, no
  shim — passing `settings=` raises `TypeError`). `AppSettings` survives only as
  an internal resolved-config holder; `get_app_settings()` is internal-only.
  Read/write config as symmetric `app.*` properties: `app.theme`/`app.locale`/
  `app.title` set live; locale-derived values are flat read-only props
  (`app.locale_date_format`, `app.locale_time_format`, `app.locale_decimal`,
  `app.locale_thousands`, `app.locale_language`). Config-change events:
  `app.on_theme_change(fn)` (→ theme name) and `app.on_locale_change(fn)`
  (→ locale code). Persistence: `bs.App.from_store(store)` (tolerant of version
  skew — filters to known kwargs) + `store.update(theme=...)` write-back. Shared
  impl in `widgets/_core/app_config.py` (`AppConfigMixin`, `APP_CONFIG_KWARGS`).
- **`bs.Signal()` is safe at module level** — the backing Tk var is created lazily on first widget binding.
- **`textsignal=`** — standard kwarg for text-bearing widgets. `signal=` for non-text
  (Slider, Checkbox, etc.). Never expose `textvariable=` / `variable=` publicly.
- **`TTKWrapperBase.__init__` overwrites `self._accent`** — store accent before `super().__init__()`,
  re-assign after.
- **`<<BsThemeChanged>>`** fires after full rebuild (use this). `<<ThemeChanged>>` fires before.
- **Canvas/imperatively-painted widgets — theme repaint:** NEVER bind ttk
  `<<ThemeChanged>>` on the **root/toplevel** — it re-fires **~1400× per rebuild**
  (once per style reconfigure); root-bound × instances = thousands of redraws (was
  the gallery's ~3s toggle lag, PR #180). Re-resolve colors via the **STD
  `Publisher`** (fires once, after rebuild) and **gate the redraw on visibility**.
  `Frame` subclasses: call `self._enable_theme_repaint(self._redraw)` (the shared
  hook — subscribes, gates on `winfo_viewable()`, defers off-screen to `<Map>`,
  releases on `<Destroy>`). Non-`Frame` (Slider/RangeSlider/chrome): publisher +
  own gate. Memory `reference_theme_repaint_mechanisms`. **#177 DONE (PR #181):**
  textarea/code-editor (`StyleRegistry`/`SearchOverlay`/`IndentGuides`) migrated onto
  `<<BsThemeChanged>>`; dead `FloodGauge` deleted. Nothing left on the racy event.
- **`bs.SelectButton`** — button-styled non-editable picker. Distinct from `bs.MenuButton`
  (action menu) and `bs.Select` (editable combobox).
- **`bs.DataTable`** (renamed from `bs.Table`) — works with any
  `DataSourceProtocol` source (decoupled from `SqliteDataSource`); identity reads
  route through `_record_id`/`_public_record`/`_internal_fields`. Defaults to an
  in-memory `SqliteDataSource` when given `rows=`. No built-in border (wrap in a
  `Card`/`Frame`); `density=` and a footer separator are supported.
- **`RadioGroup.set()` validates against keys**, not values.
- **`bs.Form` uses `col_count=`**, not `columns=`.
- **`ToggleGroup(padding=N)`** — bug fixed; safe to pass.
- **`value=` ignored when `signal=` also passed** on boolean widgets — seed the Signal directly.

### Boolean controls
- **Switch/ToggleButton unsupported features** — Switch: no `on_icon`/`off_icon`/`icon_only`/
  `show_indicator`/`tristate`/`density`. ToggleButton: no `tristate`/`show_indicator`.
  Checkbox: only widget supporting `tristate`.
- **Density** — Checkbox and Switch do NOT support `density=`. ToggleButton DOES.
- **Sphinx signatures** — give each subclass its own `__init__` to avoid inheriting
  unsupported params. Use `:inherited-members: PublicWidgetBase` in autoclass.

### Layout widgets
- **`height=`/`width=` on VStack/HStack** — setting one collapses the other axis.
  Add `fill=` + `expand=True` for the unconstrained axis.
- **`show_border=True` needs padding** — border is inside the frame edge.
- **`Grid columns=N` shorthand** — `columns=3` ≡ `[1,1,1]`. `0` == `'auto'`.
- **`**extra_kw` removed from layout wrappers** — `Card`, `GroupBox`, `VStack`,
  `HStack`, `Grid` only accept `**kwargs`.
- **`variant=` removed from VStack/HStack** — use `bs.Card` for card-variant layout.

### Dialogs
- **7 doc pages** — `dialogs.rst` is toctree-only. `ColorDropperDialog` is internal.
- **`content_builder`** fills a PUBLIC content `Column` set as the active parent —
  write the body parent-free (`def build(): bs.Label(...)`), like an App body;
  `Dialog(padding=, gap=)` configures it. `def build(content)` gets an explicit
  handle; old `def build(frame): with bs.Column(parent=frame)` still works (frame
  is the public Column, via the `_RawTkContainer` bridge in `_resolve_parent`).
  bootstack's own verb/Form dialogs render raw and opt out with `_raw_content=True`.
- **`Frame.configure(surface=...)`** does NOT work at runtime — use `configure_style_options(surface=...)`.
- **`Dialog.__init__`** is fully keyword-only; `parent=` not `master=`; `min_size=`/`max_size=`.
- **`ButtonRole`** values: `"primary"`, `"secondary"`, `"danger"`, `"cancel"`.
- **`bs-dialog-screenshot` CSS class** — dialog screenshots only; adds border + drop shadow.

### Sliders / fields
- **Slider/RangeSlider spacing** — `VStack gap=` does not visually separate tracks.
  Use `margin_y=10` on each widget. Track heights: plain ≈ 24px, ticks ≈ 45px, badge+ticks ≈ 65px.
- **Screenshot widths** — use `minsize=(720, 1)` for all input/field/slider scenes.
- **`anchor_items="baseline"`** — invalid. Use `"s"`.
- **`select.py` / `calendar.py` shadow stdlib** — use `selectfield.py` and `calendarwidget.py`.

### Misc
- **American English** — all docstrings and user-facing text. Spelling scrub still pending.
- **`font="heading-md"`** not `"heading-md[bold]"` — headings already bold.
- **`&` in `bs.Label` text** — Tkinter strips `&`. Use `"and"`.
- **`Expander` is internal** — use `bs.Accordion`.
- **Run examples after editing** — always `python docs/examples/<widget>.py` before committing.
- **Dark mode Note admonition** — override in `custom.css` inside `html[data-theme="dark"]`:
  `--pst-color-info: #6ea8fe; --pst-color-info-bg: #0d306e`.
- **`Shortcuts` service** — public surface is `bootstack.shortcuts`: the `Shortcuts`
  class, the `Shortcut` dataclass, and the `get_shortcuts()` accessor.
  `register(key, "Mod+S", fn)` + `bind_to(app)` wires the keyboard handler.
  `format_shortcut(spec)` (in `_runtime/shortcuts.py`) resolves display text only
  (no binding side effect) — it is INTERNAL, not exported from `bootstack.shortcuts`.

---

## Architecture (settled)

**Public API** is a composition layer over internal widgets. Public widgets are plain Python
objects (NOT `tk.Widget` subclasses) holding `self._internal`.

Constructor order: resolve parent → split layout kwargs → construct internal → attach to parent.
`_split_layout_kwargs` strips pack/grid/place keys before internal widget construction.

`.tk` property returns the underlying ttk widget — escape hatch, user's responsibility.

### Context-manager parenting

```python
with bs.App(title="Demo", padding=16, gap=8) as app:
    with bs.HStack(gap=4):
        bs.Label("Hello")
        bs.Button("OK", on_click=lambda: ...)
app.run()
```

`__enter__` pushes container, `__exit__` pops. App hides on enter, shows on exit.

### Events  (redesigned 2026-06-05 — see memory `project_typed_events`)

```python
sub = widget.on_change(handler)   # → Subscription (cancellable)
widget.on_change().debounce(300).listen(handler)  # → Stream (composable)
```

All `on_*()` shorthands use `@overload`: no-arg → `Stream`, with handler → `Subscription`.

**What the handler receives** (the redesign):
- **Data events** (`change`, `input`, `select`, validation, …) → the typed
  payload dataclass, **unpacked**: `on_change(lambda e: e.value)`. Payloads live
  in `bootstack.events` (the catalog) — `from bootstack.events import ChangeEvent`,
  `SliderEvent`, etc. Namespaced there ONLY, not top-level. ⚠ **Write the submodule
  import, NOT `bs.events.ChangeEvent`** — `events` is absent from `bootstack.__all__`,
  and `bs.events` resolves only because widget code imports the submodule
  transitively. This line used to teach the `bs.events.X` spelling: it was written
  2026-06-05, three days before `637b2407` (`refactor(api)!: scope framework
  primitives into submodules`, the PR #104 curation) made it stale, and it then
  seeded the same spelling into `docs/reference/events.rst` and
  `PublicWidgetBase.emit`'s docstring (both fixed on PR #414). ⚠ **`tests/test_public_surface.py`
  does NOT guard this** — it gates the curated top-level *name set* and that each
  moved symbol is importable from its submodule; it never asserts a submodule is
  unreachable as a `bs.*` attribute, which is why the drift went uncaught for two
  months. ListView item events are the exception: a plain record `dict`
  (`e["field"]`).
- **Native events** (`click`, `hover`, `focus`, `blur`, `resize`, key, scroll) →
  a curated, Tk-free `Event`: `widget`, `x/y/x_root/y_root`, `width/height`,
  `delta`, modifier bools `ctrl/shift/alt/meta`, clean `key/char`, `time`.
- `Button`/`Label` `on_click()` METHOD now passes the `Event` (the no-arg
  `on_click=` constructor command is unchanged).
- The generic `on(name, handler)` is typed `Callable[[Any], Any]` (string-keyed,
  can't infer the payload); the precise types are on the `on_<event>()` shorthands.
- Transform happens in `adapt_handler()` (`widgets/_core/base.py`); emit sites
  build the dataclass: `event_generate("<<Change>>", data=ChangeEvent(...))`.
  `_runtime/events.py` (the data-cache transport) is untouched.

### Signals

```python
sig = bs.Signal(value)
bs.TextField(textsignal=sig)   # two-way binding
sig.subscribe(lambda v: ...)
```

### Layout

⚠ **This file's layout examples were STALE and are only partly swept — verify
against a real signature before copying any of them.** Measured 2026-07-30 via
`inspect.signature`:

- **`bs.HStack` / `bs.VStack` DO NOT EXIST** — the stacks are **`bs.Row`** and
  **`bs.Column`**. Every `HStack`/`VStack` still left in this file (the screenshot
  patterns around the "HStack centering" gotcha, the layout-widget gotchas, the
  context-manager example) is wrong. **Not yet swept** — do it opportunistically,
  checking each replacement, rather than in one blind find-and-replace.
- **`fill=` / `expand=` on a flex child now RAISE**, they don't degrade:
  `BootstackError: fill is not a valid layout option for a Row/Column/Grid child.
  Use grow= / align_self= (and justify_self= in a Grid) instead`. ⚠ **THAT ERROR
  IS ITSELF WRONG, and this file used to call it a "good error — trust it over
  this file". Do not.** It names three kwargs and only `grow=` exists; following
  its advice verbatim produces a raw `TclError: unknown option "-align_self"`.
  **The real per-child keys are `horizontal=` and `vertical=`.** Measured
  2026-08-11: `bs.Picture(align_self="stretch")` raises, `horizontal="stretch"`
  and `grow=1` both construct. Tracked as **#426**, milestoned `0.3.1` — fix the
  message and this bullet together.
- **Container defaults are `horizontal_items=` / `vertical_items=` /
  `grow_items=` / `weights=`.** `fill_items=`, `expand_items=`, `anchor_items=`
  and `sticky_items=` are all GONE from `Row`/`Column`/`Grid`.

```python
bs.Column(padding=20, gap=12)
bs.Row(gap=8, vertical_items="center")
bs.Grid(columns=["auto", 1], gap=8)
```

Full current signatures — `Row`/`Column`: `parent`, `horizontal_items`,
`vertical_items`, `grow_items`, `weights`, `gap`, `padding`, `surface`,
`show_border`, `width`, `height`, `**kwargs`. `Grid` swaps `grow_items`/`weights`
for `columns`, `rows`, `auto_flow`.

---

## Source structure

```
src/bootstack/
├── _core/       infrastructure (capabilities, colorutils, mixins, publisher, images)
├── _runtime/    Tk patches (app, toplevel, menu, shortcuts, events)
├── assets/      locales, icons (themes are now Python, see style/themes/)
├── data/        DataSource (Base, Memory, Sqlite, File)
├── dialogs/     dialog implementations
├── signals/     Signal, TraceOperation
├── style/       Theme (public), themes/ (built-in Theme instances),
│                Style/Typography/Font (internal engine), builders
├── validation/  ValidationRule, ValidationResult
└── widgets/
    ├── _core/   public framework internals (base, container, context, events)
    ├── _impl/   internal implementation (primitives, composites, mixins)
    ├── app.py, button.py, ...  (~40 public wrapper files)
    └── types.py AccentToken, WidgetDensity, SurfaceToken, per-widget variant Literals, etc.
```

---

## Key API reference

```python
import bootstack as bs

with bs.App(title="My App", size=(800,600), padding=16, gap=8) as app:
    sig = bs.Signal("World")
    bs.Label("Hello!", font="heading-lg")
    bs.Button("OK", accent="primary", on_click=lambda: ...)
app.run()

# AppShell
with bs.AppShell(title="My App", theme="bootstrap-light") as shell:
    shell.commandbar.add_button(icon="sun", command=bs.toggle_theme)
    with shell.menubar.add_menu("File") as file:
        file.add_action("Quit", shortcut="Mod+Q", on_click=shell.close)
    with shell.add_page("home", text="Home", icon="house"):
        bs.Label("Welcome!")
    shell.navigate("home")
shell.run()

# Tokens
accent  = "primary|secondary|info|success|warning|danger|default"
variant = "solid|outline|ghost|toggle"
surface = "content|card|chrome|overlay"
font    = "body|heading-lg|heading-md|caption|code|body+2[italic]"

# Dialogs
bs.alert("Done.")
bs.confirm("Delete?")          # → bool
bs.ask_string("Name:")         # → str | None
bs.ask_integer("Age:", min_value=0)  # → int | None
bs.ask_date("Pick date:")      # → date | None
bs.ask_color()                 # → ColorChoice | None
bs.ask_font()                  # → Font | None
```

---

## Code standards

**Docstrings:** one-line summary + description + `Args:` (name: description, no types).
Single backtick `` `X` `` — never double. No RST roles. Valid values + defaults per kwarg.

**Dataclasses — document fields with ATTRIBUTE DOCSTRINGS, never `Args:`.** Put a
one-line class summary (+ optional prose), then a short docstring string literal
*directly under each field*. Do NOT also list the fields in an `Args:` block —
that renders them twice (a synthesized "Parameters" block + the attribute list).
autodoc `:members:` then renders each field once with its type + description.
(Functions/methods keep using `Args:`.) The conf setting
`autodoc_typehints_description_target = "documented"` suppresses the redundant
synthesized Parameters block for dataclasses. Exemplars: `bootstack.events`
payloads, `bootstack.style.theme.Theme`.

⚠ **No colon on the FIRST LINE of an attribute docstring.** napoleon splits the
first line at the first `:` and jams the pre-colon text into a bogus `:type:`
field — SILENTLY mangling the rendered type (it only *warns* when the split also
breaks a backtick pair). A colon on line 2+ is fine. Use an em-dash/period to
introduce an enum list: `"""Side to pack against — \`'top'\`, \`'bottom'\`..."""`,
not `"""Side to pack against: ..."""`. (PR #106 swept all existing offenders.)

```python
@dataclass
class ChangeEvent:
    """Fires when a field's value is committed (on blur or Enter)."""

    value: Any = None
    """The committed, parsed value."""
    prev_value: Any = None
    """The value before this change."""
```

**`on_*()` shorthands:**
```python
@overload
def on_change(self) -> Stream: ...
@overload
def on_change(self, handler: Callable[[Event], Any]) -> Subscription: ...
def on_change(self, handler=None):
    return self.on("change", handler)
```

---

## Open bugs

- `value=` silently ignored when `signal=`/`variable=` also passed (all boolean widgets)
- `Style._tk_widgets` grows forever — partially resolved; pages are never destroyed

ButtonGroup/ToggleGroup now have **separate** style builders: `ButtonGroup`
(action widgets) uses `style/builders/buttongroup.py`; `ToggleGroup` (selection
widgets) uses `style/builders/togglegroup.py` (registered for the `ToggleGroup`
ttk class; composite sets `ttk_class='ToggleGroup'`). They share the baked
`button_group_*` nine-patch shapes but have independent colors/normal states. The
old ToggleGroup solid-variant contrast issue is fixed.
