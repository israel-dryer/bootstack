"""TextField — full feature demo.

Demonstrates basic input, placeholder, label, message, reactive binding,
read-only and disabled states, validation, addons, and event handling.

Run with:
    python docs/examples/textfield.py
"""

import bootstack as bs

with bs.App(title="TextField Demo", padding=20, gap=16) as app:

    # Basic
    bs.Label("Basic", font="heading-sm")
    basic = bs.TextField(value="Hello, bootstack!", horizontal="stretch")

    # Label and message
    bs.Label("Label and Message", font="heading-sm")
    bs.TextField(
        label="Email address",
        placeholder="you@example.com",
        message="We'll never share your email.",
        horizontal="stretch",
    )

    # Required
    bs.Label("Required", font="heading-sm")
    bs.TextField(label="Username", placeholder="Choose a username", required=True, horizontal="stretch")

    # States
    bs.Label("States", font="heading-sm")
    with bs.Row(gap=8, horizontal="stretch", grow_items=True):
        bs.TextField(value="Editable",  label="Normal")
        bs.TextField(value="Read only", label="Read only", read_only=True)
        bs.TextField(value="Disabled",  label="Disabled", disabled=True)

    # Reactive binding
    bs.Label("Reactive Binding", font="heading-sm")
    with bs.Column(gap=6, horizontal="stretch"):
        name = bs.Signal("bootstack")
        bs.TextField(label="Name", textsignal=name, horizontal="stretch")
        bs.Label(textsignal=name, accent="secondary", font="caption")

    # Live character count via on_input
    bs.Label("Live Character Count (on_input)", font="heading-sm")
    with bs.Column(gap=4, horizontal="stretch"):
        count_lbl = bs.Label("0 / 50", accent="secondary", font="caption")
        field = bs.TextField(placeholder="Type to count…", horizontal="stretch")

        def _update_count(e):
            count_lbl.text = f"{len(field.value)} / 50"

        field.on_input(_update_count)

    # on_submit
    bs.Label("Submit on Enter (on_submit)", font="heading-sm")
    with bs.Column(gap=4, horizontal="stretch"):
        result_lbl = bs.Label("", accent="success", font="caption")
        submit_field = bs.TextField(placeholder="Type and press Enter…", horizontal="stretch")
        def _on_submit(e):
            result_lbl.text = f"Submitted: {submit_field.value}"

        submit_field.on_submit(_on_submit)

    # Validation
    bs.Label("Validation", font="heading-sm")
    vf = bs.TextField(label="Min 3 characters", placeholder="Enter text…", horizontal="stretch")
    vf.add_validation_rule(
        "stringLength",
        message="Must be at least 3 characters.",
        min=3,
        trigger="blur",
    )

app.run()
