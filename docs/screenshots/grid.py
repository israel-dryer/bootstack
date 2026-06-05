import bootstack as bs


def hero():
    with bs.App(title="Grid", minsize=(720, 1), padding=20) as app:
        with bs.Grid(columns=[1, 1, 1], gap=8, sticky_items="ew", fill="x"):
            for i in range(1, 7):
                with bs.Card(padding=20):
                    bs.Label(f"Cell {i}")
    app.run()


def columns():
    with bs.App(title="Grid — Columns", minsize=(720, 1), padding=20, gap=8) as app:
        with bs.Grid(columns=[1, 1, 1], gap=8, sticky_items="ew", fill="x"):
            for label in ("Equal", "Weight", "Columns"):
                bs.Button(label)
        with bs.Grid(columns=["auto", 1], gap=8, sticky_items="ew", fill="x"):
            bs.Button("auto")
            bs.Button("weight=1 (fills remaining)")
        with bs.Grid(columns=["120px", 1, "80px"], gap=8, sticky_items="ew", fill="x"):
            bs.Button("120px")
            bs.Button("weight=1")
            bs.Button("80px")
    app.run()


def gap():
    with bs.App(title="Grid — Gap", padding=20) as app:
        with bs.HStack(gap=16, anchor_items="n"):
            with bs.Grid(columns=[1, 1], gap=8, sticky_items="ew"):
                for label in ("A", "B", "C", "D"):
                    bs.Button(label)
            with bs.Grid(columns=[1, 1], gap=(32, 8), sticky_items="ew"):
                for label in ("A", "B", "C", "D"):
                    bs.Button(label)
    app.run()


def sticky():
    with bs.App(title="Grid — Sticky", padding=20, minsize=(720, 150)) as app:
        with bs.HStack(gap=16, anchor_items="n", expand=True, fill='both', fill_items='both', expand_items=True):
            with bs.Card(padding=8, fill_items='both', expand_items=True):
                with bs.Grid(columns=[1, 1], gap=8, sticky_items="ew", height=80):
                    bs.Button("A")
                    bs.Button("B")
            with bs.Card(padding=8, fill_items='both', expand_items=True):
                with bs.Grid(columns=[1, 1], gap=8, sticky_items="", height=80):
                    bs.Button("A")
                    bs.Button("B")
            with bs.Card(padding=8, fill_items='both', expand_items=True):
                with bs.Grid(columns=[1, 1], gap=8, sticky_items="nsew", height=80):
                    bs.Button("A")
                    bs.Button("B")
    app.run()


def form():
    with bs.App(title="Grid — Form", minsize=(720, 1), padding=20) as app:
        with bs.Grid(columns=["auto", 1], gap=8, sticky_items="ew", fill="x"):
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
