"""Column — full feature demo.

Demonstrates gap, vertical_items (group arrangement), horizontal_items
(cross-axis alignment), grow / weights (sharing height), and Spacer.

Run with:
    python docs/examples/column.py
"""

import bootstack as bs

with bs.App(title="Column Demo", minsize=(720, 500), padding=20, gap=16) as app:

    with bs.Row(gap=16, horizontal="stretch", vertical_items="top"):

        # gap
        with bs.Column(gap=4, grow=True):
            bs.Label("gap", font="heading-sm")
            with bs.Column(show_border=True, gap=8, padding=8,
                           horizontal="stretch", horizontal_items="stretch"):
                [bs.Button(lbl) for lbl in ("A", "B", "C")]

        # horizontal_items — cross-axis alignment of the children
        with bs.Column(gap=4, grow=True):
            bs.Label("horizontal_items", font="heading-sm")
            for alignment in ("left", "center", "right", "stretch"):
                bs.Label(f"={alignment!r}", font="caption")
                with bs.Column(horizontal_items=alignment, show_border=True,
                               padding=8, horizontal="stretch"):
                    bs.Button("Save")

    # vertical_items — arrange the whole group down the column
    bs.Label("vertical_items", font="heading-sm")
    with bs.Row(gap=16, horizontal="stretch", vertical_items="top"):
        for arrangement in ("top", "center", "bottom", "space-between"):
            with bs.Column(gap=4, grow=True):
                bs.Label(f"={arrangement!r}", font="caption")
                with bs.Column(vertical_items=arrangement, show_border=True,
                               padding=8, height=140, horizontal="stretch",
                               horizontal_items="stretch"):
                    bs.Button("Header")
                    bs.Button("Footer")

    # grow — one child claims and fills the leftover height
    bs.Label("grow", font="heading-sm")
    with bs.Column(gap=6, show_border=True, padding=8, height=150,
                   horizontal="stretch", horizontal_items="stretch"):
        bs.Button("Header")
        bs.Button("Content", grow=True)   # fills the middle
        bs.Button("Footer")

    # Spacer — push a footer to the bottom without a fixed height
    bs.Label("Spacer", font="heading-sm")
    with bs.Column(gap=6, show_border=True, padding=8, height=150,
                   horizontal="stretch", horizontal_items="stretch"):
        bs.Button("Header")
        bs.Spacer()
        bs.Button("Footer")

app.run()
