import bootstack as bs

with bs.App(title="Slider", padding=20, gap=14, minsize=(500, 1)) as app:

    bs.Label("Basic", font="heading-sm[bold]")
    bs.Slider(50, fill="x")

    bs.Label("Accent Colors", font="heading-sm[bold]")
    bs.Slider(50, accent="primary",   fill="x")
    bs.Slider(50, accent="secondary", fill="x")
    bs.Slider(50, accent="info",      fill="x")
    bs.Slider(50, accent="success",   fill="x")
    bs.Slider(50, accent="warning",   fill="x")
    bs.Slider(50, accent="danger",    fill="x")

    bs.Label("Value Badge + Tick Marks", font="heading-sm[bold]")
    bs.Slider(50, show_value=True, show_minmax=True, tick_step=25, minor_ticks=4, fill="x")

    bs.Label("Disabled", font="heading-sm[bold]")
    bs.Slider(30, disabled=True, fill="x")

app.run()
