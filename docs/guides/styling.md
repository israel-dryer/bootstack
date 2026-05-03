---
title: Styling
---

# Styling

This guide explains how to work with bootstack's design system—semantic colors, variants, and consistent styling across widgets.

---

## Design System Thinking

bootstack styling is **intent-based**, not value-based.

Instead of:

```python
# Don't do this
button.configure(background="#dc3545", foreground="white")
```

Use semantic tokens:

```python
# Do this
bs.Button(app, text="Delete", accent="danger")
```

The theme resolves `"danger"` to appropriate colors. Change the theme, and all `"danger"` widgets update.

---

## Accent Tokens

The `accent` parameter accepts semantic color tokens:

| Token | Intent |
|-------|--------|
| `primary` | Main action, brand color |
| `secondary` | Supporting action |
| `success` | Positive outcome, confirmation |
| `info` | Informational |
| `warning` | Caution, attention needed |
| `danger` | Destructive action, error |
| `light` | Light background/text |
| `dark` | Dark background/text |

### Basic Usage

```python
bs.Button(app, text="Save", accent="primary")
bs.Button(app, text="Cancel", accent="secondary")
bs.Button(app, text="Delete", accent="danger")
```

### On Any Widget

Most widgets accept `accent`:

```python
bs.Label(app, text="Success!", accent="success")
bs.Progressbar(app, accent="info")
bs.Entry(app, accent="warning")
```

---

## Color Modifiers

Colors support **chained bracket modifiers** for dynamic adjustments:

```python
# Elevation adjustments
"background[+1]"      # One level lighter/elevated
"background[-1]"      # One level darker/recessed
"primary[+2]"         # Two levels lighter

# Shade selection
"primary[100]"        # Lightest shade
"primary[500]"        # Base shade
"primary[900]"        # Darkest shade

# Semantic modifiers
"primary[subtle]"     # Subdued version for backgrounds
"primary[muted]"      # Muted foreground with good contrast

# Chained modifiers (applied left to right)
"primary[100][muted]" # Light primary shade, then muted
"background[+1][subtle]" # Elevated background, then subtle
```

### Tone Adjustments

Tone modifiers (`+N` / `-N`) adjust lightness relative to the base color:

```python
# Lighten/darken any color
"primary[+1]"     # Lighter primary
"primary[-1]"     # Darker primary
"gray[+2]"        # Much lighter gray
```

!!! tip "Prefer Surface Tokens"
    For container backgrounds, use semantic surface tokens like `content[1]` or `chrome`
    instead of `background[+1]`. Surface tokens are theme-defined and more predictable.
    See [Surface Tokens](#surface-tokens) below.

### Shades

Shade modifiers select from the color's palette using 50-step increments (50–950):

```python
# Primary color shades (50-step increments)
"primary[50]"   # Lightest tint
"primary[100]"
"primary[150]"
"primary[200]"
"primary[250]"
"primary[300]"
"primary[350]"
"primary[400]"
"primary[450]"
"primary[500]"  # Base color
"primary[550]"
"primary[600]"
"primary[650]"
"primary[700]"
"primary[750]"
"primary[800]"
"primary[850]"
"primary[900]"
"primary[950]"  # Darkest shade
```

### Subtle and Muted

Semantic modifiers for common UI patterns:

| Modifier | Purpose |
|----------|---------|
| `subtle` | Subdued background tint—good for hover states, selection highlights |
| `muted` | Low-contrast foreground—good for secondary text, disabled states |

```python
# Subtle backgrounds
"primary[subtle]"   # Tinted background for primary context
"success[subtle]"   # Light green background for success states
"danger[subtle]"    # Light red background for error states

# Muted text
"foreground[muted]" # Secondary text color
"primary[muted]"    # Subdued primary-colored text
```

### Modifier Pipeline

Modifiers are applied left-to-right as a pipeline:

```python
# Step by step:
"primary[100][muted]"
# 1. Look up primary[100] (light primary shade)
# 2. Apply muted (reduce contrast for text)

"background[+1][subtle]"
# 1. Look up background
# 2. Elevate by +1
# 3. Apply subtle treatment
```

---

## Surface Tokens

Surface tokens provide **semantic backgrounds** for containers. Instead of calculating
elevation with `background[+1]`, use theme-defined surface ramps:

### Content Surfaces

For main content areas (pages, cards, panels):

```python
bs.Frame(app, surface="content")      # Base content (same as background)
bs.Frame(app, surface="content[1]")   # Raised content (cards, panels)
bs.Frame(app, surface="content[2]")   # Higher elevation
```

### Chrome Surfaces

For UI chrome (sidebars, toolbars, navigation):

```python
bs.Frame(app, surface="chrome")       # Sidebar/navigation background
bs.Frame(app, surface="chrome[1]")    # Toolbar background
```

### Overlay Surfaces

For floating elements (menus, dialogs, tooltips):

```python
bs.Frame(app, surface="overlay")      # Menus, dropdowns
bs.Frame(app, surface="overlay[2]")   # Dialogs
bs.Frame(app, surface="overlay[3]")   # Tooltips, toasts
```

### Titlebar

For window title bars:

```python
bs.Frame(app, surface="titlebar")
```

!!! note "Why Surface Tokens?"
    Surface tokens are **deterministic per theme**—they don't rely on computed
    `+1/-1` math. Each theme defines exactly what `content[1]` means, ensuring
    consistent visual hierarchy across light and dark modes.

---

## Frame Borders

Frames support a simple `show_border` option that adds a subtle, rounded border:

```python
# Frame with border
bs.Frame(app, show_border=True, padding=20)

# Card-style layout
card = bs.Frame(app, surface="content[1]", show_border=True, padding=20)
card.pack(padx=20, pady=20)
```

The border color is automatically derived from the theme's background and foreground
colors, ensuring it adapts correctly to light and dark modes.

---

## Variants

Widgets support **variant** modifiers to control visual emphasis:

| Variant | Effect |
|---------|--------|
| `solid` | Filled background (default) |
| `outline` | Border only, no fill |
| `ghost` | Minimal chrome, subtle hover |
| `link` | Text-only, like a hyperlink |

Use `accent` and `variant` together:

```python
bs.Button(app, text="Learn More", accent="info", variant="link")
bs.Button(app, text="Options", accent="secondary", variant="outline")
bs.CheckButton(app, text="Enable", accent="success", variant="toggle")
```

### Button Variants

```python
# Solid (default)
bs.Button(app, text="Primary", accent="primary")

# Outline
bs.Button(app, text="Primary", accent="primary", variant="outline")

# Link
bs.Button(app, text="Primary", accent="primary", variant="link")
```

### Toggle Variant

For checkbuttons and radiobuttons:

```python
bs.CheckButton(app, text="Dark Mode", variant="toggle")
bs.CheckButton(app, text="Notifications", accent="success", variant="toggle")
```

!!! link "Variants Reference"
    See [Design System → Variants](../design-system/variants.md) for all combinations.

---

## Themes

Themes define **how tokens become colors**. The same `accent="primary"` resolves to different colors depending on the active theme.

```python
# Set theme at startup
app = bs.App(theme="ocean-dark")

# Switch themes at runtime
from bootstack import set_theme, toggle_theme
set_theme("forest-light")
toggle_theme()  # Toggle between light and dark
```

!!! link "Theming Guide"
    See [Theming](theming.md) for theme structure, built-in themes, and creating custom themes.

---

## Consistent Patterns

### Accent Coding by Intent

```python
# Actions
bs.Button(form, text="Submit", accent="primary")
bs.Button(form, text="Cancel", accent="secondary")
bs.Button(form, text="Delete", accent="danger")

# Status
bs.Label(status_bar, text="Connected", accent="success")
bs.Label(status_bar, text="Warning: Low disk", accent="warning")
bs.Label(status_bar, text="Error", accent="danger")
```

### Progress Indicators

```python
# Normal progress
bs.Progressbar(app, value=50, accent="primary")

# Success state
bs.Progressbar(app, value=100, accent="success")

# Warning state
bs.Progressbar(app, value=90, accent="warning")
```

### Form Validation

```python
# Normal state
entry = bs.Entry(app)

# Error state
entry.configure(accent="danger")

# Success state
entry.configure(accent="success")
```

---

## Typography

bootstack uses semantic typography where supported:

```python
# Heading style
bs.Label(app, text="Settings", font="heading-xl")

# Body text (default)
bs.Label(app, text="Configure your preferences below.")

# Caption/small text
bs.Label(app, text="Last updated: Today", font="caption")
```

Font choices should come from the design system, not hardcoded values.

!!! link "Typography"
    See [Typography](typography.md) to learn how to use bootstack typography.

---

## Icons

Icons reinforce meaning alongside color:

```python
bs.Button(app, text="Save", accent="primary", image=save_icon, compound="left")
bs.Button(app, text="Delete", accent="danger", image=trash_icon, compound="left")
```

Icons and color work together—use `danger` styling with a warning/delete icon.

!!! link "Icons"
    See [Design System → Icons](../design-system/icons.md) for icon usage.

---

## Padding and Spacing

### Widget Padding

```python
bs.Button(app, text="Compact", padding=(5, 2))
bs.Button(app, text="Roomy", padding=(20, 10))
```

### Container Padding

```python
bs.Frame(app, padding=20)
bs.PackFrame(app, padding=(20, 10), gap=15)
```

### Consistent Spacing

Use consistent values throughout:

```python
SPACING_SM = 5
SPACING_MD = 10
SPACING_LG = 20

bs.PackFrame(app, gap=SPACING_MD, padding=SPACING_LG)
```

---

## Example: Styled Form

```python
import bootstack as bs

app = bs.App(theme="flatly")

# Form container
form = bs.LabelFrame(app, text="User Settings", padding=20)
form.pack(padx=20, pady=20, fill="x")

# Form grid
grid = bs.GridFrame(form, columns=["auto", 1], gap=(10, 8))
grid.pack(fill="x")

# Fields
bs.Label(grid, text="Username:").grid()
bs.Entry(grid).grid(sticky="ew")

bs.Label(grid, text="Email:").grid()
bs.Entry(grid).grid(sticky="ew")

bs.Label(grid, text="Role:").grid()
bs.OptionMenu(grid, values=["User", "Admin", "Guest"]).grid(sticky="ew")

# Toggles
toggles = bs.PackFrame(form, direction="vertical", gap=5)
toggles.pack(fill="x", pady=(15, 0))

bs.CheckButton(toggles, text="Email notifications", variant="toggle").pack()
bs.CheckButton(toggles, text="Two-factor auth", accent="success", variant="toggle").pack()

# Actions
actions = bs.PackFrame(form, direction="horizontal", gap=10)
actions.pack(anchor="e", pady=(20, 0))

bs.Button(actions, text="Cancel", accent="secondary", variant="outline").pack()
bs.Button(actions, text="Save Changes", accent="primary").pack()

app.mainloop()
```

---

## Common Mistakes

### Avoid Hardcoded Colors

```python
# Bad
label.configure(foreground="#ff0000")

# Good
label.configure(accent="danger")
```

### Don't Mix Semantic and Literal

```python
# Bad: inconsistent
bs.Button(app, text="OK", accent="success")
bs.Button(app, text="Cancel", background="gray")  # Won't work with ttk

# Good: consistent
bs.Button(app, text="OK", accent="success")
bs.Button(app, text="Cancel", accent="secondary")
```

### Use Appropriate Tokens

```python
# Bad: using "danger" for non-destructive action
bs.Button(app, text="Next", accent="danger")

# Good: using appropriate token
bs.Button(app, text="Next", accent="primary")
```

---

## Summary

- Use **accent tokens** for semantic coloring
- Use **surface tokens** for container backgrounds
- Use **show_border** for frame borders
- Use **variant** (outline, link, ghost) for style modifications
- Change **themes** to update all widgets at once
- Maintain **consistency** with reusable spacing constants
- Let the **design system** handle the details

!!! link "Design System"
    See [Design System](../design-system/index.md) for the complete reference.

---

## Next Steps

- [App Structure](app-structure.md) — how applications are organized
- [Layout](layout.md) — building layouts with containers
- [Reactivity](reactivity.md) — signals and reactive updates