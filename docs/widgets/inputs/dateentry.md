---
title: DateEntry
---

# DateEntry

`DateEntry` is a form-ready calendar date input that combines a text field with a picker popup.

It behaves like other entry controls (message, validation, localization, events), while making date entry fast and
consistent using a calendar picker when needed.

<figure markdown>
![dateentry states](../../assets/widgets-dateentry-states.png)
</figure>

---

## Quick start

```python
import bootstack as bs

app = bs.App()

due = bs.DateEntry(
    app,
    label="Due date",
    value="2025-12-31",
    message="Pick a date or type one",
)
due.pack(fill="x", padx=20, pady=10)

app.mainloop()
```

---

## When to use

Use `DateEntry` when:

- users need to enter calendar dates reliably
- you want both typing and a picker UI
- validation and formatting should be consistent with other field controls

Consider a different control when:

- you need time-of-day input — use [TimeEntry](timeentry.md)
- the value is "date-like" but not an actual calendar date — use [TextEntry](textentry.md)
- date selection should be modal (dialog-based) — use [DateDialog](../dialogs/datedialog.md)

---

## Appearance

### `accent`

```python
bs.DateEntry(app, label="Due date")                    # primary (default)
bs.DateEntry(app, label="Due date", accent="secondary")
bs.DateEntry(app, label="Due date", accent="success")
bs.DateEntry(app, label="Due date", accent="warning")
```

Use `density='compact'` for dense form layouts:

```python
bs.DateEntry(app, label="Date", density="compact")
```

!!! link "See [Design System](../../design-system/index.md) for a complete list of available colors and styling options."

---

## Examples and patterns

### Value model

| Concept | Meaning |
|---|---|
| Text | Raw, editable string while focused |
| Value | Parsed/validated date committed on blur, Enter, or picker selection |

```python
current = due.value   # committed date value
raw = due.get()       # raw text
```

!!! tip "Commit semantics"
    Parsing, validation, and `value_format` are applied when the value is committed
    (blur/Enter or picker selection), not while typing.

### Common options

#### Formatting: `value_format`

```python
bs.DateEntry(app, label="Short Date", value="2025-01-15", value_format="shortDate").pack()
bs.DateEntry(app, label="ISO Format", value="2025-01-15", value_format="yyyy-MM-dd").pack()
bs.DateEntry(app, label="Long Date",  value="2025-01-15", value_format="longDate").pack()
```

<figure markdown>
![dateentry formats](../../assets/widgets-dateentry-formats.png)
</figure>

!!! link "See [Formatting](../../guides/formatting.md) for all date presets and custom ICU patterns."

#### `state`

```python
due = bs.DateEntry(app, label="Due date", state="disabled")

due.disable()       # prevent input
due.enable()        # restore input
due.readonly(True)  # allow reading, block editing
```

#### Picker options

Use `show_picker_button=False` to hide the calendar button when only typed input is needed:

```python
bs.DateEntry(app, label="Date", show_picker_button=False)
```

Customise the picker dialog title and first weekday:

```python
bs.DateEntry(
    app,
    label="Start date",
    picker_title="Select a start date",
    picker_first_weekday=0,   # 0 = Monday, 6 = Sunday (default)
)
```

#### Add-ons

```python
d = bs.DateEntry(app, label="Birthday")
d.insert_addon(bs.Label, position="before", icon="cake-fill", name="icon")
```

<figure markdown>
![dateentry addons](../../assets/widgets-dateentry-addons.png)
</figure>

!!! link "See [TextEntry — Add-ons](textentry.md#add-ons) for the full add-on API."

### Events

**Change events** — callback receives a Tkinter event object:

```python
def on_change(event):
    print("date:", event.data["value"])

due.on_input(on_change)    # <<Input>>  — live typing
due.on_changed(on_change)  # <<Change>> — committed (blur, Enter, or picker)
```

**Validation events** — callback receives a plain dict:

```python
def on_result(data):
    print("valid:", data["is_valid"])

due.on_valid(on_result)      # <<Valid>>
due.on_invalid(on_result)    # <<Invalid>>
due.on_validated(on_result)  # <<Validate>> — fires after any validation
```

### Validation

```python
d = bs.DateEntry(app, label="Date", required=True)
```

Use `required=True` to add the required rule. Add custom rules for business logic:

```python
from datetime import date

d.add_validation_rule("custom",
    func=lambda v: (v >= date.today(), "Date must be today or in the future"))
```

---

## Behavior

### Picker behavior

- Click the calendar button — opens the picker
- Click a day — commits the date and closes the popup
- Escape — closes the popup without committing

<figure markdown>
![dateentry picker](../../assets/widgets-dateentry-popup.png)
</figure>

---

## Localization

`DateEntry` supports locale-aware date formatting. The `value_format` option controls display format; dates adapt automatically to locale conventions (date order, separators, month names).

Labels and messages are also localized when localization is active.

!!! link "See [Localization](../../guides/localization.md) for setup and language switching."

---

## Reactivity

```python
start = bs.Signal(None)
entry = bs.DateEntry(app, label="Start date", textsignal=start)
```

!!! link "See [Reactivity](../../guides/reactivity.md) for signal patterns and data binding."

---

## Additional resources

### Related widgets

- [TimeEntry](timeentry.md) — time input control
- [TextEntry](textentry.md) — general field control with validation and formatting
- [DateDialog](../dialogs/datedialog.md) — modal date selection
- [Calendar](../selection/calendar.md) — standalone calendar widget
- [Form](../forms/form.md) — build forms from field definitions

### Framework concepts

- [Formatting](../../guides/formatting.md) — date presets and custom patterns
- [Localization](../../guides/localization.md) — internationalization and formatting
- [Reactivity](../../guides/reactivity.md) — reactive data binding

### API reference

- [`bootstack.DateEntry`](../../reference/widgets/DateEntry.md)