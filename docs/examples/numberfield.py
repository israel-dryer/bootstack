"""NumberField — full feature demo.

Demonstrates numeric input, bounds, step, stepper buttons, value
formatting, and states.

Run with:
    python docs/examples/numberfield.py
"""

import bootstack as bs

with bs.App(title="NumberField Demo", padding=20, gap=16) as app:

    # Basic
    bs.Label("Basic", font="heading-sm")
    with bs.Row(gap=8, vertical_items="bottom"):
        bs.NumberField()
        bs.NumberField(3.14, step=0.01, label="Float step")

    # Label, message, required
    bs.Label("Label, Message, Required", font="heading-sm")
    bs.NumberField(
        label="Quantity",
        message="Enter a value between 0 and 100.",
        required=True,
        horizontal="stretch",
    )

    # Bounds and step
    bs.Label("Bounds and Step", font="heading-sm")
    with bs.Row(gap=8, horizontal="stretch", grow_items=True):
        bs.NumberField(min_value=0, max_value=100, step=5, label="0–100, step 5")
        bs.NumberField(min_value=0.0, max_value=1.0, step=0.1, label="0.0–1.0, step 0.1")

    # Stepper buttons
    bs.Label("Stepper Buttons", font="heading-sm")
    with bs.Row(gap=8, horizontal="stretch", grow_items=True):
        bs.NumberField(label="With steppers", value=25)
        bs.NumberField(label="No steppers",   value=25, show_steppers=False)

    # Value formatting
    bs.Label("Value Formatting", font="heading-sm")
    with bs.Grid(columns=[1, 1], gap=8, horizontal="stretch", vertical_items="center"):
        bs.NumberField(1234567, value_format="#,##0",    label="Thousands",  show_steppers=False)
        bs.NumberField(3.14159, value_format="#,##0.00", label="2 decimals", show_steppers=False)
        bs.NumberField(0.75,    value_format="percent",  label="Percent",    show_steppers=False)
        bs.NumberField(9.99,    value_format="currency", label="Currency",   show_steppers=False)

    # States
    bs.Label("States", font="heading-sm")
    with bs.Row(gap=8, horizontal="stretch", grow_items=True):
        bs.NumberField(value=42, label="Normal")
        bs.NumberField(value=42, label="Read only", read_only=True)
        bs.NumberField(value=42, label="Disabled",  disabled=True)

app.run()
