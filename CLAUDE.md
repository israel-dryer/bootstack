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

### What's done

**Actions category:**

| Widget | Wrapper | Doc page | Example | Screenshots |
|--------|---------|----------|---------|-------------|
| Button | ✓ | `docs/api/button.rst` | `docs/examples/button.py` | ✓ |

**Inputs category:**

| Widget | Wrapper | Doc page | Example | Screenshots |
|--------|---------|----------|---------|-------------|
| TextField    | ✓ | `docs/api/textfield.rst`    | `docs/examples/textfield.py`    | ✓ |
| PasswordField | ✓ | `docs/api/passwordfield.rst` | `docs/examples/passwordfield.py` | ✓ |
| NumberField  | ✓ | `docs/api/numberfield.rst`  | `docs/examples/numberfield.py`  | ✓ |
| Slider       | ✓ | `docs/api/slider.rst`       | `docs/examples/slider.py`       | ✓ |
| RangeSlider  | ✓ | `docs/api/rangeslider.rst`  | `docs/examples/rangeslider.py`  | ✓ |

**Data Display category:**

| Widget | Wrapper | Doc page | Example | Screenshots |
|--------|---------|----------|---------|-------------|
| Label       | ✓ | `docs/api/label.rst`       | `docs/examples/label.py`       | ✓ |
| Badge       | ✓ | `docs/api/badge.rst`       | `docs/examples/badge.py`       | ✓ |
| ProgressBar | ✓ | `docs/api/progressbar.rst` | `docs/examples/progressbar.py` | ✓ |
| Gauge       | ✓ | `docs/api/gauge.rst`       | `docs/examples/gauge.py`       | ✓ |
| ListView    | ✓ | `docs/api/listview.rst`    | `docs/examples/listview.py`    | ✓ |

**Selection category:**

| Widget | Wrapper | Doc page | Example | Screenshots |
|--------|---------|----------|---------|-------------|
| Checkbox     | ✓ | `docs/api/checkbox.rst`     | `docs/examples/checkbox.py`     | ✓ |
| Select       | ✓ | `docs/api/select.rst`       | `docs/examples/selectfield.py`  | ✓ |
| Switch       | ✓ | `docs/api/switch.rst`       | `docs/examples/switch.py`       | ✓ |
| ToggleButton | ✓ | `docs/api/togglebutton.rst` | `docs/examples/togglebutton.py` | ✓ |
| RadioGroup   | ✓ | `docs/api/radiogroup.rst`   | `docs/examples/radiogroup.py`   | ✓ |
| ToggleGroup  | ✓ | `docs/api/togglegroup.rst`  | `docs/examples/togglegroup.py`  | ✓ |
| SelectButton | ✓ | `docs/api/selectbutton.rst` | `docs/examples/selectbutton.py` | ✓ |
| Calendar     | ✓ | `docs/api/calendar.rst`     | `docs/examples/calendarwidget.py` | ✓ |

**Overlays category:**

| Widget  | Wrapper | Doc page | Example | Screenshots |
|---------|---------|----------|---------|-------------|
| Tooltip | ✓ | `docs/api/tooltip.rst` | `docs/examples/tooltip.py` | ✓ |
| Toast   | ✓ | `docs/api/toast.rst`   | `docs/examples/toast.py`  | ✓ |

**Layout category:**

| Widget    | Wrapper | Doc page | Example | Screenshots |
|-----------|---------|----------|---------|-------------|
| Separator  | ✓ | `docs/api/separator.rst`  | `docs/examples/separator.py`  | ✓ |
| Card       | ✓ | `docs/api/card.rst`       | `docs/examples/card.py`       | ✓ |
| GroupBox   | ✓ | `docs/api/groupbox.rst`   | `docs/examples/groupbox.py`   | ✓ |
| VStack     | ✓ | `docs/api/vstack.rst`     | `docs/examples/vstack.py`     | ✓ |
| HStack     | ✓ | `docs/api/hstack.rst`     | `docs/examples/hstack.py`     | ✓ |
| Grid       | ✓ | `docs/api/grid.rst`       | `docs/examples/grid.py`       | ✓ |
| Accordion  | ✓ | `docs/api/accordion.rst`  | `docs/examples/accordion.py`  | ✓ |
| ScrollView | ✓ | `docs/api/scrollview.rst` | `docs/examples/scrollview.py` | ✓ |
| SplitView  | ✓ | `docs/api/splitview.rst`  | `docs/examples/splitview.py`  | ✓ |

**Navigation category:**

| Widget    | Wrapper | Doc page | Example | Screenshots |
|-----------|---------|----------|---------|-------------|
| PageStack | ✓ | `docs/api/pagestack.rst` | `docs/examples/pagestack.py` | ✓ |
| Tabs      | ✓ | `docs/api/tabs.rst`      | `docs/examples/tabs.py`      | ✓ |
| SideNav   | ✓ | `docs/api/sidenav.rst`   | `docs/examples/sidenav.py`   | ✓ |
| AppShell  | ✓ | `docs/api/appshell.rst`  | `docs/examples/appshell.py`  | ✓ |

**Menus and Toolbars category:**

| Widget     | Wrapper | Doc page | Example | Screenshots |
|------------|---------|----------|---------|-------------|
| Toolbar    | ✓ | `docs/api/toolbar.rst`    | `docs/examples/toolbar.py`    | ✓ |
| MenuButton | — | — (pending)               | —                             | — |

**Dialogs category:**

Dialogs public API fully audited, expanded, and split into 7 pages. Hero
screenshots for each page show the actual dialog window (modal=False +
lift_dialog() pattern). `docs/api/dialogs.rst` is now a category index (toctree).

| Item | Doc page | Example | Hero screenshot |
|------|----------|---------|-----------------|
| Message Dialogs | `docs/api/message-dialogs.rst` | `docs/examples/message-dialogs.py` | `docs/screenshots/message-dialogs.py` |
| Input Dialogs   | `docs/api/input-dialogs.rst`   | `docs/examples/input-dialogs.py`   | `docs/screenshots/input-dialogs.py`   |
| Color Dialog    | `docs/api/color-dialog.rst`    | `docs/examples/color-dialog.py`    | `docs/screenshots/color-dialog.py`    |
| Font Dialog     | `docs/api/font-dialog.rst`     | `docs/examples/font-dialog.py`     | `docs/screenshots/font-dialog.py`     |
| Filter Dialog   | `docs/api/filter-dialog.rst`   | `docs/examples/filter-dialog.py`   | `docs/screenshots/filter-dialog.py`   |
| Dialog          | `docs/api/dialog.rst`          | `docs/examples/dialog.py`          | `docs/screenshots/dialog.py`          |
| FormDialog      | `docs/api/formdialog.rst`      | `docs/examples/formdialog.py`      | `docs/screenshots/formdialog.py`      |

New public API additions this pass:
- `bs.ask_color()`, `bs.ColorChooserDialog`, `bs.ColorChoice`
- `bs.ask_font()`, `bs.FontDialog`
- `bs.ask_filter()`, `bs.FilterDialog`

Bugs fixed in internal dialog classes:
- `colorchooser.py`, `fontdialog.py`, `filterdialog.py`: `master=` → `parent=` in `Dialog()` constructor calls
- `fontdialog.py`: scrollbar `variant="round"` → `variant="default"` (round not a valid scrollbar variant)
- `filterdialog.py`: `minsize=`/`maxsize=` → `min_size=`/`max_size=` in `Dialog()` call

### What's next

1. **Forms** — `docs/api/forms.rst` is a stub ("Coming soon."). Full pass needed:
   - **Wrapper**: `src/bootstack/widgets/form.py` — `Form` class is well-written;
     `FormItem`, `FieldItem`, `GroupItem`, `TabsItem`, `TabItem`, `EditorType` are
     imported in the wrapper but NOT exported from `bs.*`. Add them.
   - **Audit**: check `Form` against internal `_impl/composites/form.py` for any
     missing methods, properties, or event shorthands.
   - **Doc page**: replace the stub `docs/api/forms.rst` with a full page following
     the widget documentation pattern. Split into sub-sections for auto-generated
     forms (`data=`), explicit layouts (`items=`), groups, tabs, validation,
     and signals. Note: `FormDialog` already has its own page (`formdialog.rst`).
   - **Example**: `docs/examples/forms.py` — show data= auto-form, explicit items
     with FieldItem, GroupItem, TabsItem, and a multi-column layout. Visual states
     only (no submit/validation callbacks in the example file).
   - **Screenshot**: use `app._capture_target` pattern if showing the form inside
     a dialog is cleaner, or just capture the app window for embedded forms.

2. **MenuButton** — still pending (Menus and Toolbars category). After Forms.

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
   - Brief intro + one code snippet
   - `.. raw:: html` light/dark screenshot block (see pattern below)
   - `Usage` section: one sub-section per feature (accents, variants, icons, states, etc.)
   - `Widget sizing` section with shared include (see pattern below)
   - `See also` section cross-referencing related widgets
   - `API` section: `.. autoclass:: bootstack.widgets.<name>.<Class>` with `:members:`
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
   - Use built-in `ValidationRule` types (`"stringLength"`, `"email"`, etc.)
     instead of `"custom"` when a built-in covers it
   - Do not use `fill="x"` in RST doc snippets — layout kwargs belong only in
     the example file where a real layout context exists

5. **Take screenshots:**
   ```bash
   python docs/scripts/take_screenshots.py <widget>         # both themes
   python docs/scripts/take_screenshots.py <widget> --light # one theme
   ```
   Screenshots save to `docs/_static/examples/<widget>-light.png` and `-dark.png`.
   Focus rings won't show in automated screenshots — acceptable. Retake manually
   if needed after running the example and focusing a field.

6. **Wire into the category index** (`docs/api/<category>.rst`) — add to toctree.

7. **Commit** on `feat/docs-api-improvements`.

### Screenshot HTML pattern (copy-paste for each widget page)

```rst
.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/<widget>-light.png"
        alt="<Widget> demo — light theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/<widget>-dark.png"
        alt="<Widget> demo — dark theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">
```

CSS in `docs/_static/custom.css` handles `data-theme` switching.
pydata-sphinx-theme sets `document.documentElement.dataset.theme` to
`"dark"` or `"light"` — selector is `[data-theme="dark"]`.

### Widget sizing section pattern (add to every widget page)

```rst
Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst
```

The `docs/shared/widget-sizing.rst` fragment documents self-placement kwargs
grouped by geometry manager (Stack, Grid). Path is file-relative from
`docs/api/` — do NOT use a leading `/` (that would be an absolute filesystem
path, not source-relative).

### Gotchas discovered during the docs pass

- **Self-placement via `**kwargs` on all wrappers** — `fill`, `expand`,
  `anchor`, `row`, `column`, `sticky`, etc. are NOT explicit params on any
  public wrapper. Every wrapper accepts them via `**kwargs` routed through
  `self._split_layout_kwargs(kwargs)`. VStack, HStack, Grid, Card, GroupBox,
  ScrollView, SplitView, PageStack all follow this pattern. When writing new
  wrappers, do NOT add explicit placement params — use `**kwargs`.
- **`**kwargs` not `**extra_kw`** — the catch-all for remaining kwargs must
  be named `**kwargs` for consistency. `**extra_kw` was the old convention;
  it has been renamed throughout.
- **`margin_x=` / `margin_y=`** — new public kwargs for axis-specific external
  spacing. `margin=` sets all sides (int, 2-tuple, or 4-tuple); `margin_x=`
  overrides horizontal (int or (left, right) tuple); `margin_y=` overrides
  vertical (int or (top, bottom) tuple). Defined in
  `widgets/_core/container.py` `_expand_margin`. Do NOT use `padx=`/`pady=`
  in user-facing code — those are internal ttk names.
- **`docs/shared/widget-sizing.rst`** — shared include fragment for the Widget
  sizing section. Added to all 29 existing doc pages. New pages must include
  it via `.. include:: ../shared/widget-sizing.rst` (file-relative path from
  `docs/api/`). Content is grouped by Stack and Grid geometry managers.
- **`.. include::` path is file-relative** — docutils `.. include::` resolves
  paths relative to the file, NOT the Sphinx source root. From `docs/api/`,
  use `../shared/widget-sizing.rst`. A leading `/` would be an absolute
  filesystem path, not a source-relative path.
- **ScrollView `height=`/`width=` go to the canvas** — the internal Frame
  uses `grid_propagate=True`, so passing `height=` to the Frame is silently
  ignored. The fix routes these to the canvas constructor in
  `_InternalScrollView.__init__` so the viewport is constrained directly.
- **No scrollbar variants on ScrollView** — `scrollbar_variant` was removed
  from the public API. All registered variants ('default', 'round', 'rounded')
  use the same builder and are visually identical. 'square' is the only
  distinct variant but is also not exposed.
- **SplitView `sash_thickness=`** — routes through `style_options` to the
  internal PanedWindow builder. Default is `b.scale(6)` (~6 px). No other
  scrollbar variants exist.
- **American English spelling scrub pending** — British spellings found
  throughout docs and docstrings. Fixed in this session: "labelled" → "labeled"
  (boolean_controls.py, groupbox.py), "behaviour" → "behavior" (togglegroup.py,
  packframe.py, gridframe.py), "cancelled" → "canceled" (dialogs.py). A full
  scrub pass across all files is still needed.
- **`StackPage` docstring referenced internal `Expander`** — replaced with
  accurate description. Watch for stale internal references in docstrings of
  context-manager container classes (SplitPane, StackPage, AccordionSection).
- **No `fill="x"` in RST doc snippets** — layout kwargs like `fill=`, `expand=`,
  `fill_items=`, `expand_items=` belong only in `docs/examples/<widget>.py`, not
  in the Usage code blocks in `.rst` files. Snippets should show the widget's own
  API, not layout concerns.
- **Example files show visual states only** — interactive sections (reactive
  binding, event callbacks, on_submit, validation) appear blank in a static
  screenshot. Put them in RST Usage snippets instead; keep the example file to
  things that read well visually (variants, accents, states, label/message, etc.).
- **`winfo_ismapped()` vs `winfo_manager()`** — `winfo_ismapped()` returns False
  at init time even for packed widgets (window not yet shown). Use
  `bool(winfo_manager())` when you need to know if a widget has been geometry-managed,
  regardless of visibility. Fixed in `PasswordEntry._apply_visibility_toggle`.
- **`text_signal` → `textsignal`** — the old wrappers used `text_signal` (with
  underscore). It is now fixed in Button, Label, Badge, TextField. Watch for it
  in remaining wrappers.
- **Signals must be created INSIDE `with bs.App():`** — `bs.Signal()` wraps a
  `tk.DoubleVar` which requires a root window. Module-level Signal creation
  crashes with "no default root window".
- **`icon_only` + `compound`** — when `icon_only=True`, do NOT set `compound=`
  on the internal widget. It left-aligns the icon. Only set compound when there
  is both text and an icon.
- **`ValidationRule` first arg is `rule_type`** — e.g.
  `ValidationRule("stringLength", min=3, trigger="blur")`. There is no `test=`
  kwarg; use `"custom"` with `func=` only when no built-in covers it.
  Built-ins: `"required"`, `"email"`, `"pattern"`, `"stringLength"`, `"custom"`,
  `"compare"`.
- **`anchor_items="baseline"`** — not a valid Tkinter anchor. Use `"s"` instead.
- **Screenshot runner** — removed `self.tk.update()` from the capture function
  because it dispatches focus-clearing events. `update_idletasks()` is sufficient.
- **`disabled` on Label** — not appropriate. Label is display-only; it has no
  meaningful interactive state. Do not expose `disabled=` on Label.
- **`color=` / `background_color=`** — removed from Label and TextField public
  wrappers. They bypass semantic theming. Use `accent=` for text color and
  `surface=` for background.
- **Shibuya dark mode selector** — uses `html[data-color-mode="dark"]`, NOT
  `prefers-color-scheme`. Both are covered in `custom.css`.
- **Hero vs full example split** — `docs/screenshots/<widget>.py` is the lean
  hero (visual states only, may use `app.tk.after()` for focus/blur scaffolding).
  `docs/examples/<widget>.py` is the full interactive demo. The screenshot runner
  prefers `docs/screenshots/` and falls back to `docs/examples/`.
- **Screenshot runner positioning** — window geometry is set via `after(0)` inside
  `_run` so it fires after `App.__exit__` shows the window. Setting it before
  `orig_run()` is overridden by the WM. Focus is forced via `after(50)` so the
  window owns OS focus before hero widget `focus()` calls fire.
- **`select.py` / `calendar.py` shadow stdlib** — naming an example file after a
  stdlib module shadows it when `docs/examples/` is on `sys.path`. Use
  `selectfield.py` and `calendarwidget.py` instead. Check before naming any new
  example file.
- **`&` in `bs.Label` text** — Tkinter consumes `&` as a mnemonic underline
  indicator and strips it from the displayed text (leaving two spaces). Use
  ``"and"`` instead of ``"&"`` in example section labels.
- **SelectBox disabled text fix** — `SelectBox.__init__` sets `entry.state(['readonly'])`
  AFTER `Field.__init__` sets `['disabled', '!readonly']`, leaving entry in
  `['disabled', 'readonly']`. Fixed in `field.py` by changing the foreground map
  from `('disabled !readonly', ...)` to `('disabled', ...)` so muted text applies
  regardless of the readonly flag.
- **`GridFrame` auto-placed rows had no weight** — rows not pre-defined via `rows=`
  were never `rowconfigure`d, so they defaulted to `weight=0` and couldn't share
  vertical space even with `sticky='nsew'`. Fixed in `gridframe.py`: `_on_child_grid`
  now calls `self.rowconfigure(row, weight=1)` for any row beyond `_row_defs`.
- **`ListView` requires a height constraint to scroll** — virtual scrolling measures
  the visible container height to calculate `_visible_rows`. Without a height
  constraint (from a fixed `size=` App, `sticky='nsew'` Grid, or explicit `height=`),
  the ListView expands to fit its row pool and `_clamp_indices` prevents scrolling.
  The public wrapper sets `pack_propagate(False)` to prevent the row pool from
  feeding back into the layout (which caused an infinite resize loop in Grid
  layouts). Use `height=N` for a self-contained height, or place inside a
  height-constrained layout with `fill='both', expand=True`.
- **`ListView` selection state applied before field widgets exist** — `_update_selection`
  was called before `_update_title`/`_update_text`, so newly-created Label widgets
  missed the `_update_states()` call and rendered without selected styling until
  hover. Fixed in `listitem.py`: selection is now applied after field widgets are
  created in `update_data`.
- **`ListView` pre-selection must happen after window shows** — calling
  `data_source.select_record()` + `reload()` inside `with bs.App():` sets TTK
  state before the window is mapped. Selected rows render incompletely until the
  first hover/expose event. Pre-select after the `with` block (window is shown)
  and before `app.run()`.
- **`GridFrame` equal columns** — use `uniform=f"col_w{weight}"` in `columnconfigure`
  so equal-weight columns are truly equal regardless of children's minimum sizes.
  Without `uniform`, Tkinter distributes extra space equally but still respects
  each column's minimum, so a field with stepper buttons inflates its column.
- **`tristate=False` default** — boolean controls (Checkbox, Switch, ToggleButton)
  now seed `unchecked_value` by default when no `value=`/`signal=` is given,
  preventing the indeterminate dash from appearing unexpectedly. `tristate=True`
  opts Checkbox into the three-state behaviour (None/True/False).
- **`on_icon`/`off_icon` vs `icon=`** — for stateful widgets (Checkbox, Switch),
  use `on_icon=`/`off_icon=` to show different icons per state. A static `icon=`
  only color-shifts; it does not change shape. ToggleButton may legitimately use
  just one of `on_icon=` or `off_icon=`.
- **`info` color token** — restored as a first-class semantic accent across all
  12 themes (cyan[600] light / cyan[400] dark; teal for forest, blue for ocean).
  Add to `AccentToken`, `token_maps.py`, and `cli/add.py` when creating new themes.
- **Run examples after editing** — always run `python docs/examples/<widget>.py`
  after making changes to verify it launches without errors before committing.
  Runtime bugs (e.g. unsupported kwargs like `wrap=True` on HStack) are invisible
  to static analysis.
- **pydata-sphinx-theme migration** — switched from Shibuya. Key config changes:
  `napoleon_use_param = True` (merges Napoleon Args + typehints into one Parameters
  block); `html_theme = "pydata_sphinx_theme"`; autoclass for boolean controls needs
  `:inherited-members: PublicWidgetBase` to show methods from `_BooleanControlBase`.
- **Switch/ToggleButton unsupported features** — Switch does NOT support
  `on_icon`/`off_icon`/`icon_only`/`show_indicator`/`tristate`/`density`.
  ToggleButton does NOT support `tristate`/`show_indicator`. Only Checkbox
  supports `tristate`. Give these widgets explicit `__init__` overrides so Sphinx
  shows the correct signature (not the full `_BooleanControlBase` signature).
- **`density=` on boolean controls** — Checkbox and Switch do NOT support `density=`
  (removed from their public API). ToggleButton DOES support it via
  `_capture_density_option()` in `CheckToggle`.
- **`TTKWrapperBase.__init__wrapper` overwrites `self._accent`** — composite widgets
  that pop `accent` from kwargs before calling `super().__init__()` will have
  `self._accent` reset to `None` by the wrapper. Fix: store the accent in a local
  variable, call super, then re-assign: `self._accent = accent_value`. Affects
  `_InternalRadioGroup` (fixed) and `_InternalToggleGroup` (already handled).
- **`_InternalRadioGroup` accent bug** — `RadioGroup.add()` uses `self._accent` to
  style buttons, but `_BooleanControlBase.__init__wrapper` was overwriting it to
  `None`. Fixed by storing accent before super() and restoring after in
  `_impl/composites/radiogroup.py`.
- **`ToggleGroup padding=` bug** — fixed. Added `if 'padding' not in kwargs: kwargs['padding'] = 1`
  guard before `super().__init__()` in `_impl/composites/togglegroup.py`.
- **`ToggleGroup state=` not extracted** — `state="disabled"` was leaking through
  to the underlying ttk.Frame which rejects it. Fixed by popping `state` from kwargs
  in `__init__` and applying it to buttons in `add()`.
- **`OptionMenu.style_options` not passed to super** — `icon`, `icon_only`,
  `show_dropdown_button`, `dropdown_button_icon` were being captured into
  `style_options` but the dict was never passed to `super().__init__()`. Fixed in
  `_impl/primitives/optionmenu.py`.
- **`SelectButton`** — new public widget wrapping `OptionMenu` (internal). A
  button-styled, non-editable value picker. Fills the gap between `Select`
  (editable combobox) and `MenuButton` (action menu).
- **Boolean control Sphinx signatures** — widgets that inherit `_BooleanControlBase`
  without overriding `__init__` show ALL base class params in the Sphinx signature
  (including unsupported ones). Give each subclass its own `__init__` that explicitly
  lists only the params it supports.
- **`autoclass` inherited-members for boolean controls** — use
  `:inherited-members: PublicWidgetBase` so `toggle()`, `on_change()`, `on_check()`,
  `on_uncheck()`, `value`, `checked`, `signal`, `disabled` appear in the API docs.
- **ToggleButton variants** — supports `solid`, `outline`, `ghost` like Button.
  Show variants with both inactive and active states side-by-side in the hero
  example so the state transition is visible.
- **RadioGroup `orient` parameter** — affects button layout inside the group.
  Show horizontal and vertical side by side using `HStack`, not as separate sections.
- **Tooltip `_position_anchored` bug (fixed)** — `winfo_width/height` on a freshly
  created withdrawn Toplevel returns the 200×200 default placeholder, not content
  size. Fixed to use `winfo_reqwidth/reqheight` only in `_impl/composites/tooltip.py`.
- **Tooltip hero screenshot** — `docs/screenshots/tooltip.py` simulates hover via
  `btn.tk.event_generate('<Enter>')` at t=600ms (tooltip fires after 250ms delay at
  t=850ms), then sets `topmost=True` at t=900ms so the tooltip wins z-order over the
  app window lifted at t=800ms. Grab at t=950ms captures the live tooltip popup.
- **Toast/Tooltip screenshot z-order** — the screenshot runner sets the app
  `topmost=True` and lifts it at t=800ms. To capture a floating Toplevel (toast,
  tooltip) in the screenshot, show it at t=850ms so it claims topmost AFTER the app.
- **Toast hero** — force-show via `app.tk.after(850, lambda: bs.Toast(..., position='+X+Y').show())`.
  Position must fall within the captured region: app client area is approximately
  `(winfo_rootx, winfo_rooty)` to `(rootx+w, rooty+h)` where the runner places the
  window at `+200+100` on screen.
- **Screenshot runner 2 px inset** — `take_screenshots.py` now crops 2 px from each
  edge of the captured region to remove the Windows window-border artifact.
- **Screenshot blurriness from browser downscaling** — if the captured PNG is wider
  than the docs content column, the browser scales it down and it appears blurry.
  Use `size=(W, H)` (not `minsize=`) on the example App to fix the window to a known
  width. Target ~680-720px to stay within the pydata-sphinx-theme content column.
- **Screenshot blurriness from fractional pixel positions** — narrow content centered
  in a wide window renders text at sub-pixel positions. Fix by using `Grid(fill="x")`
  or `VStack(fill="x")` for all top-level demo sections so content fills the full
  window width and stays at integer pixel boundaries.
- **`**extra_kw` removed from layout wrappers** — `Card`, `GroupBox`, `VStack`,
  `HStack`, `Grid` no longer accept `**extra_kw`. All supported kwargs are now
  explicit. Do not re-add it.
- **`variant=` removed from VStack/HStack** — use `bs.Card` for card-variant layout.
  VStack and HStack are plain layout containers only.
- **`TLabelframe` removed from `CONTAINER_CLASSES`** — it was incorrectly included,
  causing `accent=` to bleed into the surface/background instead of only coloring the
  border. Fixed in `src/bootstack/style/token_maps.py`. GroupBox/LabelFrame `accent=`
  now correctly controls border color only.
- **`height=` / `width=` on VStack/HStack** — setting either disables frame
  propagation. Setting **both** fully constrains the frame with no extra kwargs needed.
  Setting only one collapses the other axis to zero — add `fill=` and `expand=True`
  to let the parent control the unconstrained axis. The underlying pack geometry
  manager has no "minsize" for frames; a Grid-backed refactor is a future improvement.
- **`show_border=True` needs padding** — the border is drawn inside the frame edge.
  Without at least `padding=1`, children render flush against it. Always pair
  `show_border=True` with `padding=` for visual clearance.
- **Grid `columns=N` integer shorthand** — passing an integer creates N equal-weight
  columns. `columns=3` ≡ `columns=[1, 1, 1]`. Same for `rows=N`.
- **Grid `0` weight == `'auto'`** — both map to `(weight=0, minsize=0)` in
  `_parse_size`. Prefer `'auto'` for clarity; `0` reads as a mistake.
- **`bs.Event` type** — `tkinter.Event` is no longer used in public API signatures.
  All `on_*()` callbacks receive a `bootstack.widgets.types.Event` object, which is
  an enriched event with a `data: Any` attribute for application-level payloads.
  The `Event` class is the public type; do not reference `tkinter.Event` in docs or
  docstrings.
- **No Tkinter references in public docs** — the framework goal is to abstract the
  underlying toolkit away entirely. Do not mention "Tkinter", "ttk", or "tk." in
  user-facing docstrings or RST pages. Replace with neutral phrasing:
  "anchor position" not "Tkinter anchor string"; "cell alignment" not "sticky string".
- **Cross-referencing layout widgets** — all layout doc pages should have a "See also"
  section pointing to related containers. Card/GroupBox reference VStack/HStack/Grid;
  VStack/HStack/Grid reference each other and Card/GroupBox. Grid.rst also notes that
  Card and GroupBox support `layout='grid'`.
- **`Expander` is internal** — `bs.Expander` was removed from the public API. It is
  used internally by `Accordion` only. Do not re-export it. The public collapsible
  container is `bs.Accordion`.
- **`Accordion` defaults** — `show_border=True`, `show_separators=True`, and body
  `padding=16` are the defaults. This is the Bootstrap-style bordered accordion.
  Pass `show_border=False` / `show_separators=False` for a plain look.
- **`Accordion` header selected state** — uses `b.subtle()` (light tint, not
  `b.selected()` which darkens 18%). Defined in
  `src/bootstack/style/builders/expander.py` ghost variant. The solid variant uses
  `b.color(accent)` for a full-color selected header. `highlight=True` is set on all
  accordion sections by default.
- **`Accordion` fill default** — `layout_kw.setdefault('fill', 'x')` is set in the
  public wrapper so accordion always fills container width. Without this, headers
  shrink to their text width when content is hidden.
- **One doc page per widget** — never document more than one widget on a single RST
  page, even if they are closely related (e.g. Expander and Accordion are separate).
- **`[bold]` is redundant on heading fonts** — `heading-md`, `heading-lg` etc. are
  already bold. Do not write `font="heading-md[bold]"`.
- **`font="heading-md"` not `font="heading-md[bold]"`** — same as above; use the
  token name only.
- **AppShell `toolbar`/`nav` expose internals** — `shell.toolbar` returns the
  internal composite; use `command=` (not `on_click=`) on it. `shell.nav` returns
  the internal SideNav, not the public wrapper. Do not document them as if they
  were public wrappers.
- **AppShell `nav_pane_width=` not wired** — the parameter isn't threaded through
  to `_build_shell` → `SideNav`. Passing it currently raises `TypeError`. Deferred.
- **API naming standardisation done (Navigation pass)** — renamed across SideNav,
  Accordion, Tabs, AppShell: `on_change` (present tense), `current` property,
  `add_footer_page()`, `item/items/item_keys` instead of `node/nodes/node_keys`,
  `expanded=` instead of `is_expanded=`. Still pending: `on_pane_toggled`,
  `on_display_mode_changed` (SideNav), `on_selection_changed` (ListView),
  `on_date_selected` (Calendar).
- **`Accordion.on_change` / `SideNav.on_change`** — renamed from
  `on_accordion_changed` and `on_selection_changed` respectively. Internal
  `_InternalAppShell` still calls `self._nav.on_selection_changed(...)` — this
  works because it calls the internal SideNav method directly (not the public
  wrapper), but watch for drift if the internal is ever updated.
- **Dialog API conventions (dialogs pass):**
  - `Dialog.__init__` is fully keyword-only; `master=` renamed to `parent=`;
    `minsize=`/`maxsize=` renamed to `min_size=`/`max_size=`.
  - `Dialog.show()` is fully keyword-only.
  - Internal dialog callers (`MessageDialog`, `QueryDialog`, `DateDialog`,
    `_ChromeDialog`, `_InternalFormDialog`) all updated to use `parent=`,
    `min_size=`, `max_size=`.
  - `on_data_changed` → `on_data_change` (present tense) across `Form`,
    `FormDialog` (public + internal).
  - `ButtonRole` simplified to 4 values: `"primary"`, `"secondary"`,
    `"danger"`, `"cancel"`. `"default"` and `"help"` removed.
  - `"link"` was an invalid variant on `"help"` role — replaced with `"ghost"`,
    then role was removed entirely. Always verify variants against
    `VariantToken = Literal['solid', 'outline', 'ghost', 'toggle']`.
  - `Dialog` `content_builder` receives an internal `_Frame` — public widgets
    cannot be used directly inside it via `parent=frame`. Use internal
    `_Label`/`_Frame` primitives from `widgets/_impl/primitives/`.
  - `Frame.configure(surface=...)` does NOT work at runtime — `surface=` is
    constructor-only. To change a frame's surface after creation, use
    `frame.configure_style_options(surface=...)`.
  - `get_theme_color(token)` in `bootstack.style.style` returns the current
    theme's hex color for any accent token (e.g. `"danger"`, `"warning"`).
    Use this instead of hardcoding severity colors.
  - `ask_item()` now uses `SelectBox` (styled, searchable, no arbitrary input)
    instead of raw `Combobox`. Validation in `_on_submit` still checks
    `result not in self._items` as a safety net.
  - Alert/confirm layout: use two empty `_Frame` spacers with `expand=True`
    around the content frame to vertically center it (classic tkinter trick).
  - `severity=` on `alert()`/`confirm()`: auto-rings bell for `"warning"` and
    `"danger"`; auto-derives confirm button color (`"danger"` → danger role,
    `"warning"` → secondary + accent="warning"). Icon color comes from
    `get_theme_color(severity)`.
  - `min_size=` is the public convention (not `minsize=`). `App` runtime still
    uses `minsize` internally — a future cleanup pass should expose `min_size`
    explicitly on `App` like `AppShell` already does.
- **No Widget sizing section on dialog pages** — dialogs open as Toplevel windows,
  not layout-managed widgets. The `fill=`/`expand=`/`row=`/`column=` placement kwargs
  don't apply. Omit the `.. include:: ../shared/widget-sizing.rst` block from all
  dialog doc pages.
- **Dialog category has 7 doc pages** (split complete) — `dialogs.rst` is now
  a toctree-only index. `ColorDropperDialog` is internal to `ColorChooserDialog`,
  not a standalone public class.
- **`ColorChooserDialog` internal cleanup pending** — `on_dialog_result()` /
  `off_dialog_result()` on the internal class are unused by the public wrapper and
  add noise. Candidate for removal in a future cleanup pass. The public wrapper uses
  the blocking `show()` + `result` pattern; no `on_*` event needed.
- **Dialog hero screenshot pattern** — open dialog non-modally at t=200ms
  (`dialog.show(modal=False)`), then call `toplevel.attributes("-topmost", True)`
  + `toplevel.lift()` at t=850ms. The dialog appears centered on the app window.
  Screenshot at t=950ms captures the dialog on top. See `docs/screenshots/dialog.py`
  as the reference. For oversized dialogs (FontDialog: 800x600), pass an explicit
  `position=(200, 70)` and size the app to match: `position=(200, 70)` places
  dialog title bar above the capture region so content starts at the screenshot top.
- **`colorchooser.py` / `fontdialog.py` / `filterdialog.py` used `master=`** in
  their internal `Dialog()` calls — already fixed to `parent=`. Check any new
  dialog implementations for this.
- **`fontdialog.py` scrollbar `variant="round"`** — round is not a valid scrollbar
  variant (only `"default"`). Fixed. Do not use `variant="round"` on Scrollbar.
- **`filterdialog.py` used `minsize=`/`maxsize=`** instead of `min_size=`/`max_size=`
  in `Dialog()` — fixed. Always use `min_size=`/`max_size=` with `Dialog`.
- **`ColorChoice` namedtuple** — `namedtuple('ColorChoice', 'rgb hsl hex')`. Exported
  as `bs.ColorChoice`. Fields: `rgb=(r,g,b)` 0–255, `hsl=(h,s,l)` 0–360/0–100/0–100,
  `hex` lowercase hex string.
- **`ColorChooser` tabs removed** — the Advanced/Themed/Standard `TabView` was
  removed; the chooser now shows the spectrum directly with no tab navigation. Also
  removed: `STD_SHADES`, `STD_COLORS`, `create_swatches()`, `on_press_swatch()`.
- **Dialog `show(position=, modal=)` on all wrappers** — `FormDialog`, `ColorChooserDialog`,
  `FontDialog`, `FilterDialog` all expose `position: tuple[int,int] | None` and
  `modal: bool | None` on their `show()` method. Pass through to the internal dialog.
- **`app._capture_target` pattern for dialog screenshots** — set this attribute on
  the `App` instance to a Toplevel; the screenshot runner captures that window instead
  of the app window. Uses `winfo_rootx/y` for left/content-area alignment and
  `geometry()` for the outer-frame y (includes title bar). Defined in
  `docs/scripts/take_screenshots.py` `_RUNNER._grab`.
- **`bs-dialog-screenshot` CSS class** — add to all dialog screenshot `<img>` tags
  (in place of the inline `border-radius:6px`). Defined in `docs/_static/custom.css`.
  Adds a 1px border + soft drop shadow appropriate for isolated dialog window captures.
  Regular widget screenshots keep `bs-screenshot-light/dark` only.
- **`FontDialog.result` typed as `Any`** — intentional; avoids surfacing
  `tkinter.font.Font` in the public API. The actual return is a `font.Font` object;
  the docstring explains it. Don't change to `font.Font | None` as that would require
  importing tkinter in the public surface.

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
`variable=` in the public API.

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
