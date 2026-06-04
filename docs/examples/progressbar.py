"""ProgressBar — full feature demo.

Demonstrates determinate progress at various fill levels, accent colors,
the thin variant, and vertical orientation in a four-quadrant layout.

Run with:
    python docs/examples/progressbar.py
"""

import bootstack as bs

with bs.App(title="ProgressBar Demo", padding=20, gap=0) as app:
    with bs.Grid(columns=[1, 1], gap=(32, 20), sticky_items="new", fill="x", expand=True):

        # Quadrant 1 — Determinate progress
        with bs.VStack(gap=8):
            bs.Label("Determinate Progress", font="heading-sm")
            for pct in (0, 25, 50, 75, 100):
                bs.ProgressBar(value=pct, fill="x")

        # Quadrant 2 — Accent colors
        with bs.VStack(gap=8):
            bs.Label("Accent Colors", font="heading-sm")
            for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
                bs.ProgressBar(value=65, accent=accent, fill="x")

        # Quadrant 3 — Thin variant
        with bs.VStack(gap=8):
            bs.Label("Thin Variant", font="heading-sm")
            bs.ProgressBar(value=40, variant="thin", fill="x")
            bs.ProgressBar(value=70, accent="primary", variant="thin", fill="x")
            bs.ProgressBar(value=90, accent="success", variant="thin", fill="x")

        # Quadrant 4 — Vertical orientation
        with bs.VStack(gap=8):
            bs.Label("Vertical Orientation", font="heading-sm")
            with bs.HStack(gap=12):
                for pct in (25, 50, 75, 100):
                    bs.ProgressBar(value=pct, orient="vertical")

app.run()
