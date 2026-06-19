"""RangeSlider — full feature demo.

Demonstrates basic usage, value badges, tick marks, accent colors,
step snapping, and disabled state.

Run with:
    python docs/examples/rangeslider.py
"""

import bootstack as bs

with bs.App(title="RangeSlider Demo", padding=20, gap=16, minsize=(400, 200)) as app:

    # Basic
    bs.Label("Basic", font="heading-sm")
    bs.RangeSlider(20, 80, horizontal="stretch")

    # Value badges
    bs.Label("Value Badges", font="heading-sm")
    bs.RangeSlider(20, 80, show_value=True, horizontal="stretch")

    # Tick marks
    bs.Label("Tick Marks", font="heading-sm")
    bs.RangeSlider(20, 80, tick_step=20, horizontal="stretch")
    bs.RangeSlider(20, 80, tick_step=20, minor_ticks=4, show_value=True, horizontal="stretch")

    # Accent colors
    bs.Label("Accent Colors", font="heading-sm")
    with bs.Column(gap=6, horizontal="stretch", horizontal_items="stretch"):
        for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
            bs.RangeSlider(20, 80, accent=accent)

    # Step snapping (both handles snap to 0, 5, 10, … 100)
    bs.Label("Step Snapping", font="heading-sm")
    bs.RangeSlider(20, 80, step=5, tick_step=5, horizontal="stretch")

    # Disabled
    bs.Label("Disabled", font="heading-sm")
    bs.RangeSlider(20, 80, disabled=True, horizontal="stretch")

app.run()
