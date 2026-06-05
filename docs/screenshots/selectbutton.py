import bootstack as bs


def hero():
    with bs.App(title="SelectButton", size=(240, 180), padding=20) as app:
        with bs.HStack(fill="x"):
            sb = bs.SelectButton(["Light", "Dark", "Auto"], value="Light")

    app.tk.after(850, sb._internal.show_menu)
    app.run()


def accents():
    with bs.App(title="SelectButton — Accents", padding=20) as app:
        with bs.HStack(gap=8, fill="x"):
            for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
                bs.SelectButton([accent.title()], value=accent.title(), accent=accent)

    app.run()


def variants():
    with bs.App(title="SelectButton — Variants", padding=20) as app:
        with bs.HStack(gap=8, fill="x"):
            for variant in ("solid", "outline", "ghost"):
                bs.SelectButton([variant.title()], value=variant.title(), accent="primary", variant=variant)

    app.run()


def icon():
    with bs.App(title="SelectButton — With Icon", padding=20) as app:
        with bs.HStack(gap=8, fill="x"):
            bs.SelectButton(["Light", "Dark", "Auto"],
                            value="Dark", icon="moon-fill")
            bs.SelectButton(["Small", "Medium", "Large"],
                            value="Large", icon="fonts", accent="secondary")

    app.run()


def disabled():
    with bs.App(title="SelectButton — Disabled", padding=20) as app:
        with bs.HStack(gap=8, fill="x"):
            bs.SelectButton(["A", "B", "C"], value="B", disabled=True)
            bs.SelectButton(["A", "B", "C"], value="B", disabled=True,
                            accent="primary", variant="outline")

    app.run()


SCENES = {
    "hero":     hero,
    "accents":  accents,
    "variants": variants,
    "icon":     icon,
    "disabled": disabled,
}