---
title: Localization
---

# Localization

This guide shows how to make bootstack applications language-aware with message catalogs and locale-aware formatting.

---

## Why Localize?

Localization makes applications usable worldwide:

- **Text** adapts to the user's language
- **Dates and numbers** follow regional conventions
- **UI** can adapt to RTL languages

bootstack treats localization as a framework-level concern, not widget-by-widget configuration.

---

## Quick Start

A localized application:

```python
import bootstack as bs

app = bs.App(locale="es")

# Use message keys instead of literal text
bs.Label(app, text="greeting.hello").pack(pady=20)
bs.Button(app, text="actions.save").pack(pady=10)

app.mainloop()
```

With a Spanish message catalog, `"greeting.hello"` resolves to `"Hola"` and `"actions.save"` to `"Guardar"`.

---

## Message Catalogs

Message catalogs map **message keys** to **translated text**.

### Catalog Structure

Organize translations by language:

```
locales/
├── en.json
├── es.json
├── fr.json
└── de.json
```

Each file contains key-value pairs:

```json
{
    "greeting.hello": "Hello",
    "greeting.welcome": "Welcome, {name}!",
    "actions.save": "Save",
    "actions.cancel": "Cancel",
    "status.ready": "Ready"
}
```

### Loading Catalogs

```python
import bootstack as bs
from bootstack import MessageCatalog

# Load catalog from file
MessageCatalog.load("locales/en.json")
MessageCatalog.load("locales/es.json")

app = bs.App(locale="en")
```

### Using Message Keys

Widgets automatically resolve message keys:

```python
# If "greeting.hello" exists in catalog, it's resolved
# If not, the literal string is displayed
bs.Label(app, text="greeting.hello")
```

This behavior uses `localize="auto"` (the default):

```python
# Auto: resolve if key exists, otherwise use literal
bs.Label(app, text="greeting.hello")  # localize="auto"

# Force localization (error if key missing)
bs.Label(app, text="greeting.hello", localize=True)

# Disable localization (always literal)
bs.Label(app, text="Hello, World!", localize=False)
```

---

## Message Substitution

Messages can include placeholders:

```json
{
    "greeting.welcome": "Welcome, {name}!",
    "items.count": "{count} items"
}
```

Resolve with values:

```python
from bootstack import L

# L() resolves messages with substitution
text = L("greeting.welcome", name="Alice")  # "Welcome, Alice!"
text = L("items.count", count=5)  # "5 items"
```

For reactive updates with signals:

```python
from bootstack import LV

name = bs.Signal("Guest")

# LV() returns a signal that updates when inputs change
greeting = LV("greeting.welcome", name=name)

label = bs.Label(app, textvariable=greeting)
```

When `name` changes, `greeting` updates automatically.

---

## Changing Language at Runtime

Switch languages without restarting:

```python
import bootstack as bs
from bootstack import set_locale, get_locale

app = bs.App(locale="en")

def switch_to_spanish():
    set_locale("es")

def switch_to_english():
    set_locale("en")

bs.Button(app, text="Español", command=switch_to_spanish).pack()
bs.Button(app, text="English", command=switch_to_english).pack()

# This label updates when locale changes
bs.Label(app, text="greeting.hello").pack(pady=20)

app.mainloop()
```

Localized widgets re-render when the locale changes.

---

## Date and Number Formatting

Localization extends beyond text to **how values are displayed**.

### Date Formatting

```python
from bootstack import IntlFormatter
from datetime import date

formatter = IntlFormatter(locale="de")

today = date.today()
formatted = formatter.format_date(today)  # "25.12.2024" (German format)
```

### Number Formatting

```python
formatter = IntlFormatter(locale="fr")

formatted = formatter.format_number(1234567.89)  # "1 234 567,89" (French format)
formatted = formatter.format_currency(99.99, "EUR")  # "99,99 €"
```

### In Widgets

Some widgets format values automatically based on locale:

```python
app = bs.App(locale="de")

# DateEntry displays dates in German format
bs.DateEntry(app).pack()

# NumericEntry uses locale decimal separator
bs.NumericEntry(app).pack()
```

---

## Patterns

### Language Selector

```python
import bootstack as bs
from bootstack import set_locale

app = bs.App(locale="en")

languages = [("English", "en"), ("Español", "es"), ("Français", "fr")]

selector = bs.OptionMenu(
    app,
    values=[name for name, _ in languages],
    command=lambda name: set_locale(
        next(code for n, code in languages if n == name)
    ),
)
selector.pack(pady=20)

app.mainloop()
```

### Localized Form

```python
import bootstack as bs

app = bs.App(locale="en")

form = bs.GridFrame(app, columns=["auto", 1], gap=10, padding=20)
form.pack(fill="both", expand=True)

# Labels use message keys
bs.Label(form, text="form.username").grid()
bs.Entry(form).grid(sticky="ew")

bs.Label(form, text="form.password").grid()
bs.Entry(form, show="*").grid(sticky="ew")

# Button uses message key
bs.Button(form, text="actions.login").grid(column=1, sticky="e")

app.mainloop()
```

### Dynamic Messages

```python
import bootstack as bs
from bootstack import LV

app = bs.App()

# Reactive count
count = bs.Signal(0)

# Message updates when count changes
status = LV("items.selected", count=count)

bs.Label(app, textvariable=status).pack(pady=20)

def add_item():
    count.set(count.get() + 1)

bs.Button(app, text="Add", command=add_item).pack()

app.mainloop()
```

---

## Best Practices

### Use Semantic Keys

```json
{
    "actions.save": "Save",
    "actions.cancel": "Cancel",
    "errors.required": "This field is required"
}
```

Not:

```json
{
    "save_button_text": "Save",
    "the_cancel_button": "Cancel"
}
```

### Keep Translations Complete

Ensure all languages have the same keys. Missing keys fall back to the key itself.

### Test RTL Languages

If supporting Arabic or Hebrew, test that layout flows correctly.

### Don't Concatenate

```python
# Bad: concatenation breaks translation
message = L("greeting.hello") + ", " + name

# Good: use placeholders
message = L("greeting.welcome", name=name)
```

---

## Summary

- Use **message keys** in widgets instead of literal text
- Load **message catalogs** for each supported language
- Use **`L()`** for static messages with substitution
- Use **`LV()`** for reactive messages bound to signals
- Use **`IntlFormatter`** for locale-aware date/number formatting
- Change language at runtime with **`set_locale()`**

---

## Next Steps

- [App Structure](app-structure.md) — how applications are organized
- [Reactivity](reactivity.md) — signals and reactive updates
- [Color & Theming](color-and-theming.md) — working with the design system
