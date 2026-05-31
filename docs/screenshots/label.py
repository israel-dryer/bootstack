import bootstack as bs

with bs.App(title="Label", padding=20, gap=14) as app:

    bs.Label("Font Tokens", font="heading-sm[bold]")
    with bs.VStack(gap=4):
        for token in ("heading-xl", "heading-lg", "heading-md", "heading-sm",
                      "body-lg", "body", "body-sm", "caption", "code"):
            bs.Label(token, font=token)

    bs.Label("Font Modifiers", font="heading-sm[bold]")
    with bs.HStack(gap=16):
        bs.Label("Bold",        font="body[bold]")
        bs.Label("Italic",      font="body[italic]")
        bs.Label("Bold Italic", font="body[bold][italic]")
        bs.Label("Underline",   font="body[underline]")

    bs.Label("Accent Colors", font="heading-sm[bold]")
    with bs.HStack(gap=16):
        for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
            bs.Label(accent.title(), accent=accent, font="body[bold]")

    bs.Label("With Icons", font="heading-sm[bold]")
    with bs.HStack(gap=16):
        bs.Label("Home",    icon="house")
        bs.Label("Right",   icon="gear",                 icon_position="right")
        bs.Label("Warning", icon="exclamation-triangle", accent="warning")
        bs.Label(icon="heart-fill", accent="danger")

    bs.Label("Text Wrapping", font="heading-sm[bold]")
    bs.Label(
        "This label wraps automatically once it exceeds the specified "
        "wrap_width in pixels. Useful for descriptive text and help copy.",
        wrap_width=400,
        accent="secondary",
    )

app.run()
