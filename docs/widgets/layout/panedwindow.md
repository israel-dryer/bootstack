---
title: PanedWindow
---

# PanedWindow

`PanedWindow` is a **resizable split container** that arranges child panes with draggable separators.

It wraps `bs.Panedwindow` and is used to build layouts like:

- sidebar + content

- navigator + editor + inspector

- vertically stacked regions with adjustable heights

<!--
IMAGE: PanedWindow splitting sidebar/content
Theme variants: light / dark
-->

---

## Quick start

```python
import bootstack as bs

app = bs.App()

pw = bs.PanedWindow(app, orient="horizontal")
pw.pack(fill="both", expand=True)

sidebar = bs.Frame(pw, padding=12, width=220)
content = bs.Frame(pw, padding=12)

pw.add(sidebar, weight=0)
pw.add(content, weight=1)

bs.Label(sidebar, text="Sidebar").pack(anchor="w")
bs.Label(content, text="Content").pack(anchor="w")

app.mainloop()
```

---

## When to use

Use `PanedWindow` when:

- users benefit from adjustable regions

- your app has a "workbench" layout (nav/editor/inspector)

**Consider a different control when:**

- the layout should be fixed -- use [Frame](frame.md) containers

- resizing regions would add complexity without benefit

---

## Appearance

A paned layout works well when:

- panes have different importance (content gets most space)

- users may want to expand/collapse a region temporarily

- window resizing should feel responsive

!!! link "Design System"
    For theming details and color tokens, see [Design System](../../design-system/index.md).

---

## Examples & patterns

### Core concepts

#### Panes

Each child added to a paned window is a *pane*. You can assign weights (if supported) to influence how extra space is distributed.

#### Sashes

The draggable separators between panes are called *sashes*. Users drag sashes to resize panes.

### `orient`

```python
bs.PanedWindow(app, orient="horizontal")  # left/right
bs.PanedWindow(app, orient="vertical")    # top/bottom
```

### Adding panes: `add(...)`

```python
pw.add(frame)
pw.add(frame, weight=1)
```

### Removing panes

Use the ttk panedwindow API (varies by implementation/version).

### UX guidance

- Don't overuse panes -- 2 (or 3) is usually enough.

- Provide sensible default sizes.

- Consider minimum sizes for panes that contain dense UI (lists, trees, inspectors).

---

## Behavior

- Users drag the sash to resize adjacent panes.

- Panes can be sized by the program (e.g., setting widths/heights + disabling propagation on child frames).

- If you need collapsible panes, pair with explicit show/hide controls and remember prior sash positions.

---

## Additional resources

### Related widgets

- [Frame](frame.md) -- typical pane content container

- [Separator](separator.md) -- lightweight alternative when panes are fixed

- [ScrollView](scrollview.md) -- scroll content within a pane

### Framework concepts

- [Layout Properties](../../guides/layout.md)

- [Layout](../../platform/geometry-and-layout.md)

### API reference

- [`bootstack.PanedWindow`](../../reference/widgets/PanedWindow.md)