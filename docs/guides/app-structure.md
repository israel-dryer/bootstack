---
title: App Structure
---

# App Structure

This guide explains how a bootstack application is organizedâ€”the `App` class, windows, layout, state, and lifecycle.

Use `bootstack start MyApp` to scaffold a new project with the recommended structure.

---

## The App Class

Every bootstack application starts with either `App` or `AppShell`:

- **`App`** â€” a blank window. You build the layout from scratch.
- **`AppShell`** â€” an `App` with a toolbar, sidebar navigation, and page stack already wired together.

```python
import bootstack as bs

# Option A: blank window
app = bs.App(title="My Application")

# Option B: window with built-in navigation
app = bs.AppShell(title="My Application", minsize=(1000, 650))
```

Both create the main window, initialize theming, set up the application context, and manage the event loop. You typically create one per process. Additional windows use `Toplevel`.

---

## Minimal Application

A complete, runnable application:

```python
import bootstack as bs

app = bs.App(title="Hello", minsize=(400, 300))

bs.Label(app, text="Hello, bootstack!").pack(padx=20, pady=20)
bs.Button(app, text="Close", command=app.destroy).pack(pady=10)

app.mainloop()
```

This demonstrates the core pattern:

1. Create the App
2. Add widgets to it
3. Run the event loop

<div class="app-window">
    <img src="../assets/guides-app-structure-min-app.png" alt="Minimal App"/>
</div>

---

## AppShell: Navigation Built In

Most desktop applications follow the same layout: toolbar at the top, sidebar on the left, page content on the right. `AppShell` gives you that in one call:

```python
import bootstack as bs

shell = bs.AppShell(title="My App", minsize=(1000, 650))

# Each add_page() creates a nav item and returns a Frame for content
home = shell.add_page("home", text="Home", icon="house")
bs.Label(home, text="Welcome!").pack(padx=20, pady=20)

# Add as many pages as you need
docs = shell.add_page("docs", text="Documents", icon="file-earmark-text")
bs.Label(docs, text="Your documents.").pack(padx=20, pady=20)

# Add toolbar buttons (they appear on the right side)
shell.toolbar.add_button(icon="sun", command=bs.toggle_theme)

shell.mainloop()
```

<div class="app-window">
    <img src="../assets/guides-app-structure-app-shell.png" alt="App Shell"/>
</div>

`AppShell` extends `App`, so everything that works on `App` works on `AppShell` too.

### Frameless window

Set `frameless=True` to remove OS window chrome and get a fully custom window. The toolbar automatically gains minimize/maximize/close buttons and becomes draggable:

```python
shell = bs.AppShell(
    title="Custom Window",
    minsize=(1000, 650),
    frameless=True,
)
```

![frameless](../assets/guides-app-structure-frameless.png)

### When to use App vs AppShell

| | `App` | `AppShell` |
|---|---|---|
| Layout | You build everything | Toolbar + sidebar + pages included |
| Best for | Custom layouts, simple tools, dialogs | Navigation-based apps |
| Navigation | Manual (wire your own) | Automatic (add_page wires nav to pages) |

---

## Application Options

Common `App` parameters:

```python
app = bs.App(
    title="My App",           # Window title
    theme="amber-light",      # Theme name
    minsize=(800, 600),          # Initial size (width, height)
    resizable=(True, True),   # Allow resize (width, height)
    alpha=1.0,                # Window transparency
)
```

!!! link "Themes"
    See [Design System â†’ Custom Themes](../design-system/custom-themes.md) for available themes and customization.

---

## Project Structure

`bootstack start` generates one of two layouts depending on the template you
choose. The **basic** template (default) produces a single-view `App`:

```
myapp/                       # bootstack start MyApp
â”œâ”€â”€ src/myapp/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ main.py              # App entry point
â”‚   â””â”€â”€ views/
â”‚       â”œâ”€â”€ __init__.py
â”‚       â””â”€â”€ main_view.py
â”œâ”€â”€ assets/                  # Images, icons
â”œâ”€â”€ bootstack.toml                # Project configuration
â””â”€â”€ README.md
```

The **appshell** template produces an `AppShell` with sidebar navigation
and one file per page:

```
myapp/                       # bootstack start MyApp --template appshell
â”œâ”€â”€ src/myapp/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ main.py
â”‚   â””â”€â”€ pages/
â”‚       â”œâ”€â”€ __init__.py
â”‚       â”œâ”€â”€ home_page.py
â”‚       â””â”€â”€ settings_page.py
â”œâ”€â”€ assets/
â”œâ”€â”€ bootstack.toml
â””â”€â”€ README.md
```

The chosen template is recorded in `bootstack.toml` as `[app].template`, so
`bootstack add view` and `bootstack add page` know which scaffold is appropriate for
the project.

As your project grows:

```
myapp/
â”œâ”€â”€ src/myapp/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ main.py
â”‚   â”œâ”€â”€ settings.py      # AppSettings / defaults
â”‚   â”œâ”€â”€ state.py         # Signals and shared state
â”‚   â”œâ”€â”€ views/
â”‚   â”‚   â”œâ”€â”€ main_view.py
â”‚   â”‚   â””â”€â”€ settings_view.py
â”‚   â””â”€â”€ services/        # IO, data, persistence
â”œâ”€â”€ assets/
â”œâ”€â”€ locales/             # Translation files
â””â”€â”€ bootstack.toml
```

Use `bootstack start MyApp` to scaffold a new project with this structure.

!!! link "Project Structure"
    See [Tooling â†’ Project Structure](../tooling/project-structure.md) for detailed guidance on file organization, packaging, and PyInstaller.

---

## Layout Hierarchy

bootstack applications follow a **container hierarchy**:

```
App (blank window)
â””â”€â”€ PackFrame (main layout)
    â”œâ”€â”€ Frame (toolbar area)
    â”‚   â””â”€â”€ Button, Button, ...
    â”œâ”€â”€ PackFrame (content area)
    â”‚   â””â”€â”€ widgets...
    â””â”€â”€ Frame (status bar)
        â””â”€â”€ Label
```

With `AppShell`, the top-level structure is built for you:

```
AppShell (window)
â”œâ”€â”€ Toolbar
â”‚   â””â”€â”€ hamburger, title, spacer, [your buttons]
â””â”€â”€ Frame (body)
    â”œâ”€â”€ SideNav
    â”‚   â””â”€â”€ SideNavItem, SideNavGroup, ...
    â””â”€â”€ PageStack
        â”œâ”€â”€ Frame (page "home")
        â”œâ”€â”€ Frame (page "docs")
        â””â”€â”€ ...
```

Key principles:

- **Containers own layout** â€” each container manages its children
- **Widgets don't position themselves** â€” their parent decides placement
- **Nesting creates structure** â€” compose complex layouts from simple containers

!!! link "Layout Guide"
    See [Layout](layout.md) for details on Frame, PackFrame, and GridFrame.

---

## Application Settings

App-wide configuration â€” theme, locale, default behaviors â€” lives in a single
`AppSettings` object passed to `App` (or `AppShell`) at construction. Settings
are applied at startup and remain readable throughout the app lifecycle.

!!! link "See [App Settings](app-settings.md) for declaring and applying settings."

---

## State Management

Use **signals** for state shared between widgets â€” `bs.Signal(value)`, passed
to widgets via `signal=` (or read/written via `.get()` / `.set()`). For larger
apps, group related signals in a dedicated `state.py` module so views can
import them without circular dependencies.

!!! link "See [Reactivity](reactivity.md) for signals, subscriptions, callbacks, and events."

---

## Window Lifecycle

The `App` lifecycle:

1. **Creation** â€” `App()` creates the window and initializes theming
2. **Building** â€” you add widgets and configure layout
3. **Running** â€” `mainloop()` processes events until the window closes
4. **Cleanup** â€” the window is destroyed

For additional windows:

```python
def open_settings():
    settings = bs.Toplevel(app, title="Settings")

    bs.Label(settings, text="Settings go here").pack(padx=20, pady=20)
    bs.Button(settings, text="Close", command=settings.destroy).pack(pady=10)

bs.Button(app, text="Settings", command=open_settings).pack(pady=10)
```

`Toplevel` creates a secondary window that:

- shares the event loop with `App`
- can be modal or non-modal
- is destroyed independently

---

## Theme Switching

bootstack supports light/dark variants and runtime switching via
`bs.toggle_theme()` and `bs.set_theme(name)`. All widgets update automatically.

!!! link "See [Color & Theming](color-and-theming.md) for accent tokens, surfaces, custom themes, and `light_theme` / `dark_theme` configuration."

---

## Localization Setup

Set `locale=` in app settings to switch the active locale; widgets that opt in
to message keys resolve them through the active message catalog. Number, date,
and currency formatting follow the same locale.

!!! link "See [Localization](localization.md) for message catalogs and runtime language switching."

---

## Putting It Together

A structured application example:

```python
import bootstack as bs

# State
counter = bs.Signal(0)

def increment():
    counter.set(counter.get() + 1)

# App
app = bs.App(title="Counter", minsize=(300, 200))

# Layout
main = bs.PackFrame(app, direction="vertical", gap=10, padding=20)
main.pack(fill="both", expand=True)

# Display
display = bs.Label(main, font="display-xl[48]")
counter.subscribe(lambda v: display.configure(text=str(v)))
display.pack()

# Controls
controls = bs.PackFrame(main, direction="horizontal", gap=10)
controls.pack()

bs.Button(controls, text="+1", command=increment).pack()
bs.Button(controls, text="Reset", command=lambda: counter.set(0)).pack()

app.mainloop()
```

This demonstrates:

- Signal-based state
- PackFrame for layout
- Reactive label updates
- Clean separation of concerns

For navigation-based applications, `AppShell` replaces the manual layout wiring:

```python
import bootstack as bs

shell = bs.AppShell(title="My App", minsize=(900, 600))

# State
counter = bs.Signal(0)

# Pages
home = shell.add_page("home", text="Home", icon="house")
display = bs.Label(home, font="display-xl[48]")
counter.subscribe(lambda v: display.configure(text=str(v)))
display.pack(padx=20, pady=20)

controls = bs.PackFrame(home, direction="horizontal", gap=10)
controls.pack()
bs.Button(controls, text="+1", command=lambda: counter.set(counter.get() + 1)).pack()
bs.Button(controls, text="Reset", command=lambda: counter.set(0)).pack()

about = shell.add_page("about", text="About", icon="info-circle")
bs.Label(about, text="Counter App v1.0").pack(padx=20, pady=20)

shell.mainloop()
```

---

## Next Steps

- [Layout](layout.md) â€” building layouts with containers
- [Navigation](navigation.md) â€” tabs, stacks, and sidebar patterns
- [Reactivity](reactivity.md) â€” signals, callbacks, and events
- [Project Structure](../tooling/project-structure.md) â€” file organization and packaging
- [CLI](../tooling/cli.md) â€” scaffolding and build tools
