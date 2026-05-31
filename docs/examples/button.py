"""Button — full feature demo.

Demonstrates accent colors, style variants, icons, icon positions,
icon-only, custom image, uniform width, reactive text, compact density,
and disabled states.

Run with:
    python docs/examples/button.py
"""

import bootstack as bs

with bs.App(title="Button Demo", padding=20, gap=16) as app:

    # Accent colors
    bs.Label("Accent Colors", font="heading-sm[bold]")
    with bs.HStack(gap=8):
        for accent in ("default", "primary", "secondary", "info", "success", "warning", "danger"):
            bs.Button(accent.title(), accent=accent)

    # Style variants
    bs.Label("Style Variants", font="heading-sm[bold]")
    with bs.HStack(gap=8):
        bs.Button("Solid",   accent="primary", variant="solid")
        bs.Button("Outline", accent="primary", variant="outline")
        bs.Button("Ghost",   accent="primary", variant="ghost")

    # Icons
    bs.Label("Icons", font="heading-sm[bold]")
    with bs.HStack(gap=8):
        bs.Button("Save",   icon="save")
        bs.Button("Delete", icon="trash",    accent="danger")
        bs.Button("Export", icon="download", accent="secondary", variant="outline")

    # Icon position
    bs.Label("Icon Position", font="heading-sm[bold]")
    with bs.HStack(gap=8):
        bs.Button("Left",   icon="arrow-left",  icon_position="left")
        bs.Button("Right",  icon="arrow-right", icon_position="right")
        bs.Button("Top",    icon="arrow-up",    icon_position="top")
        bs.Button("Bottom", icon="arrow-down",  icon_position="bottom")

    # Icon-only
    bs.Label("Icon Only", font="heading-sm[bold]")
    with bs.HStack(gap=4):
        bs.Button(icon="plus-lg",  icon_only=True, accent="success")
        bs.Button(icon="dash-lg",  icon_only=True, accent="danger")
        bs.Button(icon="pencil",   icon_only=True, accent="secondary", variant="outline")
        bs.Button(icon="trash",    icon_only=True, accent="danger",    variant="outline")

    # Uniform width
    bs.Label("Uniform Width", font="heading-sm[bold]")
    with bs.HStack(gap=8):
        bs.Button("Save",   accent="primary", width=10)
        bs.Button("Cancel",                  width=10)
        bs.Button("Reset",  accent="danger",  width=10)

    # Reactive text via Signal
    bs.Label("Reactive Text", font="heading-sm[bold]")
    with bs.HStack(gap=8, anchor_items="center"):
        running  = bs.Signal(False)
        btn_text = bs.Signal("Start")
        running.subscribe(lambda v: btn_text.set("Stop" if v else "Start"))
        bs.Button(
            textsignal=btn_text,
            accent="success",
            on_click=lambda: running.set(not running.get()),
        )
        bs.Label(textsignal=btn_text, accent="secondary")

    # Compact density
    bs.Label("Compact Density", font="heading-sm[bold]")
    with bs.HStack(gap=4):
        bs.Button("Cut",    icon="scissors",  density="compact")
        bs.Button("Copy",   icon="copy",      density="compact")
        bs.Button("Paste",  icon="clipboard", density="compact")

    # Disabled
    bs.Label("Disabled", font="heading-sm[bold]")
    with bs.HStack(gap=8):
        bs.Button("Disabled Solid",   accent="primary", disabled=True)
        bs.Button("Disabled Outline", accent="primary", variant="outline", disabled=True)

app.run()
