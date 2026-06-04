import bootstack as bs


def hero():
    with bs.App(title="HStack", minsize=(720, 1), padding=20) as app:
        with bs.HStack(gap=8, fill="x"):
            for i in range(1, 4):
                with bs.Card(padding=20, fill="x", expand=True):
                    bs.Label(f"Item {i}")
    app.run()


def gap():
    with bs.App(title="HStack — Gap", minsize=(720, 1), padding=20) as app:
        with bs.VStack(gap=12, fill="x"):
            with bs.HStack(gap=4, show_border=True, padding=8, fill="x"):
                for i in range(1, 4):
                    bs.Button(f"Item {i}")
            with bs.HStack(gap=24, show_border=True, padding=8, fill="x"):
                for i in range(1, 4):
                    bs.Button(f"Item {i}")
    app.run()


def alignment():
    with bs.App(title="HStack — Alignment", padding=20, minsize=(720, 1)) as app:
        with bs.HStack(gap=16, fill_items='x', expand_items=True):
            with bs.HStack(gap=8, anchor_items="n", show_border=True, padding=8, height=80, width=220):
                bs.Button("A")
                bs.Button("B")
            with bs.HStack(gap=8, anchor_items="center", show_border=True, padding=8, height=80, width=220):
                bs.Button("A")
                bs.Button("B")
            with bs.HStack(gap=8, anchor_items="s", show_border=True, padding=8, height=80, width=220):
                bs.Button("A")
                bs.Button("B")
    app.run()


def fill():
    with bs.App(title="HStack — Fill", minsize=(720, 1), padding=20) as app:
        with bs.HStack(gap=8, fill_items="y", fill="x", height=150):
            bs.Button("A")
            bs.Button("B")
            bs.Button("C")
    app.run()


def border():
    with bs.App(title="HStack — Border", minsize=(720, 1), padding=20) as app:
        with bs.HStack(gap=8, show_border=True, padding=8, fill="x"):
            bs.Button("A")
            bs.Button("B")
            bs.Button("C")
    app.run()


SCENES = {
    "hero":      hero,
    "gap":       gap,
    "alignment": alignment,
    "fill":      fill,
    "border":    border,
}
