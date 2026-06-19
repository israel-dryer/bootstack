import bootstack as bs


def hero():
    with bs.App(title="Slider", minsize=(720, 1), padding=20) as app:
        bs.Slider(60, horizontal="stretch", margin_y=10)
        bs.Slider(35, tick_step=25, minor_ticks=4, show_value=True, show_minmax=True, horizontal="stretch", margin_y=10)

    app.run()


def accents():
    with bs.App(title="Slider — Accents", minsize=(720, 1), padding=20, gap=6) as app:
        bs.Slider(50, accent="primary",   horizontal="stretch")
        bs.Slider(50, accent="secondary", horizontal="stretch")
        bs.Slider(50, accent="info",      horizontal="stretch")
        bs.Slider(50, accent="success",   horizontal="stretch")
        bs.Slider(50, accent="warning",   horizontal="stretch")
        bs.Slider(50, accent="danger",    horizontal="stretch")

    app.run()


def value():
    with bs.App(title="Slider — Value Badge", minsize=(720, 1), padding=20) as app:
        bs.Slider(50, show_value=True, horizontal="stretch", margin_y=10)

    app.run()


def minmax():
    with bs.App(title="Slider — Min/Max Labels", minsize=(720, 1), padding=20) as app:
        bs.Slider(50, show_minmax=True, horizontal="stretch", margin_y=10)

    app.run()


def ticks():
    with bs.App(title="Slider — Tick Marks", minsize=(720, 1), padding=20) as app:
        bs.Slider(50, tick_step=25, horizontal="stretch", margin_y=10)
        bs.Slider(50, tick_step=25, minor_ticks=4, horizontal="stretch", margin_y=10)
        bs.Slider(0.5, min_value=0, max_value=1, tick_step=0.25, tick_format="{:.0%}", horizontal="stretch", margin_y=10)

    app.run()


def disabled():
    with bs.App(title="Slider — Disabled", minsize=(720, 1), padding=20) as app:
        bs.Slider(60, horizontal="stretch", margin_y=10)
        bs.Slider(60, disabled=True, horizontal="stretch", margin_y=10)

    app.run()


SCENES = {
    "hero":     hero,
    "accents":  accents,
    "value":    value,
    "minmax":   minmax,
    "ticks":    ticks,
    "disabled": disabled,
}