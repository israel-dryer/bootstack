"""Checkbox — full feature demo.

Demonstrates basic usage, accent colors, custom state icons, reactive
binding, custom values, disabled states, and event handling.

Run with:
    python docs/examples/checkbox.py
"""

import bootstack as bs

with bs.App(title="Checkbox Demo", padding=20, gap=16) as app:

    # Basic
    bs.Label("Basic", font="heading-sm")
    bs.Checkbox("Unchecked", value=False)
    bs.Checkbox("Checked",   value=True)

    # Accent colors
    bs.Label("Accent Colors", font="heading-sm")
    with bs.Row(gap=16):
        for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
            bs.Checkbox(accent.title(), accent=accent, value=True)

    # Custom state icons
    bs.Label("Custom State Icons", font="heading-sm")
    with bs.Row(gap=24):
        bs.Checkbox("Checked",
            on_icon="check-circle-fill", off_icon="circle",
            show_indicator=False, accent="success", value=True)
        bs.Checkbox("Unchecked",
            on_icon="check-circle-fill", off_icon="circle",
            show_indicator=False, accent="success", value=False)
        bs.Checkbox("Favorite",
            on_icon="star-fill", off_icon="star",
            accent="warning", value=True)

    # Reactive binding
    bs.Label("Reactive Binding", font="heading-sm")
    with bs.Column(gap=6):
        agreed = bs.Signal(False)
        bs.Checkbox("I agree to the terms", signal=agreed)
        status_lbl = bs.Label("Status: not agreed", accent="secondary", font="caption")

        def _update_status(v):
            status_lbl.text = "Status: agreed" if v else "Status: not agreed"

        agreed.subscribe(_update_status)

    # Custom values
    bs.Label("Custom Values", font="heading-sm")
    with bs.Column(gap=6):
        theme_sig = bs.Signal("light")
        bs.Checkbox(
            "Dark mode",
            signal=theme_sig,
            checked_value="dark",
            unchecked_value="light",
        )
        theme_lbl = bs.Label("Theme: light", accent="secondary", font="caption")
        def _update_theme(v):
            theme_lbl.text = f"Theme: {v}"

        theme_sig.subscribe(_update_theme)

    # Disabled
    bs.Label("Disabled", font="heading-sm")
    with bs.Row(gap=16):
        bs.Checkbox("Disabled unchecked", disabled=True)
        bs.Checkbox("Disabled checked", value=True, disabled=True)

    # Events
    bs.Label("Events", font="heading-sm")
    with bs.Column(gap=6):
        event_lbl = bs.Label("Toggle the checkbox…", accent="secondary", font="caption")
        event_chk = bs.Checkbox("Toggle me")

        def _on_change(e):
            state = "checked" if event_chk.checked else "unchecked"
            event_lbl.text = f"State: {state}"

        event_chk.on_change(_on_change)

app.run()
