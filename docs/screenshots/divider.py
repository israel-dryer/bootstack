import bootstack as bs


def hero():
    with bs.App(title="Separator", minsize=(720, 1), padding=0) as app:
        bs.Separator(margin_y=20, fill="x")
    app.run()


def accents():
    with bs.App(title="Separator — Accents", minsize=(720, 1), padding=20, gap=16, fill_items="x") as app:
        for accent in ("default", "primary", "secondary", "info", "success", "warning", "danger"):
            bs.Separator(accent=accent)
    app.run()


def thickness():
    with bs.App(title="Separator — Thickness", minsize=(720, 1), padding=20, gap=16, fill_items="x") as app:
        for t in (1, 2, 4):
            bs.Separator(accent="primary", thickness=t)
    app.run()


def vertical():
    with bs.App(title="Separator — Vertical", padding=20) as app:
        with bs.HStack(gap=12, anchor_items="center", fill="x"):
            bs.Label("Home")
            bs.Separator(orient="vertical", length=16)
            bs.Label("Products")
            bs.Separator(orient="vertical", length=16)
            bs.Label("About")
            bs.Separator(orient="vertical", length=16)
            bs.Label("Contact")
    app.run()


SCENES = {
    "hero":      hero,
    "accents":   accents,
    "thickness": thickness,
    "vertical":  vertical,
}
