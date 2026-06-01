"""Grid — full feature demo.

Demonstrates column/row definitions, gap, sticky_items, and auto_flow.

Run with:
    python docs/examples/grid.py
"""

import bootstack as bs

with bs.App(title="Grid Demo", size=(720, 820), padding=20, gap=16) as app:

    # Column definitions
    bs.Label("Column definitions", font="heading-sm")
    with bs.Grid(columns=[1, 1, 1], gap=8, show_border=True, padding=8,
                 sticky_items="ew", fill="x"):
        for label in ("Equal", "weight", "columns"):
            bs.Button(label)

    with bs.Grid(columns=["auto", 1, "auto"], gap=8, show_border=True, padding=8,
                 sticky_items="ew", fill="x"):
        bs.Button("auto")
        bs.Button("weight=1  (fills remaining)")
        bs.Button("auto")

    with bs.Grid(columns=["120px", 1, "80px"], gap=8, show_border=True, padding=8,
                 sticky_items="ew", fill="x"):
        bs.Button("120px")
        bs.Button("weight=1")
        bs.Button("80px")

    # Gap
    bs.Label("Gap", font="heading-sm")
    with bs.Grid(columns=[1, 1], gap=(32, 16), fill="x", sticky_items="new"):
        with bs.VStack(gap=4):
            bs.Label("gap=8 (uniform)", font="caption")
            with bs.Grid(columns=[1, 1], gap=8, show_border=True, padding=8,
                         sticky_items="ew", fill="x"):
                for label in ("A", "B", "C", "D"):
                    bs.Button(label)
        with bs.VStack(gap=4):
            bs.Label("gap=(32, 8) (col, row)", font="caption")
            with bs.Grid(columns=[1, 1], gap=(32, 8), show_border=True, padding=8,
                         sticky_items="ew", fill="x"):
                for label in ("A", "B", "C", "D"):
                    bs.Button(label)

    # sticky_items
    bs.Label("sticky_items", font="heading-sm")
    with bs.Grid(columns=[1, 1, 1], gap=(16, 0), fill="x", sticky_items="new"):
        with bs.VStack(gap=4):
            bs.Label("sticky='ew'", font="caption")
            with bs.Grid(columns=[1, 1], gap=8, show_border=True, padding=8,
                         sticky_items="ew", height=80, fill="x"):
                bs.Button("A")
                bs.Button("B")
        with bs.VStack(gap=4):
            bs.Label("sticky='' (centered)", font="caption")
            with bs.Grid(columns=[1, 1], gap=8, show_border=True, padding=8,
                         sticky_items="", height=80, fill="x"):
                bs.Button("A")
                bs.Button("B")
        with bs.VStack(gap=4):
            bs.Label("sticky='nsew'", font="caption")
            with bs.Grid(columns=[1, 1], gap=8, show_border=True, padding=8,
                         sticky_items="nsew", height=80, fill="x"):
                bs.Button("A")
                bs.Button("B")

    # In context — key/value form layout
    bs.Label("In context", font="heading-sm")
    with bs.Grid(columns=["auto", 1], gap=8, show_border=True, padding=12,
                 sticky_items="ew", fill="x"):
        bs.Label("First name")
        bs.TextField()
        bs.Label("Last name")
        bs.TextField()
        bs.Label("Email")
        bs.TextField()
        bs.Label("Role")
        bs.TextField()

app.run()