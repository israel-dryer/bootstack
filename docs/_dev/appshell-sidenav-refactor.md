# AppShell + SideNav refactor — seed brief

Status: **NOT STARTED** — seed for a fresh session (chosen 2026-06-12). This is a
starting point, not a finished design; the first task is an audit (below), then
lock the public API with the maintainer before touching internals.

## Why

Two related gaps:

1. **AppShell leaks internals.** `AppShell` is the batteries-included app frame
   (command bar + nav + paged content). Its accessors return the *internal*
   composites with the old imperative API rather than the public widgets:
   `shell.commandbar` returns the internal command-bar composite (the `command=`
   API), not a public `CommandBar`; `shell.nav` / page access are similar. So an
   AppShell user drops out of the curated public surface the moment they touch the
   chrome.
2. **SideNav is due a refactor** (maintainer, 2026-06-12). Its two events still use
   the old past-tense names (deferred from the `on_select` pass), and several
   long-standing SideNav/AppShell quality items are outstanding.

This builds on the menu/command-bar redesign (PR #124, `project_menu_redesign`):
`Toolbar`→`CommandBar`, legacy `MenuBar` removed, `app.menubar`/`app.commandbar`.

## Goals

### AppShell — public façades
- `shell.commandbar` → a public **`CommandBar`** handle (not the internal composite);
  `shell.menubar` is already public (PR #124) — confirm it stays consistent.
- `shell.nav` → a public **`SideNav`** handle; `shell.pages` (or equivalent) → public
  page handles.
- `add_*` methods return **public widget handles** (the `_adopt`-classmethod pattern
  from the widget-API audit, "§2b") instead of `None`/internal refs.
- `CommandBar.content` / make `CommandBar` a real container.
- Window-control accessors on AppShell (close/minimize/etc. — `WindowControlsMixin`
  parity with App/Window).
- Fold `menu_layout` / `chrome_surface` into AppShell (deferred in PR #124 because
  its command bar is internal/pre-placed — this refactor unblocks it).

### SideNav — refactor
- **Event renames** (present-tense convention, `project_event_naming_revisit`):
  `on_pane_toggled → on_toggle`, `on_display_mode_changed → on_display_change`.
  Clean break (pre-release, no shims). Update the public method + `self.on(...)` key
  + `register_widget_events` map + docs + tests. NOTE: the internal sidenav composite
  has its own `on_selection_changed`/`_on_selection_changed` (view.py) and AppShell
  binds the internal `on_selection_changed` — those are internal; the rename targets
  the PUBLIC `SideNav` methods only.
- Deferred SideNav/AppShell improvements (from CLAUDE.md Carryover):
  - `nav_pane_width=` not wired to `SideNav(pane_width=)`.
  - hardcoded nav density / font.
  - group active-child highlight + indentation.
  - footer non-page widgets.

## First steps (the audit)
1. Map the PUBLIC surface vs INTERNAL composites for AppShell and SideNav (an Explore
   pass like the widget-API audit). Where do internals leak through `shell.*`?
2. Inventory `add_*` methods and what they currently return.
3. Confirm the `_adopt`-classmethod pattern (how Button/etc. wrap an existing internal
   widget as a public handle) and whether it generalizes to CommandBar/SideNav/pages.
4. Draft the public API (handles + return types), get maintainer sign-off, THEN implement.

## Pointers
- `docs/_dev/widget-api-audit.md` — the §2b return-handle/`_adopt` work + AppShell
  deferred improvements are detailed here.
- Memories: `project_appshell_sidenav_refactor` (this initiative),
  `project_menu_redesign` (PR #124 base), `project_event_naming_revisit` (the SideNav
  event renames + the broader naming convention), `project_macos_window_chrome`
  (native chrome — SEPARATE follow-up, not part of this).

## Conventions (reminders)
- Pre-release → clean breaking changes, no compat shims (`feedback_prerelease_no_shims`).
- No Tk leaks in the public surface; return public widgets, not internal composites.
- `feat/*` branch off `main`; PR back. Update `tests/test_public_surface.py` for any
  surface change. Clean-build the docs (`-W`, warning-free) for any doc change.
