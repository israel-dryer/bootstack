"""RangeSlider — full feature demo.

Demonstrates basic usage, value badges, tick marks, accent colors,
reactive binding, and disabled state.

Run with:
    python docs/examples/rangeslider.py
"""

import bootstack as bs

with bs.App(title="RangeSlider Demo", padding=20, gap=16, minsize=(500, 0)) as app:

    # Basic
    bs.Label("Basic", font="heading-sm[bold]")
    bs.RangeSlider(20, 80, fill="x")

    # Value badges
    bs.Label("Value Badges", font="heading-sm[bold]")
    bs.RangeSlider(20, 80, show_value=True, fill="x")

    # Tick marks
    bs.Label("Tick Marks", font="heading-sm[bold]")
    bs.RangeSlider(20, 80, tick_step=20, fill="x")
    bs.RangeSlider(20, 80, tick_step=20, minor_ticks=4, show_value=True, fill="x")

    # Accent colors
    bs.Label("Accent Colors", font="heading-sm[bold]")
    with bs.VStack(gap=8, fill="x"):
        for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
            bs.RangeSlider(20, 80, accent=accent, fill="x")

    # Reactive binding
    bs.Label("Reactive Binding", font="heading-sm[bold]")
    with bs.VStack(gap=6, fill="x"):
        lo = bs.Signal(25.0)
        hi = bs.Signal(75.0)
        rs = bs.RangeSlider(low_signal=lo, high_signal=hi, fill="x")
        range_lbl = bs.Label("Range: 25 – 75", accent="secondary", font="caption")

        def _update_range(v):
            range_lbl.text = f"Range: {rs.low_value:.0f} – {rs.high_value:.0f}"

        lo.subscribe(_update_range)
        hi.subscribe(_update_range)

    # Disabled
    bs.Label("Disabled", font="heading-sm[bold]")
    bs.RangeSlider(20, 80, disabled=True, fill="x")

app.run()
