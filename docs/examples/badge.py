"""Badge — full feature demo.

Demonstrates shape variants, accent colors, and in-context usage patterns.

Run with:
    python docs/examples/badge.py
"""

import bootstack as bs

with bs.App(title="Badge Demo", padding=20, gap=16) as app:

    # Variants
    bs.Label("Variants", font="heading-sm")
    with bs.Row(gap=8):
        bs.Badge("Square",  accent="primary")
        bs.Badge("Pill",    accent="primary",  variant="pill")
        bs.Badge("99+",     accent="danger",   variant="pill")
        bs.Badge("New",     accent="success",  variant="pill")
        bs.Badge("Beta",    accent="warning",  variant="pill")

    # Accent colors — square
    bs.Label("Accent Colors — Square", font="heading-sm")
    with bs.Row(gap=8):
        for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
            bs.Badge(accent.title(), accent=accent)

    # Accent colors — pill
    bs.Label("Accent Colors — Pill", font="heading-sm")
    with bs.Row(gap=8):
        for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
            bs.Badge(accent.title(), accent=accent, variant="pill")

    # In context — heading with count
    bs.Label("In Context", font="heading-sm")
    with bs.Column(gap=8):
        with bs.Row(gap=8):
            bs.Label("Inbox", font="heading-md")
            bs.Badge("12", accent="primary", variant="pill")

        with bs.Row(gap=8):
            bs.Label("Alerts", font="heading-md")
            bs.Badge("3", accent="danger", variant="pill")

        with bs.Row(gap=8):
            bs.Label("Run-A15")
            bs.Badge("Complete", accent="success",  variant="pill")

        with bs.Row(gap=8):
            bs.Label("Run-A14")
            bs.Badge("2 warnings", accent="warning")
            bs.Badge("Fail",       accent="danger",  variant="pill")

app.run()
