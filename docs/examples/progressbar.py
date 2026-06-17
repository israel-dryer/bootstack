"""ProgressBar — full feature demo.

Demonstrates determinate progress at various fill levels, accent colors,
the thin variant, and vertical orientation in a four-quadrant layout.

Run with:
    python docs/examples/progressbar.py
"""

import bootstack as bs

with bs.App(title="ProgressBar Demo", padding=20, gap=0) as app:
    with bs.Grid(columns=[1, 1], gap=(32, 20), vertical_items="top", horizontal="stretch", grow=True):

        # Quadrant 1 — Determinate progress
        with bs.Column(gap=8, horizontal_items="stretch"):
            bs.Label("Determinate Progress", font="heading-sm")
            for pct in (0, 25, 50, 75, 100):
                bs.ProgressBar(value=pct)

        # Quadrant 2 — Accent colors
        with bs.Column(gap=8, horizontal_items="stretch"):
            bs.Label("Accent Colors", font="heading-sm")
            for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
                bs.ProgressBar(value=65, accent=accent)

        # Quadrant 3 — Thin variant
        with bs.Column(gap=8, horizontal_items="stretch"):
            bs.Label("Thin Variant", font="heading-sm")
            bs.ProgressBar(value=40, variant="thin")
            bs.ProgressBar(value=70, accent="primary", variant="thin")
            bs.ProgressBar(value=90, accent="success", variant="thin")

        # Quadrant 4 — Vertical orientation
        with bs.Column(gap=8, horizontal_items="stretch"):
            bs.Label("Vertical Orientation", font="heading-sm")
            with bs.Row(gap=12):
                for pct in (25, 50, 75, 100):
                    bs.ProgressBar(value=pct, orient="vertical")

app.run()
