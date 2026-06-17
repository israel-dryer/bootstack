"""Gauge — full feature demo.

Demonstrates meter types, accent colors, label/prefix/suffix, segmented arcs,
and thickness variants.

Run with:
    python docs/examples/gauge.py
"""

import bootstack as bs

with bs.App(title="Gauge Demo", padding=20, gap=16) as app:

    # Full vs semi meter types
    bs.Label("Variants", font="heading-sm")
    with bs.Row(gap=20):
        bs.Gauge(value=68, variant="full", subtitle="Full")
        bs.Gauge(value=68, variant="semi", subtitle="Semi")

    # Accent colors
    bs.Label("Accent Colors", font="heading-sm")
    with bs.Row(gap=12):
        for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
            bs.Gauge(value=65, accent=accent, size=140, thickness=14, subtitle=accent.title())

    # Prefix / suffix / subtitle
    bs.Label("Labels and Formatting", font="heading-sm")
    with bs.Row(gap=20):
        bs.Gauge(value=4200, max_value=10000, value_prefix="$", value_template="{:.0f}",
                 subtitle="Revenue", accent="success")
        bs.Gauge(value=72, value_suffix="%", subtitle="Disk Used", accent="warning")
        bs.Gauge(value=3.7, max_value=5.0, value_template="{:.1f}", subtitle="Rating",
                 accent="primary")

    # Segmented / dashed arc
    bs.Label("Segmented Arc", font="heading-sm")
    with bs.Row(gap=20):
        bs.Gauge(value=55, segment_width=8, subtitle="Segmented", accent="primary")
        bs.Gauge(value=55, segment_width=4, thickness=12, subtitle="Fine segments",
                 accent="secondary")

    # Thickness variants
    bs.Label("Thickness", font="heading-sm")
    with bs.Row(gap=20):
        bs.Gauge(value=70, thickness=6,  subtitle="Thin",   accent="info")
        bs.Gauge(value=70, thickness=14, subtitle="Default", accent="info")
        bs.Gauge(value=70, thickness=24, subtitle="Thick",  accent="info")

app.run()
