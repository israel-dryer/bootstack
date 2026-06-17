import bootstack as bs


def hero():
    with bs.App(title="ToggleGroup", padding=20) as app:
        with bs.Row(horizontal="stretch"):
            bs.ToggleGroup(["Day", "Week", "Month"], value="Week")

    app.run()


def multi():
    with bs.App(title="ToggleGroup — Multi", padding=20) as app:
        with bs.Row(horizontal="stretch"):
            bs.ToggleGroup(["Bold", "Italic", "Underline"], mode="multi", value={"Bold", "Underline"})

    app.run()


def variants():
    with bs.App(title="ToggleGroup — Variants", padding=20) as app:
        with bs.Row(gap=16, horizontal="stretch"):
            for variant in ("solid", "outline", "ghost"):
                bs.ToggleGroup(["Off", "On"], accent="primary", variant=variant, value="On")

    app.run()


def accents():
    with bs.App(title="ToggleGroup — Accents", padding=20) as app:
        with bs.Row(gap=8, horizontal="stretch"):
            for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
                bs.ToggleGroup(["Off", "On"], accent=accent, value="On")

    app.run()


def orientation():
    with bs.App(title="ToggleGroup — Orientation", padding=20) as app:
        with bs.Row(horizontal="stretch"):
            bs.ToggleGroup(["Top", "Middle", "Bottom"], orient="vertical", value="Middle")

    app.run()


def disabled():
    with bs.App(title="ToggleGroup — Disabled", padding=20) as app:
        with bs.Row(gap=16, horizontal="stretch"):
            bs.ToggleGroup(["A", "B", "C"], value="B", disabled=True)
            bs.ToggleGroup(["X", "Y", "Z"], mode="multi", value={"X", "Z"}, disabled=True)

    app.run()


def icon_only():
    # An option with an icon and no text renders as a bare glyph — the widget
    # infers icon-only automatically, giving a compact toolbar.
    with bs.App(title="ToggleGroup — Icon only", padding=20) as app:
        with bs.Row(gap=16, horizontal="stretch"):
            bs.ToggleGroup(options=[
                {"icon": "text-left", "value": "left"},
                {"icon": "text-center", "value": "center"},
                {"icon": "text-right", "value": "right"},
                {"icon": "justify", "value": "justify"},
            ], value="left")
            bs.ToggleGroup(options=[
                {"icon": "type-bold", "value": "b"},
                {"icon": "type-italic", "value": "i"},
                {"icon": "type-underline", "value": "u"},
            ], mode="multi", value={"b"})

    app.run()


def option_disabled():
    # A single option disabled (greyed, non-selectable) inside an otherwise
    # enabled group — distinct from the whole-widget `disabled=`.
    with bs.App(title="ToggleGroup — Option disabled", padding=20) as app:
        with bs.Row(horizontal="stretch"):
            bs.ToggleGroup(options=[
                ("Day", "day"),
                ("Week", "week"),
                ("Month", "month"),
                {"text": "Year", "value": "year", "disabled": True},
            ], value="week")

    app.run()


SCENES = {
    "hero":           hero,
    "multi":          multi,
    "variants":       variants,
    "accents":        accents,
    "orientation":    orientation,
    "disabled":       disabled,
    "icon_only":      icon_only,
    "option_disabled": option_disabled,
}