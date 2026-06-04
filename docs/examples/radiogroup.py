"""RadioGroup — full feature demo.

Demonstrates basic usage, orientation, titles, reactive binding, and
disabled states.

Run with:
    python docs/examples/radiogroup.py
"""

import bootstack as bs

with bs.App(title="RadioGroup Demo", padding=20, gap=16) as app:

    # Basic
    bs.Label("Basic", font="heading-sm")
    bs.RadioGroup(["Small", "Medium", "Large"], value="Medium")

    # Accent colors
    bs.Label("Accent Colors", font="heading-sm")
    with bs.HStack(gap=16):
        for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
            bs.RadioGroup(["On"], accent=accent, value="On", title=accent.title())

    # Orientation
    bs.Label("Orientation", font="heading-sm")
    with bs.HStack(gap=32):
        bs.RadioGroup(["A", "B", "C"], value="A", title="Horizontal")
        bs.RadioGroup(["A", "B", "C"], value="A", title="Vertical", orient="vertical")

    # With title
    bs.Label("With Title", font="heading-sm")
    with bs.HStack(gap=32):
        bs.RadioGroup(
            [("Small", "s"), ("Medium", "m"), ("Large", "l")], title="Size", value="m",
        )
        bs.RadioGroup(
            [("Light", "light"), ("Dark", "dark"), ("Auto", "auto")],
            title="Theme", orient="vertical", value="auto",
        )

    # Disabled
    bs.Label("Disabled", font="heading-sm")
    bs.RadioGroup(["Alpha", "Beta", "Gamma"], value="Beta", disabled=True)

app.run()
