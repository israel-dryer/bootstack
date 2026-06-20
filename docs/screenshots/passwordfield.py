import bootstack as bs


def hero():
    with bs.App(title="PasswordField", minsize=(720, 1), padding=20, gap=12) as app:
        with bs.Row(gap=12, horizontal="stretch", grow_items=True, vertical_items="top"):
            field = bs.PasswordField(
                label="Password",
                value="secret123",
                message="Must be at least 8 characters.",
            )
            bs.PasswordField(
                label="Confirm password",
                placeholder="Re-enter password…",
            )
        app.tk.after(200, field.focus)

    app.run()


def toggle():
    with bs.App(title="PasswordField — Visibility Toggle", minsize=(720, 1), padding=20) as app:
        with bs.Row(gap=12, horizontal="stretch", grow_items=True):
            bs.PasswordField(label="With toggle", value="secret123")
            bs.PasswordField(label="No toggle",   value="secret123", show_visibility_toggle=False)

    app.run()


def states():
    with bs.App(title="PasswordField — States", minsize=(720, 1), padding=20) as app:
        with bs.Row(gap=8, horizontal="stretch", grow_items=True):
            normal = bs.PasswordField(value="secret123", label="Normal")
            bs.PasswordField(value="secret123", label="Read only", read_only=True)
            bs.PasswordField(value="secret123", label="Disabled",  disabled=True)
        app.tk.after(100, normal.focus)

    app.run()


def validation():
    with bs.App(title="PasswordField — Validation", minsize=(720, 1), padding=20) as app:
        field = bs.PasswordField(label="Password", value="short", horizontal="stretch")
        field.add_validation_rule(
            "stringLength",
            message="Password must be at least 8 characters.",
            min=8,
            trigger="blur",
        )
        app.tk.after(500, field.validate)

    app.run()


SCENES = {
    "hero":       hero,
    "toggle":     toggle,
    "states":     states,
    "validation": validation,
}
