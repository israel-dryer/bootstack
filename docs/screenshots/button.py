import bootstack as bs

with bs.App(title="Button", padding=20, gap=14) as app:

    bs.Label("Accent Colors", font="heading-sm[bold]")
    with bs.HStack(gap=8):
        for accent in ("default", "primary", "secondary", "success", "warning", "danger"):
            bs.Button(accent.title(), accent=accent)

    bs.Label("Style Variants", font="heading-sm[bold]")
    with bs.HStack(gap=8):
        bs.Button("Solid",   accent="primary", variant="solid")
        bs.Button("Outline", accent="primary", variant="outline")
        bs.Button("Ghost",   accent="primary", variant="ghost")

    bs.Label("Icons", font="heading-sm[bold]")
    with bs.HStack(gap=8):
        bs.Button("Save",   icon="save")
        bs.Button("Delete", icon="trash",    accent="danger")
        bs.Button("Export", icon="download", accent="secondary", variant="outline")

    bs.Label("Icon Position", font="heading-sm[bold]")
    with bs.HStack(gap=8):
        bs.Button("Left",   icon="arrow-left",  icon_position="left")
        bs.Button("Right",  icon="arrow-right", icon_position="right")
        bs.Button("Top",    icon="arrow-up",    icon_position="top")

    bs.Label("Icon Only", font="heading-sm[bold]")
    with bs.HStack(gap=4):
        bs.Button(icon="plus-lg",  icon_only=True, accent="success")
        bs.Button(icon="dash-lg",  icon_only=True, accent="danger")
        bs.Button(icon="pencil",   icon_only=True, accent="secondary", variant="outline")
        bs.Button(icon="trash",    icon_only=True, accent="danger",    variant="outline")

    bs.Label("Compact Density", font="heading-sm[bold]")
    with bs.HStack(gap=4):
        bs.Button("Cut",   icon="scissors",  density="compact")
        bs.Button("Copy",  icon="copy",      density="compact")
        bs.Button("Paste", icon="clipboard", density="compact")

    bs.Label("Disabled", font="heading-sm[bold]")
    with bs.HStack(gap=8):
        bs.Button("Disabled Solid",   accent="primary", disabled=True)
        bs.Button("Disabled Outline", accent="primary", variant="outline", disabled=True)

app.run()
