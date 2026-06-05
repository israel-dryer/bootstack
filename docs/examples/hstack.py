"""HStack — full feature demo.

Demonstrates gap, anchor_items, and expand vs fill.

Run with:
    python docs/examples/hstack.py
"""

import bootstack as bs

with bs.App(title="HStack Demo", minsize=(720, 600), padding=20, gap=16) as app:

    # Gap
    bs.Label("gap", font="heading-sm")
    with bs.HStack(gap=16):
        with bs.VStack(gap=4):
            bs.Label("gap=8", font="caption")
            with bs.HStack(show_border=True, gap=8, padding=2):
                [bs.Button(lbl) for lbl in ("A", "B", "C")]
        with bs.VStack(gap=4):
            bs.Label("gap=16", font="caption")
            with bs.HStack(show_border=True, gap=16, padding=2):
                [bs.Button(lbl) for lbl in ("A", "B", "C")]

    # anchor_items
    bs.Label("anchor_items", font="heading-sm")
    with bs.HStack(gap=16):
        with bs.HStack(padding=8, show_border=True, height=100, width=150):
            bs.Button("anchor='n'", anchor="n", expand=True)
        with bs.HStack(padding=8, show_border=True, height=100, width=150):
            bs.Button("anchor='center'", anchor="center", expand=True)
        with bs.HStack(padding=8, show_border=True, height=100, width=150):
            bs.Button("anchor='s'", anchor="s", expand=True)

    # expand vs fill
    bs.Label("expand and fill", font="heading-sm")
    with bs.VStack(gap=12, fill="x"):

        bs.Label("Neither — all natural width", font="caption")
        with bs.HStack(gap=8, show_border=True, padding=8, fill="x", anchor_items="center"):
            bs.Label("Search:")
            bs.TextField()
            bs.Button("Go", accent="primary")

        bs.Label("expand=True only — field claims space but doesn't stretch", font="caption")
        with bs.HStack(gap=8, show_border=True, padding=8, fill="x", anchor_items="center"):
            bs.Label("Search:")
            bs.TextField(expand=True)
            bs.Button("Go", accent="primary")

        bs.Label("fill='x', expand=True — field claims and fills", font="caption")
        with bs.HStack(gap=8, show_border=True, padding=8, fill="x", anchor_items="center"):
            bs.Label("Search:")
            bs.TextField(fill="x", expand=True)
            bs.Button("Go", accent="primary")

app.run()