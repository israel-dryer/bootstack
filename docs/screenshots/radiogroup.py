import bootstack as bs


def hero():
    with bs.App(title="RadioGroup", padding=20) as app:
        with bs.Row(horizontal="stretch"):
            bs.RadioGroup(["Small", "Medium", "Large"], value="Medium")

    app.run()


def orientation():
    with bs.App(title="RadioGroup — Orientation", padding=20) as app:
        with bs.Row(gap=32, horizontal="stretch"):
            bs.RadioGroup(["A", "B", "C"], value="A", title="Horizontal")
            bs.RadioGroup(["A", "B", "C"], value="A", title="Vertical", orient="vertical")

    app.run()


def accents():
    with bs.App(title="RadioGroup — Accents", padding=20) as app:
        with bs.Row(gap=8, horizontal="stretch"):
            for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
                bs.RadioGroup([accent.title()], accent=accent, value=accent.title())

    app.run()


def title():
    with bs.App(title="RadioGroup — Title", padding=20) as app:
        with bs.Row(gap=32, horizontal="stretch"):
            bs.RadioGroup(
                [("Small", "s"), ("Medium", "m"), ("Large", "l")],
                title="Size", value="m",
            )
            bs.RadioGroup(
                [("Light", "light"), ("Dark", "dark"), ("Auto", "auto")],
                title="Theme", orient="vertical", value="auto",
            )

    app.run()


def disabled():
    with bs.App(title="RadioGroup — Disabled", padding=20) as app:
        with bs.Row(horizontal="stretch"):
            bs.RadioGroup(["Alpha", "Beta", "Gamma"], value="Beta", disabled=True)

    app.run()


SCENES = {
    "hero":        hero,
    "orientation": orientation,
    "accents":     accents,
    "title":       title,
    "disabled":    disabled,
}