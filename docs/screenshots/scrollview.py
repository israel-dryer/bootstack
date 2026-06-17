import bootstack as bs


def hero():
    with bs.App(title="ScrollView", size=(720, 300), padding=20, gap=8) as app:
        with bs.ScrollView(scroll_direction="vertical", grow=True, horizontal="stretch"):
            for i in range(1, 30):
                with bs.Row(horizontal="stretch", padding=8):
                    bs.Label(f"Row {i:02d}")
                bs.Divider(horizontal="stretch")
    app.run()


def thin():
    with bs.App(title="ScrollView — Thin scrollbar", size=(720, 300), padding=20, gap=8) as app:
        with bs.ScrollView(scroll_direction="vertical", scrollbar_variant="thin",
                           grow=True, horizontal="stretch"):
            for i in range(1, 30):
                with bs.Row(horizontal="stretch", padding=8):
                    bs.Label(f"Row {i:02d}")
                bs.Divider(horizontal="stretch")
    app.run()


def horizontal():
    with bs.App(title="ScrollView — Horizontal", size=(720, 130), padding=20, gap=8) as app:
        with bs.ScrollView(scroll_direction="horizontal", horizontal="stretch",
                           height=60, show_border=True):
            with bs.Row(gap=8, padding=8):
                for i in range(1, 20):
                    bs.Button(f"Section {i:02d}", variant="outline")
    app.run()


SCENES = {
    "hero":       hero,
    "thin":       thin,
    "horizontal": horizontal,
}
