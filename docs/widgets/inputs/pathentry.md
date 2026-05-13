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

- users need to select files or folders
- you want both typing and browsing in the same control
- you want consistent field UX (label, message, validation)

### Consider a different control when...

- the value is not a filesystem path — use [TextEntry](textentry.md)
- you need a one-off file selection with no persistent field — use a file dialog directly

## Common options

| Option | Purpose |
|---|---|
| `label` | Text label rendered above the field. |
| `message` | Helper text rendered below the field. |
| `required` | Marks the field required; adds `*` to the label. |
| `dialog` | Dialog type that opens on browse. Default `"openfilename"`. |
| `dialog_options` | Dict of options passed to the OS file dialog (`title`, `filetypes`, `initialdir`, etc.). |
| `button_text` | Text on the browse button. Default `"Browse"`. |
| `accent` | Accent token for the focus ring and active border. |
| `density` | `"default"` or `"compact"`. |
| `width` | Width in characters. |

## Value model

| Concept | Meaning |
|---|---|
| Text | Raw text while editing |
| Value | Committed path after validation or picker selection |

```python
current = path.value
raw = path.get()

path.value = r"C:\data\input.csv"
```

Picker selections commit immediately. The raw dialog result is available via `path.dialog_result`.

## Dialog type

```python
bs.PathEntry(app, dialog="openfilename")   # single file (default)
bs.PathEntry(app, dialog="directory")      # folder
bs.PathEntry(app, dialog="saveasfilename") # save-as path
bs.PathEntry(app, dialog="openfilenames")  # multiple files (returns list)
```

!!! note "`openfile` vs `openfilename`"
    `openfilename` returns a path string. `openfile` returns a file object. Use `openfilename` unless you specifically need a file handle.

The browse button opens the OS-native chooser (Windows Explorer, macOS Finder, or GTK on Linux). Its appearance is controlled by the OS, not bootstack's theme.

For multi-file selection (`"openfilenames"`), paths are joined with `", "` for display. The raw tuple is available via `path.dialog_result`.

Both `dialog` and `button_text` can be changed at runtime:

```python
path.configure(dialog="directory")
path.configure(button_text="Re-select...")
```

## File filters

Use `dialog_options=` to pass options to the OS dialog:

```python
bs.PathEntry(
    app,
    label="Document",
    dialog="openfilename",
    dialog_options={
        "filetypes": [("PDF", "*.pdf"), ("Word Document", "*.docx"), ("All files", "*.*")],
        "title": "Select a document",
    },
)
```

Common `dialog_options` keys: `title`, `initialdir`, `initialfile`, `filetypes`, `defaultextension`.

## State

```python
path = bs.PathEntry(app, label="File", state="disabled")

path.disable()         # prevent input and browsing
path.enable()          # restore
path.readonly(True)    # allow reading, block editing
```

## Add-ons

`PathEntry` supports the same `insert_addon()` API as `TextEntry`. The browse button is already placed as an add-on named `"dialog-button"` at position `"before"`.

```python
p = bs.PathEntry(app, label="File")
p.insert_addon(
    bs.Button,
    position="after",
    text="Clear",
    command=lambda: setattr(p, "value", ""),
    name="clear",
)
```

!!! link "See [TextEntry add-ons](textentry.md#add-ons) for the full API."

## Events

| Event | Fires when |
|---|---|
| `<<Input>>` | Each keystroke while typing |
| `<<Change>>` | Typed path committed, or picker selection made |
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

path.on_changed(on_change)   # <<Change>>
path.on_input(on_change)     # <<Input>>
```

**Validation events** (`<<Valid>>`, `<<Invalid>>`, `<<Validate>>`) — callback receives a plain dict:

```python
def on_result(data):
    data["is_valid"]   # bool
    data["value"]      # committed value
    data["message"]    # validation message

path.on_validated(on_result)  # <<Validate>>
path.on_valid(on_result)      # <<Valid>>
path.on_invalid(on_result)    # <<Invalid>>
```

`<<Change>>` fires from two sources. The picker source adds a `dialog_result` key:

```python
# Typed path committed — binds to inner entry
def on_typed(event):
    event.data["value"]       # committed path string
    event.data["prev_value"]  # previous path

path.on_changed(on_typed)

# Picker selection — fires on PathEntry composite; includes dialog_result
def on_picked(event):
    event.data["value"]         # display string (joined for multi-select)
    event.data["dialog_result"] # raw result; tuple for openfilenames

path.bind("<<Change>>", on_picked)
```

!!! note "`on_changed` and picker selections"
    `on_changed` binds to the inner entry and fires for typed commits only. To receive both typed and picker changes, use `path.bind("<<Change>>", callback)` directly on the `PathEntry` instance.

## Validation

Use `required=True` for required path fields. For existence and type checks, use a `"custom"` rule:

```python
import os

p = bs.PathEntry(app, label="Input file", required=True)

p.add_validation_rule("custom",
    func=os.path.isfile,
    message="File does not exist")

p.add_validation_rule("custom",
    func=lambda v: (v.endswith(".csv"), "Must be a CSV file"))
```

!!! link "See [Forms & Input](../../guides/forms-and-input.md) for validation patterns and triggers."

## Reactivity

```python
filepath = bs.Signal("")

entry = bs.PathEntry(app, label="Input file", textsignal=filepath)

filepath.subscribe(lambda v: print("path changed:", v))
```

!!! link "See [Reactivity](../../guides/reactivity.md) for signal patterns."

## Localization

Any string passed as `label=` or `message=` is used as a gettext key when localization is active.

!!! link "See [Localization](../../guides/localization.md) for setup and language switching."

## See also

- [TextEntry](textentry.md) — general-purpose text field
- [SelectBox](../selection/selectbox.md) — choose from a known list instead of browsing
- [Form](../forms/form.md) — build complete forms with path fields
- [Forms & Input guide](../../guides/forms-and-input.md)
- [Validation guide](../../guides/validation.md)

--8<-- "snippets/api/pathentry.md"