import bootstack as bs


def hero():
    with bs.App(title="Divider", minsize=(560, 1), padding=20) as app:
        with bs.Column(gap=2, horizontal="stretch", horizontal_items="stretch"):
            bs.Label("Account", font="heading-md")
            bs.Label("Manage your profile and password.")
            bs.Divider(margin_y=14)
            bs.Label("Notifications", font="heading-md")
            bs.Label("Choose what you get emailed about.")
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
