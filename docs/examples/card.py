"""Card — full feature demo.

Demonstrates accent borders, layout modes, and nested surface stepping.

Run with:
    python docs/examples/card.py
"""

import bootstack as bs

with bs.App(title="Card Demo", padding=20, gap=16) as app:

    # Accent colors
    bs.Label("Accent Borders", font="heading-sm")
    with bs.HStack(gap=12):
        for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
            with bs.Card(accent=accent, padding=12, gap=4):
                bs.Label(accent.title(), font="heading-sm", accent=accent)
                bs.Label("Card content", font="caption")

    # Layout modes
    bs.Label("Layout Modes", font="heading-sm")
    with bs.HStack(gap=12, anchor_items="n"):

        with bs.Card(padding=12, gap=8):
            bs.Label("VStack (default)", font="heading-sm")
            bs.Label("First item")
            bs.Label("Second item")
            bs.Label("Third item")

        with bs.Card(layout="hstack", padding=12, gap=12, anchor_items="center"):
            bs.Label("HStack", font="heading-sm")
            bs.Label("A")
            bs.Label("B")
            bs.Label("C")

        with bs.Card(layout="grid", columns=[1, 1], padding=12, gap=8, sticky_items="ew"):
            bs.Label("Grid", font="heading-sm")
            bs.Label("2 cols")
            bs.Label("Item A")
            bs.Label("Item B")
            bs.Label("Item C")
            bs.Label("Item D")

    # Nested surface stepping
    bs.Label("Nested Cards", font="heading-sm")
    with bs.Card(padding=12, gap=8):
        bs.Label("Outer (card surface)", font="heading-sm")
        with bs.HStack(gap=8):
            with bs.Card(padding=10, gap=4):
                bs.Label("Inner A", font="heading-sm")
                bs.Label("Overlay surface", font="caption")
            with bs.Card(padding=10, gap=4):
                bs.Label("Inner B", font="heading-sm")
                bs.Label("Overlay surface", font="caption")
            with bs.Card(accent="primary", padding=10, gap=4):
                bs.Label("Inner C", font="heading-sm", accent="primary")
                bs.Label("Accent tint", font="caption")

app.run()