"""Slider — full feature demo.

Demonstrates accent colors, value badge, min/max labels, tick marks,
custom tick format, and disabled state.

Run with:
    python docs/examples/slider.py
"""

import bootstack as bs

with bs.App(title="Slider Demo", padding=20, gap=16, min_size=(400, 1)) as app:

    # Basic
    bs.Label("Basic", font="heading-sm")
    bs.Slider(horizontal="stretch")

    # Accent colors
    bs.Label("Accent Colors", font="heading-sm")
    with bs.Column(gap=6, horizontal="stretch", horizontal_items="stretch"):
        for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
            bs.Slider(50, accent=accent)

    # Value badge
    bs.Label("Value Badge", font="heading-sm")
    bs.Slider(50, show_value=True, horizontal="stretch")

    # Min / max labels
    bs.Label("Min / Max Labels", font="heading-sm")
    bs.Slider(50, show_minmax=True, horizontal="stretch")

    # Tick marks
    bs.Label("Tick Marks", font="heading-sm")
    bs.Slider(50, tick_step=25, horizontal="stretch")
    bs.Slider(50, tick_step=25, minor_ticks=4, horizontal="stretch")
    bs.Slider(50, tick_step=25, show_value=True, show_minmax=True, horizontal="stretch")

    # Custom tick format
    bs.Label("Custom Tick Format", font="heading-sm")
    bs.Slider(
        0.5,
        min_value=0.0,
        max_value=1.0,
        tick_step=0.25,
        tick_format="{:.0%}",
        show_value=True,
        horizontal="stretch",
    )

    # Disabled
    bs.Label("Disabled", font="heading-sm")
    bs.Slider(30, disabled=True, horizontal="stretch")

app.run()
