"""SelectButton — full feature demo.

Demonstrates basic usage, accent colors, style variants, icons, and
disabled states.

Run with:
    python docs/examples/selectbutton.py
"""

import bootstack as bs

with bs.App(title="SelectButton Demo", padding=20, gap=16) as app:

    # Basic
    bs.Label("Basic", font="heading-sm")
    with bs.HStack(gap=8):
        bs.SelectButton(["Light", "Dark", "Auto"], value="Light")
        bs.SelectButton(["Small", "Medium", "Large"], value="Medium")

    # Accent colors
    bs.Label("Accent Colors", font="heading-sm")
    with bs.HStack(gap=8):
        for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
            bs.SelectButton(["On", "Off"], value="On", accent=accent)

    # Style variants
    bs.Label("Style Variants", font="heading-sm")
    with bs.HStack(gap=8):
        for variant in ("solid", "outline", "ghost"):
            bs.SelectButton(["A", "B", "C"], value="A",
                            accent="primary", variant=variant)

    # With icon
    bs.Label("With Icon", font="heading-sm")
    with bs.HStack(gap=8):
        bs.SelectButton(["Light", "Dark", "Auto"],
                        value="Dark", icon="moon-fill")
        bs.SelectButton(["Small", "Medium", "Large"],
                        value="Large", icon="fonts", accent="secondary")

    # Disabled
    bs.Label("Disabled", font="heading-sm")
    with bs.HStack(gap=8):
        bs.SelectButton(["A", "B", "C"], value="B", disabled=True)
        bs.SelectButton(["A", "B", "C"], value="B", disabled=True,
                        accent="primary", variant="outline")

app.run()
