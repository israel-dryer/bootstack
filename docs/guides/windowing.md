---
title: Windowing
---

# Windowing

`App`, `AppShell`, and `Toplevel` all share the same window management API. This guide covers that shared surface — sizing, positioning, lifecycle, close handling, secondary windows, and platform specifics.

For choosing between `App` and `AppShell`, see [App Structure](app-structure.md). For AppShell navigation configuration, see the [AppShell widget doc](../widgets/navigation/appshell.md).

---

## Window hierarchy

Every bootstack application has one root window — either `App` or `AppShell`. Secondary windows are `Toplevel` instances. All three share the same theme and event loop.

```python
import bootstack as bs

app = bs.App(title="Main Window", size=(900, 600))

def open_inspector():
    win = bs.Toplevel(title="Inspector", size=(400, 500), transient=app)
    bs.Label(win, text="Inspector content").pack(padx=20, pady=20)
    win.show()

bs.Button(app, text="Open Inspector", command=open_inspector).pack(pady=20)
app.mainloop()
```

`Toplevel` inherits the active theme automatically. You do not need to pass a theme.

---

## Sizing

Set the initial size at construction, or apply constraints after the fact.

```python
# Fixed initial size
app = bs.App(title="My App", size=(1024, 768))

# Size constraints only — window starts at its natural size
app = bs.App(title="My App", minsize=(800, 500), maxsize=(1920, 1080))

# Prevent resizing
app = bs.App(title="My App", size=(600, 400), resizable=(False, False))
```

### Sizing to a percentage of the screen

Use `set_default_size()` when you want the window to adapt to different screen sizes rather than pinning a fixed pixel size.

```python
app = bs.App(title="My App")
app.set_default_size(width_ratio=0.75, height_ratio=0.8, min_width=800, min_height=500)
app.mainloop()
```

### Applying constraints after construction

```python
app.apply_size_constraints(
    minsize=(600, 400),
    resizable=(True, False),  # width resizable, height fixed
)
```

---

## Positioning

Windows center on the screen by default when no `position` is given. You can override this at construction or move the window afterwards.

```python
# Explicit screen position at construction
app = bs.App(title="My App", size=(800, 600), position=(100, 100))
```

### Positioning utilities

All window types expose the same placement methods:

```python
app.place_center()               # center on screen
app.place_at(200, 150)           # move to specific coordinates
app.place_center_on(parent_win)  # center on another window (useful for dialogs)
```

For `Toplevel` windows used as popups, dropdowns, or context menus:

```python
# Anchor a popup below a trigger widget
popup.place_anchor(
    anchor_to=button,
    anchor_point="sw",   # bottom-left of the button
    window_point="nw",   # align popup's top-left to that point
    offset=(0, 4),
)

# Dropdown aligned to a trigger
menu.place_dropdown(trigger_widget=button, prefer_below=True, align="left")

# Context menu at the cursor
menu.place_cursor(offset=(2, 2))
```

All placement methods clamp the result to keep the window on screen.

---

## Show, hide, and window state

`mainloop()` calls `show()` automatically on the root window. For `Toplevel` windows you call `show()` yourself after construction.

```python
win = bs.Toplevel(title="Panel", size=(400, 300))
win.show()           # map the window
win.hide()           # unmap without destroying (withdraw)
win.minimize()       # iconify
win.maximize()       # zoom / maximize
win.set_fullscreen() # enter fullscreen
win.set_fullscreen(False)  # exit fullscreen
```

### Transparency

```python
win = bs.Toplevel(title="Overlay", alpha=0.9)  # set at construction
win.set_alpha(0.7)                              # change after construction
```

### Always on top

```python
win = bs.Toplevel(title="Palette", topmost=True)   # at construction
win.set_topmost(True)   # after construction
win.set_topmost(False)  # cancel
```

---

## Close handling

By default, clicking the close button destroys the window. Use `on_close()` to intercept it.

```python
app = bs.App(title="Editor")

def on_close():
    if has_unsaved_changes():
        confirmed = bs.Messagebox.yesno("Unsaved changes", "Quit without saving?")
        if confirmed == "Yes":
            app.close()
    else:
        app.close()

app.on_close(on_close)
app.mainloop()
```

`on_close()` is a convenience wrapper for `protocol("WM_DELETE_WINDOW", handler)`. The handler must explicitly call `app.close()` (or `win.destroy()`) — registering a handler replaces the default close behavior entirely.

---

## Secondary windows with Toplevel

Use `Toplevel` for persistent auxiliary windows — inspectors, tool palettes, settings panels — that coexist with the main window. Use `bs.Dialog` subclasses for prompt/response interactions where you need a return value.

```python
def open_settings():
    win = bs.Toplevel(
        title="Settings",
        size=(500, 400),
        transient=app,     # stays above app, excluded from taskbar
        minsize=(400, 300),
    )
    # ... populate with widgets ...
    win.show()
```

### Transient relationship

`transient=app` tells the window manager that this window belongs to `app`. The effect varies by platform — on most systems the transient window stays above its parent and is omitted from the taskbar or window switcher.

### Tool windows

On Windows, `toolwindow=True` gives the window a narrow title bar, which is conventional for palette-style panels.

```python
palette = bs.Toplevel(title="Tools", toolwindow=True, topmost=True, size=(200, 400))
```

---

## Window state persistence

Set `remember_window_state=True` in `AppSettings` and the app saves its size and position on close, then restores them on the next launch. Off-screen positions (from a disconnected monitor) are clamped back into view automatically.

```python
app = bs.App(
    title="My App",
    settings={"remember_window_state": True},
)
```

State is stored in the OS config directory (`%APPDATA%` on Windows, `~/Library/Application Support` on macOS, `$XDG_CONFIG_HOME` on Linux), in a per-app file so multiple bootstack apps don't collide.

Override the path if you need control over where state is stored:

```python
settings = bs.AppSettings(
    remember_window_state=True,
    state_path="config/window_state.json",
)
app = bs.App(title="My App", settings=settings)
```

---

## Platform specifics

### Windows — Mica/Acrylic effects

On Windows 11, bootstack applies the Mica material to window chrome by default. Change or disable it via `window_style`:

```python
app = bs.App(title="My App", settings={"window_style": "acrylic"})
app = bs.App(title="My App", settings={"window_style": None})   # disable
```

Accepted values: `"mica"` (default), `"acrylic"`, `"aero"`, `"transparent"`, `"win7"`.

### macOS — Quit behavior

By default, clicking the close button on macOS hides the app (matching Mac convention) rather than destroying it. Cmd+Q is the real quit signal. Set `macos_quit_behavior="classic"` to restore the cross-platform destroy-on-close behavior.

```python
app = bs.App(title="My App", settings={"macos_quit_behavior": "classic"})
```

### System appearance tracking

On macOS, `follow_system_appearance=True` switches between `light_theme` and `dark_theme` automatically when the OS appearance changes.

```python
app = bs.App(
    title="My App",
    settings={
        "follow_system_appearance": True,
        "light_theme": "bootstrap-light",
        "dark_theme": "bootstrap-dark",
    },
)
```

---

## Common pitfalls

**Creating widgets before `App`.**
Tk requires a root window before any widgets can be created. Always create `App` or `AppShell` first.

**Multiple `App` instances.**
Only one `App` per process. Use `Toplevel` for additional windows.

**Forgetting `show()` on Toplevel.**
`Toplevel` windows start withdrawn. Call `win.show()` after constructing and populating them, or the window never appears.

**`on_close` handler that doesn't close.**
Registering `on_close` replaces the default close behavior entirely. If your handler decides not to close, that's fine — but if you want the window to close in the normal case, your handler must call `app.close()` or `win.destroy()` explicitly.

---

## Additional resources

- [App Structure](app-structure.md) — choosing between App and AppShell, project layout, lifecycle
- [AppShell](../widgets/navigation/appshell.md) — navigation configuration (pages, toolbar, nav modes)
- [Dialogs](../widgets/dialogs/index.md) — modal prompt/response interactions
- [Color & Theming](color-and-theming.md) — runtime theme switching