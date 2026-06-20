"""TimeField — full feature demo.

Demonstrates time formats, interval configuration, min/max time constraints,
reactive signal binding, states, and change event handling.

Run with:
    python docs/examples/timefield.py
"""

import datetime

import bootstack as bs

with bs.App(title="TimeField Demo", padding=20, gap=16) as app:

    # Basic usage
    bs.Label("Basic", font="heading-sm")
    bs.TimeField(label="Select a time")

    # Time format presets
    bs.Label("Display Formats", font="heading-sm")
    now = datetime.time(14, 30)
    bs.TimeField(value=now, label="Short time (default)", value_format="shortTime")
    bs.TimeField(value=now, label="24-hour",              value_format="HH:mm")
    bs.TimeField(value=now, label="24-hour with seconds",  value_format="HH:mm:ss")

    # Dropdown interval
    bs.Label("Dropdown Interval", font="heading-sm")
    bs.TimeField(value=now, label="15-minute intervals", interval=15)
    bs.TimeField(value=now, label="60-minute intervals", interval=60)

    # Time range constraints
    bs.Label("Business Hours", font="heading-sm")
    bs.TimeField(
        value=datetime.time(9, 0),
        label="Appointment time",
        message="Available Monday – Friday, 9 AM – 5 PM.",
        min_time=datetime.time(9, 0),
        max_time=datetime.time(17, 0),
        interval=30,
    )

    # Reactive binding — the signal carries the time object
    bs.Label("Reactive Binding", font="heading-sm")
    time_sig = bs.Signal(now)
    bs.TimeField(label="Pick a time", signal=time_sig)
    time_text = time_sig.map(lambda t: t.strftime("%I:%M %p") if t else "")
    bs.Label(textsignal=time_text, accent="secondary")

    # States
    bs.Label("States", font="heading-sm")
    bs.TimeField(value=now, label="Normal")
    bs.TimeField(value=now, label="Read only", read_only=True)
    bs.TimeField(value=now, label="Disabled",  disabled=True)

    # Handling changes
    bs.Label("Handling Changes", font="heading-sm")
    last = bs.Signal("(none)")
    tf = bs.TimeField(label="Choose a time")
    tf.on_change(lambda e: last.set(str(tf.value)))
    bs.Label(textsignal=last, accent="secondary")

    # Validation
    bs.Label("Validation", font="heading-sm")
    validated = bs.TimeField(label="Required time", required=True)
    with bs.Row(gap=8):
        bs.Button("Validate", on_click=lambda: validated.validate())

app.run()