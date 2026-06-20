"""DateField — full feature demo.

Demonstrates date formats, single and range selection modes, min/max date
constraints, reactive signal binding, states, and change event handling.

Run with:
    python docs/examples/datefield.py
"""

from datetime import date

import bootstack as bs

with bs.App(title="DateField Demo", padding=20, gap=16) as app:

    # Basic usage
    bs.Label("Basic", font="heading-sm")
    bs.DateField(label="Select a date")

    # Date format presets
    bs.Label("Display Formats", font="heading-sm")
    today = date.today()
    bs.DateField(value=today, label="Long date (default)",   value_format="longDate")
    bs.DateField(value=today, label="Short date",            value_format="shortDate")
    bs.DateField(value=today, label="Month and year",        value_format="monthAndYear")

    # Range mode
    bs.Label("Range Mode", font="heading-sm")
    bs.DateField(
        selection_mode="range",
        range_start=date(today.year, today.month, 1),
        range_end=today,
        label="Date range",
        message="Select a start and end date.",
    )

    # Min / max date constraints
    bs.Label("Constrained Dates", font="heading-sm")
    from datetime import timedelta
    bs.DateField(
        label="Booking date",
        message="Must be within the next 30 days.",
        min_date=today,
        max_date=today + timedelta(days=30),
    )

    # Reactive binding — the signal carries the date object
    bs.Label("Reactive Binding", font="heading-sm")
    date_sig = bs.Signal(today)
    bs.DateField(label="Pick a date", signal=date_sig)
    date_text = date_sig.map(lambda d: d.strftime("%B %d, %Y") if d else "")
    bs.Label(textsignal=date_text, accent="secondary")

    # States
    bs.Label("States", font="heading-sm")
    bs.DateField(value=today, label="Normal")
    bs.DateField(value=today, label="Read only", read_only=True)
    bs.DateField(value=today, label="Disabled",  disabled=True)

    # Handling changes
    bs.Label("Handling Changes", font="heading-sm")
    last = bs.Signal("(none)")
    picker = bs.DateField(label="Choose a date")
    picker.on_change(lambda e: last.set(str(picker.value)))
    bs.Label(textsignal=last, accent="secondary")

    # Validation
    bs.Label("Validation", font="heading-sm")
    validated = bs.DateField(label="Required date", required=True)
    with bs.Row(gap=8):
        bs.Button("Validate", on_click=lambda: validated.validate())

app.run()