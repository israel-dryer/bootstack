"""ButtonGroup — full feature demo.

Demonstrates accent colors, style variants, icons, icon-only, vertical
orientation, compact density, disabled state, and item management.

Run with:
    python docs/examples/buttongroup.py
"""

import bootstack as bs

with bs.App(title="ButtonGroup Demo", padding=20, gap=16) as app:

    # Accent colors
    bs.Label("Accent Colors", font="heading-sm")
    with bs.HStack(gap=8):
        for accent in ("default", "primary", "secondary", "success", "warning", "danger"):
            bg = bs.ButtonGroup(accent=accent)
            bg.add("A")
            bg.add("B")

    # Style variants
    bs.Label("Style Variants", font="heading-sm")
    with bs.HStack(gap=8):
        for variant in ("solid", "outline", "ghost"):
            bg = bs.ButtonGroup(variant=variant)
            bg.add("Save")
            bg.add("Cancel")

    # Icons
    bs.Label("Icons", font="heading-sm")
    bg = bs.ButtonGroup(accent="primary", variant="outline")
    bg.add("Bold",      icon="type-bold")
    bg.add("Italic",    icon="type-italic")
    bg.add("Underline", icon="type-underline")

    # Icon-only (icon_only inferred when no label is provided)
    bs.Label("Icon Only", font="heading-sm")
    with bs.HStack(gap=8):
        bg1 = bs.ButtonGroup(variant="outline", accent="primary")
        bg1.add(icon="type-bold")
        bg1.add(icon="type-italic")
        bg1.add(icon="type-underline")
        bg1.add(icon="type-strikethrough")

        bg2 = bs.ButtonGroup()
        bg2.add(icon="scissors")
        bg2.add(icon="copy")
        bg2.add(icon="clipboard")

    # Vertical orientation
    bs.Label("Vertical Orientation", font="heading-sm")
    bg = bs.ButtonGroup("vertical", accent="primary", variant="outline")
    bg.add("Cut",   icon="scissors")
    bg.add("Copy",  icon="copy")
    bg.add("Paste", icon="clipboard")

    # Compact density
    bs.Label("Compact Density", font="heading-sm")
    with bs.HStack(gap=8):
        bg1 = bs.ButtonGroup(accent="primary")
        bg1.add("Cut",   icon="scissors")
        bg1.add("Copy",  icon="copy")
        bg1.add("Paste", icon="clipboard")

        bg2 = bs.ButtonGroup(accent="primary", density="compact")
        bg2.add("Cut",   icon="scissors")
        bg2.add("Copy",  icon="copy")
        bg2.add("Paste", icon="clipboard")

    # Disabled
    bs.Label("Disabled", font="heading-sm")
    with bs.HStack(gap=8):
        bg1 = bs.ButtonGroup(accent="primary")
        bg1.add("Save")
        bg1.add("Cancel")

        bg2 = bs.ButtonGroup(accent="primary", disabled=True)
        bg2.add("Save")
        bg2.add("Cancel")

    # Handling clicks (group-level on_click — e.data has key, text, icon)
    bs.Label("Handling Clicks", font="heading-sm")
    bg = bs.ButtonGroup(accent="primary")
    bg.add("Save",   icon="save",  key="save")
    bg.add("Cancel", icon="x-lg", key="cancel")
    bg.add("Delete", icon="trash", key="delete")
    last = bs.Signal("(none)")
    bg.on_click(lambda e: last.set(e.key))
    bs.Label(textsignal=last, accent="secondary")

app.run()