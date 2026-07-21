# Changelog

All notable changes to bootstack are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and from 0.1.0 onward the project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- release-notes-start -->

## [Unreleased]

### Fixed

- **`tristate` works on a `checkbox` form editor.** `0.1.5` fixed
  `bs.Checkbox(tristate=True)` itself, but a checkbox built by a `Form` (or by
  `DataTable`'s add/edit dialog) still started unchecked: the form supplied an
  explicit `value=False` that overrode the indeterminate default. (#358)
- **`editor_options` may set any of the editor's public keyword arguments.**
  Naming one the form also fills — `label`, `options`, or a boolean editor's
  caption — raised `TypeError: got multiple values for keyword argument`.
  Those options now override the form's default instead of colliding with it.
  A `value` option seeds the editor only when the form's `data` carries
  nothing for that key. (#358)
- **A falsy value no longer disappears from a text field.** `bs.TextField`,
  `bs.PasswordField`, and `bs.PathField` tested the initial value for
  truthiness, so `value=0` rendered an empty field — and in a `Form`, the
  blank was written back over the record's value.
- **A form no longer changes the type of the data it was given.** Values that
  are not text — a `Decimal`, a `date` — keep their type in `form.data`
  instead of being converted to strings at construction.
- **Option dicts aimed at a built widget no longer collide with the
  framework's own arguments.** The same defect appeared in
  `MenuButton(menu_options=)`, `ButtonGroup.add()` / `add_all()`,
  `RadioGroup.add()` / `ToggleGroup.add()`, and `Toolbar` / `StatusBar`
  `add_widget()`. In each, your options now win; the few keys a widget must
  own — where it is parented, how it tracks its selection, the callback that
  emits its events — raise a clear error naming what to use instead.
- **A `ButtonGroup` button given both a caption and an icon renders as both.**
  Supplying the caption as `text` produced an icon-only button with its label
  crammed into zero padding.
- **A required field with a placeholder no longer passes validation while
  empty.** A field showing only its placeholder was treated as though the hint
  had been typed, so `required` reported it valid — and a form with an
  untouched required field validated and submitted.
- **`text` no longer reports the placeholder as content.** A field showing only
  its placeholder returned the hint from `text` while `value` reported empty;
  the two now agree on whether the field holds anything.
- **`required` survives an unrecognized `editor=` name.** An editor name the
  form does not know falls back to a text field, but the `required` rule was
  dropped on the way, so a misspelled editor silently let an empty field
  submit. (#366)
- **A searchable `Select` no longer changes its value when you just look.**
  Opening the drop-down and dismissing it without typing or choosing anything
  replaced the field's value with the first option in the list. (#355)
- **`Select` validation rules run against the selected value, not its label.**
  On a decoupled option list — where an option displays `'United States'` and
  stores `'US'` — every rule saw the label, so a rule checking the value
  rejected valid selections. (#355)
- **A `Decimal` value now respects `value_format`.** It matched none of the
  formatter's numeric branches, so the format was silently ignored: a currency
  field seeded with a `Decimal` displayed the raw number and only started
  formatting once you edited it. `Decimal` is handed to the formatter as-is
  rather than converted, so a value keeps the precision it was given.

### Added

- **`Select.validate()`** — run a select's validation rules on demand, matching
  the other field widgets. `add_validation_rule` already pointed at it. (#355)

### Changed

- **A format rule no longer rejects an empty field.** `email`, `pattern`, and
  `stringLength` describe what a value must look like, not that one must be
  present, so they now pass on an empty field — matching `range`, which
  already behaved this way. Previously a field with no `required=` reported an
  error while untouched and `Form.validate()` refused to submit, leaving no
  way forward but typing into a field the form called optional. **If you used
  a format rule as a presence check — `stringLength(min=1)`, or a pattern that
  cannot match the empty string — add `required` to keep that behavior.**
  `compare` and `custom` are unaffected; both still run on an empty value.
  (#366)
- **A `Select` no longer rejects a value that is not in its option list.**
  Opening an editor on a stored record whose option had since been retired
  raised `ValueError: '…' is not one of the options` — in a `Form`, and in
  `DataTable`'s add/edit dialog, on ordinary data drift. A later programmatic
  write of the same value was silently dropped instead, so one value produced
  two different wrong answers. Such a value is now displayed as given, reads
  back with its own type, and is **not** added to the list, so a user cannot
  pick it. Use a `'custom'` validation rule to report one. `SelectButton`,
  which maps a value to an option's label and has no text entry, still
  rejects. (#355)

## [0.1.5] — boolean control state fixes

### Fixed

- **`Checkbox(tristate=True)` now produces a real indeterminate state.** Setting
  `tristate=True` previously left the checkbox unchecked — the dash indicator
  never rendered and `.value` returned `False` instead of `None`. (#358)
- **`ToggleButton.value` / `.checked` report the correct state.** A toggle built
  with `value=True` (and visually "on") wrongly reported `.checked` as `False`
  and `.value` as `None`. (#359)
- **Non-bool `checked_value` / `unchecked_value` round-trip on `Checkbox` and
  `Switch`.** A string or other custom on/off value (e.g. `checked_value="yes"`)
  was silently coerced to `True` / `False`; `.value` now returns the value you
  set, matching `ToggleButton`.

## [0.1.4] — Select validation fix

### Fixed

- **`add_validation_rule` works on `Select` fields again.** In `0.1.3`, calling
  `form.field(key).add_validation_rule(...)` on a `select` editor — or the same
  method on a standalone `bs.Select` — raised `AttributeError: 'Select' object
  has no attribute 'add_validation_rule'`. This was a regression from the `0.1.3`
  form rework: `field()` now returns the public editor widget, and `bs.Select`
  was the one editor missing the method. It is restored with the same signature
  as the other field widgets, so custom rules with a `message=` and `trigger=`
  work as they did in `0.1.2`. (#356, #357)

## [0.1.3] — form editor options fix

### Fixed

- **Form field editors now accept the editor widget's public option names.** A
  `FieldItem`'s `editor_options` are documented as the editor widget's keyword
  arguments, but the form built the *internal* widgets and forwarded the options
  unchanged — so the public names raised an error
  (`editor_options={"step": 10}` on a `numberfield` failed with
  `unknown option "-step"`; only the internal `increment` worked), and the
  `textarea` editor could not accept `show_border` at all. Editors are now built
  from their public widgets, so `step`, `min_value` / `max_value`,
  `show_steppers`, `show_border`, `mask`, and the slider bounds all work as
  documented — in `Form`, `FormDialog`, and the `DataTable` add/edit dialog. This
  also fixes two latent `textarea` bugs, where a programmatically set value and
  `required` validation were ignored. (#353, #354)

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

[0.1.5]: https://github.com/israel-dryer/bootstack/releases/tag/v0.1.5
[0.1.4]: https://github.com/israel-dryer/bootstack/releases/tag/v0.1.4
[0.1.3]: https://github.com/israel-dryer/bootstack/releases/tag/v0.1.3
[0.1.2]: https://github.com/israel-dryer/bootstack/releases/tag/v0.1.2
[0.1.1]: https://github.com/israel-dryer/bootstack/releases/tag/v0.1.1
[0.1.0]: https://github.com/israel-dryer/bootstack/releases/tag/v0.1.0
