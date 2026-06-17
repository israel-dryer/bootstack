"""Row — full feature demo.

Demonstrates gap, horizontal_items (group arrangement), vertical_items
(cross-axis alignment), grow / weights (sharing width), and Spacer.

Run with:
    python docs/examples/row.py
"""

import bootstack as bs

with bs.App(title="Row Demo", minsize=(720, 1), padding=20, gap=16) as app:

    # Gap
    bs.Label("gap", font="heading-sm")
    with bs.Row(gap=16):
        with bs.Column(gap=4):
            bs.Label("gap=4", font="caption")
            with bs.Row(show_border=True, gap=4, padding=8):
                [bs.Button(lbl) for lbl in ("A", "B", "C")]
        with bs.Column(gap=4):
            bs.Label("gap=16", font="caption")
            with bs.Row(show_border=True, gap=16, padding=8):
                [bs.Button(lbl) for lbl in ("A", "B", "C")]

    # horizontal_items — arrange the whole group along the row
    bs.Label("horizontal_items", font="heading-sm")
    for arrangement in ("left", "center", "right", "space-between"):
        bs.Label(f"horizontal_items={arrangement!r}", font="caption")
        with bs.Row(horizontal_items=arrangement, show_border=True, padding=8,
                    horizontal="stretch"):
            [bs.Button(lbl) for lbl in ("One", "Two", "Three")]

    # vertical_items — cross-axis alignment of mixed-height children
    bs.Label("vertical_items", font="heading-sm")
    with bs.Row(gap=16, horizontal="stretch"):
        for alignment in ("top", "center", "bottom"):
            with bs.Column(gap=4, grow=True):
                bs.Label(f"={alignment!r}", font="caption")
                with bs.Row(vertical_items=alignment, show_border=True,
                            padding=8, height=90, gap=8, horizontal="stretch"):
                    bs.Button("A")
                    bs.Label("tall\nlabel")

    # grow — let a child claim and fill leftover width
    bs.Label("grow", font="heading-sm")
    with bs.Row(gap=8, show_border=True, padding=8, vertical_items="center",
                horizontal="stretch"):
        bs.Label("Search:")
        bs.TextField(grow=True)        # claims the leftover width
        bs.Button("Go", accent="primary")

    # weights — share width in a fixed ratio (here 1 : 2 : 1)
    bs.Label("weights=[1, 2, 1]", font="heading-sm")
    with bs.Row(gap=8, weights=[1, 2, 1], show_border=True, padding=8,
                horizontal="stretch"):
        [bs.Button(lbl) for lbl in ("1", "2", "1")]

    # Spacer — a local break that pushes a cluster aside (no nesting)
    bs.Label("Spacer", font="heading-sm")
    with bs.Row(gap=4, show_border=True, padding=8, horizontal="stretch"):
        bs.Button("New")
        bs.Button("Open")
        bs.Spacer()
        bs.Button("Settings")
        bs.Button("Profile")

app.run()
