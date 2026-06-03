import bootstack as bs


def hero():
    with bs.App(title="TextField", size=(680, 120), padding=20, gap=12) as app:
        with bs.HStack(gap=12, fill="x", fill_items="x", expand_items=True, anchor_items="n"):
            field = bs.TextField(
                label="Email address",
                placeholder="you@example.com",
                message="We'll never share your email.",
                value="hello@example.com",
            )
            bs.TextField(
                label="Username",
                placeholder="john_doe",
            )
        app.tk.after(200, field.focus)

    app.run()


def states():
    with bs.App(title="TextField — States", size=(680, 120), padding=20) as app:
        with bs.HStack(gap=8, fill="x", fill_items="x", expand_items=True):
            bs.TextField(value="Editable",  label="Normal")
            bs.TextField(value="Read only", label="Read only", read_only=True)
            bs.TextField(value="Disabled",  label="Disabled", disabled=True)

    app.run()


def validation():
    with bs.App(title="TextField — Validation", size=(680, 120), padding=20) as app:
        field = bs.TextField(label="Username", value="ab", fill="x")
        field.add_validation_rule("stringLength", message="Must be at least 3 characters.", min=3, trigger="blur")
        app.tk.after(500, lambda: field.validate("blur"))

    app.run()


def required():
    with bs.App(title="TextField — Required", size=(680, 100), padding=20) as app:
        with bs.HStack(gap=12, fill="x", fill_items="x", expand_items=True):
            bs.TextField(label="Username", required=True, placeholder="Required field")
            bs.TextField(label="Email address", placeholder="Optional field")

    app.run()


def value_format():
    with bs.App(title="TextField — Value Formatting", size=(680, 174), padding=20, gap=12) as app:
        with bs.HStack(gap=12, fill="x", fill_items="x", expand_items=True):
            bs.TextField(label="Decimal",  value="1234.5",    value_format="#,##0.00")
            bs.TextField(label="Percent",  value="0.42",      value_format="percent")
        with bs.HStack(gap=12, fill="x", fill_items="x", expand_items=True):
            bs.TextField(label="Currency", value="9.99",      value_format="currency")
            bs.TextField(label="Date",     value="2024-06-01", value_format="yyyy-MM-dd")

    app.run()


SCENES = {
    "hero":         hero,
    "required":     required,
    "value-format": value_format,
    "states":       states,
    "validation":   validation,
}