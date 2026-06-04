import bootstack as bs


def hero():
    with bs.App(title="GroupBox", padding=20, minsize=(600, 1)) as app:
        with bs.GroupBox("Connection", padding=12, gap=8, fill='x', expand=True, fill_items='x', expand_items=True):
            with bs.HStack(gap=8):
                bs.Label("Host:", font='label', width=8)
                bs.Label("localhost")
            with bs.HStack(gap=8):
                bs.Label("Port:", font='label', width=8)
                bs.Label("5432")
            with bs.HStack(gap=8):
                bs.Label("Status:", font='label', width=8)
                bs.Label("Connected", accent="success")
    app.run()


def accent():
    with bs.App(title="GroupBox — Accents", padding=20, minsize=(720, 150)) as app:
        with bs.HStack(gap=12, anchor_items="n", fill='both', expand=True, fill_items='both', expand_items=True):
            for a in ("primary", "secondary", "info", "success", "warning", "danger"):
                with bs.GroupBox(a.title(), accent=a, padding=10, gap=4):
                    bs.Label("Item one")
                    bs.Label("Item two")
    app.run()


def layout():
    with bs.App(title="GroupBox — Layout Modes", padding=20) as app:
        with bs.HStack(gap=12, anchor_items="n"):
            with bs.GroupBox("VStack (default)", padding=10, gap=8):
                bs.Label("First")
                bs.Label("Second")
                bs.Label("Third")
            with bs.GroupBox("HStack", layout="hstack", padding=10, gap=12, anchor_items="center"):
                bs.Label("A")
                bs.Label("B")
                bs.Label("C")
            with bs.GroupBox("Grid", layout="grid", columns=[1, 1], padding=10, gap=8, sticky_items="ew"):
                bs.Label("Name:")
                bs.Label("Ada Lovelace")
                bs.Label("Role:")
                bs.Label("Engineer")
    app.run()


SCENES = {
    "hero":   hero,
    "accent": accent,
    "layout": layout,
}
