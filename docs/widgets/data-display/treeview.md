---
title: TreeView
---

# TreeView

`TreeView` displays **hierarchical data** in an expandable tree structure.

It's ideal for representing parent/child relationships like folders, categories, or outlines. It is also the widget to reach for when you need per-row color coding — `tag_configure` lets you map data values to background or foreground colors row by row.

---

## Quick start

```python
import bootstack as bs

app = bs.App()

tree = bs.TreeView(app)
tree.pack(fill="both", expand=True)

tree.insert("", "end", text="Root")
app.mainloop()
```

---

## When to use

Use TreeView when:

- data has a natural hierarchy
- users need to navigate parent/child relationships
- content can be expanded and collapsed
- you need per-row color coding via `tag_configure`

### Consider a different control when...

- **Data is flat and column-based** — use [TableView](tableview.md)
- **Data is a simple list without hierarchy** — use [ListView](listview.md)
- **You only need to display a single value** — use [Label](label.md) or [Badge](badge.md)

---

## Appearance

### Styling

```python
tree = bs.TreeView(app, accent="primary")
```

Bootstack-specific appearance params:

- `density` — `"default"` or `"compact"` row sizing
- `show_border` — draw a border around the widget
- `border_color` — border color token
- `select_background` — row selection highlight color token
- `header_background` — header row background token

!!! link "See [Design System](../../design-system/index.md) for color tokens and theming guidelines."

---

## Examples & patterns

### Building a tree

```python
tree = bs.TreeView(app)
tree.pack(fill="both", expand=True)

root = tree.insert("", "end", text="Documents")
tree.insert(root, "end", text="Report.pdf")
tree.insert(root, "end", text="Notes.txt")

subfolder = tree.insert(root, "end", text="Images")
tree.insert(subfolder, "end", text="photo.jpg")
```

### With columns

```python
tree = bs.TreeView(app, columns=("size", "modified"))
tree.heading("#0",       text="Name")
tree.heading("size",     text="Size")
tree.heading("modified", text="Modified")

# Configure column widths and alignment
tree.column("size",     width=80,  anchor="e")
tree.column("modified", width=120, anchor="center")

tree.insert("", "end", text="file.txt", values=("10 KB", "2024-01-15"))
```

### Per-row color with `tag_configure`

`tag_configure` is the primary reason to choose `TreeView` over `TableView` when you need status-based row colors:

```python
tree = bs.TreeView(app, columns=("status",))
tree.heading("status", text="Status")

# Define tag styles
tree.tag_configure("ok",      background="#d4edda", foreground="#155724")
tree.tag_configure("warning", background="#fff3cd", foreground="#856404")
tree.tag_configure("error",   background="#f8d7da", foreground="#721c24")

# Apply tags when inserting rows
for record in records:
    tag = "ok" if record["status"] == "active" else "warning"
    tree.insert("", "end", text=record["name"],
                values=(record["status"],), tags=(tag,))
```

!!! link "See [Data Tables](../../guides/data-tables.md) for guidance on when to use TreeView vs TableView."

### Common options

- `columns` — additional columns beyond the tree column
- `displaycolumns` — subset and display order of columns (e.g. `("#0", "size")`)
- `show` — `"tree"` (tree column only), `"headings"` (columns only), or `"tree headings"` (both)
- `selectmode` — `"browse"`, `"extended"`, or `"none"`
- `height` — number of visible rows

---

## Behavior

### Events

```python
def on_select(event):
    selected = tree.selection()
    print("Selected:", selected)

tree.bind("<<TreeviewSelect>>", on_select)
tree.bind("<<TreeviewOpen>>",   lambda e: print("expanded"))
tree.bind("<<TreeviewClose>>",  lambda e: print("collapsed"))
```

### Item operations

```python
selected = tree.selection()        # selected item IDs
tree.item(item_id, open=True)      # expand
tree.item(item_id, open=False)     # collapse
data = tree.item(item_id)          # get item dict
tree.delete(item_id)               # remove
tree.move(item_id, parent, index)  # reorder
```

---

## Reactivity

TreeView is updated imperatively — clear and rebuild when data changes:

```python
for item in tree.get_children():
    tree.delete(item)

for record in new_data:
    tree.insert("", "end", text=record["name"])
```

---

## Additional resources

### Related widgets

- [TableView](tableview.md) — tabular record display
- [ListView](listview.md) — virtual scrolling list
- [ScrollView](../layout/scrollview.md) — scrolling containers

### Framework concepts

- [Data Tables](../../guides/data-tables.md) — TreeView vs TableView guidance
- [Design System](../../design-system/index.md) — colors, typography, and theming

### API reference

- [`bootstack.TreeView`](../../reference/widgets/TreeView.md)