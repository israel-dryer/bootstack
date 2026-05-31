"""TextField — full feature demo.

Demonstrates basic input, placeholder, label, message, reactive binding,
read-only and disabled states, validation, addons, and event handling.

Run with:
    python docs/examples/textfield.py
"""

import bootstack as bs

with bs.App(title="TextField Demo", padding=20, gap=16) as app:

    # Basic
    bs.Label("Basic", font="heading-sm[bold]")
    basic = bs.TextField(value="Hello, bootstack!", fill="x")

    # Label and message
    bs.Label("Label & Message", font="heading-sm[bold]")
    bs.TextField(
        label="Email address",
        placeholder="you@example.com",
        message="We'll never share your email.",
        fill="x",
    )

    # Required
    bs.Label("Required", font="heading-sm[bold]")
    bs.TextField(label="Username", placeholder="Choose a username", required=True, fill="x")

    # States
    bs.Label("States", font="heading-sm[bold]")
    with bs.HStack(gap=8, fill="x", fill_items="x", expand_items=True):
        bs.TextField(value="Editable",  label="Normal")
        bs.TextField(value="Read only", label="Read only", read_only=True)
        bs.TextField(value="Disabled",  label="Disabled", disabled=True)

    # Reactive binding
    bs.Label("Reactive Binding", font="heading-sm[bold]")
    with bs.VStack(gap=6, fill="x"):
        name = bs.Signal("bootstack")
        bs.TextField(label="Name", textsignal=name, fill="x")
        bs.Label(textsignal=name, accent="secondary", font="caption")

    # Live character count via on_input
    bs.Label("Live Character Count (on_input)", font="heading-sm[bold]")
    with bs.VStack(gap=4, fill="x"):
        count_lbl = bs.Label("0 / 50", accent="secondary", font="caption")
        field = bs.TextField(placeholder="Type to count…", fill="x")

        def _update_count(e):
            count_lbl.text = f"{len(field.value)} / 50"

        field.on_input(_update_count)

    # on_submit
    bs.Label("Submit on Enter (on_submit)", font="heading-sm[bold]")
    with bs.VStack(gap=4, fill="x"):
        result_lbl = bs.Label("", accent="success", font="caption")
        submit_field = bs.TextField(placeholder="Type and press Enter…", fill="x")
        def _on_submit(e):
            result_lbl.text = f"Submitted: {submit_field.value}"

        submit_field.on_submit(_on_submit)

    # Validation
    bs.Label("Validation", font="heading-sm[bold]")
    from bootstack.validation import ValidationRule
    vf = bs.TextField(label="Min 3 characters", placeholder="Enter text…", fill="x")
    vf.add_validation_rule(ValidationRule(
        "stringLength",
        message="Must be at least 3 characters.",
        min=3,
        trigger="blur",
    ))

app.run()
