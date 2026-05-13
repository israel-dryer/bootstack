---
title: PasswordEntry
---

# PasswordEntry

`PasswordEntry` is a password input field with character masking and a built-in visibility toggle.

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

<div class="app-window">
    <img src="../../assets/widgets-password-quickstart.png" alt="PasswordEntry quickstart"/>
</div>

## When to use

Use `PasswordEntry` when:

- the input should not be displayed in clear text
- you want consistent form UX (label, message, validation, events)

### Consider a different control when...

- masking is not required — use [TextEntry](textentry.md)
- the input is a numeric PIN — use [TextEntry](textentry.md) with a `"pattern"` validation rule (PINs are strings where leading zeros matter, not numbers)

## Common options

| Option | Purpose |
|---|---|
| `label` | Text label rendered above the field. |
| `message` | Helper text rendered below the field. Replaced by validation errors on failure. |
| `required` | Marks the field required; adds `*` to the label. |
| `show` | Character used to mask input. Default `'•'`. |
| `show_visibility_toggle` | Show the reveal button. Default `True`. |
| `accent` | Accent token for the focus ring and active border. |
| `density` | `"default"` or `"compact"`. |
| `width` | Width in characters. |

## Value model

| Concept | Meaning |
|---|---|
| Text | Masked display text |
| Value | Actual committed password value |

```python
secret = pwd.value   # committed value
raw = pwd.get()      # raw internal text
```

The reveal toggle changes only the display, never the underlying value.

## Visibility toggle

A reveal button (eye icon) is shown by default. The password is visible only while the button is actively pressed — it masks again on release.

```python
# Disable at construction
pwd = bs.PasswordEntry(app, label="Password", show_visibility_toggle=False)

# Change at runtime
pwd.configure(show_visibility_toggle=True)
```

## State

```python
pwd = bs.PasswordEntry(app, label="Password", state="disabled")

pwd.disable()         # prevent input
pwd.enable()          # restore input
pwd.readonly(True)    # allow reading, block editing
```

## Add-ons

`PasswordEntry` supports the same `insert_addon()` API as `TextEntry`. The internal reveal button is already placed as an add-on named `"visibility"` at position `"after"`.

```python
pwd.insert_addon(bs.Label, position="before", icon="lock")
```

!!! link "See [TextEntry add-ons](textentry.md#add-ons) for the full API."

## Events

| Event | Fires when |
|---|---|
| `<<Input>>` | Each keystroke |
| `<<Change>>` | Value committed (blur or Enter) |
| `<<Valid>>` | Validation passed |
| `<<Invalid>>` | Validation failed |
| `<<Validate>>` | After any validation attempt |

Register with `on_*` / `off_*` convenience methods. The two groups have different callback shapes:

**Change events** (`<<Input>>`, `<<Change>>`) — callback receives a Tkinter event object:

```python
def on_change(event):
    event.data["value"]       # committed value
    event.data["prev_value"]  # previous value
    event.data["text"]        # raw display string

pwd.on_changed(on_change)   # <<Change>>
pwd.on_input(on_change)     # <<Input>>
```

**Validation events** (`<<Valid>>`, `<<Invalid>>`, `<<Validate>>`) — callback receives a plain dict:

```python
def on_result(data):
    data["is_valid"]   # bool
    data["value"]      # committed value
    data["message"]    # validation message

pwd.on_validated(on_result)  # <<Validate>>
pwd.on_valid(on_result)      # <<Valid>>
pwd.on_invalid(on_result)    # <<Invalid>>
```

Use `on_enter` to handle the Return key directly (useful for single-field login forms):

```python
pwd.on_enter(lambda event: submit())
```

## Validation

Validation applies on commit, not per keystroke.

```python
pwd = bs.PasswordEntry(app, label="Password", required=True)

# Minimum length
pwd.add_validation_rule("stringLength", min=8, message="Minimum 8 characters")

# Character class (regex)
pwd.add_validation_rule(
    "pattern",
    pattern=r"^(?=.*[A-Z])(?=.*\d).+$",
    message="Must contain a capital letter and a number",
)

# Confirmation match (cross-field)
pwd.add_validation_rule(
    "compare",
    other_field=confirm_pwd,
    message="Passwords do not match",
)
```

!!! link "See [Forms & Input](../../guides/forms-and-input.md) for validation patterns, triggers, and cross-field rules."

## Reactivity

```python
password = bs.Signal("")

entry = bs.PasswordEntry(app, label="Password", textsignal=password)
```

!!! link "See [Reactivity](../../guides/reactivity.md) for signal patterns."

## Localization

Any string passed as `label=` or `message=` is used as a gettext key when localization is active.

!!! link "See [Localization](../../guides/localization.md) for setup and language switching."

## See also

- [TextEntry](textentry.md) — general text input field
- [NumericEntry](numericentry.md) — numeric input with validation
- [Form](../forms/form.md) — structured field layout and submission
- [Forms & Input guide](../../guides/forms-and-input.md)

--8<-- "snippets/api/passwordentry.md"