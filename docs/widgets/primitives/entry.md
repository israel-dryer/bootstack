---
title: Entry
---

# Entry

`Entry` is the low-level, single-line text input primitive in bootstack.

It wraps `bs.Entry` and integrates bootstack styling plus reactive text support. `Entry` is also the building block
used by higher-level controls like `TextEntry`, `NumericEntry`, `DateEntry`, and `PasswordEntry`.

---

## Quick start

```python
import bootstack as bs

app = bs.App()

entry = bs.Entry(app)
entry.pack(padx=20, pady=20)

app.mainloop()
```

---

## When to use

Use `Entry` when:

- you need direct, low-level access to `bs.Entry` options

- you are building your own composite control

- you want Tk's `validate` / `validatecommand` behavior

### Consider a different control when...

- **you want labels, helper text, and standardized events** - prefer [TextEntry](../inputs/textentry.md)

- **you want commit-based validation with messages** - prefer [TextEntry](../inputs/textentry.md)

- **you are building application forms** - prefer [TextEntry](../inputs/textentry.md) or specialized input controls

---

## Appearance

### `accent` / `style`

Use semantic tokens via `accent`, or provide a concrete ttk style via `style=`.

```python
bs.Entry(app, accent="primary")
bs.Entry(app, accent="secondary")
```

!!! link "Design System"
    See the [Design System](../../design-system/index.md) for available color tokens.

---

## Examples and patterns

### Value model

`Entry` works with **raw text**:

- `entry.get()` returns the current string

- `textvariable=` or `textsignal=` keeps the text synchronized with your state

Unlike field controls such as `TextEntry`, `Entry` does not define "text vs committed value" semantics on its own.

### `textvariable`

Bind to a Tk variable.

```python
name = bs.StringVar(value="Ada")
bs.Entry(app, textvariable=name).pack()
```

### `textsignal`

Bind to a reactive signal (no Tk variable needed).

```python
entry = bs.Entry(app, textsignal=my_signal)
```

### `show`

Mask input characters (useful for basic password-style entry).

```python
bs.Entry(app, show="*")
```

!!! note "Password input"
    For a full-featured password field (reveal toggle, validation, messages), prefer [PasswordEntry](../inputs/passwordentry.md).

### Tk validation (`validate` / `validatecommand`)

Use Tk's validation when you need per-keystroke constraints.

```python
def validate_text(new_value: str) -> bool:
    return new_value.isdigit() or new_value == ""

vcmd = (app.register(validate_text), "%P")

entry = bs.Entry(app, validate="key", validatecommand=vcmd)
entry.pack(padx=20, pady=20)
```

!!! tip "Prefer field controls for forms"
    For most form UX, prefer [TextEntry](../inputs/textentry.md) (commit-time parsing + validation messages + consistent events).

---

## Behavior

`Entry` follows standard Tk/ttk behavior:

- keyboard focus and caret navigation

- standard widget states (`normal`, `readonly`, `disabled`)

- standard Tk events like `<KeyRelease>` and `<FocusOut>`

```python
entry.bind("<KeyRelease>", lambda e: print(entry.get()))
```

### Events

`Entry` emits standard Tk events, not structured v2 field events.

If you want standardized field events like `on_input` / `on_changed`, use [TextEntry](../inputs/textentry.md).

### Validation and constraints

Use `Entry` validation when you need low-level, immediate constraints while typing.

If you want user-friendly validation messages and commit-based validation, prefer [TextEntry](../inputs/textentry.md) (or a specialized `*Entry` control).

---

## Additional resources

### Related widgets

- [TextEntry](../inputs/textentry.md) - form-ready text control with labels, messages, and events

- [PasswordEntry](../inputs/passwordentry.md) - specialized masked input control

- [NumericEntry](../inputs/numericentry.md) - numeric input with bounds and stepping

- [DateEntry](../inputs/dateentry.md) / [TimeEntry](../inputs/timeentry.md) - structured date/time inputs

- [Combobox](combobox.md) - selection with optional text entry

### Framework concepts

- [Design System](../../design-system/index.md)

- [Events and Signals](../../guides/reactivity.md)

- [Localization](../../guides/localization.md)

### API reference

- [`bootstack.Entry`](../../reference/widgets/Entry.md)