---
title: Icons
---

# Icons

Icons in bootstack are **symbolic UI elements**, not static image files.

They are part of the design system and behave consistently across themes,
widgets, and screen densities.

---

## Icon model

An icon in bootstack is:

- referenced by name (not file path)
- resolved through an icon provider
- recolored automatically by theme
- DPI-aware and cached by the framework

Icons participate in widget state (hover, disabled, active) automatically.

---

## Why icons are symbolic

By treating icons symbolically:

- the same icon works in light and dark themes
- color and contrast are handled centrally
- scaling is automatic
- widgets remain declarative

Applications express *intent*, not rendering details.

---

## Icon source: Bootstrap Icons

bootstack ships with the full **[Bootstrap Icons](https://icons.getbootstrap.com/)**
catalog (2,000+ icons) as its built-in icon set. Any name from the Bootstrap
Icons catalog is a valid `icon=` value:

```python
bs.Button(app, icon="house")
bs.Label(app, icon="info-circle")
bs.CheckToggle(app, icon="bell")
```

Use the [Bootstrap Icons website](https://icons.getbootstrap.com/) as the
canonical "what icons can I use?" reference — search by keyword, copy the
name, paste it into your widget.

Internally, the catalog is supplied by the `ttkbootstrap_icons_bs` provider,
which renders each glyph from a font asset and recolors it to match the active
theme. This is an implementation detail — application code only needs the icon
name.

---

## Browsing icons in bootstack

For a quick visual browse without leaving the framework, run:

```bash
bootstack gallery
```

The widget gallery's **Icons** page showcases ~20 commonly-used icons, the
available size range (12–48 px), and accent-colored variants. Use it to
preview how an icon renders in your current theme before committing to it.

---

## Using icons in applications

How icons are applied to widgets and patterns is covered in:

- [Guides → Icons](../guides/icons.md)

Widget-specific icon usage examples appear in:

- [Widgets → Button](../widgets/actions/button.md)
- [Widgets → ContextMenu](../widgets/actions/contextmenu.md)

---

## Related concepts

- [Design System → Colors](colors.md)
- [Guides → Icons](../guides/icons.md)
