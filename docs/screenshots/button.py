import bootstack as bs


def hero():
    with bs.App(title="Button", padding=20) as app:
        with bs.HStack(gap=8, fill="x"):
            bs.Button("Save",   accent="primary")
            bs.Button("Cancel")
            bs.Button("Delete", accent="danger")
    app.run()


def accents():
    with bs.App(title="Button — Accents", padding=20) as app:
        with bs.HStack(gap=8, fill="x"):
            bs.Button("Default")
            bs.Button("Primary",   accent="primary")
            bs.Button("Secondary", accent="secondary")
            bs.Button("Info",      accent="info")
            bs.Button("Success",   accent="success")
            bs.Button("Warning",   accent="warning")
            bs.Button("Danger",    accent="danger")
    app.run()


def variants():
    with bs.App(title="Button — Variants", padding=20) as app:
        with bs.HStack(gap=8, fill="x"):
            bs.Button("Solid",   accent="primary", variant="solid")
            bs.Button("Outline", accent="primary", variant="outline")
            bs.Button("Ghost",   accent="primary", variant="ghost")
    app.run()


def icons():
    with bs.App(title="Button — Icons", padding=20) as app:
        with bs.HStack(gap=8, fill="x"):
            bs.Button("Save",   icon="save")
            bs.Button("Delete", icon="trash",    accent="danger")
            bs.Button("Export", icon="download", accent="secondary", variant="outline")
    app.run()


def icon_position():
    with bs.App(title="Button — Icon Position", padding=20) as app:
        with bs.HStack(gap=8, fill="x"):
            bs.Button("Left",   icon="arrow-left",  icon_position="left")
            bs.Button("Right",  icon="arrow-right", icon_position="right")
            bs.Button("Top",    icon="arrow-up",    icon_position="top")
            bs.Button("Bottom", icon="arrow-down",  icon_position="bottom")
    app.run()


def icon_only():
    with bs.App(title="Button — Icon Only", padding=20) as app:
        with bs.HStack(gap=4, fill="x"):
            bs.Button(icon="plus-lg",  accent="success")
            bs.Button(icon="dash-lg",  accent="danger")
            bs.Button(icon="pencil",   accent="secondary", variant="outline")
            bs.Button(icon="trash",    accent="danger",    variant="outline")
    app.run()


def width():
    with bs.App(title="Button — Uniform Width", padding=20) as app:
        with bs.HStack(gap=8, fill="x"):
            bs.Button("Save",   accent="primary", width=10)
            bs.Button("Cancel",                   width=10)
            bs.Button("Reset",  accent="danger",  width=10)
    app.run()


def density():
    with bs.App(title="Button — Compact Density", padding=20) as app:
        with bs.HStack(gap=4, fill="x"):
            bs.Button("Cut",   icon="scissors",  density="compact")
            bs.Button("Copy",  icon="copy",      density="compact")
            bs.Button("Paste", icon="clipboard", density="compact")
    app.run()


def disabled():
    with bs.App(title="Button — Disabled", padding=20) as app:
        with bs.HStack(gap=8, fill="x"):
            bs.Button("Disabled Solid",   accent="primary",                    disabled=True)
            bs.Button("Disabled Outline", accent="primary", variant="outline", disabled=True)
    app.run()


SCENES = {
    "hero":          hero,
    "accents":       accents,
    "variants":      variants,
    "icons":         icons,
    "icon-position": icon_position,
    "icon-only":     icon_only,
    "width":         width,
    "density":       density,
    "disabled":      disabled,
}