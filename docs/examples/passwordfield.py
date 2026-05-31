"""PasswordField — full feature demo.

Demonstrates masked input, visibility toggle, label, message, required,
states, reactive binding, programmatic reveal, submit on Enter, and validation.

Run with:
    python docs/examples/passwordfield.py
"""

import bootstack as bs
from bootstack.validation import ValidationRule

with bs.App(title="PasswordField Demo", padding=20, gap=16) as app:

    # Basic
    bs.Label("Basic", font="heading-sm[bold]")
    bs.PasswordField(placeholder="Enter password…", fill="x")

    # Label, message, required
    bs.Label("Label, Message, Required", font="heading-sm[bold]")
    bs.PasswordField(
        label="Password",
        placeholder="Enter password…",
        message="Must be at least 8 characters.",
        required=True,
        fill="x",
    )

    # Visibility toggle
    bs.Label("Visibility Toggle", font="heading-sm[bold]")
    with bs.HStack(gap=8, fill="x", fill_items="x", expand_items=True):
        bs.PasswordField(label="With toggle")
        bs.PasswordField(label="No toggle", show_visibility_toggle=False)

    # States
    bs.Label("States", font="heading-sm[bold]")
    with bs.HStack(gap=8, fill="x", fill_items="x", expand_items=True):
        bs.PasswordField(value="secret123", label="Normal")
        bs.PasswordField(value="secret123", label="Read only", read_only=True)
        bs.PasswordField(value="secret123", label="Disabled", disabled=True)

    # Programmatic reveal
    bs.Label("Programmatic Reveal", font="heading-sm[bold]")
    with bs.VStack(gap=6, fill="x"):
        reveal_field = bs.PasswordField(
            label="Password", show_visibility_toggle=False, fill="x"
        )

        def _toggle_reveal(e):
            if show_cb.value:
                reveal_field.reveal()
            else:
                reveal_field.hide()

        show_cb = bs.Checkbox("Show password", on_change=_toggle_reveal)

    # Reactive binding
    bs.Label("Reactive Binding", font="heading-sm[bold]")
    with bs.VStack(gap=6, fill="x"):
        password_sig = bs.Signal("")
        bs.PasswordField(label="Password", textsignal=password_sig, fill="x")
        strength_lbl = bs.Label("Strength: —", accent="secondary", font="caption")

        def _check_strength(v):
            if len(v) == 0:
                strength_lbl.text = "Strength: —"
            elif len(v) < 6:
                strength_lbl.text = "Strength: Weak"
            elif len(v) < 10:
                strength_lbl.text = "Strength: Fair"
            else:
                strength_lbl.text = "Strength: Strong"

        password_sig.subscribe(_check_strength)

    # Submit on Enter
    bs.Label("Submit on Enter", font="heading-sm[bold]")
    with bs.VStack(gap=4, fill="x"):
        result_lbl = bs.Label("", accent="success", font="caption")
        submit_field = bs.PasswordField(placeholder="Press Enter to submit…", fill="x")

        def _on_submit(e):
            result_lbl.text = f"Submitted ({len(submit_field.value)} chars)"

        submit_field.on_submit(_on_submit)

    # Validation
    bs.Label("Validation", font="heading-sm[bold]")
    vf = bs.PasswordField(label="Password (min 8 chars)", fill="x")
    vf.add_validation_rule(ValidationRule(
        "stringLength",
        message="Password must be at least 8 characters.",
        min=8,
        trigger="blur",
    ))

app.run()
