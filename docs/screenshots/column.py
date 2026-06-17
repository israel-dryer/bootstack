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
    with bs.App(title="Column — Arrange", minsize=(540, 1), padding=20) as app:
        with bs.Row(gap=16, horizontal="stretch", vertical_items="top"):
            for arrangement in ("top", "center", "bottom", "space-between"):
                with bs.Column(gap=4, grow=True):
                    bs.Label(f"={arrangement!r}", font="caption")
                    with bs.Column(vertical_items=arrangement, show_border=True,
                                   padding=8, height=140, horizontal="stretch",
                                   horizontal_items="stretch"):
                        bs.Button("Header")
                        bs.Button("Footer")
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
    "spacer":  spacer,
}
