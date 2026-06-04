import bootstack as bs


def hero():
    with bs.App(title="Badge", minsize=(720, 1), padding=20, gap=8) as app:
        with bs.HStack(gap=8):
            bs.Badge("Square",  accent="primary")
            bs.Badge("Pill",    accent="primary", variant="pill")
            bs.Badge("99+",     accent="danger",  variant="pill")
            bs.Badge("New",     accent="success", variant="pill")
            bs.Badge("Beta",    accent="warning", variant="pill")
    app.run()


def accents():
    with bs.App(title="Badge — Accents", minsize=(720, 1), padding=20, gap=8) as app:
        with bs.HStack(gap=8):
            for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
                bs.Badge(accent.title(), accent=accent)
        with bs.HStack(gap=8):
            for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
                bs.Badge(accent.title(), accent=accent, variant="pill")
    app.run()


def context():
    with bs.App(title="Badge — In Context", minsize=(720, 1), padding=20, gap=8) as app:
        with bs.HStack(gap=8, anchor_items="center"):
            bs.Label("Inbox", font="heading-md")
            bs.Badge("12", accent="primary", variant="pill")
        with bs.HStack(gap=8, anchor_items="center"):
            bs.Label("Alerts", font="heading-md")
            bs.Badge("3", accent="danger", variant="pill")
        with bs.HStack(gap=8, anchor_items="center"):
            bs.Label("Run-A15")
            bs.Badge("Complete",   accent="success", variant="pill")
        with bs.HStack(gap=8, anchor_items="center"):
            bs.Label("Run-A14")
            bs.Badge("2 warnings", accent="warning")
            bs.Badge("Fail",       accent="danger",  variant="pill")
    app.run()


SCENES = {
    "hero":    hero,
    "accents": accents,
    "context": context,
}