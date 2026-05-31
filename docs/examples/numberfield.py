"""NumberField — full feature demo.

Demonstrates numeric input, bounds, step, stepper buttons, states,
reactive binding, programmatic stepping, and validation.

Run with:
    python docs/examples/numberfield.py
"""

import bootstack as bs
from bootstack.validation import ValidationRule

with bs.App(title="NumberField Demo", padding=20, minsize=(800, 800)) as app:

    with bs.ScrollView(scroll_direction="vertical", scrollbar_visibility="scroll", fill="both", expand=True):

        with bs.VStack(gap=16, padding=(0, 0, 20, 0), fill="x"):

            # Basic
            bs.Label("Basic", font="heading-sm[bold]")
            with bs.HStack(gap=8, anchor_items="s"):
                bs.NumberField()
                bs.NumberField(3.14, step=0.01, label="Float step")

            # Label, message, required
            bs.Label("Label, Message, Required", font="heading-sm[bold]")
            bs.NumberField(
                label="Quantity",
                message="Enter a value between 0 and 100.",
                required=True,
                fill="x",
            )

            # Bounds and step
            bs.Label("Bounds and Step", font="heading-sm[bold]")
            with bs.HStack(gap=8, fill="x", fill_items="x", expand_items=True):
                bs.NumberField(min_value=0, max_value=100, step=5, label="0–100, step 5")
                bs.NumberField(min_value=0.0, max_value=1.0, step=0.1, label="0.0–1.0, step 0.1")

            # Stepper buttons
            bs.Label("Stepper Buttons", font="heading-sm[bold]")
            with bs.HStack(gap=8, fill="x", fill_items="x", expand_items=True):
                bs.NumberField(label="With steppers")
                bs.NumberField(label="No steppers", show_steppers=False)

            # Value formatting
            bs.Label("Value Formatting", font="heading-sm[bold]")
            with bs.Grid(columns=[1, 1], gap=8, fill="x", sticky_items="ew"):
                bs.NumberField(1234567, value_format="#,##0",    label="Thousands",  show_steppers=False)
                bs.NumberField(3.14159, value_format="#,##0.00", label="2 decimals", show_steppers=False)
                bs.NumberField(0.75,    value_format="percent",  label="Percent",    show_steppers=False)
                bs.NumberField(9.99,    value_format="currency", label="Currency",   show_steppers=False)

            # States
            bs.Label("States", font="heading-sm[bold]")
            with bs.HStack(gap=8, fill="x", fill_items="x", expand_items=True):
                bs.NumberField(value=42, label="Normal")
                bs.NumberField(value=42, label="Read only", read_only=True)
                bs.NumberField(value=42, label="Disabled",  disabled=True)

            # Programmatic stepping
            bs.Label("Programmatic Stepping", font="heading-sm[bold]")
            with bs.VStack(gap=6, fill="x"):
                step_field = bs.NumberField(value=10, step=5, label="Value", fill="x")
                with bs.HStack(gap=8):
                    bs.Button("−5",  on_click=lambda: step_field.decrement(), variant="outline")
                    bs.Button("+5",  on_click=lambda: step_field.increment(), variant="outline")
                    bs.Button("+10", on_click=lambda: step_field.increment(2), variant="outline")

            # Reactive binding
            bs.Label("Reactive Binding", font="heading-sm[bold]")
            with bs.VStack(gap=6, fill="x"):
                qty = bs.Signal("1")
                bs.NumberField(label="Quantity", textsignal=qty, min_value=1, fill="x")
                total_lbl = bs.Label("Total: $9.99", accent="secondary", font="caption")

                def _update_total(v):
                    try:
                        total_lbl.text = f"Total: ${float(v) * 9.99:.2f}"
                    except (ValueError, TypeError):
                        total_lbl.text = "Total: —"

                qty.subscribe(_update_total)

            # Validation
            bs.Label("Validation", font="heading-sm[bold]")
            vf = bs.NumberField(label="Age (0–120)", fill="x")
            vf.add_validation_rule(ValidationRule(
                "custom",
                func=lambda v: v != "" and 0 <= float(v) <= 120,
                message="Age must be between 0 and 120.",
                trigger="blur",
            ))

app.run()
