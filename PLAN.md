# PLAN — #407, the harness scene reset

Branch `fix/harness-scene-reset-407`, off `main` at `76ae7a26` (`0.3.1` shipped).

## Round cap: 2

`REVIEW-PROTOCOL.md` gate 3. This is a **patch-safe** change — it touches
`tests/conftest.py` and nothing under `src/`, so it adds no public surface. Two
rounds, and anything surviving them is filed as an issue rather than fixed here.

⚠ Gate 1 applies with unusual force on this branch: **a diff that touches no
`src/` earns no review round at all.** If the whole branch stays inside `tests/`,
round 1 is a self-check by the implementing session and there is no round 2.
That is not a loophole — it is the rule that exists because this project spent
four rounds reviewing test scaffolding a week ago. Open a round only if
production code changes.

## What is wrong

`tests/conftest._region()` returns `app._region_root`, and **on a decorated
`App` that attribute IS the root**. `_snapshot`/`_reset_scene` therefore walk the
root's children twice and never look inside `App._content_frame`, which is where
every widget a test builds actually lives.

**Measured on `main` at `76ae7a26`**, five labels built the way a test builds
them:

```
root          = .
_region_root  = .          region IS root? True
_content_frame= .!flexframe
widgets a test created, inside _content_frame: 5
of those, VISIBLE to _reset_scene's walk: 0 of 5
```

The reset finds `.!flexframe` in `keep`, treats it as permanent scaffolding —
which it is — and stops. **So the scene reset has never torn down a content
widget in the entire life of the shared-root harness**, and every test's widgets
accumulate for the whole session.

## What it is expected to explain

Recorded in `CLAUDE.md`, to be **re-measured here rather than assumed**:

- The widget leg runs **144s**; with the reset working it was measured at **80s**.
- `PageStack` needs an `isolated` marker it should not need.
- A geometry probe once turned "state pollution" into "reqheight 1242 > window
  828, so the geometry manager unmapped it" — the direct consequence of a root
  that never empties.

And, newly suspected on 2026-08-12 — **suspicion, not a claim**:

- **#447**, the dialog Enter/focus flakes, measured at **~5–8% of five-file
  runs** (4/50 and 2/40). One failure carried `focus_lastfor()` returning the
  empty string, and `focus_set()` silently no-ops on a window Tk does not
  consider viewable. A root crowded with a session's worth of widgets is a
  plausible cause; whether it is *the* cause is unknown.
- **#432**, the shared-root GUI leg exiting silently mid-run on Linux.

**None of these is a success criterion.** The fix is justified by the reset not
doing what it says it does. If the flake rate does not move, that is a result to
record, not a reason to keep changing the harness.

## The change

`_region()` returns `app._content_frame` when it exists, falling back to
`_region_root` and then the root. `_reset_scene` already walks the root's
children separately for stray toplevels, dialogs and chrome, so that half stays
as it is.

## Prior art, deliberately consulted

`D:\Development\ttkbootstrap` — same maintainer, same shared-root design, and
its `tests/conftest.py` says it followed bootstack's approach. Its `root` fixture
snapshots `app.winfo_children()` and destroys what is new, which **works there
because `Window` IS the root and tests parent directly into it**. bootstack
interposes a content frame, so the identical snapshot is one level too shallow.
The divergence is the whole bug.

Two things from that repo are worth taking but are **NOT in this branch's
scope**, because bundling them would make a test-infrastructure fix
unreviewable:

- Pinning Tk scaling to baseline inside `conftest`, so pixel assertions do not
  depend on the host display (a laptop at 125% breaks them).
- Its CI matrix, which is #380's answer — including `fail-fast: false` with a
  stated reason, `xvfb-run -a -s "-screen 0 1280x1024x24 -dpi 96"`, and a
  per-job step reporting the Tk build rather than inferring it.

## Verification

Against `main` at `76ae7a26`, measured — not reasoned from numbers in
`CLAUDE.md`, which have been wrong six times:

1. **The reset actually reaches content widgets.** The probe above, re-run: it
   must report all 5 visible. This is the control; without it nothing else means
   anything.
2. **Full `py -3.12 tests/run_gui.py` stays green**, with the summed counts
   recorded beside the commit. Any test that starts failing is the interesting
   result — it was passing on state a previous test left behind.
3. **Widget-leg wall clock**, before and after, same box, same session.
4. **`PageStack` without its `isolated` marker.**
5. **The #447 flake rate**, same 50-run five-file loop as on `main`. Report
   whatever it is, including "unchanged".

## Explicitly out of scope

#380 (CI), #432 (the Linux leg), #447 (the dialog flakes), the `tests/widgets/*.py`
files that `testpaths` never collects, and the second latent bug recorded under
#407 (`test_select_change_event_value_space` picking up 5 change events from
earlier tests). **If the reset fix exposes that one, it gets its own issue, not a
fix here.**
