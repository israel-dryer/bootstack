import bootstack as bs


def hero():
    with bs.App(title="VStack", minsize=(720, 1), padding=20) as app:
        with bs.VStack(gap=8, fill_items="x", anchor="w"):
            for i in range(1, 4):
                with bs.Card(padding=20):
                    bs.Label(f"Item {i}")
    app.run()


def gap():
    with bs.App(title="VStack — Gap", padding=20) as app:
        with bs.HStack(gap=16, anchor_items="n"):
            with bs.VStack(gap=4, show_border=True, padding=8):
                for i in range(1, 5):
                    bs.Button(f"Item {i}")
            with bs.VStack(gap=16, show_border=True, padding=8):
                for i in range(1, 5):
                    bs.Button(f"Item {i}")
    app.run()


def fill():
    with bs.App(title="VStack — Fill", minsize=(720, 1), padding=20) as app:
        with bs.VStack(gap=8, fill_items="x", fill="x"):
            bs.TextField()
            bs.Button("Submit", accent="primary")
    app.run()


def alignment():
    with bs.App(title="VStack — Alignment", padding=20) as app:
        with bs.HStack(gap=16, anchor_items="n"):
            with bs.VStack(gap=8, anchor_items="w", show_border=True, padding=8, width=180, height=120):
                bs.Button("A")
                bs.Button("B")
            with bs.VStack(gap=8, anchor_items="center", show_border=True, padding=8, width=180, height=120):
                bs.Button("A")
                bs.Button("B")
            with bs.VStack(gap=8, anchor_items="e", show_border=True, padding=8, width=180, height=120):
                bs.Button("A")
                bs.Button("B")
    app.run()


def border():
    with bs.App(title="VStack — Border", size=(720, 150), padding=20) as app:
        with bs.VStack(gap=8, show_border=True, padding=8, fill="x"):
            bs.Label("Bordered section")
            bs.Button("Action")
    app.run()


SCENES = {
    "hero":      hero,
    "gap":       gap,
    "fill":      fill,
    "alignment": alignment,
    "border":    border,
}
