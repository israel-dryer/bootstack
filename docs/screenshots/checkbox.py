import bootstack as bs


def hero():
    with bs.App(title="Checkbox", padding=20) as app:
        with bs.HStack(gap=24, fill="x"):
            bs.Checkbox("Unchecked", value=False)
            bs.Checkbox("Checked",   value=True)

    app.run()


def accents():
    with bs.App(title="Checkbox — Accents", padding=20) as app:
        with bs.HStack(gap=16, fill="x"):
            for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
                bs.Checkbox(accent.title(), accent=accent, value=True)

    app.run()


def tristate():
    with bs.App(title="Checkbox — Tristate", padding=20) as app:
        with bs.HStack(gap=24, fill="x"):
            bs.Checkbox("Indeterminate", tristate=True)
            bs.Checkbox("Checked",       tristate=True, value=True)
            bs.Checkbox("Unchecked",     tristate=True, value=False)

    app.run()


def custom_icons():
    with bs.App(title="Checkbox — Custom Icons", padding=20) as app:
        with bs.HStack(gap=24, fill="x"):
            bs.Checkbox("Checked",
                on_icon="check-circle-fill", off_icon="circle",
                show_indicator=False, accent="success", value=True)
            bs.Checkbox("Unchecked",
                on_icon="check-circle-fill", off_icon="circle",
                show_indicator=False, accent="success", value=False)

    app.run()


def disabled():
    with bs.App(title="Checkbox — Disabled", padding=20) as app:
        with bs.HStack(gap=24, fill="x"):
            bs.Checkbox("Disabled",         disabled=True)
            bs.Checkbox("Disabled checked", value=True, disabled=True)

    app.run()


SCENES = {
    "hero":         hero,
    "accents":      accents,
    "tristate":     tristate,
    "custom-icons": custom_icons,
    "disabled":     disabled,
}