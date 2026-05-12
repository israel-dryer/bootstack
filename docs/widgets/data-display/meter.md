---
title: Meter
---

# Meter

`Meter` displays a **single numeric value within a range** as a circular or arc-style gauge.

It's ideal for dashboards, summaries, and status panels where visual emphasis matters more than precision.

---

## Quick start

```python
import bootstack as bs

app = bs.App()

meter = bs.Meter(app, value=65, maxvalue=100)
meter.pack(padx=20, pady=20)

app.mainloop()
```

---

## When to use

Use Meter when:

- showing a snapshot or status value
- visual emphasis is important
- you need a dashboard-style indicator

### Consider a different control when...

- you are tracking task progress over time — use [Progressbar](progressbar.md)
- you are showing capacity or fullness levels — use [FloodGauge](floodgauge.md)
- you need a compact text-based indicator — use [Badge](badge.md)

---

## Appearance

### `accent`

```python
bs.Meter(app, accent="success")
bs.Meter(app, accent="danger")
bs.Meter(app, accent="info")
```

### Size and shape

```python
# Size in pixels (width and height)
bs.Meter(app, value=75, size=150)

# Arc thickness
bs.Meter(app, value=75, thickness=20)

# Semicircle style
bs.Meter(app, value=75, meter_type="semi")

# Segmented style
bs.Meter(app, value=75, segment_width=10)
```

!!! link "See [Design System](../../design-system/index.md) for color tokens and theming guidelines."

---

## Examples & patterns

### Common options

| Option | Purpose |
|---|---|
| `value` | Current meter value |
| `minvalue` | Minimum value (default `0`) |
| `maxvalue` | Maximum value (default `100`) |
| `subtitle` | Label displayed below the value |
| `meter_type` | `"full"` (default) or `"semi"` for a semicircle |
| `value_format` | Format string for the center number (default `"{:.0f}"`) |
| `value_prefix` | Text before the value (e.g. `"$"`) |
| `value_suffix` | Text after the value (e.g. `"%"`, `"mph"`) |
| `size` | Pixel dimensions of the widget (default `200`) |
| `thickness` | Arc width in pixels (default `10`) |
| `segment_width` | Segment gap for a segmented style (default `0` = solid) |
| `interactive` | Allow mouse drag to adjust value (default `False`) |
| `dtype` | `int` (default) or `float` for the internal variable |

### Value model

```python
meter = bs.Meter(app, value=75, maxvalue=100, subtitle="CPU Usage")
meter.pack()

# Read and write
print(meter.value)     # 75
meter.value = 80
meter.get()            # equivalent to meter.value
meter.set(90)          # equivalent to meter.value = 90

# Increment/decrement
meter.step(5)          # +5
meter.step(-10)        # -10
```

### Prefix / suffix

```python
bs.Meter(app, value=1234, maxvalue=5000,
         value_prefix="$", subtitle="Revenue").pack()

bs.Meter(app, value=42, maxvalue=100,
         value_suffix="%", subtitle="Disk used").pack()
```

### Value formatting

```python
# 1 decimal place
bs.Meter(app, value=87.5, value_format="{:.1f}")

# Integer (default)
bs.Meter(app, value=87.5, value_format="{:.0f}")
```

### Range customization

```python
bs.Meter(app, value=23, minvalue=0, maxvalue=50,
         subtitle="Temperature", value_suffix="°C")
```

### Interactive meter

```python
# User can drag to adjust value
meter = bs.Meter(app, value=50, interactive=True)
meter.on_changed(lambda e: print("value:", meter.value))
```

### Reacting to changes

```python
def on_update(event):
    # event.data = {'value': ..., 'prev_value': ...}
    print("changed to:", event.data["value"])

bind_id = meter.on_changed(on_update)
meter.off_changed(bind_id)
```

---

## Behavior

- The arc fills proportionally from `minvalue` to `maxvalue`
- `meter_type="semi"` renders a 270° arc instead of a full circle
- `interactive=True` enables mouse click and drag to change value
- Updates occur immediately when `value` is changed programmatically

---

## Additional resources

### Related widgets

- [Progressbar](progressbar.md) — linear progress indicators
- [FloodGauge](floodgauge.md) — capacity/level indicators
- [Badge](badge.md) — compact status indicators

### Framework concepts

- [Design System](../../design-system/index.md) — colors, typography, and theming

### API reference

- [`bootstack.Meter`](../../reference/widgets/Meter.md)