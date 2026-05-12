---
title: Progressbar
---

# Progressbar

`Progressbar` displays **task progress over time**.

It communicates how much work has completed (determinate) or that work is ongoing (indeterminate), without requiring user interaction.

---

## Quick start

```python
import bootstack as bs

app = bs.App()

pb = bs.Progressbar(app, maximum=100, value=40)
pb.pack(fill="x", padx=20, pady=20)

app.mainloop()
```

---

## When to use

Use Progressbar when:

- progress is linear and measurable
- users benefit from seeing completion percentage
- tracking task progress over time

### Consider a different control when...

- **You want a dashboard-style indicator** — use [Meter](meter.md)
- **You need to show capacity or fullness** — use [FloodGauge](floodgauge.md)
- **You need a compact status indicator** — use [Badge](badge.md)

---

## Appearance

### Styling with `accent`

```python
bs.Progressbar(app, accent="success")
bs.Progressbar(app, accent="warning")
bs.Progressbar(app, accent="danger")
```

### Variants

Use `variant=` to change the bar style:

```python
bs.Progressbar(app, variant="striped")  # animated diagonal stripes
bs.Progressbar(app, variant="thin")     # reduced height bar
```

!!! link "See [Design System](../../design-system/index.md) for color tokens and theming guidelines."

---

## Examples & patterns

### Value model

- **Determinate**: shows progress between `0` and `maximum`
- **Indeterminate**: animates continuously to indicate ongoing work

### Common options

| Option | Purpose |
|---|---|
| `value` | Current progress value |
| `maximum` | Maximum value (default `100`) |
| `mode` | `"determinate"` or `"indeterminate"` |
| `length` | Pixel length of the bar |
| `orient` | `"horizontal"` or `"vertical"` |

### Reading and setting value

```python
pb = bs.Progressbar(app, maximum=100)
pb.pack()

pb.set(50)           # set value
print(pb.get())      # read value
print(pb.value)      # property form
pb.value = 75

pb.configure(value=50)   # also works
pb.step(10)              # increment by 10
```

### Indeterminate animation

```python
pb.configure(mode="indeterminate")
pb.start(interval=10)   # interval in milliseconds
# ... long-running task ...
pb.stop()
pb.configure(mode="determinate", value=0)
```

---

## Reactivity

Bind a signal to drive the progress bar from application state:

```python
progress = bs.Signal(0)
pb = bs.Progressbar(app, signal=progress)

progress.set(50)   # progressbar updates automatically
```

!!! link "See [Reactivity](../../guides/reactivity.md) for reactive programming patterns."

---

## Additional resources

### Related widgets

- [Meter](meter.md) — dashboard-style gauge indicators
- [FloodGauge](floodgauge.md) — capacity/level indicators
- [Badge](badge.md) — compact status indicators

### Framework concepts

- [Design System](../../design-system/index.md) — colors, typography, and theming
- [Reactivity](../../guides/reactivity.md) — reactive data binding

### API reference

- [`bootstack.Progressbar`](../../reference/widgets/Progressbar.md)