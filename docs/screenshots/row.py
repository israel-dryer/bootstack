import bootstack as bs


def hero():
    with bs.App(title="Row", minsize=(720, 1), padding=20) as app:
        with bs.Row(gap=8, horizontal="stretch", grow_items=True):
            for i in range(1, 4):
                with bs.Card(padding=20):
                    bs.Label(f"Item {i}")
    app.run()


def gap():
    with bs.App(title="Row — Gap", minsize=(720, 1), padding=20) as app:
        with bs.Column(gap=12, horizontal_items="stretch"):
            with bs.Row(gap=4, show_border=True, padding=8):
                for i in range(1, 4):
                    bs.Button(f"Item {i}")
            with bs.Row(gap=24, show_border=True, padding=8):
                for i in range(1, 4):
                    bs.Button(f"Item {i}")
    app.run()


def arrange():
    modes = ("left", "center", "right", "space-between", "space-around", "space-evenly")
    with bs.App(title="Row — Arrange", minsize=(720, 1), padding=20, gap=4) as app:
        with bs.Column(gap=10, horizontal="stretch", horizontal_items="stretch"):
            for mode in modes:
                bs.Label(f"horizontal_items={mode!r}", font="caption")
                with bs.Row(horizontal_items=mode, show_border=True, padding=8):
                    for lbl in ("One", "Two", "Three"):
                        bs.Button(lbl)
    app.run()


def weights():
    with bs.App(title="Row — Weights", minsize=(720, 1), padding=20, gap=4) as app:
        with bs.Column(gap=10, horizontal="stretch", horizontal_items="stretch"):
            bs.Label("weights=[1, 2, 1] — the middle child is twice as wide", font="caption")
            with bs.Row(gap=8, weights=[1, 2, 1], show_border=True, padding=8):
                bs.Button("One")
                bs.Button("Two")
                bs.Button("Three")
    app.run()


def self_placement():
    with bs.App(title="Row — Self", minsize=(720, 1), padding=20, gap=4) as app:
        with bs.Column(gap=10, horizontal="stretch", horizontal_items="left"):
            bs.Label("default — natural width, sits at the left", font="caption")
            with bs.Row(gap=8, show_border=True, padding=8):
                bs.Button("File")
                bs.Button("Edit")
                bs.Button("View")
            bs.Label('horizontal="stretch" — spans the parent width', font="caption")
            with bs.Row(gap=8, show_border=True, padding=8, horizontal="stretch"):
                bs.Button("File")
                bs.Button("Edit")
                bs.Button("View")
    app.run()


def align():
    with bs.App(title="Row — Align", padding=20, minsize=(720, 1)) as app:
        with bs.Row(gap=16, horizontal="stretch", grow_items=True):
            for alignment in ("top", "center", "bottom"):
                with bs.Row(vertical_items=alignment, gap=8, show_border=True,
                            padding=8, height=90):
                    bs.Button("A")
                    bs.Label("tall\nlabel")
    app.run()


def grow():
    with bs.App(title="Row — Grow", minsize=(720, 1), padding=20) as app:
        with bs.Row(gap=8, show_border=True, padding=8, vertical_items="center",
                    horizontal="stretch"):
            bs.Label("Search:")
            bs.TextField(grow=True)
            bs.Button("Go", accent="primary")
    app.run()


def spacer():
    with bs.App(title="Row — Spacer", minsize=(720, 1), padding=20) as app:
        with bs.Row(gap=4, show_border=True, padding=8, horizontal="stretch"):
            bs.Button("New")
            bs.Button("Open")
            bs.Spacer()
            bs.Button("Settings")
            bs.Button("Profile")
    app.run()


def border():
    with bs.App(title="Row — Border", minsize=(720, 1), padding=20) as app:
        with bs.Row(gap=8, show_border=True, padding=8, horizontal="stretch"):
            bs.Button("A")
            bs.Button("B")
            bs.Button("C")
    app.run()


SCENES = {
    "hero":    hero,
    "gap":     gap,
    "arrange": arrange,
    "align":   align,
    "grow":    grow,
    "weights": weights,
    "self":    self_placement,
    "spacer":  spacer,
    "border":  border,
}
