---
title: DropdownButton
---

# DropdownButton

`DropdownButton` is a **button-first** control that opens a menu of related actions.
Use it when the primary interaction is still a button click, but you want a secondary list of choices available on demand.

---

## Quick start

Provide menu items as `ContextMenuItem` entries.

```python
import bootstack as bs

app = bs.App(title="Dropdown Example", minsize=(300, 200))

items = [
    bs.ContextMenuItem("command", text="Open",   command=lambda: print("Open")),
    bs.ContextMenuItem("command", text="Rename", command=lambda: print("Rename")),
    bs.ContextMenuItem("separator"),
    bs.ContextMenuItem("command", text="Delete", command=lambda: print("Delete")),
]

btn = bs.DropdownButton(app, text="File", items=items)
btn.pack(padx=20, pady=20)

app.mainloop()
```

<div class="app-window">
    <img src="../../assets/widgets-dropdown-quickstart.png" alt="Dropdown Button Quickstart"/>
</div>

---

## When to use

Use `DropdownButton` when:

- you have a **primary action** plus a small set of related actions
- you want the options to be **discoverable**, but not always visible
- the control belongs in a **toolbar** or dense header area

### Consider a different control when…

- you want a *single* action → use [Button](button.md)
- the control is primarily "a menu" (not a button) → use [MenuButton](menubutton.md)
- the menu must be shown on right-click / contextual interaction → use [ContextMenu](contextmenu.md)

---

## Appearance

`DropdownButton` supports semantic colors and variants through `accent` and `variant`.

!!! link "See [Design System → Variants](../../design-system/variants.md) for how variants map consistently across widgets."

```python
bs.DropdownButton(app, text="Primary", accent="primary", items=[]).pack(pady=4)
bs.DropdownButton(app, text="Outline", accent="primary", variant="outline", items=[]).pack(pady=4)
bs.DropdownButton(app, text="Ghost",   accent="primary", variant="ghost",   items=[]).pack(pady=4)
```

<div class="app-window">
    <img src="../../assets/widgets-dropdown-variants.png" alt="Dropdown Variants"/>
</div>

Use `density='compact'` for toolbar contexts, and `show_dropdown_button=False` to hide
the chevron when the button icon makes the dropdown affordance implicit:

```python
bs.DropdownButton(app, text="Export", density="compact", items=items).pack()
bs.DropdownButton(app, icon="gear", icon_only=True, show_dropdown_button=False, items=items).pack()
```

Use `dropdown_button_icon=` to replace the default chevron with a different icon:

```python
bs.DropdownButton(app, text="More", dropdown_button_icon="three-dots", items=items).pack()
```

---

## Examples & patterns

### Adding icons to items

`ContextMenuItem` supports icons per entry.

```python
items = [
    bs.ContextMenuItem("command", text="Settings", icon="gear",         command=lambda: print("Settings")),
    bs.ContextMenuItem("command", text="Help",     icon="circle-help",  command=lambda: print("Help")),
]
bs.DropdownButton(app, text="More", items=items).pack(pady=10)
```

!!! link "See [Icons & Imagery](../../guides/icons.md) for icon sizing, DPI handling, and recoloring behavior."

### Handling item clicks

Attach callbacks at item creation time, or subscribe to all item clicks at the widget level
for centralized routing.

```python
btn = bs.DropdownButton(app, text="Actions", items=items)
btn.pack(pady=10)

def on_action(info):
    # info keys: 'type', 'text', 'value'
    print("Clicked:", info["text"])

btn.on_item_click(on_action)
btn.off_item_click()  # remove when no longer needed
```

!!! link "See [Callbacks](../../guides/reactivity.md) for how bootstack command callbacks are structured."

### Post-construction item management

`DropdownButton` exposes the same item management API as `ContextMenu` directly on the widget.

```python
btn.add_command(text="Export", command=on_export, key="export")
btn.add_separator()
btn.insert_item(0, "command", text="New", command=on_new)

btn.configure_item("export", text="Export As...")
btn.remove_item("export")
btn.items()   # replace all items at once
```

Access the underlying `ContextMenu` directly when you need the full menu API:

```python
btn.context_menu.configure(anchor="ne")
```

---

## Behavior

- The dropdown opens relative to the button and closes when the user clicks away.
- Item commands fire on click, and the menu closes afterward.

!!! link "See [State & Interaction](../../guides/reactivity.md) for focus, hover, and disabled behavior across widgets."

---

## Localization

If localization is enabled, menu labels can be message tokens just like widget `text`.

```python
items = [
    bs.ContextMenuItem("command", text="menu.open",   command=lambda: ...),
    bs.ContextMenuItem("command", text="menu.delete", command=lambda: ...),
]
bs.DropdownButton(app, text="button.file", items=items).pack()
```

!!! link "See [Localization](../../guides/localization.md) for how message tokens are resolved and how language switching works."

---

## Additional resources

### Related widgets

- [Button](button.md)
- [MenuButton](menubutton.md)
- [ContextMenu](contextmenu.md)

### Framework concepts

- [Design System → Variants](../../design-system/variants.md)
- [Design System → Icons](../../design-system/icons.md)
- [Icons & Imagery](../../guides/icons.md)
- [Reactivity](../../guides/reactivity.md)
- [Localization](../../guides/localization.md)

### API reference

- [`bootstack.DropdownButton`](../../reference/widgets/DropdownButton.md)
- [`bootstack.ContextMenuItem`](../../reference/widgets/ContextMenuItem.md)