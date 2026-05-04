---
title: Switch
---

# Switch

`Switch` is a **selection control** for toggling a setting **on** or **off**, rendered with a distinctive
**switch/slider** appearance.

Use `Switch` when the control represents a single binary setting that takes effect immediately, such as enabling
a feature, turning on notifications, or activating a mode.

---

## Quick start

```python
import bootstack as bs

app = bs.App()

bs.Switch(app, text="Enable dark mode", value=True).pack(padx=20, pady=6)
bs.Switch(app, text="Send notifications", value=False).pack(padx=20, pady=6)

app.mainloop()
```

---

## When to use

Use `Switch` when:

- the setting is binary (on/off)
- the change takes effect immediately
- you want a clear visual toggle indicator

### Consider a different control when...

- you need tri-state (indeterminate) support -> use [CheckButton](checkbutton.md)
- multiple related options can be enabled -> use [CheckButton](checkbutton.md) for each
- you want a compact button-like toggle -> use [CheckToggle](checktoggle.md)
- only one choice is allowed in a group -> use [RadioButton](radiobutton.md)

---

## Appearance

### Colors and styling

Use semantic color tokens with the `accent` parameter.

```python
bs.Switch(app, text="Primary", accent="primary")
bs.Switch(app, text="Secondary", accent="secondary")
bs.Switch(app, text="Success", accent="success")
bs.Switch(app, text="Warning", accent="warning")
bs.Switch(app, text="Danger", accent="danger")
```

!!! link "See [Design System - Variants](../../design-system/variants.md) for how color tokens apply consistently across widgets."

---

## Examples & patterns

### How the value works

`Switch` uses a boolean value model:

- `True` -> on (switch is toggled)
- `False` -> off (switch is not toggled)

The `value` option sets the **initial state**. Once bound, the signal or variable becomes the source of truth.

!!! note "Value precedence"
    The `value` option is only used during initialization.
    After creation, the bound signal or variable controls the widget state.

### Common options

#### `text`

Label shown next to the switch.

```python
bs.Switch(app, text="Auto-save")
```

#### `command`

Run a callback when the switch toggles.

```python
enabled = bs.BooleanVar(value=True)

def on_toggle():
    print("now:", enabled.get())

bs.Switch(app, text="Enable feature", variable=enabled, command=on_toggle).pack(padx=20, pady=20)
```

#### `state`

Disable or enable the widget.

```python
sw = bs.Switch(app, text="Locked", state="disabled")
sw.pack()

sw.configure(state="normal")
```

#### `padding`, `width`, `underline`

```python
bs.Switch(app, text="Wider", padding=(10, 6), width=18).pack(pady=6)
bs.Switch(app, text="E_xport", underline=1).pack(pady=6)
```

### Reacting to changes

Use `command` for immediate callbacks, or subscribe to the signal/variable for reactive updates.

```python
# Using command callback
def on_toggle():
    print("toggled!")

sw = bs.Switch(app, text="Feature", command=on_toggle)

# Using signal subscription
enabled = bs.Signal(False)
sw = bs.Switch(app, text="Feature", signal=enabled)
enabled.subscribe(lambda v: print(f"Value: {v}"))
```

---

## Behavior

- Click toggles between on and off states.
- Unlike `CheckButton`, `Switch` does not support an indeterminate state.
- Keyboard navigation follows standard ttk checkbutton behavior (focus + Space to toggle).
- The visual design clearly communicates whether the setting is active.

---

## Localization

By default, widgets use `localize="auto"`:

- if a translation key exists, it is used
- otherwise, the label is treated as a literal string

```python
bs.Switch(app, text="settings.dark_mode")
bs.Switch(app, text="settings.dark_mode", localize=True)
bs.Switch(app, text="Dark Mode", localize=False)
```

!!! tip "Safe to pass literal text"
    With `localize="auto"`, passing literal text is safe when no translation exists.

!!! link "See [Localization](../../capabilities/localization.md) for configuring translations and message catalogs."

---

## Reactivity

Prefer a reactive `signal=...` in v2 apps:

```python
import bootstack as bs

app = bs.App()

dark_mode = bs.Signal(False)

sw = bs.Switch(
    app,
    text="Dark mode",
    signal=dark_mode,
)
sw.pack(padx=20, pady=20)

# React to changes
dark_mode.subscribe(lambda v: print(f"Dark mode: {v}"))

app.mainloop()
```

You can also bind a Tk variable with `variable=...`.

!!! link "See [Signals](../../capabilities/signals/index.md) for reactive programming patterns."

---

## Switch vs CheckButton vs CheckToggle

| Widget | Appearance | Use case |
|--------|------------|----------|
| **Switch** | Slider/toggle track | Immediate on/off settings |
| **CheckButton** | Checkbox indicator | Multi-select, forms, tri-state |
| **CheckToggle** | Pressed button | Toolbars, compact UI areas |

Choose based on the visual context and whether you need tri-state support.

---

## Additional resources

### Related widgets

- [CheckButton](checkbutton.md) - classic checkbox with tri-state support
- [CheckToggle](checktoggle.md) - button-like toggle presentation
- [RadioButton](radiobutton.md) - choose one option from a group
- [Form](../forms/form.md) - use `editor='switch'` or `editor='toggle'` for switch fields

### Framework concepts

- [Signals](../../capabilities/signals/index.md) - reactive state management
- [Localization](../../capabilities/localization.md) - text translation
- [Design System](../../design-system/variants.md) - color tokens and variants

### API reference

- [`bootstack.Switch`](../../reference/widgets/Switch.md)
