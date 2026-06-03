import bootstack as bs


def hero():
    with bs.App(title="Slider", size=(860, 160), padding=20, gap=12) as app:
        bs.Slider(60, fill="x")
        bs.Slider(35, tick_step=25, minor_ticks=4, show_value=True, show_minmax=True, fill="x")

    app.run()


def accents():
    with bs.App(title="Slider — Accents", size=(860, 220), padding=20, gap=6) as app:
        bs.Slider(50, accent="primary",   fill="x")
        bs.Slider(50, accent="secondary", fill="x")
        bs.Slider(50, accent="info",      fill="x")
        bs.Slider(50, accent="success",   fill="x")
        bs.Slider(50, accent="warning",   fill="x")
        bs.Slider(50, accent="danger",    fill="x")

    app.run()


def ticks():
    with bs.App(title="Slider — Tick Marks", size=(860, 200), padding=20, gap=8) as app:
        bs.Slider(50, tick_step=25, fill="x")
        bs.Slider(50, tick_step=25, minor_ticks=4, fill="x")
        bs.Slider(0.5, min_value=0, max_value=1, tick_step=0.25, tick_format="{:.0%}", show_value=True, fill="x")

    app.run()


def disabled():
    with bs.App(title="Slider — Disabled", size=(860, 90), padding=20, gap=8) as app:
        bs.Slider(60, fill="x")
        bs.Slider(60, disabled=True, fill="x")

    app.run()


SCENES = {
    "hero":     hero,
    "accents":  accents,
    "ticks":    ticks,
    "disabled": disabled,
}
