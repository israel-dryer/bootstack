"""Tooltip demo — hover any button to see its tooltip."""
import bootstack as bs

with bs.App(title="Tooltip", size=(660, 440), padding=20, gap=14) as app:

    bs.Label("Basic", font="heading-md")
    with bs.HStack(gap=8):
        b1 = bs.Button("Hover me")
        bs.Tooltip(b1, "This is a helpful tooltip.")

        b2 = bs.Button("Instant")
        bs.Tooltip(b2, "Appears immediately.", delay=0)

        b3 = bs.Button("Slow (1 s)")
        bs.Tooltip(b3, "Appears after a 1-second delay.", delay=1000)

    bs.Label("Accent colors", font="heading-md")
    with bs.HStack(gap=8):
        b4 = bs.Button("Default")
        bs.Tooltip(b4, "Default accent")

        b5 = bs.Button("Primary")
        bs.Tooltip(b5, "Primary accent", accent="primary")

        b6 = bs.Button("Info")
        bs.Tooltip(b6, "Info accent", accent="info")

        b7 = bs.Button("Success")
        bs.Tooltip(b7, "Success accent", accent="success")

        b8 = bs.Button("Warning")
        bs.Tooltip(b8, "Warning accent", accent="warning")

        b9 = bs.Button("Danger")
        bs.Tooltip(b9, "Danger accent", accent="danger")

    bs.Label("Anchored positioning", font="heading-md")
    with bs.HStack(gap=8):
        b10 = bs.Button("Above")
        bs.Tooltip(b10, "Anchored above the button",
                   anchor_point="n", window_point="s")

        b11 = bs.Button("Below")
        bs.Tooltip(b11, "Anchored below the button",
                   anchor_point="s", window_point="n")

        b12 = bs.Button("Right")
        bs.Tooltip(b12, "Anchored to the right",
                   anchor_point="e", window_point="w")

        b13 = bs.Button("Left")
        bs.Tooltip(b13, "Anchored to the left",
                   anchor_point="w", window_point="e")

    bs.Label("Text wrapping and alignment", font="heading-md")
    with bs.HStack(gap=8):
        b14 = bs.Button("Wrapped text")
        bs.Tooltip(
            b14,
            "This tooltip has a longer explanation that wraps across multiple lines.",
            wrap_width=200,
        )

        b15 = bs.Button("Center aligned")
        bs.Tooltip(
            b15,
            "Centered\ntooltip text",
            justify="center",
            wrap_width=180,
        )

app.run()
