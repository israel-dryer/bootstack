import bootstack as bs


def hero():
    with bs.App(title="ToggleGroup", padding=20) as app:
        with bs.HStack(fill="x"):
            bs.ToggleGroup(["Day", "Week", "Month"], value="Week")

    app.run()


def multi():
    with bs.App(title="ToggleGroup — Multi", padding=20) as app:
        with bs.HStack(fill="x"):
            bs.ToggleGroup(["Bold", "Italic", "Underline"], mode="multi", value={"Bold", "Underline"})

    app.run()


def variants():
    with bs.App(title="ToggleGroup — Variants", padding=20) as app:
        with bs.HStack(gap=16, fill="x"):
            for variant in ("solid", "outline", "ghost"):
                bs.ToggleGroup(["Off", "On"], accent="primary", variant=variant, value="On")

    app.run()


def accents():
    with bs.App(title="ToggleGroup — Accents", padding=20) as app:
        with bs.HStack(gap=8, fill="x"):
            for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
                bs.ToggleGroup(["Off", "On"], accent=accent, value="On")

    app.run()


def orientation():
    with bs.App(title="ToggleGroup — Orientation", padding=20) as app:
        with bs.HStack(fill="x"):
            bs.ToggleGroup(["Top", "Middle", "Bottom"], orient="vertical", value="Middle")

    app.run()


def disabled():
    with bs.App(title="ToggleGroup — Disabled", padding=20) as app:
        with bs.HStack(gap=16, fill="x"):
            bs.ToggleGroup(["A", "B", "C"], value="B", disabled=True)
            bs.ToggleGroup(["X", "Y", "Z"], mode="multi", value={"X", "Z"}, disabled=True)

    app.run()


SCENES = {
    "hero":        hero,
    "multi":       multi,
    "variants":    variants,
    "accents":     accents,
    "orientation": orientation,
    "disabled":    disabled,
}