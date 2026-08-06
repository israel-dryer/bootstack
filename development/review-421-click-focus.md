# `/code-review` record — `fix/datatable-click-focus-421` (#421)

**Run:** 2026-08-06, by the maintainer via `/code-review`. **Target:** the top 3 commits only — `f425430f` (the fix), `ff814b85` (CHANGELOG), `6c18d34e` (the #417 review record). The lower 8 commits (`fix/datatable-double-click-417`) were reviewed separately on the same day; that record is `development/review-417-double-click.md`.

**Verdict: the #421 fix is correct and ship-ready.** One real bug found in the lines the diff touches, plus two low-severity items. Neither branch was modified during the review — it worked from committed blobs (`git show <sha>:<path>`) and a detached `git worktree`, since removed. `fix/datatable-click-focus-421` remained at `6c18d34e`, `fix/datatable-double-click-417` at `f7405d97`.

## Verified — do NOT re-derive

- **The two new tests are not vacuous.** Run against unfixed source, both fail with exactly the right symptom (`focus_lastfor()` returns the App root, not the tree), while test 1's internal control arm — clicking a plain data row — passes. Against the branch source, 23/23 green. This is the control that the #417 review skipped and that let two defective tests through.
- **Full suite green at the head.** `py -3.12 tests/run_gui.py` → **973 passed / 13 skipped** (widgets+CLI) and **123 passed / 6 skipped** (data), matching the count recorded for `ff814b85`. A second independent shared-root run of `tests/widgets/public` → 949 passed / 13 skipped. The previously-flaky `test_group_chevron_tracks_keyboard_expand` passed in both runs.
- **The group-header focus concern is a non-issue** — this was the open question the handoff flagged for the reviewer. Tk's `<space>` binding is `ttk::treeview::ToggleFocus`, whose body is `Toggle $w $item`: it toggles the item's *open state*, not selection. Measured after clicking a group header — `tree.selection()` is `()`, `table.selection` is `[]`, no `SelectionChange` fires. Item focus on a group header cannot leak into selection.
- **No downstream reader is affected.** `_tree.focus` is read nowhere else in the `tableview` package, so nothing assumes the focus item is a data row.
- **The fix is complete for the click path.** Only two `return "break"` sites exist in `tableview.py`; both got the call.
- **Taking focus on an empty-space click is not a regression** — it matches ttk's own `Press`, which does `focus $w` unconditionally.

## Findings

### 1 — MEDIUM. `tableview.py:2918` — column resizing is dead whenever selection checkboxes are on

`_on_header_click` only special-cases `region == "heading"`. A click on a column **separator** (region `"separator"`) falls through to `if self._toggle_select_active():`, where `identify_row(event.y)` returns `""` — and the branch still returns `"break"`, swallowing ttk's `resize.press`.

**Measured on a live app:** a plain table's separator drag moves widths (`120 → 156`); on a table with `selection_mode="multi", show_selection_controls=True`, dragging **any** of its three separators changes nothing.

The `break` is load-bearing only when there is a row to toggle. **The diff makes this worse on the same lines:** `_take_click_focus(iid)` sits *above* the `if iid:` guard, so a user attempting a column resize on a checkbox table now also has keyboard focus yanked into the tree body (measured: `focus_lastfor()` becomes the tree after a separator press).

Fix — move the call inside the guard and return `"break"` only there:

```python
if self._toggle_select_active():
    iid = self._tree.identify_row(event.y)
    if iid:
        self._take_click_focus(iid)
        ...
        return "break"
```

**Verified by the reviewer:** with that change all three separators resize correctly (`#0` 43→79, `#1`/`#2` likewise) and all 23 `test_datatable.py` tests stay green.

The resize breakage **predates this branch**, but the diff edits exactly these lines and the correct scoping is the same one-line change. No test covers it either way — a separator-resize test is missing.

### 2 — LOW. `tableview.py:2874` — `except Exception: pass` is silent in the one place where silence is the bug

The whole defect #421 fixes is "focus silently did not happen." If `focus_set()` or `focus(iid)` ever raises, the fix degrades back to the original bug with zero signal on any channel. Use `debug_log_exception` (`_runtime/utility.py`, added by #399) — it never raises, so it is safe in a Tk dispatch path. Neighboring code does the same bare-`pass` thing, but this is new code.

### 3 — LOW. `CHANGELOG.md:25` — the bullet's headline overstates the blast radius

> **Clicking a `DataTable` row now leaves the keyboard pointed at that row.**

reads as though ordinary row clicks were broken. They never were — the branch's own control assertion ("clicking a data row did not focus the table") proves plain rows always took focus, confirmed against unfixed source. A reader scanning the release notes for "was I affected?" gets a false positive on every ordinary `DataTable`. That is the standard `CLAUDE.md` sets for CHANGELOG entries — it is why #397/#401 were omitted from `0.2.1`. Scope the headline to group headers and checkbox tables; the body already says the right thing.

## Gotcha worth carrying

**A `git worktree` runs against `main`'s source unless you set `PYTHONPATH`.** The editable install points at `D:\Development\bootstack\src`, so a worktree's tests import **main's** source, not the worktree's. That accident handed this review a free pre-fix control — but it would silently invalidate a post-fix run. Set `PYTHONPATH` to the worktree's `src` when testing in one.

## Disposition (maintainer, 2026-08-06)

All three findings are to be **fixed on `fix/datatable-click-focus-421`** as part of #421 before `0.2.2` ships. Finding 1 is a user-visible bug on shipped behavior and adds no public surface, so it belongs on the patch line either way.
