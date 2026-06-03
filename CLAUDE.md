# bootstack — Claude Handoff

## Project overview

bootstack is a batteries-included Python desktop UI framework. It is **not**
advertised as a Tkinter wrapper — the goal is to abstract Tkinter away entirely
so that Tkinter's warts, naming conventions, and legacy API are invisible to the
user. Widget names, arguments, methods, and events are designed for modern Python
and ease of use, not compatibility with the raw tk/ttk surface.

**Design philosophy:**
- Opinionated and configurable within a reasonable range — not infinitely
  customizable at the cost of simplicity
- Go from nothing to something fast — layouts, theming, signals, and navigation
  should all have sensible defaults
- The user should never need to `import tkinter` — everything is `bs.*`

**Working directory:** `D:\Development\bootstack`

**Branch strategy:** `feat/*` branches off `main` for feature/API work.
PRs go `feat/*` → `main`.

---

## Current initiative — Sphinx docs + public API audit

**Branch:** `feat/docs-api-improvements` (active, not yet PRed to `main`)

**Goal:** Build the Sphinx documentation site and simultaneously audit/improve
every public widget wrapper — proper types, complete kwargs, thorough docstrings,
`@overload` event shorthands, and runnable examples with screenshots.

### Status

**Done** (wrapper ✓ · doc page ✓ · example ✓ · screenshots ✓):
Actions, Inputs, Data Display, Selection, Overlays, Layout, Navigation,
Menus (Toolbar only), Dialogs (7 pages — `dialogs.rst` is now a toctree index).

Dialog pages: `message-dialogs.rst`, `input-dialogs.rst`, `color-dialog.rst`,
`font-dialog.rst`, `filter-dialog.rst`, `dialog.rst`, `formdialog.rst`.

New public API added (dialogs pass): `bs.ask_color()`, `bs.ColorChooserDialog`,
`bs.ColorChoice`, `bs.ask_font()`, `bs.FontDialog`, `bs.ask_filter()`,
`bs.FilterDialog`.

**Done (wrapper ✓ · doc page ✓ · example ✓ · screenshots pending):**
Forms — `docs/api/forms.rst`, `docs/examples/forms.py`.

New public API added (forms pass): `bs.FormItem`, `EditorType` renamed to match
public widget names, `on_data_change()` event shorthand, `<<BsDataChange>>` event.

**Pending:** Forms screenshots, MenuButton.

### What's next

1. **Forms screenshots** — take `forms-light.png` / `forms-dark.png` via
   `python docs/scripts/take_screenshots.py forms`. No code changes needed.

2. **MenuButton** — still pending (Menus and Toolbars category). After Forms screenshots.

Note: Tree and Table (Data Display) are deferred — too complex for this pass.

### AppShell deferred improvements (tackle as a dedicated pass)

These were identified during the docs pass but require internal changes:

1. **`nav_pane_width=` not wired** — public wrapper accepts it but the param is
   not threaded through `_build_shell` → `SideNav(pane_width=...)`. Fix: add
   `nav_pane_width: int | None = None` to internal `AppShell.__init__` and
   `_build_shell`, then pass to `SideNav(pane_width=nav_pane_width)`.

2. **Nav item density/font size not controllable** — row height, font size, and
   icon size are hardcoded in the SideNav style builder. Fix: expose a
   `nav_density: WidgetDensity` param on AppShell/SideNav that the item builder
   respects (similar to `toolbar_density`).

3. **`toolbar` and `nav` properties expose internals** — `shell.toolbar` returns
   the internal composite (callers must use `command=` not `on_click=`);
   `shell.nav` returns the internal SideNav, not the public wrapper. Fix: return
   the public `Toolbar` and `SideNav` wrapper instances instead.

4. **Group UX issues** — when a child item is selected, the parent group header
   gets the same full selection highlight (should use a lighter "has-active-child"
   style). Child items also have no visual indentation. Both are internal SideNav
   style/layout issues.

5. **`add_footer_area` / nav footer container** — currently only page-linked
   items can go in the footer (`add_footer_page()`). Non-page widgets (e.g. a
   user-menu `MenuButton`) have no placement API. Fix: expose a `footer_area`
   layout container on AppShell (similar to how `toolbar` works).

6. **Event naming in remaining widgets** — broader audit found past-tense event
   names still needing rename to present tense:
   - `SideNav.on_pane_toggled` → `on_pane_toggle`
   - `SideNav.on_display_mode_changed` → `on_display_mode_change`
   - `ListView.on_selection_changed` → `on_change`
   - `Calendar.on_date_selected` → `on_date_change`

### Widget documentation pattern (established — follow exactly)

For each widget:

1. **Audit** — spawn an Explore agent to compare the public wrapper
   (`src/bootstack/widgets/<name>.py`) against the internal implementation
   (`src/bootstack/widgets/_impl/...`) and `FieldAddonMixin`. Check: missing
   kwargs, methods, properties, event shorthands.

2. **Fix the wrapper** — apply the standard improvements:
   - Use `AccentToken`, `VariantToken`, `WidgetDensity`, `Justify`, etc. from
     `widgets/types.py` instead of bare `str`
   - All `on_*()` shorthands must have `@overload`: no-arg → `Stream`,
     handler → `Subscription`
   - Remove low-level kwargs that bypass semantic theming (`color=`,
     `background_color=`, `foreground=`) — use `accent=` / `surface=` instead
   - **No explicit self-placement params** — `fill`, `expand`, `anchor`, `row`,
     `column`, etc. must NOT appear as named parameters. Accept them via
     `**kwargs` and route through `self._split_layout_kwargs(kwargs)`. See
     ScrollView/SplitView as the reference implementation.
   - **No `**extra_kw`** — the parameter must be named `**kwargs`.
   - Expand class docstring: valid values, defaults, behavior notes per kwarg

3. **Write `docs/api/<widget>.rst`** — structure:
   - Brief intro (one sentence) — **no intro code block above the hero screenshot**
   - `.. raw:: html` hero screenshot block (see pattern below)
   - `Usage` section: one sub-section per feature (accents, variants, icons, states, etc.)
     Subsections with a focused screenshot use the same `.. raw:: html` pattern
     referencing `<widget>-<scene>-light/dark.png`. Put the screenshot **after** the
     code block in each subsection.
   - `Widget sizing` section with shared include (see pattern below)
   - `See also` section cross-referencing related widgets
   - `API` section: `.. autoclass:: bootstack.widgets.<name>.<Class>` with `:members:`
     Add `:inherited-members: FieldAddonMixin` for field widgets; add
     `:exclude-members: tk` on all widgets to hide the escape hatch.
   - `Full Example` section: `.. literalinclude:: ../../docs/examples/<widget>.py`
     with `:start-after: import bootstack as bs`

4. **Write `docs/examples/<widget>.py`** — a clean, runnable app that also
   serves as the screenshot source. Rules:
   - **Show visual states only** — basic usage, variants, accents, label/message,
     states (disabled, read-only), density, etc. Omit interactive-only sections
     (reactive binding, event callbacks, validation) — those read as blank/default
     in a static screenshot and are better shown as RST code snippets in Usage.
   - No `app.tk.after(...)` or screenshot scaffolding in the example file
   - No `__setattr__` hacks — use proper function defs instead of assignment lambdas
   - No backslash line continuations — put stream chains inline or use a function
   - Use built-in rule type strings (`"stringLength"`, `"email"`, etc.) with
     `add_validation_rule()` — never construct `ValidationRule` objects in user-facing code
   - Do not use `fill="x"` in RST doc snippets — layout kwargs belong only in
     the example file where a real layout context exists

5. **Write `docs/screenshots/<widget>.py`** — scene-based hero file. Each scene is a
   self-contained callable that creates its own `bs.App` and calls `app.run()`.
   Define a `SCENES` dict mapping scene names to callables. The runner probes for
   `SCENES` and captures each separately.

   **Hero scene guidelines:**
   - Input widgets: 1–2 fields max. Show focused state with content + unfocused with
     placeholder side by side. Use `anchor_items="n"` when fields have different heights.
   - Button/action widgets: 2–3 key variants side by side.
   - Layout/composite widgets: representative composition.
   - Dial in `size=(W, H)` manually — height must be tight to content with ~20px
     padding. Too much empty space below is the most common issue.

   **Per-section scene guidelines:**
   - Only add a scene for sections with visible UI to show (skip interactive-only sections).
   - Scene content must match the RST code block exactly — same labels, values, rule types.
   - Name scenes to match their RST subsection: `"states"`, `"validation"`, `"accents"`, etc.

   ```python
   # docs/screenshots/widget.py
   import bootstack as bs

   def hero():
       with bs.App(title="Widget", size=(680, 120), padding=20) as app:
           ...
       app.run()

   def states():
       with bs.App(title="Widget — States", size=(680, 100), padding=20) as app:
           ...
       app.run()

   SCENES = {"hero": hero, "states": states}
   ```

6. **Take screenshots:**
   ```bash
   py -3.12 docs/scripts/take_screenshots.py <widget>                  # all scenes, both themes
   py -3.12 docs/scripts/take_screenshots.py <widget> --light          # all scenes, light only
   py -3.12 docs/scripts/take_screenshots.py <widget> --scene hero     # one scene, both themes
   ```
   Scene outputs: `docs/_static/examples/<widget>-<scene>-light.png` and `-dark.png`.
   Legacy (no SCENES): `docs/_static/examples/<widget>-light.png` and `-dark.png`.

7. **Wire into the category index** (`docs/api/<category>.rst`) — add to toctree.

8. **Commit** on `feat/docs-api-improvements`.

### Screenshot HTML pattern (copy-paste for each widget page)

Hero (top of page):
```rst
.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/<widget>-hero-light.png"
        alt="<Widget> demo — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/<widget>-hero-dark.png"
        alt="<Widget> demo — dark theme"
        style="max-width:100%;">
```

Per-section (after the code block in a Usage subsection):
```rst
.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/<widget>-<scene>-light.png"
        alt="<Widget> <scene> — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/<widget>-<scene>-dark.png"
        alt="<Widget> <scene> — dark theme"
        style="max-width:100%;">
```

Margin and border-radius are owned by `docs/_static/custom.css` — do NOT put them in inline styles.

CSS in `docs/_static/custom.css` handles `data-theme` switching.
pydata-sphinx-theme sets `document.documentElement.dataset.theme` to
`"dark"` or `"light"` — selector is `[data-theme="dark"]`.

### Widget sizing section pattern (add to every widget page)

```rst
Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst
```

Path is file-relative from `docs/api/` — do NOT use a leading `/`.
Omit this section entirely from dialog doc pages (dialogs are Toplevel windows,
not layout-managed widgets).

### Gotchas

- **Self-placement via `**kwargs`** — `fill`, `expand`, `anchor`, `row`, `column`,
  `sticky`, etc. are NOT explicit params on any public wrapper. Every wrapper accepts
  them via `**kwargs` routed through `self._split_layout_kwargs(kwargs)`. Never add
  explicit placement params — use `**kwargs`.
- **`**kwargs` not `**extra_kw`** — the catch-all must be named `**kwargs`.
  `**extra_kw` was the old convention; it has been renamed throughout.
- **`margin_x=` / `margin_y=`** — axis-specific external spacing. `margin=` sets
  all sides; `margin_x=`/`margin_y=` override horizontal/vertical respectively.
  Defined in `widgets/_core/container.py` `_expand_margin`. Never use `padx=`/
  `pady=` in user-facing code — those are internal ttk names.
- **`.. include::` path is file-relative** — docutils resolves paths relative to
  the file, NOT the Sphinx source root. From `docs/api/`, use
  `../shared/widget-sizing.rst`. A leading `/` is an absolute filesystem path.
- **ScrollView `height=`/`width=` go to the canvas** — passing them to the Frame
  is silently ignored. The fix routes these to the canvas constructor so the
  viewport is constrained directly.
- **No scrollbar variants on ScrollView** — `scrollbar_variant` was removed from
  the public API. Do not re-expose it.
- **SplitView `sash_thickness=`** — routes through `style_options` to the internal
  PanedWindow builder. Default is `b.scale(6)` (~6 px).
- **American English** — all docstrings, comments, and user-facing text must use
  American English (color, dialog, center, analyze, etc.). A full spelling scrub
  is still pending.
- **No `fill="x"` in RST doc snippets** — layout kwargs belong only in
  `docs/examples/<widget>.py`, not in Usage code blocks in `.rst` files.
- **Example files show visual states only** — interactive sections (reactive
  binding, event callbacks, validation) appear blank in a static screenshot. Put
  them in RST Usage snippets; keep the example file to visually readable states.
- **`ValidationRule` first arg is `rule_type`** — e.g.
  `ValidationRule("stringLength", min=3, trigger="blur")`. Built-ins:
  `"required"`, `"email"`, `"pattern"`, `"stringLength"`, `"custom"`, `"compare"`.
- **`anchor_items="baseline"`** — not a valid anchor. Use `"s"` instead.
- **Screenshot runner** — use `update_idletasks()`, not `update()` (dispatches
  focus-clearing events). Window geometry is set via `after(0)` inside `_run` so
  it fires after `App.__exit__` shows the window. Focus is forced via `after(50)`.
- **`disabled` on Label** — not appropriate. Label is display-only; do not expose
  `disabled=` on it.
- **`color=` / `background_color=`** — removed from public wrappers. Use `accent=`
  for text color and `surface=` for background.
- **Hero vs full example split** — `docs/screenshots/<widget>.py` is the lean
  hero (may use `app.tk.after()` for focus/blur scaffolding).
  `docs/examples/<widget>.py` is the full interactive demo. The screenshot runner
  prefers `docs/screenshots/` and falls back to `docs/examples/`.
- **`select.py` / `calendar.py` shadow stdlib** — use `selectfield.py` and
  `calendarwidget.py`. Check for stdlib name collisions before naming any new
  example file.
- **`&` in `bs.Label` text** — Tkinter strips `&` (mnemonic underline indicator).
  Use `"and"` instead of `"&"` in example section labels.
- **`ListView` requires a height constraint to scroll** — without one, it expands
  to fit its row pool and scrolling is disabled. Use `height=N` for a
  self-contained height, or place inside a height-constrained layout with
  `fill='both', expand=True`. Pre-select after the `with bs.App():` block (before
  `app.run()`) — pre-selecting inside the block renders incompletely.
- **`GridFrame` equal columns** — use `uniform=f"col_w{weight}"` in
  `columnconfigure` so equal-weight columns are truly equal regardless of
  children's minimum sizes.
- **`tristate=False` default** — boolean controls seed `unchecked_value` by
  default when no `value=`/`signal=` is given. `tristate=True` opts Checkbox
  into three-state behavior (None/True/False).
- **`on_icon`/`off_icon` vs `icon=`** — for stateful widgets, use `on_icon=`/
  `off_icon=` for state-specific icons. A static `icon=` only color-shifts.
  ToggleButton may use just one of the two.
- **`info` color token** — first-class semantic accent. Add to `AccentToken`,
  `token_maps.py`, and `cli/add.py` when creating new themes.
- **Run examples after editing** — always run `python docs/examples/<widget>.py`
  after making changes before committing. Runtime bugs are invisible to static
  analysis.
- **pydata-sphinx-theme** — current theme (migrated from Shibuya). Key config:
  `napoleon_use_param = True` (merges Napoleon Args + typehints into one
  Parameters block); autoclass for boolean controls needs
  `:inherited-members: PublicWidgetBase` to show methods from
  `_BooleanControlBase`.
- **Switch/ToggleButton unsupported features** — Switch does NOT support
  `on_icon`/`off_icon`/`icon_only`/`show_indicator`/`tristate`/`density`.
  ToggleButton does NOT support `tristate`/`show_indicator`. Only Checkbox
  supports `tristate`. Give each subclass an explicit `__init__` so Sphinx shows
  the correct signature.
- **`density=` on boolean controls** — Checkbox and Switch do NOT support it.
  ToggleButton DOES via `_capture_density_option()` in `CheckToggle`.
- **`TTKWrapperBase.__init__wrapper` overwrites `self._accent`** — composite
  widgets that pop `accent` before calling `super().__init__()` will have
  `self._accent` reset to `None`. Fix: store accent in a local var, call super,
  then re-assign: `self._accent = accent_value`.
- **`SelectButton`** — public widget wrapping `OptionMenu` (internal). A
  button-styled, non-editable value picker. Fills the gap between `Select`
  (editable combobox) and `MenuButton` (action menu).
- **Boolean control Sphinx signatures** — widgets inheriting `_BooleanControlBase`
  without overriding `__init__` show ALL base class params in Sphinx (including
  unsupported ones). Give each subclass its own `__init__` listing only its
  supported params. Use `:inherited-members: PublicWidgetBase` in `autoclass`.
- **ToggleButton variants** — supports `solid`, `outline`, `ghost`. Show with
  both inactive and active states side-by-side so the transition is visible.
- **RadioGroup `orient`** — show horizontal and vertical side by side using
  `HStack`, not as separate sections.
- **Toast/Tooltip screenshot z-order** — the screenshot runner sets the app
  `topmost=True` and lifts it at t=800ms. Show floating Toplevels at t=850ms so
  they claim topmost after the app. Tooltip: simulate hover via
  `btn.tk.event_generate('<Enter>')` at t=600ms (fires after 250ms delay). Toast:
  `app.tk.after(850, lambda: bs.Toast(..., position='+X+Y').show())`.
- **Screenshot sizing** — use `size=(W, H)` on the example App (not `minsize=`).
  Target ~680-720px width to stay within the pydata-sphinx-theme content column.
  Use `Grid(fill="x")` or `VStack(fill="x")` for all top-level demo sections to
  keep content at integer pixel boundaries and avoid browser downscale blurriness.
- **Screenshot runner 2px inset** — `take_screenshots.py` crops 2px from each
  edge to remove the Windows window-border artifact.
- **`**extra_kw` removed from layout wrappers** — `Card`, `GroupBox`, `VStack`,
  `HStack`, `Grid` no longer accept it. Do not re-add.
- **`variant=` removed from VStack/HStack** — use `bs.Card` for card-variant
  layout. VStack and HStack are plain layout containers only.
- **`height=`/`width=` on VStack/HStack** — setting either disables frame
  propagation. Setting both fully constrains the frame. Setting only one collapses
  the other axis to zero — add `fill=` + `expand=True` to let the parent control
  the unconstrained axis.
- **`show_border=True` needs padding** — border is drawn inside the frame edge.
  Always pair `show_border=True` with `padding=` for visual clearance.
- **Grid `columns=N` integer shorthand** — `columns=3` ≡ `columns=[1, 1, 1]`.
  `0` weight == `'auto'`; prefer `'auto'` for clarity.
- **`bs.Event` type** — all `on_*()` callbacks receive
  `bootstack.widgets.types.Event` (not `tkinter.Event`). It has a `data: Any`
  attribute for application-level payloads.
- **No Tkinter references in public docs** — say "anchor position" not "Tkinter
  anchor string"; "cell alignment" not "sticky string".
- **Cross-referencing layout widgets** — Card/GroupBox reference VStack/HStack/Grid;
  VStack/HStack/Grid reference each other and Card/GroupBox. Grid.rst also notes
  that Card and GroupBox support `layout='grid'`.
- **`Expander` is internal** — removed from public API. Use `bs.Accordion`.
- **`Accordion` defaults** — `show_border=True`, `show_separators=True`, body
  `padding=16`. Pass `show_border=False`/`show_separators=False` for a plain look.
  `layout_kw.setdefault('fill', 'x')` ensures accordion fills container width.
- **`Accordion` header selected state** — uses `b.subtle()` (light tint) for ghost
  variant; `b.color(accent)` for solid. `highlight=True` is set on all sections.
- **One doc page per widget** — never document more than one widget per RST page.
- **`font="heading-md"` not `font="heading-md[bold]"`** — heading tokens are
  already bold. The `[bold]` modifier is redundant.
- **AppShell `toolbar`/`nav` expose internals** — `shell.toolbar` returns the
  internal composite (use `command=`, not `on_click=`); `shell.nav` returns the
  internal SideNav, not the public wrapper. Do not document them as public
  wrappers. `nav_pane_width=` is not wired — passing it raises `TypeError`.
  Deferred.
- **API naming standard** — present-tense event names (`on_change`, `on_pane_toggle`,
  etc.); `current` property; `item/items/item_keys` (not `node/nodes/node_keys`);
  `expanded=` (not `is_expanded=`). Still pending on SideNav
  (`on_pane_toggled`, `on_display_mode_changed`), ListView
  (`on_selection_changed`), Calendar (`on_date_selected`).
- **Dialog API conventions:**
  - `Dialog.__init__` is fully keyword-only; use `parent=` (not `master=`);
    `min_size=`/`max_size=` (not `minsize=`/`maxsize=`).
  - `ButtonRole` values: `"primary"`, `"secondary"`, `"danger"`, `"cancel"`.
  - `content_builder` receives an internal `_Frame` — use `_Label`/`_Frame`
    primitives from `widgets/_impl/primitives/`, not public wrappers.
  - `Frame.configure(surface=...)` does NOT work at runtime — use
    `frame.configure_style_options(surface=...)`.
  - `get_theme_color(token)` in `bootstack.style.style` returns the hex color for
    any accent token. Use it instead of hardcoding severity colors.
  - `on_data_change` (present tense) on `Form` and `FormDialog`.
  - `min_size=` is the public convention. `App` still uses `minsize` internally
    (future cleanup needed).
  - All dialog wrappers expose `show(position: tuple[int,int] | None, modal: bool | None)`.
- **Dialog category has 7 doc pages** — `dialogs.rst` is a toctree-only index.
  `ColorDropperDialog` is internal to `ColorChooserDialog`, not a standalone public
  class. `ColorChooserDialog` internal cleanup pending (`on_dialog_result()` /
  `off_dialog_result()` are unused).
- **Dialog hero screenshot pattern** — open non-modally at t=200ms
  (`dialog.show(modal=False)`), lift dialog at t=850ms, screenshot at t=950ms. See
  `docs/screenshots/dialog.py` as reference. For oversized dialogs (FontDialog:
  800×600), pass `position=(200, 70)` so the title bar is above the capture region.
- **`app._capture_target`** — set to a Toplevel to capture that window instead of
  the app window. Defined in `docs/scripts/take_screenshots.py` `_RUNNER._grab`.
- **`bs-dialog-screenshot` CSS class** — use on dialog screenshot `<img>` tags
  instead of inline `border-radius`. Adds 1px border + drop shadow. Regular widget
  screenshots keep `bs-screenshot-light/dark` only.
- **`ColorChoice` namedtuple** — `namedtuple('ColorChoice', 'rgb hsl hex')`.
  Fields: `rgb=(r,g,b)` 0–255, `hsl=(h,s,l)` 0–360/0–100/0–100, `hex` lowercase.
- **`FontDialog.result` typed as `Any`** — intentional; avoids surfacing
  `tkinter.font.Font` in the public API.

---

## Architecture (settled)

### Public widget layer

The public API is a **composition layer** over internal widgets. Public widgets
are plain Python objects (NOT `tk.Widget` subclasses) holding `self._internal`.

- `.tk` property returns the underlying `tk.Widget` / `ttk.Widget` — escape
  hatch, undocumented, user's responsibility.
- Constructor order for every public widget:
  resolve parent → split layout kwargs → construct internal → attach to parent.
- `_split_layout_kwargs` strips `PACK_KEYS`/`GRID_KEYS`/`PLACE_KEYS` before
  the internal widget is constructed — layout kwargs never leak into ttk ctors.

### Context-manager parenting

Thread-local context stack. `parent=` is optional — omitting it uses the current
context; passing it explicitly overrides the stack.

```python
with bs.App(title="Demo", padding=16, gap=8) as app:
    with bs.HStack(gap=4):
        bs.Label("Hello")
        bs.Button("OK", on_click=lambda: ...)
app.run()
```

- `__enter__` pushes the container; `__exit__` pops it.
- `App` hides on enter, shows on exit (eliminates flash). Only `App.__exit__`
  calls `update_idletasks()`.

### Events — `on`, `Stream`, `Subscription`

```python
# Handler → Subscription (cancellable)
sub = widget.on_change(handler)
sub.cancel()

# No handler → Stream (composable)
widget.on_change().debounce(300).listen(handler)

# Context manager (auto-cancel)
with widget.on_change(handler):
    ...
```

All `on_*()` shorthands use `@overload` to return `Stream` (no handler) or
`Subscription` (with handler). The base `on(event, handler?)` follows the same
pattern. `<<BsThemeChanged>>` fires after the full theme rebuild (correct timing
for reading new colors); `<<ThemeChanged>>` fires before (Tcl-internal, avoid).

### Signals

```python
sig = bs.Signal(value)          # reactive primitive
widget = bs.TextField(textsignal=sig)   # two-way binding
sig.subscribe(lambda v: ...)    # imperative subscription
```

`textsignal=` is the standard kwarg for all text-bearing widgets. `signal=` for
non-text widgets (Slider, Checkbox, etc.). Never expose `textvariable=` or
`variable=` in the public API. `bs.Signal()` must be created inside `with bs.App():`.

### Layout

```python
with bs.VStack(padding=20, gap=12, fill="both", expand=True):
    with bs.HStack(gap=8, fill="x"):
        bs.Label("Name:")
        bs.TextField(fill="x", expand=True)
    with bs.Grid(columns=["auto", 1], gap=8, sticky_items="ew", fill="x"):
        bs.Label("A:")
        bs.TextField()
```

- `fill="x"/"y"/"both"/"none"` — layout kwarg consumed by parent container
- `expand=True` — layout kwarg; widget takes extra space in pack direction
- `margin=` — space outside (CSS margin); `padding=` — space inside
- `fill_items=`, `expand_items=`, `anchor_items=` — container applies to all
  children as defaults; per-child kwargs override

---

## Source package structure

```
src/bootstack/
├── _core/          internal infrastructure (capabilities, colorutils, mixins, publisher, images, variables)
├── _runtime/       Tk patches & startup hooks (app, toplevel, menu, shortcuts, events)
├── assets/         themes, locales, icons
├── cli/            CLI commands
├── data/           DataSource classes (BaseDataSource, MemoryDataSource, SqliteDataSource, FileDataSource)
├── dialogs/        dialog implementations
├── i18n/           MessageCatalog, L, LV, IntlFormatter
├── signals/        Signal, TraceOperation
├── style/          Style, Theme, Typography, builders
├── validation/     ValidationRule, ValidationResult
└── widgets/
    ├── _core/      public framework internals (base, container, context, events, exceptions, subscription)
    ├── _impl/      all internal widget implementation (never import directly)
    │   ├── primitives/   TTK widget subclasses
    │   ├── composites/   complex internal widgets
    │   ├── mixins/       shared mixins
    │   ├── _internal/    TTKWrapperBase
    │   └── _parts/       entry sub-components
    ├── app.py, stacks.py, button.py, ...  (flat public widget surface, ~40 files)
    └── types.py    Shared type aliases and base TypedDicts
```

**`widgets/types.py` public types:**
- Primitive aliases: `Master`, `EventCallback`, `CommandCallback`
- Geometry: `Anchor`, `Orient`, `Justify`, `Relief`, `CompoundMode`, `Fill`, `Sticky`
- State/density: `WidgetState`, `WidgetDensity`
- Styling tokens: `AccentToken`, `VariantToken`, `SurfaceToken`
- Base TypedDicts: `BaseWidgetKwargs`, `StyledKwargs`

---

## Docs structure

```
docs/
├── conf.py                    Sphinx config (pydata-sphinx-theme, napoleon, sphinx-design)
├── index.rst                  Root toctree (hidden, 5 sections)
├── requirements.txt           sphinx, pydata-sphinx-theme, sphinx-autodoc-typehints, sphinx-design, sphinx-autobuild
├── scripts/
│   └── take_screenshots.py   Automated screenshot runner (light + dark)
├── examples/
│   └── <widget>.py            Runnable demo for each widget
├── _static/
│   ├── custom.css             Nav logo sizing + light/dark screenshot switching
│   ├── favicon.ico
│   ├── bootstack-logo-light.svg
│   ├── bootstack-logo-dark.svg
│   └── examples/
│       └── <widget>-light.png / <widget>-dark.png
└── getting-started/           Installation, Quick Start, App Structures
    tasks/                     Common Tasks (7 pages)
    deeper/                    Going Deeper (10 pages)
    production/                CLI, Distribution, Debugging, App Settings
    api/                       Widget reference (9 categories, each a toctree)
```

**Live reload during writing:**
```bash
sphinx-autobuild docs docs/_build/html
```
Opens at `http://127.0.0.1:8000`.

---

## Key API reference

```python
import bootstack as bs

# App — context manager required; Signal creation goes inside the with block
with bs.App(title="My App", size=(800, 600), padding=16, gap=8) as app:
    name = bs.Signal("World")          # Signal must be inside with block
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

# Layout containers
bs.VStack(padding=16, gap=8, fill="both", expand=True)
bs.HStack(gap=8, anchor_items="center", fill="x")
bs.Grid(columns=["auto", 1], gap=(12, 6), sticky_items="ew", padding=12)
bs.Card(accent="primary", padding=16)
bs.GroupBox("Section", layout="vstack", padding=12)

# Signals
sig = bs.Signal(value)
bs.TextField(textsignal=sig)
bs.Slider(signal=sig)
sig.subscribe(lambda v: ...)

# Images (use bs.Image, not tkinter.PhotoImage)
img = bs.Image.open("path/to/image.png")
img = bs.Image.from_bytes(raw_bytes)
bs.Button("Launch", image=img)

# Color/font tokens
accent="primary|secondary|info|success|warning|danger|default"
variant="solid|outline|ghost|toggle"
surface="content|card|chrome|overlay"
font="body|heading-lg|heading-md[bold]|caption|code|body+2[italic]"

# Theming
bs.set_theme("bootstrap-dark")
bs.toggle_theme()
bs.get_theme()  # → str

# Dialogs
bs.alert("Done.")
bs.confirm("Delete?")         # → bool
bs.ask_string("Name:")        # → str | None
bs.ask_integer("Age:", min_value=0)  # → int | None
bs.ask_date("Pick date:")     # → date | None
```

---

## Code standards (do not relitigate)

### Docstring conventions

Class docstrings hold:
1. One-line summary + one-paragraph description
2. `Args:` — param name and description only (type is in the signature)
3. `Attributes:` only for runtime-assigned names with no `@property`

Param line format: `name: description` — never `name (type): description`.
Use single backtick `` `X` `` — never double. No RST roles.

### Public API docstring style (for wrappers)

Each kwarg description should state: what it does, valid values, and default.
Example:
```
accent: Color intent token. One of ``'primary'``, ``'secondary'``,
    ``'success'``, ``'warning'``, ``'danger'``, ``'default'``.
    Defaults to the theme's default color.
```

### `on_*()` event shorthand standard

Every `on_*()` shorthand uses `@overload`:
```python
@overload
def on_change(self) -> Stream: ...
@overload
def on_change(self, handler: Callable[[tkinter.Event], Any]) -> Subscription: ...
def on_change(self, handler=None):
    """Register a callback fired when the value changes.

    Returns:
        ``Subscription`` (with handler) or ``Stream`` (without handler).
    """
    return self.on("change", handler)
```

---

## API gotchas

- **`bs.App` does not accept `theme=`** — use `settings={"theme": "..."}`.
  Exception: `localize=` IS a direct kwarg.
- **`bs.Table` only accepts `SqliteDataSource`** — not `MemoryDataSource` or
  `FileDataSource`.
- **`bs.Signal()` crashes at module level** — must be inside `with bs.App():`.
- **`bs.Select` emits `<<Change>>`**, not `<<SelectionChange>>`.
- **`text=Signal(...)` does NOT work for reactive labels** — use `textsignal=`.
- **`bs.Label` uses `.text` not `.value`** — `.value` is for data-bearing widgets
  only (Entry, Checkbox, Slider, etc.).
- **`value=` is ignored when `signal=` is also passed** on boolean widgets
  (Checkbox, Switch, RadioButton, etc.) — seed the Signal directly.
- **`ToggleGroup(padding=N)`** — bug fixed; `padding=` is now safe to pass.
- **`ValidationRule` first arg is the rule type string** — e.g.
  `ValidationRule("stringLength", min=3)`. Built-ins: `"required"`, `"email"`,
  `"pattern"`, `"stringLength"`, `"custom"`, `"compare"`.
- **`bs.Form` uses `col_count=`**, not `columns=`.
- **`bs.L(key, *fmtargs)` uses positional `%s`/`%d` format args**, not `{name}` kwargs.
- **`RadioGroup.set()` validates against keys**, not values.
- **`bs.SelectButton`** — new widget (button-styled value picker). Use instead of
  `bs.OptionMenu` (internal only). Distinct from `bs.MenuButton` (action menu)
  and `bs.Select` (editable combobox).
- **`<<BsThemeChanged>>`** fires after rebuild (use this). `<<ThemeChanged>>`
  fires before (TTK internal — avoid for reading colors).

---

## Open bugs

- `value=` silently ignored when `signal=`/`variable=` also passed (all boolean widgets)
- `ToggleGroup` solid variant has poor contrast — user handling
  `src/bootstack/style/builders/toolbutton.py`
- `Style._tk_widgets` grows forever — partially resolved (WeakSet + visibility guard);
  remaining issue is pages are never destroyed