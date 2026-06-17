import bootstack as bs


def hero():
    with bs.App(title="NumberField", minsize=(720, 1), padding=20, gap=12) as app:
        with bs.Row(gap=12, horizontal="stretch", grow_items=True, vertical_items="top"):
            field = bs.NumberField(
                label="Quantity",
                value=42,
                message="Max 100 units.",
            )
            bs.NumberField(
                label="Price",
                value=9.99,
                step=0.01,
            )
        app.tk.after(200, field.focus)

    app.run()


def steppers():
    with bs.App(title="NumberField — Stepper Buttons", minsize=(720, 1), padding=20) as app:
        with bs.Row(gap=12, horizontal="stretch", grow_items=True):
            bs.NumberField(label="With steppers", value=25)
            bs.NumberField(label="No steppers",   value=25, show_steppers=False)

    app.run()


def value_format():
    with bs.App(title="NumberField — Value Formatting", minsize=(720, 1), padding=20, gap=8) as app:
        with bs.Grid(columns=[1, 1], gap=8, horizontal="stretch", horizontal_items="stretch"):
            bs.NumberField(1234567, value_format="#,##0",    label="Thousands",  show_steppers=False)
            bs.NumberField(3.14159, value_format="#,##0.00", label="2 decimals", show_steppers=False)
            bs.NumberField(0.75,    value_format="percent",  label="Percent",    show_steppers=False)
            bs.NumberField(9.99,    value_format="currency", label="Currency",   show_steppers=False)

    app.run()


def states():
    with bs.App(title="NumberField — States", minsize=(720, 1), padding=20) as app:
        with bs.Row(gap=8, horizontal="stretch", grow_items=True):
            normal = bs.NumberField(value=42, label="Normal")
            bs.NumberField(value=42, label="Read only", read_only=True)
            bs.NumberField(value=42, label="Disabled",  disabled=True)
        app.tk.after(100, normal.focus)

    app.run()


def validation():
    with bs.App(title="NumberField — Validation", minsize=(720, 1), padding=20) as app:
        field = bs.NumberField(label="Age", value=150, horizontal="stretch")
        field.add_validation_rule(
            "custom",
            func=lambda v: v != "" and 0 <= float(v) <= 120,
            message="Age must be between 0 and 120.",
            trigger="blur",
        )
        app.tk.after(500, lambda: field.validate("blur"))

    app.run()


SCENES = {
    "hero":         hero,
    "steppers":     steppers,
    "value-format": value_format,
    "states":       states,
    "validation":   validation,
}