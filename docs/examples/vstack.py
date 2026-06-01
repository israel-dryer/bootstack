"""VStack — full feature demo.

Demonstrates gap, anchor_items, and expand vs fill.

Run with:
    python docs/examples/vstack.py
"""

import bootstack as bs

with bs.App(title="VStack Demo", size=(680, 780), padding=20, gap=16) as app:

    # Gap
    bs.Label("gap", font="heading-sm")
    with bs.Grid(columns=[1, 1], gap=(16, 0), fill="x", sticky_items="new"):
        with bs.VStack(gap=4, fill="x"):
            bs.Label("gap=8", font="caption")
            with bs.VStack(show_border=True, gap=8, padding=8, fill="x", fill_items="x"):
                for lbl in ("A", "B", "C"):
                    bs.Button(lbl)
        with bs.VStack(gap=4, fill="x"):
            bs.Label("gap=16", font="caption")
            with bs.VStack(show_border=True, gap=16, padding=8, fill="x", fill_items="x"):
                for lbl in ("A", "B", "C"):
                    bs.Button(lbl)

    # anchor_items
    bs.Label("anchor_items", font="heading-sm")
    with bs.Grid(columns=[1, 1, 1], gap=(16, 0), fill="x", sticky_items="new"):
        with bs.VStack(gap=4, fill="x"):
            bs.Label("anchor='w'", font="caption")
            with bs.VStack(padding=8, show_border=True, height=100, fill="x"):
                bs.Button("anchor='w'", anchor="w", expand=True)
        with bs.VStack(gap=4, fill="x"):
            bs.Label("anchor='center'", font="caption")
            with bs.VStack(padding=8, show_border=True, height=100, fill="x"):
                bs.Button("anchor='center'", anchor="center", expand=True)
        with bs.VStack(gap=4, fill="x"):
            bs.Label("anchor='e'", font="caption")
            with bs.VStack(padding=8, show_border=True, height=100, fill="x"):
                bs.Button("anchor='e'", anchor="e", expand=True)

    # expand and fill
    bs.Label("expand and fill", font="heading-sm")
    with bs.Grid(columns=[1, 1, 1], gap=(16, 0), fill="x", sticky_items="new"):
        with bs.VStack(gap=4, fill="x"):
            bs.Label("Neither", font="caption")
            with bs.VStack(show_border=True, padding=8, height=180, fill="x", gap=6, fill_items="x"):
                bs.Button("Header")
                bs.Button("Content")
                bs.Button("Footer")
        with bs.VStack(gap=4, fill="x"):
            bs.Label("expand=True only", font="caption")
            with bs.VStack(show_border=True, padding=8, height=180, fill="x", gap=6, fill_items="x"):
                bs.Button("Header")
                bs.Button("Content", expand=True)
                bs.Button("Footer")
        with bs.VStack(gap=4, fill="x"):
            bs.Label("fill='y', expand=True", font="caption")
            with bs.VStack(show_border=True, padding=8, height=180, fill="x", gap=6, fill_items="x"):
                bs.Button("Header")
                bs.Button("Content", fill="y", expand=True)
                bs.Button("Footer")

app.run()