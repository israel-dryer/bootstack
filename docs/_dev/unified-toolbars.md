# Unified toolbars — design brief

Status: **design locked, not yet built.** Branch `feat/unified-toolbars`
(folds in GitHub #162 — the undecorated-window controls).

## Problem

Today the top window chrome is three concepts:

- **`menubar`** (`app.menubar` / `shell.menubar`) — menus only, rendered as a
  themed in-window strip on Windows/Linux and the native global menu bar on macOS.
- **`commandbar`** (`app.commandbar` / `shell.commandbar`) — a `CommandBar`
  (internally a `Toolbar`) of buttons / labels / widgets.
- **`menu_layout='fused'|'stacked'`** — a switch deciding how the menu strip and
  the command bar share the single chrome row.

This is overloaded. The two surfaces are really the same thing (a horizontal bar
of items), a *menu* is just one more kind of item, and "fused vs stacked" is a
clumsy stand-in for "how many rows do I want and what's on each." The #162 work
made it worse: the undecorated titlebar became a *third* job crammed onto the
chrome band.

## The model

**One primitive — `Toolbar` — that holds buttons, labels, widgets, AND menus.**
The window's top region is a **vertical stack of toolbars** the author composes;
each toolbar is full-width and stacks top-to-bottom in creation order. A *menu*
(File / Edit / View) is added with `toolbar.add_menu("File")`, which returns the
same context-manager menu builder used today — the menu simply lives *as an item
in the toolbar* rather than in a separate menubar.

```python
with bs.AppShell(undecorated=True) as shell:
    with shell.add_toolbar(show_window_controls=True, surface="primary") as tb:
        tb.add_menu("File")           # menu as a toolbar item
        tb.add_menu("Edit")
        tb.add_spacer()
        tb.add_theme_toggle()
    with shell.add_toolbar(surface="chrome") as tb:   # stacks below
        tb.add_button("Save", icon="save")
        tb.add_button("Run", icon="play")
```

There is no `menubar`, no `commandbar`, no `menu_layout`. You get exactly the rows
you ask for, with exactly the items you put on them.

### Naming

- Public **`CommandBar` → `Toolbar`** (the broader name fits the consolidated
  role). The internal composite is already `Toolbar`.
- **`menubar` / `commandbar` / `menu_layout` are removed** (clean break — bootstack
  is pre-stable; no shims, per `feedback_prerelease_no_shims`).
- `MenuButton` **stays** (it's the in-window dropdown primitive `add_menu` builds
  on, and remains useful standalone). `StatusBar` is unaffected (a separate
  bottom-band concept).

## Public API

### `Toolbar`

Construction (all passthrough via `add_toolbar(**kwargs)`):

| kwarg | meaning |
|---|---|
| `surface` | background surface token (`'chrome'`, `'primary'`, …) |
| `density` | `'default'` / `'compact'` |
| `button_variant` | default variant for `add_button` (`'ghost'`) |
| `padding`, `show_border` | frame options |
| `show_window_controls` | render min/max/close at the right edge + enable drag |
| `draggable` | drag the window (auto-on with `show_window_controls`) |
| `divider` | draw a hairline under this toolbar (explicit, per-toolbar) |
| `use_macos_menus` | bridge this toolbar's menus to the macOS native bar (default `True`) |

Items:

- `add_menu(text, *, key=None) -> MenuGroup` — a dropdown menu item; the returned
  group is a context manager (`with tb.add_menu("File") as f: f.add_action(...)`)
  and also accepts `load([...])`.
- `add_button` / `add_label` / `add_separator` / `add_spacer` / `add_widget` /
  `add_theme_toggle` — unchanged from today's `CommandBar`.
- Container protocol (`_child_master` / `guide_layout`) + context-manager
  (`__enter__`/`__exit__`) so `with shell.add_toolbar() as tb:` works AND bare
  widgets created inside auto-parent into it (the `add_page` dual pattern).

### `add_toolbar()` on App / Window / AppShell

`add_toolbar(**toolbar_kwargs) -> Toolbar` lives on `ChromeHostMixin`, so all three
window types get it. Each call **appends** a toolbar to the window's chrome stack
(append-only for v1) and returns the handle (context-manager capable) — the author
keeps the handle; there is no `host.toolbars` read accessor in v1.

No magic defaults: a window starts with **zero** toolbars. Window controls,
dragging, surfaces, density, and macOS-menu behavior are all per-toolbar params —
there is no window-level `window_controls` / `chrome_surface` / `menu_layout`.

## macOS native menu bridge

macOS must render menus in the native global menu bar, not in the window. So:

- A single logical **`MenuModel`** aggregates the menus from every chrome toolbar
  whose `use_macos_menus=True`, in **stack order then left-to-right** within each
  toolbar (so the native bar reads File, Edit, … deterministically).
- **Windows/Linux:** each `add_menu` renders an in-window `MenuButton` dropdown in
  its toolbar; the aggregated model still binds the menus' keyboard shortcuts.
- **macOS:** the aggregated model renders to the native `NSMenu`; the in-window
  `MenuButton`s for bridged menus are **hidden** (the native bar shows them).
- `use_macos_menus=False` on a toolbar opts its menus *out* of the bridge — they
  render as in-window dropdowns even on macOS.
- A **standalone** `bs.Toolbar` in the body (not part of window chrome) never
  bridges; its menus are always in-window dropdowns.

Shortcuts: the aggregated `MenuModel` binds pattern shortcuts to the host window
(as `WindowMenu` does today), independent of rendering.

## Undecorated windows (folds in #162)

`undecorated=True` only removes the OS chrome — it creates **no** toolbar. The
author builds the titlebar explicitly, which teaches the API on the first line:

```python
with shell.add_toolbar(show_window_controls=True) as tb:
    ...
```

- `show_window_controls=True` adds min/max/close at the right edge and turns on
  dragging (double-click maximizes; a maximized window snaps to normal on drag).
  Close hovers red (danger accent). Minimize uses the Win32 `WS_EX_APPWINDOW`
  taskbar route so a borderless window stays recoverable (Windows); a decoration
  toggle is the non-Windows fallback. (All ported in the #162 work, already on
  this branch.)
- **Trust the author**: nothing prevents two toolbars with controls, and a
  decorated window's `add_toolbar(show_window_controls=True)` simply no-ops the
  controls (the OS draws them). The footgun (undecorated + zero toolbars =
  unmovable window) is self-evident at first run and self-corrects by adding a
  toolbar — no runtime checks.
- macOS force-disables `undecorated` upstream (unchanged).

## What's removed (clean break / migration)

| removed | replacement |
|---|---|
| `bs.CommandBar` | `bs.Toolbar` |
| `app/window/shell.menubar` (+ `WindowMenu`) | `add_toolbar()` + `toolbar.add_menu()` |
| `app/window/shell.commandbar` | `add_toolbar()` |
| `menu_layout='fused'/'stacked'` | author one or two `add_toolbar()` layers |
| `AppShell(chrome_surface=, titlebar_surface=, chrome_divider=)` | per-toolbar `surface=` (+ a stack divider option) |
| `AppShell(window_controls=, draggable=)` | per-toolbar `show_window_controls=`, `draggable=` |
| `AppShell.titlebar` accessor | `add_toolbar(show_window_controls=True)` |

Docs/examples/CLI that wire `menubar`/`commandbar` get swept to `add_toolbar`.

## Internal architecture

- **`ChromeHostMixin` rework** (`widgets/_core/window_menu.py`): replace the
  lazy `menubar`/`commandbar` + `_arrange_chrome` (fused/stacked) with a
  **toolbar-stack manager** — a host-owned `PackFrame` (the chrome stack) into
  which `add_toolbar()` packs each `Toolbar` top-to-bottom, plus the aggregated
  `MenuModel` and its renderers (themed-hidden vs native). `WindowMenu` collapses
  into this manager.
- **`Toolbar.add_menu`** builds a `MenuGroup` in the shared model and, on
  Win/Linux, a `MenuButton` bound to that group's items; subscribes the model's
  `on_change` to re-render. On macOS the `MenuButton` is created hidden (or not at
  all) and the native renderer owns display.
- **`AppShell` layout** (`shell/layout.py`): the dedicated chrome/titlebar band
  logic is replaced by the chrome-stack manager mounted above the body row. The
  `_titlebar` Toolbar built for #162 becomes "the first `add_toolbar` the author
  makes" — i.e. the shell stops auto-building it.
- **App/Window**: the chrome stack mounts above the content frame (today's single
  chrome row generalizes to the stack).

## Resolved decisions (were open questions)

1. **Divider** — an explicit per-toolbar `divider=` param (no implicit stack-wide
   divider; the author opts each toolbar's hairline in). Replaces `chrome_divider`.
2. **`add_toolbar` ordering** — **append-only** for v1 (no `index=`/`before=` until
   there's a real need).
3. **Per-layer surface** — a sensible default (`'chrome'`) with per-call `surface=`
   override.
4. **Read accessor** — **none** for v1. The author holds the handles returned by
   `add_toolbar()`; add a `toolbars` accessor later only if needed.
5. **macOS multi-window** — reuse today's per-window native behavior: the native
   global bar shows the focused window's chrome-toolbar menus, swapping on focus.
   No new design; just don't regress it.
6. **Standalone body `Toolbar` with `add_menu`** — never bridges to the native bar;
   its menus are in-window dropdowns on every platform. Only chrome toolbars (added
   via `add_toolbar()`) participate in the macOS bridge.

## Build order (proposed)

1. `CommandBar` → `Toolbar` rename (public surface + tests + docs sweep).
2. `Toolbar.add_menu()` + the shared `MenuModel` plumbing (Win/Linux in-window
   `MenuButton` path first; native macOS bridge second).
3. `ChromeHostMixin` toolbar-stack manager + `add_toolbar()` on App/Window.
4. AppShell: mount the stack above the body; remove the old chrome/titlebar/
   menubar/commandbar surface; re-home the #162 controls onto a normal toolbar.
5. macOS native bridge (aggregation order + hide in-window + `use_macos_menus`).
6. Remove `menubar`/`commandbar`/`menu_layout`; sweep docs/examples/CLI.
7. Tests (one `App` per process) + clean-build docs.
