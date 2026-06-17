"""ToggleGroup — full feature demo.

Demonstrates single-select, multi-select, style variants, accent colors,
orientation, and disabled states.

Run with:
    python docs/examples/togglegroup.py
"""

import bootstack as bs

with bs.App(title="ToggleGroup Demo", padding=20, gap=16) as app:

    # Single mode
    bs.Label("Single Select", font="heading-sm")
    bs.ToggleGroup(["Day", "Week", "Month"], value="Week")

    # Multi mode
    bs.Label("Multi Select", font="heading-sm")
    bs.ToggleGroup(["Bold", "Italic", "Underline"], mode="multi", value={"Bold", "Underline"})

    # Style variants — inactive + active per variant
    bs.Label("Style Variants", font="heading-sm")
    with bs.Row(gap=16):
        for variant in ("solid", "outline", "ghost"):
            with bs.Column(gap=4):
                bs.ToggleGroup(["Off", "On"], accent="primary", variant=variant, value="On")

    # Accent colors
    bs.Label("Accent Colors", font="heading-sm")
    with bs.Row(gap=8):
        tg = bs.ToggleGroup(value="primary")
        for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
            tg.add(accent, accent=accent)

    # Vertical orientation
    bs.Label("Vertical", font="heading-sm")
    bs.ToggleGroup(["Top", "Middle", "Bottom"], orient="vertical", value="Middle")

    # Disabled
    bs.Label("Disabled", font="heading-sm")
    with bs.Row(gap=16):
        bs.ToggleGroup(["A", "B", "C"], value="B", disabled=True)
        bs.ToggleGroup(["X", "Y", "Z"], mode="multi", value={"X", "Z"}, disabled=True)

app.run()
