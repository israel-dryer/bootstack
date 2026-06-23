"""Switch — full feature demo.

Demonstrates basic usage, accent colors, custom state icons, reactive
binding, disabled states, and density.

Run with:
    python docs/examples/switch.py
"""

import bootstack as bs

with bs.App(title="Switch Demo", padding=20, gap=16) as app:

    # Basic
    bs.Label("Basic", font="heading-sm")
    with bs.Row(gap=24):
        bs.Switch("Off", value=False)
        bs.Switch("On",  value=True)

    # Accent colors
    bs.Label("Accent Colors", font="heading-sm")
    with bs.Row(gap=16):
        for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
            bs.Switch(accent.title(), accent=accent, value=True)

    # Reactive binding
    bs.Label("Reactive Binding", font="heading-sm")
    with bs.Column(gap=6):
        dark_sig = bs.Signal(False)
        bs.Switch("Dark mode", signal=dark_sig, accent="secondary")
        status_lbl = bs.Label("Theme: light", accent="secondary", font="caption")
        def _update_theme(v):
            status_lbl.text = f"Theme: {'dark' if v else 'light'}"

        dark_sig.subscribe(_update_theme)

    # Disabled
    bs.Label("Disabled", font="heading-sm")
    with bs.Row(gap=24):
        bs.Switch("Disabled off", disabled=True, value=False)
        bs.Switch("Disabled on",  disabled=True, value=True)

app.run()
