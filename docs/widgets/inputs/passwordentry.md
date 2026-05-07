---
title: PasswordEntry
---

# PasswordEntry

`PasswordEntry` is a secure, form-ready text input control for passwords and other sensitive values.

It builds on `TextEntry`, adding masking, an optional reveal toggle, and password-specific validation patterns — while
preserving the same label/message, localization, and event model used throughout bootstack.

---

## Quick start

```python
import bootstack as bs

app = bs.App()

pwd = bs.PasswordEntry(
    app,
    label="Password",
    required=True,
    message="Must be at least 8 characters",
)
pwd.pack(fill="x", padx=20, pady=10)

app.mainloop()
```

---

## When to use

Use `PasswordEntry` when:

- the input should not be displayed in clear text
- you want consistent form UX (label/message/validation/events)

Consider a different control when:

- masking is not required — use [TextEntry](textentry.md)
- the input is a numeric PIN — use [TextEntry](textentry.md) with a `pattern` validation rule (PINs are strings where leading zeros matter, not numbers)

---

## Appearance

### `accent`

```python
bs.PasswordEntry(app, label="Password")                    # primary (default)
bs.PasswordEntry(app, label="Password", accent="secondary")
```

Use `density='compact'` for dense layouts:

```python
bs.PasswordEntry(app, label="Password", density="compact")
```

!!! link "See [Design System](../../design-system/index.md) for a complete list of available colors and styling options."

---

## Examples and patterns

### Value model

| Concept | Meaning |
|---|---|
| Text | Masked display text |
| Value | Actual committed password value |

```python
secret = pwd.value   # committed value
raw = pwd.get()      # raw internal text
```

The reveal toggle changes only the display, never the underlying value.

### Common options

#### `required`, `message`, `show`

```python
bs.PasswordEntry(app, label="Password", required=True, message="Minimum 8 characters")

# Custom mask character (default is '•')
bs.PasswordEntry(app, label="PIN", show="*")
```

#### Reveal toggle: `show_visibility_toggle`

```python
pwd = bs.PasswordEntry(app, label="Password", show_visibility_toggle=False)
```

#### `state`

```python
pwd = bs.PasswordEntry(app, label="Password", state="disabled")

pwd.disable()       # prevent input
pwd.enable()        # restore input
pwd.readonly(True)  # allow reading, block editing
```

#### Add-ons

```python
pwd.insert_addon(bs.Label, position="before", icon="lock", icon_only=True)
```

!!! link "See [TextEntry — Add-ons](textentry.md#add-ons) for the full add-on API."

### Events

**Change events** — callback receives a Tkinter event object:

```python
def on_change(event):
    print("password updated:", event.data["value"])

pwd.on_input(on_change)    # <<Input>>  — fires on each keystroke
pwd.on_changed(on_change)  # <<Change>> — fires on commit
```

**Validation events** — callback receives a plain dict:

```python
def on_result(data):
    print("valid:", data["is_valid"], "message:", data["message"])

pwd.on_valid(on_result)      # <<Valid>>
pwd.on_invalid(on_result)    # <<Invalid>>
pwd.on_validated(on_result)  # <<Validate>> — fires after any validation
```

Use `on_enter` to handle the Return key directly (useful for single-field login forms):

```python
pwd.on_enter(lambda event: submit())
```

All `on_*` methods return a bind ID for unsubscribing:

```python
bid = pwd.on_changed(on_change)
pwd.off_changed(bid)
```

### Validation

Password validation is applied **on commit**, not per keystroke.

```python
pwd = bs.PasswordEntry(app, label="Password", required=True)
pwd.add_validation_rule("stringLength", min=8, message="Minimum 8 characters")
```

Common patterns:

```python
# Minimum length
pwd.add_validation_rule("stringLength", min=8, message="At least 8 characters")

# Character class (regex)
pwd.add_validation_rule("pattern",
    pattern=r"^(?=.*[A-Z])(?=.*\d).+$",
    message="Must contain a capital letter and a number")

# Confirmation match (cross-field)
pwd.add_validation_rule("compare",
    other_field=confirm_pwd,
    message="Passwords do not match")
```

---

## Behavior

- Characters are masked while typing (default mask character: `'•'`).
- A reveal button is shown by default (`show_visibility_toggle=True`).
- Commit semantics match other field controls (blur or Enter).

---

## Localization

Labels, messages, and validation feedback can be localized. Any string passed as `label=` or `message=` is used as a gettext key when localization is active.

!!! link "See [Localization](../../guides/localization.md) for setup and language switching."

---

## Reactivity

```python
password = bs.Signal("")
entry = bs.PasswordEntry(app, label="Password", textsignal=password)
```

!!! link "See [Reactivity](../../guides/reactivity.md) for signal patterns and data binding."

---

## Additional resources

### Related widgets

- [TextEntry](textentry.md) — general text field
- [NumericEntry](numericentry.md) — numeric input with validation
- [Form](../forms/form.md) — structured field layout and submission

### Framework concepts

- [Localization](../../guides/localization.md) — internationalization and formatting
- [Reactivity](../../guides/reactivity.md) — reactive data binding

### API reference

- [`bootstack.PasswordEntry`](../../reference/widgets/PasswordEntry.md)