---
title: FloodGauge
---

# FloodGauge

`FloodGauge` is a **filled-level indicator** that visualizes how full a value is within a range.

It's especially useful for capacity, utilization, or threshold-based indicators.

---

## Quick start

```python
import bootstack as bs

app = bs.App()

fg = bs.FloodGauge(app, value=75)
fg.pack(fill="x", padx=20, pady=20)

app.mainloop()
```

---

## When to use

Use FloodGauge when:

- capacity or fullness matters
- thresholds are more important than exact numbers
- visualizing resource utilization

### Consider a different control when...

- **Tracking task progress over time** — use [Progressbar](progressbar.md)
- **You need a dashboard-style circular gauge** — use [Meter](meter.md)
- **You need a compact text-based indicator** — use [Badge](badge.md)

---

## Appearance

### Styling with `accent`

```python
bs.FloodGauge(app, accent="warning")
bs.FloodGauge(app, accent="danger")
bs.FloodGauge(app, accent="success")
```

!!! link "See [Design System](../../design-system/index.md) for color tokens and theming guidelines."

---

## Examples & patterns

### Common options

- `value` — current fill level (int, default `0`)
- `maximum` — maximum value (default `100`)
- `text` — static label displayed on the gauge
- `mask` — dynamic text overlay with `{}` placeholder (e.g. `"{} MB free"`) — updates automatically as value changes
- `orient` — `"horizontal"` (default) or `"vertical"`
- `length` — pixel length along the main axis (default `200`)
- `thickness` — pixel size along the minor axis (default `50`)
- `increment` — step size for `start()` animations (default `1`)

### Programmatic control

```python
fg = bs.FloodGauge(app, value=50)
fg.pack()

current = fg.get()     # 50
fg.set(75)
print(fg.value)        # 75
fg.value = 90
fg.step(5)             # increment by 5
```

### With text label

Static label:
```python
bs.FloodGauge(app, value=65, text="Storage").pack(fill="x", padx=20)
```

Dynamic label (updates with value):
```python
bs.FloodGauge(app, value=65, mask="{}% used").pack(fill="x", padx=20)
```

### Indeterminate animation

```python
fg = bs.FloodGauge(app, mode="indeterminate")
fg.pack(fill="x")
fg.start()     # begins bouncing animation
# ...
fg.stop()
```

### Vertical orientation

```python
bs.FloodGauge(app, value=50, orient="vertical").pack(pady=20)
```

### Reactive updates

FloodGauge has no signal mixin. Drive updates by subscribing a signal to `fg.set`:

```python
level = bs.Signal(25)
fg = bs.FloodGauge(app, variable=level.var)

# Or subscribe directly
level.subscribe(fg.set)
level.set(90)   # gauge updates
```

---

## Behavior

- The fill level updates proportionally based on `value / maximum`
- Call `configure(accent="danger")` when a threshold is crossed — color does not change automatically
- `step()` increments with wraparound

---

## Additional resources

### Related widgets

- [Progressbar](progressbar.md) — linear progress indicators
- [Meter](meter.md) — dashboard-style gauge indicators
- [Badge](badge.md) — compact status indicators

### Framework concepts

- [Design System](../../design-system/index.md) — colors, typography, and theming

### API reference

- [`bootstack.FloodGauge`](../../reference/widgets/FloodGauge.md)