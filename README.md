![bootstack](https://raw.githubusercontent.com/israel-dryer/bootstack/main/assets/banner-readme.png)

![](https://img.shields.io/github/release/israel-dryer/bootstack.svg)
[![Downloads](https://pepy.tech/badge/bootstack)](https://pepy.tech/project/bootstack)
[![Downloads](https://pepy.tech/badge/bootstack/month)](https://pepy.tech/project/bootstack)
![](https://img.shields.io/github/issues/israel-dryer/bootstack.svg)
![](https://img.shields.io/github/issues-closed/israel-dryer/bootstack.svg)
![](https://img.shields.io/github/license/israel-dryer/bootstack.svg)
![](https://img.shields.io/github/stars/israel-dryer/bootstack.svg)
![](https://img.shields.io/github/forks/israel-dryer/bootstack.svg)


> **From the maker of [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap).**

**bootstack** is a batteries-included desktop framework for Python, built on Tk.

60+ themed widgets. Reactive state. Declarative layout. Built-in icons and localization. A CLI that scaffolds, builds, and ships. Everything ttkbootstrap was missing.

<p align="center">
  <img src="docs/assets/hero-demo-app-light.png" width="49%" alt="bootstack Data Analysis Workbench — light theme">
  <img src="docs/assets/hero-demo-app-dark.png" width="49%" alt="bootstack Data Analysis Workbench — dark theme">
</p>

> **Active alpha.** APIs may change before the first stable release.
> See the [documentation](https://bootstack.org) for guides and the API reference.

## Installation

Requires Python 3.12+.

bootstack is currently in **active alpha**, so the `--pre` flag is required to opt in to pre-release versions:

```bash
pip install --pre bootstack
```

## See it

The widget gallery is a single-window tour of everything bootstack ships — every widget, theme switcher, accent variants, and layout containers. Fastest way to see the framework in action without writing a line of code:

```bash
bootstack gallery
```

## Quick Start

```python
import bootstack as bs

app = bs.App(title="Hello bootstack", theme="bootstrap-light")

bs.Label(app, text="Hello from bootstack!").pack(pady=10)
bs.Button(app, text="Primary", accent="primary").pack(pady=5)
bs.Button(app, text="Success", accent="success").pack(pady=5)
bs.Button(app, text="Danger Outline", accent="danger", variant="outline").pack(pady=5)

app.mainloop()
```

For navigation-based apps, use `AppShell` — it gives you a toolbar, sidebar, and page stack in one call:

```python
import bootstack as bs

shell = bs.AppShell(title="My App", size=(1000, 650))

home = shell.add_page("home", text="Home", icon="house")
bs.Label(home, text="Welcome!").pack(padx=20, pady=20)

docs = shell.add_page("docs", text="Documents", icon="file-earmark-text")
bs.Label(docs, text="Your documents.").pack(padx=20, pady=20)

shell.mainloop()
```

## How it works

### Layout containers

`PackFrame` and `GridFrame` let you describe a layout once instead of repeating geometry calls on each child:

```python
form = bs.GridFrame(app, columns=["auto", 1], gap=(12, 6), sticky_items="ew", padding=12)
form.pack(fill="both", expand=True)

bs.Label(form, text="Name").grid()
bs.TextEntry(form).grid()
bs.Label(form, text="Email").grid()
bs.TextEntry(form).grid()
bs.Button(form, text="Submit", accent="primary").grid(columnspan=2)
```

### Semantic styling

Widgets take an `accent` (color intent) and `variant` (visual weight) instead of hard-coded colors, so the same code looks right across themes and light/dark modes:

```python
bs.Button(app, text="Save", accent="primary")                       # solid (default)
bs.Button(app, text="Cancel", accent="secondary", variant="outline")
bs.Label(app, text="Heading", font="heading-lg")
```

### Signals (optional)

Plain callbacks work fine for most things. When state needs to flow between widgets, signals give you a small subscribe/get/set primitive:

```python
counter = bs.Signal(0)

label = bs.Label(app)
counter.subscribe(lambda v: label.configure(text=f"Count: {v}"))

bs.Button(app, text="+1", command=lambda: counter.set(counter.get() + 1))
```

## Features

- **Application scaffolding** — `App` for blank windows, `AppShell` for toolbar + sidebar + page-stack apps, undecorated windows with custom chrome
- **60+ themed widgets** — ttk-derived primitives plus higher-level composites (TableView, Calendar, DateEntry, Form, FloodGauge, Meter, ToggleGroup, PageStack, Toast, Tooltip, and more)
- **9 dialogs** — Message, Query, ColorChooser, ColorDropper, DateDialog, FontDialog, FilterDialog, FormDialog, plus a `Dialog` base
- **Layout containers** — `PackFrame` and `GridFrame` for declarative layouts; `ScrollView`, `PanedWindow`, `Accordion`, `Card`, `Expander`
- **Design system** — semantic `accent` colors (primary, secondary, success, danger, warning, info) and `variant` tokens (solid, outline, ghost, link, text), consistent across widgets
- **Built-in themes** — paired light/dark variants (amber, aurora, bootstrap, classic, docs, forest, ocean, rose) with runtime theme switching and a custom-theme API
- **Reactive signals** — observable state with subscribe/get/set, integrates with widgets via `signal=` / `textvariable=`
- **Forms & validation** — `Form` and `Field` with built-in validators
- **DataSource** — common interface over in-memory, SQLite, and file backends, with pagination, filtering, sorting, CRUD, and CSV export
- **Localization (i18n)** — 23 bundled message catalogs, locale-aware number/date/time formatting via Babel, runtime language switching
- **Icons & images** — icon handling with theme-aware recoloring, DPI scaling, and caching
- **Platform support** — DPI awareness, multi-monitor centering, mica/acrylic effects on Windows
- **CLI (`bootstack`)** — project scaffolding, run, add components, theme/i18n setup, doctor, build/package

## Widget Categories

| Category | Widgets |
|----------|---------|
| **Actions** | Button, ButtonGroup, MenuButton, DropdownButton, ContextMenu |
| **Inputs** | TextEntry, PasswordEntry, PathEntry, NumericEntry, SpinnerEntry, Scale, ScrolledText, DateEntry, TimeEntry |
| **Selection** | CheckButton, CheckToggle, RadioButton, RadioToggle, RadioGroup, ToggleGroup, OptionMenu, SelectBox, Calendar, Switch |
| **Data Display** | Label, Badge, ListView, TreeView, TableView, Progressbar, Meter, FloodGauge |
| **Layout** | Frame, PackFrame, GridFrame, LabelFrame, PanedWindow, ScrollView, Accordion, Card, Expander, Separator, SizeGrip |
| **Navigation** | AppShell, Toolbar, SideNav, Tabs, PageStack |
| **Dialogs** | MessageDialog, QueryDialog, ColorChooser, ColorDropper, DateDialog, FontDialog, FilterDialog, FormDialog |
| **Overlays** | Toast, Tooltip |
| **Forms** | Form, Field (with validation) |

## CLI

bootstack ships with an optional CLI for scaffolding, running, and packaging applications:

```bash
bootstack gallery                           # Launch the interactive widget gallery
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

- **Documentation**: https://bootstack.org
- **Getting Started**: https://bootstack.org/getting-started/
- **Guides**: https://bootstack.org/guides/
- **Widgets**: https://bootstack.org/widgets/

## Links

- **GitHub**: https://github.com/israel-dryer/bootstack
- **Icons**: https://github.com/israel-dryer/ttkbootstrap-icons

## Acknowledgements

bootstack is derived from [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap) and continues that project's mission. See [`NOTICE`](NOTICE) for license attribution.