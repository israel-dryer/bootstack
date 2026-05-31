![bootstack](https://raw.githubusercontent.com/israel-dryer/bootstack/main/assets/banner-readme.png)

![](https://img.shields.io/github/release/israel-dryer/bootstack.svg)
[![Downloads](https://pepy.tech/badge/bootstack)](https://pepy.tech/project/bootstack)
[![Downloads](https://pepy.tech/badge/bootstack/month)](https://pepy.tech/project/bootstack)
![](https://img.shields.io/github/issues/israel-dryer/bootstack.svg)
![](https://img.shields.io/github/issues-closed/israel-dryer/bootstack.svg)
![](https://img.shields.io/github/license/israel-dryer/bootstack.svg)
![](https://img.shields.io/github/stars/israel-dryer/bootstack.svg)
![](https://img.shields.io/github/forks/israel-dryer/bootstack.svg)

> **Active alpha.** APIs may change before the first stable release.
> Documentation is coming soon.

<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://raw.githubusercontent.com/israel-dryer/bootstack/main/assets/readme/hero-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/israel-dryer/bootstack/main/assets/readme/hero-light.png">
  <img alt="bootstack hero demo" src="https://raw.githubusercontent.com/israel-dryer/bootstack/main/assets/readme/hero-light.png">
</picture>

## Why bootstack?

Most Python desktop frameworks make you fight the framework. bootstack gets out of the way.

- **30% less code** — the declarative, context-manager layout eliminates geometry calls, explicit parenting, and most of the wiring boilerplate
- **Reads like Python** — nested `with` blocks mirror your UI structure; the code hierarchy *is* the layout
- **Modern layout system** — `HStack`, `VStack`, and `Grid` containers handle spacing, alignment, and fill automatically; CSS conventions (`gap`, `padding`, `margin`, `fill`, `anchor`) without writing CSS
- **60+ widgets out of the box** — primitives through full composites: tables, trees, calendars, date pickers, gauges, sliders, and more — including a full `CodeEditor` with syntax highlighting, line numbers, bracket matching, smart indent, and search; no external editor dependency required
- **Reactive signals** — observable state that flows between widgets; bind once, update everywhere
- **Event and stream pipelines** — compose, filter, debounce, and throttle UI events with a chainable stream API
- **Built-in icons** — the full Bootstrap Icons catalog, theme-aware and DPI-scaled, bundled with the framework
- **Built-in localization** — 23 language catalogs, locale-aware number/date/time formatting, runtime language switching
- **Semantic styling** — `accent="primary"`, `variant="outline"` — no hard-coded colors; looks right across every theme automatically
- **8 paired light/dark themes** — with a runtime switcher and a custom-theme API
- **Forms and validation** — field-level validators, inline error messages, and a `FormDialog` for quick modal forms
- **DataSource abstraction** — one interface over SQLite, in-memory, and file backends with filtering, sorting, pagination, and CRUD
- **A real CLI** — scaffold, run, add pages/views/dialogs/themes, and package for distribution
- **PyInstaller packaging built in** — `bootstack build` produces a standalone executable; no separate toolchain required

## Installation

Requires Python 3.12+.

Install directly from the repository:

```bash
pip install git+https://github.com/israel-dryer/bootstack.git
```

## See it

The widget gallery is a single-window tour of everything bootstack ships — every widget, theme switcher, accent variants, and layout containers. Fastest way to see the framework in action without writing a line of code:

```bash
bootstack gallery
```

<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://raw.githubusercontent.com/israel-dryer/bootstack/main/assets/readme/gallery-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/israel-dryer/bootstack/main/assets/readme/gallery-light.png">
  <img alt="bootstack widget gallery" src="https://raw.githubusercontent.com/israel-dryer/bootstack/main/assets/readme/gallery-light.png">
</picture>

## Quick Start

```python
import bootstack as bs

with bs.App(title="Hello", padding=16, gap=16) as app:
    bs.Label("Hello from bootstack!")
    bs.Button("Primary", accent="primary")
    bs.Button("Success", accent="success")
    bs.Button("Danger Outline", accent="danger", variant="outline")

app.run()
```

<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://raw.githubusercontent.com/israel-dryer/bootstack/main/assets/readme/ex-quickstart-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/israel-dryer/bootstack/main/assets/readme/ex-quickstart-light.png">
  <img alt="bootstack quick start example" src="https://raw.githubusercontent.com/israel-dryer/bootstack/main/assets/readme/ex-quickstart-light.png">
</picture>

For navigation-based apps, use `AppShell` — it gives you a toolbar, sidebar, and page stack in one call:

```python
import bootstack as bs

shell = bs.AppShell(title="My App", size=(1000, 650))

with shell.add_page("home", text="Home", icon="house"):
    bs.Label("Welcome!")

with shell.add_page("docs", text="Documents", icon="file-earmark-text"):
    bs.Label("Your documents.")

shell.run()
```

## How it works

### Layout containers

`VStack`, `HStack`, and `Grid` let you describe a layout once instead of repeating geometry calls on each child:

```python
with bs.App(title="Sign In") as app:
    with bs.Grid(columns=["auto", 1], gap=(12, 6), sticky_items="ew", padding=16):
        bs.Label("Name:")
        bs.TextField(placeholder="Full name")
        bs.Label("Email:")
        bs.TextField(placeholder="email@example.com")
        bs.Label("Role:")
        bs.Select(options=["Admin", "User", "Viewer"], value="User")
        bs.Button("Submit", accent="primary", columnspan=2)

app.run()
```

<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://raw.githubusercontent.com/israel-dryer/bootstack/main/assets/readme/ex-layout-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/israel-dryer/bootstack/main/assets/readme/ex-layout-light.png">
  <img alt="bootstack layout containers example" src="https://raw.githubusercontent.com/israel-dryer/bootstack/main/assets/readme/ex-layout-light.png">
</picture>

### Semantic styling

Widgets take an `accent` (color intent) and `variant` (visual weight) instead of hard-coded colors, so the same code looks right across themes and light/dark modes:

```python
bs.Button("Save", accent="primary")
bs.Button("Cancel", accent="secondary", variant="outline")
bs.Label("Heading", font="heading-lg")
```

<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://raw.githubusercontent.com/israel-dryer/bootstack/main/assets/readme/ex-semantic-styling-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/israel-dryer/bootstack/main/assets/readme/ex-semantic-styling-light.png">
  <img alt="bootstack semantic styling example" src="https://raw.githubusercontent.com/israel-dryer/bootstack/main/assets/readme/ex-semantic-styling-light.png">
</picture>

### Signals (optional)

Plain callbacks work fine for most things. When state needs to flow between widgets, signals give you a small reactive primitive with two-way binding:

```python
with bs.App(title="Hello") as app:
    name = bs.Signal("World")
    bs.Label(textsignal=name)      # updates automatically when name changes
    bs.TextField(textsignal=name)  # two-way binding to the same state

app.run()
```

## Features

- **Application scaffolding** — `App` for blank windows, `AppShell` for toolbar + sidebar + page-stack apps, undecorated windows with custom chrome
- **60+ themed widgets** — ttk-derived primitives plus higher-level composites (Table, Tree, Calendar, DateField, Form, Gauge, ToggleGroup, PageStack, Toast, Tooltip, and more)
- **9 dialogs** — Message, Query, ColorChooser, ColorDropper, DateDialog, FontDialog, FilterDialog, FormDialog, plus a `Dialog` base
- **Layout containers** — `VStack`, `HStack`, and `Grid` for declarative layouts; `Card`, `GroupBox`, `ScrollView`, `SplitView`, `Accordion`, `Expander`
- **Design system** — semantic `accent` colors (primary, secondary, success, danger, warning, info) and `variant` tokens (solid, outline, ghost, link), consistent across widgets
- **Built-in themes** — paired light/dark variants (amber, aurora, bootstrap, classic, docs, forest, ocean, rose) with runtime theme switching and a custom-theme API
- **Reactive signals** — observable state with subscribe/get/set, integrates with widgets via `signal=` / `textsignal=`
- **Forms & validation** — `Form` and `Field` with built-in validators
- **DataSource** — common interface over in-memory, SQLite, and file backends, with pagination, filtering, sorting, CRUD, and CSV export
- **Localization (i18n)** — 23 bundled message catalogs, locale-aware number/date/time formatting via Babel, runtime language switching
- **Icons & images** — Bootstrap Icons catalog with theme-aware recoloring, DPI scaling, and caching
- **Platform support** — DPI awareness, multi-monitor centering, mica/acrylic effects on Windows
- **CLI (`bootstack`)** — project scaffolding, run, add components, theme/i18n setup, doctor, build/package

## Widget Categories

| Category | Widgets |
|----------|---------|
| **Actions** | Button, ButtonGroup, MenuButton, DropdownButton, ContextMenu |
| **Inputs** | TextField, PasswordField, PathField, NumberField, SpinnerField, Slider, RangeSlider, TextArea, CodeEditor, DateField, TimeField |
| **Selection** | Checkbox, Switch, ToggleButton, RadioGroup, ToggleGroup, Select, Calendar |
| **Data Display** | Label, Badge, ListView, Tree, Table, ProgressBar, Gauge |
| **Layout** | VStack, HStack, Grid, Card, GroupBox, SplitView, ScrollView, Accordion, Expander, Separator |
| **Navigation** | AppShell, Toolbar, SideNav, Tabs, PageStack |
| **Dialogs** | MessageDialog, QueryDialog, ColorChooser, ColorDropper, DateDialog, FontDialog, FilterDialog, FormDialog |
| **Overlays** | Toast, Tooltip |
| **Forms** | Form, Field (with validation) |

## CLI

bootstack ships with an optional CLI for scaffolding, running, and packaging applications:

```bash
bootstack gallery                           # Launch the interactive widget gallery
bootstack icons                             # Browse the built-in icon catalog
bootstack start MyApp                       # Create a new project (basic template)
bootstack start MyApp --template appshell   # ...or with sidebar navigation
bootstack run                               # Run the app defined in the project config
bootstack add page Dashboard                # Add a new page (appshell)
bootstack add view Settings                 # Add a new view (basic)
bootstack add dialog Preferences            # Add a new dialog
bootstack add theme my-brand                # Scaffold a custom theme
bootstack add i18n --languages en es fr     # Add i18n support
bootstack list themes                       # List available themes
bootstack doctor                            # Diagnose project & environment
bootstack build                             # Package for distribution
```

## Documentation

Documentation is coming soon.

## Links

- **GitHub**: https://github.com/israel-dryer/bootstack
