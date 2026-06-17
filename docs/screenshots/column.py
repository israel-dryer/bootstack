import bootstack as bs


def hero():
    with bs.App(title="Column", minsize=(360, 1), padding=20) as app:
        with bs.Column(gap=8, horizontal="stretch", horizontal_items="stretch"):
            for i in range(1, 4):
                with bs.Card(padding=20):
                    bs.Label(f"Item {i}")
    app.run()


def gap():
    with bs.App(title="Column — Gap", minsize=(360, 1), padding=20) as app:
        with bs.Row(gap=16, horizontal="stretch", vertical_items="top"):
            with bs.Column(gap=4, grow=True):
                bs.Label("gap=8", font="caption")
                with bs.Column(gap=8, show_border=True, padding=8,
                               horizontal="stretch", horizontal_items="stretch"):
                    for lbl in ("A", "B", "C"):
                        bs.Button(lbl)
            with bs.Column(gap=4, grow=True):
                bs.Label("gap=24", font="caption")
                with bs.Column(gap=24, show_border=True, padding=8,
                               horizontal="stretch", horizontal_items="stretch"):
                    for lbl in ("A", "B", "C"):
                        bs.Button(lbl)
    app.run()


def align():
    with bs.App(title="Column — Align", minsize=(540, 1), padding=20) as app:
        with bs.Row(gap=16, horizontal="stretch", vertical_items="top"):
            for alignment in ("left", "center", "right", "stretch"):
                with bs.Column(gap=4, grow=True):
                    bs.Label(f"={alignment!r}", font="caption")
                    with bs.Column(horizontal_items=alignment, show_border=True,
                                   padding=8, horizontal="stretch"):
                        bs.Button("Save")
    app.run()


def arrange():
    modes = ("top", "center", "bottom", "space-between", "space-around", "space-evenly")
    with bs.App(title="Column — Arrange", minsize=(820, 1), padding=20) as app:
        with bs.Row(gap=12, horizontal="stretch", vertical_items="top", grow_items=True):
            for mode in modes:
                with bs.Column(gap=4):
                    bs.Label(f"={mode!r}", font="caption")
                    with bs.Column(vertical_items=mode, show_border=True,
                                   padding=8, height=150, horizontal="stretch",
                                   horizontal_items="stretch"):
                        bs.Button("Header")
                        bs.Button("Footer")
    app.run()


def weights():
    with bs.App(title="Column — Weights", minsize=(360, 1), padding=20, gap=4) as app:
        bs.Label("weights=[1, 2, 1] — the middle child is twice as tall", font="caption")
        with bs.Column(gap=8, weights=[1, 2, 1], height=220, show_border=True,
                       padding=8, horizontal="stretch", horizontal_items="stretch"):
            bs.Button("One")
            bs.Button("Two")
            bs.Button("Three")
    app.run()


def self_placement():
    with bs.App(title="Column — Self", minsize=(540, 1), padding=20) as app:
        with bs.Row(gap=12, horizontal="stretch", vertical_items="stretch", height=160):
            with bs.Column(gap=8, width=180, show_border=True, padding=8,
                           horizontal_items="stretch"):
                bs.Label("width=180", font="caption")
                bs.Button("Inbox")
                bs.Button("Drafts")
            with bs.Column(gap=8, grow=True, show_border=True, padding=8,
                           horizontal_items="stretch"):
                bs.Label('grow=True — claims the leftover width', font="caption")
                bs.Label("Content", font="heading-md")
    app.run()


def grow():
    with bs.App(title="Column — Grow", minsize=(360, 1), padding=20) as app:
        with bs.Column(gap=6, show_border=True, padding=8, height=160,
                       horizontal="stretch", horizontal_items="stretch"):
            bs.Button("Header")
            bs.Button("Content", grow=True)
            bs.Button("Footer")
    app.run()


def spacer():
    with bs.App(title="Column — Spacer", minsize=(360, 1), padding=20) as app:
        with bs.Column(gap=6, show_border=True, padding=8, height=160,
                       horizontal="stretch", horizontal_items="stretch"):
            bs.Button("Header")
            bs.Spacer()
            bs.Button("Footer")
    app.run()


SCENES = {
    "hero":    hero,
    "gap":     gap,
    "align":   align,
    "arrange": arrange,
    "grow":    grow,
    "weights": weights,
    "self":    self_placement,
    "spacer":  spacer,
}
