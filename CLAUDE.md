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

**Branch strategy:** `feat/*` branches off `main` for widget/API work. PRs go
`feat/*` → `main`.

---

## Strategic direction (as of Session 26)

The focus is API redesign — a clean public layer over the existing internal
widgets, abstracting Tkinter away entirely. bootstack is pre-release; there
is no v1 in the wild, so there is no backward-compat pressure. Rename, remove,
and restructure freely. Key decisions are settled below. Performance is resolved
(PR #53). Docs will be redone from scratch after the API is stable.

---

## Target API design decisions (settled — Session 26)

These were arrived at by reviewing `ttkbootstrap-next` (a prior reference
implementation) and an Opus architectural review.

### Widget layer

The public API is a **wrapper layer** over the existing internal widgets.
Internal widgets keep their current implementation; the public layer owns
naming, kwargs, Signal integration, layout, and context parenting. Users never
touch `tk.*` or `ttk.*`.

- Per-widget complexity varies: simple primitives may be the internal widget
  with a modernized interface; composites wrap the internal widget as a delegate.
- **Escape hatch:** every public widget exposes `.tk` (read-only property) that
  returns the underlying `tk.Widget` / `ttk.Widget`. Same convention for
  Signals: `signal.tk` returns the underlying `tk.Variable`. Named `.tk` not
  `.native` (which implies platform-native Win32/Cocoa) or `.internal`.
  Documented as unsupported — anything done through `.tk` is on the user.

### App window layout

`App` behaves as a `VStack` from the user's perspective — it accepts the same
child-guidance kwargs (`padding`, `gap`, `fill_items`, `expand_items`,
`anchor_items`). App-level kwargs (`title`, `size`, `settings`) are cleanly
separate with no naming collisions.

Internally, `App` wraps a content frame that fills the root window. Children
are placed into the content frame, not the `tk.Tk` root directly:

```
tk.Tk  (root window — title, size, theme, chrome)
  └── content frame  (internal VStack — padding, gap, fill_items)
        ├── child 1
        ├── child 2
        └── child 3
```

The content frame is an implementation detail — users never interact with it.
`app.tk` returns the `tk.Tk` root. `App.guide_layout()` delegates to the
content frame's pack guidance. Layout kwargs on `App` configure the guidance
it provides to children, not its own placement (App has no parent).

```python
with bs.App(title="My App", size=(800, 600), padding=16, gap=8) as app:
    bs.Label("Header")
    bs.Button("OK")
```

### Context-manager parenting

Thread-local context stack (same pattern as ttkbootstrap-next). `parent=`
is optional — omitting it uses the current context; passing it explicitly
overrides the stack. This covers dynamic widget creation outside `with` blocks.

```python
# Context-managed (common case)
with bs.App(title="Demo") as app:
    with bs.HStack(padding=8, gap=4):
        bs.Label("Hello")
        bs.Button("OK", on_click=lambda: ...)
app.run()

# Explicit parent (dynamic / programmatic case)
btn = bs.Button("Add", parent=toolbar, on_click=handler)
```

- `__enter__` pushes the container onto the stack; `__exit__` pops it.
- Child widgets resolve parent as: explicit `parent=` kwarg → context stack →
  root window.
- App hides the root window on enter, shows it on exit (eliminates flash of
  unstyled content). Only `App.__exit__` calls `update_idletasks()`.

### Layout — inline kwargs, no `.attach()`

Layout options live in the widget constructor, not a separate method call.
The container knows its layout manager; it strips layout kwargs before they
reach the widget:

```python
with bs.Row():
    bs.Label("Name:", width=80)
    bs.Entry(textsignal=name, fill="x", expand=True)

with bs.Grid(columns=[120, 1]):
    bs.Label("Name:")          # auto row/col
    bs.Entry(textsignal=name)
    bs.Label("Email:")
    bs.Entry(textsignal=email)
```

- `PACK_KEYS`, `GRID_KEYS`, `PLACE_KEYS` are module-level frozen sets.
  Base widget `__init__` splits kwargs before constructing the internal widget.
- Container `guide_layout(child, method, options)` merges container defaults
  (gap, fill_items, expand_items) with per-child overrides — same guidance
  pattern as ttkbootstrap-next, but child placement is automatic (no
  `.attach()` call required).
- Presence of `x`/`y`/`relx`/`rely` in kwargs signals absolute positioning —
  the container uses `place()` instead of `pack()`/`grid()`. No separate
  method needed. `PLACE_KEYS` will need care to avoid colliding with widget-level
  options (`width`, `height`, `anchor` appear in both); aliasing/renaming
  deferred until public property names are settled per-widget.
- Public containers: `HStack`, `VStack`, `Grid`, `Card` (with `layout="pack"|"grid"`).
  No public `Frame` — plain containers are always one of these four.
  `place()` is internal only; absolute positioning exposed via inline kwargs.
- One free function `bs.attach(widget, **layout_kw)` as escape hatch for
  widgets built outside a `with` block.

### Positional arguments for primary content

Common widgets accept their primary content as the first positional argument.
The "primary content" is the most commonly passed, unambiguous value:

```python
bs.Button("Save")                  # label
bs.Label("Hello world")            # text
bs.Badge("21+")                    # text
bs.CheckButton("Enable feature")   # label
bs.RadioButton("Option A")         # label
bs.Entry("placeholder")            # placeholder text (optional, less clear — TBD)
```

Not all widgets get a positional — only those where the first argument is
unambiguous. Composites and containers with multiple required config values
use kwargs only. The positional is always optional; kwargs are always accepted
as the alternative.

### Events — `on`, `emit`, `Subscription`

`bind` / `unbind` / `event_generate` are internal only. The public API uses:

```python
# Subscribe
sub = widget.on(Event.Input.CHANGE, handler)
sub = widget.on_change(handler)          # typed shorthand, same return type

# Unsubscribe — no off_* methods, subscription is self-contained
sub.cancel()

# Fire
widget.emit(Event.Input.CHANGE, data={"value": 42})

# Scoped lifetime
with widget.on(Event.Widget.CLICK, handler):
    do_something()   # handler active only within block

# Escape hatch
widget.tk.bind("<<SomeObscureEvent>>", handler)
```

**`Subscription` class** — returned by all `on`/`on_*` calls:
- `.cancel()` — unbinds the handler
- Context manager support — cancels on `__exit__`
- Internally wraps the Tk bind ID; users never see it

**Event name resolution — two-level lookup:**
1. Widget-specific map checked first (e.g. `TreeView` `"select"` →
   `<<TreeviewSelect>>`)
2. Global map fallback (e.g. `"click"` → `<Button-1>`)
3. Unknown name → `UnknownEventError` with helpful message

Both `<...>` (built-in Tk) and `<<...>>` (virtual) events are mapped.
String literals always work as fallback; the enum is preferred.

**`Event` namespace** — categorized, discoverable, type-safe:

```python
class Event:
    class Widget:
        CLICK        = "click"
        DOUBLE_CLICK = "double_click"
        RIGHT_CLICK  = "right_click"
        HOVER        = "hover"
        LEAVE        = "leave"
        FOCUS        = "focus"
        BLUR         = "blur"
        RESIZE       = "resize"

    class Input:
        CHANGE       = "change"
        SUBMIT       = "submit"
        VALIDATE     = "validate"

    class Selection:
        SELECT       = "select"
        DESELECT     = "deselect"

    class App:
        THEME_CHANGE = "theme_change"
        PAGE_MOUNT   = "page_mount"
        PAGE_UNMOUNT = "page_unmount"
```

Enum values are plain strings — `on("change", ...)` and
`on(Event.Input.CHANGE, ...)` are equivalent. The enum adds discoverability
and IDE autocomplete, not a separate type system.

`emit` uses the same two-level lookup as `on` — clean names always resolve
to the same Tk sequence for both directions.

### Signals only — no tk.Variable in the public API

`variable=` and `textvariable=` are removed from the public API entirely.
Signal is the only reactive primitive.

- Signal continues to wrap `tk.Variable` internally — the Tcl variable is
  the two-way broadcast bus and is not bypassed.
- Widgets accept `signal=` / `textsignal=` only. Raw values auto-wrap:
  `bs.Entry(textsignal="hello")` creates a `Signal("hello")` internally;
  `.textsignal` returns it.
- `signal.tk` exposes the underlying `tk.Variable` for interop.

### Sizing contract for canvas-based widgets

No deferred construction — Tk's geometry pass is already lazy, and
`after_idle` deferral produces unreadable tracebacks.

- Canvas/size-sensitive widgets inherit a `SizedWidget` mixin.
- `_on_size(width, height)` fires once real dimensions are known (first
  `<Configure>` where both dims > 1), coalesced via `after_idle`.
- `winfo_*` size reads are forbidden in `__init__`.
- `widget.when_sized(callback)` — one-shot helper that fires once the widget
  has real dimensions. Cleaner than wiring `<Configure>` for the common case.
- Slider/RangeSlider already follow this pattern correctly.

### Configuration and properties

The existing `configure_delegate` pattern already makes virtually everything
runtime-settable — no explicit construction-only restrictions exist in the
current codebase. The v2 property layer is largely surfacing this as Python
properties rather than routing through `configure()`.

**Three downstream patterns cover the whole codebase:**
- TTK widgets: `configure_style_options()` + `rebuild_style()` — re-runs
  the style builder, generates a new hashed TTK style name
- Canvas widgets (Slider, Meter): calls `_draw()` directly, bypasses the
  style builder
- Pure state (value, variable, font): direct delegation, no rebuild

**Property vs configure in v2:**
- Properties are the primary interface — `widget.accent = "success"` not
  `widget.configure(accent="success")`
- `configure(**kwargs)` is kept for the dynamic/programmatic case, but
  accepts public API names only (not Tk names) and dispatches to property
  setters internally
- `cget()` is removed from the public API — use properties directly
- `on_*` / `off_*` replaced by `on()` returning `Subscription` (see Events)

**Structural variation → separate classes**, not constructor flags. The "same
widget, different structure" problem (e.g. horizontal vs vertical) is best
solved by separate classes where the variation is significant, following Qt's
`QLineEdit` vs `QTextEdit` precedent. bootstack already does this well
(`Slider` vs `RangeSlider`, `Entry` vs `TextArea`).

### Width — character vs pixel units

For TTK text-bearing widgets (`Label`, `Button`, etc.), `width` is in
character units. Negative values do NOT mean pixels on ttk widgets (tested:
`width=-10` produces the same result as `width=10`).

For pixel-based sizing in v2:
- Use `min_width` / `min_height` (maps to geometry manager `minsize`)
- Use layout column/row weights for proportional sizing
- `ttk.Frame`-based containers (`HStack`, `VStack`, `Grid`) already accept
  pixel dimensions directly since Frame `width`/`height` are always pixels

### Layout kwargs — self-placement vs child guidance

Every layout container needs **two** sets of kwargs:

```python
HStack(
    # Self-placement (consumed by parent's guide_layout when THIS widget
    # is a child of another container):
    fill="both", expand=True,

    # Child guidance (how THIS widget lays out its own children):
    gap=8, fill_items="x", expand_items=True, padding=16
)
```

Parent strips the self-placement set; the widget uses the child-guidance set.
No name collision: `fill` vs `fill_items`, `expand` vs `expand_items`, etc.

### Spacing — margin vs padding

CSS conventions apply throughout v2:
- `margin` — space **outside** the widget, between it and siblings/container
  (was `padx`/`pady` in Tk)
- `padding` — space **inside** the widget, between its border and content
  (was `ipadx`/`ipady` in Tk)

Both accept: `int` (uniform), `(x, y)` tuple, or `(left, top, right, bottom)` (ttk convention).

### Dialogs and one-shot functions

**Two patterns only — no static-method-class pattern in the public API:**

**Module-level functions** for simple one-shot interactions:
```python
bs.alert("Operation complete.")              # message, no return
bs.confirm("Delete this record?")           # → bool
bs.ask_string("Enter your name:")           # → str | None
bs.ask_integer("Enter age:", min_value=0)   # → int | None
bs.ask_float("Enter value:")                # → float | None
bs.ask_date("Select start date:")           # → date | None
bs.ask_item("Choose one:", options=[...])   # → str | None
```

**Classes for complex dialogs** where you configure, show, and inspect:
```python
dlg = bs.FormDialog(title="Settings", items=[...])
dlg.show()
if dlg.result:
    process(dlg.result)
```

`MessageBox` and `QueryBox` classes are removed from the public API —
their methods become module-level `bs.*` functions. Internal singletons
(`Style`, `Typography`, `Publisher`) remain internal; user-facing helpers
(`bs.set_theme()`, `bs.get_theme()`) are the API.

### Widget consolidation decisions

- **`FloodGauge` → removed.** A v2 `ProgressBar` absorbs what was useful
  (canvas rendering, text overlay, flood-fill visual) into one well-designed
  widget. `FloodGauge` was a ttkbootstrap artifact.
- **`Meter` → `Gauge`, kept and modernized.** Circular gauges are genuinely
  useful for engineering/scientific dashboards. API cleanup needed (deprecated
  params still in source). Renamed to `Gauge` to drop ttkbootstrap association.
- **`Combobox` → removed.** Replaced by `Select` (was `SelectBox`). Covers
  the use case with a better API and popup list.
- **`Spinbox` → kept.** Distinct form factor from `NumberField` — cycles
  through a fixed list of text or numeric values; different visual and use case.

### Pre-work before implementation starts

1. ~~`Style._tk_widgets` WeakSet + visibility guard~~ — done (PR #53)
2. ~~`autostyle` container-level opt-out~~ — done (Session 27, `_bs_autostyle = False`
   class attribute; checks class and parent before registering a tk widget)

---

## Code standards (settled — do not relitigate)

### Docstring conventions

Class docstrings hold:
1. One-line summary
2. One-paragraph description
3. `Args:` on `__init__` (param name only — no type, the signature has it)
4. `Attributes:` **only** for runtime-assigned names invisible to griffe
   (e.g. `self.x = ...` in `__init__` that has no corresponding `@property`)

Class docstrings do **not** hold: `!!! note "Events"` admonitions, `Example:`
blocks, behavioral prose, "See also" lists.

Param line format: `name: description` — never `name (type): description`.
Type is already in the signature. Never RST roles (`:class:\`X\``). Use single
backtick only: `` `X` ``, never ` ``X`` `.

### `on_*/off_*` event handler standard

- Opener: `"Register a callback for \`<<EventName>>\` events."`
- Callback type: `Callable[[XEventData], None]` when TypedDict exists; `Callable` otherwise
- Returns: `"Bind ID — pass to \`off_*()\` to unsubscribe."`
- `off_*` opener: `"Unsubscribe from \`<<EventName>>\`."`
- `off_*` arg: `bind_id: str | None = None` — `"ID returned by \`on_*()\`. If None, removes all."`
- TypedDict required for payloads with 2+ keys or complex types
- Signal-based widgets (RadioGroup, ToggleGroup, Tabs): same pattern; `bind_id: Any`

### No `!!! warning` for type errors

Reserve warnings for runtime gotchas the type system can't catch (deprecation,
version-specific behavior, ordering hazards, mutation traps). Do not warn about
invalid types when the type signature already restricts callers.

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

All public names accessible via `bs.*`. Internal paths with `_` prefix are not
for direct import.

**`widgets/types.py` public types:**
- Primitive aliases: `Master`, `EventCallback`, `CommandCallback`
- Geometry: `Anchor`, `Orient`, `Justify`, `Relief`, `CompoundMode`, `Fill`, `Sticky`, `Side`, `BorderMode`, `Direction`
- State/density: `WidgetState`, `WidgetDensity`
- Styling tokens: `AccentToken`, `VariantToken`, `SurfaceToken`
- Base TypedDicts: `BaseWidgetKwargs`, `StyledKwargs` (all primitive `*Kwargs` inherit from `StyledKwargs`)

---

## Key API reference

```python
import bootstack as bs

# App
app = bs.App(title="...", size=(w, h))
app.mainloop()

# AppShell
shell = bs.AppShell(title="...", size=(w, h))
page = shell.add_page("key", text="Label", icon="icon-name")
shell.toolbar.add_button(icon="...", command=...)

# Layout
bs.PackFrame(parent, direction="vertical|horizontal|row|column|row-reverse|column-reverse",
             gap=N, padding=N, fill_items="x|y|both|none",
             expand_items=True, anchor_items="n|ne|e|se|s|sw|w|nw|center")
bs.GridFrame(parent, rows=N|[...], columns=N|[...], gap=N|(col_gap, row_gap),
             sticky_items="ew|nsew|...", auto_flow="row|column|row-dense|column-dense|none")
bs.VStack(variant='card', padding=16)  # card surface; show_border=True default
bs.GroupBox(title="Section", layout='vstack', padding=16)  # bordered section with title

# Signals
sig = bs.Signal(value)  # widgets accept signal=sig or textsignal=sig

# Icons — Bootstrap Icons catalog
bs.Button(parent, icon="house")   # https://icons.getbootstrap.com/

# Color tokens
accent="primary|secondary|success|warning|danger|info|light|dark"
variant="solid|outline|ghost|link|toggle"
surface="content|card|chrome|overlay|input"
# Modifiers: "primary[+1]", "primary[500]", "primary[subtle]", "primary[100][muted]"

# Font tokens
font="body"  |  font="heading-lg[bold]"  |  font="body+2[italic]"
```

### API gotchas

- **`bs.App` does not accept `theme=`, `locale=`, `light_theme=`, `dark_theme=`
  as direct kwargs.** Use `settings={"theme": "..."}` or `AppSettings`. Exception: `localize=` IS a direct kwarg.
- **`bs.Form` uses `col_count=`, not `columns=`.**
- **`Form.validate()` only fires rules with trigger `always` or `manual`.** `blur`/`key` rules are skipped.
- **`Dialog.show()` / `FormDialog.show()` return `None`** — set `self.result`. Use `dlg.show(); if dlg.result: ...`
- **`bs.Table` only accepts `SqliteDataSource`**, not `MemoryDataSource` or `FileDataSource`.
- **`bs.Select` (internal `SelectBox`) emits `<<Change>>`**, not `<<SelectionChange>>`.
- **All Field-based widgets emit `<<Change>>`** (not `<<Changed>>`) and `<<Validate>>`** (not `<<Validated>>`).
- **`on_changed`/`on_input` callbacks receive a Tkinter event object** (`event.data["value"]`).
  **`on_valid`/`on_invalid`/`on_validated` callbacks receive a plain dict** (`data["value"]`).
- **`text=Signal(...)` does NOT work for reactive labels.** Use `textsignal=signal` instead.
- **`bs.Label` uses `.text` not `.value`** to get/set the display string. This is intentional — `.text` is semantically correct for a display-only widget; `.value` is reserved for data-bearing widgets (Entry, Checkbox, Slider, etc.).
- **`value=` is ignored when `signal=` or `variable=` is also passed** on CheckButton,
  CheckToggle, Switch, RadioButton, RadioToggle. Seed the Signal directly: `bs.Signal(True)`.
- **`ToggleGroup(padding=N)` raises `TypeError`** — source bug, do not pass `padding=`.
- **`insert_addon` with `bs.CheckButton` raises `TclError`** — `density=` leaks to ttk. Use `bs.CheckToggle`.
- **`Field.variable` / `Field.signal` are `@property`.** Read-only.
- **`bs.L(key, *fmtargs)` uses positional `%s`/`%d` format args**, not `{name}` kwargs.
- **`bs.Form` button command lambda receives the form as first arg:** `lambda f: print(f.value)`.
- **`RadioGroup.set()` validates against keys, not values.**
- **`Accordion.items(expanded=True/False)` filters by expansion state.**

---

## Open source bugs

See memory `project_api_gaps.md` for full list. Key items:
- `ToggleGroup` `padding=` kwarg causes `TypeError`
- `insert_addon` passes `density=` to `CheckButton` causing `TclError`
- `Meter` deprecated param names (`amountused`, `amounttotal`, `subtext`, `stripethickness`) not yet removed from source
- `value=` silently ignored when `signal=`/`variable=` also passed (all boolean widgets)
- `ToggleGroup` solid (default) variant has poor contrast — selected button text is hard to read against the filled background; user handling `src/bootstack/style/builders/toolbutton.py`
- `Style._tk_widgets` grows forever — destroyed widgets never removed; causes theme-change slowdown *(partially resolved in Session 26 — WeakSet + visibility guard; remaining issue is pages are never destroyed)*
- `TextField` `placeholder=` not supported — `TextEntry` composite (single-line) was never given placeholder logic; `TextArea` has it, `TextField` does not
- `TabView` pill variant — never implemented; removed from type signatures and docstrings (Session 39)
- `Label`/`Badge` use `.text` (not `.value`) — this is settled and intentional; `.value` is for data-bearing widgets only

---

## Handoff log

### Session 28 — public layer plan (2026-05-28)

- **`development/v2_base_layer_plan.md`** — full implementation plan for the
  public API base layer. 7 phases (A foundations → B `PublicWidgetBase`
  → C container protocol → D `HStack`/`VStack`/`Grid` → E `App` →
  F reference `Button` → G smoke tests). Dependencies and acceptance
  criteria are explicit; per-widget migration is deferred.
- **Key architectural decisions:**
  - **Composition, not inheritance.** Public widgets are plain Python
    objects holding an internal `tk.Widget` as `self._internal`, reachable
    via the `.tk` property. They are NOT `tk.Widget` subclasses. Reasons:
    avoids shadowing `tk.Widget.tk` (the Tcl interp handle), and makes
    `.pack()`/`.bind()` physically inaccessible on public widgets so the
    escape hatch (`widget.tk.pack(...)`) is the only path to raw Tk.
  - **File location:** `src/bootstack/widgets/public/` during development. No
    edits to existing `widgets/primitives/*` or `_runtime/*` except a
    one-line `Signal.tk` property alias.
  - **`App` owns an internal `PackFrame` content frame.** `app.tk` returns
    the `tk.Tk` root; children are parented to and placed in the content
    frame via `App._child_master()` returning `self._content_frame`. The
    settled "App behaves as a VStack" design.
  - **Layout-key splitting** lives in
    `PublicWidgetBase._split_layout_kwargs`, called before the internal
    widget is constructed so pack/grid kwargs never leak into the ttk
    ctor. `PACK_KEYS`, `GRID_KEYS`, `PLACE_KEYS`, `PLACE_TRIGGER_KEYS` are
    module-level frozensets in `public/container.py`. PLACE collisions on
    `width`/`height`/`anchor` are left as widget options (deferred per
    earlier CLAUDE.md decision).
  - **Event resolution is two-level:** widget-class map (walked via MRO)
    → `GLOBAL_EVENT_MAP` → literal `<...>` pass-through → `UnknownEventError`.
    `Event.Widget.CLICK` etc. are `str`-valued enum members so they
    compare equal to plain strings. The global map holds only true
    cross-widget events; widget-specific virtuals like `<<TreeviewSelect>>`
    register per-class via `register_widget_events(cls, mapping)`.
  - **`Subscription`** wraps `(internal_widget, sequence, bind_id)`. Holds
    a reference to the internal widget so `.cancel()` can call
    `unbind(sequence, bind_id)`. Idempotent; context-manager support.
  - **Constructor order** for every public widget: resolve parent → split
    layout kwargs → construct internal → attach to parent. Subclasses
    don't call `super().__init__()` (there is no Python super to call);
    base provides static helpers.
- **Next step:** Sonnet executes the plan on branch `feat/public-api-base`.

### Session 27 — API design + autostyle pre-work (2026-05-28)

- **Extensive API design session.** All target API decisions settled and
  documented in the "Target API design decisions" section above.
- **`development/v2_api_proposal.md`** — full per-widget API mapping (40+
  classes, every kwarg/method/property/event) from current to target API,
  generated by Opus and corrected against session decisions.
- **autostyle pre-work complete:** `_bs_autostyle = False` class attribute on
  `Slider` and `RangeSlider` replaces 8 per-call `autostyle=False` kwargs.
  The `override_tk_widget_constructor` wrapper now checks:
  1. `type(self)._bs_autostyle` — widget's class opts out
  2. `master._bs_autostyle` — parent opts out children
  Future canvas-based composites just set `_bs_autostyle = False` on the class.
- **Ready for implementation.** All pre-work done. Next step: Opus plans the
  base layer implementation (see briefing below); Sonnet executes.

---

## v2 base layer — implementation status

**Plan written:** `development/v2_base_layer_plan.md` (Session 28). Covers
the base layer only: context stack, `PublicWidgetBase`, `Subscription`,
`Event` enum + two-level resolution, container `guide_layout` protocol,
`HStack`/`VStack`/`Grid`, `App`, and `Button` as a reference primitive.
Structured in 7 phases (A–G) with explicit dependencies and acceptance
criteria. Per-widget migration of the remaining ~40 widgets is out of scope
for the first PR and follows after the base layer lands.

**Branch:** `feat/public-api-base` off `main`. New code lives at
`src/bootstack/widgets/public/`; no edits to existing `widgets/primitives/*` or
`_runtime/*` except the `Signal.tk` property alias (Phase A6).

**Status: COMPLETE (Session 29).** All 7 phases implemented and passing.
All acceptance criteria met. Next step: open PR `feat/public-api-base` → `main`,
then begin per-widget migration.

### Session 29 — public layer implementation (2026-05-28)

- **All 7 phases implemented** on `feat/public-api-base`.
- **Files created under `src/bootstack/widgets/public/`:**
  - `exceptions.py` — `BootstackV2Error`, `UnknownEventError`, `ParentResolutionError`
  - `events.py` — `Event` namespace (`_Widget`, `_Input`, `_Selection`, `_App`);
    `GLOBAL_EVENT_MAP`; `register_widget_events`; `resolve_event` (two-level lookup)
  - `subscription.py` — `Subscription` (idempotent cancel, context-manager support)
  - `context.py` — thread-local container stack (`push_container`, `pop_container`,
    `current_container`)
  - `container.py` — `PACK_KEYS`, `GRID_KEYS`, `PLACE_KEYS`, `PLACE_TRIGGER_KEYS`
    constants + `PublicContainer` class with `guide_layout`, `__enter__`/`__exit__`
  - `base.py` — `PublicWidgetBase` with `_resolve_parent`, `_split_layout_kwargs`,
    `_attach_to_parent`, `.tk` property, `.on()`, `.emit()`
  - `stacks.py` — `HStack`, `VStack` (wrap `PackFrame`)
  - `grid.py` — `Grid` (wraps `GridFrame`)
  - `app.py` — `App` (wraps `_runtime.app.App` + internal `PackFrame` content frame)
  - `primitives/button.py` — reference `Button` implementation
  - `__init__.py` — re-exports all public symbols
- **`Signal.tk` property** added to `src/bootstack/signals/signal.py` (aliases `var`).
- **Circular import** between `base.py` and `container.py` resolved by lazy import
  of layout key constants inside `_split_layout_kwargs` static method.
- **Tests:** `tests/widgets/public/test_base_layer.py` — 11 non-GUI tests (context
  stack, kwarg splitting, event resolution, subscription, Event enum), 6 GUI-gated
  integration tests. All 11 non-GUI tests pass; `pytest.mark.gui` registered in
  `pyproject.toml`.
- **Acceptance criteria verified:** imports, `btn.tk` returns `ttk.Button`,
  `Subscription.cancel()` works, `UnknownEventError` raised for unknown events,
  no regressions in existing test suite.

### Session 30 — Per-widget migration (2026-05-28)

Continued migrating internal widgets to the public layer. All widgets live in
`src/bootstack/widgets/public/primitives/`. Each PR followed the same pattern:
wrap the highest-level internal, rename Tk-isms, add a visual test under
`tests/features/`, open PR.

**Widgets completed this session (all merged to `main`):**
- **PR #55** — `Label`, `Badge` (`_internal_class` pattern for Badge subclass)
- **PR #56** — `TextField` (wraps `composites/TextEntry`; overrides `on()` to
  route `<<Change>>` etc. to inner `_entry`)
- **PR #57** — `Checkbox`, `Switch`, `ToggleButton` (shared `_BooleanControlBase`;
  `command=` wired to generate `<<Change>>`/`<<ToggleOn>>`/`<<ToggleOff>>`)
- **PR #58** — `RadioGroup` (fixes `options=` gap; signal trace → `<<Change>>`)
- **PR #59** — `Select` (wraps `SelectBox`), `NumberField` (wraps `NumericEntry`;
  `min_value=`/`max_value=`/`step=` replace `minvalue=`/`maxvalue=`/`increment=`)
- **PR #60** — `Slider`, `RangeSlider` (canvas-based; events fire on widget directly;
  value setters coerce to float; `RangeSlider.value` → `(lo, hi)` tuple)
- **PR #61** — `ProgressBar`, `Gauge` (wraps `Meter`; **fixes Progressbar setter
  infinite recursion** — `get()`/`set()` now call `ttk.Progressbar` directly);
  `meter_type=` replaces internal `meter_type=` (public name settled as `meter_type=`)
- **PR #62** — `Spinbox`, `Separator`; **fill= aliases** (`"horizontal"`→`"x"`,
  `"vertical"`→`"y"`, `"all"`→`"both"`) in `container.py`/`stacks.py`/`app.py`
- **PR #63** — `PasswordField` (`mask_char=`, `show_visibility_toggle=`, `reveal()`/`hide()`),
  `TextArea` (`_core.text` event routing; `placeholder=` supported; `select_all()`
  fix: `focus_set()` + `end-1c`)
- **PR #64** — `Expander` (`PublicContainer`; children → `_content_frame`),
  `Accordion` (`add()` → `_AccordionSection` context manager), `ToggleGroup`
  (fixes `options=` gap; `mode='single'|'multi'`)

**Key patterns established:**
- Field-composite wrappers (TextField, Select, NumberField, PasswordField) override
  `on()` to route input events to `self._internal._entry`
- TextArea routes events to `self._internal._core.text`
- Canvas/frame widgets (Slider, ProgressBar, Expander) bind directly on `self._internal`
- `_BooleanControlBase` / `_internal_class` for shared-constructor widget families
- Signal trace → `event_generate("<<Change>>")` for composites whose change
  notification doesn't go through Tk's bind system (RadioGroup, ToggleGroup)

**Bugs fixed in internals:**
- `Progressbar.get()`/`set()` infinite recursion — bypasses delegate with
  `ttk.Progressbar.configure(self, ...)` directly
- `TextArea.select_all()` — needs `focus_set()` and `"end-1c"` not `"end"`

**Known issues logged (see Open source bugs above):**
- `TextArea` border: raw Tk Text border instead of Field-style themed border
- `ToggleGroup` solid variant: poor contrast on selected buttons
- Field composite default width grows with addon slots (gap #13)

**Next steps after Session 30:** `Tabs`, `Toast`, `Tooltip`, `Card`, `ListView`,
`TreeView`, `TableView`, `AppShell`, `Window` — all completed in subsequent sessions
(see PRs #65–75). API drift cleanup and misc-widgets batch followed (Session 31).

### Session 31 — API drift cleanup + SelectBox bug fixes (2026-05-28)

Full audit of all public wrappers against `development/v2_api_proposal.md` revealed
widespread drift in class names and kwarg names. All drift fixed in `fix/public-api-drift`
branch (commit a857ef2) before continuing misc-widgets work.

**Class renames (file renames + rewrites):**
- `NumericEntry` → `NumberField` (`numericentry.py` → `numberfield.py`)
- `PasswordEntry` → `PasswordField` (`passwordentry.py` → `passwordfield.py`);
  `show_toggle=` → `show_visibility_toggle=`
- `TreeView` → `Tree` (`treeview.py` → `tree.py`)
- `TableView` → `Table` (`tableview.py` → `table.py`)

**Kwarg renames across 10 widgets:**
- `Gauge`: `style=` → `meter_type=`, `step_size=` → `step=`
- `ProgressBar`: `maximum=` → `max_value=`
- `Slider`: `tick_interval=` → `tick_step=`
- `RangeSlider`: `lo_value/hi_value` → `low_value/high_value`; `lo_signal/hi_signal` →
  `low_signal/high_signal`; `.lo`/`.hi` properties → `.low_value`/`.high_value`
- `RadioGroup`: `label=` → `title=` (group border label; still maps to internal `text=`)
- `Select`: `allow_custom=` → `allow_custom_values=`
- `Tabs`: `enable_closing=` → `allow_close=`, `enable_adding=` → `allow_add=`,
  `add()` `text=` → `label=`
- `ListView`: `datasource=` → `data_source=`, `enable_removing=` → `allow_remove=`,
  `enable_dragging=` → `allow_reorder=`, `show_separator=` → `show_separators=`,
  `.datasource` property → `.data_source`
- `Toast`: `memo=` → `detail=`, `buttons=` → `actions=`, `alert=` → `play_sound=`,
  `on_dismissed=` → `on_dismiss=`
- `Tooltip`: `wraplength=` → `wrap_width=`

**SelectBox internal bug fixes** (in `widgets/composites/selectbox.py`):
- Disabled `Select` no longer opens popup on field click — `_show_selection_options`
  now checks `entry_widget.instate(['disabled'])` and returns early.
- Readonly entry (non-searchable, non-custom mode) now shows `hand2` pointer cursor
  set in `_bind_readonly_selection_on_click`.

**Naming convention confirmed:** "Field" suffix is correct for all text-input widgets
(matches MUI, Radix, SwiftUI, Compose). `DateField` could arguably be `DatePicker`
(more universal) but not urgent. `TimeEntry`/`SpinnerEntry` pending migration as
`TimeField`/`SpinnerField` in misc-widgets batch.

**Settled:** `Label`/`Badge` keep `.text` as the canonical property. `.value` is for
data-bearing widgets only; a display-only label has no "value" in the semantic sense.

**PR #76** (`fix/public-api-drift` → `main`) — merged.

### Session 32 — Misc-widgets batch (2026-05-28)

Added `ScrollView`, `SpinnerField`, `TimeField`, and `MenuBar` to the public layer
on `feat/public-misc-widgets` (PR #77).

**Files created under `src/bootstack/widgets/public/primitives/`:**
- `scrollview.py` — `ScrollView` (`PublicContainer`; children → `_internal.add()` content
  frame; exposes `scroll_to_top/bottom/left/right`, `yview/xview_moveto`,
  `enable/disable_scrolling`, `refresh_bindings`)
- `spinnerfield.py` — `SpinnerField` (two modes: fixed `options=` list or numeric range
  via `min_value=`/`max_value=`/`step=`; `wrap=`; maps to internal `SpinnerEntry`)
- `timefield.py` — `TimeField` (time-input with searchable interval dropdown;
  `value_format=`, `interval=`, `min_time=`/`max_time=`; maps to internal `TimeEntry`)
- `menubar.py` — `MenuBar` (three-region bar: `before`/`center`/`after`;
  `add_button`, `add_label`, `add_menu`)

Both `SpinnerField` and `TimeField` override `on()` to route `<<Change>>`/`<Return>`
events to `self._internal._entry` (same pattern as `TextField`, `Select`, `NumberField`).

**Visual test:** `tests/features/misc_widgets.py`

**Next steps:** Merge PR #77, then determine remaining widgets to migrate.
Notable gaps: `DateField` needs review against v2 proposal; open bugs from the known-issues list.

### Session 35 — Namespace migration + Card layout + widget structure plan (2026-05-29)

**PR #81** (`feat/namespace-migration` → `main`) — 2 commits, pending merge:

**Namespace migration:**
- `bootstack/__init__.py` replaced lazy-import system with direct imports from
  the public layer. All widgets now exported under public names (`TextField`,
  `Checkbox`, `Select`, `NumberField`, `Tree`, `Table`, `Gauge`, etc.).
  `Form`, `SideNav`, `Calendar` kept from internals (no public equivalent yet).
  Non-widget utilities unchanged (style, data, i18n, signals, AppSettings, etc.).
- `pyproject.toml`: added `testpaths` — pytest now scopes to `tests/cli` and
  `tests/widgets/public` only; old `tests/widgets/` scripts are manual visual
  demos.
- `ContextMenuItem` added to public namespace.
- CLI templates rewritten to use context-manager layout (Grid, VStack) and
  public API naming. Views are plain classes, not subclasses of internal widgets.
- CLI test assertions updated to match new template output.

**Card layout:**
- `Card` now accepts `layout=` kwarg: `'vstack'` (default), `'hstack'`, `'grid'`.
  Backed by an internal `PackFrame`/`GridFrame` inside the card surface.
- Child-guidance kwargs added: `gap`, `fill_items`, `expand_items`,
  `anchor_items`, `columns`, `rows`, `sticky_items`, `auto_flow`.
- `_child_master()` returns the layout frame; children are managed by the layout
  engine rather than placed directly on the card surface.

**`*_items` defaults fix (VStack, HStack, Card, Grid):**
- `_merge_layout_options` now applies `fill_items`/`expand_items`/`anchor_items`
  as defaults when not set per-child. Fixes canvas-based widgets (Slider,
  RangeSlider, Gauge) that bypass PackFrame's `_on_child_pack` hook.
- Grid/Card(grid): `sticky_items` applied as default in `_merge_layout_options`.

**form_demo.py** rewritten using the public API; 118 → 72 lines.

**Widget directory structure — settled, deferred to next PR:**

Final target structure:
```
widgets/
  _core/           # public framework internals (base, container, context,
                   # events, exceptions, subscription) — extend here, don't
                   # import directly from user code
  _impl/           # all internal widget implementation (never import directly)
    primitives/    # TTK widget subclasses (was widgets/primitives/)
    composites/    # complex internal widgets (was widgets/composites/)
    mixins/        # shared mixins (was widgets/mixins/)
    _internal/     # TTK wrapper base (unchanged)
    _parts/        # entry sub-components (unchanged)
  # Everything below is the public widget surface — flat
  types.py
  app.py
  appshell.py
  window.py
  stacks.py
  grid.py
  dialogs.py
  button.py
  label.py
  textfield.py
  card.py
  ... (~40 widget files, all flat)
```
Deferred because: ~540 import changes across ~150 files; purely internal
reorganization with no public API effect; cleaner as its own focused PR.
Branch: `refactor/widget-structure` off `main` after #81 merges.

**Remaining work (after Session 35):**
- ~~Merge PR #81~~ — done
- ~~`refactor/widget-structure`~~ — done (Session 36, PR #82)
- ~~Gallery/examples rebuild using public API~~ — CLI gallery done (Session 37); `examples/` legacy demos separate effort
- ToggleGroup solid variant contrast — user handling
  `src/bootstack/style/builders/toolbutton.py`

### Session 36 — Widget directory restructure (2026-05-29)

**PR:** `refactor/widget-structure` → `main` (branch, pending merge)

**What changed:** Migrated `widgets/` to the settled target layout from Session 35.
All 204 files changed (~540 import updates across ~150 source files + 25 test files).
No public API effect — `bs.*` names unchanged.

**New structure:**
- `widgets/_core/` — public framework internals (base, container, context, events,
  exceptions, subscription); re-exported via `widgets/_core/__init__.py`
- `widgets/_impl/` — all internal implementation (composites, mixins, primitives,
  _internal, _parts); never import directly
- `widgets/*.py` — flat public widget surface (~40 files, formerly `widgets/public/primitives/`)
- `widgets/__init__.py` — lean (TYPE_CHECKING + TTK_WIDGETS/TK_WIDGETS); public API
  lives in `bootstack/__init__.py` which imports from flat module paths directly

**Key design note — circular import:** `widgets/__init__` cannot eagerly import widgets
because `constants.py` → `widgets.types` triggers `widgets/__init__` before `style.style`
is initialized. `bootstack/__init__` now imports directly from flat module paths (e.g.
`from bootstack.widgets.button import Button`) instead of `from bootstack.widgets import (...)`.

**Tests:** 28 non-GUI tests pass. Pre-existing CLI spec template failure unchanged
(`test_spec_template_bundles_icon_package_assets` — `ttkbootstrap_icons` not in
rewritten spec template from Session 35, unrelated to this PR).

**Remaining work:**
- ~~Merge `refactor/widget-structure` PR~~ — done (PR #82)
- ~~Gallery/examples rebuild using public API~~ — CLI gallery done (Session 37); `examples/` legacy demos are a separate effort
- ToggleGroup solid variant contrast — user handling
  `src/bootstack/style/builders/toolbutton.py`

### Session 37 — Gallery rewrite + API gap fixes (2026-05-29)

All work committed directly to `main`.

**CLI gallery (`cli/demo.py`) fully rewritten for public API:**
- `fill="horizontal"/"vertical"` throughout
- Lazy page builds via `on_page_changed` hook; home page built eagerly
- `Calendar`/`Form` use `current_container()._child_master()` for explicit parent
- `Toast` uses `message=`; `FormDialog` uses `data=` with inferred editors
- Theme selector uses `sel.on_change` + `after(0)` to defer outside the event

**Bug fixes:**
- `SelectBox` popup: set `takefocus=False` on items so `<FocusOut>` no longer
  fires on the popup `Toplevel` before `<ButtonRelease-1>`, which was closing
  the dropdown before `on_change` could fire — broke all `Select` widgets
  after the enhanced-events migration
- `SelectBox` value setter: lifts readonly state before updating so
  `textsignal` propagates visually to the readonly entry, then restores it
- `GroupBox`: mirrors `Card`'s `layout=` kwarg (`'vstack'` default, `'hstack'`,
  `'grid'`); `fill_items=None` default; `padding=8`
- `PackFrame._build_options`: normalizes `fill` aliases (`horizontal→x`,
  `vertical→y`) via `normalize_fill` so internal and public callers both work
- `AppShell`: `add_nav_separator` → `add_separator`
- `ButtonGroup.add()`: fixed auto-key counter never advancing
- `Toast`, `dialog.py`, `icons.py`: replaced `bs.X` widget calls with `_impl`
  imports (prevents circular import during init)
- `tests/features`: fixed 23 demo files to import from `bootstack` not
  `bootstack.widgets`; removed stale `ttkbootstrap_icons` CLI test

**Tests:** 28 non-GUI tests pass. Gallery starts immediately; all pages build on
first navigation; `Select` dropdown, dialogs, and toasts all work correctly.

### Session 38 — Remove Card + GroupBox composite + card surface elevation (2026-05-29)

**PR #84** (`refactor/remove-card` → `main`) — merged:
- `Card` removed — no unique value over `VStack/HStack/Grid(variant='card')`
- Migration: `Card(layout='vstack')` → `VStack(variant='card')`,
  `Card(layout='hstack')` → `HStack(variant='card')`,
  `Card(layout='grid')` → `Grid(variant='card')`,
  `Card()` → `VStack(variant='card')` (default was `vstack`)
- `card.py` deleted; `Card` removed from `bootstack.__init__` and `widgets/__init__`
- `cli/demo.py` and `tests/features/form_demo.py` updated

**GroupBox composite + card surface elevation** (follow-on commit to `main`):

*GroupBox:*
- Replaced `ttk.LabelFrame` with a custom composite to eliminate background bleed:
  outer `PackFrame` (transparent) → muted title `Label` → card-variant `Frame`
  → layout engine (`PackFrame` or `GridFrame` per `layout=`)
- Content frame uses `variant='card'`, `surface='card'` so `_surface` token
  propagates to all descendants via `_refresh_descendant_surfaces`
- `padding=16` default; title uses `font='label'`, `accent='secondary'`

*Card variant frame builder (`style/builders/frame.py`):*
- `stroke` token for borders — semantic, theme-aware contrast
- `show_border=True` default for `variant='card'`
- `surface` defaults to `'card'` token; `accent=` overrides the surface token
- Removed hardcoded `padding=8` (padding is a widget-level concern, not style)

*VStack/HStack surface stepping (`widgets/stacks.py`):*
- `variant='card'` detects parent surface via `_child_master()._surface`
- Steps up one level: `background`/`content` → `card`, `card` → `overlay`
- Ensures nested cards render visually distinct from their parent surface

*Label (`widgets/label.py`):*
- `icon_position=` kwarg added (maps to `compound=`)
- Auto-detects `icon_only` when `text` is empty and `icon` is provided
- Default `compound='left'` when both text and icon are present

**Tests:** 28 non-GUI tests pass.

**Remaining work:**
- ToggleGroup solid variant contrast — user handling
  `src/bootstack/style/builders/toolbutton.py`
- `TextField` `placeholder=` not supported (only `TextArea` has it)
- `TabView` pill variant crash — builder not registered
- `Meter`/`Gauge` deprecated param names still in source
- `ListView` hover blends with striped rows
- `examples/` legacy demos — separate effort

### Session 34 — Bug fixes, public API gaps, secondary token (2026-05-29)

**PRs #79 and #80 opened** (pending merge at session end).

**PR #79** (`fix/public-api-gaps` → `main`) — 6 commits:
- Public API gaps filled: `DateField.picker_button`, `Spinbox.value_format`,
  `SplitView.sash_positions`/`min_size`, `MenuButton.add_radio_item`/`item`/`items`/`menu_options`,
  `ButtonGroup.item`/`items`
- `TextArea`/`CodeEditor` border: replaced raw `highlightthickness` with `Frame(ttk_class="TField",
  padding=5)`; both now have consistent focus ring; `show_border=True` default; label gets
  `padx=(4,0)` matching Field
- Validation callback shape: `on_valid`/`on_invalid`/`on_validated` now pass Tkinter Event
  (not unwrapped dict), matching `on_input`/`on_changed`
- `secondary` color token restored across all 12 theme JSONs, `COLOR_TOKENS`, `AccentToken`;
  field addon style builder now uses accent color for button background when `accent is not None`
- `PathField` browse button: replaced text button with `folder2-open` icon-only (position=after),
  matching DateField calendar picker pattern; removed `button_label`/`button_accent` params
- `Field`/`TextArea` message label: `accent="secondary"` replaces `"muted"`/`"default"` —
  fixes gray background on `required=True` fields
- `ListView` hover: `active = b.elevate(b.color(base_token), 2)` gives consistent hover
  across striped and unstriped rows; base extracted by stripping modifier from surface token
- TabView pill variant bug removed (never existed)

**PR #80** (`fix/issue-40-window-controls` → `main`) — fixes GitHub issue #40:
- `Toolbar._sync_maximize_state`: hides maximize button when `resizable=(False, False)`
- `Toolbar._on_minimize`: temporarily lifts `overrideredirect`, iconifies, restores on `<Map>`
- Repro script: `tests/features/issue_40_repro.py`

**`secondary` token decisions:**
- Buttons: keep `accent="default"` everywhere it was changed in the removal commit
- PathField browse button: now icon-only, no accent needed
- Field/TextArea message labels: restored to `accent="secondary"` (this was the root fix)

**Remaining work (next session):**
- **Migrate `bs.*` namespace** — wire public widgets as canonical exports in
  `bootstack/__init__.py`, replacing old internal widgets (`Entry`→`TextField`,
  `DateEntry`→`DateField`, `CheckButton`→`Checkbox`, etc.)
- ToggleGroup solid variant contrast — user handling `src/bootstack/style/builders/toolbutton.py`

### Session 33 — Style asset recoloring + branch cleanup (2026-05-29)

**PRs #77 and #78 merged** at session start. All misc widgets and style fixes landed.

**Asset color channel convention settled** (saved to memory `feedback_asset_color_channels.md`):
- White → fill, Black → border, Magenta → focus ring, Transparent → surface behind widget
- Ghost/no-border style: pass fill color for both `white_color` and `black_color`
- Always pass `transparent_color` for button-family assets — never leave as `None`

**Style fixes shipped in PR #78** (`fix/style-asset-recoloring`):
- `style/builders/menubar.py` — added `transparent_color=surface` to all three
  `recolor_element_image` calls; was `None`, leaving raw transparent corners
- `style/builders/field.py` — `build_field_addon_style`: magenta channel changed from
  `None` → `input_background` for all non-focused states (was leaking raw pink)
- `style/builders/scrollbar.py` — removed ALL arrow infrastructure from all four builder
  functions; scrollbars are now fully arrow-free (`arrowsize=0`); removed unused imports
- `widgets/composites/selectbox.py` — `on_canvas_configure` subtracts 2px from canvas
  width so list content doesn't touch the scrollbar
- Scrollbar assets (user): updated to 8px rendered thickness (16px at 2× source)

**ToggleGroup solid variant contrast** — investigated Bootstrap toggle pattern (normal =
full accent, selected = clearly darker). Attempted fixes reverted; user will handle
`src/bootstack/style/builders/toolbutton.py` directly.

**Stale branches deleted:** `fix/style-asset-recoloring` and `feat/public-radio` (both
fully superseded by merged PRs; style-asset branch had pre-Session-31 CLAUDE.md content).

**Remaining work (next session):**
- `DateField` — review against `development/v2_api_proposal.md`
- `TextArea` border — adopt Field-style focus-ring/border instead of raw Tk Text border
- Spinbox, GroupBox, PathField, MenuButton, ButtonGroup, SplitView, PageStack —
  confirm public wrappers exist and are correct

### Session 26 — Performance fixes (2026-05-28)

- **PR #53** (`perf/theme-change-accumulation` → `main`).
- **Root cause found and fixed:** `Slider`, `RangeSlider`, and `FloodGauge` used
  `root.bind("<<ThemeChanged>>", handler, add="+")` in their constructors.
  `<<ThemeChanged>>` is fired by Tcl/Tk (not bootstack) on every `theme_use()`.
  With `add="+"` and pages never destroyed, one new root callback accumulated per
  widget per page visit — O(total-widgets-ever-created) work on every theme change.
- **Fix:** track bind ID → unbind on `<Destroy>`; `winfo_viewable()` guard in
  handler (skip hidden, set `_theme_update_pending`); `<Map>` binding to apply
  deferred update when page is shown again.
- **`create_style()` fast path:** Python-side `_style_registry` set check before
  the Tcl `self.configure(style)` round-trip on every widget creation.
- **`BootstyleBuilderBuilderTk` cached** as singleton on `Style` (`_get_tk_builder()`);
  was being instantiated fresh per widget creation.
- **`_rebuild_all_tk_widgets`** now skips `winfo_viewable() == 0` widgets; defers
  to `<Map>` handler via `_theme_version` integer counter.
- **`register_tk_widget`** uses `tkinter.BaseWidget.bind` to bypass subclass
  `bind()` overrides (e.g. `_MultilineCore` delegates `bind()` to `self.text`
  which doesn't exist yet during `__init__`).
- Note: `<<ThemeChanged>>` is Tcl-native — it fires from `super().theme_use()`
  BEFORE `_rebuild_all_styles()` runs. Canvas/tk widgets (Slider, FloodGauge)
  must use `root.bind` since `tk.Frame`/`Canvas` don't receive `<<ThemeChanged>>`
  directly. TTK widgets can use `self.bind`.

### Session 25 — Slider PR + strategic direction (2026-05-28)

- Opened PR #52 (`feat/slider` → `main`) for Slider/RangeSlider work.
- Added `autostyle=False` to Slider/RangeSlider `tk.Frame` and `tk.Canvas`
  constructors to opt out of autostyle registration (manages own theming).
- Identified performance root cause: `Style._tk_widgets` accumulates forever;
  `_rebuild_all_tk_widgets` iterates the full set on every theme change.
- Strategic direction agreed: standalone framework identity, context-manager
  layout API, modern naming, performance investigation. Docs to be redone from
  scratch in a future session.

### Session 24 — Slider/RangeSlider redesign + Scale removal (2026-05-28)

- **`bs.Slider`** — full custom canvas widget. Horizontal/vertical, `show_value`
  badge, tick marks (major/minor), `show_minmax` end labels, disabled state,
  Signal-first binding, `<<Change>>` + `<<Commit>>` events.
- **`bs.RangeSlider`** — two-handle variant. Lo/hi signals. Vertical fill:
  `fill_start = end - lo_pos`, `fill_end = end - hi_pos` (PIL CCW rotation).
- **`bs.Scale` removed** — `primitives/scale.py` deleted. `form.py` keeps
  `'scale'` as deprecated alias → `'slider'` is canonical.
- **`bs.LabeledScale` removed** — use `bs.Slider(show_value=True)`.
- TypedDicts: `SliderEventData`, `SliderCommitEventData`, `RangeSliderEventData`,
  `RangeSliderCommitEventData` exported from `bs.*`.
- Visual test: `tests/features/slider_v2.py`
- Key architecture: PIL `rotate(90)` is CCW. Vertical badge_zone uses
  `tkfont.Font.measure()`. `style/builders/scale.py` retained for `ttk.Scale`.

### Session 23 — TextArea + CodeEditor complete (2026-05-18)

- **`bs.TextArea`** — multiline text widget replacing ScrolledText. `FilterChain`
  via `idlelib.redirector.WidgetRedirector`. `UndoManager` with word-level grouping.
- **`bs.CodeEditor`** — full editor with `LineNumbers`, `BracketMatcher`,
  `SmartIndent`, `PygmentsHighlighter` (150ms debounce, 49 styles), `IndentGuides`,
  `SearchOverlay` (Ctrl+F, z-order show/hide via `lift()`).
- Branch: `feat/textarea-codeeditor` — PRed.

### Session 21 — Toplevel polish + TabView parity (2026-05-17)

- **Toplevel** (PR #45): multi-handler close chain, `modal=`, `center_on_parent=`,
  `block_until_closed()`, `result` property.
- **TabView** (PR #46): `tv["key"]` access, locale-aware labels, typed events
  (`TabChangeEventData` etc.), `hide_tab`/`show_tab`/`forget_tab`.

### Sessions 16–20 — Source foundations (2026-05-14 to 2026-05-16)

- Package reorganized: `_runtime/`, `_core/`, `data/`, `signals/`, `i18n/`, `validation/` (PR #44).
- Type system in `widgets/types.py`: Literal aliases, `BaseWidgetKwargs`, `StyledKwargs`.
- Docstring sweep complete across all 44+ widget files.
- `on_*/off_*` standard applied to full widget tree.
- `bootstyle=` legacy support removed.
