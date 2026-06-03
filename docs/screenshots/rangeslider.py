import bootstack as bs


def hero():
    with bs.App(title="RangeSlider", size=(860, 200), padding=20) as app:
        bs.RangeSlider(20, 80, fill="x", margin_y=10)
        bs.RangeSlider(25, 75, tick_step=25, minor_ticks=4, show_value=True, fill="x", margin_y=10)

    app.run()


def accents():
    with bs.App(title="RangeSlider — Accents", size=(860, 220), padding=20, gap=6) as app:
        bs.RangeSlider(20, 80, accent="primary",   fill="x")
        bs.RangeSlider(20, 80, accent="secondary", fill="x")
        bs.RangeSlider(20, 80, accent="info",      fill="x")
        bs.RangeSlider(20, 80, accent="success",   fill="x")
        bs.RangeSlider(20, 80, accent="warning",   fill="x")
        bs.RangeSlider(20, 80, accent="danger",    fill="x")

    app.run()


def ticks():
    with bs.App(title="RangeSlider — Tick Marks", size=(860, 230), padding=20) as app:
        bs.RangeSlider(20, 80, tick_step=20, fill="x", margin_y=10)
        bs.RangeSlider(20, 80, tick_step=20, minor_ticks=4, show_value=True, fill="x", margin_y=10)

    app.run()


def disabled():
    with bs.App(title="RangeSlider — Disabled", size=(860, 140), padding=20) as app:
        bs.RangeSlider(20, 80, fill="x", margin_y=10)
        bs.RangeSlider(20, 80, disabled=True, fill="x", margin_y=10)

    app.run()


SCENES = {
    "hero":     hero,
    "accents":  accents,
    "ticks":    ticks,
    "disabled": disabled,
}
