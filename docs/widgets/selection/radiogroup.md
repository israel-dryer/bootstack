---
title: RadioGroup
---

# RadioGroup

`RadioGroup` is a **composite selection control** that manages a set of `RadioButton` widgets as a single unit.

Use `RadioGroup` when you want a convenient way to build a mutually exclusive choice list without manually wiring
multiple `RadioButton` instances to the same signal or variable.

---

## Quick start

```python
import bootstack as bs

app = bs.App()

group = bs.RadioGroup(app, text="Choose a plan", orient="vertical", value="basic")
group.add("Basic",      "basic")
group.add("Pro",        "pro")
group.add("Enterprise", "enterprise")
group.pack(padx=20, pady=20, fill="x")

app.mainloop()
```

---

## When to use

Use `RadioGroup` when:

- you want a single widget that manages a set of radio options
- you want consistent layout and labeling for the group
- you want a simple subscribe/unsubscribe change API

### Consider a different control when...

- you need custom per-option layout — use individual **RadioButton** widgets
- you want complete control over spacing and structure — use individual **RadioButton** widgets

---

## Appearance

### Orientation

`orient` defaults to `"horizontal"`. Pass `orient="vertical"` for a stacked layout.

```python
bs.RadioGroup(app, orient="horizontal")  # default
bs.RadioGroup(app, orient="vertical")
```

### Label placement

`labelanchor` controls where the group label appears. Accepts `'n'` (default), `'s'`, `'w'`, `'e'`.

```python
bs.RadioGroup(app, text="Pick one", labelanchor="w", orient="horizontal")
```

### Border and surface

Use `show_border=True` to draw a border around the group. `surface=` controls the background token.

```python
bs.RadioGroup(app, text="Plan", show_border=True)
bs.RadioGroup(app, surface="card")
```

### Colors and styling

`accent` is forwarded to all child buttons.

```python
group = bs.RadioGroup(app, accent="success")
```

### Indicator visibility

`show_indicator` is forwarded to all child buttons. Set it to `False` for icon-only groups
where the icon itself conveys the selection state:

```python
group = bs.RadioGroup(app, orient="horizontal", show_indicator=False)
group.add("Grid", "grid", icon="grid",      on_icon="grid-fill")
group.add("List", "list", icon="list",      on_icon="list-check")
group.add("Map",  "map",  icon="map",       on_icon="map-fill")
group.pack(padx=20, pady=20)
```

Individual `add()` calls can override the group default:

!!! link "See [Icons](../../guides/icons.md) for stateful icon specs, `on_icon`/`off_icon` shortcuts, and color overrides."

```python
group = bs.RadioGroup(app, show_indicator=False)
group.add("Standard", "std")                           # inherits show_indicator=False
group.add("Custom",   "custom", show_indicator=True)   # overrides to show indicator
```

!!! link "See [Design System](../../design-system/index.md) for available colors and styling options."

---

## Examples and patterns

### How the value works

```python
group.set("pro")       # select by key (see note below)
print(group.get())     # current selection key
print(group.value)     # property form
group.value = "basic"
```

!!! note "`set()` and `get()` use **keys**, not values"
    `add(text, value, key=None)` — `key` defaults to `value`, but when you pass a custom `key=`,
    `set()` and `get()` operate on the key, not the value. For example:
    ```python
    group.add("High", "high", key="hi")
    group.set("hi")      # correct — uses key
    group.set("high")    # raises ValueError — "high" is not a key
    ```

### `add(text, value, key=None, **kwargs)`

Add an option. `value` is required. `key` defaults to `value`. Returns the created button.

```python
group.add("Low",  "low")
group.add("High", "high", key="hi")

# Pass extra kwargs to the underlying RadioButton
group.add("Pro", "pro", icon="star", state="disabled")
```

### Item management

Give items a `key=` to retrieve or modify them after creation:

```python
btn = group.item("basic")                    # retrieve button by key
group.configure_item("basic", state="disabled")  # reconfigure
group.remove("basic")                        # remove and destroy
group.keys()                                 # all keys in order
group.values()                               # all option values in order
group.items()                                # all button widgets in order
```

### `state`

```python
group = bs.RadioGroup(app, state="disabled")
group.configure(state="normal")
```

### Events

```python
def on_change(value):
    print("Selected:", value)

sub_id = group.on_changed(on_change)
group.off_changed(sub_id)
```

The callback receives the **new value** (not the key) when the selection changes.

---

## Behavior

- In horizontal orientation, buttons are packed left-to-right.
- In vertical orientation, buttons are stacked top-to-bottom.
- `orient`, `accent`, `state`, `text`, `labelanchor`, and `value` can all be updated via `configure()`.

---

## Localization

Group label and per-option labels follow normal localization rules.

!!! link "See [Localization](../../guides/localization.md) for details."

---

## Reactivity

Bind a `signal=` to control the group from outside:

```python
choice = bs.Signal("opt2")

group = bs.RadioGroup(app, text="Select:", signal=choice, orient="vertical")
group.add("Option 1", "opt1")
group.add("Option 2", "opt2")
group.pack(padx=20, pady=20)
```

!!! link "See [Reactivity](../../guides/reactivity.md) for reactive programming patterns."

---

## Additional resources

### Related widgets

- [RadioButton](radiobutton.md) — individual radio option
- [RadioToggle](radiotoggle.md) — button-like radio option
- [ToggleGroup](togglegroup.md) — connected button-style selection
- [SelectBox](selectbox.md) — single selection from a list (dropdown)
- [CheckButton](checkbutton.md) — independent multi-selection

### Framework concepts

- [Design System](../../design-system/index.md) — colors, themes, and styling
- [Reactivity](../../guides/reactivity.md) — reactive state management
- [Localization](../../guides/localization.md) — internationalization support

### API reference

- [`bootstack.RadioGroup`](../../reference/widgets/RadioGroup.md)