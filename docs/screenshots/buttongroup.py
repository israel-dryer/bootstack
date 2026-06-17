import bootstack as bs


def hero():
    with bs.App(title="ButtonGroup", padding=20) as app:
        bg = bs.ButtonGroup()
        bg.add(icon="type-bold")
        bg.add(icon="type-italic")
        bg.add(icon="type-underline")
        bg.add(icon="type-strikethrough")
    app.run()


def accents():
    with bs.App(title="ButtonGroup — Accents", padding=20, gap=8) as app:
        for accent in ("default", "primary", "secondary", "success", "warning", "danger"):
            with bs.Row(horizontal="stretch"):
                bg = bs.ButtonGroup(accent=accent)
                bg.add("Save")
                bg.add("Cancel")
    app.run()


def variants():
    with bs.App(title="ButtonGroup — Variants", padding=20, gap=8) as app:
        for variant in ("solid", "outline", "ghost"):
            with bs.Row(horizontal="stretch"):
                bg = bs.ButtonGroup(accent="primary", variant=variant)
                bg.add("Save")
                bg.add("Cancel")
                bg.add("Reset")
    app.run()


def icons():
    with bs.App(title="ButtonGroup — Icons", padding=20) as app:
        with bs.Row(horizontal="stretch"):
            bg = bs.ButtonGroup(accent="primary", variant="outline")
            bg.add("Bold",      icon="type-bold")
            bg.add("Italic",    icon="type-italic")
            bg.add("Underline", icon="type-underline")
    app.run()


def icon_only():
    with bs.App(title="ButtonGroup — Icon Only", padding=20, gap=8) as app:
        with bs.Row(horizontal="stretch"):
            bg1 = bs.ButtonGroup(variant="outline", accent="primary")
            bg1.add(icon="type-bold")
            bg1.add(icon="type-italic")
            bg1.add(icon="type-underline")
            bg1.add(icon="type-strikethrough")

        with bs.Row(horizontal="stretch"):
            bg2 = bs.ButtonGroup()
            bg2.add(icon="scissors")
            bg2.add(icon="copy")
            bg2.add(icon="clipboard")
    app.run()


def vertical():
    with bs.App(title="ButtonGroup — Vertical", padding=20) as app:
        with bs.Row(horizontal="stretch"):
            bg = bs.ButtonGroup("vertical", accent="primary", variant="outline")
            bg.add("Cut",   icon="scissors")
            bg.add("Copy",  icon="copy")
            bg.add("Paste", icon="clipboard")
    app.run()


def density():
    with bs.App(title="ButtonGroup — Density", padding=20) as app:
        with bs.Row(gap=20, horizontal="stretch"):
            bg1 = bs.ButtonGroup(accent="primary")
            bg1.add("Cut",   icon="scissors")
            bg1.add("Copy",  icon="copy")
            bg1.add("Paste", icon="clipboard")

            bg2 = bs.ButtonGroup(accent="primary", density="compact")
            bg2.add("Cut",   icon="scissors")
            bg2.add("Copy",  icon="copy")
            bg2.add("Paste", icon="clipboard")
    app.run()


def disabled():
    with bs.App(title="ButtonGroup — Disabled", padding=20) as app:
        with bs.Row(gap=20, horizontal="stretch"):
            bg1 = bs.ButtonGroup(accent="primary")
            bg1.add("Save")
            bg1.add("Cancel")

            bg2 = bs.ButtonGroup(accent="primary", disabled=True)
            bg2.add("Save")
            bg2.add("Cancel")
    app.run()


SCENES = {
    "hero":     hero,
    "accents":  accents,
    "variants": variants,
    "icons":    icons,
    "icon-only": icon_only,
    "vertical": vertical,
    "density":  density,
    "disabled": disabled,
}