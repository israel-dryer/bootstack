---
title: PathEntry
---

# PathEntry

`PathEntry` is a file and folder input field that combines text entry with a browse button that opens a native OS file chooser.

```python
import bootstack as bs

app = bs.App()

path = bs.PathEntry(
    app,
    label="Input file",
    message="Select a CSV file to import",
)
path.pack(fill="x", padx=20, pady=10)

app.mainloop()
```

<div class="app-window">
    <img src="../../assets/widgets-pathentry-quickstart.png" alt="PathEntry quickstart"/>
</div>

## When to use

Use `PathEntry` when:

- users need to select files or folders from the filesystem
- you want both typing and browsing in the same control
- you want consistent field UX (label, message, validation)

### Consider a different control when...

- the value is not a filesystem path — use [TextEntry](textentry.md)
- you need a one-off file selection with no persistent field — use a file dialog directly

## See also

**Examples:** [File import form](../../examples/forms/file-import.md) · [Settings with paths](../../examples/forms/settings.md)  
**Guides:** [Forms & Input](../../guides/forms-and-input.md) · [Validation](../../guides/validation.md)  
**API reference:** [PathEntry](../../reference/widgets/pathentry.md)