import bootstack as bs


def hero():
    with bs.App(title="RangeSlider", minsize=(720, 1), padding=20) as app:
        bs.RangeSlider(20, 80, horizontal="stretch", margin_y=10)
        bs.RangeSlider(25, 75, tick_step=25, minor_ticks=4, show_value=True, horizontal="stretch", margin_y=10)

    app.run()


def accents():
    with bs.App(title="RangeSlider — Accents", minsize=(720, 1), padding=20, gap=6) as app:
        bs.RangeSlider(20, 80, accent="primary",   horizontal="stretch")
        bs.RangeSlider(20, 80, accent="secondary", horizontal="stretch")
        bs.RangeSlider(20, 80, accent="info",      horizontal="stretch")
        bs.RangeSlider(20, 80, accent="success",   horizontal="stretch")
        bs.RangeSlider(20, 80, accent="warning",   horizontal="stretch")
        bs.RangeSlider(20, 80, accent="danger",    horizontal="stretch")

    app.run()


def value():
    with bs.App(title="RangeSlider — Value Badges", minsize=(720, 1), padding=20) as app:
        bs.RangeSlider(20, 80, show_value=True, horizontal="stretch", margin_y=10)

    app.run()


def ticks():
    with bs.App(title="RangeSlider — Tick Marks", minsize=(720, 1), padding=20) as app:
        bs.RangeSlider(20, 80, tick_step=20, horizontal="stretch", margin_y=10)
        bs.RangeSlider(20, 80, tick_step=20, minor_ticks=4, horizontal="stretch", margin_y=10)

    app.run()


def disabled():
    with bs.App(title="RangeSlider — Disabled", minsize=(720, 1), padding=20) as app:
        bs.RangeSlider(20, 80, horizontal="stretch", margin_y=10)
        bs.RangeSlider(20, 80, disabled=True, horizontal="stretch", margin_y=10)

    app.run()


SCENES = {
    "hero":     hero,
    "accents":  accents,
    "value":    value,
    "ticks":    ticks,
    "disabled": disabled,
}