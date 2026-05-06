---
title: Badge
---

# Badge

`Badge` is a compact **status indicator** built on top of `Label`.

It's designed for short, scannable values like **counts**, **statuses**, and **tags** — for example: "New", "Beta", "3", "Offline".

---

## Quick start

```python
import bootstack as bs

app = bs.App()

bs.Badge(app, text="New").pack(padx=20, pady=10)
bs.Badge(app, text="3", accent="primary").pack(padx=20, pady=10)

app.mainloop()
```

---

## When to use

Use `Badge` when:

- you need a small, high-contrast label for status or counts

- the value is short (typically 1-12 characters)

- you want a consistent visual "pill" across the UI

### Consider a different control when...

- **Text is long or multi-line** — use [Label](label.md) instead

- **Content should blend into the surrounding layout** — use [Label](label.md) for less visual emphasis

- **You need transient feedback that disappears automatically** — use [Toast](../overlays/toast.md) instead

---

## Appearance

### Styling with `accent`

`Badge` defaults to `variant="badge"` and uses the badge styling automatically.

```python
bs.Badge(app, text="Beta")                    # default badge styling
bs.Badge(app, text="Beta", accent="primary")   # primary colored badge
bs.Badge(app, text="Beta", accent="success")   # success colored badge
bs.Badge(app, text="Beta", accent="danger")    # danger colored badge
```

!!! link "Design System"
    See [Design System](../../design-system/index.md) for color tokens and theming guidelines.

---

## Examples & patterns

### Icon badges

Because `Badge` subclasses `Label`, you can use icons the same way:

```python
bs.Badge(app, text="Verified", icon="check").pack(pady=6)
bs.Badge(app, icon="bell", icon_only=True, accent="info").pack(pady=6)
```

### Common options

Badge accepts the standard `Label` options, including:

- `text`

- `icon`, `image`, `compound`

- `icon_only`

- `padding`, `width`, `wraplength`

- `font`, `foreground`, `background`

- `localize`, `value_format`

---

## Behavior

Badge is a static display widget that shows text or icons. It does not respond to user interaction by default.

---

## Localization

Badge inherits localization support from `Label`:

```python
bs.Badge(app, text="status.new", localize=True)
```

!!! link "Localization"
    See [Localization](../../guides/localization.md) for translation setup.

---

## Reactivity

Badge can be updated dynamically by binding to signals:

```python
count = bs.Signal(5)
badge = bs.Badge(app, text=count)
count.set(10)  # Badge updates automatically
```

!!! link "Signals"
    See [Signals](../../guides/reactivity.md) for reactive programming patterns.

---

## Additional resources

### Related widgets

- [Label](label.md) — general-purpose read-only text

- [Toast](../overlays/toast.md) — non-blocking feedback

- [Progressbar](progressbar.md) — continuous progress indicators

- [Meter](meter.md) — dashboard-style gauges

- [FloodGauge](floodgauge.md) — capacity indicators

### Framework concepts

- [Design System](../../design-system/index.md) — colors, typography, and theming

- [Signals](../../guides/reactivity.md) — reactive data binding

- [Localization](../../guides/localization.md) — translation support

### API reference

- [`bootstack.Badge`](../../reference/widgets/Badge.md)