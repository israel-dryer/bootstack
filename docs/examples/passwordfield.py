"""PasswordField — full feature demo.

Demonstrates masked input, visibility toggle, label, message, required,
custom mask, and states.

Run with:
    python docs/examples/passwordfield.py
"""

import bootstack as bs

with bs.App(title="PasswordField Demo", padding=20, gap=16) as app:

    # Basic
    bs.Label("Basic", font="heading-sm")
    bs.PasswordField(placeholder="Enter password…", horizontal="stretch")

    # Label, message, required
    bs.Label("Label, Message, Required", font="heading-sm")
    bs.PasswordField(
        label="Password",
        placeholder="Enter password…",
        message="Must be at least 8 characters.",
        required=True,
        horizontal="stretch",
    )

    # Visibility toggle
    bs.Label("Visibility Toggle", font="heading-sm")
    with bs.Row(gap=8, horizontal="stretch", grow_items=True):
        bs.PasswordField(label="With toggle", value="secret123")
        bs.PasswordField(label="No toggle",   value="secret123", show_visibility_toggle=False)

    # Custom mask character
    bs.Label("Custom Mask Character", font="heading-sm")
    with bs.Row(gap=8, horizontal="stretch", grow_items=True):
        bs.PasswordField(value="secret", label="Default (•)")
        bs.PasswordField(value="secret", label="Asterisk (*)", mask="*")

    # States
    bs.Label("States", font="heading-sm")
    with bs.Row(gap=8, horizontal="stretch", grow_items=True):
        bs.PasswordField(value="secret123", label="Normal")
        bs.PasswordField(value="secret123", label="Read only", read_only=True)
        bs.PasswordField(value="secret123", label="Disabled",  disabled=True)

app.run()
