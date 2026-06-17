import bootstack as bs


def hero():
    with bs.App(title="Grid", minsize=(720, 1), padding=20) as app:
        with bs.Grid(columns=[1, 1, 1], gap=8, horizontal_items="stretch", horizontal="stretch"):
            for i in range(1, 7):
                with bs.Card(padding=20):
                    bs.Label(f"Cell {i}")
    app.run()


def columns():
    with bs.App(title="Grid — Columns", minsize=(720, 1), padding=20, gap=8) as app:
        with bs.Grid(columns=[1, 1, 1], gap=8, horizontal_items="stretch", horizontal="stretch"):
            for label in ("Equal", "Weight", "Columns"):
                bs.Button(label)
        with bs.Grid(columns=["auto", 1], gap=8, horizontal_items="stretch", horizontal="stretch"):
            bs.Button("auto")
            bs.Button("weight=1 (fills remaining)")
        with bs.Grid(columns=["120px", 1, "80px"], gap=8, horizontal_items="stretch", horizontal="stretch"):
            bs.Button("120px")
            bs.Button("weight=1")
            bs.Button("80px")
    app.run()


def gap():
    with bs.App(title="Grid — Gap", padding=20) as app:
        with bs.Row(gap=16):
            with bs.Grid(columns=[1, 1], gap=8, horizontal_items="stretch"):
                for label in ("A", "B", "C", "D"):
                    bs.Button(label)
            with bs.Grid(columns=[1, 1], gap=(32, 8), horizontal_items="stretch"):
                for label in ("A", "B", "C", "D"):
                    bs.Button(label)
    app.run()


def sticky():
    with bs.App(title="Grid — Sticky", padding=20, gap=8, minsize=(720, 1)) as app:
        with bs.Row(gap=16, horizontal="stretch", grow_items=True, vertical_items="top"):
            with bs.Column(gap=4, horizontal_items="stretch"):
                bs.Label("vertical_items='center'", font="caption")
                with bs.Card(padding=8, horizontal_items="stretch"):
                    with bs.Grid(columns=[1, 1], rows=[1], gap=8,
                                 vertical_items="center", height=120, horizontal="stretch"):
                        bs.Button("A")
                        bs.Button("B")
            with bs.Column(gap=4, horizontal_items="stretch"):
                bs.Label("centered (both axes)", font="caption")
                with bs.Card(padding=8, horizontal_items="stretch"):
                    with bs.Grid(columns=[1, 1], rows=[1], gap=8,
                                 horizontal_items="center", vertical_items="center",
                                 height=120, horizontal="stretch"):
                        bs.Button("A")
                        bs.Button("B")
            with bs.Column(gap=4, horizontal_items="stretch"):
                bs.Label("stretch (default)", font="caption")
                with bs.Card(padding=8, horizontal_items="stretch"):
                    with bs.Grid(columns=[1, 1], rows=[1], gap=8,
                                 height=120, horizontal="stretch"):
                        bs.Button("A")
                        bs.Button("B")
    app.run()


def form():
    with bs.App(title="Grid — Form", minsize=(720, 1), padding=20) as app:
        with bs.Grid(columns=["auto", 1], gap=8, horizontal_items="stretch", horizontal="stretch"):
            bs.Label("First name")
            bs.TextField()
            bs.Label("Last name")
            bs.TextField()
            bs.Label("Email")
            bs.TextField()
            bs.Label("Role")
            bs.TextField()
    app.run()


SCENES = {
    "hero":    hero,
    "columns": columns,
    "gap":     gap,
    "sticky":  sticky,
    "form":    form,
}
