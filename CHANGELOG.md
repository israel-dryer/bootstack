# Changelog

All notable changes to bootstack are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and from 0.1.0 onward the project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- release-notes-start -->

## [Unreleased]

### Fixed

- **Typing a lowercase `b` no longer collapses an `AppShell` sidebar.** The sidebar toggle is documented as Ctrl-B (Cmd-B on macOS), but off macOS it also fired on a bare `b` typed into any field — including a `TextField`, `PasswordField`, `TextArea` or `CodeEditor` — on a machine with NumLock switched on. Windows reports NumLock using the same modifier bit that the shortcut's macOS half was registered under, so an unmodified keystroke matched it. The macOS shortcut is now registered only on macOS. An uppercase `B` was never affected, which is what made the behavior look intermittent. (#403)

- **A disabled or read-only number field no longer suppresses other handlers for the same event.** Its internal increment and decrement handlers declined to step the value by returning the toolkit's "stop the remaining handlers" signal, which since 0.2.0 is honored — so dispatching an increment on a non-interactive field silently dropped every handler after it. The field still refuses to step; it no longer speaks for anyone else. (#401)

- **A window's transparency setup no longer keeps re-running.** On X11, alpha is applied once the window becomes visible and the binding that does it is meant to remove itself afterward. It was removing nothing, so it re-applied on every later visibility change. (#398)

- **A dialog result now reaches the callbacks waiting for it, and unsubscribing removes the right handler.** The internal dialog helpers worked out which widget to act on separately at each step. A dialog's window does not exist until it is shown and is gone once it closes, so subscribing before and cancelling after resolved to two different widgets and the cancellation quietly did nothing — and the result itself was announced on the window that had just been dismissed, where nothing could receive it and the resulting error was discarded. Announcing and listening now share one target that outlives the dialog, and the binder returns a `Subscription` that remembers what it bound to. (#397)

- **A cancellation that fails no longer reports success.** `Subscription.cancelled` became `True` even when the underlying removal raised, so a subscription that was still delivering events described itself as cancelled. Relatedly, an internal removal that failed partway could leave a handler bound while reporting that it had been removed, or strand the resources behind one that had. (#400)

- **An unbind that matches nothing is now reported under `BOOTSTACK_DEBUG`.** Declining to release resources it cannot prove are unused is the safe behavior, but it was silent, so the drift that caused it was invisible. (#399)

## [0.2.0] — form and field correctness

This is the first minor release since `0.1.0`, and it carries one change that is not backward compatible: an argument naming a behavior mode now raises on a value outside its documented set, where it used to degrade quietly. See **Changed**.

### Added

- **`InvalidChoiceError`** in `bootstack.errors`, raised when an argument with a closed set of values is given something outside it. It is both a `BootstackError` and a `ValueError`, so either one catches it. (#381)

### Changed

- **A misspelled mode argument now tells you, instead of quietly doing something else.** Arguments that name a behavior mode — `selection_mode`, `sorting_mode`, `paging_mode`, `scrollbars`, `scroll_direction`, `scrollbar_visibility`, and the `mode` on `ToggleGroup` and `PathField` — are read by comparing against one value, so a near miss such as `selection_mode="multiple"` used to switch multi-select off without a word. Passing a value outside the documented set now raises `InvalidChoiceError` naming the value and listing what is accepted. Covers `DataTable`, `ListView`, `Tree`, `Gallery`, `Calendar`, `DateField`, `ToggleGroup`, `PathField`, `ScrollView`, `TextArea`, and `CodeEditor`. (#381)

- **A field stretched taller than it needs now keeps its entry under its label.** Where a field shares a grid row or a `'stretch'` cross axis with a taller widget, the extra height used to be inserted *between* the label and the input, leaving the input floating below its own caption; it now collects beneath the field instead. Affects layouts that pair a field with something taller, such as a `bs.Grid` row holding a field beside a multi-line `TextArea`. (#394)

### Fixed

- **Cancelling one subscription no longer silences the others.** Calling `cancel()` on a `Subscription` — or letting one fall out of a `with` block — stopped every *other* handler listening to that same event on that widget, with nothing raised to show for it. Two `on_click` handlers, cancel the first, and neither ran again. It affected every bootstack event, and so a wide range of behavior that unsubscribes as part of ordinary work: dialogs returning a result, field validation, meters, tab views, calendars, accordions, expanders, page stacks, and the theme toggle. Cancelling now removes exactly the one handler it was asked to. That holds in the cases hardest to get right too: a handler that cancels itself, a handler that cancels another handler while the same event is being delivered, and a replacement handler registered immediately after a cancellation. (#392)

- **Adding a validation rule no longer misaligns a row of fields.** A field reserves space for its message as soon as it has a rule, and the fields without one sat about nine pixels lower — both inside a `Form` and in a hand-built `Row`. Two separate causes: the entry row absorbed the extra height a form cell gave the field and centered itself in it, and a row centered the shorter fields against their taller neighbors. Input fields — including `Select` — now align to the top of a row on their own, so a row of them lines up whether or not each one is validated. This applies to every container that lays out as a row (`Row`, `Card`, `GroupBox`, `Expander`, `Tabs`, `PageStack`, `SplitView` and an AppShell page), not just `Row`. Passing `vertical_items` yourself still applies to every child, fields included. (#394)

- **Choosing a date from the calendar reports the change.** The picker set the field but announced nothing, so a bound `Signal` kept its old date, an `on_change` handler never ran, and a `Form` did not register the edit — while typing the same date and pressing Return worked. Picking now behaves like any other commit. Date ranges were already correct. (#388)

- **A date field can be cleared.** Setting `value` to `None` — and the field's own `clear()` method, which does exactly that — silently left the previous date in place, on screen and in `form.get()`. Clearing now works through every path, including `Form.set({key: None})`. The same no-op affected `None` on the other entry-backed fields (`TextField`, `NumberField`, `PasswordField`, `PathField`, `SpinnerField`), which reached empty only when given `""`; `None` and `""` now agree. (#387)

- **`Form.set()` writes only the fields you name.** It walked every field and blanked the ones absent from the dictionary — harmless only because blanking was itself broken. A partial update such as `form.set({'date': value})` now leaves the other fields, and the rest of the form data, untouched. (#387)

## [0.1.8] — macOS sizing on Tcl/Tk 9

### Fixed

- **The interface is sized correctly on macOS with Tcl/Tk 9.** Tk 9 changed
  the resolution macOS reports, and bootstack read that as a high-density
  display — so on a Homebrew or conda Python, or any build linked against
  Tk 9, the whole interface rendered about a third too large. Text, icons,
  padding, and control sizes are all restored to their intended size, and
  now match Tk 8.6 exactly. Windows and Linux are unaffected. (#375)

## [0.1.7] — Tcl/Tk 9 scroll support

### Fixed

- **Scrolling works again on Tcl/Tk 9.** A trackpad, Magic Mouse, or Magic
  Trackpad reports precise scroll deltas, which Tk 9 delivers as a different
  event than a mouse wheel. Every scrolling widget listened only for the
  wheel, so on a Mac running Tk 9 — a Homebrew or conda Python, or any build
  linked against Tk 9 — scrolling did nothing at all in `ScrollView`,
  `ListView`, `Tree`, `TextArea`, `CodeEditor`, `Gallery`, and the `Tabs`
  strip. Reported against Python 3.14.6 with Tcl/Tk 9.0.3; the same code runs
  correctly on Python 3.13 only because it ships Tk 8.6. (#372)
- **A wheel notch scrolls by one step on Tk 9, not by a hundred and twenty.**
  Tk 9 normalized wheel deltas across platforms; on macOS the old reading
  scrolled a full view per notch.
- **Wheel scrolling works on Linux with Tk 9.** Tk 9 stopped delivering the
  X11 wheel buttons to applications, and the affected widgets listened for
  nothing else there.
- **A wheel notch scrolls a `ScrollView` consistently across platforms.** On
  Linux one notch moved the view ten times as far as it did elsewhere.
- **A widget detached across a theme change is recolored when you attach it
  back.** Widgets that paint themselves — charts, gauges, and the other
  canvas-drawn widgets — skip a theme change while they are off screen and
  repaint when they next become visible. Returning one with `attach()` was not
  treated as becoming visible, so a chart hidden with `detach()` across a theme
  toggle came back with the old palette and kept it until something else forced
  a repaint. Showing a page or expanding an accordion section already worked.

## [0.1.6] — form, field, and validation fixes

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

[0.2.0]: https://github.com/israel-dryer/bootstack/releases/tag/v0.2.0
[0.1.8]: https://github.com/israel-dryer/bootstack/releases/tag/v0.1.8
[0.1.7]: https://github.com/israel-dryer/bootstack/releases/tag/v0.1.7
[0.1.6]: https://github.com/israel-dryer/bootstack/releases/tag/v0.1.6
[0.1.5]: https://github.com/israel-dryer/bootstack/releases/tag/v0.1.5
[0.1.4]: https://github.com/israel-dryer/bootstack/releases/tag/v0.1.4
[0.1.3]: https://github.com/israel-dryer/bootstack/releases/tag/v0.1.3
[0.1.2]: https://github.com/israel-dryer/bootstack/releases/tag/v0.1.2
[0.1.1]: https://github.com/israel-dryer/bootstack/releases/tag/v0.1.1
[0.1.0]: https://github.com/israel-dryer/bootstack/releases/tag/v0.1.0
