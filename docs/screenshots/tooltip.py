"""Tooltip screenshot hero — run this to record a GIF, or the screenshot
runner simulates hover so the tooltip appears in the static capture."""
import bootstack as bs

with bs.App(title="Tooltip", size=(420, 200), padding=30, gap=14) as app:
    bs.Label("Hover a button to see its tooltip", font="caption")

    with bs.HStack(gap=8):
        b1 = bs.Button("Default")
        t1 = bs.Tooltip(b1, "A helpful tooltip.", anchor_point="s", window_point="n")

        b2 = bs.Button("Primary")
        t2 = bs.Tooltip(b2, "Primary accent tooltip.", accent="primary",
                        anchor_point="s", window_point="n")

        b3 = bs.Button("Danger")
        t3 = bs.Tooltip(b3, "Danger accent tooltip.", accent="danger",
                        anchor_point="s", window_point="n")

    # Simulate hover at t=600ms → tooltip fires at t=850ms (250ms delay)
    # → screenshot runner grabs at t=950ms, tooltip is on top.
    def trigger():
        b2.tk.event_generate('<Enter>')

    def ensure_topmost():
        if t2._internal._toplevel:
            t2._internal._toplevel.attributes('-topmost', True)

    app.tk.after(600, trigger)
    app.tk.after(900, ensure_topmost)

app.run()
