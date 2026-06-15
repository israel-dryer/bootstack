import bootstack as bs

with bs.App(title="Semantic Styling", size=(600, 360)) as app:
    with bs.VStack(padding=20, gap=16):
        bs.Label("Accent Colors", font="heading-md[bold]")
        with bs.HStack(gap=8):
            for accent in ("primary", "secondary", "success", "info", "warning", "danger"):
                bs.Button(accent.title(), accent=accent)

        bs.Label("Style Variants", font="heading-md[bold]")
        with bs.HStack(gap=8):
            for variant in ("solid", "outline", "ghost"):
                bs.Button(variant.title(), accent="primary", variant=variant)

        bs.Label("Typography", font="heading-md[bold]")
        bs.Label("Heading Large", font="heading-lg")
        bs.Label("Body text", font="body")
        bs.Label("Caption / muted", font="caption", accent="secondary")

app.run()
