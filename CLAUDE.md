# bootstack — Claude Handoff

## Project overview

bootstack is a batteries-included Python desktop UI framework. It is **not**
advertised as a Tkinter wrapper — the goal is to abstract Tkinter away entirely
so that Tkinter's warts, naming conventions, and legacy API are invisible to the
user. Widget names, arguments, methods, and events are designed for modern Python
and ease of use, not compatibility with the raw tk/ttk surface.

**Design philosophy:** Opinionated and configurable within a reasonable range.
Go from nothing to something fast. The user should never need to `import tkinter`.

**Working directory:** `D:\Development\bootstack`
**Branch strategy:** `feat/*` branches off `main`. PRs go `feat/*` → `main`.

---

## Current initiative — Sphinx docs + public API audit

**Branch:** `feat/docs-api-improvements` (active)

### Docs structure (RESOLVED 2026-06-04, committed b7625f36 + follow-ups)

Top-level sections (pydata horizontal navbar — keep this set SMALL, ~5):
**Getting Started · Tasks · Widgets · Reference · Production**.

- **`docs/widgets/`** — every widget as a flat leaf page. Grouping is done with
  **caption toctrees** in `widgets/index.rst` (one `.. toctree:: :caption: <Group>`
  per group, listing widget pages directly). The 10 old category landing pages
  (`actions.rst`, `inputs.rst`, …) were RETIRED — captions replace them. Curated
  (common-first) order within groups, NOT alphabetical.
- **`docs/reference/`** — framework primitives: theming, typography, signals,
  events, validation, data-sources, shortcuts, scheduling. Flat (no captions).
- **`docs/api/` and `docs/deeper/` are GONE.** typography moved into reference/.
- `show_nav_level: 2` (conf.py) renders the caption groups as sidebar headers.
- Sections are **flat by default**; add caption toctrees only when a section
  needs internal organization (e.g. if Common Tasks grows).
- Do NOT promote widget groups to top-level — ~14 navbar items overflow pydata.

**Reference page pattern** (distinct from widgets — non-visual, NO screenshots):
prose intro → task-ordered usage sections (code blocks) → See also → curated
`autoclass` → Full Example `literalinclude`. Curate the documented surface with a
denylist `:exclude-members:` mirroring the widget `.tk` exclusion, plus
`:undoc-members:` so new public members auto-appear (lower-maintenance than an
allowlist). **Exemplar: `docs/reference/signals.rst`** (+ `docs/examples/signals.py`,
run-verified). The other 7 reference pages were MOVED but NOT yet reworked to this
pattern — that is the main remaining work (see Next session).

**No Tkinter in docs or docstrings** — no `tk.*` types or Tkinter terms unless
strictly necessary; don't feature escape-hatch interop. A full docstring scrub of
`src/` is still pending; `signals/signal.py` is done.

### Status

**Done** (wrapper ✓ · doc page ✓ · example ✓ · screenshots ✓):
- Actions: Button, ButtonGroup
- Inputs: TextField, PasswordField, NumberField, Slider, RangeSlider,
  PathField, SpinnerField, TextArea, CodeEditor, DateField, TimeField
- Selection: Checkbox, Select, Switch, ToggleButton, RadioGroup, ToggleGroup,
  SelectButton, Calendar
- Data Display: Label, Badge, ProgressBar, Gauge, ListView
- Layout: Separator, Card, GroupBox, VStack, HStack, Grid, Accordion,
  ScrollView, SplitView
- Menus and Toolbars: Toolbar, MenuButton, ContextMenu
- Navigation: PageStack, Tabs, SideNav, AppShell
- Overlays: Tooltip, Toast
- Dialogs: 7 pages (message, input, color, font, filter, dialog, formdialog)
- Forms

**Pending:**
- Data Display: Tree, Table (deferred — too complex for this pass)
- Actions: DropdownButton is internal (public face is MenuButton — no separate page needed)

### Cross-cutting wrapper improvements (this + prior sessions)
- `commit()` and `set_cursor()` removed from all field widgets (TextField,
  PasswordField, NumberField, PathField, SpinnerField) — internal plumbing
- `placeholder` property removed from TextField, PasswordField, PathField —
  constructor-only concern
- `trigger=` param removed from `validate()` on all 8 field wrappers —
  internal routing concern, callers are always doing a manual check
- All field wrappers now have full event parity: 8 shorthands, typed tokens
- `TextArea.width=` added (was missing; internal hardcoded default)
- `CodeEditor.height=` added (was hardcoded to 20; now configurable)
- `LineNumbers` sidebar height bug fixed — no longer overrides `height=`
- `TextArea` critical bugs fixed: `<<Change>>` vs `<<Changed>>` event name,
  undefined `inner_sequences` in `on()` (crash), `text_signal` → `textsignal`
- `CodeEditor`: `text_signal` → `textsignal`, removed `disabled` alias,
  cleaned up inline imports, added `signal` property
- DateField calendar picker right-aligns to button side; `position_anchored`
  now uses actual rendered size (`winfo_width`) for widget anchors
- **SideNav compact mode**: selection indicator bar now matches fill color
  (invisible) instead of accent color. `SideNavItem.set_compact()` rebuilds
  the frame style via `configure_style_options(icon_only=) + rebuild_style()`.
- **`AppShell.on_page_change`** bug fixed: was binding `<<PageChanged>>`
  (never fired) — corrected to `<<PageChange>>`.
- **`Tabs.item()` / `items()`** bug fixed: were calling non-existent
  `TabView.item/items` — corrected to `tab()` / `tabs()`.
- **`TabView`** now forwards `<<TabAdd>>` and `<<TabClose>>` to itself so
  the public wrapper needs no private `_tabs` access for event routing.
- **`PublicWidgetBase.emit`** simplified: now wraps `event_generate(data=data)`
  directly — `_bs_emit_data` side-channel removed.
- **`ContextMenu`**: `ValueError` on unknown `trigger=`; `add_items()` type
  hint broadened to `list[ContextMenuItem | dict[str, Any]]`.
- **`AppShell.mainloop`** alias removed from public API.
- **`Tabs.items()` / `PageStack.items()`** return type fixed to `tuple[Any, ...]`.

### Next session (docs + API audit initiative)

**PRIORITY — finish the Reference section.** Apply the signals exemplar
(`docs/reference/signals.rst`) to the other 7 reference pages: theming,
typography, events, validation, data-sources, shortcuts, scheduling. For EACH
page: (1) audit that class's public API — docs are the forcing function, so
surface bugs / inconsistencies / code-smell and either fix or log them; (2)
curate the documented surface via autoclass denylist exclusion; (3) write prose
+ a runnable `docs/examples/<topic>.py` and verify it runs; (4) wire into
`reference/index.rst`. theming/typography may warrant a screenshot (visual).
Follow the established audit-and-curate convention (curation = visibility
discipline for plain/composition classes; twin public wrapper only when
inheritance forces it, as with widgets).

**Signal API — DECIDED this session:** `signal()` is the single getter, `.set()`
writes, `.get()` is deprecated (doc-excluded now, to be removed in the runtime
pass). Possible future add: `.update(fn)`. Do NOT adopt a callable-setter
`signal(x)` (analysis in memory).

**Other pending:**
1. **Improve index/landing pages before release** — root `index.rst`,
   `widgets/index.rst`, `reference/index.rst`, and the section indexes are bare
   (intro + toctree). Add real landing content / orientation / gallery.
2. **Signal runtime-cleanup pass** — 6 audit findings (memory
   `project_signal_api_audit_findings`). Notably: remove `.get()` AND the
   `__getattr__` variable proxy together (the proxy keeps `.get()` reachable);
   `set()` rejects numeric widening (`Signal(0.0).set(5)` raises); silent
   exception swallow in `subscribe(immediate=)`. Behavioral — deliberate pass.
3. **localization / windowing** — write as `tasks/` how-tos (were deleted as
   empty `deeper/` stubs this session).
4. **Screenshots still pending:** Tooltip/Toast (per-scene SCENES dict), 7 Dialog
   pages (per-scene + dialog hero pattern).
5. **AppShell deferred improvements** (dedicated follow-on pass):
   - `nav_pane_width=` not wired through to `SideNav(pane_width=...)`
   - Nav item density/font hardcoded in SideNav style builder
   - `toolbar`/`nav` properties expose internals instead of public wrappers
   - Group UX: active-child header highlight + child indentation missing
   - `add_footer_area` / non-page widgets in nav footer (no API)
   - Past-tense event names pending rename: `SideNav.on_pane_toggled`,
     `SideNav.on_display_mode_changed`, `ListView.on_selection_changed`,
     `Calendar.on_date_selected`

---

## Widget documentation pattern (established — follow exactly)

1. **Audit** — Explore agent comparing public wrapper vs `_impl/` internals.
2. **Fix wrapper** — typed params (`AccentToken`, `VariantToken`, `WidgetDensity`);
   `@overload` event shorthands; no low-level color kwargs; layout via `**kwargs`
   + `_split_layout_kwargs`; catch-all must be `**kwargs` not `**extra_kw`.
3. **`docs/widgets/<widget>.rst`** (NOTE: was `docs/api/` — moved 2026-06-04) —
   intro sentence → hero screenshot → Usage sections (code block then screenshot)
   → Widget sizing include → See also → API autoclass → Full Example
   literalinclude. No intro code block above hero.
4. **`docs/examples/<widget>.py`** — runnable visual-states-only demo. No
   `app.tk.after()`, no screenshot scaffolding, no `fill="x"` in RST snippets.
5. **`docs/screenshots/<widget>.py`** — SCENES dict. Each scene: own `bs.App`,
   tight `size=(W,H)`, `HStack(fill="x")` for button rows to avoid centering
   offset, `app.run()`. Hero for button/action widgets: single representative
   state with menu/popdown open if applicable.
6. **Screenshots:** `py -3.12 docs/scripts/take_screenshots.py <widget> [--scene X] [--light]`
   Outputs: `docs/_static/examples/<widget>-<scene>-light/dark.png`
7. **Wire** into the matching `:caption:` toctree in `docs/widgets/index.rst`
   (category landing pages are retired — captions group the widgets now).
8. **Commit** on `feat/docs-api-improvements`.

### Screenshot image pattern

```rst
.. image:: /_static/examples/<widget>-<scene>-light.png
   :class: bs-screenshot-light
   :alt: <Widget> <scene> — light theme

.. image:: /_static/examples/<widget>-<scene>-dark.png
   :class: bs-screenshot-dark
   :alt: <Widget> <scene> — dark theme
```

Hero uses `-hero-light/dark.png`. Dialogs add `bs-dialog-screenshot` to the class
(e.g. `:class: bs-screenshot-light bs-dialog-screenshot`).
Margin/radius owned by `docs/_static/custom.css` — no inline styles.

### Widget sizing section pattern

```rst
Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst
```

Path is file-relative from `docs/api/`. Omit from dialog pages.

---

## Gotchas

### Layout and wrappers
- **Self-placement via `**kwargs`** — `fill`, `expand`, `anchor`, `row`, `column` etc.
  are NOT explicit params. Route through `self._split_layout_kwargs(kwargs)`.
- **`**kwargs` not `**extra_kw`** — catch-all must be named `**kwargs` throughout.
- **`**kwargs` override protection** — when merging user kwargs into `internal_kwargs`,
  filter out reserved keys so explicit constructor params can't be silently overridden.
  Pattern: `_RESERVED_INTERNAL_KEYS = frozenset({...})` then skip collisions.
- **`margin_x=` / `margin_y=`** — axis-specific external spacing. Never `padx=`/`pady=`.
- **`.. include::` path is file-relative** — from `docs/api/`, use `../shared/widget-sizing.rst`.

### Screenshots
- **HStack centering** — App's VStack centers children. For button-row scenes, wrap in
  `HStack(fill="x")` so buttons are left-aligned, not centered with dead space on the left.
- **No `size=` by default** — omit `size=` from `bs.App` in screenshot scenes unless there
  is a specific reason (popdown/dropdown needs room to render inside the capture bbox). Let
  the window auto-fit its content. For input/field/slider rows use `minsize=(720, 1)` to
  enforce a minimum width without locking height. Never add `size=` just to "feel right".
- **Popdown menus in screenshots** — runner sets app `topmost=True` at t=800ms, grabs at
  t=950ms. Call `mb.show_menu()` at t=850ms (after topmost set, before grab). Size the
  app window tall enough to contain the menu within its capture bbox — the menu Toplevel
  is captured via `ImageGrab.grab(bbox=app_region)` which is a screen grab, not a window
  grab.
- **`_ToplevelContextMenu` topmost** — `show()` now sets `-topmost True` on the
  overrideredirect Toplevel so it appears above a parent with `-topmost True`.
- **SelectBox popup topmost** — `_create_popup_toplevel` sets `-topmost True` so the
  popup appears above the screenshot runner's topmost window.
- **Screenshot runner 2px inset** — crops 2px from each edge to remove Windows border artifact.
- **Dialog hero pattern** — open non-modally at t=200ms, lift dialog at t=850ms, screenshot
  at t=950ms. Use `app._capture_target = <toplevel>` to capture a dialog instead of the app.
- **Full-app widget sizing** — PageStack, SideNav, AppShell use `fill="both", expand=True`
  and need `size=(W, H)` (not `minsize=`) to give the canvas a defined size.
- **Navigation window padding** — use `padding=8` on the App for full-app nav scenes to
  give footer-pinned items breathing room at the bottom edge.
- **Tabs vertical scene** — use `padding=16` and `size=(W, H)` since `fill="both"` needs
  a canvas; `minsize=` is sufficient for horizontal tabs scenes.

### MenuButton specifics
- **`icon_only` inferred** — `DropdownButton.__init__` auto-sets `icon_only=True` in
  `style_options` when `icon` is in style_options and `text` is None/empty. The public
  wrapper doesn't need to infer it.
- **Menubutton layout centering** — `Menubutton.label` has `side="left"` in the ttk
  layout. When `icon_only=True` and no dropdown, drop `side="left"` so the label fills
  the full content area and `anchor="center"` can take effect.
- **Item type names** — public API uses `'command'`, `'check'`, `'radio'`, `'separator'`.
  Internal ContextMenu uses `'checkbutton'` / `'radiobutton'`. Translate at the wrapper
  boundary via `_ITEM_TYPE_MAP`. Legacy names accepted for backwards compat.
- **Radio group variable** — `add_radio_item()` auto-creates a shared `StringVar` on the
  internal widget. Values are stored as strings internally. Use `selected=True` to
  pre-select. Multiple `add_radio_item()` calls share one group variable per MenuButton.
- **`show_menu()` respects disabled state** — guard with
  `self._internal.instate(("!disabled", "!readonly"))` before delegating.
- **`disabled` property** — use `instate(("disabled",))`, not string comparison on `cget`.
- **`shortcut=` in `add_item()`** — display-only label. Passes through `format_shortcut()`
  which handles: registered key name → platform display, `"Mod+S"` pattern → `"Ctrl+S"` /
  `"⌘S"` (no registration required), literal string → pass-through.
- **MenuButton hero pattern** — show a standalone "Actions" button (Edit/Duplicate/Archive/
  Delete), NOT a File/Edit/View menubar pattern. Shortcuts section uses the File menu example.

### Style rebuild pattern
- **`configure_style_options` alone doesn't rebuild** — it only updates the stored
  `_style_options` dict. Call `rebuild_style()` immediately after to regenerate the TTK
  style with the new options and apply it to the widget.
- **`emit` wraps `event_generate`** — `PublicWidgetBase.emit(event, data=...)` calls
  `self._internal.event_generate(sequence, data=data)` directly. For internal widgets
  use `event_generate` with `data=` natively (the event system is patched to support it).

### Widgets and API
- **`disabled` on Label** — not appropriate. Label is display-only.
- **`color=` / `background_color=`** — removed. Use `accent=` / `surface=`.
- **`bs.App` does not accept `theme=`** — use `settings={"theme": "..."}`.
- **`bs.Signal()` crashes at module level** — must be inside `with bs.App():`.
- **`textsignal=`** — standard kwarg for text-bearing widgets. `signal=` for non-text
  (Slider, Checkbox, etc.). Never expose `textvariable=` / `variable=` publicly.
- **`TTKWrapperBase.__init__` overwrites `self._accent`** — store accent before `super().__init__()`,
  re-assign after.
- **`<<BsThemeChanged>>`** fires after full rebuild (use this). `<<ThemeChanged>>` fires before.
- **`bs.SelectButton`** — button-styled non-editable picker. Distinct from `bs.MenuButton`
  (action menu) and `bs.Select` (editable combobox).
- **`bs.Table` only accepts `SqliteDataSource`**.
- **`RadioGroup.set()` validates against keys**, not values.
- **`bs.Form` uses `col_count=`**, not `columns=`.
- **`ToggleGroup(padding=N)`** — bug fixed; safe to pass.
- **`value=` ignored when `signal=` also passed** on boolean widgets — seed the Signal directly.

### Boolean controls
- **Switch/ToggleButton unsupported features** — Switch: no `on_icon`/`off_icon`/`icon_only`/
  `show_indicator`/`tristate`/`density`. ToggleButton: no `tristate`/`show_indicator`.
  Checkbox: only widget supporting `tristate`.
- **Density** — Checkbox and Switch do NOT support `density=`. ToggleButton DOES.
- **Sphinx signatures** — give each subclass its own `__init__` to avoid inheriting
  unsupported params. Use `:inherited-members: PublicWidgetBase` in autoclass.

### Layout widgets
- **`height=`/`width=` on VStack/HStack** — setting one collapses the other axis.
  Add `fill=` + `expand=True` for the unconstrained axis.
- **`show_border=True` needs padding** — border is inside the frame edge.
- **`Grid columns=N` shorthand** — `columns=3` ≡ `[1,1,1]`. `0` == `'auto'`.
- **`**extra_kw` removed from layout wrappers** — `Card`, `GroupBox`, `VStack`,
  `HStack`, `Grid` only accept `**kwargs`.
- **`variant=` removed from VStack/HStack** — use `bs.Card` for card-variant layout.

### Dialogs
- **7 doc pages** — `dialogs.rst` is toctree-only. `ColorDropperDialog` is internal.
- **`content_builder`** receives an internal `_Frame` — use `_Label`/`_Frame` primitives.
- **`Frame.configure(surface=...)`** does NOT work at runtime — use `configure_style_options(surface=...)`.
- **`Dialog.__init__`** is fully keyword-only; `parent=` not `master=`; `min_size=`/`max_size=`.
- **`ButtonRole`** values: `"primary"`, `"secondary"`, `"danger"`, `"cancel"`.
- **`bs-dialog-screenshot` CSS class** — dialog screenshots only; adds border + drop shadow.

### Sliders / fields
- **Slider/RangeSlider spacing** — `VStack gap=` does not visually separate tracks.
  Use `margin_y=10` on each widget. Track heights: plain ≈ 24px, ticks ≈ 45px, badge+ticks ≈ 65px.
- **Screenshot widths** — use `minsize=(720, 1)` for all input/field/slider scenes.
- **`anchor_items="baseline"`** — invalid. Use `"s"`.
- **`select.py` / `calendar.py` shadow stdlib** — use `selectfield.py` and `calendarwidget.py`.

### Misc
- **American English** — all docstrings and user-facing text. Spelling scrub still pending.
- **`font="heading-md"`** not `"heading-md[bold]"` — headings already bold.
- **`&` in `bs.Label` text** — Tkinter strips `&`. Use `"and"`.
- **`Expander` is internal** — use `bs.Accordion`.
- **Run examples after editing** — always `python docs/examples/<widget>.py` before committing.
- **Dark mode Note admonition** — override in `custom.css` inside `html[data-theme="dark"]`:
  `--pst-color-info: #6ea8fe; --pst-color-info-bg: #0d306e`.
- **`Shortcuts` service** — `register(key, "Mod+S", fn)` + `bind_to(app)` wires the keyboard
  handler. `format_shortcut(spec)` resolves display text only (no binding side effect).

---

## Architecture (settled)

**Public API** is a composition layer over internal widgets. Public widgets are plain Python
objects (NOT `tk.Widget` subclasses) holding `self._internal`.

Constructor order: resolve parent → split layout kwargs → construct internal → attach to parent.
`_split_layout_kwargs` strips pack/grid/place keys before internal widget construction.

`.tk` property returns the underlying ttk widget — escape hatch, user's responsibility.

### Context-manager parenting

```python
with bs.App(title="Demo", padding=16, gap=8) as app:
    with bs.HStack(gap=4):
        bs.Label("Hello")
        bs.Button("OK", on_click=lambda: ...)
app.run()
```

`__enter__` pushes container, `__exit__` pops. App hides on enter, shows on exit.

### Events

```python
sub = widget.on_change(handler)   # → Subscription (cancellable)
widget.on_change().debounce(300).listen(handler)  # → Stream (composable)
```

All `on_*()` shorthands use `@overload`: no-arg → `Stream`, with handler → `Subscription`.

### Signals

```python
sig = bs.Signal(value)
bs.TextField(textsignal=sig)   # two-way binding
sig.subscribe(lambda v: ...)
```

### Layout

```python
bs.VStack(padding=20, gap=12, fill="both", expand=True)
bs.HStack(gap=8, anchor_items="center", fill="x")
bs.Grid(columns=["auto", 1], gap=8, sticky_items="ew", fill="x")
```

`fill_items=`, `expand_items=`, `anchor_items=` — container defaults, per-child kwargs override.

---

## Source structure

```
src/bootstack/
├── _core/       infrastructure (capabilities, colorutils, mixins, publisher, images)
├── _runtime/    Tk patches (app, toplevel, menu, shortcuts, events)
├── assets/      themes, locales, icons
├── data/        DataSource (Base, Memory, Sqlite, File)
├── dialogs/     dialog implementations
├── signals/     Signal, TraceOperation
├── style/       Style, Theme, Typography, builders
├── validation/  ValidationRule, ValidationResult
└── widgets/
    ├── _core/   public framework internals (base, container, context, events)
    ├── _impl/   internal implementation (primitives, composites, mixins)
    ├── app.py, button.py, ...  (~40 public wrapper files)
    └── types.py AccentToken, VariantToken, WidgetDensity, SurfaceToken, etc.
```

---

## Key API reference

```python
import bootstack as bs

with bs.App(title="My App", size=(800,600), padding=16, gap=8) as app:
    sig = bs.Signal("World")
    bs.Label("Hello!", font="heading-lg")
    bs.Button("OK", accent="primary", on_click=lambda: ...)
app.run()

# AppShell
with bs.AppShell(title="My App", settings={"theme": "bootstrap-light"}) as shell:
    shell.toolbar.add_button(icon="sun", command=bs.toggle_theme)
    with shell.add_page("home", text="Home", icon="house"):
        bs.Label("Welcome!")
    shell.navigate("home")
shell.run()

# Tokens
accent  = "primary|secondary|info|success|warning|danger|default"
variant = "solid|outline|ghost|toggle"
surface = "content|card|chrome|overlay"
font    = "body|heading-lg|heading-md|caption|code|body+2[italic]"

# Dialogs
bs.alert("Done.")
bs.confirm("Delete?")          # → bool
bs.ask_string("Name:")         # → str | None
bs.ask_integer("Age:", min_value=0)  # → int | None
bs.ask_date("Pick date:")      # → date | None
bs.ask_color()                 # → ColorChoice | None
bs.ask_font()                  # → Font | None
```

---

## Code standards

**Docstrings:** one-line summary + description + `Args:` (name: description, no types).
Single backtick `` `X` `` — never double. No RST roles. Valid values + defaults per kwarg.

**`on_*()` shorthands:**
```python
@overload
def on_change(self) -> Stream: ...
@overload
def on_change(self, handler: Callable[[Event], Any]) -> Subscription: ...
def on_change(self, handler=None):
    return self.on("change", handler)
```

---

## Open bugs

- `value=` silently ignored when `signal=`/`variable=` also passed (all boolean widgets)
- `ToggleGroup` solid variant poor contrast (`src/bootstack/style/builders/toolbutton.py`)
- `Style._tk_widgets` grows forever — partially resolved; pages are never destroyed
