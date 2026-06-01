"""Tooltip screenshot hero."""
import bootstack as bs

with bs.App(title="Tooltip", size=(340, 160), padding=40, gap=14) as app:
    bs.Label("Hover a button to see its tooltip", font="caption")

    btn = bs.Button("Hover me")
    tip = bs.Tooltip(btn, "This is a helpful tooltip.", accent="primary",
                     anchor_point="s", window_point="n")

    def trigger():
        btn.tk.event_generate('<Enter>')

    def ensure_topmost():
        if tip._internal._toplevel:
            tip._internal._toplevel.attributes('-topmost', True)

    app.tk.after(600, trigger)
    app.tk.after(900, ensure_topmost)

app.run()
