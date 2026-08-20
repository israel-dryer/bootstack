# Changelog

All notable changes to bootstack are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and from 0.1.0 onward the project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- release-notes-start -->

## [Unreleased]

### Fixed

- **`DataTable`'s `context_menus` option now works.** It was documented and shown in the widget guide but had no effect: every table offered both right-click menus whatever you asked for, so `context_menus="none"` still opened the column-header menu and the row menu. The option is now honored as documented — `'all'` (the default, and what every table has always done), `'headers'` or `'rows'` for one menu only, `'none'` for neither — and a misspelled value is reported rather than ignored. Tables that do not pass the option are unaffected. `on_row_right_click` fires no matter which menus you turn off: the option chooses which menus the table offers, not whether a right-click reaches your code. ([#456](https://github.com/israel-dryer/bootstack/issues/456))
- **A `Select` bound to a `Signal` now tracks the selection, not the text on screen.** Seeding the signal with an option's value displayed that raw value instead of the option's label, and setting it later moved the displayed text without moving the selection — so the field showed one option while `value` and `selection` still reported the previous one, and no change event fired. That second half applied to plain string options too, and it did not correct itself. The signal now carries the option's value in both directions, matching `value=` and the `signal=` on `NumberField`, `DateField` and `TimeField`. Two things to check when you upgrade — what a `Select` writes into its signal changes from the option's label to its value, and passing `textsignal=` to a `Select` now raises instead of being silently discarded. `SelectButton` is unchanged and still binds the label shown for an option. ([#458](https://github.com/israel-dryer/bootstack/issues/458))

## [0.3.2] — Read-only select fields

### Fixed

- A read-only `Select` can no longer be changed. `read_only=True` was accepted and then ignored: the dropdown arrow dimmed, so the field looked locked, while clicking its text area still opened the option list and let a new value be chosen. The list now stays shut from both the arrow and the field, and `read_only` survives being combined with `searchable` or `allow_custom_values`, which used to cancel it outright. Reading `select.read_only` now reports what you set — it previously answered `True` for every `Select`, whether or not one had been asked for. `TimeField` offers the same kind of dropdown and had the same defect on its own `read_only`, both when passed to the constructor and when set afterwards; a locked time field is now genuinely locked, and its time list stays shut. ([#453](https://github.com/israel-dryer/bootstack/issues/453))

## [0.3.1] — Dialog keyboard and modality

### Fixed

- **Pressing Enter in a dialog's multi-line field no longer submits the dialog.** A dialog binds Enter so its default button can be pressed from an input field — which is what lets `ask_string()` be finished from the keyboard — and that binding stood down only for buttons. A `TextArea` answers Enter too, by inserting a newline, so the newline went in and the dialog closed on top of it: you were typing a paragraph and the dialog shut under you. Enter is now treated as text wherever it means text, and as a command everywhere else, so a `TextArea` or `CodeEditor` in a dialog body behaves the way it does anywhere else. A read-only one is unaffected: nothing there consumes the key, so Enter still presses the default button. The keypad's Enter key is handled on the same terms rather than assumed to match the main one: on the systems that report it separately, a multi-line field does not answer it at all, so it presses the default button rather than doing nothing at all. (#441)

- **A dialog no longer loses its modality when a second dialog closes on top of it.** The inner dialog took over the block on the rest of the app and then released it entirely when it closed, instead of handing it back. The outer dialog stayed on screen and still blocked the code that opened it, while you could click straight past it into the main window and drive the app underneath — modal in appearance only. This was reachable from ordinary code: any dialog button command that shows an alert, a confirmation, or a second dialog. Nesting now restores the previous dialog's modality at every depth, and closing the outermost one leaves nothing blocked. A window opened with `modal="app"` keeps the wider block it was created with, rather than coming back narrowed to this application alone. (#440)

- **A dialog's default button now actually receives keyboard focus.** It is documented as focused and triggered by Enter, but only the second half was true: the request was made while the window was still hidden, where it is silently ignored, so a dialog opened with nothing focused. Keyboard users got no focus ring and a Tab order that started from nowhere. The same defect meant the prompts that put you straight into a field — `ask_string()`, `ask_integer()`, `ask_float()` and `ask_item()` — did not focus their input either, so you could not type into one without clicking it first; those now focus their field, which takes precedence over the default button. `ask_date()` is unchanged, having no field to focus: its calendar still opens with focus on the window itself. (#439)

- **The error raised for an outdated layout option now names options that exist.** Passing `fill=`, `expand=`, `anchor=`, `sticky=` or `side=` to a child of any layout container correctly raises, but the message recommended `align_self=` and `justify_self=`, which were renamed before release and never shipped. Following the advice produced a second, lower-level error naming an option you had never written. The message now names real options, and which ones it names depends on how the container places the child. A `Row` or `Column` child is pointed at `grow=` for claiming leftover space along the stacking axis and `horizontal=`/`vertical=` for aligning or stretching across it. A grid cell — a `Grid` child, a page or a pane, or a child of any container built with `layout="grid"` — is pointed at `horizontal=`/`vertical=` and at weighting the row or column on the container, because `grow=` is not honored there: recommending it would have replaced advice that raised with advice that quietly did nothing. Both forms list the values each option takes. (#426)

## [0.3.0] — Screen capture and dialog results

### Added

- **Every widget can now save a picture of itself.** `capture(path)` writes the area a widget occupies on screen to an image file and returns the path it wrote — call it on the app for the whole window, or on any single widget for just that part of it. The file extension picks the format, so `.png`, `.jpg`, and `.pdf` all work, and missing folders in the path are created for you. Pair it with `ask_save_file()` to let the user choose where the picture goes. The window is raised before the picture is taken, and an always-on-top setting the window already had is left exactly as it was found. Capturing a hidden or detached widget raises an error rather than silently saving whatever happened to be behind it. (#427)

### Changed

- **A dialog button's command can now refuse its own press by returning `False`.** The dialog then records no result and stays open, where previously the return value was ignored and the press completed regardless — recording the button's result and closing the window even when the command had decided to do nothing. This is how a button rejects the input it was given: validate in the command, return `False` to keep the dialog open, return anything else to let it close. If you have a button command that returns `False` for some other reason, it will now suppress that button rather than being ignored; return `None` to keep the previous behavior. `FormDialog` already treated `False` this way for the commands you give it, so this brings the underlying `Dialog` in line with it — and `Form`'s own button row, the other place these specifications are used, honors it too, where it previously recorded a result for a press its command had just declined. A form stays on screen after a press, so a refused press there also clears any result an earlier press recorded: `form.result` is the most recent press that completed, never an older one made against data you have since edited. (#437)

### Removed

- **`DialogButton.closes` is gone.** It was meant to say whether a button dismisses the dialog, but it could not be honored: `FormDialog` set the same flag internally on every non-cancel button — to stop the window closing before the form had been validated — and could not then tell its own value apart from one you had set. So the same declaration did three different things depending on the button's role and whether it had a command, and both uses of it inside bootstack were really reaching for something else. What they wanted was a way to say "not this press" rather than "not this button", which is what returning `False` from the command now does — per press, and without the button having to close the window itself. If you passed `closes=False` to keep a dialog open after a press, return `False` from that button's command instead. A footer button that never dismisses the dialog is not really a footer button; put it in the dialog body, where it needs no flag at all. (#438)

### Fixed

- **Deleting a record from a `DataTable` no longer requires the record to be valid.** The dialog validated the form for every button except Cancel, so a Delete button — which never reads the form — was refused whenever the record failed validation, and pressing it simply did nothing. This hit exactly the records most likely to need deleting: validation happens in the editors, which only exist while the dialog is open, so it has no say over what is already in the table. A record with a required field left blank, or one missing that field entirely, is accepted by `DataTable(rows=...)` without complaint and then cannot be deleted. The same applied to any custom action button you added to a `FormDialog`, provided it carried a `result=` of its own — which is what marks a button as an action rather than a submission. Validation now runs only for the buttons that submit the form: the standard `'ok'`, `'submit'` and `'save'`, plus any button with no `result=`, whose result *is* the entered data. (#437)

- **Cancelling a `FormDialog` after a refused button press no longer performs that press.** A press the dialog declined still recorded its button's result, and Cancel could not clear it — so backing out of the dialog handed the caller the refused button's result as though it had been pressed successfully. On a `DataTable` this meant that pressing Delete on an invalid record (which did nothing, per the fix above), and then cancelling because the form could not be satisfied, **deleted the record** at the moment you asked for nothing. A refused press now leaves nothing behind. (#437)

- **The keypad Enter key now submits a dialog you are typing in.** In `ask_string`, `ask_integer` and any other dialog that puts the cursor straight into a field, only the main Enter key finished the dialog — the keypad one did nothing, so a value typed on the number pad had to be committed with the other hand or with the mouse. Both keys now submit, through the same command and the same refusal path as a click. Once you have clicked or tabbed to a button, that button answers both keys itself. (#437)

- **Enter now presses the button you tabbed to, and nothing else.** A dialog bound Enter to its default button for every key press in the window, including one already delivered to a button — buttons answer Enter themselves — so one press ran two commands: the focused button's, then the default button's on top of it. It only surfaced on a dialog that stayed open after a press, since otherwise the closing window took the second command with it, which meant a footer button declared `closes=False`. That declaration is gone in this release, and returning `False` from a command replaces it, so the same press would have started refusing and running the default button instead. Enter on a focused button now presses that button alone; with the cursor in a field it still presses the default button. (#437)

- **A `FormDialog` no longer modifies the `DialogButton` you pass it.** It rewrote `command` directly on your object, so a button specification reused across two dialogs came back altered — and the second dialog then wrapped the first one's wrapper, leaving the press running against a dialog that was already gone. It works on its own copy now. (#438)

- **`FormDialog.result` now gives you the values you put in, not the text shown on screen.** A `select` built from `[('One', 1), ('Two', 2)]` returned `'One'` where a plain `Select` and the same field in a `Form` both returned `1` — so the three disagreed, and the dialog was the odd one out. It affected every editor whose displayed text differs from its underlying value, not only `select`: the result was read back after the dialog had already closed, at which point the only thing left to read was the on-screen text, and that arrives as a string whatever the value's real type was. A date field, for instance, handed back its formatted text rather than a date. The entries are now taken when you press the button, while the form is still on screen, so what you get back is what was entered — same values, same types, matching `Form` and `Select`. Cancelling still returns `None`, and re-using a dialog no longer reports the previous run's entries — including for a button declared with the `'cancel'` role but an `'ok'` result, the one combination where the dialog took no entries yet still tried to hand some back. (#428)

## [0.2.3] — Import without IDLE

### Fixed

- **`import bootstack` no longer requires `idlelib`, so it works on Linux builds of Python that ship without IDLE.** `idlelib` is part of the standard library, but Debian and Ubuntu package IDLE separately — the way they package Tkinter separately — and it is not installed by default. bootstack imported `WidgetRedirector` from it at module scope, in code the top-level package reaches unconditionally, so on those systems `import bootstack` raised `ModuleNotFoundError: No module named 'idlelib'` and nothing in the framework could be used at all. Since `idlelib` is standard library it is not on PyPI and could not be declared as a dependency, so there was no way to fix this by installing something. That one class is now part of bootstack, alongside the other pieces of the code editor already adapted from IDLE, and nothing in the framework imports `idlelib` any more. Windows and macOS were never affected: the python.org installers bundle IDLE. (#430)

## [0.2.2] — DataTable group headers and row events

### Changed

- **On a read-only `DataTable`, the second press of a double-click no longer repeats the first press's action.** Because the double-click event is now bound on every table rather than only on editable ones, the second press is delivered as a double-click instead of as another single click. Two visible consequences, both of which bring read-only tables in line with how editable ones have always behaved: double-clicking a column heading now advances the sort once rather than twice, so it flips direction where it previously came back to where it started; and with `selection_mode="multi"` and selection controls shown, double-clicking a row now leaves it toggled rather than back in its original state. (#417)

- **A double-click also runs your `on_row_click` handler twice — once before `on_row_double_click` and once after.** That has always been true of the click event: a double-click is reported on the second press while a row click is reported on release, so the order is click, double-click, click. What is new is that pairing the two handlers on one table is worth doing at all, since `on_row_double_click` never fired on a read-only table before. Single click selects, double click opens is now the natural thing to write — so if the double delivery matters for your handler, keep the work in `on_row_click` idempotent, or move it to the double-click handler. (#417)

### Fixed

- **Double-clicking a `DataTable` row now fires `on_row_double_click`.** The binding behind the event was installed only when the table was also built with `allow_edit=True`, so on a read-only table — the common case — the event had nothing behind it and the handler never ran, while `on_row_click` and `on_row_right_click` on the same table kept working. That is what made it look like the event itself was broken rather than absent. The event is public API and does not depend on editing, so it is now bound unconditionally; `allow_edit` still controls only whether the built-in edit dialog opens alongside it. (#417)

- **A group header in a grouped `DataTable` no longer fires row events carrying an empty record.** A group header is not a row and carries no record, but `on_row_double_click` and `on_row_right_click` only checked that some tree item was under the pointer, so clicking one emitted a `RowEvent` whose `record` was `{}` and whose `id` was `None` — enough to raise `KeyError` inside a handler doing the documented `e.record["name"]`. The right-click half needed no unusual setup, since right-click menus are on by default, so any grouped table was affected; the double-click half also opened a spurious **New Record** dialog when the table was built with `allow_edit=True`. A group header also stopped being recorded as the row menu's target, which could leave a later menu command pointed at a row that carries no record. `on_row_click` has always ignored group headers; both of the others now match it. (#418, #420)

- **An expanded `DataTable` group header now shows the correct chevron.** Expanding a group with the keyboard, or by double-clicking its header, left the group open while its chevron still pointed at collapsed, so the arrow and the group disagreed until something else repainted the row. Collapsing was never affected. The chevron is now read after the new state has settled rather than during the change, which also covers the keyboard path that has been wrong since grouped tables gained custom chevrons. (#419)

- **Clicking a `DataTable` group header, or any row on a table showing selection checkboxes, now leaves the keyboard pointed at that row.** Ordinary row clicks were never affected. In those two cases the click toggled the row but did not give the table keyboard focus, so the arrow keys did not continue from what had just been clicked, and a following Space or arrow key did nothing to the table at all. With selection checkboxes that applied to every row, leaving Tab as the only way to start driving the table from the keyboard. (#421)

- **A column separator can be dragged again on a `DataTable` showing selection checkboxes.** Dragging one moved nothing at all there, so those columns could not be resized. The click handling that makes a plain click toggle a row was also stopping clicks that landed between two columns rather than on a row, and that press is what begins the resize drag. It now stops only the clicks it actually handles. (#421)

## [0.2.1] — event and shortcut correctness

### Fixed

- **Typing a lowercase `b` no longer collapses an `AppShell` sidebar.** The sidebar toggle is documented as Ctrl+B (Cmd+B on macOS), but off macOS it also fired on a bare `b` typed into any field — including a `TextField`, `PasswordField`, `TextArea` or `CodeEditor` — on a machine with NumLock switched on. Windows reports NumLock using the same modifier bit that the shortcut's macOS half was registered under, so an unmodified keystroke matched it. The macOS shortcut is now registered only on macOS. An uppercase `B` was never affected, which is what made the behavior look intermittent. (#403)

- **A `Command+` or `Option+` shortcut now binds the key its own menu label promises.** Off macOS these were the last two modifier names left unmapped, so `Shortcut(pattern="Command+S")` produced an accelerator reading *Ctrl+S* beside a binding that listened for something else entirely — and on Windows that something else was satisfied by NumLock, so the shortcut fired on an unmodified `s`. `Option+K` had the same shape. Both now resolve to Ctrl and Alt off macOS, matching what has always been displayed, and keep their own meanings on macOS. This is the same trap as #403, closed once at the shared modifier map rather than at another call site. (#405)

- **`emit()` now reaches the handlers registered with the matching `on_*()`.** On the field widgets — `TextField`, `PasswordField`, `PathField`, `NumberField`, `SpinnerField`, `DateField`, `TimeField`, `Select`, `TextArea`, `CodeEditor` — the text-editing events belong to the entry inside the field, and registering a handler correctly listened there while `emit()` fired on the field's outer frame. So `field.emit("change", data=...)` never reached `field.on_change(...)`, contradicting `emit()`'s own documentation that the two take the same event name. Both now resolve the target through one shared seam, so they cannot disagree. `emit()` is documented more plainly at the same time: it announces the framework's own events, and the names that stand for a real input event instead — `click`, `focus`, `blur`, `submit` — are not a way to notify listeners. (#396)

- **A window's transparency setup no longer keeps re-running.** On X11, alpha is applied once the window becomes visible and the binding that does it is meant to remove itself afterward. It was removing nothing, so it re-applied on every later visibility change. (#398)

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

[0.3.2]: https://github.com/israel-dryer/bootstack/releases/tag/v0.3.2
[0.3.1]: https://github.com/israel-dryer/bootstack/releases/tag/v0.3.1
[0.3.0]: https://github.com/israel-dryer/bootstack/releases/tag/v0.3.0
[0.2.3]: https://github.com/israel-dryer/bootstack/releases/tag/v0.2.3
[0.2.2]: https://github.com/israel-dryer/bootstack/releases/tag/v0.2.2
[0.2.1]: https://github.com/israel-dryer/bootstack/releases/tag/v0.2.1
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
