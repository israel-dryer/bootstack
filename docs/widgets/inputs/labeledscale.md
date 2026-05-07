---
title: LabeledScale
---

# LabeledScale

`LabeledScale` is a **horizontal scale widget** with a label that displays and tracks the current value.

Use `LabeledScale` when users need visual feedback of the exact value as they drag — common for volume controls,
opacity settings, or any numeric range where precision matters.

---

## Quick start

```python
import bootstack as bs

app = bs.App()

scale = bs.LabeledScale(
    app,
    value=50,
    minvalue=0,
    maxvalue=100,
)
scale.pack(padx=20, pady=20, fill="x")

app.mainloop()
```

---

## When to use

Use `LabeledScale` when:

- users need to see the exact value while dragging
- you want a compact slider with built-in value display
- the value label should track the slider handle position

### Consider a different control when...

- you don't need a tracking label — use [Scale](scale.md)
- you need numeric entry with increment buttons — use [SpinnerEntry](spinnerentry.md)
- you need precise typed input — use [NumericEntry](numericentry.md)

---

## Appearance

### `compound`

Label position relative to the scale:

- `"before"` (default) — label above the scale
- `"after"` — label below the scale

```python
bs.LabeledScale(app, compound="after")
```

### `accent`

```python
bs.LabeledScale(app, accent="success")
bs.LabeledScale(app, accent="primary")
```

!!! link "See [Design System](../../design-system/index.md) for customization options."

---

## Examples and patterns

### `minvalue` / `maxvalue`

Range defaults to 0–100.

```python
bs.LabeledScale(app, minvalue=0, maxvalue=255)    # RGB range
bs.LabeledScale(app, minvalue=-50, maxvalue=50)   # centered range
```

### `value`

Initial value. Defaults to 0.

```python
bs.LabeledScale(app, value=50, minvalue=0, maxvalue=100)
```

### `dtype`

Data type for the value: `int` (default) or `float`.

```python
bs.LabeledScale(app, dtype=float, minvalue=0.0, maxvalue=1.0)
```

!!! note "`dtype` cannot be changed after construction"
    Setting `dtype` via `configure()` after the widget is created raises a `ConfigurationWarning` and has no effect. Set it at construction time.

### Range aliases: `from_` / `to`

`from_=` and `to=` are accepted as aliases for `minvalue` and `maxvalue`:

```python
bs.LabeledScale(app, from_=0, to=100)
```

### Value access

```python
current = scale.value   # get
scale.value = 75        # set
```

### Reacting to changes: `variable=`

Bind a `tkinter.Variable` to observe changes:

```python
var = bs.IntVar(value=50)
scale = bs.LabeledScale(app, variable=var, minvalue=0, maxvalue=100)

var.trace_add("write", lambda *_: print("value:", var.get()))
```

!!! note "`signal=` is not supported on `LabeledScale`"
    Passing `signal=` to `LabeledScale` has no effect — the kwarg is absorbed by the outer frame and never reaches the inner scale. Use `variable=` with a `tkinter.Variable` for external observation.

---

## Behavior

- The label automatically updates to show the current value.
- The label position tracks the slider handle as it moves.
- Only horizontal orientation is supported.
- If a value outside the configured range is set, the widget reverts to the last valid value (it does not clamp to the boundary).

!!! note "`padding` is fixed"
    The outer frame padding is set to `2` internally and cannot be overridden via `padding=`. Use the parent container for layout spacing instead.

---

## Additional resources

### Related widgets

- [Scale](scale.md) — scale without tracking label
- [SpinnerEntry](spinnerentry.md) — numeric input with increment/decrement buttons
- [NumericEntry](numericentry.md) — numeric input field with validation

### API reference

- [`bootstack.LabeledScale`](../../reference/widgets/LabeledScale.md)