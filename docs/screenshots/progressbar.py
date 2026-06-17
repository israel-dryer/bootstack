import bootstack as bs


def hero():
    with bs.App(title="ProgressBar", minsize=(720, 1), padding=20, gap=8, horizontal_items="stretch") as app:
        for pct in (0, 25, 50, 75, 100):
            bs.ProgressBar(value=pct)
    app.run()


def accents():
    with bs.App(title="ProgressBar — Accents", minsize=(720, 1), padding=20, gap=8, horizontal_items="stretch") as app:
        for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
            bs.ProgressBar(value=65, accent=accent)
    app.run()


def variants():
    with bs.App(title="ProgressBar — Variants", minsize=(720, 1), padding=20, gap=16) as app:
        with bs.Column(gap=6, horizontal="stretch", horizontal_items="stretch"):
            bs.Label("Thin", font="heading-sm")
            bs.ProgressBar(value=40, variant="thin")
            bs.ProgressBar(value=70, accent="primary", variant="thin")
            bs.ProgressBar(value=90, accent="success", variant="thin")
        with bs.Column(gap=6):
            bs.Label("Vertical", font="heading-sm")
            with bs.Row(gap=12):
                for pct in (25, 50, 75, 100):
                    bs.ProgressBar(value=pct, orient="vertical")
    app.run()


SCENES = {
    "hero":     hero,
    "accents":  accents,
    "variants": variants,
}