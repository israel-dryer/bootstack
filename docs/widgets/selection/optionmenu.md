---
title: OptionMenu
---

# OptionMenu

`OptionMenu` is a **selection control** that lets users pick **one value from a short list** using a
menu-style dropdown.

`OptionMenu` wraps `bs.MenuButton` and adds theming, icons, signals, and standardized change events.
It is best suited for **compact, known option sets**.

Use `OptionMenu` when the list is small and users already know the available choices.
For longer lists or search/filtering, prefer [SelectBox](selectbox.md).

---

## Overview

`OptionMenu` provides:

- **single selection** (one committed value)
- **menu-based** dropdown behavior
- compact desktop-friendly appearance
- optional **signals** and `<<Change>>` events

It is intentionally simpler than `SelectBox` and does not support search or custom values.

---

## Basic usage

```python
import bootstack as bs

app = bs.App()

menu = bs.OptionMenu(
    app,
    value="Medium",
    options=["Low", "Medium", "High"],
)
menu.pack(padx=20, pady=20)

app.mainloop()
```

---

## How the value works

- `options` defines the list of valid values
- `value` is the currently selected option

```python
print(menu.value)
menu.value = "High"
menu.get()              # equivalent to menu.value
menu.set("Low")         # equivalent to menu.value = "Low"
```

---

## Binding to signals or variables

### Using a signal (preferred)

```python
selected = bs.Signal("Medium")

menu = bs.OptionMenu(
    app,
    textsignal=selected,
    options=["Low", "Medium", "High"],
)

selected.subscribe(lambda v: print("changed:", v))
```

### Using a Tk variable

```python
color = bs.StringVar(value="Green")

menu = bs.OptionMenu(
    app,
    textvariable=color,
    options=["Red", "Green", "Blue"],
)
```

---

## Common options

### `options`

```python
menu.configure(options=["Apple", "Banana", "Cherry"])
```

### `command`

Callback invoked on every selection change — no arguments:

```python
menu = bs.OptionMenu(app, value="A", options=["A", "B"],
                     command=lambda: print("selected:", menu.value))
```

### `state`

```python
menu.configure(state="disabled")
menu.configure(state="normal")
```

### `density`

```python
bs.OptionMenu(app, value="A", options=["A", "B"], density="compact")
```

### `localize`

Control label localization per-widget:

```python
bs.OptionMenu(app, value="menu.opt.a", options=["menu.opt.a", "menu.opt.b"],
              localize=True)
```

### `width` and `padding`

```python
bs.OptionMenu(app, value="A", options=["A", "B"], width=20, padding=(10, 6))
```

### Dropdown button options

```python
bs.OptionMenu(app, value="A", options=["A", "B"], show_dropdown_button=False)
bs.OptionMenu(app, value="A", options=["A", "B"], dropdown_button_icon="chevron-down")
```

---

## Behavior

- Clicking the button opens a menu of options.
- Selecting an item immediately commits the value.
- The menu closes automatically after selection.
- Keyboard: standard menubutton navigation.

---

## Events

```python
def on_changed(event):
    print("Selected:", event.data["value"])

bind_id = menu.on_changed(on_changed)
menu.off_changed(bind_id)
```

The event name is `<<Change>>`. The callback receives a Tkinter event object with `event.data["value"]`.

---

## Colors and styling

`OptionMenu` supports the same `accent` and `variant` options as `MenuButton` (`"solid"`, `"outline"`, `"ghost"`):

```python
bs.OptionMenu(app, value="A", options=["A", "B"], accent="primary")
bs.OptionMenu(app, value="A", options=["A", "B"], accent="primary", variant="outline")
bs.OptionMenu(app, value="A", options=["A", "B"], accent="primary", variant="ghost")
```

---

## Icons

```python
bs.OptionMenu(
    app,
    value="Dark",
    options=["Light", "Dark", "Auto"],
    icon="palette",
)
```

!!! warning "Using `image=`"
    Passing a Tk `PhotoImage` via `image=` will not automatically recolor on theme changes.

---

## Localization

`OptionMenu` text participates in localization. When `localize="auto"` (the default), untranslated keys fall back to literal text.

!!! link "See [Localization](../../guides/localization.md) for configuring translations and message catalogs."

---

## When should I use OptionMenu?

Use `OptionMenu` when:

- the option list is short (up to ~8 items)
- the control should remain compact
- search or rich presentation is unnecessary

Prefer **SelectBox** when the list is longer, search helps, or users may enter custom values.
Prefer **RadioButton / RadioGroup** when there are very few options and showing them inline improves clarity.

---

## Additional resources

### Related widgets

- [SelectBox](selectbox.md) — dropdown selection with search and filtering
- [RadioButton](radiobutton.md) — inline mutually exclusive options
- [RadioGroup](radiogroup.md) — grouped radio options
- [MenuButton](../actions/menubutton.md) — base widget for menu-triggered buttons

### API reference

- [`bootstack.OptionMenu`](../../reference/widgets/OptionMenu.md)