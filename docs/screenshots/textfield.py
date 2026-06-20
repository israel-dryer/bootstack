import bootstack as bs


def hero():
    with bs.App(title="TextField", minsize=(720, 1), padding=20, gap=12) as app:
        with bs.Row(gap=12, horizontal="stretch", grow_items=True):
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
    with bs.App(title="TextField — States", minsize=(720, 1), padding=20) as app:
        with bs.Row(gap=8, horizontal="stretch", grow_items=True):
            bs.TextField(value="Editable",  label="Normal")
            bs.TextField(value="Read only", label="Read only", read_only=True)
            bs.TextField(value="Disabled",  label="Disabled", disabled=True)

    app.run()


def validation():
    with bs.App(title="TextField — Validation", minsize=(720, 1), padding=20) as app:
        field = bs.TextField(label="Username", value="ab", horizontal="stretch")
        field.add_validation_rule("stringLength", message="Must be at least 3 characters.", min=3, trigger="blur")
        app.tk.after(500, field.validate)

    app.run()


def required():
    with bs.App(title="TextField — Required", minsize=(720, 1), padding=20) as app:
        with bs.Row(gap=12, horizontal="stretch", grow_items=True):
            bs.TextField(label="Username", required=True, placeholder="Required field")
            bs.TextField(label="Email address", placeholder="Optional field")

    app.run()


def value_format():
    with bs.App(title="TextField — Value Formatting", minsize=(720, 1), padding=20, gap=12) as app:
        with bs.Row(gap=12, horizontal="stretch", grow_items=True):
            bs.TextField(label="Decimal",  value="1234.5",     value_format="#,##0.00")
            bs.TextField(label="Percent",  value="0.42",       value_format="percent")
        with bs.Row(gap=12, horizontal="stretch", grow_items=True):
            bs.TextField(label="Currency", value="9.99",       value_format="currency")
            bs.TextField(label="Date",     value="2024-06-01", value_format="yyyy-MM-dd")

    app.run()


SCENES = {
    "hero":         hero,
    "required":     required,
    "value-format": value_format,
    "states":       states,
    "validation":   validation,
}