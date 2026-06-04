"""RangeSlider — full feature demo.

Demonstrates basic usage, value badges, tick marks, accent colors,
and disabled state.

Run with:
    python docs/examples/rangeslider.py
"""

import bootstack as bs

with bs.App(title="RangeSlider Demo", padding=20, gap=16) as app:

    # Basic
    bs.Label("Basic", font="heading-sm")
    bs.RangeSlider(20, 80, fill="x")

    # Value badges
    bs.Label("Value Badges", font="heading-sm")
    bs.RangeSlider(20, 80, show_value=True, fill="x")

    # Tick marks
    bs.Label("Tick Marks", font="heading-sm")
    bs.RangeSlider(20, 80, tick_step=20, fill="x")
    bs.RangeSlider(20, 80, tick_step=20, minor_ticks=4, show_value=True, fill="x")

    # Accent colors
    bs.Label("Accent Colors", font="heading-sm")
    with bs.VStack(gap=6, fill="x"):
        for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
            bs.RangeSlider(20, 80, accent=accent, fill="x")

    # Disabled
    bs.Label("Disabled", font="heading-sm")
    bs.RangeSlider(20, 80, disabled=True, fill="x")

app.run()
