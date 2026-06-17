"""Grid — full feature demo.

Demonstrates column/row definitions, gap, in-cell alignment, and auto_flow.

Run with:
    python docs/examples/grid.py
"""

import bootstack as bs

with bs.App(title="Grid Demo", size=(720, 820), padding=20, gap=16) as app:

    # Column definitions
    bs.Label("Column definitions", font="heading-sm")
    with bs.Grid(columns=[1, 1, 1], gap=8, show_border=True, padding=8,
                 vertical_items="center", horizontal="stretch"):
        for label in ("Equal", "weight", "columns"):
            bs.Button(label)

    with bs.Grid(columns=["auto", 1, "auto"], gap=8, show_border=True, padding=8,
                 vertical_items="center", horizontal="stretch"):
        bs.Button("auto")
        bs.Button("weight=1  (fills remaining)")
        bs.Button("auto")

    with bs.Grid(columns=["120px", 1, "80px"], gap=8, show_border=True, padding=8,
                 vertical_items="center", horizontal="stretch"):
        bs.Button("120px")
        bs.Button("weight=1")
        bs.Button("80px")

    # Gap
    bs.Label("Gap", font="heading-sm")
    with bs.Grid(columns=[1, 1], gap=(32, 16), horizontal="stretch", vertical_items="top"):
        with bs.Column(gap=4):
            bs.Label("gap=8 (uniform)", font="caption")
            with bs.Grid(columns=[1, 1], gap=8, show_border=True, padding=8,
                         vertical_items="center", horizontal="stretch"):
                for label in ("A", "B", "C", "D"):
                    bs.Button(label)
        with bs.Column(gap=4):
            bs.Label("gap=(32, 8) (col, row)", font="caption")
            with bs.Grid(columns=[1, 1], gap=(32, 8), show_border=True, padding=8,
                         vertical_items="center", horizontal="stretch"):
                for label in ("A", "B", "C", "D"):
                    bs.Button(label)

    # In-cell alignment
    bs.Label("In-cell alignment", font="heading-sm")
    with bs.Grid(columns=[1, 1, 1], gap=(16, 0), horizontal="stretch", vertical_items="top"):
        with bs.Column(gap=4):
            bs.Label("vertical_items='center'", font="caption")
            with bs.Grid(columns=[1, 1], gap=8, show_border=True, padding=8,
                         vertical_items="center", height=80, horizontal="stretch"):
                bs.Button("A")
                bs.Button("B")
        with bs.Column(gap=4):
            bs.Label("horizontal_items='center'", font="caption")
            with bs.Grid(columns=[1, 1], gap=8, show_border=True, padding=8,
                         horizontal_items="center", vertical_items="center", height=80, horizontal="stretch"):
                bs.Button("A")
                bs.Button("B")
        with bs.Column(gap=4):
            bs.Label("stretch (default)", font="caption")
            with bs.Grid(columns=[1, 1], gap=8, show_border=True, padding=8,
                         height=80, horizontal="stretch"):
                bs.Button("A")
                bs.Button("B")

    # In context — key/value form layout
    bs.Label("In context", font="heading-sm")
    with bs.Grid(columns=["auto", 1], gap=8, show_border=True, padding=12,
                 vertical_items="center", horizontal="stretch"):
        bs.Label("First name")
        bs.TextField()
        bs.Label("Last name")
        bs.TextField()
        bs.Label("Email")
        bs.TextField()
        bs.Label("Role")
        bs.TextField()

app.run()