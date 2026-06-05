"""SpinnerField — full feature demo.

Demonstrates text mode, numeric mode, wrap-around, label and message,
reactive signal binding, states, and change event handling.

Run with:
    python docs/examples/spinnerfield.py
"""

import bootstack as bs

with bs.App(title="SpinnerField Demo", padding=20, gap=16) as app:

    # Text mode — fixed list of options
    bs.Label("Text Mode", font="heading-sm")
    bs.SpinnerField(
        label="Priority",
        options=["Low", "Medium", "High", "Critical"],
        value="Medium",
    )

    # Numeric mode — min / max / step
    bs.Label("Numeric Mode", font="heading-sm")
    bs.SpinnerField(
        label="Quantity",
        value=1,
        min_value=1,
        max_value=99,
        step=1,
    )

    # Wrap-around
    bs.Label("Wrap Around", font="heading-sm")
    bs.SpinnerField(
        label="Month",
        options=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        value="Jan",
        wrap=True,
    )

    # Label and message
    bs.Label("Label and Message", font="heading-sm")
    bs.SpinnerField(
        label="Font size",
        value=12,
        min_value=6,
        max_value=72,
        step=2,
        message="Applies to the selected text.",
    )

    # Reactive binding
    bs.Label("Reactive Binding", font="heading-sm")
    size_sig = bs.Signal("Medium")
    bs.SpinnerField(
        label="T-shirt size",
        options=["XS", "S", "M", "L", "XL", "XXL"],
        value="M",
        textsignal=size_sig,
    )
    bs.Label(textsignal=size_sig, accent="secondary")

    # States
    bs.Label("States", font="heading-sm")
    bs.SpinnerField(value=5, min_value=1, max_value=10, label="Normal")
    bs.SpinnerField(value=5, min_value=1, max_value=10, label="Read only", read_only=True)
    bs.SpinnerField(value=5, min_value=1, max_value=10, label="Disabled",  disabled=True)

    # Handling changes
    bs.Label("Handling Changes", font="heading-sm")
    last = bs.Signal("(none)")
    sf = bs.SpinnerField(
        label="Rating",
        options=["★", "★★", "★★★", "★★★★", "★★★★★"],
        value="★★★",
        wrap=True,
    )
    sf.on_change(lambda e: last.set(sf.value))
    bs.Label(textsignal=last, accent="secondary")

app.run()