"""Separator — full feature demo.

Demonstrates orientation, accent colors, thickness, and in-context usage.

Run with:
    python docs/examples/separator.py
"""

import bootstack as bs

with bs.App(title="Separator Demo", size=(680, 520), padding=20, gap=24, fill_items='x') as app:

    with bs.VStack(gap=10, fill_items='x'):
        bs.Label("Accent Colors", font="heading-sm")
        for accent in ("default", "primary", "secondary", "info", "success", "warning", "danger"):
            bs.Separator(accent=accent)

    with bs.VStack(gap=10, fill_items='x'):
        bs.Label("Thickness", font="heading-sm")
        for t in (1, 2, 4):
            bs.Separator(thickness=t, accent="primary")

    with bs.VStack(gap=8, fill_items='x'):
        bs.Label("Vertical Orientation", font="heading-sm")
        with bs.HStack(gap=12, anchor_items="center"):
            bs.Label("Home")
            bs.Separator(orient="vertical", length=16)
            bs.Label("Products")
            bs.Separator(orient="vertical", length=16)
            bs.Label("Contact")

    # Full-width in-context examples
    with bs.VStack(fill_items='x'):
        bs.Label("In Context", font="heading-sm")
        with bs.HStack(gap=32, anchor_items='n'):
            with bs.VStack(gap=6, fill_items='x'):
                bs.Label("Profile", font="heading-md")
                bs.Separator()
                bs.Label("Name: Ada Lovelace")
                bs.Label("Role: Engineer")

            with bs.VStack(gap=6, fill_items='x'):
                bs.Label("Danger Zone", font="heading-md")
                bs.Separator(accent="danger", thickness=2)
                bs.Label("Irreversible action below", accent="danger")

app.run()
