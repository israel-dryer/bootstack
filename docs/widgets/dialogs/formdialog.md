---
title: FormDialog
---

# FormDialog

`FormDialog` is a **modal dialog** that collects multiple related values using a structured form layout.

Use it when a workflow needs a small set of inputs (2-8 fields) with an explicit OK/Cancel outcome.

---

## Quick start

```python
import bootstack as bs

app = bs.App()

dlg = bs.FormDialog(
    title="New connection",
    data={"port": 5432},
    items=[
        {"key": "host", "label": "Host",
         "editor": "textentry", "editor_options": {"required": True}},
        {"key": "port", "label": "Port", "editor": "numericentry"},
        {"key": "user", "label": "User", "editor": "textentry"},
    ],
)
dlg.show()

print("result:", dlg.result)  # dict on accept, None on cancel
app.mainloop()
```

---

## When to use

Use `FormDialog` when:

- you need several inputs at once

- the user should commit/cancel explicitly

- the inputs are part of a single small task

### Consider a different control when...

- you only need one value - use [QueryBox](querybox.md) instead

- the flow is multi-step or requires navigation - use [PageStack](../views/pagestack.md) instead

---

## Examples & patterns

### Common options

- `title` - dialog title

- `items` - form field definitions (FieldItem/GroupItem/TabsItem mappings)

- `data` - initial values keyed by field name

- `col_count` - number of columns in the form layout (default 1)

- `buttons` - footer buttons (DialogButton, mapping, or string)

### Value model

`FormDialog.show()` returns `None` and populates `dlg.result` once the
dialog closes:

- a dict mapping field keys to committed values when the user accepts, or

- `None` when cancelled

### Events

Most form dialogs are handled via return value.
If your dialog emits validation lifecycle events, use them for UX only (messages/state), not as the primary result.

### Validation and constraints

Use field-level validation:

- required fields

- type parsing (int/float/date)

- cross-field rules (password confirmation, ranges)

For complex "live" forms, prefer an inline [Form](../forms/form.md) in a normal window or a [PageStack](../views/pagestack.md) flow.

---

## Behavior

- OK commits and closes

- Cancel closes without committing

- Escape cancels (typical)

- Enter may submit the form (implementation-dependent)

---

## Additional resources

### Related widgets

- [Dialog](dialog.md) - base dialog API

- [QueryBox](querybox.md) - single-value prompts

- [QueryDialog](querydialog.md) - alternative query dialog

- [Form](../forms/form.md) - inline multi-field form layouts

- [PageStack](../views/pagestack.md) - multi-step workflows

### Framework concepts

- [Forms & Input](../../guides/forms-and-input.md) — picking input widgets and end-to-end form patterns

### API reference

- [`bootstack.FormDialog`](../../reference/dialogs/FormDialog.md)