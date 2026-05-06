---
title: Spinbox
---

# Spinbox

`Spinbox` is a **primitive input** that wraps `bs.Spinbox` with bootstack styling and reactive text support.

It provides low-level spin behavior (range or list stepping) while still allowing direct typing. Use `Spinbox` when you want
native ttk options like `format` and `command`. For a form-ready field with labels/messages/validation and standardized events,
prefer [SpinnerEntry](../inputs/spinnerentry.md).

---

## Quick start

### Numeric range

```python
import bootstack as bs

app = bs.App()

spin = bs.Spinbox(app, from_=0, to=10, increment=1, width=8)
spin.pack(padx=20, pady=20)

app.mainloop()
```

### Fixed list of values

```python
import bootstack as bs

app = bs.App()

spin = bs.Spinbox(app, values=("XS", "S", "M", "L", "XL"), wrap=True, width=8)
spin.pack(padx=20, pady=20)

app.mainloop()
```

---

## When to use

Use `Spinbox` when:

- you want low-level ttk spinbox behavior and options

- the range/list is small and predictable

- you're building your own composite control

### Consider a different control when...

- **you want a form-ready field (labels/messages/validation/events)** - prefer [SpinnerEntry](../inputs/spinnerentry.md)

- **the choices are better expressed as a dropdown list** - prefer [SelectBox](../selection/selectbox.md)

---

## Appearance

### `accent`

Applies bootstack theme styling.

```python
bs.Spinbox(app, from_=0, to=10, accent="primary")
```

!!! link "Design System"
    See the [Design System](../../design-system/index.md) for available color tokens.

---

## Examples and patterns

### Value model

Spinbox stores and returns **text** (even in numeric mode).

```python
value = spin.get()
```

Bind with:

- `textvariable=` (Tk variable), or

- `textsignal=` (reactive signal)

### Common options

#### Range mode: `from_`, `to`, `increment`

```python
bs.Spinbox(app, from_=1, to=31, increment=1)
```

#### Values mode: `values`

```python
bs.Spinbox(app, values=("Low", "Medium", "High"))
```

If `values` is provided, it takes precedence over the numeric range.

#### `wrap`

```python
bs.Spinbox(app, from_=0, to=5, wrap=True)
bs.Spinbox(app, values=("A", "B", "C"), wrap=True)
```

#### `state="readonly"`

Use readonly mode when you want pick-only interaction.

```python
bs.Spinbox(app, values=("A", "B", "C"), state="readonly")
```

#### `format` (range mode)

```python
bs.Spinbox(app, from_=0, to=1, increment=0.05, format="%.2f")
```

### Events

#### `command`

```python
def on_change():
    print(spin.get())

spin = bs.Spinbox(app, from_=0, to=10, command=on_change)
```

If you need to respond to typing, bind key events:

```python
spin.bind("<KeyRelease>", lambda e: print(spin.get()))
```

---

## Behavior

- Users can type or use arrows to step.

- In many Tk builds, `command` is primarily invoked by arrow interactions (not typing).

- Wrapping cycles max->min (range) or last->first (values).

### Validation and constraints

Spinbox does not provide control-level parsing/validation by default. It is a primitive widget.

For validated, commit-based workflows, prefer [SpinnerEntry](../inputs/spinnerentry.md) or [NumericEntry](../inputs/numericentry.md).

---

## Additional resources

### Related widgets

- [SpinnerEntry](../inputs/spinnerentry.md) - form-ready stepper control

- [NumericEntry](../inputs/numericentry.md) - validated numeric input

- [Scale](../inputs/scale.md) - continuous adjustment

- [Combobox](combobox.md) - selection + optional typing

### Framework concepts

- [Events and Signals](../../guides/reactivity.md)

### API reference

- [`bootstack.Spinbox`](../../reference/widgets/Spinbox.md)