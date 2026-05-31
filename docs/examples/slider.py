"""Slider — full feature demo.

Demonstrates accent colors, value badge, min/max labels, tick marks,
reactive binding, and disabled state.

Run with:
    python docs/examples/slider.py
"""

import bootstack as bs

with bs.App(title="Slider Demo", padding=20, gap=16, minsize=(500, 0)) as app:

    # Basic
    bs.Label("Basic", font="heading-sm[bold]")
    bs.Slider(fill="x")

    # Accent colors
    bs.Label("Accent Colors", font="heading-sm[bold]")
    with bs.VStack(gap=8, fill="x"):
        for accent in ("primary", "secondary", "success", "warning", "danger"):
            bs.Slider(50, accent=accent, fill="x")

    # Value badge
    bs.Label("Value Badge", font="heading-sm[bold]")
    bs.Slider(50, show_value=True, fill="x")

    # Min / max labels
    bs.Label("Min / Max Labels", font="heading-sm[bold]")
    bs.Slider(50, show_minmax=True, fill="x")

    # Tick marks
    bs.Label("Tick Marks", font="heading-sm[bold]")
    bs.Slider(50, tick_step=25, fill="x")
    bs.Slider(50, tick_step=25, minor_ticks=4, fill="x")
    bs.Slider(50, tick_step=25, show_value=True, show_minmax=True, fill="x")

    # Custom tick format
    bs.Label("Custom Tick Format", font="heading-sm[bold]")
    bs.Slider(
        0.5,
        min_value=0.0,
        max_value=1.0,
        tick_step=0.25,
        tick_format="{:.0%}",
        show_value=True,
        fill="x",
    )

    # Reactive binding
    bs.Label("Reactive Binding", font="heading-sm[bold]")
    with bs.VStack(gap=6, fill="x"):
        volume = bs.Signal(50.0)
        bs.Slider(signal=volume, fill="x")
        vol_lbl = bs.Label("Volume: 50", accent="secondary", font="caption")

        def _update_vol(v):
            vol_lbl.text = f"Volume: {v:.0f}"

        volume.subscribe(_update_vol)

    # Disabled
    bs.Label("Disabled", font="heading-sm[bold]")
    bs.Slider(30, disabled=True, fill="x")

app.run()
