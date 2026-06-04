import bootstack as bs


def hero():
    with bs.App(title="Label", minsize=(720, 1), padding=20, gap=4) as app:
        for token in ("heading-xl", "heading-lg", "heading-md", "heading-sm",
                      "body-lg", "body", "body-sm", "caption", "code"):
            bs.Label(token, font=token)
    app.run()


def accents():
    with bs.App(title="Label — Accents", minsize=(720, 1), padding=20) as app:
        with bs.HStack(gap=16):
            for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
                bs.Label(accent.title(), accent=accent, font="body[bold]")
    app.run()


def icons():
    with bs.App(title="Label — Icons", minsize=(720, 1), padding=20) as app:
        with bs.HStack(gap=16, anchor_items="center"):
            bs.Label("Home",    icon="house")
            bs.Label("Settings", icon="gear",                icon_position="right")
            bs.Label("Warning", icon="exclamation-triangle", accent="warning")
            bs.Label(icon="heart-fill", accent="danger")
    app.run()


SCENES = {
    "hero":    hero,
    "accents": accents,
    "icons":   icons,
}