"""ToggleButton — full feature demo.

Demonstrates basic usage, accent colors, icon states, icon-only buttons,
compact density, and disabled states.

Run with:
    python docs/examples/togglebutton.py
"""

import bootstack as bs

with bs.App(title="ToggleButton Demo", padding=20, gap=16) as app:

    # Basic
    bs.Label("Basic", font="heading-sm[bold]")
    with bs.HStack(gap=8):
        bs.ToggleButton("Inactive", value=False)
        bs.ToggleButton("Active",   value=True)

    # Accent colors
    bs.Label("Accent Colors", font="heading-sm[bold]")
    with bs.HStack(gap=8):
        for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
            bs.ToggleButton(accent.title(), accent=accent, value=True)

    # Style variants
    bs.Label("Style Variants", font="heading-sm[bold]")
    with bs.HStack(gap=16):
        for variant in ("solid", "outline", "ghost"):
            with bs.VStack(gap=4):
                bs.ToggleButton(f"{variant.title()} — off", accent="primary", variant=variant, value=False)
                bs.ToggleButton(f"{variant.title()} — on",  accent="primary", variant=variant, value=True)

    # State icons
    bs.Label("State Icons", font="heading-sm[bold]")
    with bs.HStack(gap=8):
        bs.ToggleButton("Favorite",
            on_icon="star-fill", off_icon="star",
            accent="warning", value=True)
        bs.ToggleButton("Favorite",
            on_icon="star-fill", off_icon="star",
            accent="warning", value=False)
        bs.ToggleButton("Pin",
            on_icon="pin-fill", off_icon="pin",
            accent="primary", value=True)
        bs.ToggleButton("Pin",
            on_icon="pin-fill", off_icon="pin",
            accent="primary", value=False)

    # Icon only
    bs.Label("Icon Only", font="heading-sm[bold]")
    with bs.HStack(gap=8):
        bs.ToggleButton(on_icon="star-fill",  off_icon="star",   accent="warning", value=True,  icon_only=True)
        bs.ToggleButton(on_icon="star-fill",  off_icon="star",   accent="warning", value=False, icon_only=True)
        bs.ToggleButton(on_icon="pin-fill",   off_icon="pin",    accent="primary", value=True,  icon_only=True)
        bs.ToggleButton(on_icon="heart-fill", off_icon="heart",  accent="danger",  value=True,  icon_only=True)
        bs.ToggleButton(on_icon="heart-fill", off_icon="heart",  accent="danger",  value=False, icon_only=True)

    # Compact density
    bs.Label("Compact Density", font="heading-sm[bold]")
    with bs.HStack(gap=8):
        bs.ToggleButton("Compact",  density="compact", value=False)
        bs.ToggleButton("Compact",  density="compact", value=True, accent="primary")
        bs.ToggleButton(on_icon="star-fill", off_icon="star", density="compact",
                        accent="warning", value=True, icon_only=True)

    # Disabled
    bs.Label("Disabled", font="heading-sm[bold]")
    with bs.HStack(gap=8):
        bs.ToggleButton("Disabled inactive", disabled=True, value=False)
        bs.ToggleButton("Disabled active",   disabled=True, value=True)

app.run()
