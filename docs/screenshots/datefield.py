from datetime import date

import bootstack as bs

TODAY = date.today()


def hero():
    with bs.App(title="DateField", padding=20, minsize=(720, 1)) as app:
        with bs.HStack(gap=12, fill="x", fill_items="x", expand_items=True, anchor_items="n"):
            df = bs.DateField(
                value=TODAY,
                label="Start date",
                message="Select the project start date.",
            )
            bs.DateField(
                label="End date",
                message="Select the project end date.",
            )
        app.tk.after(200, df.focus)
    app.run()


def formats():
    with bs.App(title="DateField — Formats", padding=20, gap=12, minsize=(720, 1)) as app:
        with bs.HStack(gap=12, fill="x", fill_items="x", expand_items=True, anchor_items="n"):
            bs.DateField(value=TODAY, label="Long date",    value_format="longDate")
            bs.DateField(value=TODAY, label="Short date",   value_format="shortDate")
            bs.DateField(value=TODAY, label="Month + year", value_format="monthAndYear")
    app.run()


def range_mode():
    with bs.App(title="DateField — Range", padding=20, minsize=(720, 1)) as app:
        start = date(TODAY.year, TODAY.month, 1)
        bs.DateField(
            selection_mode="range",
            range_start=start,
            range_end=TODAY,
            label="Date range",
            message="Select a start and end date.",
            fill="x",
        )
    app.run()


def states():
    with bs.App(title="DateField — States", padding=20, minsize=(720, 1)) as app:
        with bs.HStack(gap=12, fill="x", fill_items="x", expand_items=True, anchor_items="n"):
            bs.DateField(value=TODAY, label="Normal")
            bs.DateField(value=TODAY, label="Read only", read_only=True)
            bs.DateField(value=TODAY, label="Disabled",  disabled=True)
    app.run()


SCENES = {
    "hero":     hero,
    "formats":  formats,
    "range":    range_mode,
    "states":   states,
}