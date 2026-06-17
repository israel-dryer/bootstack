import bootstack as bs


def hero():
    with bs.App(title="GroupBox", padding=20, minsize=(600, 1)) as app:
        with bs.GroupBox("Connection", padding=12, gap=8, horizontal="stretch", grow=True, horizontal_items="stretch", grow_items=True):
            with bs.Row(gap=8):
                bs.Label("Host:", font='label', width=8)
                bs.Label("localhost")
            with bs.Row(gap=8):
                bs.Label("Port:", font='label', width=8)
                bs.Label("5432")
            with bs.Row(gap=8):
                bs.Label("Status:", font='label', width=8)
                bs.Label("Connected", accent="success")
    app.run()


def accent():
    with bs.App(title="GroupBox — Accents", padding=20, minsize=(720, 150)) as app:
        with bs.Row(gap=12, grow=True, horizontal="stretch", vertical_items="stretch", grow_items=True):
            for a in ("primary", "secondary", "info", "success", "warning", "danger"):
                with bs.GroupBox(a.title(), accent=a, padding=10, gap=4):
                    bs.Label("Item one")
                    bs.Label("Item two")
    app.run()


def layout():
    with bs.App(title="GroupBox — Layout Modes", padding=20) as app:
        with bs.Row(gap=12, vertical_items="top"):
            with bs.GroupBox("Column (default)", padding=10, gap=8):
                bs.Label("First")
                bs.Label("Second")
                bs.Label("Third")
            with bs.GroupBox("Row", layout="row", padding=10, gap=12, vertical_items="center"):
                bs.Label("A")
                bs.Label("B")
                bs.Label("C")
            with bs.GroupBox("Grid", layout="grid", columns=[1, 1], padding=10, gap=8, horizontal_items="stretch"):
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
