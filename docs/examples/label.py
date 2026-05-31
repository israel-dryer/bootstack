"""Label — full feature demo.

Demonstrates font tokens, modifiers, accent colors, icons, icon position,
text wrapping, and reactive text via Signal.

Run with:
    python docs/examples/label.py
"""

import bootstack as bs

with bs.App(title="Label Demo", padding=20, gap=16) as app:

    # Font tokens
    bs.Label("Font Tokens", font="heading-sm[bold]")
    with bs.VStack(gap=4):
        for token in ("heading-xl", "heading-lg", "heading-md", "heading-sm",
                      "body-lg", "body", "body-sm", "caption", "code"):
            bs.Label(token, font=token)

    # Font modifiers
    bs.Label("Font Modifiers", font="heading-sm[bold]")
    with bs.HStack(gap=16):
        bs.Label("Bold",        font="body[bold]")
        bs.Label("Italic",      font="body[italic]")
        bs.Label("Bold Italic", font="body[bold][italic]")
        bs.Label("Underline",   font="body[underline]")

    # Accent colors
    bs.Label("Accent Colors", font="heading-sm[bold]")
    with bs.HStack(gap=16):
        for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
            bs.Label(accent.title(), accent=accent, font="body[bold]")

    # Icons
    bs.Label("With Icons", font="heading-sm[bold]")
    with bs.HStack(gap=16):
        bs.Label("Home",    icon="house")
        bs.Label("Right",   icon="gear",                 icon_position="right")
        bs.Label("Warning", icon="exclamation-triangle", accent="warning")
        bs.Label(icon="heart-fill", accent="danger")

    # Text wrapping
    bs.Label("Text Wrapping", font="heading-sm[bold]")
    bs.Label(
        "This label wraps automatically once it exceeds the specified "
        "wrap_width in pixels. Useful for descriptive text and help copy.",
        wrap_width=400,
        accent="secondary",
    )

    # Reactive text
    bs.Label("Reactive Text", font="heading-sm[bold]")
    with bs.HStack(gap=12, anchor_items="center"):
        count      = bs.Signal(0)
        count_text = bs.Signal("Count: 0")
        count.subscribe(lambda v: count_text.set(f"Count: {v}"))
        bs.Label(textsignal=count_text, font="heading-md[bold]", accent="primary")
        bs.Button("+1", accent="primary",
                  on_click=lambda: count.set(count.get() + 1))

app.run()
