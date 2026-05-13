---
title: TextEntry
---

# TextEntry

`TextEntry` is a form-ready text input field with a label, input, and message area.

```python
import bootstack as bs

app = bs.App()

name = bs.TextEntry(
    app,
    label="Name",
    message="Enter your full name",
    required=True,
)
name.pack(fill="x", padx=20, pady=10)

app.mainloop()
```

<div class="app-window">
    <img src="../../assets/widgets-textentry-quickstart.png" alt="TextEntry quickstart"/>
</div>

## When to use

Use `TextEntry` when:

- you want a form-ready text field with label, message area, and validation
- you want consistent events and commit semantics
- you want optional localization and formatting

### Consider a different control when...

- you need the lowest-level text input without field chrome — use [Entry](../primitives/entry.md)
- you are building a custom composite control — use [Entry](../primitives/entry.md)

## Common options

| Option | Purpose |
|---|---|
| `label` | Text label rendered above the field. |
| `message` | Helper text rendered below the field. Auto-shown when set. Replaced by validation errors on failure. |
| `required` | Marks the field required; adds `*` to the label and a `"required"` validation rule. |
| `accent` | Accent token for the focus ring and active border. |
| `density` | `"default"` or `"compact"`. |
| `allow_blank` | If `False`, empty input restores the previous value on commit. Default `True`. |
| `width` | Width in characters. |
| `font` | Font token for the input text. |
| `justify` | Text alignment: `"left"`, `"center"`, or `"right"`. |
| `show_message` | Show the message area even without `message=` or `required=` set. |
| `initial_focus` | Give the field focus on creation. |

## Value model

Entry-based fields separate what the user is typing from the committed value.

| Concept | Meaning |
|---|---|
| Text | Raw, editable string while the field is active |
| Value | Committed value after parsing and validation on blur or Enter |

```python
current = name.value        # committed value
raw = name.get()            # raw text at any time

name.value = "Ada Lovelace"
```

## Value format

Use `value_format=` to parse and display the committed value. Formatting applies on blur or Enter — never on each keystroke.

```python
# Named presets
bs.TextEntry(app, label="Amount",  value=1234.56,         value_format="currency")
bs.TextEntry(app, label="Date",    value="March 14 1981", value_format="shortDate")
bs.TextEntry(app, label="Percent", value=0.42,            value_format="percent")

# Precision control via dict
bs.TextEntry(app, label="Rate", value=0.0875,
             value_format={"type": "percent", "precision": 1})

# Custom ICU pattern
bs.TextEntry(app, label="Code", value_format="000-000")
```

<div class="app-window">
    <img src="../../assets/widgets-textentry-format.png" alt="TextEntry with value_format"/>
</div>

!!! link "See [Formatting](../../guides/formatting.md) for all number, date, and time presets, dict options, and custom pattern syntax."

## State

```python
entry = bs.TextEntry(app, label="Notes", state="disabled")

entry.disable()         # prevent input
entry.enable()          # restore input
entry.readonly(True)    # allow reading, block editing
```

## Add-ons

`insert_addon` places a widget inside the field container, to the left (`"before"`) or right (`"after"`) of the input. Add-ons share the field's focus ring and disabled state.

```python
# Icon prefix
email = bs.TextEntry(app, label="Email")
email.insert_addon(bs.Label, position="before", icon="envelope")

# Action suffix
search = bs.TextEntry(app)
search.insert_addon(bs.Button, position="after", icon="search", command=handle_search)
```

<div class="app-window">
    <img src="../../assets/widgets-textentry-addons.png" alt="TextEntry add-ons"/>
</div>

Use `name=` to retrieve the add-on later via `entry.addons`:

```python
search.insert_addon(
    bs.Button,
    position="after",
    icon="search",
    command=on_search,
    name="search-btn",
)

search.addons["search-btn"].configure(icon="x")
```

Without `name=`, the key is the widget's string representation — not stable enough to rely on.

Add-ons automatically disable and re-enable with the field:

```python
search.disable()   # entry and search-btn both become disabled
search.enable()    # both restored
```

Use `bs.CheckToggle` as a toggle add-on. Pass `signal=` to link it to a reactive boolean:

```python
case_sensitive = bs.Signal(True)

search.insert_addon(
    bs.CheckToggle,
    position="after",
    text="Aa",
    name="case-btn",
    signal=case_sensitive,
    command=lambda: print("Toggled:", case_sensitive.get()),
)
```

<div class="app-window">
    <img src="../../assets/widgets-textentry-checktoggle.png" alt="TextEntry toggle add-on"/>
</div>

Use `pack_options=` to pass spacing arguments to the add-on's `pack()` call:

```python
entry.insert_addon(
    bs.Label,
    position="before",
    text="$",
    pack_options={"padx": (6, 2)},
)
```

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

name.on_changed(on_change)   # <<Change>>
name.on_input(on_change)     # <<Input>>
```

**Validation events** (`<<Valid>>`, `<<Invalid>>`, `<<Validate>>`) — callback receives a plain dict:

```python
def on_result(data):
    data["is_valid"]   # bool
    data["value"]      # committed value
    data["message"]    # validation message

name.on_validated(on_result)  # <<Validate>>
name.on_valid(on_result)      # <<Valid>>
name.on_invalid(on_result)    # <<Invalid>>
```

## Validation

```python
email = bs.TextEntry(app, label="Email", required=True)
email.add_validation_rule("email", message="Enter a valid email address")
```

Available rule types: `"required"`, `"email"`, `"pattern"`, `"stringLength"`, `"compare"`, `"custom"`.

```python
# Pattern rule
phone.add_validation_rule(
    "pattern",
    pattern=r"^\d{3}-\d{4}$",
    message="Format: 555-1234",
)

# Length rule
bio.add_validation_rule(
    "stringLength",
    min=10,
    max=500,
    message="10–500 characters",
)

# Custom rule
def check_username(value):
    return value.isalnum(), "Letters and numbers only"

username.add_validation_rule("custom", func=check_username)
```

!!! link "See [Forms & Input](../../guides/forms-and-input.md) for validation patterns, triggers, and cross-field rules."

## Reactivity

```python
username = bs.Signal("")

entry = bs.TextEntry(app, label="Username", textsignal=username)

print(username.get())
username.set("ada")

entry.signal.subscribe(lambda val: print("changed to:", val))
```

!!! link "See [Reactivity](../../guides/reactivity.md) for signal patterns and data binding."

## Localization

Any string passed as `label=`, `message=`, or `text=` is used as a gettext key when localization is active.

```python
bs.TextEntry(app, label="field.name", message="field.name.hint")
```

!!! link "See [Localization](../../guides/localization.md) for setup, domain configuration, and language switching."

## See also

- [Entry](../primitives/entry.md) — low-level primitive text input
- [PasswordEntry](passwordentry.md) — obscured text input
- [NumericEntry](numericentry.md) — numeric input with bounds and stepping
- [DateEntry](dateentry.md) — structured date input
- [Form](../forms/form.md) — build complete forms from field definitions
- [Forms & Input guide](../../guides/forms-and-input.md)
- [Formatting guide](../../guides/formatting.md)

--8<-- "snippets/api/textentry.md"