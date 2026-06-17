"""Separator — full feature demo.

Demonstrates orientation, accent colors, thickness, and in-context usage.

Run with:
    python docs/examples/separator.py
"""

import bootstack as bs

with bs.App(title="Separator Demo", size=(680, 520), padding=20, gap=24, horizontal_items="stretch") as app:

    with bs.Column(gap=10, horizontal_items="stretch"):
        bs.Label("Accent Colors", font="heading-sm")
        for accent in ("default", "primary", "secondary", "info", "success", "warning", "danger"):
            bs.Separator(accent=accent)

    with bs.Column(gap=10, horizontal_items="stretch"):
        bs.Label("Thickness", font="heading-sm")
        for t in (1, 2, 4):
            bs.Separator(thickness=t, accent="primary")

    with bs.Column(gap=8, horizontal_items="stretch"):
        bs.Label("Vertical Orientation", font="heading-sm")
        with bs.Row(gap=12, vertical_items="center"):
            bs.Label("Home")
            bs.Separator(orient="vertical", length=16)
            bs.Label("Products")
            bs.Separator(orient="vertical", length=16)
            bs.Label("Contact")

    # Full-width in-context examples
    with bs.Column(horizontal_items="stretch"):
        bs.Label("In Context", font="heading-sm")
        with bs.Row(gap=32):
            with bs.Column(gap=6, horizontal_items="stretch"):
                bs.Label("Profile", font="heading-md")
                bs.Separator()
                bs.Label("Name: Ada Lovelace")
                bs.Label("Role: Engineer")

            with bs.Column(gap=6, horizontal_items="stretch"):
                bs.Label("Danger Zone", font="heading-md")
                bs.Separator(accent="danger", thickness=2)
                bs.Label("Irreversible action below", accent="danger")

app.run()
