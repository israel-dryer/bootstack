import bootstack as bs

with bs.App(title="RangeSlider", padding=20, gap=14, minsize=(500, 1)) as app:

    bs.Label("Basic", font="heading-sm[bold]")
    bs.RangeSlider(20, 80, fill="x")

    bs.Label("Value Badges + Tick Marks", font="heading-sm[bold]")
    bs.RangeSlider(20, 80, show_value=True, tick_step=20, minor_ticks=4, fill="x")

    bs.Label("Accent Colors", font="heading-sm[bold]")
    bs.RangeSlider(20, 80, accent="primary",   fill="x")
    bs.RangeSlider(20, 80, accent="secondary", fill="x")
    bs.RangeSlider(20, 80, accent="success",   fill="x")
    bs.RangeSlider(20, 80, accent="warning",   fill="x")
    bs.RangeSlider(20, 80, accent="danger",    fill="x")

    bs.Label("Disabled", font="heading-sm[bold]")
    bs.RangeSlider(20, 80, disabled=True, fill="x")

app.run()
