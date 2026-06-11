# Menu / Menu bar redesign

Branch: `feat/menu-redesign`. Started 2026-06-11.

Modernize the menu bar into a single cross-platform facade: a themed in-window
strip on Windows/Linux, the native global menu bar on macOS. Retire the legacy
`tk.Menu` icon machinery that supported icons on Win/Linux menubars.

## The two-surface model (the core idea)

A **menu bar** and a **command bar** are two *different* surfaces — on every
platform, not just Windows. Conflating them is what makes cross-platform hard.

| Surface | Contents | Windows / Linux | macOS |
|---|---|---|---|
| **Menu bar** | menus only (File/Edit/View → flat item lists) | themed in-window strip | **native global menu bar** (`app['menu']`) |
| **Command bar** (= existing `Toolbar`) | arbitrary widgets — buttons, toggles, theme switch, search | in-window strip | **in-window** toolbar strip (NOT the global bar) |

**Hard macOS constraint (the reason for the split):** the macOS global menu bar
(`app['menu']`) lives at the top of the *screen*, is OS-owned, and can contain
**only menu cascades** — no buttons, toggles, or arbitrary widgets. The right-hand
"menu extras" area is OS-owned (NSStatusItem) and unreachable via Tk. So arbitrary
widgets *fundamentally cannot* live in the Mac menu bar.

**Resolution — split honestly, don't artificially limit.** The limitation falls
out of the type system: the menu-bar API only accepts menus (so it translates to
native Mac for free); widgets go in the command bar, which is **in-window on every
platform** and therefore has no Mac constraint. Tk note: `image`/`compound` *do*
work on Aqua menus, but native Mac menus are text-only by HIG convention — so we
drop icons on Mac by choice, not because Tk can't.

## "Fusing" — Win/Linux rendering of the two surfaces

On Win/Linux the framework draws both surfaces in **one physical row** by default:
menu triggers pinned left, command-bar regions filling center/right. On macOS the
two models split to their native homes automatically — the menu lifts out to the
global bar, the command bar stays as an in-window row. Same user code; placement is
entirely internal.

```
Windows / Linux (fused, one row):
┌──────────────────────────────────────────────────┐
│ File  Edit  View       🔍 search      🌙   ⚙     │
├──────────────────────────────────────────────────┤

macOS (split):
  App  File  Edit  View              ← OS global menu bar (screen top)
┌──────────────────────────────────────────────────┐
│                        🔍 search      🌙   ⚙     │  ← in-window command bar
├──────────────────────────────────────────────────┤
```

**`menu_layout` option** (`'fused' | 'stacked'`, default `'fused'`) — Win/Linux-only
layout hint. `fused` = menus + command bar share one row (modern, compact; good for
simple apps). `stacked` = a menu row with the command bar in its own full-width row
beneath (good for toolbar-heavy single-page apps). **No effect on macOS** (the menu
always leaves the window, so both render identically) — document it as exactly that.
Justified because the two scenarios want opposite layouts and no single default
serves both; cheap because the two-surface model already separates them (it's a
layout branch, not a subsystem).

## Locked decisions (2026-06-11)

1. **Two-surface model.** New `win.menu` facade (menus only) + the existing
   `Toolbar` as the command bar. Do NOT overload either into the other.
2. **macOS icons: drop on ALL Mac native menus** (menu bar AND right-click context
   menus). → Lets us largely **retire `MenuManager`** (its entire job is icon
   tracking + theme-aware recolor on `tk.Menu`).
3. **Item type rename `command` → `action`.** Types become
   `action`/`check`/`radio`/`separator`. The public verb stays `on_click`. (This is
   the deferred Tk-ism rename the handoff flagged.)
4. **Shortcuts: display + auto-bind.** A *pattern* (`shortcut='Mod+S'` with
   `on_click`) is registered + bound via the `Shortcuts` service so the keypress
   actually fires, AND shown as the accelerator. A *registered key*
   (`shortcut='save'`) is display-only (assumed already bound). Rationale: `tk.Menu`
   accelerators are **display-only** on every platform (Tk never binds them), and the
   themed Win/Linux strip doesn't either — so binding belongs in the model layer,
   not the renderer.
5. **Single layer only.** Menu bar → top-level menus → flat item lists. No
   sub-submenus (one level of cascade on Mac, the normal menubar shape). Kills the
   recursion in `_add_menu_items` and the rebuild-on-insert dance.
6. **`menu_layout` default `'fused'`**, `'stacked'` available.

## Architecture: one model, two renderers

A platform-neutral **menu model** is the single source of truth; two renderers
consume it. Most machinery already exists.

- **Menu model** — a list of menu groups, each a flat list of items
  (`action`/`check`/`radio`/`separator`). Essentially today's `ContextMenuItem` +
  dict form, single-layer.
- **Renderer A — Win/Linux (themed):** a horizontal strip of trigger buttons, each
  opening a `_ToplevelContextMenu` from that group's items. The
  `DropdownButton → ContextMenu` chain in the existing region-bar already does this.
- **Renderer B — macOS (native):** translate the model to `tk.Menu` cascades and
  assign `app['menu']` (the `MenuManager.create_menu` path, **minus icons**, minus
  nested cascades).

### What we reuse / retire

- **`ContextMenu`** (dual backend, `_runtime`-dispatched on `windowingsystem`) —
  KEEP. It's already the facade pattern. The Win/Linux menu-bar dropdowns reuse
  `_ToplevelContextMenu`.
- **`Toolbar`** (`widgets/toolbar.py` + `_impl/composites/toolbar.py`) — KEEP as the
  **command bar**. Already has buttons/labels/separators/spacer/`add_widget`/window
  controls; auto-included in AppShell. Gets a public façade on App/Window.
- **`MenuManager`** (`_runtime/menu.py`) — **largely RETIRE.** With icons gone on
  Mac and single-layer menus, its icon-tracking + theme-recolor + recursive cascade
  builder are no longer needed. Native menu-bar build becomes a thin flat-cascade
  builder (label translation + accelerator display only). Audit remaining callers
  before deleting (`_NativeContextMenu` uses it for icon resolution — that path also
  loses icons on Mac per decision #2).
- **`MenuBar`** composite (region before/center/after) — this is really command-bar
  / chrome territory and overlaps `Toolbar`. Its consolidation is the HELD
  **Toolbar/MenuBar rework**; this redesign does NOT fold it in, but the new menu
  facade makes the region-bar's menu role obsolete. Decide its fate in the rework.
- **Legacy `create_menu` / `create_menu_items` + `app['menu'] = create_menu(...)`**
  — the Win/Linux usage is superseded by the themed strip; the Mac usage is absorbed
  by Renderer B. Retire the public-ish helpers (they're in `_runtime`, not exported
  top-level — confirm).

## Public API (proposed)

```python
with bs.Window(title="Editor", menu_layout="fused") as win:

    # Menu bar — menus only; relocates to the global bar on macOS
    with win.menu.add_menu("File") as file:
        file.add_action("Open", shortcut="Mod+O", on_click=open_file)
        file.add_separator()
        file.add_action("Quit", shortcut="Mod+Q", on_click=win.close)
    with win.menu.add_menu("Edit") as edit:
        edit.add_action("Undo", shortcut="Mod+Z", on_click=undo)

    # Command bar (Toolbar) — widgets; stays in-window everywhere
    win.toolbar.add_button(icon="moon", on_click=bs.toggle_theme)   # right side via spacer/region

    # Declarative form — same model
    win.menu.load([
        {"text": "File", "items": [
            {"text": "Open", "shortcut": "Mod+O", "on_click": open_file},
            {"type": "separator"},
            {"text": "Quit", "shortcut": "Mod+Q", "on_click": win.close},
        ]},
    ])
```

- `win.menu` — lazy facade. `add_menu(text) -> MenuGroup` (context-manager capable);
  `MenuGroup.add_action/add_check/add_radio/add_separator`; `load([...])` declarative.
  No `region=` (menus always run left-to-right).
- `win.toolbar` — public façade over the existing `Toolbar` command bar.
- `menu_layout` — Window/App/AppShell ctor kwarg.
- AppShell exposes the same `shell.menu` / `shell.toolbar`.

## Implementation sequence (proposed)

1. **Menu model + builder** (`MenuGroup`, item dataclasses, `action` type, declarative
   `load`). Pure data + shortcut resolution (display + auto-bind via `Shortcuts`).
2. **Renderer A (Win/Linux)** — themed menu-bar strip from the model (reuse
   `_ToplevelContextMenu`). Trigger buttons + dropdowns.
3. **Renderer B (macOS)** — flat-cascade `tk.Menu` → `app['menu']`, no icons, label
   translation + accelerator display.
4. **`win.menu` facade + placement** — wire into App/Window/AppShell; `menu_layout`
   fused/stacked; `win.toolbar` public façade.
5. **Retire** `MenuManager` icon machinery + legacy `create_menu` path; drop icons in
   `_NativeContextMenu`. Audit callers first.
6. **Tests** — model, shortcut binding, single-layer enforcement, per-platform render
   (mock `windowingsystem`). One module-scoped App (multi-App-per-process crashes —
   see attach/detach tests).
7. **Docs** — Widgets page + a how-to; API Reference home; screenshots
   (fused/stacked, both themes). Per the established widget-doc pattern.

## Progress

- **Step 1 — model: DONE & green.** `menu/model.py` (`MenuModel`/`MenuGroup`/
  `MenuItem`, `action` type, declarative `load`, single-layer enforced, shortcut
  display + `bind_shortcuts`). `classify_shortcut` extracted in `_runtime/shortcuts.py`.
  Tests `test_menu_model.py` (20).
- **Step 2 — Renderer A (Win/Linux themed): DONE & green.** `menu/render_themed.py`
  (`ThemedMenuBar`: horizontal `PackFrame` of `DropdownButton` triggers, one per group;
  model→`ContextMenuItem` translation; shared radio vars; `rebuild()`). Smoke tests
  `test_menu_render_themed.py` (5, gui-marked).
  - **DEFERRED renderer-A interaction polish** (after the facade is visible): hover-to-
    switch between open menus, Alt-to-focus + arrow navigation across triggers. Core
    click-to-open works; these are feel refinements.

## Open questions / to confirm during build

- Fate of the region-bar `MenuBar` composite (defer to HELD Toolbar rework, but the
  new facade obsoletes its menu role).
- `win.menu` vs `app.menu` naming consistency across App/AppShell/Window.
- Whether `menu_layout` lives as a ctor kwarg only or also a live property.
- Confirm `create_menu`/`create_menu_items` are not part of any public surface before
  retiring (they live in `_runtime/menu.py`).