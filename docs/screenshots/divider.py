import bootstack as bs


def hero():
    with bs.App(title="Divider", minsize=(720, 1), padding=0) as app:
        bs.Divider(margin_y=20, horizontal="stretch")
    app.run()


def accents():
    with bs.App(title="Divider — Accents", minsize=(720, 1), padding=20, gap=16, horizontal_items="stretch") as app:
        for accent in ("default", "primary", "secondary", "info", "success", "warning", "danger"):
            bs.Divider(accent=accent)
    app.run()


def thickness():
    with bs.App(title="Divider — Thickness", minsize=(720, 1), padding=20, gap=16, horizontal_items="stretch") as app:
        for t in (1, 2, 4):
            bs.Divider(accent="primary", thickness=t)
    app.run()


def vertical():
    with bs.App(title="Divider — Vertical", padding=20) as app:
        with bs.Row(gap=12, vertical_items="center", horizontal="stretch"):
            bs.Label("Home")
            bs.Divider(orient="vertical", length=16)
            bs.Label("Products")
            bs.Divider(orient="vertical", length=16)
            bs.Label("About")
            bs.Divider(orient="vertical", length=16)
            bs.Label("Contact")
    app.run()


SCENES = {
    "hero":      hero,
    "accents":   accents,
    "thickness": thickness,
    "vertical":  vertical,
}
