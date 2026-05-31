import bootstack as bs

with bs.App(title="Badge", padding=20, gap=14) as app:

    bs.Label("Variants", font="heading-sm[bold]")
    with bs.HStack(gap=8):
        bs.Badge("Square", accent="primary")
        bs.Badge("Pill",   accent="primary", variant="pill")
        bs.Badge("99+",    accent="danger",  variant="pill")
        bs.Badge("New",    accent="success", variant="pill")
        bs.Badge("Beta",   accent="warning", variant="pill")

    bs.Label("Accent Colors — Square", font="heading-sm[bold]")
    with bs.HStack(gap=8):
        for accent in ("primary", "secondary", "success", "warning", "danger"):
            bs.Badge(accent.title(), accent=accent)

    bs.Label("Accent Colors — Pill", font="heading-sm[bold]")
    with bs.HStack(gap=8):
        for accent in ("primary", "secondary", "success", "warning", "danger"):
            bs.Badge(accent.title(), accent=accent, variant="pill")

    bs.Label("In Context", font="heading-sm[bold]")
    with bs.VStack(gap=8):
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
