---
title: AppShell
---

# AppShell

`AppShell` is an **application window with built-in navigation** — it wires a `Toolbar`, `SideNav`, and `PageStack` into the standard desktop app layout so you don't have to build it manually.

For window management (sizing, positioning, close handling, Toplevel) see the [Windowing guide](../../guides/windowing.md).

---

## Quick start

```python
import bootstack as bs

shell = bs.AppShell(title="My App", minsize=(1000, 650))

home = shell.add_page("home", text="Home", icon="house")
bs.Label(home, text="Welcome!").pack(padx=20, pady=20)

docs = shell.add_page("docs", text="Documents", icon="file-earmark-text")
bs.Label(docs, text="Your documents.").pack(padx=20, pady=20)

shell.mainloop()
```

Each `add_page()` call creates both a nav item in the sidebar and a `Frame` in the page stack. Populate the returned frame with any widgets.

---

## When to use

Use `AppShell` when your application has multiple distinct pages and you want the standard toolbar + sidebar + content layout wired automatically.

Use plain `App` when you need full control over the layout, or when your application is a single-page utility without navigation.

---

## Navigation display modes

The sidebar can be shown in three modes:

| Mode | Description |
|------|-------------|
| `expanded` | Full width with icon and text (default) |
| `compact` | Narrow, icon-only |
| `minimal` | Hidden until the hamburger button is pressed |

```python
shell = bs.AppShell(title="My App", nav_display_mode="compact")
```

---

## Pages and groups

### Adding pages

```python
page = shell.add_page("settings", text="Settings", icon="gear")
bs.Label(page, text="Settings content").pack()
```

### Groups

Group related pages under a collapsible section:

```python
shell.add_group("files", text="Files", icon="folder")
shell.add_page("local", text="Local", icon="hdd", group="files")
shell.add_page("cloud", text="Cloud", icon="cloud", group="files")
```

### Footer pages

Place items at the bottom of the sidebar (settings, help, user profile):

```python
shell.add_page("settings", text="Settings", icon="gear", is_footer=True)
```

---

## Toolbar

The toolbar is shown by default. Add buttons to it after construction:

```python
shell.toolbar.add_button(icon="sun", command=bs.toggle_theme)
shell.toolbar.add_button(icon="gear", command=open_settings)
```

Disable the toolbar entirely:

```python
shell = bs.AppShell(title="My App", show_toolbar=False)
```

---

## Programmatic navigation

```python
shell.navigate("settings")          # switch to a page by key
print(shell.current_page)           # key of the active page
```

### Responding to page changes

```python
shell.on_page_changed(lambda e: print(f"Now on: {shell.current_page}"))
```

---

## Undecorated (custom window chrome)

!!! warning "Windows and Linux only"
    `undecorated=True` has no effect on macOS and is silently ignored there.

Remove the OS title bar and borders, giving the toolbar full control over window chrome. The toolbar automatically gains minimize, maximize, and close buttons and becomes draggable.

```python
shell = bs.AppShell(
    title="Custom Window",
    minsize=(1000, 650),
    undecorated=True,
)

shell.toolbar.add_button(icon="sun", command=bs.toggle_theme)

home = shell.add_page("home", text="Home", icon="house")
settings = shell.add_page("settings", text="Settings", icon="gear", is_footer=True)

shell.mainloop()
```

---

## Components

AppShell exposes its internal widgets as properties:

| Property | Type | Description |
|----------|------|-------------|
| `toolbar` | `Toolbar` or `None` | The top toolbar |
| `nav` | `SideNav` or `None` | The sidebar navigation |
| `pages` | `PageStack` | The page content area |
| `current_page` | `str` or `None` | Key of the active page |

---

## Additional resources

### Related widgets

- [SideNav](sidenav.md) — standalone sidebar navigation
- [Toolbar](toolbar.md) — standalone toolbar
- [PageStack](../views/pagestack.md) — page container

### Guides

- [App Structure](../../guides/app-structure.md) — App vs AppShell, project layout, lifecycle
- [Windowing](../../guides/windowing.md) — sizing, positioning, close handling
- [Navigation](../../guides/navigation.md) — navigation patterns and AppShell usage

### API reference

- [`bootstack.AppShell`](../../reference/app/AppShell.md)