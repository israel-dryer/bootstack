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

### What's next

Continue widget by widget through the API categories in this order:
Data Display → Layout → Navigation → Overlays → Dialogs → Forms.

Suggested next (Data Display category): ListView, Tree, Table.

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
   - Expand class docstring: valid values, defaults, behavior notes per kwarg

3. **Write `docs/api/<widget>.rst`** — structure:
   - Brief intro + one code snippet
   - `.. raw:: html` light/dark screenshot block (see pattern below)
   - `Usage` section: one sub-section per feature (accents, variants, icons, states, etc.)
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

### Gotchas discovered during the docs pass

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
