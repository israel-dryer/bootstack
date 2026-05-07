---
title: TimeEntry
---

# TimeEntry

`TimeEntry` is a form-ready input control for entering a **time of day**.

It combines a text field with a time dropdown, and supports the same label/message, validation, localization, and events
as other entry controls.

---

## Quick start

```python
import bootstack as bs

app = bs.App()

t = bs.TimeEntry(
    app,
    label="Start time",
    value="08:30",
)
t.pack(fill="x", padx=20, pady=10)

app.mainloop()
```

---

## When to use

Use `TimeEntry` when:

- users need to enter times (schedules, appointments, thresholds)
- you want consistent field behavior (label, message, validation, events)

Consider a different control when:

- the value is not semantically a time — use [TextEntry](textentry.md)
- users should step through time in fixed increments — use [SpinnerEntry](spinnerentry.md)

---

## Appearance

### `accent`

```python
bs.TimeEntry(app, label="Start time")                    # primary (default)
bs.TimeEntry(app, label="Start time", accent="secondary")
```

Use `density='compact'` for dense form layouts:

```python
bs.TimeEntry(app, label="Time", density="compact")
```

!!! link "See [Design System](../../design-system/index.md) for a complete list of available colors and styling options."

---

## Examples and patterns

### Value model

`TimeEntry` separates **typed text** from the **committed time value**.

```python
current = t.value   # committed time value
raw = t.get()       # raw text
```

On commit (blur or Enter), the value is parsed and normalized. If parsing fails, the value is unchanged and validation feedback is emitted.

### Common options

#### `value`

!!! note "Default is current time"
    If `value` is not provided, `TimeEntry` pre-fills with the current wall-clock time. Pass `value=""` or an explicit time string to start with a known value.

```python
bs.TimeEntry(app, label="Alarm", value="07:00")
```

#### Dropdown options: `interval`, `min_time`, `max_time`

The dropdown shows time options at regular intervals. Customize to limit what appears:

```python
# 15-minute intervals from 9 AM to 5 PM
bs.TimeEntry(
    app,
    label="Appointment",
    interval=15,
    min_time="09:00",
    max_time="17:00",
)
```

`interval` defaults to 30 minutes. `min_time` and `max_time` default to midnight and 23:59.

#### Formatting: `value_format`

```python
bs.TimeEntry(app, label="Short Time", value_format="shortTime")  # "3:30 PM"
bs.TimeEntry(app, label="Long Time",  value_format="longTime")   # "3:30:45 PM PST"
bs.TimeEntry(app, label="24-Hour",    value_format="HH:mm")      # "15:30"
```

!!! link "See [Formatting](../../guides/formatting.md) for all time presets and custom patterns."

#### `state`

```python
t = bs.TimeEntry(app, label="Time", state="disabled")

t.disable()       # prevent input
t.enable()        # restore input
t.readonly(True)  # allow reading, block editing
```

### Events

**Change events** — callback receives a Tkinter event object:

```python
def on_change(event):
    print("time:", event.data["value"])

t.on_input(on_change)    # <<Input>>  — live typing
t.on_changed(on_change)  # <<Change>> — committed value
```

**Validation events** — callback receives a plain dict:

```python
def on_result(data):
    print("valid:", data["is_valid"])

t.on_valid(on_result)      # <<Valid>>
t.on_invalid(on_result)    # <<Invalid>>
t.on_validated(on_result)  # <<Validate>> — fires after any validation
```

### Validation

```python
t = bs.TimeEntry(app, label="End time", required=True)

t.add_validation_rule("custom",
    func=lambda v: (v >= start.value, "End must be after start"))
```

---

## Behavior

- Users type a time directly (`"8:30"`, `"08:30"`, `"8:30 PM"`) or select from the dropdown.
- Accepted formats: `HH:MM` and `HH:MM AM/PM`. Other formats may not parse correctly and will leave the value unchanged.
- Commit occurs on blur or Enter.
- Formatting is applied on commit.

---

## Reactivity

```python
alarm = bs.Signal("07:00")
entry = bs.TimeEntry(app, label="Alarm", textsignal=alarm)
```

!!! link "See [Reactivity](../../guides/reactivity.md) for signal patterns and data binding."

---

## Additional resources

### Related widgets

- [DateEntry](dateentry.md) — date input control
- [TextEntry](textentry.md) — general field control
- [SpinnerEntry](spinnerentry.md) — stepped input (useful for minute/hour increments)
- [Form](../forms/form.md) — build forms from field definitions

### Framework concepts

- [Formatting](../../guides/formatting.md) — time presets and custom patterns
- [Localization](../../guides/localization.md) — internationalization and formatting
- [Reactivity](../../guides/reactivity.md) — reactive data binding

### API reference

- [`bootstack.TimeEntry`](../../reference/widgets/TimeEntry.md)