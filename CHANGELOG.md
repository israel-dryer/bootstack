# Changelog

All notable changes to bootstack are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and from 0.1.0 onward the project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- release-notes-start -->

## [0.1.2] — menu dismissal fix

### Fixed

- **Dropdown and context menus now dismiss when their window moves.** On
  Windows and Linux, an open menu — a toolbar `add_menu` dropdown, or any
  right-click `ContextMenu`, `Select`, or `MenuButton` popup — stayed pinned to
  its original screen position when the window was dragged, resized, or
  minimized: it "hung in the air." Only clicks *outside* the menu dismissed it,
  and dragging the title bar fires no click. Menus now also close on the owning
  window's own move, resize, or minimize, matching native menu behavior. (macOS
  already used the native system menu, which dismisses on its own.)

## [0.1.1] — packaging fix

### Fixed

- **Declared `pygments` as a runtime dependency.** `CodeEditor` requires Pygments
  for syntax highlighting, but it was not listed in the project dependencies, so a
  clean `pip install bootstack` would raise `ModuleNotFoundError: No module named
  'pygments'` when constructing a `CodeEditor` (including on the bundled demo's
  editing page). Pygments is now installed automatically with bootstack.

## [0.1.0] — first stable release

The first stable release of bootstack. The public **compose API** — everything
you import as `bootstack as bs` plus the curated submodules (`bootstack.data`,
`bootstack.style`, `bootstack.events`, `bootstack.dialogs`, …) — is now **frozen**
under Semantic Versioning. Breaking changes to it will not land before 1.0 except
as documented, versioned migrations.

### Highlights

- **Applications and windows** — `App`, `Window`, and two navigation shells:
  `AppShell` (single sidebar) and `Workbench` (two-tier rail + workspaces), plus
  a borderless `Splash` intro screen. Undecorated windows auto-inject a draggable
  titlebar and border.
- **A full widget catalog** — layout (`Row`/`Column`/`Grid`/`Card`/`ScrollView`/
  `SplitView`/`Accordion`), inputs (`TextField`/`NumberField`/`DateField`/
  `TextArea`/`CodeEditor`/`Slider`/…), selection (`Checkbox`/`Switch`/`Select`/
  `Calendar`/…), data display (`DataTable`/`Tree`/`ListView`/`Label`/`Badge`/
  `Gauge`/…), media (`Picture`/`Gallery`/`Carousel`/`Avatar`/`Chart`), navigation
  (`Tabs`/`PageStack`), and overlays (`Tooltip`/`toast`/`Notification`/`Snackbar`).
- **Reactive state** — `Signal` for two-way widget binding; a typed event system
  (`on_change()`/`on_click()`/… returning cancelable `Subscription`s or composable
  `Stream`s); reactive `Form.valid`/`Form.errors`.
- **Theming** — light/dark themes, `set_theme`/`toggle_theme`, `ThemeToggle`,
  system-appearance following, and a public `bootstack.style` API.
- **Data** — `bootstack.data` source protocol (memory/SQLite/file-backed) with a
  filtering DSL (`col`/`any_of`/`all_of`), a non-scalar data bag carried across
  `Tree`/`DataTable`/`ListView`, and large-file streaming.
- **Dialogs** — verbs (`alert`/`confirm`/`ask_*`) at the top level plus dialog
  classes in `bootstack.dialogs` (`Dialog`/`FormDialog`/…).
- **Tooling** — a `bootstack` CLI (`start`/`run`/`add`/`doctor`/`appicon`/…) and
  application packaging.

### Provisional (excluded from the freeze)

- **`bootstack.dev`** — the hot-reload workflow (`reloadable`, `is_dev_mode`, and
  the `bootstack dev` command) is **experimental**. Its surface is carved out of
  the 0.1.0 freeze and may change before a later release.

### Migrating from the `0.1.0aN` alpha series

Pre-1.0 alphas were never a stable contract; this summarizes the notable breaks
for anyone who tracked an alpha. (If you are installing bootstack for the first
time, you can ignore this section.)

#### Renamed

- Layout: `HStack` → `Row`, `VStack` → `Column`, `Separator` → `Divider`; added
  `Spacer`. The layout vocabulary moved to screen-axis terms — `fill`/`expand`/
  `anchor`/`sticky` are replaced by `horizontal`/`vertical`/`grow` with edge-name
  values (`left`/`center`/`right`/`stretch`). The legacy kwargs now **raise**.
- `Table` → `DataTable` (and decoupled from any specific data source).
- `Toolbar` → `CommandBar` for the app-level bar (`app.commandbar`); `app.menu` →
  `app.menubar`; the standalone `bs.MenuBar` was removed in favor of `app.menubar`.
- `Signal.subscribe()` now returns a cancelable handle (was a string token).
- Selection: per-widget `get_selected()` / `selected_rows` / `selected_nodes` were
  unified into a single polymorphic `.selection` accessor across
  `ListView`/`DataTable`/`Tree`.
- Navigation: the single `AppShell` was split into `AppShell` (single sidebar) and
  `Workbench` (two-tier workspaces); nav providers became `page_nav()` / `list_nav()`
  / `tree_nav()` / `custom_nav()` (the old `panel()` is now `custom_nav()`).

#### Removed / moved

- **`AppSettings` and `settings=`** were removed. All former settings are now flat
  `App(...)` / `AppShell(...)` keyword arguments (`theme`, `locale`,
  `remember_window_state`, …), with symmetric `app.*` properties. Passing
  `settings=` raises `TypeError`.
- **Top-level namespace curated** to the compose surface only. Types you reference
  to *configure* behavior moved to submodules — e.g. `Theme`/`get_theme_color`
  (`bootstack.style`), `col`/`SqliteDataSource` (`bootstack.data`),
  `ValidationRule` (`bootstack.validation`), `Event`/`Subscription`
  (`bootstack.events`), `AccentToken` (`bootstack.types`). Dialog **classes**
  (`Dialog`/`FormDialog`/…) moved to `bootstack.dialogs`; the dialog **verbs**
  (`alert`/`confirm`/`ask_*`) stay top-level.
- **`Toast`** was split into `toast()` (function), `Notification`, `Snackbar`, and
  `snackbar()`.
- `MessageCatalog`, `IntlFormatter`, `get_current_app`, and `Image` were demoted to
  internal (import widgets/icons via the public `bootstack.images` API).
- `Scale` and the `VariantToken` type were removed.

#### Changed (behavior)

- `TimeField` now starts **empty** (it previously defaulted to the current time,
  which silently defeated `required=True`).
- Field validation runs against the field's **typed value**; rules are type-aware
  (a new `range` rule for number/date/time bounds), and `field.valid` / `field.error`
  are reactive `Signal`s.
- `Toolbar.add_widget` / `StatusBar.add_widget` are now class-based
  (`add_widget(WidgetClass, **kwargs)`).

[0.1.2]: https://github.com/israel-dryer/bootstack/releases/tag/v0.1.2
[0.1.1]: https://github.com/israel-dryer/bootstack/releases/tag/v0.1.1
[0.1.0]: https://github.com/israel-dryer/bootstack/releases/tag/v0.1.0
