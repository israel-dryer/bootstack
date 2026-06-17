import bootstack as bs


def hero():
    with bs.App(title="ToggleButton", padding=20) as app:
        with bs.Row(gap=8, horizontal="stretch"):
            bs.ToggleButton("Inactive", value=False)
            bs.ToggleButton("Active",   value=True)

    app.run()


def accents():
    with bs.App(title="ToggleButton — Accents", padding=20) as app:
        with bs.Row(gap=8, horizontal="stretch"):
            for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
                bs.ToggleButton(accent.title(), accent=accent, value=True)

    app.run()


def variants():
    with bs.App(title="ToggleButton — Variants", padding=20) as app:
        with bs.Row(gap=8, horizontal="stretch"):
            for variant in ("solid", "outline", "ghost"):
                bs.ToggleButton(f"{variant.title()} off", accent="primary", variant=variant, value=False)
                bs.ToggleButton(f"{variant.title()} on",  accent="primary", variant=variant, value=True)

    app.run()


def state_icons():
    with bs.App(title="ToggleButton — State Icons", padding=20) as app:
        with bs.Row(gap=8, horizontal="stretch"):
            bs.ToggleButton("Favorite", on_icon="star-fill", off_icon="star",
                            accent="warning", value=True)
            bs.ToggleButton("Favorite", on_icon="star-fill", off_icon="star",
                            accent="warning", value=False)
            bs.ToggleButton("Pin", on_icon="pin-fill", off_icon="pin",
                            accent="primary", value=True)
            bs.ToggleButton("Pin", on_icon="pin-fill", off_icon="pin",
                            accent="primary", value=False)

    app.run()


def icon_only():
    with bs.App(title="ToggleButton — Icon Only", padding=20) as app:
        with bs.Row(gap=8, horizontal="stretch"):
            bs.ToggleButton(on_icon="star-fill",  off_icon="star",  accent="warning", value=True,  icon_only=True)
            bs.ToggleButton(on_icon="star-fill",  off_icon="star",  accent="warning", value=False, icon_only=True)
            bs.ToggleButton(on_icon="pin-fill",   off_icon="pin",   accent="primary", value=True,  icon_only=True)
            bs.ToggleButton(on_icon="heart-fill", off_icon="heart", accent="danger",  value=True,  icon_only=True)
            bs.ToggleButton(on_icon="heart-fill", off_icon="heart", accent="danger",  value=False, icon_only=True)

    app.run()


def density():
    with bs.App(title="ToggleButton — Density", padding=20) as app:
        with bs.Row(gap=8, horizontal="stretch"):
            bs.ToggleButton("Compact", density="compact", value=False)
            bs.ToggleButton("Compact", density="compact", value=True, accent="primary")
            bs.ToggleButton(on_icon="star-fill", off_icon="star",
                            density="compact", accent="warning", value=True, icon_only=True)

    app.run()


def disabled():
    with bs.App(title="ToggleButton — Disabled", padding=20) as app:
        with bs.Row(gap=8, horizontal="stretch"):
            bs.ToggleButton("Disabled inactive", disabled=True, value=False)
            bs.ToggleButton("Disabled active",   disabled=True, value=True)

    app.run()


SCENES = {
    "hero":        hero,
    "accents":     accents,
    "variants":    variants,
    "state-icons": state_icons,
    "icon-only":   icon_only,
    "density":     density,
    "disabled":    disabled,
}