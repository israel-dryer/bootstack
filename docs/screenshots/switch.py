import bootstack as bs


def hero():
    with bs.App(title="Switch", padding=20) as app:
        with bs.HStack(gap=24, fill="x"):
            bs.Switch("Off", value=False)
            bs.Switch("On",  value=True)

    app.run()


def accents():
    with bs.App(title="Switch — Accents", padding=20) as app:
        with bs.HStack(gap=16, fill="x"):
            for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
                bs.Switch(accent.title(), accent=accent, value=True)

    app.run()


def disabled():
    with bs.App(title="Switch — Disabled", padding=20) as app:
        with bs.HStack(gap=24, fill="x"):
            bs.Switch("Cannot change", disabled=True, value=False)
            bs.Switch("Locked on",    disabled=True, value=True)

    app.run()


SCENES = {
    "hero":     hero,
    "accents":  accents,
    "disabled": disabled,
}