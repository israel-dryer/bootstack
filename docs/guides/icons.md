---
title: Icons
---

# Icons

This guide explains how to use icons effectively in bootstack applications—from simple buttons to state-aware toolbar actions.

---

## Icons as framework infrastructure

In bootstack, icons are **named resources**, not file paths.

When you specify an icon:

```python
bs.Button(app, text="Settings", icon="gear")
```

The framework:

- resolves the name through an icon provider
- recolors the icon to match the widget's foreground
- scales it for the current DPI
- caches it for reuse
- updates it when the theme changes

You don't manage image files, recolor assets, or worry about resolution. The framework handles it.

---

## Where icons come from

bootstack ships with the full **[Bootstrap Icons](https://icons.getbootstrap.com/)**
catalog. Any icon name from that catalog works as the `icon=` value:

```python
bs.Button(app, icon="house")
bs.Button(app, icon="exclamation-triangle")
bs.Button(app, icon="bar-chart")
```

When you need to find an icon, browse the
[Bootstrap Icons catalog](https://icons.getbootstrap.com/) — search by keyword,
copy the name, paste it into your widget. There are over 2,000 icons covering
common UI metaphors (navigation, actions, status, charts, file types, devices).

The underlying provider is `ttkbootstrap_icons_bs`, but you don't need to
interact with it — bootstack wires the provider in for you. Treat that package
as an implementation detail.

### Icon explorer

bootstack ships a dedicated icon browser. Run it from anywhere:

```bash
bootstack icons
```

This delegates to the `ttkbootstrap-icons` tool, which provides a full
searchable browser of the Bootstrap Icons catalog. Any icon name you find
there works directly as the `icon=` value on any bootstack widget. See
[Tooling → CLI](../tooling/cli.md) for full CLI reference.

<div class="app-window">
    <img src="../assets/guides-icons-browser.png" alt="icon browser"/>
</div>

---

## The mental model

Think of icons as **semantic identifiers**, similar to color tokens:

| Concept | You write | Framework resolves |
|---------|-----------|-------------------|
| Color | `accent="danger"` | `#dc3545` (or theme equivalent) |
| Icon | `icon="trash"` | Themed, scaled, cached image |

The same icon name works across light and dark themes. The icon adapts automatically—you don't maintain separate assets.

Icons also participate in **widget state**. When a button is disabled, its icon dims. When hovered, it can change. This happens without extra code.

---

## Basic usage

### Icon with text

```python
bs.Button(app, text="Save", icon="check")
bs.Button(app, text="Delete", icon="trash", accent="danger")
```

The icon appears to the left of the text by default.

### Icon only

```python
bs.Button(app, icon="plus", icon_only=True)
bs.Button(app, icon="x-lg", icon_only=True, accent="secondary")
```

Use `icon_only=True` when the icon is self-explanatory. The widget adjusts its padding accordingly.

### Labels with icons

```python
bs.Label(app, text="Warning: unsaved changes", icon="exclamation-triangle")
```

Icons in labels reinforce the message without making it interactive.

---

## Common UI patterns

### Toolbar actions

Toolbars typically use icon-only buttons:

```python
toolbar = bs.PackFrame(app, direction="horizontal", gap=4)

bs.Button(toolbar, icon="folder-open", icon_only=True).pack(side="left")
bs.Button(toolbar, icon="save", icon_only=True).pack(side="left")
bs.Button(toolbar, icon="printer", icon_only=True).pack(side="left")
```

### Icon + text for clarity

Primary actions benefit from both:

```python
bs.Button(app, text="New Project", icon="plus-lg", accent="primary")
bs.Button(app, text="Export", icon="download")
```

### Contextual emphasis

Use color to reinforce icon meaning:

```python
bs.Button(app, text="Delete", icon="trash", accent="danger")
bs.Button(app, text="Success", icon="check-circle", accent="success")
bs.Label(app, text="Connection lost", icon="wifi-off", accent="warning")
```

### Menu items

Menus support icons for quick recognition:

```python
menu.add_command(label="Cut", icon="scissors")
menu.add_command(label="Copy", icon="copy")
menu.add_command(label="Paste", icon="clipboard")
```

---

## Icon specifications

For more control, pass a dict instead of a string:

```python
bs.Button(app, text="Settings", icon={
    "name": "gear",
    "size": 18,
})
```

### Available options

| Key | Purpose |
|-----|---------|
| `name` | Icon identifier (required) |
| `size` | Size in pixels (default: 20, DPI-scaled) |
| `color` | Override color (hex or semantic token) |
| `state` | Per-state icon overrides (list of tuples) |

### State-based icons

Some widgets have multiple visual states where different icons make sense. Use the `state` key to specify per-state overrides:

```python
bs.CheckToggle(app, text="Enable notifications", icon={
    "name": "bell-slash",
    "state": [
        ("selected", {"name": "bell"}),
    ]
})
```

When unselected, the toggle shows `bell-slash`. When selected, it shows `bell`.

State expressions follow TTK conventions:

| Expression | Meaning |
|------------|---------|
| `"selected"` | Widget is selected/checked |
| `"disabled"` | Widget is disabled |
| `"hover !disabled"` | Mouse over, but not disabled |
| `"pressed !disabled"` | Being clicked |
| `"focus !disabled"` | Has keyboard focus |

Each state override can specify `name`, `color`, or both:

```python
bs.Button(app, text="Play", icon={
    "name": "play",
    "state": [
        ("hover !disabled", {"name": "play-fill"}),
        ("pressed !disabled", {"color": "#ffffff"}),
    ]
})
```

### When to use specs

Use the dict form when you need to:

- adjust size for visual balance
- override color for emphasis
- fine-tune appearance in specific contexts

For most cases, the string form is sufficient.

---

## DPI and scaling

bootstack handles icon scaling automatically.

When you specify `size=16`, the framework:

- detects the display's DPI
- scales the icon appropriately
- maintains crisp rendering

You write the same code for standard and high-DPI displays. No manual asset management, no `@2x` variants.

---

## Icons and themes

Icons adapt to theme changes automatically:

```python
# Same code works for both themes
bs.Button(app, text="Edit", icon="pencil")
```

In a light theme, the icon renders dark. In a dark theme, it renders light. The framework derives icon color from the widget's foreground, which the theme controls.

If you override `color` in an icon spec, that color is used instead—but this is rarely necessary.

---

## Icons and localization

Icons reinforce meaning but shouldn't replace text for critical actions:

```python
# Good: icon reinforces label
bs.Button(app, text="Delete", icon="trash")

# Use carefully: icon-only requires universal recognition
bs.Button(app, icon="x-lg", icon_only=True)  # Close button - widely understood
```

For localized applications:

- pair icons with translated labels
- reserve icon-only for universally understood symbols (close, minimize, search)
- test icon meaning across target cultures

!!! link "Localization Guide"
    See [Localization](localization.md) for internationalization patterns.

---

## What not to do

Avoid Tkinter habits that bypass the icon system:

| Don't | Why |
|-------|-----|
| Use file paths for icons | Bypasses theming and caching |
| Manually recolor images | Framework handles state colors |
| Maintain light/dark asset sets | Icons adapt automatically |
| Hardcode icon colors | Use color token or let theme decide |
| Resize images yourself | DPI scaling is automatic |

The icon system exists to handle these concerns. Use it.

---

## Summary

- Icons are **named resources**, not files
- The framework handles **theming, scaling, and caching**
- Use `icon="name"` for simple cases, `icon={...}` for control
- Icons adapt to **widget state** automatically
- Pair icons with text for **clarity and accessibility**

---

## Related resources

- [Design System: Icons](../design-system/icons.md) — design philosophy and principles
- [Color & Theming](color-and-theming.md) — color tokens, surfaces, theme configuration and switching
- [Localization](localization.md) — internationalization patterns