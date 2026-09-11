# #511 — a shell slot hidden across a theme change comes back wearing the old palette

> **Outcome (2026-09-11).** Shipped as `f74f0837` on `0.4.x — Patch line`, with three departures from this plan. The fix walks slots by their show flag, not `winfo_ismapped()`, and **omits the dock**, which nothing public can show. The test was cut from four to **one** (maintainer: test only what is necessary); the controls were run once rather than kept. And the module had to be added to `ISOLATED` in `tests/run_gui.py`, or it ran nowhere. `AppShell` was measured stale pre-fix as well as `Workbench`. ⚠ **This plan is wrong that `only_stale=False` would merely over-repaint:** measured, at idle the pane's canvas is not yet viewable, so that walk skips it and does not fix #511 at all.

**Status:** plan for the maintainer. Written 2026-09-08 against `main` @ `7e0f371e` (one commit past the `v0.4.3` tag). Every measurement below was taken with `development/probe_511_hidden_sidebar_theme.py`; nothing here is reasoned from reading alone.

**The test is already written and committed-ready:** `tests/widgets/public/test_shell_slot_theme_refresh.py`. On unfixed `main` it reports **2 failed, 2 passed** — the two failures are the defect, asserting on color, and the two passes are the controls. Do not edit it to make it pass; it should turn green on the fix alone.

## What the user sees

Reported against `0.4.2` on Windows 10: collapse the nav pane by clicking the active workspace's rail icon, switch to the dark theme, expand the pane again — the pane's background stays white while everything around it is dark. The screenshot on the issue shows the selected `General` item correctly dark **on a white pane**, which is the tell.

## Root cause

`Style.apply_theme_walk(root, only_stale=False)` (`style/style.py:349`, called from `theme_use` at `style.py:256`) **skips every widget that is not `winfo_viewable()`** — that is the design, not a bug. Off-screen widgets are deliberately left stale and repainted by whatever container next shows them. Three such "now visible" triggers exist:

| trigger | file |
|---|---|
| `PageStack._navigate` | `_impl/composites/pagestack.py:236` |
| `Expander.expand` | `_impl/composites/expander.py:273` |
| `PublicWidgetBase._recolor_on_attach` | `widgets/_core/base.py:550` |

**`ShellLayout` is a fourth hide/show container and has no trigger.** `_relayout_body()` (`_impl/composites/shell/layout.py:210`) `pack_forget`s and re-`pack`s the rail, sidebar and dock; `_relayout_window()` (`layout.py:194`) does the same for the statusbar and the body. Neither calls the walk, so a slot that was unpacked across a theme change is never repainted.

`docs/_dev/theme-repaint-architecture.md` predicts this in its *Known limitations* section and states the remedy: *"If you add another hide/show container, call `get_style().apply_theme_walk(shown_subtree, only_stale=True)` after you pack the content (deferred to `after_idle` so it is mapped first)."* **The fix is to do exactly that.**

### Why only the pane background looks wrong

ttk widgets follow the global style, which `theme_use` rebuilds wholesale, so they cannot go stale. Only imperatively-painted Tk widgets hold their own color. In this layout that is the nav panel's scroll canvas — `navpanel → scrollview → canvas`. Hence dark items on a light pane.

## Measured evidence

One `Workbench`, one process, colors read as `cget('background')` rather than from screenshots (the shell has exactly two painted widgets in the sidebar, one nav pane per workspace):

| arm | sequence | pane canvas |
|---|---|---|
| baseline | light, sidebar visible | `#f8f8f8` |
| **A** | hide → dark → show (the report) | **`#f8f8f8`** — stale |
| **B** | control: same final dark theme, toggled while visible | `#2a2f35` |
| **D** | re-staled in dark, then navigate to the other workspace | that pane repaints to `#2a2f35`; the stale one stays `#f8f8f8` |

**Arm B is what rules out "dark just looks like that."** **Arm D proves the repaint machinery is sound** — `PageStack._navigate`'s walk fixes any pane it shows, so only the trigger is missing. It also explains the report's shape: toggling the *same* workspace fires no navigation, so nothing rescues the pane. **A user can work around it today by switching workspace and back.**

⚠ **Two instrument failures worth not repeating.** The first probe reported "no difference" because the window was never mapped, so the walk skipped *everything* and both arms agreed for the wrong reason — the probe now asserts viewability and aborts rather than concluding. And **a `_bs_theme_version` staleness count is a useless instrument here**: a freshly built widget is never stamped, so "24 of 24 stale" is the normal state, not evidence. Color is the only honest observable.

## The fix

Add one deferred, stale-only walk over the slots that are currently packed, called at the end of both relayout methods. Shape, not prescription:

```python
def _recolor_shown_slots(self) -> None:
    """Repaint slots that just became visible after a theme change (#511).

    The theme walk skips off-screen widgets, so a slot unpacked across a theme
    change comes back stale. Re-packing is the genuine "now visible" trigger,
    matching PageStack navigation and Expander expansion.
    """
    if self._recolor_pending:
        return
    self._recolor_pending = True

    def _recolor() -> None:
        self._recolor_pending = False
        from bootstack.style.style import get_style
        style = get_style()
        for slot in (self._rail, self._sidebar, self._content, self._dock, self._statusbar):
            try:
                if slot.winfo_ismapped():
                    style.apply_theme_walk(slot, only_stale=True)
            except tkinter.TclError:
                pass          # destroyed between the relayout and the idle callback

    try:
        self.after_idle(_recolor)
    except (tkinter.TclError, AttributeError):
        pass
```

⚠ **Two things about that sketch, both verified rather than assumed.** `ShellLayout(App)` and `App(BaseWindow, WidgetCapabilitiesMixin, tkinter.Tk)` — **`self` IS the root window**, so `self.after_idle(...)` already satisfies "defer on the root, never on the widget"; there is no `_root()` call to make and no orphaned-command hazard. And **`layout.py` does not import `tkinter`** (only `sys`, `typing`, and four bootstack modules), so either add the import or catch `Exception`.

Points that matter, each with its reason:

- **`only_stale=True`, never `False`.** With `only_stale`, a relayout that follows no theme change matches versions and does nothing — no repaint, no flicker, no cost in the common case. That is what makes it safe to call on *every* relayout. `test_showing_a_pane_without_a_theme_change_keeps_its_color` guards this.
- **Defer to `after_idle` on the shell itself, never on a slot.** A callback registered on a widget is a Tcl command owned by that widget: destroying it deletes the command while the timer is pending and Tcl fires an orphan. Here `self` is the root, so scheduling on `self` is already the safe form. The deferral is needed because the walk must run after the geometry manager has actually mapped the slot.
- **Guard `TclError` *and* `AttributeError`** — `destroy()` sets `_tclCommands` to `None`, so a late callback can raise either.
- **Collapse repeats behind a `_recolor_pending` flag.** `_relayout_body` and `_relayout_window` can both run in one gesture (and `_relayout_window` re-packs the body); without the flag a resize storm queues one walk per call.
- **Walk each packed slot, not the shell root.** Walking the root would also repaint slots that are still hidden, which defeats the laziness the design is built on. Iterating the packed slots keeps the existing contract: a hidden thing stays stale until it is shown.
- **Initialize `self._recolor_pending = False` in `__init__`**, beside the other slot state around `layout.py:129`.

### Scope — all four visibility axes, not just the sidebar

`_relayout_body` covers **rail, sidebar and dock**; `_relayout_window` covers the **statusbar** (and re-packs the body). All four go through the same two functions, so one helper called from both closes every one of them. **Only the sidebar is measured** — the rail carried no imperatively-painted widget in the reported configuration, so it shows nothing today; that is a property of the configuration, not a guarantee about the slot.

### Rejected, so they are not re-proposed

- **Dropping the `winfo_viewable()` check in `apply_theme_walk`.** That would repaint every off-screen widget on every theme change — the exact cost the two-mode design exists to avoid — and would fight `PageStack`'s `_bs_nav_hidden` pruning, which deliberately keeps inactive pages mapped but unpainted.
- **Binding `<Map>` on the slot or its children.** `docs/_dev/theme-repaint-architecture.md` rules this out by name: *"There is no `_enable_theme_repaint`, no per-widget `<Map>` deferral, and no widget registry."* Visibility is resolved at apply time, and a new trigger must not reintroduce per-widget bookkeeping.
- **Repainting from the navmodel's sidebar facet handler.** It would fix the sidebar only, leave the other three axes broken, and put view work in the model.

## Suggested commits

Four, in this order. The first two are yours; the third is written and ready.

1. **`fix(shell): repaint a slot that becomes visible after a theme change`**
   `layout.py` only — the helper, the `_recolor_pending` init, and the call at the end of `_relayout_body()` and `_relayout_window()`. Body should name #511 and say the walk skips off-screen widgets by design, so re-packing is the trigger that was missing.

2. **`docs(dev): add the shell slots to the container-show triggers`**
   `docs/_dev/theme-repaint-architecture.md` — add `ShellLayout._relayout_body` / `_relayout_window` to the *Container-show triggers* list, and drop the sidebar case from *Known limitations* now that it is covered. **That file is the live account of this machinery; leaving it listing three triggers when there are four is how the next session re-derives this.**

3. **`test(shell): cover a slot hidden across a theme change`**
   `tests/widgets/public/test_shell_slot_theme_refresh.py` (written) plus `development/probe_511_hidden_sidebar_theme.py` (the instrument). Fine to fold into commit 1 if you prefer fix-with-test; keep the probe either way — it is the only thing that reproduces the *user's* sequence end to end.

4. **`docs(changelog): note the shell slot theme refresh`**
   Under `## [Unreleased]` → `### Fixed`. The section does not exist right now; `0.4.3` consumed it, so this commit recreates it. Draft, one paragraph on one line per the CHANGELOG rule:

   > - **A collapsed shell region now picks up a theme change when it is shown again.** Collapsing an `AppShell` or `Workbench` sidebar, switching theme, and expanding it again brought the pane back in the previous theme's colors — a white nav pane against an otherwise dark window, with the correctly-themed navigation items still drawn on it. Regions that are on screen when the theme changes were never affected, and switching to another workspace and back already corrected it. This reaches the rail, sidebar, dock and status bar, which share the same show/hide path. ([#511](https://github.com/israel-dryer/bootstack/issues/511))

## Verifying it

```bash
py -3.12 -m pytest tests/widgets/public/test_shell_slot_theme_refresh.py -v   # 4 passed
py -3.12 development/probe_511_hidden_sidebar_theme.py                        # ARM A == ARM B
py -3.12 tests/run_gui.py                                                     # exit 0
```

Baseline to move from: **Windows `1786 / 22`, 33 legs, exit 0** at `f6d59d19`. The new file adds **4** tests, so expect `1790 / 22`. ⚠ Read exit codes without a pipe.

**Drive it by hand as well**, with `issues/issue_511.py` — a green suite is not the same as the user's gesture. Collapse the pane with the rail icon, toggle the theme from the toolbar, expand: the pane must come back dark. **A demo found the last two blockers this project shipped past a green suite and a written review.**

## Decisions left to you

- **Milestone.** The fix adds no public surface, so it is patch-shaped and `0.4.x — Patch line` fits — but placement is your call, and #511 is currently unmilestoned.
- **Whether the statusbar and dock get their own tests.** The helper covers them; I did not write assertions for them because neither carries an imperatively-painted widget in a default shell, and a test that cannot fail is worse than no test.
- **Whether `0.4.4` is cut for this alone**, or it waits for company on the patch line (#488 is the widest-reaching thing open there).
