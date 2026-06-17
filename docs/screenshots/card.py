import bootstack as bs


def hero():
    with bs.App(title="Card", padding=20) as app:
        with bs.Card(padding=16, gap=8):
            bs.Label("Project Status", font="heading-md")
            bs.Label("3 of 12 tasks completed.")
            bs.Button("View Tasks", accent="primary")
    app.run()


def accent():
    with bs.App(title="Card — Accents", padding=20, minsize=(720, 1)) as app:
        with bs.Row(gap=12):
            for a in ("primary", "secondary", "info", "success", "warning", "danger"):
                with bs.Card(accent=a, padding=24, gap=4):
                    bs.Label(a.title(), accent=a, font="heading-sm")
                    bs.Label("Card content")
    app.run()


def layout():
    with bs.App(title="Card — Layout Modes", padding=20) as app:
        with bs.Row(gap=12, vertical_items="top"):
            with bs.Card(padding=12, gap=8):
                bs.Label("Column (default)", font="heading-sm")
                bs.Label("First item")
                bs.Label("Second item")
                bs.Label("Third item")
            with bs.Card(layout="row", padding=12, gap=12, vertical_items="center"):
                bs.Label("Row", font="heading-sm")
                bs.Label("A")
                bs.Label("B")
                bs.Label("C")
            with bs.Card(layout="grid", columns=[1, 1], padding=12, gap=8, horizontal_items="stretch"):
                bs.Label("Grid", font="heading-sm")
                bs.Label("2 cols")
                bs.Label("Item A")
                bs.Label("Item B")
                bs.Label("Item C")
                bs.Label("Item D")
    app.run()


def nested():
    with bs.App(title="Cards — Nested", padding=20) as app:
        with bs.Card(padding=50):
            with bs.Card(padding=50):
                with bs.Card(padding=50):
                    bs.Label("Nested Cards")



    app.run()


SCENES = {
    "hero":   hero,
    "accent": accent,
    "layout": layout,
    "nested": nested,
}
