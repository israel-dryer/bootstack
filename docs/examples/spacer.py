"""Spacer — full feature demo.

A flexible (or fixed) break that pushes neighbors apart in a Row or Column.

Run with:
    python docs/examples/spacer.py
"""

import bootstack as bs

with bs.App(title="Spacer Demo", size=(640, 560), padding=20, gap=16) as app:

    # Flexible — pushes the trailing group to the right edge
    bs.Label("Toolbar (flexible spacer)", font="heading-sm")
    with bs.Row(gap=4, show_border=True, padding=8, horizontal="stretch"):
        bs.Button("New")
        bs.Button("Open")
        bs.Spacer()
        bs.Button("Settings")
        bs.Button("Profile")

    # Fixed-size gaps between clusters
    bs.Label("Fixed gaps (size=)", font="heading-sm")
    with bs.Row(gap=4, show_border=True, padding=8):
        bs.Button("One")
        bs.Spacer(size=48)
        bs.Button("Two")
        bs.Spacer(size=48)
        bs.Button("Three")

    # Weighted spacers share the leftover space 1:2
    bs.Label("Weighted spacers (weight=)", font="heading-sm")
    with bs.Row(gap=4, show_border=True, padding=8, horizontal="stretch"):
        bs.Button("Left")
        bs.Spacer(weight=1)
        bs.Button("Center")
        bs.Spacer(weight=2)
        bs.Button("Right")

    # In a column — push the footer to the bottom
    bs.Label("Footer (column spacer)", font="heading-sm")
    with bs.Column(gap=6, show_border=True, padding=8, grow=True,
                   horizontal="stretch", horizontal_items="stretch"):
        bs.Label("Body content.")
        bs.Spacer()
        bs.Button("Save", accent="primary")

app.run()
