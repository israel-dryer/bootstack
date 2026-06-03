import bootstack as bs


def hero():
    with bs.App(title="NumberField", size=(680, 130), padding=20, gap=12) as app:
        with bs.HStack(gap=12, fill="x", fill_items="x", expand_items=True, anchor_items="n"):
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
    with bs.App(title="NumberField — Stepper Buttons", size=(680, 100), padding=20) as app:
        with bs.HStack(gap=12, fill="x", fill_items="x", expand_items=True):
            bs.NumberField(label="With steppers", value=25)
            bs.NumberField(label="No steppers",   value=25, show_steppers=False)

    app.run()


def value_format():
    with bs.App(title="NumberField — Value Formatting", size=(680, 174), padding=20, gap=8) as app:
        with bs.Grid(columns=[1, 1], gap=8, fill="x", sticky_items="ew"):
            bs.NumberField(1234567, value_format="#,##0",    label="Thousands",  show_steppers=False)
            bs.NumberField(3.14159, value_format="#,##0.00", label="2 decimals", show_steppers=False)
            bs.NumberField(0.75,    value_format="percent",  label="Percent",    show_steppers=False)
            bs.NumberField(9.99,    value_format="currency", label="Currency",   show_steppers=False)

    app.run()


def states():
    with bs.App(title="NumberField — States", size=(780, 100), padding=20) as app:
        with bs.HStack(gap=8, fill="x", fill_items="x", expand_items=True):
            normal = bs.NumberField(value=42, label="Normal")
            bs.NumberField(value=42, label="Read only", read_only=True)
            bs.NumberField(value=42, label="Disabled",  disabled=True)
        app.tk.after(100, normal.focus)

    app.run()


def validation():
    with bs.App(title="NumberField — Validation", size=(680, 120), padding=20) as app:
        field = bs.NumberField(label="Age", value=150, fill="x")
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
